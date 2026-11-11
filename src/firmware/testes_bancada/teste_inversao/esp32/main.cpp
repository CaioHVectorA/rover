#include <Arduino.h>

constexpr uint8_t PIN_TX = 43;
constexpr uint8_t PIN_RX = 44;
constexpr uint32_t BAUD = 9600;

static bool invertido = true;
static uint32_t ultimoEnvio = 0;
static bool estadoLed = false;

static void aplicarInversao(bool inv) {
  invertido = inv;
  Serial2.end();
  delay(50);
  Serial2.begin(BAUD, SERIAL_8N1, PIN_RX, PIN_TX, invertido);
  Serial.printf("\n======================================================\n");
  Serial.printf(">> POLARIDADE: TX Invertido = %s <<\n", invertido ? "TRUE (Modo BC337: Repouso 0V)" : "FALSE (Modo Normal: Repouso 3.3V)");
  Serial.printf("======================================================\n");
  if (invertido) {
    Serial.println("-> ESP IO43: ~0.0V (LOW)");
    Serial.println("-> Base BC337: 0.0V (corte)");
    Serial.println("-> Nano D0 RX: 5.0V (HIGH)");
    Serial.println("-> LED RX Nano: APAGADO em repouso (pisca nos envios)");
  } else {
    Serial.println("-> ESP IO43: ~3.3V (HIGH)");
    Serial.println("-> Base BC337: 0.6V (saturado)");
    Serial.println("-> Nano D0 RX: 1.5V (LOW)");
    Serial.println("-> LED RX Nano: ACESO DIRETO (bloqueia comunicacao)");
  }
  Serial.println("------------------------------------------------------\n");
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n\n==========================================");
  Serial.println(" ROVER - TESTE DE ENLACE SERIAL ESP32-S3");
  Serial.println("==========================================");
  Serial.println("Controles pelo Monitor Serial:");
  Serial.println(" [i] : Alternar inversao TX (True/False)");
  Serial.println(" [1] : Enviar <L,1> (Ligar LED D13)");
  Serial.println(" [0] : Enviar <L,0> (Desligar LED D13)");
  Serial.println(" [2] : Enviar <L,2> (Piscar LED D13 5x)");
  Serial.println("==========================================\n");

  aplicarInversao(true);
}

void loop() {
  // Leitura de teclas no Monitor Serial USB
  if (Serial.available()) {
    char c = static_cast<char>(Serial.read());
    if (c == 'i' || c == 'I') {
      aplicarInversao(!invertido);
    } else if (c == '1') {
      Serial.println("[MANUAL] Enviando <L,1> -> Ligar D13");
      Serial2.println("<L,1>");
    } else if (c == '0') {
      Serial.println("[MANUAL] Enviando <L,0> -> Desligar D13");
      Serial2.println("<L,0>");
    } else if (c == '2') {
      Serial.println("[MANUAL] Enviando <L,2> -> Piscar D13 5x");
      Serial2.println("<L,2>");
    }
  }

  // Envio automatico a cada 2 segundos
  uint32_t agora = millis();
  if (agora - ultimoEnvio >= 2000) {
    ultimoEnvio = agora;
    estadoLed = !estadoLed;
    if (estadoLed) {
      Serial.println("[AUTO] Enviando <L,1> (Ligar LED D13 Nano)...");
      Serial2.println("<L,1>");
    } else {
      Serial.println("[AUTO] Enviando <L,0> (Desligar LED D13 Nano)...");
      Serial2.println("<L,0>");
    }
  }
}
