// ====================================================================================
// ROVER TOTAL - NANO: MOTORES 4WD (TB6612FNG) + PAN/TILT (SG90)
// ====================================================================================
// - Recebe do ESP32:
//     <M,esq,dir>      -> Controle diferencial dos motores 4WD (-255..255)
//     <S,pan10,tilt10> -> Controle dos servos Pan/Tilt (0..1800 decimos de grau)
//     <X>              -> Parada de emergencia
//     <C,id,valor>     -> Configuracao de parametros dinamicos
// - Pinos TB6612FNG:
//     PWMA=D3, AIN1=D4, AIN2=D5, PWMB=D6, BIN1=D7, BIN2=D8, STBY=D12
// - Pinos Servos SG90:
//     Pan=D9, Tilt=D10
// - Enlace Serial:
//     RX no pino D0 (Hardware UART) a 9600 baud
// ====================================================================================
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "nano_enlace.h"
#include "nano_diag.h"
#include "nano_servos.h"
#include "nano_motores.h"

// Motores TB6612
#define PIN_PWMA 3
#define PIN_AIN1 4
#define PIN_AIN2 5
#define PIN_PWMB 6
#define PIN_BIN1 7
#define PIN_BIN2 8
#define PIN_STBY 12

// Servos SG90
#define PINO_PAN   9
#define PINO_TILT  10
#define PAN_MIN   200
#define PAN_MAX  1600
#define TILT_MIN  400
#define TILT_MAX 1400

static MotoresTB6612 mot;
static ServoParams   sp;
static ServoSuave    pan, tilt;

static uint32_t ultHb = 0, ultBat = 0, ultN = 0;

static void configurar(long id, long v) {
  // 1..6: Servos
  switch (id) {
    case 1: sp.velPadraoUs = grausParaUs(constrain(v, 1, 600)); break;
    case 2: sp.velMinUs    = grausParaUs(constrain(v, 0, 200)); break;
    case 3: sp.accUs       = grausParaUs(constrain(v, 20, 3000)); break;
    case 4: sp.deadUs      = constrain(v, 0, 20); break;
    case 5: sp.backlashUs  = constrain(v, 0, 120); break;
    case 6: sp.soltarMs    = (uint16_t)(constrain(v, 0, 600) * 100); break;
    // 10..16: Motores
    case 10: mot.P.rampaMs    = constrain(v, 100, 5000); break;
    case 11: mot.P.pwmMin     = constrain(v, 0, 120); break;
    case 12: mot.P.pwmMax     = constrain(v, 50, 255); break;
    case 13: mot.P.deadMs     = constrain(v, 0, 1000); break;
    case 14: mot.P.watchdogMs = constrain(v, 0, 5000); break;
    case 15: mot.P.invEsq     = v != 0; break;
    case 16: mot.P.invDir     = v != 0; break;
    default: return;
  }
  tx('K', id, v);
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(150);
  digitalWrite(LED_BUILTIN, LOW);

  enlaceBegin();

  // Inicia Servos
  pan.begin(PINO_PAN,   PAN_MIN,  PAN_MAX,  900, &sp);
  tilt.begin(PINO_TILT, TILT_MIN, TILT_MAX, 900, &sp);

  // Inicia Motores
  mot.begin(PIN_PWMA, PIN_AIN1, PIN_AIN2, PIN_PWMB, PIN_BIN1, PIN_BIN2, PIN_STBY);
  mot.P.rampaMs = 800;
  mot.P.deadMs = 150;
  mot.P.watchdogMs = 600;

  delay(200);
  Serial.println(F("== ROVER TOTAL: MOTORES + PAN/TILT =="));
  Serial.print(F("Ultimo reset: ")); Serial.println(diagResetTexto(g_resetFlags));
  tx('R', g_resetFlags);
}

void loop() {
  uint32_t agora = millis();
  ProtoFrame f;

  while (enlaceLer(f)) {
    switch (f.cmd) {
      case 'M':
        if (f.n >= 2) mot.comando((int)f.arg[0], (int)f.arg[1], agora);
        break;
      case 'S':
        if (f.n >= 2) {
          long vel = (f.n >= 3) ? f.arg[2] : 0;
          pan.mover((int)f.arg[0], (int)vel);
          tilt.mover((int)f.arg[1], (int)vel);
        }
        break;
      case 'X':
        mot.paradaImediata();
        pan.mover(pan.posDeg10(), 0);
        tilt.mover(tilt.posDeg10(), 0);
        break;
      case 'C':
        if (f.n >= 2) configurar(f.arg[0], f.arg[1]);
        break;
      case 'P':
        if (f.n >= 1) tx('A', f.arg[0]);
        break;
      case 'L':
        if (f.n >= 1) {
          if (f.arg[0] == 2) digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
          else digitalWrite(LED_BUILTIN, f.arg[0] ? HIGH : LOW);
          tx('L', digitalRead(LED_BUILTIN) ? 1 : 0);
        }
        break;
    }
  }

  // Atualiza Servos e Motores (congela calculo durante inrush de arrancada dos motores)
  bool arranco = mot.arrancando(agora);
  pan.atualizar(agora, arranco);
  tilt.atualizar(agora, arranco);
  mot.atualizar(agora);

  // Telemetria
  static uint32_t ultAmostra = 0;
  if (agora - ultAmostra >= 5) { ultAmostra = agora; bateriaLer_mV(); }

  if (agora - ultBat >= 2000) { ultBat = agora; long v = bateriaLer_mV(); tx('B', v, bateriaMinimoEReset()); }
  if (!mot.parado() && agora - ultN >= 200) { ultN = agora; tx('N', mot.saidaEsq(), mot.saidaDir()); }
  if (agora - ultHb >= 1000) { ultHb = agora; tx('H', agora / 1000, enlaceRx, enlaceErros()); }
}
