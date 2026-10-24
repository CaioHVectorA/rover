// ====================================================================================
// POC 1 - NANO: TESTE DE ENLACE RX/TX (lado do Nano)
// ====================================================================================
// - Recebe quadros do ESP32 (D2 invertido via BC337) e do Serial Monitor (USB, 9600).
// - <P,n>  -> responde <A,n> (ack, mede ida e volta)
// - qualquer outro quadro valido -> responde <K,codigo_do_comando,n_args>
// - 1x por segundo envia <H,uptime_s,quadros_rx,erros> (testa o sentido Nano -> ESP sozinho)
// - No boot envia <R,flags> com a causa do reset (power-on / BROWN-OUT / watchdog / externo)
// - LED D13 inverte a cada quadro recebido.
// ====================================================================================
#include <Arduino.h>
#include <SoftwareSerial.h>   // citado aqui para o PlatformIO (LDF) localizar a biblioteca
#include "nano_enlace.h"
#include "nano_diag.h"

static uint32_t ultHb = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  enlaceBegin();
  delay(50);
  Serial.println(F("== POC1 NANO: teste de enlace =="));
  Serial.print(F("Ultimo reset: ")); Serial.println(diagResetTexto(g_resetFlags));
  tx('R', g_resetFlags);
}

void loop() {
  ProtoFrame f;
  while (enlaceLer(f)) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    if (f.cmd == 'P' && f.n >= 1) tx('A', f.arg[0]);
    else                          tx('K', (long)f.cmd, f.n);
  }

  uint32_t agora = millis();
  if (agora - ultHb >= 1000) {
    ultHb = agora;
    tx('H', agora / 1000, enlaceRx, enlaceErros());
  }
}
