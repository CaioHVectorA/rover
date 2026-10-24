// ====================================================================================
// POC 5 - NANO: TESTE AUTOMATICO DOS MOTORES (vai-e-volta, gira, com rampa) - SEM ESP32
// ====================================================================================
// Alimente o Nano + TB6612 + motores com a bateria (Mini 560 -> 5V). Abra o Serial Monitor
// a 115200. Por seguranca NADA se move ao ligar: digite uma tecla.
//
//   g = roda a sequencia completa     p = so polaridade      v = so vai-e-volta
//   c = so giros                      s = PARAR (aborta)     + / - = PWM maximo do teste +-20
//   e / d = inverte sentido do lado esquerdo / direito (resolve fiacao trocada)
//
// Sequencia: [1] POLARIDADE (cada lado sozinho, 1,2 s)  [2] VAI-E-VOLTA (rampa, cruzeiro, rampa,
// tempo morto, re)  [3] GIRO NO EIXO (horario/anti-horario)  [4] CURVA SUAVE.
// Em cada fase imprime tensao da bateria e o MINIMO observado (queda na arrancada). Se o Nano
// resetar, o boot imprime a causa (BROWN-OUT = queda de tensao). Procure o limite onde isso acontece.
// ====================================================================================
#include <Arduino.h>
#include "nano_diag.h"
#include "nano_motores.h"

#define PIN_PWMA 3
#define PIN_AIN1 4
#define PIN_AIN2 5
#define PIN_PWMB 6
#define PIN_BIN1 7
#define PIN_BIN2 8
#define PIN_STBY 12

static MotoresTB6612 mot;
static int pwmTeste = 150;          // comando maximo do teste (0..255) - comece baixo!
static bool abortar = false;

static void relatorio(const __FlashStringHelper *fase) {
  long v = bateriaLer_mV();
  Serial.print(F("   [")); Serial.print(fase);
  Serial.print(F("] Vbat=")); Serial.print(v / 1000.0f, 2);
  Serial.print(F(" V  minimo=")); Serial.print(bateriaMinimoEReset() / 1000.0f, 2);
  Serial.print(F(" V  saida E/D=")); Serial.print(mot.saidaEsq()); Serial.print('/'); Serial.println(mot.saidaDir());
}

static void tratarTecla(char c);

// Espera ms mantendo rampa, bateria e teclas. Retorna false se abortado.
static bool esperar(uint32_t ms) {
  uint32_t t0 = millis();
  while (millis() - t0 < ms) {
    uint32_t agora = millis();
    mot.atualizar(agora);
    bateriaLer_mV();
    if (Serial.available()) { char c = Serial.read(); if (c == 's' || c == 'S') abortar = true; else tratarTecla(c); }
    if (abortar) { mot.parar(); return false; }
  }
  return true;
}
static bool esperarParado(uint32_t limiteMs) {
  uint32_t t0 = millis();
  while (!mot.parado() && millis() - t0 < limiteMs) if (!esperar(10)) return false;
  return esperar(mot.P.deadMs + 50);
}

static bool fasePolaridade() {
  Serial.println(F("\n[1] POLARIDADE: cada lado deve girar PARA FRENTE. Se algum girar ao contrario, use 'e'/'d'."));
  Serial.println(F("   >> ESQUERDO (canal A) frente"));
  mot.comando(pwmTeste, 0, millis());   if (!esperar(1500)) return false; relatorio(F("esq")); mot.parar();
  if (!esperarParado(2000)) return false;
  Serial.println(F("   >> DIREITO (canal B) frente"));
  mot.comando(0, pwmTeste, millis());   if (!esperar(1500)) return false; relatorio(F("dir")); mot.parar();
  return esperarParado(2000);
}

static bool faseVaiVolta() {
  Serial.println(F("\n[2] VAI-E-VOLTA (2 ciclos): rampa -> cruzeiro -> rampa -> tempo morto -> re"));
  for (uint8_t i = 0; i < 2; i++) {
    Serial.print(F("   frente, ciclo ")); Serial.println(i + 1);
    bateriaMinimoEReset();
    mot.comando(pwmTeste, pwmTeste, millis());  if (!esperar(2500)) return false; relatorio(F("frente")); mot.parar();
    if (!esperarParado(3000)) return false;
    Serial.println(F("   re"));
    bateriaMinimoEReset();
    mot.comando(-pwmTeste, -pwmTeste, millis()); if (!esperar(2500)) return false; relatorio(F("re")); mot.parar();
    if (!esperarParado(3000)) return false;
  }
  Serial.println(F("   REVERSAO DIRETA (frente -> re sem parar: o codigo deve frear, esperar o tempo morto e inverter)"));
  bateriaMinimoEReset();
  mot.comando(pwmTeste, pwmTeste, millis());   if (!esperar(1800)) return false;
  mot.comando(-pwmTeste, -pwmTeste, millis()); if (!esperar(3500)) return false; relatorio(F("reversao")); mot.parar();
  return esperarParado(3000);
}

static bool faseGiros() {
  Serial.println(F("\n[3] GIRO NO EIXO"));
  Serial.println(F("   horario (esq frente / dir re)"));
  bateriaMinimoEReset();
  mot.comando(pwmTeste, -pwmTeste, millis()); if (!esperar(1800)) return false; relatorio(F("horario")); mot.parar();
  if (!esperarParado(3000)) return false;
  Serial.println(F("   anti-horario"));
  mot.comando(-pwmTeste, pwmTeste, millis()); if (!esperar(1800)) return false; relatorio(F("anti")); mot.parar();
  return esperarParado(3000);
}

static bool faseCurva() {
  Serial.println(F("\n[4] CURVA SUAVE (lado externo 100%, interno 40%)"));
  bateriaMinimoEReset();
  mot.comando(pwmTeste, pwmTeste * 4 / 10, millis()); if (!esperar(2500)) return false; relatorio(F("curva dir")); mot.parar();
  if (!esperarParado(3000)) return false;
  mot.comando(pwmTeste * 4 / 10, pwmTeste, millis()); if (!esperar(2500)) return false; relatorio(F("curva esq")); mot.parar();
  return esperarParado(3000);
}

static void fimTeste() {
  mot.parar();
  esperarParado(3000);
  abortar = false;
  Serial.println(F("\n== fim. Digite g/p/v/c para repetir. =="));
}

static void tratarTecla(char c) {
  switch (c) {
    case 'g': abortar = false; fasePolaridade() && faseVaiVolta() && faseGiros() && faseCurva(); fimTeste(); break;
    case 'p': abortar = false; fasePolaridade(); fimTeste(); break;
    case 'v': abortar = false; faseVaiVolta(); fimTeste(); break;
    case 'c': abortar = false; faseGiros() && faseCurva(); fimTeste(); break;
    case '+': pwmTeste = min(255, pwmTeste + 20); Serial.print(F("PWM teste = ")); Serial.println(pwmTeste); break;
    case '-': pwmTeste = max(60,  pwmTeste - 20); Serial.print(F("PWM teste = ")); Serial.println(pwmTeste); break;
    case 'e': mot.P.invEsq = !mot.P.invEsq; Serial.print(F("invEsq = ")); Serial.println(mot.P.invEsq); break;
    case 'd': mot.P.invDir = !mot.P.invDir; Serial.print(F("invDir = ")); Serial.println(mot.P.invDir); break;
    default: break;
  }
}

void setup() {
  Serial.begin(115200);
  mot.begin(PIN_PWMA, PIN_AIN1, PIN_AIN2, PIN_PWMB, PIN_BIN1, PIN_BIN2, PIN_STBY);
  mot.P.rampaMs = 900;      // 0 -> 100% em 0,9 s
  mot.P.deadMs  = 200;      // tempo morto na reversao
  mot.P.pwmMin  = 60;
  delay(300);
  Serial.println(F("\n== POC5 NANO: TESTE DE MOTORES (sem ESP) =="));
  Serial.print(F("Ultimo reset: ")); Serial.println(diagResetTexto(g_resetFlags));
  Serial.print(F("Vbat agora: ")); Serial.print(bateriaLer_mV() / 1000.0f, 2); Serial.println(F(" V"));
  Serial.println(F("Rodas no AR na primeira vez! Digite: g (tudo) p (polaridade) v (vai-e-volta) c (giros) s (parar) + - e d"));
  Serial.print(F("PWM teste = ")); Serial.println(pwmTeste);
}

void loop() {
  mot.atualizar(millis());
  bateriaLer_mV();
  if (Serial.available()) tratarTecla(Serial.read());
}
