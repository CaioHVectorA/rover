#include <Arduino.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// ====================================================================================
// TESTE DE TRANSMISSAO SERIAL - ESP32-S3 (TX CONTADOR)
// ====================================================================================
// ESP32 envia pacotes incrementais sequenciais (<CNT:1>, <CNT:2>, ...) a cada 1 segundo
// pela Serial2 (Pino IO43 - TX) na velocidade de 9600 baud.
//
// Ligacao:
// - ESP32 GND  <---> Arduino Nano GND (Comum)
// - ESP32 IO43 <---> Base do BC337 (resistor 1k) -> Coletor vai para Nano D2 (com pull-up 10k para 5V)
// - ESP32 IO44 <---> Nano D1/D3 (se houver fio de retorno TX do Nano)
// ====================================================================================

const int PINO_TX = 43; // Serial2 TX
const int PINO_RX = 44; // Serial2 RX
const long BAUD_RATE = 9600;

uint32_t contador = 0;
unsigned long ultimoEnvio = 0;
const unsigned long INTERVALO_ENVIO_MS = 1000; // 1 pacote por segundo

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  delay(1000);

  Serial2.begin(BAUD_RATE, SERIAL_8N1, PINO_RX, PINO_TX);

  Serial.println();
  Serial.println(F("=================================================="));
  Serial.println(F("   ESP32-S3: TESTE DE TX SERIAL (CONTADOR ATIVO)  "));
  Serial.println(F("=================================================="));
  Serial.printf("Porta Serial2 configurada: TX=IO%d, RX=IO%d a %ld baud\n", PINO_TX, PINO_RX, BAUD_RATE);
  Serial.println(F("Enviando pacotes sequenciais a cada 1 segundo..."));
  Serial.println(F("=================================================="));
}

void loop() {
  unsigned long agora = millis();

  if (agora - ultimoEnvio >= INTERVALO_ENVIO_MS) {
    ultimoEnvio = agora;
    contador++;

    Serial2.print(F("<CNT:"));
    Serial2.print(contador);
    Serial2.println(F(">"));

    Serial.printf("[ESP32 TX -> IO%d] Pacote enviado: <CNT:%u>\n", PINO_TX, contador);
  }

  if (Serial2.available() > 0) {
    String resposta = Serial2.readStringUntil('\n');
    resposta.trim();
    if (resposta.length() > 0) {
      Serial.printf("   [ESP32 RX <- NANO IO%d] Resposta: %s\n", PINO_RX, resposta.c_str());
    }
  }
}
