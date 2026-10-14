/*
 * ====================================================================================
 * ROVER ARDUINO NANO - RECEPTOR SERIAL (RX) E CONTROLE DE LED
 * ====================================================================================
 * Este firmware roda no Arduino Nano V3 (ATmega328P).
 * Ele escuta continuamente a porta Serial física (pino RX / D0) a 115200 baud.
 * Ao receber o caractere '1' vindo do ESP32, ele acende o LED onboard (D13).
 * Ao receber o caractere '0', ele apaga o LED onboard.
 *
 * Conexão de Bancada:
 * - GND do Arduino Nano ---- ligado ao ---- GND do ESP32 (Referência comum)
 * - Pino RX (D0) do Nano --- ligado ao ---- Pino TX do ESP32
 *
 * ATENÇÃO AO GRAVAR O NANO:
 * - O pino RX (D0) do Nano é compartilhado com o chip conversor USB (CH340 ou FTDI).
 * - Ao fazer o upload deste código via cabo USB no Arduino IDE, DESCONECTE temporariamente
 *   o fio que vem do TX do ESP32 para evitar conflito na gravação.
 * - Após o upload terminar, reconecte o fio no pino RX (D0).
 * ====================================================================================
 */

// O pino do LED onboard do Arduino Nano é o pino digital 13
const int PINO_LED = LED_BUILTIN;

void setup() {
  // Inicializa o pino do LED como saída
  pinMode(PINO_LED, OUTPUT);
  digitalWrite(PINO_LED, LOW);

  // Inicializa a comunicação Serial de hardware a 115200 baud (mesma velocidade do ESP32)
  Serial.begin(115200);

  // Pisca 3 vezes rapidamente no boot para confirmar visualmente que o Nano ligou
  for (int i = 0; i < 3; i++) {
    digitalWrite(PINO_LED, HIGH);
    delay(100);
    digitalWrite(PINO_LED, LOW);
    delay(100);
  }

  Serial.println(F("[NANO] Pronto! Aguardando comandos seriais do ESP32..."));
}

void loop() {
  // Verifica se há bytes disponíveis no buffer serial sem travar o processador
  if (Serial.available() > 0) {
    char comando = Serial.read();

    switch (comando) {
      case '1':
        digitalWrite(PINO_LED, HIGH);
        // Opcional: feedback de volta se houver fio de retorno ligado
        Serial.println(F("[NANO] LED ACESO!"));
        break;

      case '0':
        digitalWrite(PINO_LED, LOW);
        Serial.println(F("[NANO] LED APAGADO!"));
        break;

      default:
        // Ignora quebras de linha '\r', '\n' ou espaços em branco
        break;
    }
  }
}
