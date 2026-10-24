#pragma once
// ====================================================================================
// NANO: DIAGNOSTICO DE RESET E BATERIA
// ====================================================================================
// 1) Causa do ultimo reset. O Optiboot (bootloader do env nanoatmega328new) guarda o MCUSR
//    no registrador r2 antes de limpa-lo; capturamos r2 em .init0, antes de qualquer codigo C.
//    Bits: 1 = Power-on, 2 = Reset externo, 4 = BROWN-OUT (queda de tensao), 8 = Watchdog.
//    (Com bootloader antigo o valor pode ser lixo: confira com o Serial Monitor.)
// 2) Leitura da bateria 2S em A0 (divisor 100k/47k ou 10k/4k7 -> fator 3,128) com minimo
//    por janela: o MINIMO mostra o afundamento (sag) durante a arrancada dos motores.
// ====================================================================================
#include <Arduino.h>
#include <avr/io.h>

uint8_t g_resetFlags __attribute__((section(".noinit")));
void nanoCapturaReset(void) __attribute__((naked, used, section(".init0")));
void nanoCapturaReset(void) { __asm__ __volatile__("sts g_resetFlags, r2 \n\t" ::); }

static const char *diagResetTexto(uint8_t f) {
  if (f & 0x04) return "BROWN-OUT (queda de tensao!)";
  if (f & 0x08) return "Watchdog";
  if (f & 0x01) return "Power-on (ligou a energia)";
  if (f & 0x02) return "Reset externo (botao/USB)";
  return "indefinido";
}

#define PINO_BAT A0
#ifndef BAT_DIV
#define BAT_DIV 3.128f              // (100k+47k)/47k  =  (10k+4k7)/4k7
#endif
#ifndef VREF_MV
#define VREF_MV 5000.0f             // meca o 5V real com multimetro e ajuste aqui
#endif

static inline long batMinJanela = 99999;

// Fonte com impedancia ~32k: leitura dupla descarta o residuo do multiplexador. Ideal: 100 nF entre A0 e GND.
static inline long bateriaLer_mV() {
  analogRead(PINO_BAT);
  long s = 0;
  for (uint8_t i = 0; i < 4; i++) s += analogRead(PINO_BAT);
  float v = (s / 4.0f) * VREF_MV / 1023.0f * BAT_DIV;
  long mv = (long)v;
  if (mv < batMinJanela) batMinJanela = mv;
  return mv;
}
static inline long bateriaMinimoEReset() { long m = batMinJanela; batMinJanela = 99999; return m; }
