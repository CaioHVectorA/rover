/*
 * ====================================================================================
 * TESTE PAN/TILT COM ARDUINO NANO - COREOGRAFIA E MOVIMENTO SUAVE
 * ====================================================================================
 * Servos: SG90 9g
 * Pinos:
 *   - Pan  (Horizontal): Pino D9
 *   - Tilt (Vertical):   Pino D10
 *
 * ALIMENTAÇÃO:
 *   - Fios Vermelho (5V) e Marrom (GND) dos servos devem ir preferencialmente na saída
 *     de 5V do Step-Down Mini 560 ou fonte externa. O pino 5V do Nano pode resetar
 *     se os dois servos se moverem rápido demais na USB!
 * ====================================================================================
 */

#include <Servo.h>

// Definição dos pinos
const int PINO_PAN  = 9;   // Servo Horizontal
const int PINO_TILT = 10;  // Servo Vertical

// Limites seguros para proteger o suporte mecânico impresso (ajuste se necessário)
const int PAN_MIN  = 30;
const int PAN_MAX  = 150;
const int PAN_MID  = 90;

const int TILT_MIN = 45;   // Cima / Baixo conforme o sentido de montagem
const int TILT_MAX = 90;
const int TILT_MID = 67;

Servo servoPan;
Servo servoTilt;

// Posições atuais dos servos
int posAtualPan  = PAN_MID;
int posAtualTilt = TILT_MID;

// Função para movimentar os dois servos simultaneamente de forma suave (sem trancos)
void moverSuave(int destinoPan, int destinoTilt, int velocidadeDelay = 15) {
  destinoPan  = constrain(destinoPan, PAN_MIN, PAN_MAX);
  destinoTilt = constrain(destinoTilt, TILT_MIN, TILT_MAX);

  while (posAtualPan != destinoPan || posAtualTilt != destinoTilt) {
    if (posAtualPan < destinoPan)  posAtualPan++;
    else if (posAtualPan > destinoPan) posAtualPan--;

    if (posAtualTilt < destinoTilt) posAtualTilt++;
    else if (posAtualTilt > destinoTilt) posAtualTilt--;

    servoPan.write(posAtualPan);
    servoTilt.write(posAtualTilt);
    delay(velocidadeDelay);
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

 // Serial.println(F("=================================================="));
 // Serial.println(F("    TESTE MECANISMO PAN & TILT - ARDUINO NANO     "));
 // Serial.println(F("=================================================="));

  // Conecta os servos aos pinos digitais
  servoPan.attach(PINO_PAN);
  servoTilt.attach(PINO_TILT);

  // Inicializa reto à frente (90 graus)
 // Serial.println(F("[1/5] Centralizando servos em 90 graus..."));
  servoPan.write(PAN_MID);
  servoTilt.write(TILT_MID);
  delay(1500);
}

void loop() {
  // ----------------------------------------------------
  // GESTO 1: Dizendo "NÃO" (Head Shake - Pan)
  // ----------------------------------------------------
  //Serial.println(F("[2/5] Gesto: Dizendo NAO (Olhando Esquerda / Direita)..."));
  for (int i = 0; i < 2; i++) {
    moverSuave(PAN_MIN, TILT_MID, 8);  // Olha esquerda rápido
    moverSuave(PAN_MAX, TILT_MID, 8);  // Olha direita rápido
  }
  moverSuave(PAN_MID, TILT_MID, 12);   // Volta ao centro
  delay(800);

  // ----------------------------------------------------
  // GESTO 2: Dizendo "SIM" (Head Nod - Tilt)
  // ----------------------------------------------------
  //Serial.println(F("[3/5] Gesto: Dizendo SIM (Olhando Cima / Baixo)..."));
  for (int i = 0; i < 2; i++) {
    moverSuave(PAN_MID, TILT_MIN, 10); // Cima
    moverSuave(PAN_MID, TILT_MAX, 10); // Baixo
  }
  moverSuave(PAN_MID, TILT_MID, 12);   // Volta ao centro
  delay(800);

  // ----------------------------------------------------
  // GESTO 3: Olhando para os 4 Cantos (Inspeção Tática)
  // ----------------------------------------------------
  //Serial.println(F("[4/5] Olhando para os 4 cantos..."));
  
  // Canto Superior Esquerdo
  //Serial.println(F(" -> Cima-Esquerda"));
  moverSuave(PAN_MIN, TILT_MIN, 15);
  delay(600);

  // Canto Superior Direito
 // Serial.println(F(" -> Cima-Direita"));
  moverSuave(PAN_MAX, TILT_MIN, 15);
  delay(600);

  // Canto Inferior Direito
  //Serial.println(F(" -> Baixo-Direita"));
  moverSuave(PAN_MAX, TILT_MAX, 15);
  delay(600);

  // Canto Inferior Esquerdo
 // Serial.println(F(" -> Baixo-Esquerda"));
  moverSuave(PAN_MIN, TILT_MAX, 15);
  delay(600);

  // Centro
  moverSuave(PAN_MID, TILT_MID, 12);
  delay(800);

  // ----------------------------------------------------
  // GESTO 4: Varredura Panorâmica Contínua (Sweep)
  // ----------------------------------------------------
  //Serial.println(F("[5/5] Varredura Panoramica (Sweep suave)..."));
  moverSuave(PAN_MIN, 80, 20);
  moverSuave(PAN_MAX, 100, 20);
  moverSuave(PAN_MID, TILT_MID, 15);

  //Serial.println(F("Ciclo finalizado com sucesso! Aguardando 2s para reiniciar..."));
  //Serial.println();
  delay(2000);
}