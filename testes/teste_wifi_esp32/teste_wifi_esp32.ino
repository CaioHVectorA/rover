#include <WiFi.h>

// ============================================================================
// CONFIGURAÇÕES DA REDE
// ============================================================================
const char* ssid     = "PET_ELETRICA";
const char* password = "1478965P";

void setup() {
  Serial.begin(115200);
  delay(2000); // Aguarda a porta serial abrir na Arduino IDE

  Serial.println();
  Serial.println("==========================================");
  Serial.println("Teste Simples de Conexao Wi-Fi - ESP32-S3");
  Serial.println("==========================================");
  Serial.print("Conectando na rede: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 40) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("==========================================");
    Serial.println("Conectado com sucesso!");
    Serial.print("Endereco IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Mascara:     ");
    Serial.println(WiFi.subnetMask());
    Serial.print("Gateway:     ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("DNS:         ");
    Serial.println(WiFi.dnsIP());
    Serial.print("Sinal RSSI:  ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.println("==========================================");
  } else {
    Serial.println("==========================================");
    Serial.println("Falha ao conectar no tempo limite (20s)!");
    Serial.print("Status do WiFi: ");
    Serial.println(WiFi.status());
    Serial.println("Dicas:");
    Serial.println(" - 1 = WL_NO_SSID_AVAIL (Rede nao encontrada / fora de alcance / 5GHz)");
    Serial.println(" - 4 = WL_CONNECT_FAILED (Senha incorreta)");
    Serial.println(" - 6 = WL_DISCONNECTED (Desconectado)");
    Serial.println("==========================================");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Conectado! IP: ");
    Serial.print(WiFi.localIP());
    Serial.print(" | Sinal: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("Desconectado.");
  }
  delay(5000);
}
