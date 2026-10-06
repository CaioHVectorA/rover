#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Servo.h>

// RX = D2 (Coletor do BC337), TX = D3, inverse_logic = true
SoftwareSerial s3Serial(2, 3, true);

Servo servoPan;
Servo servoTilt;

const int PINO_PAN  = 9;
const int PINO_TILT = 10;

int panAtual  = 90;
int tiltAtual = 90;

void setup() {
  Serial.begin(9600);
  s3Serial.begin(9600);

  servoPan.attach(PINO_PAN);
  servoTilt.attach(PINO_TILT);

  servoPan.write(panAtual);
  servoTilt.write(tiltAtual);

  Serial.println("--- Nano Receptor Pan-Tilt Iniciado ---");
}

void loop() {
  if (s3Serial.available() > 0) {
    char c = s3Serial.read();

    if (c == '<') {
      s3Serial.setTimeout(50);
      String pacote = s3Serial.readStringUntil('>');
      pacote.trim();

      int separador = pacote.indexOf(',');
      if (separador > 0) {
        int novoPan  = pacote.substring(0, separador).toInt();
        int novoTilt = pacote.substring(separador + 1).toInt();

        if (novoPan >= 0 && novoPan <= 180 && novoPan != panAtual) {
          servoPan.write(novoPan);
          panAtual = novoPan;
        }

        if (novoTilt >= 0 && novoTilt <= 180 && novoTilt != tiltAtual) {
          servoTilt.write(novoTilt);
          tiltAtual = novoTilt;
        }

        Serial.print("Pan: ");
        Serial.print(panAtual);
        Serial.print(" | Tilt: ");
        Serial.println(tiltAtual);
      }
    }
  }
}
