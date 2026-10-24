/*
 * ====================================================================================
 * ROVER ESP32-S3-CAM - SERVIDOR WEBSOCKET (PORTA 81) & STREAM DE VÍDEO (PORTA 80)
 * ====================================================================================
 * Este firmware é a ponte de alta velocidade entre o Aplicativo Mobile Expo e o robô:
 *  1. Conecta na rede Wi-Fi configurada (ou cria o Access Point próprio "Rover-S3" se falhar).
 *  2. Inicia o Servidor WebSocket na porta 81.
 *  3. Ao receber coordenadas do Giroscópio/App ({"type":"servo","pan":X,"tilt":Y}):
 *     -> Repassa imediatamente via Serial de hardware (IO43 TX / IO44 RX) para o Arduino Nano:
 *        "S 9 <pan>\n" e "S 10 <tilt>\n"
 *  4. Ao receber comandos de tração 4WD ({"type":"drive","cmd":"F","speed":220}):
 *     -> Repassa os comandos dos motores para o Nano.
 *  5. Responde pings para cálculo de latência em tempo real no app.
 *
 * Ligações de Bancada (Chicote de 4 Fios):
 *   ESP32 5V       <->  Arduino Nano 5V (ou regulador Mini 560)
 *   ESP32 GND      <->  Arduino Nano GND (Terra Comum)
 *   ESP32 IO43 TX  -->  Arduino Nano D0 RX (Comandos)
 *   ESP32 IO44 RX  <--  Arduino Nano D1 TX (via divisor 1k/2k) (Telemetria)
 *
 * Biblioteca necessária na Arduino IDE:
 *   - "WebSockets" por Markus Sattler (Instalar via Gerenciador de Bibliotecas)
 * ====================================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <esp_wifi.h>

// ==================== CONFIGURAÇÃO DE HARDWARE ====================
#define PLACA_ESP32_S3_CAM

#if defined(PLACA_ESP32_S3_CAM)
  #define PINO_TX_PARA_NANO 43
  #define PINO_RX_DO_NANO   44
  HardwareSerial SerialNano(1);
#else
  #define PINO_TX_PARA_NANO 1
  #define PINO_RX_DO_NANO   3
  #define SerialNano Serial
#endif

// Pinos dos Servos no Arduino Nano
#define PINO_SERVO_PAN   9   // D9 no Arduino Nano
#define PINO_SERVO_TILT 10   // D10 no Arduino Nano

// ==================== CONFIGURAÇÃO DE REDE ====================
const char *WIFI_SSID = "Apple Network fdd7b9";
const char *WIFI_PASS = "";

const char *AP_SSID = "Rover-S3";
const char *AP_PASS = ""; // Rede aberta para bancada

WebServer serverHttp(80);
WebSocketsServer webSocket(81);

// ==================== FUNÇÃO DE REPASSE SERIAL ====================
void enviaComandoNano(const String &cmd) {
  SerialNano.print(cmd);
  SerialNano.print('\n');
}

// ==================== PARSER LEVE DE JSON DO APP ====================
void processaComandoWS(uint8_t num, uint8_t *payload, size_t length) {
  String msg = String((char *)payload);

  // 1. Resposta ao Ping do App para cálculo de latência
  if (msg.indexOf("\"ping\"") >= 0) {
    webSocket.sendTXT(num, "{\"type\":\"pong\"}");
    return;
  }

  // 2. Comandos de Giroscópio / Servos Pan & Tilt
  // Exemplo recebido: {"type":"servo","pan":95,"tilt":80}
  if (msg.indexOf("\"servo\"") >= 0) {
    int idxPan = msg.indexOf("\"pan\":");
    int idxTilt = msg.indexOf("\"tilt\":");

    if (idxPan >= 0 && idxTilt >= 0) {
      int pan = msg.substring(idxPan + 6).toInt();
      int tilt = msg.substring(idxTilt + 7).toInt();

      pan = constrain(pan, 20, 160);
      tilt = constrain(tilt, 50, 130);

      // Envia os dois comandos ao Nano
      enviaComandoNano("S " + String(PINO_SERVO_PAN) + " " + String(pan));
      enviaComandoNano("S " + String(PINO_SERVO_TILT) + " " + String(tilt));

      // Debug serial do computador
      Serial.printf("[WS SERVO] Pan: %d | Tilt: %d\n", pan, tilt);
    }
    return;
  }

  // 3. Comandos de Tração 4WD
  // Exemplo recebido: {"type":"drive","cmd":"F","speed":220}
  if (msg.indexOf("\"drive\"") >= 0) {
    int idxCmd = msg.indexOf("\"cmd\":\"");
    if (idxCmd >= 0) {
      char direcao = msg.charAt(idxCmd + 7);
      enviaComandoNano("D_CMD " + String(direcao));
      Serial.printf("[WS DRIVE] Direção: %c\n", direcao);
    }
    return;
  }
}

// ==================== EVENTOS WEBSOCKET ====================
void webSocketEvent(uint8_t num, WStype_t type, uint8_t *payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.printf("[WS] Cliente #%u Desconectado\n", num);
      break;

    case WStype_CONNECTED: {
      IPAddress ip = webSocket.getRemoteIP(num);
      Serial.printf("[WS] Cliente #%u Conectado de %s\n", num, ip.toString().c_str());
      webSocket.sendTXT(num, "{\"type\":\"telemetry\",\"status\":\"online\"}");
      break;
    }

    case WStype_TEXT:
      processaComandoWS(num, payload, length);
      break;

    default:
      break;
  }
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n🚀 Inicializando Rover ESP32-S3 WebSocket Gateway...");

  // Inicia a comunicação serial física com o Arduino Nano
#if defined(PLACA_ESP32_S3_CAM)
  SerialNano.begin(115200, SERIAL_8N1, PINO_RX_DO_NANO, PINO_TX_PARA_NANO);
#else
  SerialNano.begin(115200);
#endif

  // Configuração do Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("[WI-FI] Conectando em ");
  Serial.println(WIFI_SSID);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(400);
    Serial.print(".");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("\n[WI-FI] Conectado! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    Serial.print("\n[WI-FI] Falhou na rede local. Criado AP '");
    Serial.print(AP_SSID);
    Serial.print("'. IP do Rover: ");
    Serial.println(WiFi.softAPIP());
  }
  esp_wifi_set_ps(WIFI_PS_NONE); // Desativa economia de energia para latência mínima

  // Inicia o Servidor WebSocket na porta 81
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  Serial.println("[WEBSOCKET] Servidor ativo na porta 81 (ws://<IP>:81)");

  // Servidor HTTP simples para checagem rápida de saúde
  serverHttp.on("/", HTTP_GET, []() {
    serverHttp.send(200, "text/plain", "Rover ESP32-S3 WebSocket Online na porta 81!");
  });
  serverHttp.begin();
  Serial.println("[HTTP] Servidor de checagem ativo na porta 80");
}

// ==================== LOOP PRINCIPAL ====================
void loop() {
  webSocket.loop();
  serverHttp.handleClient();

  // Se o Arduino Nano enviar alguma telemetria pela serial, repassa aos clientes WS
  if (SerialNano.available()) {
    String respostaNano = SerialNano.readStringUntil('\n');
    respostaNano.trim();
    if (respostaNano.length() > 0) {
      Serial.println("[NANO->ESP] " + respostaNano);
      webSocket.broadcastTXT("{\"type\":\"telemetry\",\"msg\":\"" + respostaNano + "\"}");
    }
  }
}
