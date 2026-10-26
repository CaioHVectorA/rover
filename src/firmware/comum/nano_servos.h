#pragma once
// ====================================================================================
// NANO: SERVO SUAVE (anti-"rebolado")
// ====================================================================================
// Por que o Pan "rebola" em movimento lento? Atrito estatico + folga do encaixe: o SG90 agarra,
// acumula tensao, solta e passa do ponto (stick-slip). Estrategias deste modulo:
//  1. Posicao interna em float, saida em microssegundos (resolucao ~10x melhor que graus inteiros)
//     a cada 20 ms (= periodo do pulso do servo): nada de "escadinha" de 2 em 2 graus.
//  2. Perfil trapezoidal: aceleracao limitada + frenagem ~ raiz(2*a*dist): sem chicoteio.
//  3. PISO de velocidade na aproximacao (velMin): nunca chega "se arrastando", que e a faixa
//     onde o stick-slip acontece. Movimentos explicitamente lentos (vel pedida < piso) sao respeitados.
//  4. ANTIFOLGA (opcional): apos um movimento no sentido negativo, passa um pouco do ponto e volta,
//     de modo que o ponto final seja SEMPRE alcancado pelo mesmo lado (a folga fica sempre do mesmo lado).
//  5. Banda morta pequena em us (nao em graus) so para parar de comandar quando chegou.
//  6. Opcional: solta o pulso (detach) apos parado -> sem zumbido/aquecimento; a cabeca pode ceder.
// Tudo ajustavel em tempo real (protocolo <C,id,valor>) para voce calibrar na bancada.
// ====================================================================================
#include <Arduino.h>

#define SERVO_US_MIN  544
#define SERVO_US_MAX  2400
#define SERVO_TICK_MS 20

struct ServoParams {
  float    velPadraoUs = 1500;   // us/s   (~145 graus/s)
  float    velMinUs    = 150;    // us/s   piso de aproximacao (~14 graus/s)
  float    accUs       = 9000;   // us/s^2 (~870 graus/s^2)
  int      deadUs      = 2;
  int      backlashUs  = 0;
  uint16_t soltarMs    = 0;
};

static inline float deg10ParaUs(int d10) {
  return SERVO_US_MIN + (float)d10 * (SERVO_US_MAX - SERVO_US_MIN) / 1800.0f;
}
static inline float grausParaUs(float g) { return g * (SERVO_US_MAX - SERVO_US_MIN) / 180.0f; }

// Servo por hardware (Timer1 modo Fast PWM 14, ICR1=20 ms): D9=OC1A, D10=OC1B.
// Sem ISR e sem desabilitar interrupcoes -> nao interfere na serial nem gera jitter.
class ServoT1 {
 public:
  void attach(uint8_t p, int, int) {
    static bool init = false;
    if (!init) {
      TCCR1A = _BV(WGM11);
      TCCR1B = _BV(WGM13) | _BV(WGM12) | _BV(CS11);   // prescaler 8 -> 2 ticks/us
      ICR1 = 39999;
      init = true;
    }
    pin = p;
    pinMode(pin, OUTPUT);
    if (pin == 9) TCCR1A |= _BV(COM1A1); else TCCR1A |= _BV(COM1B1);
  }
  void writeMicroseconds(int us) {
    us = constrain(us, 400, 2500);
    if (pin == 9) OCR1A = (uint16_t)us * 2; else OCR1B = (uint16_t)us * 2;
  }
  void detach() {
    if (pin == 9) TCCR1A &= ~_BV(COM1A1); else TCCR1A &= ~_BV(COM1B1);
    digitalWrite(pin, LOW);
  }
 private:
  uint8_t pin = 9;
};

class ServoSuave {
 public:
  void begin(uint8_t pino, int minD10, int maxD10, int iniD10, const ServoParams *p) {
    pin = pino; P = p;
    minUs = deg10ParaUs(minD10); maxUs = deg10ParaUs(maxD10);
    minD = minD10; maxD = maxD10;
    pos = destino = finalUs = deg10ParaUs(constrain(iniD10, minD10, maxD10));
    ultUs = (int)(pos + 0.5f);
    s.attach(pin, SERVO_US_MIN, SERVO_US_MAX);
    s.writeMicroseconds(ultUs);
    ligado = true;
    ultMov = millis();
  }

  // vel10 = decimos de grau/s (0 = velocidade padrao)
  void mover(int deg10, int vel10) {
    deg10 = constrain(deg10, minD, maxD);
    float novo = deg10ParaUs(deg10);
    if (novo > pos + 0.5f) ultDir = +1; else if (novo < pos - 0.5f) ultDir = -1;
    finalUs = destino = novo;
    fase = 0;
    vmax = (vel10 > 0) ? vel10 * 1.031f : P->velPadraoUs;
    if (!ligado) { s.attach(pin, SERVO_US_MIN, SERVO_US_MAX); s.writeMicroseconds(ultUs); ligado = true; }
    mov = true;
  }

  // Chame sempre no loop. congelar=true segura o servo (orcamento de corrente na arrancada dos motores).
  bool atualizar(uint32_t agora, bool congelar) {
    if (agora - ultTick < SERVO_TICK_MS) return mov;
    ultTick = agora;
    if (congelar || !mov) { soltarSeParado(agora); return mov; }

    float erro = destino - pos;
    float dist = fabsf(erro);

    if (dist <= P->deadUs) {                       // chegou ao destino atual
      pos = destino;
      escrever();
      vAt = 0;
      if (fase == 0 && ultDir < 0 && P->backlashUs > 0) {          // passa do ponto e volta (antifolga)
        fase = 1; destino = max(minUs, finalUs - P->backlashUs);
        if (destino >= finalUs - 1) { fase = 0; mov = false; }
      } else if (fase == 1) { fase = 2; destino = finalUs; }
      else { if (fase == 2) { fase = 0; ultDir = +1; } mov = false; }
      ultMov = agora;
      return mov;
    }

    float dir = (erro > 0) ? 1.0f : -1.0f;
    float vmin = min(P->velMinUs, vmax);
    float vDes = sqrtf(2.0f * P->accUs * dist);      // frenagem
    if (vDes < vmin) vDes = vmin;
    if (vDes > vmax) vDes = vmax;
    float dv = P->accUs * (SERVO_TICK_MS / 1000.0f);
    if (vDes > vAt) vAt = min(vDes, vAt + dv); else vAt = vDes;
    if (vAt < vmin) vAt = vmin;
    float passo = vAt * (SERVO_TICK_MS / 1000.0f);
    if (passo > dist) passo = dist;
    pos += dir * passo;
    escrever();
    ultMov = agora;
    return true;
  }

  bool emMovimento() const { return mov; }
  int  posDeg10() const { return (int)((pos - SERVO_US_MIN) * 1800.0f / (SERVO_US_MAX - SERVO_US_MIN) + 0.5f); }

 private:
  ServoT1 s;
  uint8_t pin = 0;
  const ServoParams *P = nullptr;
  float pos = 1472, destino = 1472, finalUs = 1472, minUs = 544, maxUs = 2400, vAt = 0, vmax = 1500;
  int   minD = 0, maxD = 1800, ultUs = 1472;
  int8_t ultDir = +1, fase = 0;
  bool  mov = false, ligado = false;
  uint32_t ultTick = 0, ultMov = 0;

  void escrever() {
    int us = (int)(pos + 0.5f);
    if (us != ultUs) { s.writeMicroseconds(us); ultUs = us; }
  }
  void soltarSeParado(uint32_t agora) {
    if (!mov && ligado && P->soltarMs > 0 && (agora - ultMov) > P->soltarMs) { s.detach(); ligado = false; }
  }
};
