// ====================================================================================
// POC: TRANSMISSAO DE VIDEO UDP DE ALTA PERFORMANCE (ESP32-S3-CAM + OV5640)
// ====================================================================================
// - Zero-Buffer: Envio direto por datagramas UDP sem overhead de TCP/HTTP.
// - Auto-descoberta: O servidor Python envia um 'HELLO' na porta 5005 e o ESP32 passa a
//   transmitir os frames diretamente para o IP do servidor.
// - Duplo Frame Buffer (fb_count=2) para captura e streaming em paralelo.
// - Suporte a troca dinâmica de resolução (QVGA, CIF, VGA, SVGA) via comandos UDP.
// ====================================================================================

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_camera.h"
#include "esp_config.h"
#include "esp_rede.h"

#define UDP_PORT 5005
#define UDP_CHUNK_MAX 1400  // Tamanho maximo do payload UDP por pacote (< MTU de 1500)

// Cabecalho binario em cada pacote UDP (16 bytes)
struct __attribute__((packed)) UdpPacketHeader {
  uint32_t magic;         // 0x52565231 ('RVR1')
  uint16_t frame_id;      // Contador sequencial de frames
  uint16_t chunk_id;      // Indice deste pacote (0 .. total_chunks - 1)
  uint16_t total_chunks;  // Quantidade total de pacotes no frame
  uint16_t payload_size;  // Bytes de JPEG neste pacote
  uint32_t timestamp_us;  // micros() no momento da captura
};

static WiFiUDP udp;
static IPAddress serverIp;
static uint16_t serverPort = UDP_PORT;
static bool streamingAtivo = false;
static uint32_t ultHeartbeatMs = 0;
static uint16_t seqFrameId = 0;

static framesize_t resAtual = FRAMESIZE_VGA;
static uint8_t jpegQualidade = 18;  // 10..30 (menor = melhor qualidade / mais bytes)

static bool cameraIniciar(framesize_t fs, uint8_t q) {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = CAM_Y2;
  config.pin_d1 = CAM_Y3;
  config.pin_d2 = CAM_Y4;
  config.pin_d3 = CAM_Y5;
  config.pin_d4 = CAM_Y6;
  config.pin_d5 = CAM_Y7;
  config.pin_d6 = CAM_Y8;
  config.pin_d7 = CAM_Y9;
  config.pin_xclk = CAM_XCLK;
  config.pin_pclk = CAM_PCLK;
  config.pin_vsync = CAM_VSYNC;
  config.pin_href = CAM_HREF;
  config.pin_sccb_sda = CAM_SIOD;
  config.pin_sccb_scl = CAM_SIOC;
  config.pin_pwdn = CAM_PWDN;
  config.pin_reset = CAM_RESET;
  config.xclk_freq_hz = 20000000;  // 20 MHz para taxa de quadros maxima
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = fs;
  config.jpeg_quality = q;
  config.fb_count = 2;              // Duplo buffer em PSRAM
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.grab_mode = CAMERA_GRAB_LATEST;  // Sempre captura o frame mais recente

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[CAM] Falha ao inicializar camera: 0x%x\n", err);
    return false;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    s->set_vflip(s, 0);
    s->set_hmirror(s, 0);
  }
  Serial.printf("[CAM] Inicializada com sucesso (Res: %d, Qualidade: %d)\n", (int)fs, q);
  return true;
}

static void cameraTrocarConfig(framesize_t fs, uint8_t q) {
  sensor_t *s = esp_camera_sensor_get();
  if (!s) return;
  resAtual = fs;
  jpegQualidade = q;
  s->set_framesize(s, fs);
  s->set_quality(s, q);
  Serial.printf("[CAM] Nova configuracao aplicada: Res=%d Qualidade=%d\n", (int)fs, q);
}

void setup() {
  logIniciar();
  Serial.println("\n==================================================");
  Serial.println("  ROVER: POC Transmissao de Video UDP de Baixa Latencia");
  Serial.println("==================================================");

  redeIniciar("Rover-UDP-POC");

  if (!cameraIniciar(resAtual, jpegQualidade)) {
    Serial.println("[ERRO] Camera nao detectada. Reiniciando em 5s...");
    delay(5000);
    ESP.restart();
  }

  udp.begin(UDP_PORT);
  Serial.printf("[UDP] Aguardando conexao do servidor Python na porta %d...\n", UDP_PORT);
}

static void processarComandosUDP() {
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    char buf[64];
    int len = udp.read(buf, sizeof(buf) - 1);
    if (len > 0) {
      buf[len] = '\0';
      // Atualiza endereco do servidor que enviou o comando
      serverIp = udp.remoteIP();
      serverPort = udp.remotePort();
      streamingAtivo = true;
      ultHeartbeatMs = millis();

      if (strncmp(buf, "HELLO", 5) == 0) {
        Serial.printf("[UDP] Servidor conectado: %s:%d\n", serverIp.toString().c_str(), serverPort);
        udp.beginPacket(serverIp, serverPort);
        udp.write((const uint8_t *)"READY", 5);
        udp.endPacket();
      } else if (buf[0] == '1') {
        cameraTrocarConfig(FRAMESIZE_QVGA, jpegQualidade);   // 320x240
      } else if (buf[0] == '2') {
        cameraTrocarConfig(FRAMESIZE_CIF, jpegQualidade);    // 400x296
      } else if (buf[0] == '3') {
        cameraTrocarConfig(FRAMESIZE_VGA, jpegQualidade);    // 640x480
      } else if (buf[0] == '4') {
        cameraTrocarConfig(FRAMESIZE_SVGA, jpegQualidade);   // 800x600
      } else if (buf[0] == '+') {
        if (jpegQualidade > 10) cameraTrocarConfig(resAtual, jpegQualidade - 2);
      } else if (buf[0] == '-') {
        if (jpegQualidade < 40) cameraTrocarConfig(resAtual, jpegQualidade + 2);
      } else if (buf[0] == 'P') { // Ping-Pong de medicao de RTT
        udp.beginPacket(serverIp, serverPort);
        udp.write((const uint8_t *)buf, len); // devolve o mesmo pacote com timestamp
        udp.endPacket();
      }
    }
  }

  // Timeout: se ficar 5 segundos sem nenhum sinal do servidor, pausa streaming
  if (streamingAtivo && millis() - ultHeartbeatMs > 5000) {
    streamingAtivo = false;
    Serial.println("[UDP] Servidor desconectou (timeout). Pausando stream.");
  }
}

static void transmitirQuadroUDP() {
  if (!streamingAtivo) return;

  uint32_t t0 = micros();
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[CAM] Falha ao capturar frame");
    return;
  }

  uint32_t capUs = micros() - t0;
  size_t fbLen = fb->len;
  uint8_t *fbBuf = fb->buf;

  uint16_t totalChunks = (fbLen + UDP_CHUNK_MAX - 1) / UDP_CHUNK_MAX;
  uint16_t fId = seqFrameId++;

  UdpPacketHeader header;
  header.magic = 0x52565231; // 'RVR1'
  header.frame_id = fId;
  header.total_chunks = totalChunks;
  header.timestamp_us = micros();

  // Envia cada fragmento UDP
  for (uint16_t chunk = 0; chunk < totalChunks; chunk++) {
    size_t offset = chunk * UDP_CHUNK_MAX;
    size_t chunkLen = min((size_t)UDP_CHUNK_MAX, fbLen - offset);

    header.chunk_id = chunk;
    header.payload_size = (uint16_t)chunkLen;

    udp.beginPacket(serverIp, serverPort);
    udp.write((const uint8_t *)&header, sizeof(header));
    udp.write(fbBuf + offset, chunkLen);
    udp.endPacket();
  }

  esp_camera_fb_return(fb);
}

void loop() {
  processarComandosUDP();
  transmitirQuadroUDP();
  yield();
}
