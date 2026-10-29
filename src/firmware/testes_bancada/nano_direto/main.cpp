#include <Arduino.h>

// TB6612FNG: canal A = lado esquerdo; canal B = lado direito.
constexpr uint8_t PWMA = 3;
constexpr uint8_t AIN1 = 4;
constexpr uint8_t AIN2 = 5;
constexpr uint8_t PWMB = 6;
constexpr uint8_t BIN1 = 7;
constexpr uint8_t BIN2 = 8;
constexpr uint8_t STBY = 12;

constexpr uint8_t PWM_FRENTE = 120;
constexpr unsigned long ATRASO_INICIAL_MS = 3000;
constexpr unsigned long PULSO_FRENTE_MS = 1000;

void setup() {
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(STBY, OUTPUT);

  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  digitalWrite(STBY, LOW);
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);

  delay(ATRASO_INICIAL_MS);

  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);
  digitalWrite(STBY, HIGH);
  analogWrite(PWMA, PWM_FRENTE);
  analogWrite(PWMB, PWM_FRENTE);
  delay(PULSO_FRENTE_MS);

  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  digitalWrite(STBY, LOW);
}

void loop() {}
