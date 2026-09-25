# 🏎️ Projeto Mecânico, Case & Sistema Pan/Tilt

Este documento estabelece as diretrizes de projeto do **chassi (case)** e a **integração mecânica do sistema Pan & Tilt** com a tração do robô móvel, viabilizando a condução em primeira pessoa (FPV) fluida e estável.

---

## 📐 1. Conceito do Chassi & Distribuição de Massa (Dois Conveses)

Para acomodar toda a eletrônica com fácil manutenção e evitar emaranhados de fios, o chassi deve ser estruturado em **dois conveses (andares)** conectados por espaçadores M3 de nylon ou latão (25mm a 35mm).

```
                      +-----------------------------+
                      |   🎥 ESP32-S3 no PAN/TILT   |
                      +--------------+--------------+
                                     | (Eixo Pan)
        +============================V===========================+
        |  CONVÉS SUPERIOR                                       |
        |  • Step-Down 5V    • Driver TB6612FNG   • Mini Bus 5V  |
        |  • Módulo Buzzer   • Fiação de Sinal                   |
        +============================+===========================+
                                     | (Espaçadores M3 30mm)
        +============================V===========================+
        |  CONVÉS INFERIOR                                       |
        |  [Motor Esq 1]   🔋 Bateria 7.4V 2500mAh  [Motor Dir 1]|
        |  [Motor Esq 2]   🔘 Chave Gangorra (Trás) [Motor Dir 2]|
        +========================================================+
             (O)                                            (O)
             Roda                                           Roda
```

### 📍 Nível 1: Piso Inferior (Centro de Gravidade & Tração)
* **4x Motores JGA-050 com Suportes em L:** Parafusados rente às extremidades inferiores para maximizar a distância entre eixos (wheelbase) e a bitola (track width). Isso reduz o tombamento e garante tração firme nas 4 rodas de borracha.
* **Pack de Bateria Li-Ion 7.4V 2500mAh:** É o componente mais pesado do robô (~100g). Deve ser posicionado **exatamente no centro geométrico do piso inferior**. Isso garante que o peso seja igualmente distribuído sobre os 4 motores, permitindo curvas no próprio eixo (*skid-steer*) sem derrapagens desiguais.
* **Chave Gangorra:** Instalada no painel traseiro inferior para fácil acesso rápido ao ligar/desligar.

### 📍 Nível 2: Convés Superior (Eletrônica de Potência & Lógica)
* **Driver TB6612FNG:** Fixado próximo aos furos de passagem de fios dos motores.
* **Step-Down 5V & Barra de Pinos 5V/GND:** Centralizados para roteamento limpo dos cabos.
* **Buzzer:** Fixado na traseira ou sob o convés superior.

---

## 🔄 2. Sistema Pan & Tilt Integrado com a Câmera

### 🎯 Desafio de Engenharia Resolvido: O Cabo Flat da Câmera
O cabo flat da câmera OV5640 (ou OV2640) é extremamente curto e possui trilhas microscópicas de cobre que se rompem se submetidas a dobras repetitivas.
* **Solução:** A placa inteira (ESP32-S3-CAM ou ESP32-CAM) é fixada no suporte do **Tilt (inclinação vertical)**.
* Como a placa inteira pesa apenas ~16 gramas e o micro servo SG90 possui torque de ~1.6 kg·cm a 5V, o servo movimenta a placa com facilidade brutal e zero esforço mecânico.
* O cabo flat da câmera fica **100% estático e protegido**, eliminando qualquer risco de quebra.

```
       [ Lente OV5640 ]
      +----------------+
      |  ESP32-S3-CAM  |  <--- Placa inteira no berço do Tilt
      +-------+--------+
              | (Braço do Tilt)
        [ Servo Tilt ]
              |
       +------+-------+
       | Suporte Pan  |
       +------+-------+
              | (Eixo vertical)
        [ Servo Pan ]  <--- Fixo na frente do convés superior
              |
     =================== Convés Superior do Robô
```

### 📐 Posicionamento e Campo de Visão (FOV)
1. **Avanço Frontal:** O conjunto Pan/Tilt deve ser instalado na **extremidade dianteira** do convés superior. Se for instalado no meio do carrinho, ao inclinar o Tilt para baixo a câmera filmará o próprio teto e as rodas dianteiras do robô.
2. **Limites Angulares Recomendados no Software:**
   * **Pan (Azimute / Giro Horizontal):** Centro em **90°** (olhando para a frente). Limites operacionais de **15° a 165°** (amplitude de 150°), evitando forçar batentes físicos do servo.
   * **Tilt (Elevação / Inclinação Vertical):** Centro em **90°** (olhando para o horizonte). Limites operacionais de **50°** (olhando para o chão a 15 cm à frente do robô) até **130°** (olhando ligeiramente para cima).

### ➰ Chicote Elétrico com Alça de Alívio (Strain Relief)
Para levar os fios de alimentação da placa móvel até a base sem criar resistência mecânica:
* Utilize cabos flexíveis finos (26 AWG ou jumpers de fita flexível).
* Deixe uma **alça em formato de "U" (laço folgado)** com cerca de 5 a 7 cm descendo atrás do eixo do servo Pan.
* Quando o Pan girar para a extrema esquerda ou direita, o laço de fios simplesmente torce suavemente sobre seu próprio eixo, sem puxar os conectores nem frear o servo.

---

## 💡 3. Montagem da Barra de 8 LEDs RGB WS2812B

Você tem duas opções excelentes de posicionamento:

1. **Opção A - Farol Direcional na Câmera (Recomendada):**
   * Fixar a barra de 8 LEDs logo acima ou abaixo da placa ESP32 no próprio berço do Tilt.
   * **Vantagem:** Para onde quer que você aponte a câmera com o Pan/Tilt no escuro, o feixe de luz segue a visão, como a lanterna de um capacete de exploração!
2. **Opção B - Para-choque Frontal:**
   * Fixar a barra no bico do chassi inferior.
   * **Vantagem:** Fiação 100% estática e iluminação fixa do caminho à frente das rodas.

---

## 🎮 4. Experiência de Controle Integrado (Carrinho + Pan/Tilt)

Na interface Web embarcada no ESP32 (acessível pelo celular ou notebook):

* **Joystick Esquerdo (Tração Diferencial / Skid-Steer):**
  * Eixo Y: Marcha para frente e ré com controle proporcional de velocidade via PWM.
  * Eixo X: Curvas suaves e giro 360° no próprio eixo (rodas esquerdas e direitas girando em sentidos opostos).
* **Joystick Direito ou Área de Toque sobre o Vídeo (Controle Pan/Tilt):**
  * Ao arrastar o dedo na tela de streaming de vídeo, a câmera acompanha o movimento do dedo em tempo real.
* **Botão "Centralizar Câmera":**
  * Um toque no botão redefine Pan para 90° e Tilt para 90° instantaneamente, facilitando a navegação após inspecionar o ambiente.
* **Botão "Buzina" / "Farol":**
  * Bip no buzzer passivo e acendimento dos LEDs WS2812B em branco frio de alta intensidade.

---

## 🖨️ 5. Especificações para Fabricação do Case (3D ou Chapa)

Caso vá imprimir em 3D ou cortar chapas (acrílico/MDF):
* **Comprimento do chassi:** 140 mm a 160 mm.
* **Largura do chassi:** 80 mm a 100 mm (sem contar as rodas).
* **Furação dos suportes dos motores:** Furos para parafusos M2 / M3 compatíveis com os suportes em L dos micromotores.
* **Passagens de cabos:** Rasgos ovais centrais de 15x8 mm no convés superior para passagem limpa dos fios de alimentação e dos servos.
