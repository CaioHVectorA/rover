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
6. **Galeria Visual de Inspirações ([`inspiracoes/`](file:///home/usuario/Documentos/rover/inspiracoes/INSPIRACOES_CASE_E_PAN_TILT.md)):**
   * Pasta `/inspiracoes` criada com imagens de referência e renders 3D conceituais.
7. **Estilo Visual e Carcaça Fechada (`04_chassi_fechado_sumo.jpg`):**
   * Chassi fechado/carenado em impressão 3D: eletrônica, bateria e motores protegidos internamente, sem fios ou placas expostas.
   * Rodas de borracha compactas estilo sumô (alta aderência).
   * Cabeça móvel totalmente encapsulada: o ESP32 fica 100% alojado internamente, ficando exposto apenas o círculo da lente da câmera e a barra de 8 LEDs RGB logo abaixo.
8. **Cinemática Definida (Pan na Base e Tilt no Topo):**
   * **Ordem:** O servo de Pan (giro horizontal) fica parafusado na base do chassi, e o servo de Tilt (inclinação vertical) fica no braço móvel segurando a cabeça da câmera.
   * **Vantagens de Engenharia:**
     * Menor peso móvel: o servo de Tilt levanta apenas a caixinha da câmera (não precisa levantar o peso de outro motor).
     * Horizonte estável: ao virar para os lados mesmo com a câmera inclinada para baixo, o horizonte não tomba na diagonal (evita efeito indesejado de roll).

---

## 🎯 Foco Atual (Brainstorm & Discussão)

* **Encaixes e Abertura do Case Fechado:** Como dividir a carcaça 3D (ex: tampa superior removível para manutenção interna e troca/recarga da bateria).
* **Fixação dos 4 Motores JGA-050:** Projeto dos berços internos para os motores de redução metálica no chassi fechado.
* **Facilitação da Elétrica:** Distribuição dos conectores e fiação interna antes da chegada das peças.
