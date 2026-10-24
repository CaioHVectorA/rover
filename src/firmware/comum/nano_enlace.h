#pragma once
// ====================================================================================
// NANO: ENLACE SERIAL COM O ESP32
// ====================================================================================
// Modo padrao (montagem atual com BC337): RX invertido por software em D2 (SoftwareSerial).
//   - Respostas saem pelo UART de hardware (D1 TX -> divisor -> ESP IO44).
//   - O Serial Monitor (USB) tambem e aceito como entrada de comandos: da para testar sem ESP.
//
// Modo -DLINK_HW (melhor desempenho): RX no UART de hardware D0, sem BC337 (ESP TX direto,
//   3,3 V > 3,0 V minimo do Nano). Elimina o SoftwareSerial, que desabilita interrupcoes
//   durante cada byte recebido e causa tremor/"rebolado" no Servo. Desconecte o fio de D0
//   para gravar o Nano.
// ====================================================================================
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "rover_protocolo.h"

#ifndef LINK_BAUD
#define LINK_BAUD 9600
#endif
#define PINO_LINK_RX          2
#define PINO_LINK_TX_NAOUSADO A1   // reservado: nunca ligar nada aqui (evita conflito com PWM D3)

#ifdef LINK_HW
  #define LINK_IN Serial
#else
  static SoftwareSerial linkSw(PINO_LINK_RX, PINO_LINK_TX_NAOUSADO, true);
  #define LINK_IN linkSw
#endif

static ProtoParser pLink;
#ifndef LINK_HW
static ProtoParser pUsb;
#endif
static uint32_t enlaceRx = 0;
static uint32_t enlaceUltimoRxMs = 0;

static inline void enlaceBegin() {
  Serial.begin(LINK_BAUD);
#ifndef LINK_HW
  linkSw.begin(LINK_BAUD);
#endif
}

static inline uint16_t enlaceErros() {
#ifdef LINK_HW
  return pLink.erros;
#else
  return pLink.erros + pUsb.erros;
#endif
}

// Retorna true quando ha um quadro valido (chame em loop ate retornar false).
static inline bool enlaceLer(ProtoFrame &f) {
  while (LINK_IN.available() > 0) {
    if (pLink.feed((char)LINK_IN.read(), f)) { enlaceRx++; enlaceUltimoRxMs = millis(); return true; }
  }
#ifndef LINK_HW
  while (Serial.available() > 0) {
    if (pUsb.feed((char)Serial.read(), f)) { enlaceRx++; enlaceUltimoRxMs = millis(); return true; }
  }
#endif
  return false;
}

static inline void enviarQuadro(char cmd, const long *args, uint8_t n) {
  char out[44];
  uint8_t k = protoFormatar(out, cmd, args, n);
  out[k++] = '\n';
  Serial.write((const uint8_t *)out, k);
}
static inline void tx(char cmd)                              { enviarQuadro(cmd, nullptr, 0); }
static inline void tx(char cmd, long a)                      { long v[1] = {a};       enviarQuadro(cmd, v, 1); }
static inline void tx(char cmd, long a, long b)              { long v[2] = {a, b};    enviarQuadro(cmd, v, 2); }
static inline void tx(char cmd, long a, long b, long c)      { long v[3] = {a, b, c}; enviarQuadro(cmd, v, 3); }
