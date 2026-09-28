/*
 * 🤖 Rover ESP32 - Firmware Extensao do CameraWebServer (WebSocket Relay Stream)
 *
 * Este codigo captura quadros da camera (OV2640 / OV5640) e os transmite via WebSocket binario
 * para um Servidor Relay Central (Node.js/VPS). Isso permite assistir ao vivo a camera do
 * carrinho de QUALQUER internet (4G/LTE ou Wi-Fi remoto), contornando CGNAT.
 *
 * Bibliotecas Necessarias no Arduino IDE:
 * 1. esp32 (Placa oficial Espressif v2.0.x ou v3.x)
 * 2. WebSockets de Markus Sattler (Links2004) -> Buscar "WebSockets" no Library Manager
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <esp_wifi.h>
#include "camera_pins.h"

// ============================================================================
// ⚙️ CONFIGURACOES DE REDE & RELAY
// ============================================================================
const char* WIFI_SSID     = "SUA_REDE_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";

// Endereco IP ou Dominio do Servidor Relay (Ex: "192.168.1.100" ou "seu-servidor.com")
const char* RELAY_HOST    = "192.168.1.100";
const uint16_t RELAY_PORT = 3000;
const char* RELAY_PATH    = "/ws?role=esp32";

// ============================================================================
// 📹 CONFIGURACOES DA CAMERA
// ============================================================================
// Resolucoes Recomendadas:
// - FRAMESIZE_QVGA (320x240) -> Fluidez maxima (~25-30 FPS em Wi-Fi e 4G)
// - FRAMESIZE_CIF  (400x296) -> Equilíbrio perfeito entre nitidez e velocidade
// - FRAMESIZE_VGA  (640x480) -> Alta resolucao (~15-20 FPS)
#define CAMERA_FRAMESIZE FRAMESIZE_QVGA
#define JPEG_QUALITY     12  // Qualidade JPEG (10 = Alta, 12 = Balanceada, 20 = Baixa)

WebSocketsClient webSocket;
bool isWebSocketConnected = false;
unsigned long lastFrameTime = 0;
const unsigned long FRAME_INTERVAL_MS = 33; // ~30 FPS (1000ms / 30)

// Callbacks de Eventos do WebSocket
void webSocketEvent(WSType_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WSType_DISCONNECTED:
      Serial.println("[WS] Desconectado do Servidor Relay!");
      isWebSocketConnected = false;
      break;

    case WSType_CONNECTED:
      Serial.printf("[WS] Conectado ao Servidor Relay em http://%s:%d%s\n", RELAY_HOST, RELAY_PORT, RELAY_PATH);
      isWebSocketConnected = true;

      // Enviar mensagem de identificacao
      webSocket.sendTXT("{\"device\":\"Rover-ESP32-CAM\",\"status\":\"ready\"}");
      break;

    case WSType_TEXT:
      Serial.printf("[WS Text] Recebido do Servidor: %s\n", payload);
      break;

    case WSType_BIN:
      // Se o servidor enviar comandos binarios no futuro
      break;

    case WSType_ERROR:
      Serial.println("[WS Error] Erro na conexao WebSocket!");
      break;

    default:
      break;
  }
}

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
  config.frame_size   = CAMERA_FRAMESIZE;
  config.jpeg_quality = JPEG_QUALITY;
  config.fb_count     = 2; // Duplo buffer na PSRAM para alta taxa de quadros (DMA)

  // Verificar se possui PSRAM para alocacao otimizada
  if (psramFound()) {
    Serial.println("✅ PSRAM Encontrada! Ativando duplo buffer e alta resolucao.");
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode   = CAMERA_GRAB_LATEST; // Captura sempre o quadro mais recente
  } else {
    Serial.println("⚠️ Sem PSRAM! Reduzindo tamanho do buffer de quadro.");
    config.frame_size   = FRAMESIZE_QVGA;
    config.fb_count     = 1;
    config.fb_location  = CAMERA_FB_IN_DRAM;
    config.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
  }

  // Inicializar a Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Falha critica ao inicializar a camera: 0x%x\n", err);
    while (true) {
      delay(1000);
    }
  }

  // Ajustes no sensor da camera
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_vflip(s, 1);       // Inverter verticalmente se necessario
    s->set_hmirror(s, 0);     // Inverter horizontalmente se necessario
    s->set_brightness(s, 1);  // Ligeiro ganho de brilho
  }

  Serial.println("📷 Camera inicializada com sucesso!");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n===================================================");
  Serial.println("🤖 Rover ESP32 - Streaming Remoto WebSocket Relay");
  Serial.println("===================================================");

  // Inicializar Hardware de Câmera
  setupCamera();

  // Conectar ao Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.printf("📶 Conectando ao Wi-Fi '%s'...", WIFI_SSID);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ Wi-Fi Conectado!");
  Serial.printf("📍 IP Local do ESP32: %s\n", WiFi.localIP().toString().c_str());

  // OTIMIZACAO DE REDE: Desativar economia de energia do Wi-Fi para latencia minima
  esp_wifi_set_ps(WIFI_PS_NONE);

  // Configurar Cliente WebSocket
  webSocket.begin(RELAY_HOST, RELAY_PORT, RELAY_PATH);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(2000); // Tentar reconectar a cada 2s se cair
}

void sendCameraFrame() {
  if (!isWebSocketConnected) return;

  unsigned long now = millis();
  if (now - lastFrameTime < FRAME_INTERVAL_MS) {
    return; // Respeita o intervalo limite para nao sobrecarregar
  }
  lastFrameTime = now;

  // Capturar quadro da camera
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("⚠️ Falha ao capturar quadro da camera!");
    return;
  }

  // Transmitir o payload binario do JPEG via WebSocket
  bool success = webSocket.sendBIN(fb->buf, fb->len);

  // Devolver o buffer para a camera IMEDIATAMENTE apos o envio
  esp_camera_fb_return(fb);

  if (!success) {
    Serial.println("⚠️ Falha ao enviar quadro via WebSocket.");
  }
}

void loop() {
  // Manter a pilha do WebSocket ativa
  webSocket.loop();

  // Transmitir quadros continuamente se o WebSocket estiver conectado
  if (isWebSocketConnected) {
    sendCameraFrame();
  }
}
