/**
 * ============================================================================
 * PROJETO: Rover FPV - Telepresença & Sistemas Distribuídos
 * CÓDIGO: Firmware Cliente ESP32-S3 (Push de Vídeo Binário via WebSocket Seguro)
 * SERVIDOR DE DESTINO: wss://rover-relay-fpv-sp.fly.dev/ws/robot (Fly.io gru)
 * MICROCONTROLADOR: ESP32-S3 CAM (N16R8: 16MB Flash, 8MB Octal PSRAM)
 * SENSORES: OV2640 / OV5640 / OV3660
 * ============================================================================
 * 
 * PROTOCOLO BINÁRIO DE BAIXA LATÊNCIA (Two-Leg RTT):
 *  - O ESP32 envia pacotes binários diretamente ao Relay com 8 bytes de cabeçalho:
 *      [0..3]: uint32BE Frame ID (contador sequencial)
 *      [4..7]: uint32BE Timestamp ESP32 (millis())
 *      [8..N]: Bytes JPEG brutos capturados do sensor
 *  - O Relay responde com ACK de 9 bytes [0x01, Frame ID, Timestamp]
 *  - O ESP32 calcula instantaneamente o RTT: rtt_esp = millis() - Timestamp
 * ============================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include "esp_camera.h"

// ============================================================================
// 1. CONFIGURAÇÕES DE REDE WI-FI E RELAY NA NUVEM
// ============================================================================
const char* WIFI_SSID     = "PET_ELETRICA";
const char* WIFI_PASSWORD = "1478965P";

// Servidor Fly.io na região gru (São Paulo)
const char* RELAY_HOST    = "rover-relay-fpv-sp.fly.dev";
const int   RELAY_PORT    = 443;
const char* RELAY_PATH    = "/ws/robot";

// ============================================================================
// 2. PINAGEM DA CÂMERA NO ESP32-S3 CAM (N16R8)
// ============================================================================
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

// ============================================================================
// 3. OBJETOS E VARIÁVEIS GLOBAIS
// ============================================================================
WebSocketsClient webSocket;
bool isWsConnected = false;
uint32_t frameSequence = 0;
uint32_t lastFrameTime = 0;
uint32_t lastTelemetryTime = 0;
uint32_t lastRttMs = 0;

// Taxa máxima de envio de frames (alvo: 20 a 25 FPS para não saturar buffer)
const uint32_t FRAME_INTERVAL_MS = 40; // ~25 FPS

// Protótipos
void setupCamera();
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length);
void sendCameraFrame();

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n==================================================");
  Serial.println("🚀 ROVER ESP32-S3 - CLIENTE WEBSOCKET FPV");
  Serial.println("==================================================");

  // 1. Inicializa o Sensor de Câmera
  setupCamera();

  // 2. Conecta ao Wi-Fi
  Serial.printf("[Wi-Fi] Conectando a %s...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Conectado com sucesso!");
    Serial.printf("[Wi-Fi] IP Local: %s | RSSI: %d dBm\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("\n[Wi-Fi] Falha ao conectar. Reiniciando...");
    ESP.restart();
  }

  // 3. Configura o Cliente WebSocket Seguro (WSS / TLS)
  Serial.printf("[WSS] Conectando ao Relay: wss://%s:%d%s\n", RELAY_HOST, RELAY_PORT, RELAY_PATH);
  
  // Conexão SSL nativa na porta 443 sem validação de CA estrita (usa certificado público da Fly)
  webSocket.beginSSL(RELAY_HOST, RELAY_PORT, RELAY_PATH);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(2000);
  webSocket.enableHeartbeat(15000, 3000, 2);
}

void loop() {
  webSocket.loop();

  // Dispara transmissão contínua de vídeo se o WebSocket estiver conectado
  if (isWsConnected) {
    uint32_t now = millis();
    if (now - lastFrameTime >= FRAME_INTERVAL_MS) {
      lastFrameTime = now;
      sendCameraFrame();
    }

    // Telemetria periódica a cada 2 segundos (RSSI, Heap, RTT)
    if (now - lastTelemetryTime >= 2000) {
      lastTelemetryTime = now;
      StaticJsonDocument<256> doc;
      doc["type"] = "esp_telemetry";
      doc["rssi"] = WiFi.RSSI();
      doc["freeHeap"] = ESP.getFreeHeap();
      doc["freePsram"] = ESP.getFreePsram();
      doc["rttMs"] = lastRttMs;

      String jsonOut;
      serializeJson(doc, jsonOut);
      webSocket.sendTXT(jsonOut);
    }
  }
}

// ============================================================================
// 4. TRATAMENTO DE EVENTOS WEBSOCKET
// ============================================================================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      isWsConnected = false;
      Serial.println("[WSS] Desconectado do Relay.");
      break;

    case WStype_CONNECTED:
      isWsConnected = true;
      Serial.printf("[WSS] Conectado com sucesso à nuvem! (%s)\n", payload);
      break;

    case WStype_BIN:
      // Resposta ACK recebida do Relay para cálculo de RTT
      // Pacote ACK: [0x01, FrameID (4B), Timestamp (4B)]
      if (length >= 9 && payload[0] == 0x01) {
        uint32_t sentMillis = ((uint32_t)payload[5] << 24) |
                              ((uint32_t)payload[6] << 16) |
                              ((uint32_t)payload[7] << 8)  |
                              ((uint32_t)payload[8]);
        lastRttMs = millis() - sentMillis;
        // Serial.printf("[RTT] Robô <-> Nuvem: %u ms\n", lastRttMs);
      }
      break;

    case WStype_TEXT: {
      // Comandos de pilotagem vindos do cockpit do piloto (WASD / Pan / Tilt)
      StaticJsonDocument<384> doc;
      DeserializationError error = deserializeJson(doc, payload, length);
      if (!error) {
        const char* typeStr = doc["type"];
        if (typeStr && strcmp(typeStr, "cmd") == 0) {
          int v = doc["v"] | 0;
          int w = doc["w"] | 0;
          int pan = doc["pan"] | 90;
          int tilt = doc["tilt"] | 90;

          // Aqui serão aplicados os pulsos nos servos e na ponte H
          Serial.printf("[CMD PILOTO] Vel: %d | Dir: %d | Pan: %d° | Tilt: %d°\n", v, w, pan, tilt);
        }
      }
      break;
    }

    case WStype_ERROR:
      Serial.println("[WSS] Erro na conexão WebSocket.");
      break;

    default:
      break;
  }
}

// ============================================================================
// 5. CAPTURA E ENVIO DE FRAMES DA CÂMERA (PUSH BINÁRIO)
// ============================================================================
void sendCameraFrame() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[CÂMERA] Falha ao capturar frame.");
    return;
  }

  frameSequence++;
  uint32_t now = millis();

  // Aloca buffer temporário na Octal PSRAM para o pacote binário:
  // [8 bytes de cabeçalho] + [bytes JPEG brutos]
  size_t packetSize = fb->len + 8;
  uint8_t* packet = (uint8_t*)ps_malloc(packetSize);

  if (packet) {
    // 1. Frame ID (uint32BE)
    packet[0] = (frameSequence >> 24) & 0xFF;
    packet[1] = (frameSequence >> 16) & 0xFF;
    packet[2] = (frameSequence >> 8) & 0xFF;
    packet[3] = frameSequence & 0xFF;

    // 2. Timestamp millis() (uint32BE)
    packet[4] = (now >> 24) & 0xFF;
    packet[5] = (now >> 16) & 0xFF;
    packet[6] = (now >> 8) & 0xFF;
    packet[7] = now & 0xFF;

    // 3. Payload JPEG
    memcpy(packet + 8, fb->buf, fb->len);

    // 4. Envia pacote binário via WebSocket Seguro
    webSocket.sendBIN(packet, packetSize);

    // Libera a memória do pacote
    free(packet);
  } else {
    Serial.println("[MEMÓRIA] Falha ao alocar buffer do frame na PSRAM.");
  }

  // Devolve o buffer da câmera imediatamente ao driver
  esp_camera_fb_return(fb);
}

// ============================================================================
// 6. INICIALIZAÇÃO DO SENSOR OV2640 / OV5640
// ============================================================================
void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode    = CAMERA_GRAB_LATEST;
  config.fb_location  = CAMERA_FB_IN_PSRAM;

  // Resolução VGA (640x480) ou SVGA (800x600) para taxa fluida e estável em Wi-Fi
  if (psramFound()) {
    config.frame_size   = FRAMESIZE_VGA;
    config.jpeg_quality = 12; // 10-14 oferece excelente definição com compressão ágil
    config.fb_count     = 2;
    Serial.printf("[PSRAM] Detectada! Total: %u KB | Livre: %u KB\n", ESP.getPsramSize() / 1024, ESP.getFreePsram() / 1024);
  } else {
    config.frame_size   = FRAMESIZE_QVGA;
    config.jpeg_quality = 15;
    config.fb_count     = 1;
    Serial.println("[AVISO] PSRAM não encontrada. Operando em modo reduzido (QVGA).");
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[CÂMERA] Erro fatal ao inicializar o sensor (0x%x). Reiniciando em 5s...\n", err);
    delay(5000);
    ESP.restart();
  }

  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    // Inversões se a imagem estiver de cabeça para baixo no suporte da câmera
    s->set_vflip(s, 0);
    s->set_hmirror(s, 0);
  }

  Serial.println("[CÂMERA] Sensor inicializado com sucesso!");
}
