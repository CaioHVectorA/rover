# 🤖 Robô Móvel ESP32 (4WD & Pan/Tilt)

Projeto de um robô móvel com tração nas 4 rodas e câmera com mecanismo Pan/Tilt, controlado via ESP32.

> **Regra Obrigatória para o Modelo / Memória Contínua do Projeto:**
> Este documento deve ser **incrementado e atualizado a cada troca de mensagens**. A ideia é que ele vá crescendo organicamente conforme conversamos e conforme o projeto anda.
> * Sempre registre aqui novas decisões, ideias validadas, respostas a dúvidas e o avanço real do projeto.
> * Mantenha os registros estritamente fiéis ao que foi de fato conversado, decidido ou testado (sem inventar esquemas elétricos prontos, pinagens definitivas ou códigos como se já estivessem funcionando enquanto ainda estamos na fase de planejamento).

---

## 📦 Componentes Comprados (Aguardando Chegada)

As compras foram finalizadas com os seguintes itens e especificações físicas:

* **Tração & Rodas (Dimensões Físicas):**
  * **4x Rodas:** Modelo **StickyMAX S20 Macia - 22 mm (RoboCore)**:
    * **Diâmetro externo:** **22 mm** (Raio = 11 mm do centro do eixo ao solo)
    * **Largura da banda:** **~12 mm**
    * **Furo de acoplamento:** **3 mm com perfil em D** (encaixe direto no eixo dos micromotores sem necessidade de parafusos adicionais)
    * **Pneu:** Silicone/borracha macia de altíssima aderência (padrão de mini sumô)
  * **4x Motores:** Motores DC com Caixa de Redução Metálica **série JGA-050 (JGA16-050)**:
    * **Diâmetro do motor:** Cilíndrico de **16 mm de diâmetro** (raio = 8 mm)
    * **Comprimento total:** ~30 mm a 35 mm (com caixa de redução toda metálica)
    * **Eixo de saída:** Aço com **perfil em D de 3 mm de diâmetro** e ~9 mm a 10 mm de comprimento
    * **Tensão nominal:** 6V a 12V (alimentado pelos 7.4V da bateria via TB6612FNG)
    * **Análise Geométrica com Rodas de 22 mm:**
      * Raio da roda de 22 mm = **11 mm** (altura do centro do eixo até o solo)
      * Raio do motor JGA-050 = **8 mm** (do centro do eixo ao fundo da carcaça)
      * **Vão livre sob o motor:** $11\text{ mm} - 8\text{ mm} = \mathbf{3\text{ mm}}$!
      * **Diretriz de Design 3D:** O chassi não deve ter assoalho fechado por baixo do motor; o motor deve ser abraçado por cima e pelas laterais, mantendo os **3 mm de folga livres** para o solo.
* **Placas de Controle:**
  * **ESP32-S3-CAM N16R8** (Mercado Livre - USB-C, 16MB Flash, 8MB PSRAM, Câmera 5MP OV5640)
  * **ESP32-CAM** (RoboCore - com câmera OV2640)
  * **Arduino Nano V3** (com cabo mini-USB)
* **Ponte H:**
  * Driver duplo MOSFET **TB6612FNG** (~20 mm x 20 mm, suporta até 1.2A contínuo por canal e lógica 3.3V)
* **Visão / Mecanismo Pan & Tilt:**
  * 2x Micro Servos **SG90 9g** (dimensões: 22.8 mm x 12.2 mm x 28.5 mm, torque de 1.6 kg·cm)
  * Suporte articulado de 2 eixos para os servos
* **Alimentação & Energia:**
  * **Pack Bateria Li-Ion 2S 7.4V 2500mAh com BMS integrado:** Dimensões aprox. **69 mm x 37 mm x 19 mm**, peso ~100g, com conector JST-RCY fêmea
  * **Regulador Step-Down Mini 560 5V:** Placa ultracompacta (30 mm x 18 mm x 5.5 mm) que rebaixa 7.4V para 5.0V fixos com até 5A
  * **Chave Geral Liga/Desliga:** Chave gangorra **KCD1-101 2T** (recorte para encaixe no painel 3D: **19 mm x 13 mm**)
* **Sinalização & Acessórios:**
  * Módulo **WS2812B com 8 LEDs RGB endereçáveis** (barra estreita de ~53 mm x 10 mm)
  * Módulo **Buzzer passivo 5V** (diâmetro ~12 mm)
  * Jumpers Fêmea-Fêmea e Macho-Macho (40 de cada)

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
6. **Galeria de Fotos dos Componentes Reais ([`inspiracoes/`](file:///home/usuario/Documentos/rover/inspiracoes/INSPIRACOES_CASE_E_PAN_TILT.md)):**
   * Pasta `/inspiracoes` atualizada exclusivamente com **fotos reais dos produtos adquiridos e montagens reais**:
     * `roda_stickymax_s20_22mm.png`: Foto de alta resolução da roda de sumô StickyMAX S20 (22mm).
     * `micromotor_reducao_metalica.png`: Foto do micromotor N20 com caixa de redução metálica e eixo D 3mm.
     * `suporte_pan_tilt_robocore.png`: Suporte comercial de 2 eixos para os servos SG90.
     * `pan_tilt_sg90_mechanism.jpg` e `esp32_cam_pan_tilt_assembled.jpg`: Montagens reais de referência da comunidade.
7. **Estilo Visual, Rodas 22 mm e Motores JGA-050 (Desafio dos 3 mm de Vão Livre):**
   * **Os motores JGA-050 cabem com as rodas de 22 mm, mas com folga justa de 3 mm:**
     * $11\text{ mm (roda)} - 8\text{ mm (motor JGA)} = 3\text{ mm}$ do chão.
     * **Solução na Impressão 3D:** O chassi abraça o motor de 16 mm por cima e pelos lados. A face inferior do motor fica exposta (sem plástico embaixo dele) para não "roubar" nenhum milímetro desses 3 mm.
     * **Compatibilidade Futura:** Como o eixo do JGA-050 é padrão de 3 mm com chanfro em D, se no futuro o usuário quiser andar em pisos irregulares ou tapetes mais altos, basta desencaixar as rodas de 22 mm e colocar rodas de 32 mm, aumentando o vão livre de 3 mm para 8 mm sem refazer o robô.
   * **Chassi Fechado/Carenado em 3D:** Corpo protegendo bateria e eletrônica internamente, com a cabeça móvel encapsulando o ESP32 (expondo apenas lente e barra de 8 LEDs).
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
