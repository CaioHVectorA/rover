// ====================================================================================
// POC 6 - NANO: MOTORES CONTROLADOS PELO ESP32 (joystick / D-pad no celular)
// ====================================================================================
// - <M,esq,dir> a ~10 Hz enquanto o dedo esta no joystick. WATCHDOG: sem <M> por 600 ms (padrao)
//   a saida desce em rampa ate zero (queda de Wi-Fi, app fechado, celular travado).
// - <X> = parada de emergencia IMEDIATA (solta os motores sem rampa).
// - <C,id,valor> ids 10..16 (rampa, PWM min/max, tempo morto, watchdog, inversoes).
// - Telemetria: <B,mV,minmV> (2 s), <N,esq,dir> (5 Hz em movimento), <H,...> (1 Hz), <R,flags> no boot.
// - Aceita os mesmos quadros pelo Serial Monitor (9600): ex. <M,120,120>
// ====================================================================================
#include <Arduino.h>
#include <SoftwareSerial.h>   // citado aqui para o PlatformIO (LDF) localizar a biblioteca
#include "nano_enlace.h"
#include "nano_diag.h"
#include "nano_motores.h"

#define PIN_PWMA 3
#define PIN_AIN1 4
#define PIN_AIN2 5
#define PIN_PWMB 6
#define PIN_BIN1 7
#define PIN_BIN2 8
#define PIN_STBY 12

static MotoresTB6612 mot;
static uint32_t ultHb = 0, ultBat = 0, ultN = 0;

static void configurar(long id, long v) {
  switch (id) {
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
  enlaceBegin();
  mot.begin(PIN_PWMA, PIN_AIN1, PIN_AIN2, PIN_PWMB, PIN_BIN1, PIN_BIN2, PIN_STBY);
  mot.P.rampaMs = 800;
  mot.P.deadMs = 150;
  mot.P.watchdogMs = 600;
  delay(100);
  Serial.println(F("== NANO: MOTORES CONTROLADOS =="));
  Serial.print(F("Ultimo reset: ")); Serial.println(diagResetTexto(g_resetFlags));
  tx('R', g_resetFlags);
}

void loop() {
  uint32_t agora = millis();
  ProtoFrame f;
  while (enlaceLer(f)) {
    switch (f.cmd) {
      case 'M': if (f.n >= 2) mot.comando((int)f.arg[0], (int)f.arg[1], agora); break;
      case 'X': mot.paradaImediata(); break;
      case 'C': if (f.n >= 2) configurar(f.arg[0], f.arg[1]); break;
      case 'P': if (f.n >= 1) tx('A', f.arg[0]); break;
    }
  }

  mot.atualizar(agora);

  static uint32_t ultAmostra = 0;
  if (agora - ultAmostra >= 5) { ultAmostra = agora; bateriaLer_mV(); }   // minimo da janela pega o sag

  if (agora - ultBat >= 2000) { ultBat = agora; long v = bateriaLer_mV(); tx('B', v, bateriaMinimoEReset()); }
  if (!mot.parado() && agora - ultN >= 200) { ultN = agora; tx('N', mot.saidaEsq(), mot.saidaDir()); }
  if (agora - ultHb >= 1000) { ultHb = agora; tx('H', agora / 1000, enlaceRx, enlaceErros()); }
}
