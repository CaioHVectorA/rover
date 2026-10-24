#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Servo.h>

// ====================================================================================
// ROVER ARDUINO NANO - RECEPTOR DE GIROSCÓPIO & CONTROLE DE SERVOS PAN/TILT
// ====================================================================================
// - Escuta o ESP32 no pino D2 via SoftwareSerial com lógica invertida (BC337).
// - Controla os servos SG90 de Pan (pino D9) e Tilt (pino D10).
// - FILTRO DE BANDA MORTA (DEADBAND): Elimina ruído, tremor e zumbido dos servos SG90
//   ignorando variações menores que 2 graus.
// ====================================================================================

// RX = D2 (Coletor do BC337), TX = D3, inverse_logic = true
SoftwareSerial s3Serial(2, 3, true);

Servo servoPan;
Servo servoTilt;

const int PINO_PAN  = 9;
const int PINO_TILT = 10;
const int PINO_LED  = LED_BUILTIN; // D13

int panAtual  = 90;
int tiltAtual = 90;

void centralizarServos() {
  servoPan.write(90);
  servoTilt.write(90);
  panAtual = 90;
  tiltAtual = 90;
  digitalWrite(PINO_LED, HIGH);
  delay(500); // Dá tempo físico para os servos atingirem o centro de 90°
  digitalWrite(PINO_LED, LOW);
}

void setup() {
  pinMode(PINO_LED, OUTPUT);
  digitalWrite(PINO_LED, LOW);

  Serial.begin(9600);
  s3Serial.begin(9600);

  // Conecta os pinos de PWM aos servos SG90 (pulsos 544us a 2400us)
  servoPan.attach(PINO_PAN, 544, 2400);
  servoTilt.attach(PINO_TILT, 544, 2400);

  // Centraliza imediatamente em 90° / 90° ao ligar ou reiniciar
  centralizarServos();

  for (int i = 0; i < 3; i++) {
    digitalWrite(PINO_LED, HIGH);
    delay(80);
    digitalWrite(PINO_LED, LOW);
    delay(80);
  }

  Serial.println(F("=================================================="));
  Serial.println(F("  NANO V3: SERVOS CENTRALIZADOS (FILTRO ANTI-RUÍDO)"));
  Serial.println(F("=================================================="));
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

        // Limita os ângulos para proteção mecânica dos servos (0 a 180)
        novoPan  = constrain(novoPan, 0, 180);
        novoTilt = constrain(novoTilt, 0, 180);

        bool moveu = false;

        // FILTRO ANTI-TREMOR / ANTI-RUÍDO:
        // Só atualiza o servo se a mudança for de pelo menos 2 graus,
        // ou se for o comando explícito de recentralização (90).
        if (abs(novoPan - panAtual) >= 2 || novoPan == 90) {
          servoPan.write(novoPan);
          panAtual = novoPan;
          moveu = true;
        }

        if (abs(novoTilt - tiltAtual) >= 2 || novoTilt == 90) {
          servoTilt.write(novoTilt);
          tiltAtual = novoTilt;
          moveu = true;
        }

        if (moveu) {
          digitalWrite(PINO_LED, !digitalRead(PINO_LED));
          Serial.print(F("[PAN-TILT] Pan: "));
          Serial.print(panAtual);
          Serial.print(F("° | Tilt: "));
          Serial.print(tiltAtual);
          Serial.println(F("°"));
        }
      }
    }
  }
}
