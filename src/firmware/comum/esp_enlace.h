#pragma once
// ====================================================================================
// ESP32: ENLACE COM O NANO (UART1 em IO43 TX / IO44 RX)
// ====================================================================================
// - Caixa de correio "ultimo valor vence" para servo (S) e motores (M): nao importa quantos
//   comandos o celular mande, o fio serial (9600 baud!) so recebe 1 quadro a cada LINK_INTERVALO_MS.
//   (Um quadro de servo tem ~14 bytes = ~15 ms a 9600 baud.)
// - <X> (parada) fura a fila e cancela qualquer <M> pendente.
// - Le e interpreta a telemetria do Nano (A, H, B, N, K, R) e guarda para a API /api/stats.
// - Ping com medicao de ida e volta (RTT) e estatistica de perda para o POC 1.
// ====================================================================================
#include <Arduino.h>
#include "rover_protocolo.h"
#include "esp_config.h"

#define ENLACE_LOG_N 14

struct EnlaceStats {
  uint32_t tx = 0, rx = 0, rxErros = 0;
  uint32_t ultimoRxMs = 0, ultimoHbMs = 0;
  long nanoUp = -1, nanoRx = 0, nanoErr = 0;
  long vbat = 0, vmin = 0;
  long motE = 0, motD = 0;
  long resetFlags = -1;
  // ping
  uint32_t pings = 0, acks = 0, rttMinUs = 0xFFFFFFFF, rttMaxUs = 0, rttUltUs = 0;
  uint64_t rttSomaUs = 0;
};

class EnlaceNano {
 public:
  EnlaceStats st;
  String logRx[ENLACE_LOG_N];
  uint8_t logPos = 0;

  void begin() {
    Serial2.setRxBufferSize(512);
    Serial2.begin(LINK_BAUD, SERIAL_8N1, PIN_LINK_RX, PIN_LINK_TX);
  }

  void loop(uint32_t agora) {
    if (boxS.pend && agora - ultS >= LINK_INTERVALO_MS) { long a[3] = {boxS.a, boxS.b, boxS.c}; raw('S', a, boxS.c ? 3 : 2); boxS.pend = false; ultS = agora; }
    if (boxM.pend && agora - ultM >= LINK_INTERVALO_MS) { long a[2] = {boxM.a, boxM.b}; raw('M', a, 2); boxM.pend = false; ultM = agora; }

    while (Serial2.available() > 0) {
      ProtoFrame f;
      if (parser.feed((char)Serial2.read(), f)) tratar(f, agora);
    }
    st.rxErros = parser.erros;
  }

  // ---- saida ----
  void servo(long p10, long t10, long vel) {
    boxS.a = constrain(p10, 0, 1800); boxS.b = constrain(t10, 0, 1800); boxS.c = constrain(vel, 0, 6000); boxS.pend = true;
  }
  void motores(long e, long d) { boxM.a = constrain(e, -255, 255); boxM.b = constrain(d, -255, 255); boxM.pend = true; }
  void parar() { boxM.pend = false; raw('X', nullptr, 0); }
  void ping() {
    long s = ++pingSeq;
    pingT[s & 15] = micros();
    st.pings++;
    long a[1] = {s};
    raw('P', a, 1);
  }
  void config(long id, long v) { long a[2] = {id, v}; raw('C', a, 2); }
  void zerarPing() { st.pings = st.acks = 0; st.rttMinUs = 0xFFFFFFFF; st.rttMaxUs = 0; st.rttSomaUs = 0; st.rttUltUs = 0; }

  // Despacha um quadro vindo do celular (WebSocket / HTTP). Somente comandos conhecidos passam.
  bool despachar(const ProtoFrame &f) {
    switch (f.cmd) {
      case 'S': if (f.n >= 2) { servo(f.arg[0], f.arg[1], f.n >= 3 ? f.arg[2] : 0); return true; } break;
      case 'M': if (f.n >= 2) { motores(f.arg[0], f.arg[1]); return true; } break;
      case 'X': parar(); return true;
      case 'C': if (f.n >= 2) { config(f.arg[0], f.arg[1]); return true; } break;
      case 'P': ping(); return true;
    }
    return false;
  }

  uint32_t idadeRxMs(uint32_t agora) const { return st.ultimoRxMs ? agora - st.ultimoRxMs : 0xFFFFFFFF; }
  uint32_t idadeHbMs(uint32_t agora) const { return st.ultimoHbMs ? agora - st.ultimoHbMs : 0xFFFFFFFF; }

 private:
  struct Box { long a = 0, b = 0, c = 0; bool pend = false; };
  Box boxS, boxM;
  uint32_t ultS = 0, ultM = 0, pingT[16] = {0};
  long pingSeq = 0;
  ProtoParser parser;

  void raw(char cmd, const long *a, uint8_t n) {
    char out[44];
    uint8_t k = protoFormatar(out, cmd, a, n);
    out[k++] = '\n';
    Serial2.write((const uint8_t *)out, k);
    st.tx++;
  }

  void tratar(const ProtoFrame &f, uint32_t agora) {
    st.rx++;
    st.ultimoRxMs = agora;
    char txt[44];
    protoFormatar(txt, f.cmd, f.arg, f.n);
    logRx[logPos] = String(txt);
    logPos = (logPos + 1) % ENLACE_LOG_N;

    switch (f.cmd) {
      case 'A':
        if (f.n >= 1) {
          uint32_t t0 = pingT[f.arg[0] & 15];
          uint32_t rtt = micros() - t0;
          st.acks++; st.rttUltUs = rtt; st.rttSomaUs += rtt;
          if (rtt < st.rttMinUs) st.rttMinUs = rtt;
          if (rtt > st.rttMaxUs) st.rttMaxUs = rtt;
        }
        break;
      case 'H': if (f.n >= 3) { st.nanoUp = f.arg[0]; st.nanoRx = f.arg[1]; st.nanoErr = f.arg[2]; st.ultimoHbMs = agora; } break;
      case 'B': if (f.n >= 2) { st.vbat = f.arg[0]; st.vmin = f.arg[1]; } break;
      case 'N': if (f.n >= 2) { st.motE = f.arg[0]; st.motD = f.arg[1]; } break;
      case 'R': if (f.n >= 1) st.resetFlags = f.arg[0]; break;
      default: break;
    }
  }
};
