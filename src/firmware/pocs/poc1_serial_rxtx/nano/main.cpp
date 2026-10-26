// ====================================================================================
// POC 1 - NANO: CONTROLE DE LED VIA ENLACE SERIAL (ESCUTA TANTO D0/RX QUANTO D2!)
// ====================================================================================
// - Aceita comandos tanto pelo pino RX0 nativo (D0, fio direto) quanto pelo D2 (BC337) a 9600 baud!
// - <L,1> ou '1' -> Liga o LED D13
// - <L,0> ou '0' -> Desliga o LED D13
// - <L,2> ou '2' -> Pisca 5 vezes rapido
// ====================================================================================
#include <Arduino.h>
#include <SoftwareSerial.h>

SoftwareSerial s3Serial(2, 3, true); // D2 com BC337 (invertido)

static unsigned long ultimoStatusMs = 0;
static unsigned long totalBytes = 0;
static unsigned long totalComandos = 0;

static void piscarRapido(int vezes) {
  for (int i = 0; i < vezes; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(80);
    digitalWrite(LED_BUILTIN, LOW);
    delay(80);
  }
}

static void processarChar(char c) {
  totalBytes++;
  if (c == '1') {
    digitalWrite(LED_BUILTIN, HIGH);
    totalComandos++;
  } else if (c == '0') {
    digitalWrite(LED_BUILTIN, LOW);
    totalComandos++;
  } else if (c == '2') {
    totalComandos++;
    piscarRapido(5);
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.begin(9600);   // Escuta pino RX0 (D0) a 9600 baud!
  s3Serial.begin(9600); // Escuta pino D2 (BC337) a 9600 baud!
  pinMode(2, INPUT_PULLUP);

  // Pisca 3 vezes no boot confirmando que ligou
  piscarRapido(3);
}

void loop() {
  // 1) Se estiver ligado no pino RX0 (D0):
  while (Serial.available() > 0) {
    processarChar((char)Serial.read());
  }

  // 2) Se estiver ligado no pino D2 (via BC337):
  while (s3Serial.available() > 0) {
    processarChar((char)s3Serial.read());
  }
}
