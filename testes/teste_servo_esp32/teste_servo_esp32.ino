/*
 * ============================================================================
 * TESTE DE SERVO MOTOR SG90 NO ESP32-S3 - ALINHAMENTO E ENCAIXE 3D
 * ============================================================================
 * Projeto: Rover / Drone Terrestre
 * Microcontrolador: ESP32-S3 CAM (N16R8) ou qualquer placa ESP32
 * 
 * ESQUEMA DE LIGAÇÃO:
 * -------------------
 * Fio do Servo SG90 | Sinal | Conectar no ESP32-S3 CAM
 * ------------------|-------|----------------------------------------------
 * Marrom / Preto    | GND   | Pino GND
 * Vermelho          | VCC   | Pino 5V (ou VBUS da porta USB)
 * Laranja / Amarelo | PWM   | GPIO 1 (Servo 1 - Pan)
 * (Opcional 2º)     | PWM   | GPIO 2 (Servo 2 - Tilt)
 * 
 * ⚠️ ATENÇÃO ELÉTRICA NO ESP32:
 * 1. O ESP32 trabalha com nível lógico de 3.3V. O sinal PWM de 3.3V (GPIO 1/2) 
 *    é 100% compatível com a entrada de sinal do micro servo SG90.
 * 2. O servo precisa de 5V na alimentação (fio vermelho). NÃO ligue o fio
 *    vermelho no pino 3.3V do ESP32 (o servo ficará fraco e com falhas).
 * 3. Queda de tensão (Brownout): Servos puxam picos de corrente na partida.
 *    Se o ESP32 reiniciar sozinho (Brownout Reset), utilize uma porta USB 3.0
 *    com bom cabo ou alimente o servo por uma fonte 5V externa (Step-Down 5V),
 *    mantendo SEMPRE o GND do ESP32 interligado ao GND da fonte externa.
 * ============================================================================
 */

#include <ESP32Servo.h>

Servo servo1; // Servo 1 (Pan)
Servo servo2; // Servo 2 (Tilt)

// Pinos GPIO padrão livres na maioria das placas ESP32-S3 CAM
const int PINO_SERVO_1 = 1;
const int PINO_SERVO_2 = 2;

int servoSelecionado = 1; // 1 = Servo 1, 2 = Servo 2, 3 = Ambos
int anguloAtual = 90;
bool modoSweep = false;
int direcaoSweep = 1;
unsigned long ultimoPassoSweep = 0;
const int VELOCIDADE_SWEEP_MS = 15;

void imprimirMenu() {
  Serial.println(F("\n=================================================="));
  Serial.println(F("🤖 TESTE DE SERVO SG90 - ESP32-S3 CAM"));
  Serial.println(F("=================================================="));
  Serial.println(F("COMANDOS VIA MONITOR SERIAL:"));
  Serial.println(F("  [0 a 180] : Move para o ângulo desejado (ex: 90, 45, 180)"));
  Serial.println(F("  'c'       : Centralizar em 90 graus (NEUTRO PARA ENCAIXE 3D)"));
  Serial.println(F("  'min'     : Ir para batente mínimo (0 graus)"));
  Serial.println(F("  'max'     : Ir para batente máximo (180 graus)"));
  Serial.println(F("  's'       : Iniciar / Pausar varredura suave contínua (Sweep)"));
  Serial.println(F("  '1'       : Selecionar apenas Servo 1 (GPIO 1)"));
  Serial.println(F("  '2'       : Selecionar apenas Servo 2 (GPIO 2)"));
  Serial.println(F("  'b'       : Selecionar AMBOS os servos simultaneamente"));
  Serial.println(F("--------------------------------------------------"));
  Serial.print(F("Alvo atual: "));
  if (servoSelecionado == 1) Serial.println(F("Servo 1 (GPIO 1)"));
  else if (servoSelecionado == 2) Serial.println(F("Servo 2 (GPIO 2)"));
  else Serial.println(F("Ambos (GPIO 1 e 2)"));
  Serial.print(F("Ângulo atual: "));
  Serial.print(anguloAtual);
  Serial.println(F(" graus (Centro Neutro)"));
  Serial.println(F("==================================================\n"));
}

void moverServo(int angulo) {
  angulo = constrain(angulo, 0, 180);
  anguloAtual = angulo;

  if (servoSelecionado == 1 || servoSelecionado == 3) {
    servo1.write(angulo);
  }
  if (servoSelecionado == 2 || servoSelecionado == 3) {
    servo2.write(angulo);
  }

  Serial.print(F("-> Servo posicionado em: "));
  Serial.print(angulo);
  Serial.println(F(" graus"));
}

void setup() {
  Serial.begin(115200);
  delay(1000); // Tempo para o conversor USB CDC do ESP32-S3 enumerar

  // Aloca timers do ESP32 para controle PWM
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  // Frequência padrão de controle para servos analógicos SG90 (50Hz)
  servo1.setPeriodHertz(50);
  servo2.setPeriodHertz(50);

  // Associa os pinos com pulsos padrão do SG90 (500us a 2400us)
  servo1.attach(PINO_SERVO_1, 500, 2400);
  servo2.attach(PINO_SERVO_2, 500, 2400);

  // Posição inicial: 90 graus (neutro/central para encaixe da cruzeta)
  servo1.write(90);
  servo2.write(90);
  anguloAtual = 90;

  imprimirMenu();
}

void loop() {
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    entrada.trim();

    if (entrada.length() > 0) {
      if (entrada.equalsIgnoreCase("c")) {
        modoSweep = false;
        Serial.println(F(">> [CENTRO] Alinhando em 90 graus para encaixe mecânico..."));
        moverServo(90);
      }
      else if (entrada.equalsIgnoreCase("min")) {
        modoSweep = false;
        Serial.println(F(">> [MÍNIMO] Indo para 0 graus..."));
        moverServo(0);
      }
      else if (entrada.equalsIgnoreCase("max")) {
        modoSweep = false;
        Serial.println(F(">> [MÁXIMO] Indo para 180 graus..."));
        moverServo(180);
      }
      else if (entrada.equalsIgnoreCase("s")) {
        modoSweep = !modoSweep;
        if (modoSweep) {
          Serial.println(F(">> [SWEEP] Varredura contínua iniciada (0° a 180°)..."));
        } else {
          Serial.println(F(">> [SWEEP] Varredura pausada."));
        }
      }
      else if (entrada.equals("1")) {
        servoSelecionado = 1;
        Serial.println(F(">> Selecionado: SERVO 1 (GPIO 1)"));
      }
      else if (entrada.equals("2")) {
        servoSelecionado = 2;
        Serial.println(F(">> Selecionado: SERVO 2 (GPIO 2)"));
      }
      else if (entrada.equalsIgnoreCase("b")) {
        servoSelecionado = 3;
        Serial.println(F(">> Selecionado: AMBOS OS SERVOS (GPIO 1 e 2)"));
      }
      else {
        bool ehNumero = true;
        for (unsigned int i = 0; i < entrada.length(); i++) {
          if (!isDigit(entrada.charAt(i))) {
            ehNumero = false;
            break;
          }
        }

        if (ehNumero) {
          modoSweep = false;
          int anguloDesejado = entrada.toInt();
          if (anguloDesejado >= 0 && anguloDesejado <= 180) {
            moverServo(anguloDesejado);
          } else {
            Serial.println(F("⚠️ Ângulo inválido! Digite um valor entre 0 e 180."));
          }
        } else {
          Serial.print(F("⚠️ Comando não reconhecido: '"));
          Serial.print(entrada);
          Serial.println(F("'. Digite 'c', 's', 'min', 'max' ou um número (0-180)."));
        }
      }
    }
  }

  // Execução da varredura suave
  if (modoSweep) {
    if (millis() - ultimoPassoSweep >= VELOCIDADE_SWEEP_MS) {
      ultimoPassoSweep = millis();
      anguloAtual += direcaoSweep;

      if (anguloAtual >= 180) {
        anguloAtual = 180;
        direcaoSweep = -1;
      } else if (anguloAtual <= 0) {
        anguloAtual = 0;
        direcaoSweep = 1;
      }

      if (servoSelecionado == 1 || servoSelecionado == 3) {
        servo1.write(anguloAtual);
      }
      if (servoSelecionado == 2 || servoSelecionado == 3) {
        servo2.write(anguloAtual);
      }
    }
  }
}
