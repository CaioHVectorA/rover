# 🛠️ Guia Rápido: Teste e Encaixe do Servo SG90 na Impressão 3D

Este guia orienta o teste elétrico e o procedimento correto de **alinhamento mecânico (90° neutro)** antes de fixar definitivamente os servos SG90 nas peças impressas em 3D (`Case_drone_terrestre`, `Estrutura_drone_terrestre`, `Case_Eixo`, etc.).

---

## ⚠️ A Regra de Ouro da Mecânica do Servo SG90

> [!CAUTION]
> **NUNCA force o eixo do servo SG90 com as mãos.**
> As engrenagens internas do SG90 são de nylon e podem quebrar/espanar se forçadas manualmente. 
> Sempre faça a movimentação alimentando o servo e enviando comandos de controle.

> [!IMPORTANT]
> **NUNCA parafuse o braço (cruzeta) antes de energizar o servo em 90°.**
> Se você encaixar o braço plástico na posição errada com o servo desligado, quando o robô ligar o servo tentará rodar até o batente e **forçará contra a parede da sua peça impressa**, podendo quebrar a impressão ou queimar o motor.

---

## 🔌 1. Esquema de Ligação (Arduino Nano V3)

O servo possui um conector de 3 vias com código de cores padrão:

| Cor do Cabo | Sinal | Pino no Arduino Nano V3 |
|---|---|---|
| **Marrom** (ou Preto) | **GND** | Qualquer pino **GND** |
| **Vermelho** | **VCC (5V)** | Pino **5V** do Nano |
| **Laranja** (ou Amarelo) | **Sinal PWM** | Pino **D9** (Servo 1 - Pan) |
| *(Opcional 2º servo)* | **Sinal PWM** | Pino **D10** (Servo 2 - Tilt) |

*(Para teste de bancada de 1 a 2 servos sem carga pesada, a própria porta USB do computador conectada ao Nano é suficiente para alimentar).*

---

## 💻 2. Como Carregar o Código de Teste

O sketch pronto está salvo em:
[`testes/teste_servo_sg90/teste_servo_sg90.ino`](file:///c:/Users/caihe/Documents/develop/rover/testes/teste_servo_sg90/teste_servo_sg90.ino)

### Pela Arduino IDE:
1. Conecte o **Arduino Nano** à porta USB do computador pelo cabo azul.
2. Abra a **Arduino IDE**.
3. Vá em **Arquivo -> Abrir** e selecione `testes/teste_servo_sg90/teste_servo_sg90.ino`.
4. Em **Ferramentas -> Placa**, selecione **Arduino Nano**.
5. Em **Ferramentas -> Processador**, selecione **ATmega328P** (se falhar o upload, mude para *ATmega328P (Old Bootloader)*).
6. Em **Ferramentas -> Porta**, selecione a porta COM correspondente ao Nano.
7. Clique em **Carregar (Upload)** (seta para a direita).
8. Abra o **Monitor Serial** (canto superior direito) e mude a velocidade para **115200 baud**.

---

## 🎯 3. Passo a Passo do Teste de Encaixe 3D

1. **Subir o código:** Assim que o código carregar, o servo se posicionará automaticamente em **90° (posição central exata)**.
2. **Centralização garantida:** No Monitor Serial, você pode digitar `c` a qualquer momento para garantir que ele está travado em 90°.
3. **Encaixe da Cruzeta/Braço:** Com o servo ligado e mantendo a posição de 90°, posicione a peça impressa em 3D (ou o braço articulador) na sua **posição central/neutra** (nem virado para a esquerda nem para a direita). Encaixe o braço dentado sobre o eixo do servo.
4. **Verificação de Folgas (Batentes):**
   * Digite `min` (ou `0`): observe se a peça impressa tem folga ou se esbarra na lateral.
   * Digite `max` (ou `180`): observe o batente oposto.
   * Digite `s` (Sweep): o servo fará uma varredura contínua e suave de 0° a 180°. Observe se há atrito, se o plástico range ou se o motor esquenta.
5. **Ajuste de Tolerância 3D (se necessário):**
   * Se o encaixe estiver muito apertado a ponto de deformar a carcaça do servo, dê um leve lixamento nas paredes internas da impressão 3D (folga recomendada no CAD: ~0.2mm a 0.3mm em cada lado).
   * Se estiver com folga excessiva, uma tira fina de fita isolante ou calço segura o corpo do servo com firmeza.
