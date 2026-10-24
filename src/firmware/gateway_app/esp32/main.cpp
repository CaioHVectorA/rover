#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include "esp_camera.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// ====================================================================================
// ESP32-S3: GATEWAY COMPLETO COM CÂMERA OV5640 / OV2640 & WEBSOCKET PORTA 81
// ====================================================================================
// 1. Streaming de Vídeo:
//    - /stream  : Stream MJPEG contínuo (Navegadores Web / FPV)
//    - /capture : Snapshot JPEG unitário de alta velocidade (App Mobile Expo)
// 2. Servidor WebSocket (Porta 81): Telemetria, ping e controle de servos SG90
// 3. Serial2 (IO43 TX / IO44 RX a 9600 baud): Repasse para o Arduino Nano
// ====================================================================================

const char* ssid     = "PET_ELETRICA";
const char* password = "1478965P";

WebServer server(80);
WebSocketsServer wsServer(81);

// ==================== PINAGEM DA CÂMERA ESP32-S3 (Freenove / N16R8) ====================
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     15
#define SIOD_GPIO_NUM      4
#define SIOC_GPIO_NUM      5
#define Y9_GPIO_NUM       16
#define Y8_GPIO_NUM       17
#define Y7_GPIO_NUM       18
#define Y6_GPIO_NUM       12
#define Y5_GPIO_NUM       10
#define Y4_GPIO_NUM        8
#define Y3_GPIO_NUM        9
#define Y2_GPIO_NUM       11
#define VSYNC_GPIO_NUM     6
#define HREF_GPIO_NUM      7
#define PCLK_GPIO_NUM     13

bool cameraOk = false;

const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>Rover Pan-Tilt & Câmera FPV</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --accent: #00e676;
      --accent-blue: #29b6f6;
      --text: #f0f6fc;
      --text-sub: #8b949e;
      --border: #30363d;
      --danger: #ff5252;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 15px; display: flex; justify-content: center; min-height: 100vh; }
    .container { width: 100%; max-width: 440px; display: flex; flex-direction: column; gap: 15px; }
    .header { text-align: center; padding: 6px 0; }
    .header h1 { font-size: 1.3rem; font-weight: 700; color: var(--text); }
    .header p { font-size: 0.75rem; color: var(--text-sub); }
    .video-box { width: 100%; height: 240px; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; position: relative; }
    .video-feed { width: 100%; height: 100%; object-fit: cover; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
    .angle-display { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .angle-box { background: #0d1117; border: 1px solid var(--border); border-radius: 10px; padding: 10px; text-align: center; }
    .angle-title { font-size: 0.7rem; font-weight: 600; color: var(--text-sub); text-transform: uppercase; }
    .angle-val { font-size: 2rem; font-weight: 800; color: var(--accent); margin-top: 2px; }
    .angle-val span { font-size: 1rem; color: var(--text-sub); font-weight: 400; }
    .btn { width: 100%; padding: 12px; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 700; cursor: pointer; transition: 0.15s active; display: flex; align-items: center; justify-content: center; gap: 8px; }
    .btn-primary { background: var(--accent-blue); color: #000; }
    .btn-secondary { background: #21262d; color: var(--text); border: 1px solid var(--border); }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Rover FPV & Pan-Tilt</h1>
      <p>Câmera ESP32-S3 + Servos Nano</p>
    </div>

    <!-- Feed de Vídeo -->
    <div class="video-box">
      <img class="video-feed" src="/stream" onerror="this.src='/capture?t='+Date.now()" alt="Feed de Vídeo">
    </div>

    <!-- Mostrador de Ângulos -->
    <div class="card">
      <div class="angle-display">
        <div class="angle-box">
          <div class="angle-title">PAN (Horizontal)</div>
          <div class="angle-val"><span id="txtPan">90</span><span>°</span></div>
        </div>
        <div class="angle-box">
          <div class="angle-title">TILT (Vertical)</div>
          <div class="angle-val"><span id="txtTilt">90</span><span>°</span></div>
        </div>
      </div>

      <button class="btn btn-secondary" onclick="sendSet(90, 90)">🎯 Centralizar Servos (90°, 90°)</button>

      <div class="grid-2">
        <button class="btn btn-secondary" onclick="sendSet(45, 90)">◀ Esquerda (45°)</button>
        <button class="btn btn-secondary" onclick="sendSet(135, 90)">▶ Direita (135°)</button>
        <button class="btn btn-secondary" onclick="sendSet(90, 130)">▲ Cima (130°)</button>
        <button class="btn btn-secondary" onclick="sendSet(90, 60)">▼ Baixo (60°)</button>
      </div>
    </div>
  </div>

  <script>
    function sendSet(p, t) {
      document.getElementById('txtPan').innerText = p;
      document.getElementById('txtTilt').innerText = t;
      fetch(`/set?p=${p}&t=${t}`).catch(e => console.error(e));
    }
  </script>
</body>
</html>
)rawliteral";

void handleRoot() { server.send(200, "text/html", INDEX_HTML); }

void handleSet() {
  if (server.hasArg("p") && server.hasArg("t")) {
    int p = server.arg("p").toInt();
    int t = server.arg("t").toInt();

    p = constrain(p, 0, 180);
    t = constrain(t, 0, 180);

    Serial2.printf("<%d,%d>\n", p, t);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "ERRO");
  }
}

// ==================== ENDPOINT /view (Visualizador FPV Fullscreen para WebView) ====================
void handleView() {
  String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>*{margin:0;padding:0;box-sizing:border-box;background:#000;overflow:hidden;}html,body{width:100%;height:100%;display:flex;align-items:center;justify-content:center;}img{width:100%;height:100%;object-fit:cover;}</style></head><body><img src='/stream' onerror=\"this.src='/capture?t='+Date.now()\"></body></html>";
  server.send(200, "text/html", html);
}

// ==================== ENDPOINT /resolution (Muda resolução dinamicamente) ====================
void handleResolution() {
  if (!cameraOk) {
    server.send(503, "text/plain", "Camera offline");
    return;
  }
  sensor_t * s = esp_camera_sensor_get();
  if (!s) {
    server.send(500, "text/plain", "Sensor nao encontrado");
    return;
  }
  String val = server.arg("val");
  val.toLowerCase();
  framesize_t fs = FRAMESIZE_HQVGA;
  if (val == "qqvga")      fs = FRAMESIZE_QQVGA; // 160x120
  else if (val == "hqvga") fs = FRAMESIZE_HQVGA; // 240x176
  else if (val == "qvga")  fs = FRAMESIZE_QVGA;  // 320x240
  else if (val == "cif")   fs = FRAMESIZE_CIF;   // 400x296
  else if (val == "vga")   fs = FRAMESIZE_VGA;   // 640x480
  else if (val == "svga")  fs = FRAMESIZE_SVGA;  // 800x600
  else if (val == "hd")    fs = FRAMESIZE_HD;    // 1280x720
  else {
    server.send(400, "text/plain", "Resolucao invalida");
    return;
  }
  s->set_framesize(s, fs);
  Serial.printf("[CAMERA] Resolucao alterada para: %s\n", val.c_str());
  server.send(200, "text/plain", "OK");
}

// ==================== ENDPOINT /capture (Snapshot JPEG) ====================
void handleCapture() {
  if (!cameraOk) {
    server.send(503, "text/plain", "Camera offline");
    return;
  }
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Falha de captura");
    return;
  }
  WiFiClient client = server.client();
  String header = "HTTP/1.1 200 OK\r\n";
  header += "Content-Type: image/jpeg\r\n";
  header += "Content-Length: " + String(fb->len) + "\r\n";
  header += "Access-Control-Allow-Origin: *\r\n\r\n";
  server.sendContent(header);
  client.write(fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

// ==================== ENDPOINT /stream (MJPEG Stream) ====================
void handleStream() {
  if (!cameraOk) {
    server.send(503, "text/plain", "Camera offline");
    return;
  }
  WiFiClient client = server.client();
  String header = "HTTP/1.1 200 OK\r\n";
  header += "Content-Type: multipart/x-mixed-replace; boundary=123456789000000000000987654321\r\n";
  header += "Access-Control-Allow-Origin: *\r\n\r\n";
  server.sendContent(header);

  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) break;

    String part = "--123456789000000000000987654321\r\n";
    part += "Content-Type: image/jpeg\r\n";
    part += "Content-Length: " + String(fb->len) + "\r\n\r\n";
    client.print(part);
    client.write(fb->buf, fb->len);
    client.print("\r\n");

    esp_camera_fb_return(fb);
    delay(5);
  }
}

// ==================== EVENTOS DO WEBSOCKET (PORTA 81 - APP EXPO) ====================
void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.printf("[WS] App #%u Desconectado\n", num);
      break;

    case WStype_CONNECTED: {
      IPAddress ip = wsServer.remoteIP(num);
      Serial.printf("[WS] App #%u Conectado de %s\n", num, ip.toString().c_str());
      wsServer.sendTXT(num, "{\"type\":\"telemetry\",\"status\":\"online\"}");
      Serial2.println("<90,90>"); // Centraliza ao conectar no App!
      break;
    }

    case WStype_TEXT: {
      String msg = String((char*)payload);

      if (msg.indexOf("\"ping\"") >= 0) {
        wsServer.sendTXT(num, "{\"type\":\"pong\"}");
        return;
      }

      if (msg.indexOf("\"servo\"") >= 0) {
        int idxPan = msg.indexOf("\"pan\":");
        int idxTilt = msg.indexOf("\"tilt\":");

        if (idxPan >= 0 && idxTilt >= 0) {
          int pan = msg.substring(idxPan + 6).toInt();
          int tilt = msg.substring(idxTilt + 7).toInt();

          pan = constrain(pan, 0, 180);
          tilt = constrain(tilt, 0, 180);

          Serial2.printf("<%d,%d>\n", pan, tilt);
        }
        return;
      }

      if (msg.indexOf("\"drive\"") >= 0) {
        int idxCmd = msg.indexOf("\"cmd\":\"");
        if (idxCmd >= 0) {
          char cmd = msg.charAt(idxCmd + 7);
          Serial2.printf("<D,%c>\n", cmd);
        }
        return;
      }

      if (msg.indexOf("\"resolution\"") >= 0) {
        sensor_t * s = esp_camera_sensor_get();
        if (s) {
          if (msg.indexOf("\"VGA\"") >= 0 || msg.indexOf("\"vga\"") >= 0) s->set_framesize(s, FRAMESIZE_VGA);
          else if (msg.indexOf("\"QVGA\"") >= 0 || msg.indexOf("\"qvga\"") >= 0) s->set_framesize(s, FRAMESIZE_QVGA);
          else if (msg.indexOf("\"HQVGA\"") >= 0 || msg.indexOf("\"hqvga\"") >= 0) s->set_framesize(s, FRAMESIZE_HQVGA);
          else if (msg.indexOf("\"SVGA\"") >= 0 || msg.indexOf("\"svga\"") >= 0) s->set_framesize(s, FRAMESIZE_SVGA);
          else if (msg.indexOf("\"HD\"") >= 0 || msg.indexOf("\"hd\"") >= 0) s->set_framesize(s, FRAMESIZE_HD);
          else if (msg.indexOf("\"QQVGA\"") >= 0 || msg.indexOf("\"qqvga\"") >= 0) s->set_framesize(s, FRAMESIZE_QQVGA);
        }
        return;
      }
      break;
    }

    default:
      break;
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Desativa protecao BOD
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, 44, 43); // RX=44, TX=43 para o transistor BC337

  // Dispara centralização imediata em 90 90 no boot
  delay(200);
  Serial2.println("<90,90>");

  // 1. Inicializa a Câmera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA; // Aloca buffers DMA no tamanho maximo (VGA 640x480)
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 16;
  config.fb_count = 2;

  if (!psramFound()) {
    config.frame_size = FRAMESIZE_QVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.fb_count = 1;
    config.jpeg_quality = 20;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[CAMERA] Falha de inicializacao: 0x%x\n", err);
    cameraOk = false;
  } else {
    Serial.println("[CAMERA] Camera inicializada com sucesso!");
    cameraOk = true;

    // Inicia por padrão em QVGA (320x240)
    sensor_t * s = esp_camera_sensor_get();
    if (s) {
      s->set_framesize(s, FRAMESIZE_QVGA);
    }
  }

  // 2. Wi-Fi
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP("Rover-PanTilt", "12345678");
  WiFi.begin(ssid, password);

  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 5000) { 
    delay(200); 
  }

  Serial.println("\n[SISTEMA CONECTADO]");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("IP Wi-Fi (Rede Local): http://");
    Serial.println(WiFi.localIP());
  }
  Serial.print("IP Ponto de Acesso (AP): http://");
  Serial.println(WiFi.softAPIP());

  // 3. Servidor Web HTTP (Porta 80)
  server.on("/", handleRoot);
  server.on("/view", handleView);
  server.on("/set", handleSet);
  server.on("/capture", handleCapture);
  server.on("/stream", handleStream);
  server.on("/resolution", handleResolution);
  server.begin();

  // 4. Servidor WebSocket (Porta 81 - Para o App Mobile Expo)
  wsServer.begin();
  wsServer.onEvent(onWebSocketEvent);

  Serial.println("[GATEWAY PRONTO] Câmera, HTTP (80) e WebSocket (81) ativos!");
}

void loop() {
  server.handleClient();
  wsServer.loop();
}
