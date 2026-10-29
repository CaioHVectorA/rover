#include <Arduino.h>
#include "../protocolo.h"

// Mesmo acionamento e pinos do nano_motor_direto que funcionou na bancada.
constexpr uint8_t PWMA = 3, AIN1 = 4, AIN2 = 5;
constexpr uint8_t PWMB = 6, BIN1 = 7, BIN2 = 8, STBY = 12;

static ProtoParser parser;
static bool aguardando = false, rodando = false;
static int alvoE = 0, alvoD = 0;
static uint32_t iniciarEm = 0, pararEm = 0, ultimoByte = 0;
static uint8_t piscadas = 0;
static uint32_t proximaPiscada = 0;

static bool venceu(uint32_t agora, uint32_t prazo) {
  return static_cast<int32_t>(agora - prazo) >= 0;
}

static void pararMotores() {
  digitalWrite(STBY, LOW);
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);
  aguardando = rodando = false;
}

static void aplicarLado(uint8_t pwm, uint8_t in1, uint8_t in2, int valor) {
  digitalWrite(in1, valor > 0 ? HIGH : LOW);
  digitalWrite(in2, valor < 0 ? HIGH : LOW);
  analogWrite(pwm, valor < 0 ? -valor : valor);  // PWM bruto; sem rampa/mapeamento.
}

static void receber(const ProtoFrame &f, uint32_t agora) {
  if (!TesteD0::valido(f)) return;
  if (f.cmd == 'L') {
    piscadas = 0;
    if (f.arg[0] == 2) {
      // Preserva o POC 1: comando 2 pisca o D13 cinco vezes.
      digitalWrite(LED_BUILTIN, LOW);
      piscadas = 10;
      proximaPiscada = agora + 80;
    } else {
      digitalWrite(LED_BUILTIN, f.arg[0] ? HIGH : LOW);
    }
  } else if (f.cmd == 'X') {
    pararMotores();
  } else if (f.cmd == 'M') {
    pararMotores();
    alvoE = static_cast<int>(f.arg[0]);
    alvoD = static_cast<int>(f.arg[1]);
    if (alvoE || alvoD) {
      iniciarEm = agora + TesteD0::PAUSA_MS;
      aguardando = true;
    }
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  pinMode(STBY, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pararMotores();
  Serial.begin(TesteD0::BAUD);  // UART fisica: D0/RX. Nenhuma resposta no D1.
}

void loop() {
  uint32_t agora = millis();
  if (agora - ultimoByte > 250) parser = ProtoParser();

  // Limita o trabalho por volta para nao atrasar a parada em caso de ruido serial.
  uint8_t limite = 32;
  while (limite-- && Serial.available() > 0) {
    ProtoFrame f;
    const char c = static_cast<char>(Serial.read());
    ultimoByte = millis();
    if (parser.feed(c, f)) receber(f, ultimoByte);
  }

  agora = millis();
  if (aguardando && venceu(agora, iniciarEm)) {
    aplicarLado(PWMA, AIN1, AIN2, alvoE);
    aplicarLado(PWMB, BIN1, BIN2, alvoD);
    digitalWrite(STBY, HIGH);
    aguardando = false;
    rodando = true;
    pararEm = agora + TesteD0::PULSO_MS;
  }
  // O Nano termina o pulso mesmo que Wi-Fi, pagina ou ESP parem de funcionar.
  if (rodando && venceu(agora, pararEm)) pararMotores();

  if (piscadas && venceu(agora, proximaPiscada)) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    --piscadas;
    proximaPiscada = agora + 80;
    if (!piscadas) digitalWrite(LED_BUILTIN, LOW);
  }
}
