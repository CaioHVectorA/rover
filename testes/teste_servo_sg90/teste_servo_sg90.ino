/*
 * ============================================================================
 * TESTE DE SERVO MOTOR SG90 - ALINHAMENTO E ENCAIXE DE IMPRESSÃO 3D
 * ============================================================================
 * Projeto: Rover / Drone Terrestre
 * Microcontrolador: Arduino Nano V3 (ou Arduino Uno)
 * 
 * ESQUEMA DE LIGAÇÃO (Padrão Micro Servo 9g SG90):
 * ------------------------------------------------
 * Cor do Fio | Função      | Conectar no Arduino Nano
 * -----------|-------------|-------------------------
 * Marrom     | GND         | GND
 * Vermelho   | VCC (5V)    | 5V (para teste sem carga / 1-2 servos)
 * Laranja    | Sinal (PWM) | D9  (Servo 1 - Pan / Eixo Principal)
 * (Opcional) | Sinal (PWM) | D10 (Servo 2 - Tilt / Eixo Secundário)
 * 
 * INSTRUÇÕES PARA ENCAIXE NA PEÇA 3D:
 * 1. Conecte o servo no Arduino (sem o braço/cruzeta parafusado ainda).
 * 2. Carregue este código no Arduino Nano.
 * 3. O servo irá automaticamente para 90° (posição neutra/central).
 * 4. COM O SERVO LIGADO EM 90°, encaixe a cruzeta/braço plástico na posição 
 *    central/reta alinhada com a sua peça impressa em 3D.
 * 5. Abra o Monitor Serial (115200 bps) para testar os limites mecânicos (0° a 180°)
 *    e garantir que a impressão 3D não está raspando ou travando o servo.
 * ============================================================================
 */

#include <Servo.h>

Servo servo1; // Servo 1 (Pino D9 - Pan)
Servo servo2; // Servo 2 (Pino D10 - Tilt)

const int PINO_SERVO_1 = 9;
const int PINO_SERVO_2 = 10;

int servoSelecionado = 1; // 1 = Servo 1, 2 = Servo 2, 3 = Ambos
int anguloAtual = 90;
bool modoSweep = false;
int direcaoSweep = 1;
unsigned long ultimoPassoSweep = 0;
const int VELOCIDADE_SWEEP_MS = 15; // Intervalo em ms entre cada grau na varredura

void imprimirMenu() {
  Serial.println(F("\n=================================================="));
  Serial.println(F("🤖 TESTE DE SERVO SG90 - CALIBRAÇÃO IMPRESSÃO 3D"));
  Serial.println(F("=================================================="));
  Serial.println(F("COMANDOS DISPONÍVEIS:"));
  Serial.println(F("  [0 a 180] : Move para o ângulo desejado (ex: 90, 45, 180)"));
  Serial.println(F("  'c'       : Centralizar em 90 graus (NEUTRO PARA ENCAIXE)"));
  Serial.println(F("  'min'     : Ir para batente mínimo (0 graus)"));
  Serial.println(F("  'max'     : Ir para batente máximo (180 graus)"));
  Serial.println(F("  's'       : Iniciar / Parar varredura suave contínua (Sweep)"));
  Serial.println(F("  '1'       : Controlar apenas Servo 1 (Pino D9)"));
  Serial.println(F("  '2'       : Controlar apenas Servo 2 (Pino D10)"));
  Serial.println(F("  'b'       : Controlar AMBOS os servos simultaneamente"));
  Serial.println(F("--------------------------------------------------"));
  Serial.print(F("Alvo atual: "));
  if (servoSelecionado == 1) Serial.println(F("Servo 1 (D9)"));
  else if (servoSelecionado == 2) Serial.println(F("Servo 2 (D10)"));
  else Serial.println(F("Ambos (D9 e D10)"));
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
  while (!Serial && millis() < 3000); // Aguarda serial estabilizar

  servo1.attach(PINO_SERVO_1);
  servo2.attach(PINO_SERVO_2);

  // Posiciona em 90° imediatamente ao iniciar (Posição Neutra)
  servo1.write(90);
  servo2.write(90);
  anguloAtual = 90;

  imprimirMenu();
}

void loop() {
  // Leitura de comandos via Monitor Serial
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
          Serial.println(F(">> [SWEEP] Varredura contínua suave INICIADA (0° a 180°)..."));
        } else {
          Serial.println(F(">> [SWEEP] Varredura PAUSADA."));
        }
      }
      else if (entrada.equals("1")) {
        servoSelecionado = 1;
        Serial.println(F(">> Selecionado: SERVO 1 (Pino D9)"));
      }
      else if (entrada.equals("2")) {
        servoSelecionado = 2;
        Serial.println(F(">> Selecionado: SERVO 2 (Pino D10)"));
      }
      else if (entrada.equalsIgnoreCase("b")) {
        servoSelecionado = 3;
        Serial.println(F(">> Selecionado: AMBOS OS SERVOS (D9 e D10)"));
      }
      else {
        // Verifica se é um número (graus)
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

  // Execução do Sweep suave (quando ativado)
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
