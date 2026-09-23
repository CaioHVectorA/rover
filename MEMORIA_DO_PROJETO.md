# 🧠 Memória Externa e Diário de Decisões do Projeto

Este documento serve como a **memória viva e persistente** de todas as nossas conversas, decisões técnicas, escolha de componentes, fornecedores e soluções mecânicas/elétricas do robô móvel. Toda nova conversa relevante e decisão tomada será documentada e atualizada aqui.

> 📚 **Documentos Relacionados:**
> * 🗺️ [**`ROADMAP.md`**](file:///home/usuario/Documentos/rover/ROADMAP.md): Canvas do MVP, fluxo visual em Mermaid e cronograma em 5 fases.
> * 🛒 [**`linha-esp32-s3/LISTA_DE_COMPRAS.md`**](file:///home/usuario/Documentos/rover/linha-esp32-s3/LISTA_DE_COMPRAS.md): Lista consolidada de componentes no Mercado Livre e RoboCore.
> * 🏠 [**`README.md`**](file:///home/usuario/Documentos/rover/README.md): Visão geral do repositório.

---

## 📌 1. Visão Geral e Objetivo do Robô
* **Proposta:** Robô móvel educacional com tração nas 4 rodas (4WD - Skid-Steer / diferencial), câmera móvel com visão em tempo real via Wi-Fi, sinalização visual (LEDs RGB) e sonora (áudio/buzzer).
* **Arquitetura Selecionada:** Baseada no microcontrolador **ESP32-S3 CAM (All-in-One)**, eliminando a necessidade de Raspberry Pi + Arduino e reduzindo drasticamente o custo e a complexidade.
* **Estratégia de Aquisição:**
  1. **Mercado Livre:** Placa principal ESP32-S3 CAM N16R8 com câmera OV5640 5MP.
  2. **RoboCore (`robocore.net`):** Todo o restante dos componentes (motores de redução, rodas de borracha, servos, driver de motor, regulador, baterias, etc.) em um único pedido com pronta entrega e qualidade profissional.

---

## 🗣️ 2. Histórico de Conversas e Decisões

### 🗓️ Sessão 1: Definição da Arquitetura e Periféricos (Mensagem de Áudio)
* **Objetivos informados pelo usuário:**
  * Uso do microcontrolador ESP32-S3 CAM;
  * 2 micro servos para controle de câmera (Pan & Tilt);
  * Dispositivo de saída de som: alto-falante ou buzzer;
  * LEDs RGB para iluminação e feedback de status;
  * 4 motores com caixa de redução (~200 RPM) e 4 rodas de borracha para acabamento profissional;
  * ESP32 comprado no Mercado Livre e o restante em loja única;
  * **Dúvida levantada:** *"Não sei se estou esquecendo de alguma coisa..."*
* **Análise técnica & Itens críticos identificados como faltantes:**
  * **Driver de Motor (Ponte H):** O ESP32 não pode acionar motores diretamente. É indispensável um driver como TB6612FNG, DRV8833 ou L9110/MX1616.
  * **Alimentação & Baterias:** Baterias 18650 Li-Ion (2S = 7.4V) + suporte + carregador.
  * **Regulador Step-Down (DC-DC):** Os servos e o ESP32 exigem 5.0V estáveis. **Regra de ouro:** nunca alimentar servos pelo pino 5V do ESP32 para evitar *brownout* (reinicialização da placa por queda de tensão provocada pelos servos).
  * **Economia de Pinos (GPIO):** Sugerido o uso de LEDs endereçáveis **WS2812B (Neopixel)** (usam apenas 1 pino de dados para múltiplos LEDs) e definição entre Buzzer (1 pino) vs Amplificador I2S MAX98357A (voz real).

---

### 🗓️ Sessão 2: Escolha da Placa no ML e Fornecedor RoboCore
* **Link selecionado pelo usuário:** [Placa ESP32-S3 CAM OV5640 Wifi Bluetooth 5.0 BLE N16R8 no Mercado Livre](https://www.mercadolivre.com.br/p/MLB2061307865?matt_tool=38524122&pdp_filters=item_id:MLB5139266661)
* **Validação Técnica da Placa:**
  * **Modelo:** ESP32-S3 CAM N16R8 (16MB Flash / 8MB Octal PSRAM).
  * **Câmera:** Sensor OV5640 de 5 Megapixels.
  * **Interface:** Conector USB Type-C nativo (dispensa gravador FTDI serial externo).
  * **Avaliação:** Escolha ideal para transmissão de vídeo estável com baixo consumo e bom framerate.
* **Fornecedor Eleito:** **RoboCore**, pela reputação técnica, qualidade dos motores de redução em metal e rodas de alta aderência (linha StickyMAX).

---

### 🗓️ Sessão 3: Solução da Mecânica do Pan & Tilt
* **Dúvida/Desafio do Usuário:**
  > *"O maior problema possivelmente vai ser como fazer a mecânica de pan tilt no esp, já que a câmera é acoplada no esp."*
* **Resolução de Engenharia Definida:**
  * **A placa ESP32-S3 inteira é montada sobre o mecanismo Pan/Tilt:**
    * **Massa:** O ESP32-S3 CAM pesa apenas ~16 gramas.
    * **Torque do Servo:** O micro servo SG90 possui torque de 1.5 a 1.8 kg.cm, sendo capaz de movimentar até 150g com tranquilidade.
    * **Proteção do Flat Cable:** O cabo da câmera OV5640 é extremamente curto e frágil. Tentar movimentar apenas a lente levaria ao rompimento das trilhas internas por fadiga. Mantendo a placa montada no suporte, o cabo flat fica 100% estático.
    * **Chicote com Alívio de Tensão:** A ligação entre a placa (móvel) e a base do chassi é feita por um feixe flexível de fios jumpers com folga em arco (laço de alívio).
    * **Bônus:** A antena Wi-Fi do ESP32 fica na posição mais alta do robô, maximizando o sinal.

---

### 🗓️ Sessão 4: Definição do Escopo do MVP e Criação do Roadmap
* **Diretriz do Usuário:**
  * O foco inicial do robô será **estritamente em rede Wi-Fi local** com o **MVP**:
    1. Mobilidade completa (robô 4WD se movimentando sob controle remoto);
    2. Transmissão da câmera em tempo real via Wi-Fi;
    3. Controle do Pan & Tilt em tempo real;
  * Deixar conexão de longa distância (4G/Internet) e recursos secundários (som/LEDs) para as fases seguintes.
  * Criação de um documento visual de Roadmap com formato Canvas e cronograma em fases.
* **Ações Realizadas:**
  * Criação do arquivo [`ROADMAP.md`](file:///home/usuario/Documentos/rover/ROADMAP.md) contendo o **Canvas do MVP**, o diagrama de fases em Mermaid e o detalhamento das 5 fases de implementação.
  * Confirmação técnica de que o ESP32-S3 possui base pronta de código (`esp_camera` e `CameraWebServer` com MJPEG e PSRAM) que acelera o desenvolvimento em mais de 80%.

---

## 🛠️ 3. Matriz Consolidada de Componentes

| Subsistema | Componente | Qtd | Loja | Justificativa / Especificação |
|---|---|:---:|:---:|---|
| **Cérebro & Visão** | Placa ESP32-S3 CAM N16R8 + OV5640 5MP | 1 | Mercado Livre | USB-C nativo, 16MB Flash, 8MB PSRAM, Wi-Fi/BLE |
| **Mecânica Pan/Tilt** | Micro Servo 9g SG90 (com cruzetas) | 2 | RoboCore | Movimentação horizontal (Pan) e vertical (Tilt) |
| **Mecânica Pan/Tilt** | Suporte Pan-Tilt 2 eixos para SG90 | 1 | RoboCore / Impressão 3D | Suporte mecânico articulado |
| **Tração (Motores)** | Micromotores DC com redução de metal (~200 RPM) | 4 | RoboCore | Eixo D de 3mm, alto torque e tamanho compacto |
| **Tração (Rodas)** | Rodas de Borracha (ex: StickyMAX 3mm) | 4 | RoboCore | Alta aderência em pisos lisos |
| **Tração (Fixação)** | Suportes em "L" para Micromotores | 4 | RoboCore | Fixação dos motores ao chassi |
| **Ponte H** | Módulo Driver Ponte H (L9110 / MX1616 ou L298N) | 1 | RoboCore | Controle de sentido e PWM dos 4 motores |
| **Regulação de Tensão**| Conversor Step-Down DC-DC (LM2596 ou XL4015) | 1 | RoboCore | Rebaixa 7.4V para 5.0V estáveis (ESP32 + Servos) |
| **Alimentação** | Suporte para 2 Baterias 18650 com rabicho | 1 | RoboCore | Conexão em série (7.4V nominais) |
| **Alimentação** | Baterias 18650 Li-Ion Recarregáveis | 2 | RoboCore / Especializada | Alta densidade energética |
| **Saída Sonora** | Buzzer Passivo ou Ativo 5V | 1 | RoboCore | Bips de status, alarme e inicialização |
| **Sinalização Visual**| Módulo LED RGB Endereçável WS2812B | 1 | RoboCore | Efeitos luminosos coloridos usando apenas 1 GPIO |
| **Acessórios** | Fios Jumpers + Chave Gangorra (Liga/Desliga) | 1 | RoboCore | Chicote elétrico e interrupção geral |

---

## ⚡ 4. Diretrizes Elétricas e Boas Práticas Estabelecidas
1. **GND Comum Obrigatório:** Todos os GNDs (Bateria, Step-Down, ESP32, Servos e Driver) devem ser interligados.
2. **Isolamento de Linhas de Corrente:**
   * A linha de 7.4V da bateria vai direto para o Step-Down e para o pino de potência (`VM`/`VCC2`) dos motores.
   * A saída de 5.0V do Step-Down alimenta o ESP32 (pino 5V) e os 2 Servos em paralelo.
   * **NUNCA** puxar a alimentação dos servos a partir do pino 5V ou 3.3V do ESP32.
3. **Mapeamento Racional de GPIOs:**
   * Motores (4 a 6 pinos para PWM e direção);
   * Servos (2 pinos PWM);
   * Buzzer (1 pino PWM/tone);
   * LEDs WS2812B (1 pino de dados serial).

---

### 🗓️ Sessão 5: Montagem Automatizada do Carrinho RoboCore via Python
* **Ação Executada:**
  * Criação de ambiente de automação direta de navegador usando **Python + Playwright** para contornar qualquer instabilidade e interagir diretamente com a loja `robocore.net`.
  * Mapeamento de 100% dos produtos em estoque: micro servos SG90, suporte pan/tilt 2 eixos, 4 micromotores 6V 100RPM em metal, 4 rodas StickyMAX S20 macias com cubo 3mm, 2 pares de suportes em L, driver L298N, regulador Step-Down Mini 560 5V, Pack de baterias Li-Ion 7.4V com BMS embutido, rabicho JST fêmea, buzzer passivo, régua de 8 LEDs WS2812B, chave gangorra e jumpers (F-F e M-M).
  * **Carrinho montado com sucesso (22 itens no total):** R$ 435,61 no PIX ou R$ 458,54 em 3x sem juros no cartão.
### 🗓️ Sessão 6: Pan/Tilt em Impressão 3D, 2 Drivers L298N, Arduino Nano no Carrinho e Planilha Minimalista
* **Decisões de Engenharia & Ações Executadas:**
  1. **Arduino Nano V3 no Carrinho RoboCore:** O Arduino Nano V3 com cabo USB foi incluído diretamente no pedido da RoboCore por **R$ 28,90**. Ele atuará como co-processador de tempo real (motores e servos), liberando o ESP32-S3 para a câmera e Wi-Fi.
  2. **Giroscópio para VR Head Tracking:** Verificado o catálogo da RoboCore em tempo real: o MPU-6050 está esgotado na RoboCore (o único giroscópio em estoque lá é o BNO055 por R$ 219,90). Por custo-benefício, o MPU-6050 (~R$ 16,90) permanece alocado no Mercado Livre junto com o ESP32-S3 CAM.
  3. **Remoção da 'Parte 3' (Impressão 3D):** A seção de estimativas de impressão 3D foi retirada da documentação e da planilha para deixar tudo focado estritamente nas compras.
  4. **Planilha Excel Simples e Minimalista (`LISTA_DE_COMPRAS_ROVER_ESP32.xlsx`):** A planilha foi reformulada para ser ultra limpa, sem cabeçalhos pesados, sem banners decorativos e sem mesclagens complexas, permitindo edição direta e simples no Excel.
* **Status do Carrinho RoboCore Atual:** **23 itens** | **Subtotal R$ 495,44** | **R$ 470,67 à vista no PIX** | **3x de R$ 165,15 sem juros**.

### 🗓️ Sessão 7: Migração para Arquitetura Raspberry Pi 3 + Nano + Câmera CSI + 2 Drivers L298N
* **Decisões de Engenharia & Ações Executadas:**
  1. **Raspberry Pi 3 como Cérebro Principal:** O projeto adotou a Raspberry Pi 3 Model B para rodar Linux e streaming de vídeo WebRTC de ultrabaixa latência (<80ms).
  2. **Arduino Nano V3 como Co-processador:** O Nano assume o controle PWM dos 4 motores (2x Drivers L298N) e dos 2 servos SG90 via comunicação serial USB com a Pi 3.
  3. **Câmera CSI vs Webcam USB:** Avaliação confirmou a superioridade da Câmera CSI Rev 1.3 (3g, cabo flat sem torque mecânico nos servos, encoder H.264 direto no hardware Broadcom).
  4. **Atualização do Carrinho RoboCore via Script Python:** Carrinho atualizado para **25 itens (17 linhas)** incluindo a Câmera Pi CSI Rev 1.3 e o suporte Pan/Tilt comercial sob medida. Subtotal: **R$ 552,24** (ou **R$ 524,63 no PIX**).
  5. **Planilhas Excel Geradas:** Criada a planilha minimalista [**`LISTA_DE_COMPRAS_ROVER_PI.xlsx`**](file:///c:/Users/caihe/Documents/develop/rover/LISTA_DE_COMPRAS_ROVER_PI.xlsx).

---

## 📝 5. Próximos Passos Imediatos
- [x] Mapear os links e códigos exatos dos produtos na RoboCore para fechar o carrinho de compras.
- [x] Atualizar o carrinho de compras na RoboCore para a arquitetura Raspberry Pi 3 (25 itens).
- [x] Gerar planilha consolidada XLSX minimalista (`LISTA_DE_COMPRAS_ROVER_PI.xlsx`).
- [ ] Elaborar o esquema elétrico de pinagem Raspberry Pi 3 + Arduino Nano + 2x L298N + Step-Down 5V.
- [ ] Configurar imagem Raspberry Pi OS Lite com OverlayFS (Read-Only) e streamer WebRTC.



