#pragma once
// ====================================================================================
// NANO: MOTORES 4WD (TB6612FNG) COM RAMPA DE ACELERACAO
// ====================================================================================
// Lado esquerdo = canal A (2 motores em paralelo)   Lado direito = canal B (2 motores em paralelo)
//   PWMA D3, AIN1 D4, AIN2 D5  |  PWMB D6, BIN1 D7, BIN2 D8  |  STBY D12
//
// Protecoes que atacam o reset do Nano por queda de tensao:
//  - RAMPA: o comando (-255..255) nunca vira PWM direto; a saida sobe a uma taxa maxima
//    (rampaMs = tempo de 0 a 100%), freia ao dobro da taxa. Corta o pico de partida.
//  - REVERSAO: inverter o sentido com o motor girando passa obrigatoriamente por zero e espera
//    deadMs (tempo morto) antes de acelerar no sentido oposto (evita o pico de corrente de reversao).
//  - PWM MINIMO: abaixo de ~60/255 o motor com reducao metalica nao vence o atrito; a faixa
//    util 1..255 e mapeada em [pwmMin..pwmMax] (sem zona morta para o usuario).
//  - WATCHDOG: sem novo comando em watchdogMs, a saida desce em rampa ate zero (perda de Wi-Fi).
//  - STBY em LOW apos 1,5 s parado (menos consumo e motor solto).
// Aritmetica em ponto fixo x16 (int de 16 bits no AVR!).
// ====================================================================================
#include <Arduino.h>

struct MotorParams {
  uint16_t rampaMs    = 800;
  uint8_t  pwmMin     = 60;
  uint8_t  pwmMax     = 255;
  uint16_t deadMs     = 150;
  uint16_t watchdogMs = 0;
  bool     invEsq     = false;
  bool     invDir     = false;
};

struct LadoMotor {
  uint8_t pwm, in1, in2;
  int     alvo = 0;          // -255..255
  long    cur = 0;           // x16
  int8_t  ultSinal = 0;
  uint32_t liberaMs = 0;
};

static inline int8_t sinalDe(long v) { return (v > 0) - (v < 0); }

class MotoresTB6612 {
 public:
  MotorParams P;

  void begin(uint8_t pwmA, uint8_t a1, uint8_t a2, uint8_t pwmB, uint8_t b1, uint8_t b2, uint8_t stby) {
    L[0].pwm = pwmA; L[0].in1 = a1; L[0].in2 = a2;
    L[1].pwm = pwmB; L[1].in1 = b1; L[1].in2 = b2;
    pinStby = stby;
    for (uint8_t i = 0; i < 2; i++) {
      pinMode(L[i].pwm, OUTPUT); pinMode(L[i].in1, OUTPUT); pinMode(L[i].in2, OUTPUT);
      aplicar(L[i], i);
    }
    pinMode(pinStby, OUTPUT);
    digitalWrite(pinStby, LOW);
  }

  void comando(int esq, int dir, uint32_t agora) {
    L[0].alvo = constrain(esq, -255, 255);
    L[1].alvo = constrain(dir, -255, 255);
    ultCmd = agora;
    if (L[0].alvo || L[1].alvo) { ultAtivo = agora; digitalWrite(pinStby, HIGH); }
  }
  void parar() { L[0].alvo = L[1].alvo = 0; }                     // com rampa
  void paradaImediata() {                                         // emergencia: solta ja
    for (uint8_t i = 0; i < 2; i++) { L[i].alvo = 0; L[i].cur = 0; L[i].liberaMs = millis() + P.deadMs; aplicar(L[i], i); }
  }

  void atualizar(uint32_t agora) {
    if (agora - ultTick < 10) return;
    ultTick = (agora - ultTick > 100) ? agora : ultTick + 10;

    if (P.watchdogMs && (agora - ultCmd) > P.watchdogMs) { L[0].alvo = L[1].alvo = 0; }

    long acc = 40800L / (long)max((uint16_t)50, P.rampaMs);    // x16 por tick de 10 ms
    if (acc < 1) acc = 1;
    long dec = acc * 2;

    for (uint8_t i = 0; i < 2; i++) {
      LadoMotor &m = L[i];
      long tgt = (long)m.alvo * 16L;
      int8_t sa = sinalDe(m.alvo), sc = sinalDe(m.cur);
      if (sa != 0 && sc != 0 && sa != sc) tgt = 0;                                   // passa por zero
      if (sa != 0 && sc == 0 && m.ultSinal != 0 && sa != m.ultSinal && agora < m.liberaMs) tgt = 0;   // tempo morto

      long antes = m.cur;
      bool sobe = labs(tgt) > labs(m.cur);
      long passo = sobe ? acc : dec;
      long d = tgt - m.cur;
      if (d > passo) d = passo; else if (d < -passo) d = -passo;
      m.cur += d;

      if (antes == 0 && m.cur != 0) ultArranque = agora;
      if (antes != 0 && m.cur == 0) m.liberaMs = agora + P.deadMs;
      if (m.cur != 0) m.ultSinal = sinalDe(m.cur);
      if (m.cur != antes) aplicar(m, i);
    }

    bool algum = L[0].cur != 0 || L[1].cur != 0;
    if (algum) ultAtivo = agora;
    digitalWrite(pinStby, (algum || (agora - ultAtivo) < 1500) ? HIGH : LOW);
  }

  bool arrancando(uint32_t agora) const { return (agora - ultArranque) < 250 && (L[0].cur != 0 || L[1].cur != 0); }
  bool parado() const { return L[0].cur == 0 && L[1].cur == 0; }
  int  saidaEsq() const { return (int)(L[0].cur / 16); }
  int  saidaDir() const { return (int)(L[1].cur / 16); }

 private:
  LadoMotor L[2];
  uint8_t pinStby = 12;
  uint32_t ultCmd = 0, ultAtivo = 0, ultArranque = 0, ultTick = 0;

  void aplicar(LadoMotor &m, uint8_t idx) {
    if (m.cur == 0) {                                 // coast
      digitalWrite(m.in1, LOW); digitalWrite(m.in2, LOW); analogWrite(m.pwm, 0);
      return;
    }
    long v = labs(m.cur) / 16; if (v < 1) v = 1;
    long out = P.pwmMin + v * (long)(P.pwmMax - P.pwmMin) / 255L;
    bool inv = (idx == 0) ? P.invEsq : P.invDir;
    bool frente = (m.cur > 0) != inv;
    digitalWrite(m.in1, frente ? HIGH : LOW);
    digitalWrite(m.in2, frente ? LOW : HIGH);
    analogWrite(m.pwm, (int)out);
  }
};
