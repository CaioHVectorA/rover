#pragma once
// ====================================================================================
// ESP32: APLICACAO COMUM DOS POCs 2, 3, 4 e 6
// ====================================================================================
// Cada POC define antes de incluir este arquivo:
//   POC_NOME   "pocN_..."          POC_AP "Rover-POCn"
//   POC_CAM    0/1  camera + video (porta 82)
//   POC_SERVO  0/1  painel Pan/Tilt (exige o Nano com servos)
//   POC_MOTOR  0/1  painel de motores (exige o Nano com motores)
// Portas: 80 = painel + API  |  81 = WebSocket (comandos)  |  82 = video MJPEG (task propria)
// WebSocket: texto com quadros do protocolo, ex. "<S,900,900,0>", "<M,100,100>", "<X>".
// ====================================================================================
#include <Arduino.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include "esp_config.h"
#include "esp_rede.h"
#include "esp_painel.h"

#ifndef POC_CAM
#define POC_CAM 0
#endif
#ifndef POC_SERVO
#define POC_SERVO 0
#endif
#ifndef POC_MOTOR
#define POC_MOTOR 0
#endif
#define POC_USA_NANO (POC_SERVO || POC_MOTOR)

#if POC_CAM
#include "esp_camera_frio.h"
#endif
#if POC_USA_NANO
#include "esp_enlace.h"
static EnlaceNano enlace;
#endif

static WebServer web(80);
static WebSocketsServer wsServer(81);
static uint32_t tGov = 0;

static void apiInfo() {
  String caps = "[";
#if POC_CAM
  caps += "\"cam\",";
#endif
#if POC_SERVO
  caps += "\"servo\",";
#endif
#if POC_MOTOR
  caps += "\"motor\",";
#endif
  if (caps.length() > 1) caps.remove(caps.length() - 1);
  caps += "]";
  String info = String("{\"poc\":\"") + POC_NOME + "\",\"ip\":\"" + redeEndereco + "\",\"caps\":" + caps;
#if CONTROLE_D0_DIRETO
  info += ",\"controle\":{\"retorno\":false,\"pwm_max\":120,\"pan_min\":30,\"pan_max\":150,\"tilt_min\":40,\"tilt_max\":140,\"vel_servo\":150}";
#endif
  web.send(200, "application/json", info + "}");
}

static void apiStats() {
  uint32_t agora = millis();
  String s = "{\"sys\":{";
  s += "\"temp\":" + String(temperatureRead(), 1);
  s += ",\"cpu\":" + String(getCpuFrequencyMhz());
  s += ",\"heap\":" + String(ESP.getFreeHeap());
  s += ",\"psram\":" + String(ESP.getFreePsram());
  s += ",\"rssi\":" + String(WiFi.getMode() == WIFI_STA ? WiFi.RSSI() : 0);
  s += ",\"up\":" + String(agora / 1000) + "}";
#if POC_USA_NANO
  const EnlaceStats &e = enlace.st;
  uint32_t hb = enlace.idadeHbMs(agora);
  s += ",\"link\":{";
#if ENLACE_SO_IDA
  s += "\"retorno\":false,";
#else
  s += "\"retorno\":true,";
#endif
  s += "\"tx\":" + String(e.tx) + ",\"rx\":" + String(e.rx) + ",\"err\":" + String(e.rxErros);
  s += ",\"hb_age\":" + String(hb == 0xFFFFFFFF ? -1L : (long)hb);
  s += ",\"vbat\":" + String(e.vbat) + ",\"vmin\":" + String(e.vmin);
  s += ",\"mot_e\":" + String(e.motE) + ",\"mot_d\":" + String(e.motD);
  s += ",\"reset\":" + String(e.resetFlags);
  s += ",\"led\":" + String(e.ledNano);
  s += ",\"tx_inv\":" + String(enlace.txInvertido ? 1 : 0);
  s += ",\"rtt_ult\":" + String(e.rttUltUs);
  s += ",\"nano_up\":" + String(e.nanoUp) + "}";
#endif
#if POC_CAM
  s += ",\"cam\":" + camStatsJson();
#endif
  s += "}";
  web.send(200, "application/json", s);
}

#if POC_USA_NANO
// Valida e encaminha um quadro de texto vindo do celular.
static bool tratarQuadro(const char *txt, size_t n, const char *origem) {
  // Serial USB de diagnostico; Serial2 permanece exclusiva do enlace com o Nano.
  Serial.printf("[WEB RX %s %lu ms] ", origem, (unsigned long)millis());
  Serial.write((const uint8_t *)txt, n);
  Serial.println();
  static ProtoParser p;
  ProtoFrame f;
  bool ok = false;
  for (size_t i = 0; i < n; i++) if (p.feed(txt[i], f)) { ok = enlace.despachar(f) || ok; }
  if (ok) {
#if POC_CAM
    camNotificarAtividade();
#endif
  }
  return ok;
}
#endif

static void aoEventoWS(uint8_t num, WStype_t type, uint8_t *payload, size_t len) {
  switch (type) {
    case WStype_CONNECTED:
      Serial.printf("[WS] cliente %u conectado\n", num);
#if POC_CAM
      camNotificarAtividade();
#endif
      break;
    case WStype_DISCONNECTED:
      Serial.printf("[WS] cliente %u saiu\n", num);
#if POC_MOTOR
      if (wsServer.connectedClients() == 0) enlace.parar();      // perdeu o controle -> para
#endif
      break;
    case WStype_TEXT:
#if POC_USA_NANO
      tratarQuadro((const char *)payload, len, "WS");
#endif
      break;
    default: break;
  }
}

void setup() {
  logIniciar();
  setCpuFrequencyMhz(POC_CPU_MHZ);
  Serial.printf("\n== %s ==\n", POC_NOME);
#if POC_USA_NANO
  enlace.begin();
#endif
#if POC_CAM
  camIniciar();
#endif
  redeIniciar(POC_AP);

  web.on("/", []() { web.sendHeader("Cache-Control", "no-store"); web.send_P(200, "text/html; charset=utf-8", PAINEL_HTML); });
  web.on("/api/info", apiInfo);
  web.on("/api/stats", apiStats);
#if POC_USA_NANO
  web.on("/api/cmd", []() {                       // fallback HTTP e testes com curl: /api/cmd?f=<S,900,900>
    String f = web.arg("f");
    bool ok = tratarQuadro(f.c_str(), f.length(), "HTTP");
    web.send(ok ? 200 : 400, "text/plain", ok ? "ok" : "quadro invalido");
  });
  web.on("/api/link/invert", []() {
    Serial.printf("[WEB RX HTTP %lu ms] /api/link/invert inv=%s\n", (unsigned long)millis(), web.hasArg("inv") ? web.arg("inv").c_str() : "alternar");
    if (web.hasArg("inv")) enlace.setInversaoTx(web.arg("inv") == "1");
    else enlace.setInversaoTx(!enlace.txInvertido);
    web.send(200, "application/json", String("{\"tx_inv\":") + (enlace.txInvertido ? 1 : 0) + "}");
  });
#endif
#if POC_CAM
  camRotas(web);
  camIniciarServidor();
#endif
  web.begin();
  wsServer.begin();
  wsServer.onEvent(aoEventoWS);
  Serial.println("[PRONTO] painel :80  websocket :81");
}

void loop() {
  uint32_t agora = millis();
  web.handleClient();
  wsServer.loop();
#if POC_USA_NANO
  enlace.loop(agora);
#endif
#if POC_CAM
  if (agora - tGov >= 500) { tGov = agora; camGovernorTick(agora); }
#endif
}
