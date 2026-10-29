#include <Arduino.h>
#include "rover_protocolo.h"
#include "nano_servos.h"

constexpr uint8_t PWMA = 3, AIN1 = 4, AIN2 = 5;
constexpr uint8_t PWMB = 6, BIN1 = 7, BIN2 = 8, STBY = 12;
constexpr int PWM_MAX = 120;
constexpr uint32_t WATCHDOG_MS = 600, REVERSAO_MS = 150;
static ProtoParser parser;
static ServoParams parametros;
static ServoSuave pan, tilt;
static int atualE = 0, atualD = 0, alvoE = 0, alvoD = 0;
static bool esperando = false;
static uint32_t liberarEm = 0, ultimoMotor = 0, ultimoByte = 0;
static uint8_t piscadas = 0;
static uint32_t proximaPiscada = 0;

static void desligarSaidas() {
  digitalWrite(STBY, LOW);
  analogWrite(PWMA, 0); analogWrite(PWMB, 0);
  digitalWrite(AIN1, LOW); digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW); digitalWrite(BIN2, LOW);
  atualE = atualD = 0;
}
static void parar() {
  desligarSaidas();
  esperando = false;
  alvoE = alvoD = 0;
}
static void lado(uint8_t pwm, uint8_t in1, uint8_t in2, int v) {
  digitalWrite(in1, v > 0 ? HIGH : LOW);
  digitalWrite(in2, v < 0 ? HIGH : LOW);
  analogWrite(pwm, v < 0 ? -v : v);
}
static void aplicar() {
  lado(PWMA, AIN1, AIN2, alvoE);
  lado(PWMB, BIN1, BIN2, alvoD);
  digitalWrite(STBY, (alvoE || alvoD) ? HIGH : LOW);
  atualE = alvoE; atualD = alvoD;
}
static bool invertendo(int atual, int alvo) {
  return (atual > 0 && alvo < 0) || (atual < 0 && alvo > 0);
}
static void motores(int e, int d, uint32_t agora) {
  ultimoMotor = agora;
  if (!e && !d) { parar(); return; }
  alvoE = e; alvoD = d;
  if (esperando) return;  // Novos pacotes nao reiniciam a espera de reversao.
  if ((!atualE && !atualD) || invertendo(atualE, e) || invertendo(atualD, d)) {
    desligarSaidas();
    esperando = true;
    liberarEm = agora + REVERSAO_MS;
  } else aplicar();
}

static void receber(const ProtoFrame &f, uint32_t agora) {
  switch (f.cmd) {
    case 'M':
      if (f.n == 2 && f.arg[0] >= -255 && f.arg[0] <= 255
                   && f.arg[1] >= -255 && f.arg[1] <= 255) {
        motores(constrain(f.arg[0], -PWM_MAX, PWM_MAX),
                constrain(f.arg[1], -PWM_MAX, PWM_MAX), agora);
      }
      break;
    case 'S':
      if ((f.n == 2 || f.n == 3) && f.arg[0] >= 0 && f.arg[0] <= 1800
          && f.arg[1] >= 0 && f.arg[1] <= 1800) {
        const int vel = f.n == 3 ? constrain(f.arg[2], 0L, 6000L) : 0;
        pan.mover(constrain(f.arg[0], 300L, 1500L), vel);
        tilt.mover(constrain(f.arg[1], 400L, 1400L), vel);
      }
      break;
    case 'L':
      if (f.n == 1 && f.arg[0] >= 0 && f.arg[0] <= 2) {
        piscadas = 0;
        if (f.arg[0] == 2) {
          digitalWrite(LED_BUILTIN, LOW);
          piscadas = 10; proximaPiscada = agora + 80;
        } else digitalWrite(LED_BUILTIN, f.arg[0] ? HIGH : LOW);
      }
      break;
    case 'X':
      if (f.n == 0) {
        parar();
        pan.mover(pan.posDeg10(), 0);
        tilt.mover(tilt.posDeg10(), 0);
      }
      break;
    case 'C':
      if (f.n != 2) break;
      switch (f.arg[0]) {
        case 1: parametros.velPadraoUs = grausParaUs(constrain(f.arg[1], 1L, 600L)); break;
        case 2: parametros.velMinUs = grausParaUs(constrain(f.arg[1], 0L, 200L)); break;
        case 3: parametros.accUs = grausParaUs(constrain(f.arg[1], 20L, 3000L)); break;
        case 4: parametros.deadUs = constrain(f.arg[1], 0L, 20L); break;
        case 5: parametros.backlashUs = constrain(f.arg[1], 0L, 120L); break;
        case 6: parametros.soltarMs = constrain(f.arg[1], 0L, 600L) * 100; break;
      }
      break;
  }
}

void setup() {
  pinMode(STBY, OUTPUT);
  pinMode(PWMA, OUTPUT); pinMode(AIN1, OUTPUT); pinMode(AIN2, OUTPUT);
  pinMode(PWMB, OUTPUT); pinMode(BIN1, OUTPUT); pinMode(BIN2, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT); digitalWrite(LED_BUILTIN, LOW);
  parar();
  Serial.begin(9600);  // Somente recepcao pelo D0. Nenhuma resposta no D1.
  parametros.velPadraoUs = grausParaUs(150);
  // Timer1 somente nos servos D9/D10; PWM dos motores permanece em D3/D6.
  pan.begin(9, 300, 1500, 900, &parametros);
  tilt.begin(10, 400, 1400, 900, &parametros);
}

void loop() {
  uint32_t agora = millis();
  if (agora - ultimoByte > 250) parser = ProtoParser();
  uint8_t limite = 32;
  while (limite-- && Serial.available()) {
    ProtoFrame f;
    const char c = static_cast<char>(Serial.read());
    ultimoByte = millis();
    if (parser.feed(c, f)) receber(f, ultimoByte);
  }
  agora = millis();
  if ((esperando || atualE || atualD) && agora - ultimoMotor >= WATCHDOG_MS) parar();
  if (esperando && static_cast<int32_t>(agora - liberarEm) >= 0) {
    esperando = false;
    aplicar();
  }
  pan.atualizar(agora, false);
  tilt.atualizar(agora, false);
  if (piscadas && static_cast<int32_t>(agora - proximaPiscada) >= 0) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    --piscadas; proximaPiscada = agora + 80;
    if (!piscadas) digitalWrite(LED_BUILTIN, LOW);
  }
}
