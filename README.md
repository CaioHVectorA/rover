# 🤖 Robô Móvel ESP32 (4WD & Pan/Tilt)

Projeto de um robô móvel com tração nas 4 rodas e câmera com mecanismo Pan/Tilt, controlado via ESP32.

> **Regra Obrigatória para o Modelo / Memória Contínua do Projeto:**
> Este documento deve ser **incrementado e atualizado a cada troca de mensagens**. A ideia é que ele vá crescendo organicamente conforme conversamos e conforme o projeto anda.
> * Sempre registre aqui novas decisões, ideias validadas, respostas a dúvidas e o avanço real do projeto.
> * Mantenha os registros estritamente fiéis ao que foi de fato conversado, decidido ou testado (sem inventar esquemas elétricos prontos, pinagens definitivas ou códigos como se já estivessem funcionando enquanto ainda estamos na fase de planejamento).

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
6. **Mapeamento de Inspirações de Cases 3D ([`inspiracoes/`](file:///home/usuario/Documentos/rover/inspiracoes/INSPIRACOES_CASE_E_PAN_TILT.md)):**
   * Pasta `/inspiracoes` criada contendo referências do Printables, Thingiverse, MakerWorld e GrabCAD para placas ESP32-S3-WROOM / ESP32-CAM com micro servos SG90.
   * Destaques mapeados: cases compactos snap-fit, ranhuras de ventilação para o chip S3, suporte direto para a cruzeta (servo horn) do SG90 e alojamento integrado para os LEDs WS2812B.

---

## 🎯 Foco Atual (Brainstorm & Discussão)

* **Definição da Geometria do Case 3D:** Escolher entre um case estilo "torreta" exposta ou estilo "cockpit" semi-embutido no chassi do robô.
* **Sistema Pan & Tilt:** Integrar os encaixes dos 2 servos SG90 ao chassi 4WD de forma firme e com alívio nos fios flexíveis.
* **Facilitação da Elétrica:** Pensar na melhor forma de organizar a fiação, chaves e conectores antes das peças chegarem.
