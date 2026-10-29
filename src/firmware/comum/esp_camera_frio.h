#pragma once
// ====================================================================================
// ESP32-S3-CAM: CAMERA "FRIA" + SERVIDOR DE VIDEO MJPEG
// ====================================================================================
// Onde esta o calor do OV5640 e o que fazemos em software (do maior efeito para o menor):
//  1. SONECA REAL: sem espectador por N s, escreve 0x3008=0x42 (software power-down do sensor):
//     ISP, PLL e compressor JPEG param (de ~140 mA para < 1 mA). Acorda sozinho no proximo /stream.
//  2. XCLK DINAMICO: o consumo CMOS e proporcional a frequencia e o pixel clock do sensor deriva do
//     XCLK. Ativo 12 MHz / Eco 8 MHz / Termico 6 MHz (padrao 20 MHz do exemplo da Espressif).
//  3. TETO DE FPS no servidor (ativo / eco / termico) + modo ECO (robo parado -> poucos quadros).
//  4. RESOLUCAO e QUALIDADE JPEG configuraveis em tempo real (menos pixels = menos trabalho do
//     sensor e menos banda); no modo TERMICO limita a QVGA.
//  5. GOVERNADOR TERMICO: le a temperatura interna do ESP32-S3 (temperatureRead). ATENCAO: nao e a
//     temperatura do OV5640 (o sensor nao tem leitura); e o melhor indicador disponivel sem
//     hardware extra. Acima de tempAlerta -> TERMICO; acima de tempCorte -> dorme ate esfriar.
//  6. Placa: CPU a 160 MHz, WiFi TX 15 dBm, so um radio (STA ou AP), WiFi sem sleep so quando preciso.
//  Servidor: esp_http_server em task propria (porta 82) -> o video NUNCA bloqueia o loop() do
//  WebSocket/serial (era o defeito do gateway anterior, com while() dentro do handler).
//  So 1 espectador de video por vez (um stream bloqueia a task do httpd). Feche o navegador
//  antes de abrir o app, ou use /capture.
// ====================================================================================
#include <Arduino.h>
#include <WebServer.h>
#include <Preferences.h>
#include "esp_camera.h"
#include "esp_http_server.h"
#include "esp_config.h"

#ifndef POC_ECO_APOS_S
#define POC_ECO_APOS_S 0           // 0 = modo eco desligado (POC 3: so assistindo); POC 4/6 definem 8
#endif
#define CAM_CFG_VERSAO 3

enum ModoCam : uint8_t { MODO_ATIVO = 0, MODO_ECO, MODO_DORMINDO, MODO_TERMICO };
static const char *MODO_NOME[] = {"ATIVO", "ECO", "DORMINDO", "TERMICO"};

static const char *RES_NOME[] = {"qqvga", "hqvga", "qvga", "cif", "vga", "svga", "hd"};
static const framesize_t RES_ENUM[] = {FRAMESIZE_QQVGA, FRAMESIZE_HQVGA, FRAMESIZE_QVGA, FRAMESIZE_CIF, FRAMESIZE_VGA, FRAMESIZE_SVGA, FRAMESIZE_HD};
static const char *RES_DESC[] = {"160x120", "240x176", "320x240", "400x296", "640x480", "800x600", "1280x720"};
#define RES_N 7
#define RES_IDX_QVGA 2

struct CamConfig {
  uint8_t versao = CAM_CFG_VERSAO;
  uint8_t res = RES_IDX_QVGA;           // indice em RES_NOME
  uint8_t qualidade = 20;               // JPEG 8..45  (MAIOR = mais comprimido = menos banda/trabalho)
  uint8_t xclkAtivo = 12, xclkEco = 8, xclkTermico = 6;   // MHz (6..20)
  uint8_t fpsAtivo = 20, fpsEco = 5, fpsTermico = 8;      // teto de FPS do stream
  uint8_t dormirApos_s = 3;             // sem espectador -> soneca (0 = nunca)
  uint8_t ecoApos_s = POC_ECO_APOS_S;   // sem comandos -> eco (0 = nunca)
  uint8_t tempAlerta = 68, tempCorte = 80;   // graus C (chip ESP32-S3)
  uint8_t governor = 1, espelho = 0, inverte = 0;
  int8_t  brilho = 0;
  uint16_t rotacao = 90;                // 0, 90, 180, 270 graus (camera deitada = 90 ou 270)
};

struct CamEstado {
  volatile ModoCam modo = MODO_ATIVO;
  volatile bool dormindo = false, forcadoTermico = false, ok = false, ov5640 = false;
  volatile int clientes = 0;
  volatile uint32_t ultClienteMs = 0, ultCaptureMs = 0, ultAtividadeMs = 0;
  volatile uint32_t frames = 0, bytes = 0, capUs = 0, ultFrameBytes = 0;
  uint8_t xclkAtual = 0;
  float tempChip = 0, fps = 0, kbps = 0;
  uint32_t jMs = 0, jFrames = 0, jBytes = 0;
};

static CamConfig camCfg;
static CamEstado camEst;
static SemaphoreHandle_t camMtx = nullptr;
static httpd_handle_t camHttpd = nullptr;

static inline framesize_t camResEnum() { return RES_ENUM[camCfg.res]; }
static inline void camNotificarAtividade() { camEst.ultAtividadeMs = millis(); }

static void camClamp() {
  camCfg.res = constrain(camCfg.res, 0, RES_N - 1);
  camCfg.qualidade = constrain(camCfg.qualidade, 8, 45);
  camCfg.xclkAtivo = constrain(camCfg.xclkAtivo, 6, 20);
  camCfg.xclkEco = constrain(camCfg.xclkEco, 6, 20);
  camCfg.xclkTermico = constrain(camCfg.xclkTermico, 6, 20);
  camCfg.fpsAtivo = constrain(camCfg.fpsAtivo, 1, 30);
  camCfg.fpsEco = constrain(camCfg.fpsEco, 1, 30);
  camCfg.fpsTermico = constrain(camCfg.fpsTermico, 1, 30);
  camCfg.tempAlerta = constrain(camCfg.tempAlerta, 45, 95);
  camCfg.tempCorte = constrain(camCfg.tempCorte, camCfg.tempAlerta + 3, 100);
  camCfg.brilho = constrain(camCfg.brilho, -2, 2);
  camCfg.governor = camCfg.governor ? 1 : 0;
  camCfg.espelho = camCfg.espelho ? 1 : 0;
  camCfg.inverte = camCfg.inverte ? 1 : 0;
  if (camCfg.rotacao != 0 && camCfg.rotacao != 90 && camCfg.rotacao != 180 && camCfg.rotacao != 270) camCfg.rotacao = 90;
}

static void camCarregar() {
  Preferences p;
  if (!p.begin("rovercam", true)) return;
  if (p.getBytesLength("cfg") == sizeof(CamConfig)) {
    CamConfig c;
    p.getBytes("cfg", &c, sizeof(c));
    if (c.versao == CAM_CFG_VERSAO) camCfg = c;
  }
  p.end();
  camClamp();
}
static void camSalvar() {
  Preferences p;
  if (!p.begin("rovercam", false)) return;
  p.putBytes("cfg", &camCfg, sizeof(camCfg));
  p.end();
}

// ---------------------------------------------------------------- controle do sensor
static uint8_t camXclkDoModo(ModoCam m) {
  return m == MODO_ECO ? camCfg.xclkEco : (m == MODO_TERMICO ? camCfg.xclkTermico : camCfg.xclkAtivo);
}
static uint8_t camFpsDoModo(ModoCam m) {
  return m == MODO_ECO ? camCfg.fpsEco : (m == MODO_TERMICO ? camCfg.fpsTermico : camCfg.fpsAtivo);
}
static uint32_t camIntervaloMs() { return 1000 / max<uint8_t>(1, camFpsDoModo(camEst.modo)); }

static framesize_t camResEfetiva(ModoCam m) {
  uint8_t idx = camCfg.res;
  if (m == MODO_TERMICO && idx > RES_IDX_QVGA) idx = RES_IDX_QVGA;
  return RES_ENUM[idx];
}

// Chamar com camMtx tomado.
static void camDormirL() {
  sensor_t *s = esp_camera_sensor_get();
  if (s && camEst.ov5640) s->set_reg(s, 0x3008, 0xFF, 0x42);   // bit 6: software power-down
  camEst.dormindo = true;
}
static void camAcordarL() {
  sensor_t *s = esp_camera_sensor_get();
  if (s && camEst.ov5640) s->set_reg(s, 0x3008, 0xFF, 0x02);
  camEst.dormindo = false;
  vTaskDelay(pdMS_TO_TICKS(40));
  for (int i = 0; i < 2; i++) { camera_fb_t *fb = esp_camera_fb_get(); if (fb) esp_camera_fb_return(fb); }   // descarta quadros velhos/ruins
}

static void camAplicarModo(ModoCam m) {
  if (!camEst.ok) return;
  xSemaphoreTake(camMtx, portMAX_DELAY);
  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    uint8_t mhz = camXclkDoModo(m);
    if (m != MODO_DORMINDO && mhz != camEst.xclkAtual) { s->set_xclk(s, LEDC_TIMER_0, mhz); camEst.xclkAtual = mhz; }
    framesize_t r = camResEfetiva(m);
    if (m != MODO_DORMINDO && s->status.framesize != r) s->set_framesize(s, r);
  }
  if (m == MODO_DORMINDO) { if (!camEst.dormindo) camDormirL(); }
  else if (camEst.dormindo) camAcordarL();
  camEst.modo = m;
  xSemaphoreGive(camMtx);
}

// Aplica a configuracao atual ao sensor (apos mudar parametros). Mantem o modo vigente.
static void camReaplicar() {
  if (!camEst.ok) return;
  xSemaphoreTake(camMtx, portMAX_DELAY);
  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    s->set_quality(s, camCfg.qualidade);
    s->set_hmirror(s, camCfg.espelho);
    s->set_vflip(s, camCfg.inverte);
    s->set_brightness(s, camCfg.brilho);
    if (!camEst.dormindo) {
      uint8_t mhz = camXclkDoModo(camEst.modo);
      if (mhz != camEst.xclkAtual) { s->set_xclk(s, LEDC_TIMER_0, mhz); camEst.xclkAtual = mhz; }
      framesize_t r = camResEfetiva(camEst.modo);
      if (s->status.framesize != r) s->set_framesize(s, r);
    }
  }
  xSemaphoreGive(camMtx);
}

static bool camIniciar() {
  camMtx = xSemaphoreCreateMutex();
  camCarregar();

  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0;
  c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0 = CAM_Y2; c.pin_d1 = CAM_Y3; c.pin_d2 = CAM_Y4; c.pin_d3 = CAM_Y5;
  c.pin_d4 = CAM_Y6; c.pin_d5 = CAM_Y7; c.pin_d6 = CAM_Y8; c.pin_d7 = CAM_Y9;
  c.pin_xclk = CAM_XCLK; c.pin_pclk = CAM_PCLK; c.pin_vsync = CAM_VSYNC; c.pin_href = CAM_HREF;
  c.pin_sccb_sda = CAM_SIOD; c.pin_sccb_scl = CAM_SIOC;
  c.pin_pwdn = CAM_PWDN; c.pin_reset = CAM_RESET;
  c.xclk_freq_hz = (int)camCfg.xclkAtivo * 1000000;
  c.pixel_format = PIXFORMAT_JPEG;
  c.frame_size = FRAMESIZE_HD;                 // buffers dimensionados para o maior quadro; troca em tempo real
  c.jpeg_quality = camCfg.qualidade;
  c.fb_count = 2;
  c.fb_location = CAMERA_FB_IN_PSRAM;
  c.grab_mode = CAMERA_GRAB_LATEST;            // sempre o quadro mais novo (latencia minima)
  if (!psramFound()) { c.frame_size = FRAMESIZE_QVGA; c.fb_location = CAMERA_FB_IN_DRAM; c.fb_count = 1; }

  esp_err_t e = esp_camera_init(&c);
  if (e != ESP_OK) { Serial.printf("[CAM] falha init 0x%x (camera conectada? cabo flat?)\n", e); camEst.ok = false; return false; }

  camEst.ok = true;
  camEst.xclkAtual = camCfg.xclkAtivo;
  sensor_t *s = esp_camera_sensor_get();
  camEst.ov5640 = s && s->id.PID == OV5640_PID;
  Serial.printf("[CAM] sensor PID=0x%04x (%s)  soneca por software: %s\n", s ? s->id.PID : 0, camEst.ov5640 ? "OV5640" : "outro", camEst.ov5640 ? "SIM" : "NAO (so OV5640)");
  camEst.modo = MODO_ATIVO;
  camEst.ultClienteMs = millis();
  s->set_framesize(s, camResEnum());
  camReaplicar();
  return true;
}

// ---------------------------------------------------------------- governador (chamar a cada ~500 ms)
static void camGovernorTick(uint32_t agora) {
  if (!camEst.ok) return;
  float t = temperatureRead();
  camEst.tempChip = t;

  // estatisticas de janela
  uint32_t dt = agora - camEst.jMs;
  if (dt >= 1000) {
    uint32_t f = camEst.frames, b = camEst.bytes;
    camEst.fps = (f - camEst.jFrames) * 1000.0f / dt;
    camEst.kbps = (b - camEst.jBytes) * 8.0f / dt;   // bits/ms = kbit/s
    camEst.jMs = agora; camEst.jFrames = f; camEst.jBytes = b;
  }

  bool clientes = camEst.clientes > 0 || (camEst.ultCaptureMs && (agora - camEst.ultCaptureMs) < 3000);
  if (clientes) camEst.ultClienteMs = agora;

  if (camCfg.governor) {
    if (t >= camCfg.tempCorte) camEst.forcadoTermico = true;
    else if (camEst.forcadoTermico && t < camCfg.tempCorte - 8) camEst.forcadoTermico = false;
  } else camEst.forcadoTermico = false;

  ModoCam novo;
  if (camEst.forcadoTermico) novo = MODO_DORMINDO;
  else if (camCfg.dormirApos_s && !clientes && (agora - camEst.ultClienteMs) > (uint32_t)camCfg.dormirApos_s * 1000) novo = MODO_DORMINDO;
  else if (camCfg.governor && (t >= camCfg.tempAlerta || (camEst.modo == MODO_TERMICO && t >= camCfg.tempAlerta - 5))) novo = MODO_TERMICO;
  else if (camCfg.ecoApos_s && (agora - camEst.ultAtividadeMs) > (uint32_t)camCfg.ecoApos_s * 1000) novo = MODO_ECO;
  else novo = MODO_ATIVO;

  if (novo != camEst.modo) {
    Serial.printf("[CAM] modo %s -> %s (chip %.1f C)\n", MODO_NOME[camEst.modo], MODO_NOME[novo], t);
    camAplicarModo(novo);
  }
}

// ---------------------------------------------------------------- servidor de video (porta 82)
static bool camPreparar() {
  if (!camEst.ok || camEst.forcadoTermico) return false;
  if (camEst.dormindo || camEst.modo == MODO_DORMINDO) camAplicarModo(MODO_ATIVO);
  return true;
}

static esp_err_t camStreamHandler(httpd_req_t *req) {
  if (!camPreparar()) { httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "camera indisponivel (offline ou superaquecida)"); return ESP_FAIL; }
  httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=frame");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  camEst.clientes++;
  esp_err_t res = ESP_OK;
  char part[96];
  uint32_t proximo = millis();
  while (true) {
    if (camEst.forcadoTermico) break;
    if (camEst.dormindo) camAplicarModo(MODO_ATIVO);

    int32_t espera = (int32_t)(proximo - millis());
    if (espera > 0) vTaskDelay(pdMS_TO_TICKS(espera));
    proximo = max<uint32_t>(proximo + camIntervaloMs(), millis());

    uint32_t t0 = micros();
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) { res = ESP_FAIL; break; }
    camEst.capUs = (camEst.capUs * 7 + (micros() - t0)) / 8;
    size_t n = fb->len;
    int hl = snprintf(part, sizeof(part), "\r\n--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", (unsigned)n);
    res = httpd_resp_send_chunk(req, part, hl);
    if (res == ESP_OK) res = httpd_resp_send_chunk(req, (const char *)fb->buf, n);
    esp_camera_fb_return(fb);
    if (res != ESP_OK) break;
    camEst.frames++; camEst.bytes += n; camEst.ultFrameBytes = n;
  }
  camEst.clientes--;
  camEst.ultClienteMs = millis();
  return res;
}

static esp_err_t camCaptureHandler(httpd_req_t *req) {
  if (!camPreparar()) { httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "camera indisponivel"); return ESP_FAIL; }
  camEst.ultCaptureMs = millis();
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) { httpd_resp_send_500(req); return ESP_FAIL; }
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  esp_err_t r = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return r;
}

static void camIniciarServidor() {
  httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
  cfg.server_port = 82;
  cfg.ctrl_port = 32769;
  cfg.stack_size = 6144;
  cfg.core_id = 0;                 // WiFi no core 0; loop() (WebSocket + serial) fica livre no core 1
  cfg.max_open_sockets = 4;
  cfg.lru_purge_enable = true;
  httpd_uri_t uStream = {"/stream", HTTP_GET, camStreamHandler, nullptr};
  httpd_uri_t uCap = {"/capture", HTTP_GET, camCaptureHandler, nullptr};
  if (httpd_start(&camHttpd, &cfg) == ESP_OK) {
    httpd_register_uri_handler(camHttpd, &uStream);
    httpd_register_uri_handler(camHttpd, &uCap);
    Serial.println("[CAM] video em :82/stream  e  :82/capture");
  } else Serial.println("[CAM] httpd nao iniciou");
}

// ---------------------------------------------------------------- API HTTP de configuracao (porta 80)
static String camCfgJson() {
  char b[450];
  snprintf(b, sizeof(b),
    "{\"res\":\"%s\",\"rot\":%u,\"q\":%u,\"xclk\":%u,\"xclk_eco\":%u,\"xclk_t\":%u,\"fps\":%u,\"fps_eco\":%u,\"fps_t\":%u,"
    "\"sleep_s\":%u,\"eco_s\":%u,\"t_alerta\":%u,\"t_corte\":%u,\"gov\":%u,\"hmirror\":%u,\"vflip\":%u,\"bright\":%d}",
    RES_NOME[camCfg.res], camCfg.rotacao, camCfg.qualidade, camCfg.xclkAtivo, camCfg.xclkEco, camCfg.xclkTermico,
    camCfg.fpsAtivo, camCfg.fpsEco, camCfg.fpsTermico, camCfg.dormirApos_s, camCfg.ecoApos_s,
    camCfg.tempAlerta, camCfg.tempCorte, camCfg.governor, camCfg.espelho, camCfg.inverte, camCfg.brilho);
  return String(b);
}

static String camStatsJson() {
  char b[380];
  snprintf(b, sizeof(b),
    "{\"ok\":%d,\"ov5640\":%d,\"modo\":\"%s\",\"dormindo\":%d,\"forcado\":%d,\"clientes\":%d,\"fps\":%.1f,\"kbps\":%.0f,"
    "\"kb_frame\":%.1f,\"cap_ms\":%.1f,\"xclk\":%u,\"res\":\"%s\",\"res_px\":\"%s\",\"rot\":%u,\"teto_fps\":%u,\"frames\":%lu}",
    camEst.ok, camEst.ov5640, MODO_NOME[camEst.modo], camEst.dormindo, camEst.forcadoTermico, camEst.clientes,
    camEst.fps, camEst.kbps, camEst.ultFrameBytes / 1024.0f, camEst.capUs / 1000.0f, camEst.xclkAtual,
    RES_NOME[camCfg.res], RES_DESC[camCfg.res], camCfg.rotacao, camFpsDoModo(camEst.modo), (unsigned long)camEst.frames);
  return String(b);
}

static void camPreset(const String &n) {
  if (n == "frio")            { camCfg.res = 2; camCfg.qualidade = 26; camCfg.xclkAtivo = 8;  camCfg.xclkEco = 6; camCfg.fpsAtivo = 12; camCfg.fpsEco = 3; }
  else if (n == "equilibrado"){ camCfg.res = 4; camCfg.qualidade = 20; camCfg.xclkAtivo = 12; camCfg.xclkEco = 8; camCfg.fpsAtivo = 15; camCfg.fpsEco = 5; }
  else if (n == "qualidade")  { camCfg.res = 5; camCfg.qualidade = 12; camCfg.xclkAtivo = 16; camCfg.xclkEco = 8; camCfg.fpsAtivo = 15; camCfg.fpsEco = 5; }
  else if (n == "maximo")     { camCfg.res = 6; camCfg.qualidade = 10; camCfg.xclkAtivo = 20; camCfg.xclkEco = 10; camCfg.fpsAtivo = 15; camCfg.fpsEco = 5; }
  camClamp();
}

static void camLogComando(WebServer &w) {
  Serial.printf("[WEB RX HTTP %lu ms] %s", (unsigned long)millis(), w.uri().c_str());
  for (int i = 0; i < w.args(); ++i)
    Serial.printf(" %s=%s", w.argName(i).c_str(), w.arg(i).c_str());
  Serial.println();
}

static void camRotas(WebServer &w) {
  w.on("/api/cam/cfg", HTTP_GET, [&w]() { w.send(200, "application/json", camCfgJson()); });

  w.on("/api/cam/set", HTTP_GET, [&w]() {
    camLogComando(w);
    if (w.hasArg("res")) {
      String r = w.arg("res"); r.toLowerCase();
      for (int i = 0; i < RES_N; i++) if (r == RES_NOME[i]) camCfg.res = i;
    }
    if (w.hasArg("rot"))      camCfg.rotacao     = w.arg("rot").toInt();
    if (w.hasArg("q"))        camCfg.qualidade   = w.arg("q").toInt();
    if (w.hasArg("xclk"))     camCfg.xclkAtivo   = w.arg("xclk").toInt();
    if (w.hasArg("xclk_eco")) camCfg.xclkEco     = w.arg("xclk_eco").toInt();
    if (w.hasArg("xclk_t"))   camCfg.xclkTermico = w.arg("xclk_t").toInt();
    if (w.hasArg("fps"))      camCfg.fpsAtivo    = w.arg("fps").toInt();
    if (w.hasArg("fps_eco"))  camCfg.fpsEco      = w.arg("fps_eco").toInt();
    if (w.hasArg("fps_t"))    camCfg.fpsTermico  = w.arg("fps_t").toInt();
    if (w.hasArg("sleep_s"))  camCfg.dormirApos_s = w.arg("sleep_s").toInt();
    if (w.hasArg("eco_s"))    camCfg.ecoApos_s   = w.arg("eco_s").toInt();
    if (w.hasArg("t_alerta")) camCfg.tempAlerta  = w.arg("t_alerta").toInt();
    if (w.hasArg("t_corte"))  camCfg.tempCorte   = w.arg("t_corte").toInt();
    if (w.hasArg("gov"))      camCfg.governor    = w.arg("gov").toInt();
    if (w.hasArg("hmirror"))  camCfg.espelho     = w.arg("hmirror").toInt();
    if (w.hasArg("vflip"))    camCfg.inverte     = w.arg("vflip").toInt();
    if (w.hasArg("bright"))   camCfg.brilho      = w.arg("bright").toInt();
    camClamp();
    camReaplicar();
    if (w.hasArg("save")) camSalvar();
    w.send(200, "application/json", camCfgJson());
  });

  w.on("/api/cam/preset", HTTP_GET, [&w]() {
    camLogComando(w);
    camPreset(w.arg("n"));
    camReaplicar();
    w.send(200, "application/json", camCfgJson());
  });

  // EXPERIMENTAL: le/escreve registrador do sensor. Ex.: /api/cam/reg?r=0x3008  |  ?r=0x3008&v=0x42&m=0xFF
  w.on("/api/cam/reg", HTTP_GET, [&w]() {
    camLogComando(w);
    sensor_t *s = esp_camera_sensor_get();
    if (!s || !w.hasArg("r")) { w.send(400, "text/plain", "uso: ?r=0xREG[&v=0xVAL[&m=0xMASK]]"); return; }
    int reg = strtol(w.arg("r").c_str(), nullptr, 0);
    xSemaphoreTake(camMtx, portMAX_DELAY);
    if (w.hasArg("v")) s->set_reg(s, reg, w.hasArg("m") ? (int)strtol(w.arg("m").c_str(), nullptr, 0) : 0xFF, (int)strtol(w.arg("v").c_str(), nullptr, 0));
    int val = s->get_reg(s, reg, 0xFF);
    xSemaphoreGive(camMtx);
    char b[64]; snprintf(b, sizeof(b), "{\"reg\":\"0x%04X\",\"val\":\"0x%02X\"}", reg, val & 0xFF);
    w.send(200, "application/json", b);
  });
}
