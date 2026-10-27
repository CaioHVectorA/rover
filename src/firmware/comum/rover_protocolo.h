#pragma once
// ====================================================================================
// PROTOCOLO SERIAL ESP32 <-> NANO  (v2, ASCII, quadros curtos)
// ====================================================================================
// Formato:  <C,a,b,c>     C = 1 caractere de comando, args = inteiros decimais (0..4)
// Qualquer byte fora de '<' ... '>' (ex.: '\n', logs) e ignorado. Compartilhado por ESP32 e Nano.
//
// ESP32 -> NANO                                    NANO -> ESP32
//   <P,n>              ping                          <A,n>              ack do ping
//   <L,estado>         LED D13 (0=off, 1=on, 2=alt)  <L,estado>         ack do estado do LED
//   <S,pan10,tilt10[,vel10]>  servos (decimos de grau, vel = decimos de grau/s, 0=padrao)
//   <M,esq,dir>        motores -255..255 (cada lado)  <H,up_s,rx,err>    heartbeat (1 Hz)
//   <X>                parada de emergencia           <B,mV,minmV>       bateria (a cada 2 s)
//   <C,id,valor>       configuracao (ver abaixo)      <N,esq,dir>        saida atual dos motores
//                                                     <K,id,valor>       ack de configuracao
//                                                     <R,flags>          causa do ultimo reset (MCUSR)
//
// IDs de configuracao <C,id,valor>:
//   Servos : 1 vel padrao (graus/s)    2 vel minima de aproximacao (graus/s)   3 aceleracao (graus/s^2)
//            4 deadband (us)           5 antifolga (us, 0=off)                 6 soltar parado (x100 ms, 0=nunca)
//   Motores: 10 rampa 0->100% (ms)     11 PWM minimo (0..120)   12 PWM maximo (50..255)
//            13 tempo morto na reversao (ms)   14 watchdog (ms, 0=off)   15 inverte esq (0/1)   16 inverte dir (0/1)
// ====================================================================================
#include <Arduino.h>
#include <stdlib.h>

#define PROTO_MAX_LEN  28
#define PROTO_MAX_ARGS 4

struct ProtoFrame {
  char    cmd;
  long    arg[PROTO_MAX_ARGS];
  uint8_t n;
};

class ProtoParser {
 public:
  uint16_t erros = 0;

  // Alimenta 1 byte. Retorna true quando um quadro completo e valido foi montado em f.
  bool feed(char c, ProtoFrame &f) {
    if (c == '<') { len = 0; ativo = true; return false; }
    if (!ativo) return false;
    if (c == '>') { ativo = false; buf[len] = 0; return parse(f); }
    if (len >= PROTO_MAX_LEN) { ativo = false; erros++; return false; }
    buf[len++] = c;
    return false;
  }

 private:
  char    buf[PROTO_MAX_LEN + 1];
  uint8_t len = 0;
  bool    ativo = false;

  bool parse(ProtoFrame &f) {
    if (len == 0) { erros++; return false; }
    f.cmd = buf[0];
    f.n = 0;
    char *p = buf + 1;
    while (*p == ',' && f.n < PROTO_MAX_ARGS) {
      p++;
      char *fim;
      long v = strtol(p, &fim, 10);
      if (fim == p) { erros++; return false; }
      f.arg[f.n++] = v;
      p = fim;
    }
    if (*p != 0) { erros++; return false; }
    return true;
  }
};

// Escreve "<C,a,b>" em out (>= 40 bytes). Retorna o tamanho.
static inline uint8_t protoFormatar(char *out, char cmd, const long *args, uint8_t n) {
  uint8_t k = 0;
  out[k++] = '<';
  out[k++] = cmd;
  for (uint8_t i = 0; i < n; i++) {
    out[k++] = ',';
    k += snprintf(out + k, 14, "%ld", args[i]);
  }
  out[k++] = '>';
  out[k] = 0;
  return k;
}
