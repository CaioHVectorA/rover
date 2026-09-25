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
  * **4x Rodas:** Modelo **32 mm de Diâmetro** (Borracha/Silicone macia de alta aderência, padrão sumô/StickyMAX 32mm):
    * **Diâmetro externo:** **32 mm** (garante vão livre do solo de ~8 mm a 10 mm, evitando que a barriga do robô raspe no chão)
    * **Furo de acoplamento:** **3 mm com perfil em D** (encaixe direto no eixo dos motores JGA-050)
    * **Pneu:** Borracha/silicone macio de alta tração em pisos lisos
  * **4x Motores:** Micromotores DC com **Caixa de Redução Metálica série JGA-050 (JGA16-050)**:
    * **Diâmetro do motor:** Cilíndrico de **16 mm de diâmetro** (mais torque e robustez que o N20 tradicional)
    * **Comprimento total:** ~30 mm a 35 mm (com caixa de redução toda metálica)
    * **Eixo de saída:** Metálico com **perfil em D de 3 mm de diâmetro** e ~9 mm a 10 mm de comprimento
    * **Tensão nominal:** 6V a 12V (compatível com a bateria Li-Ion 7.4V)
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
7. **Estilo Visual, Rodas de 32 mm e Motores JGA-050:**
   * Chassi fechado/carenado em impressão 3D: eletrônica, bateria e motores protegidos internamente, sem fios ou placas expostas.
   * **Adoção de Rodas de 32 mm (em vez de 22 mm):** A roda de 22 mm deixava o robô quase raspando o chassi no chão (vão livre de ~3 mm). Com 32 mm, o vão livre sobe para ~8 a 10 mm, permitindo vencer desníveis, tapetes e pequenos obstáculos com velocidade de cruzeiro mais agradável (~17 cm/s a 100 RPM).
   * **Motores série JGA-050 (JGA16-050):** Diâmetro de 16 mm com caixa de redução metálica e eixo D de 3 mm. Oferece muito mais torque e durabilidade sob carga que os micromotores N20 menores.
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
