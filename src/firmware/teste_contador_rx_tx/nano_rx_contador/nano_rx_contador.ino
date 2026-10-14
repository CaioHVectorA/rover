#include <Arduino.h>
#include <SoftwareSerial.h>

// ====================================================================================
// TESTE DE RECEPCAO SERIAL - ARDUINO NANO V3 (RX CONTADOR)
// ====================================================================================
// Escuta o ESP32 no pino D2 via SoftwareSerial com logica invertida (inversor BC337).
// A cada pacote <CNT:numero> recebido com sucesso:
// 1. Alterna o estado do LED onboard (D13) - pisca a cada pacote!
// 2. Incrementa o contador total de recepcoes
// 3. Exibe o pacote detalhado no Serial Monitor do PC (9600 baud)
// 4. Envia de volta um pacote de ACK (<ACK:total>) pelo pino D3
// ====================================================================================

// RX = D2 (Coletor do BC337 com pull-up 10k), TX = D3, inverse_logic = true
SoftwareSerial s3Serial(2, 3, true);

const int PINO_LED = LED_BUILTIN; // D13
uint32_t totalRecebidos = 0;
bool estadoLed = false;
unsigned long ultimoStatus = 0;
const unsigned long INTERVALO_STATUS_MS = 2000;

void setup() {
  pinMode(PINO_LED, OUTPUT);
  digitalWrite(PINO_LED, LOW);

  Serial.begin(9600);
  s3Serial.begin(9600);

  for (int i = 0; i < 3; i++) {
    digitalWrite(PINO_LED, HIGH);
    delay(100);
    digitalWrite(PINO_LED, LOW);
    delay(100);
  }

  Serial.println();
  Serial.println(F("=================================================="));
  Serial.println(F("   ARDUINO NANO: TESTE DE RX SERIAL (CONTADOR)    "));
  Serial.println(F("=================================================="));
  Serial.println(F("Escutando no pino D2 (SoftwareSerial, 9600 baud, invertido)"));
  Serial.println(F("LED D13 alternara a cada pacote recebido com sucesso."));
  Serial.println(F("=================================================="));
}

void loop() {
  if (s3Serial.available() > 0) {
    char c = s3Serial.read();

    if (c == '<') {
      s3Serial.setTimeout(100);
      String pacote = s3Serial.readStringUntil('>');
      pacote.trim();

      totalRecebidos++;

      estadoLed = !estadoLed;
      digitalWrite(PINO_LED, estadoLed ? HIGH : LOW);

      Serial.print(F("[NANO RX OK] Pacote recebido: <"));
      Serial.print(pacote);
      Serial.print(F("> | Total de pacotes: "));
      Serial.println(totalRecebidos);

      s3Serial.print(F("<ACK:"));
      s3Serial.print(totalRecebidos);
      s3Serial.println(F(">"));
    }
  }

  unsigned long agora = millis();
  if (agora - ultimoStatus >= INTERVALO_STATUS_MS) {
    ultimoStatus = agora;

    int nivelD2 = digitalRead(2);

    Serial.print(F("[NANO STATUS] Total recebidos: "));
    Serial.print(totalRecebidos);
    Serial.print(F(" | Nivel fisico no pino D2: "));
    if (nivelD2 == LOW) {
      Serial.println(F("LOW (Normal: BC337 conduzindo / ESP32 em Idle)"));
    } else {
      Serial.println(F("HIGH (Pull-up 5V: ESP32 desconectado ou em transicao)"));
    }
  }
}
