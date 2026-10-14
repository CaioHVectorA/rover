/*
 * TESTE DE PINO DO ESP32 (sem serial, sem Wi-Fi)
 * Alterna o pino TESTE_PINO entre HIGH e LOW a cada 1 s.
 * Meça com o multímetro (pino x GND): deve alternar entre ~3,3 V e ~0 V.
 * Mude TESTE_PINO para testar outros pinos (IO1, IO2, IO3, IO21, IO41, IO42...).
 * Fio no Nano: ESP pino -> Nano D2. Se o D2 do Nano alternar, o fio e o pino estão OK.
 */
#define TESTE_PINO 43

void setup() {
  pinMode(TESTE_PINO, OUTPUT);
}

void loop() {
  digitalWrite(TESTE_PINO, HIGH);
  delay(1000);
  digitalWrite(TESTE_PINO, LOW);
  delay(1000);
}
