// ====================================================================================
// POC 2 / POC 4 - NANO: PAN/TILT CONTROLADO (servos suaves, anti-rebolado)
// ====================================================================================
// - Servos SG90 Pan D9 / Tilt D10 com ServoSuave (ver nano_servos.h).
// - Comandos: <S,pan10,tilt10[,vel10]>, <C,id,valor> (ids 1..6), <P,n>, <X>.
// - Telemetria: <H,...> a 1 Hz, <R,flags> no boot, <K,id,valor> a cada configuracao.
// - Centraliza em 90/90 ao ligar. Aceita os mesmos comandos pelo Serial Monitor (9600).
// - Mesmo firmware serve ao POC 2 (sem video) e ao POC 4 (com video).
// ====================================================================================
#include <Arduino.h>
#include <SoftwareSerial.h>   // citado aqui para o PlatformIO (LDF) localizar a biblioteca
#include <Servo.h>
#include "nano_enlace.h"
#include "nano_diag.h"
#include "nano_servos.h"

#define PINO_PAN   9
#define PINO_TILT  10
// Limites mecanicos (decimos de grau). Ajuste conforme o case 3D (evita bater no batente).
#define PAN_MIN   100
#define PAN_MAX  1700
#define TILT_MIN  300
#define TILT_MAX 1500

static ServoParams sp;
static ServoSuave  pan, tilt;
static uint32_t ultHb = 0;

static void configurar(long id, long v) {
  switch (id) {
    case 1: sp.velPadraoUs = grausParaUs(constrain(v, 1, 600)); break;
    case 2: sp.velMinUs    = grausParaUs(constrain(v, 0, 200)); break;
    case 3: sp.accUs       = grausParaUs(constrain(v, 20, 3000)); break;
    case 4: sp.deadUs      = constrain(v, 0, 20); break;
    case 5: sp.backlashUs  = constrain(v, 0, 120); break;
    case 6: sp.soltarMs    = (uint16_t)(constrain(v, 0, 600) * 100); break;
    default: return;
  }
  tx('K', id, v);
}

void setup() {
  enlaceBegin();
  pan.begin(PINO_PAN,   PAN_MIN,  PAN_MAX,  900, &sp);
  tilt.begin(PINO_TILT, TILT_MIN, TILT_MAX, 900, &sp);
  delay(400);
  Serial.println(F("== NANO: PAN/TILT SUAVE =="));
  Serial.print(F("Ultimo reset: ")); Serial.println(diagResetTexto(g_resetFlags));
  tx('R', g_resetFlags);
}

void loop() {
  ProtoFrame f;
  while (enlaceLer(f)) {
    switch (f.cmd) {
      case 'S':
        if (f.n >= 2) { long vel = (f.n >= 3) ? f.arg[2] : 0; pan.mover((int)f.arg[0], (int)vel); tilt.mover((int)f.arg[1], (int)vel); }
        break;
      case 'C': if (f.n >= 2) configurar(f.arg[0], f.arg[1]); break;
      case 'P': if (f.n >= 1) tx('A', f.arg[0]); break;
      case 'X': pan.mover(pan.posDeg10(), 0); tilt.mover(tilt.posDeg10(), 0); break;   // para onde estiver
    }
  }

  uint32_t agora = millis();
  pan.atualizar(agora, false);
  tilt.atualizar(agora, false);

  if (agora - ultHb >= 1000) {
    ultHb = agora;
    tx('H', agora / 1000, enlaceRx, enlaceErros());
  }
}
