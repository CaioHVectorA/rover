/*
 * ====================================================================================
 * ROVER ARDUINO NANO - CONTROLE GENÉRICO DE PINOS VIA SERIAL (comandos em texto)
 * ====================================================================================
 * Roda no Arduino Nano V3. Recebe linhas de texto do ESP32 (RX = D2 via SoftwareSerial, 38400 baud),
 * executa na hora e responde uma linha de volta (TX = D1).
 *
 * PROTOCOLO (uma linha por comando, terminada em '\n'):
 *   M <pino> <modo>   modo: 0 = INPUT, 1 = OUTPUT, 2 = INPUT_PULLUP   -> "OK"
 *   W <pino> <0|1>    digitalWrite                                    -> "OK"
 *   P <pino> <0-255>  analogWrite (PWM; só D3 D5 D6 D9 D10 D11)       -> "OK"
 *   S <pino> <0-180>  servo no pino (anexa sozinho na 1a vez)         -> "OK"
 *   D <pino>          digitalRead                                     -> "D <pino> <0|1>"
 *   A <0-7>           analogRead (A0..A7)                             -> "A <n> <0-1023>"
 *   X                 solta servos e volta todos os pinos p/ INPUT    -> "OK"
 *   Qualquer erro                                                     -> "ERR"
 *
 * Numeração: D2..D13 = 2..13 | A0..A5 como digitais = 14..19 | A6/A7 só analógicos.
 * D0 e D1 são BLOQUEADOS (são a própria serial).
 *
 * ATENÇÃO AO GRAVAR O NANO:
 *  - Desconecte o fio ESP TX -> Nano D0 durante o upload.
 *  - Não deixe o jumper 5V ESP -> 5V Nano ligado ao mesmo tempo que o USB do Nano.
 * ====================================================================================
 */

#include <Servo.h>
#include <SoftwareSerial.h>

// Entrada dos comandos: SoftwareSerial no D2 (evita a briga com o CH340 no D0).
// Respostas e debug saem pelo Serial (USB do Nano), 115200.
SoftwareSerial entrada(2, 3);   // RX = D2, TX = D3 (não usado)

const byte TOTAL_PINOS = 20;          // D0..D13 + A0..A5 (14..19)
Servo servos[TOTAL_PINOS];
bool servoAtivo[TOTAL_PINOS];

char linha[32];
byte tam = 0;

bool pinoValido(long p) {
  return p >= 3 && p < TOTAL_PINOS;   // bloqueia D0, D1 (USB) e D2 (RX dos comandos)
}

void soltaServo(byte p) {
  if (servoAtivo[p]) {
    servos[p].detach();
    servoAtivo[p] = false;
  }
}

void processa(char *s) {
  char cmd = s[0];
  char *p = s + 1;
  long a = strtol(p, &p, 10);
  long b = strtol(p, &p, 10);

  switch (cmd) {
    case 'M':
      if (!pinoValido(a) || b < 0 || b > 2) break;
      soltaServo(a);
      pinMode(a, b == 1 ? OUTPUT : (b == 2 ? INPUT_PULLUP : INPUT));
      Serial.println(F("OK"));
      return;

    case 'W':
      if (!pinoValido(a)) break;
      soltaServo(a);
      pinMode(a, OUTPUT);
      digitalWrite(a, b ? HIGH : LOW);
      Serial.println(F("OK"));
      return;

    case 'P':
      if (!pinoValido(a)) break;
      soltaServo(a);
      pinMode(a, OUTPUT);
      analogWrite(a, constrain(b, 0, 255));
      Serial.println(F("OK"));
      return;

    case 'S':
      if (!pinoValido(a)) break;
      if (!servoAtivo[a]) {
        servos[a].attach(a);
        servoAtivo[a] = true;
      }
      servos[a].write(constrain(b, 0, 180));
      Serial.println(F("OK"));
      return;

    case 'D':
      if (!pinoValido(a)) break;
      Serial.print(F("D "));
      Serial.print(a);
      Serial.print(' ');
      Serial.println(digitalRead(a));
      return;

    case 'A':
      if (a < 0 || a > 7) break;
      Serial.print(F("A "));
      Serial.print(a);
      Serial.print(' ');
      Serial.println(analogRead(A0 + a));
      return;

    case 'X':
      for (byte i = 3; i < TOTAL_PINOS; i++) {
        soltaServo(i);
        pinMode(i, INPUT);
      }
      Serial.println(F("OK"));
      return;
  }
  Serial.println(F("ERR"));
}

void setup() {
  Serial.begin(115200);
  entrada.begin(38400);
  // Pisca o LED (D13) 3x no boot para confirmar que o Nano ligou
  pinMode(LED_BUILTIN, OUTPUT);
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH); delay(100);
    digitalWrite(LED_BUILTIN, LOW);  delay(100);
  }
  pinMode(LED_BUILTIN, INPUT);
}

void loop() {
  while (entrada.available() > 0) {
    char c = entrada.read();
    if (c == '\n' || c == '\r') {
      if (tam > 0) {
        linha[tam] = 0;
        processa(linha);
        tam = 0;
      }
    } else if (tam < sizeof(linha) - 1) {
      linha[tam++] = c;
    }
  }
}
