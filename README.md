# 🤖 Robô Móvel ESP32 (4WD & Pan/Tilt)

Projeto de um robô móvel com tração nas 4 rodas e câmera com mecanismo Pan/Tilt, controlado via ESP32.

> **Nota para o Modelo / Memória do Projeto:**
> Este documento registra estritamente o estado real do projeto e as decisões tomadas até o momento. Não invente esquemas elétricos prontos, pinagens finais ou códigos já testados, pois as peças acabaram de ser compradas e o projeto está na fase conceitual de case e mecânica.

---

## 📦 Componentes Comprados (Aguardando Chegada)

As compras foram finalizadas com os seguintes itens:

* **Placas:**
  * ESP32-S3-CAM (comprado no Mercado Livre)
  * ESP32-CAM (comprado na RoboCore)
  * Arduino Nano V3
* **Tração:**
  * 4x Micromotores de redução metálica (série JGA-050 ou similar)
  * 4x Rodas com cubo e acabamento emborrachado
  * Suportes de fixação dos motores
* **Ponte H:**
  * Driver duplo TB6612FNG (TB66)
* **Visão / Mecanismo:**
  * 2x Micro Servos SG90 para o Pan/Tilt
* **Alimentação & Elétrica:**
  * Pack Bateria Li-Ion 7.4V 2500mAh com BMS embutido
  * Regulador Step-Down DC-DC
  * Chave gangorra liga/desliga
* **Sinalização & Feedback:**
  * Barra com 8 LEDs RGB WS2812B
  * Módulo Buzzer passivo 5V
* **Acessórios:**
  * Cabos, conectores e jumpers

---

## 📌 Decisões e Alinhamentos Feitos até Agora

1. **Linha ESP32:** Foco total no ecossistema ESP32 para controle e streaming de vídeo.
2. **Fabricação 100% em Impressão 3D:** Toda a estrutura física, chassi/case e suportes serão impressos em 3D.
3. **Mecânica do Pan & Tilt com a Câmera:**
   * O cabo flat da câmera é muito curto e frágil.
   * Decisão: Montar a própria placa ESP32 no berço móvel de inclinação vertical (Tilt), para que a câmera não sofra torção no cabo flat.
4. **Alimentação e Cuidados:**
   * Bateria de 7.4V precisa alimentar os motores (via TB6612FNG) e passar pelo Step-Down para gerar 5V para o ESP32 e servos.
   * Não sobrecarregar a placa tentando alimentar servos direto dos pinos do microcontrolador.
5. **Integração Carrinho + Pan/Tilt:**
   * O objetivo principal agora é fazer o carrinho se movimentar juntamente com a movimentação da câmera nos eixos Pan e Tilt.

---

## 🎯 Foco Atual (Brainstorm & Discussão)

* **Design do Case 3D:** Como modelar o chassi para acomodar a bateria, o TB6612FNG, os 4 motores e o mecanismo Pan/Tilt.
* **Sistema Pan & Tilt:** Como posicionar e montar os servos para trabalhar em harmonia com o movimento do carrinho.
* **Facilitação da Elétrica:** Pensar na melhor forma de organizar a fiação e conectores antes das peças chegarem, evitando gambiarras na montagem.
