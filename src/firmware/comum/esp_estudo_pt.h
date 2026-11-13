#pragma once
// ====================================================================================
// ESP32: ESTUDO DE CASO DE JITTER PAN/TILT (GERADOR DETERMINISTICO LOCAL)
// ====================================================================================
// Gera movimentos controlados diretamente no loop() do ESP32 (sem variacao de Wi-Fi
// ou setInterval do navegador), permitindo isolar em bancada se o tremor vem de:
//   1. EST_PULSO_1X       : Um unico <S> por trecho (A -> B -> Centro), sem pacotes no meio.
//   2. EST_RADAR_EXTREMOS : Varredura continua A <-> B com 1 unico <S> por perna.
//   3. EST_RADAR_BUG_420  : Passos incrementais a cada passoMs forcando vel=420 deg/s
//                           (reproduz o efeito anda-e-para do tracking incremental).
//   4. EST_RADAR_CASADO   : Passos incrementais a cada passoMs com horizonte a frente e
//                           velocidade casada (~1.06x) para nao zerar vAt no Nano.
// Requer Zero alteracoes no Arduino Nano (usa exclusivamente <S,p10,t10,vel10>).
// ====================================================================================
#include <Arduino.h>
#include <math.h>
#include "esp_enlace.h"

#if defined(CONTROLE_D0_DIRETO) && CONTROLE_D0_DIRETO
static constexpr long EST_PAN_MIN  = 300,  EST_PAN_MAX  = 1500;
static constexpr long EST_TILT_MIN = 400,  EST_TILT_MAX = 1400;
#else
static constexpr long EST_PAN_MIN  = 200,  EST_PAN_MAX  = 1600;
static constexpr long EST_TILT_MIN = 400,  EST_TILT_MAX = 1400;
#endif

enum EstudoModo : uint8_t {
  EST_OFF = 0,
  EST_PULSO_1X = 1,
  EST_RADAR_EXTREMOS = 2,
  EST_RADAR_BUG_420 = 3,
  EST_RADAR_CASADO = 4
};

class EspEstudoPT {
 public:
  EstudoModo modo = EST_OFF;
  uint8_t eixo = 0;         // 0 = Pan, 1 = Tilt
  long a10 = 600, b10 = 1200, centro10 = 900, fixo10 = 900;
  long velDegS = 60;
  uint16_t passoMs = 90;
  uint16_t pausaMs = 250;
  uint32_t ciclos = 0;

  void iniciar(uint8_t m, uint8_t ax, long amplDeg, long vel, uint16_t pMs, uint16_t pauseMs, EnlaceNano &enlace, uint32_t agora) {
    if (m < EST_PULSO_1X || m > EST_RADAR_CASADO) { parar(); return; }
    modo = static_cast<EstudoModo>(m);
    eixo = ax ? 1 : 0;
    const long limMin = eixo == 0 ? EST_PAN_MIN : EST_TILT_MIN;
    const long limMax = eixo == 0 ? EST_PAN_MAX : EST_TILT_MAX;
    const long fixMin = eixo == 0 ? EST_TILT_MIN : EST_PAN_MIN;
    const long fixMax = eixo == 0 ? EST_TILT_MAX : EST_PAN_MAX;

    centro10 = 900;
    long curMov = eixo == 0 ? enlace.st.sUltPan10 : enlace.st.sUltTilt10;
    long curFix = eixo == 0 ? enlace.st.sUltTilt10 : enlace.st.sUltPan10;
    if (curMov < limMin || curMov > limMax) curMov = centro10;
    if (curFix < fixMin || curFix > fixMax) curFix = 900;
    fixo10 = curFix;

    long meia10 = constrain(amplDeg, 10L, 120L) * 5L;   // metade da amplitude em decimos de grau
    a10 = constrain(centro10 - meia10, limMin, limMax);
    b10 = constrain(centro10 + meia10, limMin, limMax);
    if (b10 - a10 < 100) {
      a10 = constrain(centro10 - 150, limMin, limMax);
      b10 = constrain(centro10 + 150, limMin, limMax);
    }

    velDegS = constrain(vel, 15L, 500L);
    passoMs = constrain(pMs, (uint16_t)(LINK_INTERVALO_MS + 5), (uint16_t)250);
    pausaMs = constrain(pauseMs, (uint16_t)0, (uint16_t)1500);
    ciclos = 0;

    if (modo == EST_PULSO_1X || modo == EST_RADAR_EXTREMOS) {
      fase = 0;
      long dist10 = labs(a10 - curMov);
      enviarEixo(enlace, a10, velDegS * 10L);
      proxTrocaMs = agora + duracaoTrechoMs(dist10, velDegS) + pausaMs;
    } else {
      // Modos incrementais partem da posicao atual ou de a10 indo em direcao a b10.
      posF = (float)constrain(curMov, a10, b10);
      dir = (posF >= (float)(a10 + b10) * 0.5f) ? -1 : +1;
      ultTickMs = agora;
      retomarEmMs = agora;
      enviarIncremental(enlace, agora, 0.0f);
    }
  }

  void parar() {
    modo = EST_OFF;
  }

  bool ativo() const { return modo != EST_OFF; }

  void loop(uint32_t agora, EnlaceNano &enlace) {
    if (modo == EST_OFF) return;

    if (modo == EST_PULSO_1X) {
      if (static_cast<int32_t>(agora - proxTrocaMs) < 0) return;
      if (fase == 0) {
        fase = 1;
        enviarEixo(enlace, b10, velDegS * 10L);
        proxTrocaMs = agora + duracaoTrechoMs(labs(b10 - a10), velDegS) + pausaMs;
      } else if (fase == 1) {
        fase = 2;
        enviarEixo(enlace, centro10, velDegS * 10L);
        proxTrocaMs = agora + duracaoTrechoMs(labs(centro10 - b10), velDegS) + 200;
      } else {
        ciclos++;
        modo = EST_OFF;
      }
      return;
    }

    if (modo == EST_RADAR_EXTREMOS) {
      if (static_cast<int32_t>(agora - proxTrocaMs) < 0) return;
      fase = (fase == 0) ? 1 : 0;
      if (fase == 0) ciclos++;
      long alvo = (fase == 0) ? a10 : b10;
      enviarEixo(enlace, alvo, velDegS * 10L);
      proxTrocaMs = agora + duracaoTrechoMs(labs(b10 - a10), velDegS) + pausaMs;
      return;
    }

    // EST_RADAR_BUG_420 ou EST_RADAR_CASADO
    if (agora - ultTickMs < passoMs) return;
    uint32_t dtMs = agora - ultTickMs;
    ultTickMs = agora;
    if (static_cast<int32_t>(agora - retomarEmMs) < 0) return;
    if (dtMs > 300) dtMs = passoMs;
    enviarIncremental(enlace, agora, dtMs / 1000.0f);
  }

  String json() const {
    static const char *NOMES[] = {"off", "pulso_1x", "extremos", "passos_420", "passos_casados"};
    const char *nome = (modo <= EST_RADAR_CASADO) ? NOMES[modo] : "off";
    char b[160];
    snprintf(b, sizeof(b),
      "{\"ativo\":%d,\"modo\":%u,\"nome\":\"%s\",\"eixo\":%u,\"vel\":%ld,\"passo_ms\":%u,\"ciclos\":%lu}",
      ativo() ? 1 : 0, (unsigned)modo, nome, (unsigned)eixo, velDegS, (unsigned)passoMs, (unsigned long)ciclos);
    return String(b);
  }

 private:
  uint8_t fase = 0;
  int8_t dir = 1;
  float posF = 900.0f;
  uint32_t proxTrocaMs = 0, ultTickMs = 0, retomarEmMs = 0;

  static uint32_t duracaoTrechoMs(long dist10, long velDeg) {
    if (velDeg < 1) velDeg = 1;
    // dist10 / 10 / velDeg * 1000 = dist10 * 100 / velDeg
    uint32_t cruiseMs = (uint32_t)((dist10 * 100UL) / (unsigned long)velDeg);
    uint32_t rampMs = (uint32_t)(((unsigned long)velDeg * 1000UL) / 750UL);
    return cruiseMs + rampMs + 140UL;
  }

  void enviarEixo(EnlaceNano &enlace, long val10, long vel10) {
    if (eixo == 0) enlace.servo(constrain(val10, EST_PAN_MIN, EST_PAN_MAX), fixo10, vel10);
    else enlace.servo(fixo10, constrain(val10, EST_TILT_MIN, EST_TILT_MAX), vel10);
  }

  void enviarIncremental(EnlaceNano &enlace, uint32_t agora, float dtSec) {
    bool virou = false;
    long pontoVirada = 0;
    if (dtSec > 0.0f) {
      posF += (float)dir * ((float)velDegS * 10.0f) * dtSec;
      if (dir > 0 && posF >= (float)b10) {
        posF = (float)b10;
        dir = -1;
        retomarEmMs = agora + pausaMs;
        virou = true;
        pontoVirada = b10;
      } else if (dir < 0 && posF <= (float)a10) {
        posF = (float)a10;
        dir = +1;
        ciclos++;
        retomarEmMs = agora + pausaMs;
        virou = true;
        pontoVirada = a10;
      }
    }

    if (modo == EST_RADAR_BUG_420) {
      // Simula o padrao problematico: envia pequenos degraus com vel fixa em 420 deg/s.
      enviarEixo(enlace, virou ? pontoVirada : lroundf(posF), 4200);
      return;
    }

    long velCasada10 = constrain((long)lroundf((float)velDegS * 10.6f), 150L, 6000L);
    if (virou) {
      enviarEixo(enlace, pontoVirada, velCasada10);
      return;
    }

    // EST_RADAR_CASADO: projeta horizonte a frente (>= 5.5 deg enquanto em movimento) e casa velocidade (~1.06x).
    const long fimLeg = (dir > 0) ? b10 : a10;
    float leadMin = (float)velDegS * 10.0f * ((float)passoMs * 1.6f / 1000.0f);
    if (leadMin < 55.0f) leadMin = 55.0f;   // mantem dist fora da curva de frenagem sqrt(2*a*dist) ate perto do fim
    float alvoF = posF + (float)dir * leadMin;
    if ((dir > 0 && alvoF > (float)fimLeg) || (dir < 0 && alvoF < (float)fimLeg)) alvoF = (float)fimLeg;
    enviarEixo(enlace, lroundf(alvoF), velCasada10);
  }
};
