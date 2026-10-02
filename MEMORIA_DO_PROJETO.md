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
  5. **Planilhas Excel Geradas:** Criada a planilha minimalista [**`LISTA_DE_COMPRAS_ROVER.xlsx`**](file:///c:/Users/caihe/Documents/develop/rover/LISTA_DE_COMPRAS_ROVER.xlsx).

### 🗓️ Sessão 8: Unificação das Planilhas em Arquivo Único com 2 Abas
* **Decisão do Usuário & Ação Executada:**
  1. **Consolidação em Arquivo Único:** Atendendo ao pedido do usuário de manter apenas duas planilhas, todas as listas de compras foram consolidadas no arquivo único [**`LISTA_DE_COMPRAS_ROVER.xlsx`**](file:///c:/Users/caihe/Documents/develop/rover/LISTA_DE_COMPRAS_ROVER.xlsx).
  2. **Estrutura com 2 Planilhas (Abas):**
     * 📑 **Aba 1 (`Rover ESP32-S3`):** 18 itens (15 RoboCore + 3 Mercado Livre), com fórmulas automáticas de subtotal, desconto PIX (-5%) e total geral estimado (R$ 659,47).
     * 📑 **Aba 2 (`Rover Raspberry Pi 3`):** 20 itens (17 RoboCore + 3 Mercado Livre), com fórmulas automáticas de subtotal, desconto PIX (-5%) e total geral estimado (R$ 1.003,43).
  3. **Limpeza do Repositório:** Remoção definitiva das planilhas intermediárias e duplicadas (`_RESTAURADA`, `_ATUALIZADA`, `_FINAL`, etc.), mantendo a raiz do projeto limpa e organizada.

### 🗓️ Sessão 9: Validação do ESP32-S3 em Wi-Fi e Arquitetura de Sistemas Distribuídos na Nuvem (Fly.io)
* **Diagnósticos e Ações de Engenharia Executadas:**
  1. **Solução do Reset de Boot / Brownout (`E BOD: Brownout detector was triggered`):**
     * Identificado que o uso de `WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0)` (comum no ESP32 clássico) é **incompatível no ESP32-S3**, pois corrompe o registrador do RTC e força o reset contínuo (`rst:0x3 RTC_SW_SYS_RST`).
     * A instrução foi completamente removida dos códigos em C++, estabilizando o boot e o rádio Wi-Fi.
  2. **Validação de Conectividade Wi-Fi e Sinal (Rede `PET_ELETRICA`):**
     * Criado o sketch de teste isolado [`testes/teste_wifi_esp32/teste_wifi_esp32.ino`](file:///c:/Users/caihe/Documents/develop/rover/testes/teste_wifi_esp32/teste_wifi_esp32.ino).
     * O ESP32-S3 conectou com sucesso em apenas ~2.5s, obtendo IP `192.168.7.26` com excelente nível de sinal RSSI (**`-24 dBm` a `-31 dBm`**).
  3. **Solução do Erro de Compilação na Arduino IDE (`multiple definition of camera_httpd / startCameraServer`):**
     * Esclarecido que o nosso código [`testes/teste_camera_web_server/teste_camera_web_server.ino`](file:///c:/Users/caihe/Documents/develop/rover/testes/teste_camera_web_server/teste_camera_web_server.ino) é **All-in-One (Arquivo Único)**. O erro ocorria ao colar o código dentro do exemplo nativo de 4 abas da Arduino IDE mantendo o `app_httpd.cpp` ativo ao lado.
  4. **Evolução de Arquitetura: Transição do Modelo LAN para Sistemas Distribuídos na Nuvem (Fly.io):**
     * **Motivação:** No modelo LAN tradicional (ESP32 como Servidor HTTP passivo), o robô fica inacessível fora da rede local por conta de NAT, CGNAT e firewalls.
     * **Novo Modelo Produtor-Consumidor (Push via WebSocket):**
       * O ESP32-S3 atua como **Cliente Ativo**, abrindo uma conexão permanente via WebSocket Seguro (**`wss://` na porta 443**) para um servidor de relay distribuído na nuvem (**Fly.io** na região `gru` - São Paulo).
       * **Payload Binário Ultra-Leve:** Envio de pacotes binários diretos (Frame ID 4B + Timestamp millis 4B + Bytes brutos JPEG = apenas 8 bytes de overhead por frame).
       * **Medição Precisa de Latência Fim-a-Fim:** Implementação do protocolo *Two-Leg RTT (Round Trip Time)* para calcular em tempo real no HUD a latência do robô (`RTT_esp / 2`), do piloto (`RTT_piloto / 2`) e o FPS real de entrega.

### 🗓️ Sessão 10: Implementação do Servidor Relay no Fly.io (gru) e Firmware Cliente ESP32-S3
* **Ações de Engenharia Executadas:**
  1. **Servidor Relay WebSocket de Baixa Latência ([`servidor-relay/`](file:///c:/Users/caihe/Documents/develop/rover/servidor-relay)):**
     * Criado servidor em Node.js com apenas uma dependência (`ws`), com suporte nativo a retransmissão binária sem processamento inútil de pixels.
     * Implementação do protocolo *Two-Leg RTT*: cálculo de $\Delta t_{esp}$ (via ACK binário de 9 bytes) e $\Delta t_{piloto}$ (via ping-pong periódico no WebSocket).
     * Endpoint de healthcheck em `/health` e `/status` reportando estado do robô, pilotos conectados e uptime.
  2. **Interface Web do Cockpit FPV ([`servidor-relay/public/index.html`](file:///c:/Users/caihe/Documents/develop/rover/servidor-relay/public/index.html)):**
     * Interface moderna com tema escuro aeroespacial / HUD cyberpunk.
     * Retículo central de mira FPV, indicadores de FPS dinâmico, Bitrate e Resolução.
     * Painel de telemetria com breakdown da latência Robô $\to$ Nuvem, Nuvem $\to$ Piloto e Total Fim-a-Fim.
     * Suporte a pilotagem por teclado (WASD, Setas de Pan/Tilt do gimbal e Espaço para parada de emergência).
  3. **Infraestrutura em Nuvem (Fly.io):**
     * Configurado `Dockerfile` (Node 20 Alpine) e `fly.toml` apontando para o datacenter de São Paulo (`gru`).
     * Provisionado o app `rover-relay-fpv-sp` em `https://rover-relay-fpv-sp.fly.dev` com certificados SSL/TLS automáticos na porta 443.
  4. **Firmware Cliente ESP32-S3 ([`testes/teste_camera_websocket_client`](file:///c:/Users/caihe/Documents/develop/rover/testes/teste_camera_websocket_client)):**
     * Desenvolvido sketch [`teste_camera_websocket_client.ino`](file:///c:/Users/caihe/Documents/develop/rover/testes/teste_camera_websocket_client/teste_camera_websocket_client.ino) com conexão Wi-Fi na rede `PET_ELETRICA`, conexão segura `wss://rover-relay-fpv-sp.fly.dev/ws/robot`, push contínuo de frames JPEG alocados na Octal PSRAM e recepção de comandos de teleoperação.

---

## 📝 5. Próximos Passos Imediatos
- [x] Mapear os links e códigos exatos dos produtos na RoboCore para fechar o carrinho de compras.
- [x] Consolidar as compras em planilha XLSX única com 2 abas (`LISTA_DE_COMPRAS_ROVER.xlsx` / `COMPONENTES_DRONE_TERRESTRE.xlsx`).
- [x] Validar estabilidade de Wi-Fi e solução de Brownout no ESP32-S3 CAM.
- [x] Criar o projeto do servidor de relay em Node.js com Dockerfile e `fly.toml` configurado para a região `gru` (São Paulo).
- [x] Fazer o deploy do servidor no Fly.io (`fly deploy` - app `rover-relay-fpv-sp`).
- [x] Implementar o sketch cliente no ESP32-S3 (`teste_camera_websocket_client.ino`) conectando em `wss://`.
- [ ] Gravar o sketch no ESP32-S3 e validar transmissão de vídeo ao vivo no painel web (inclusive em rede externa / 4G).
- [ ] Integrar o controle PWM dos servos Pan/Tilt ao receber os comandos do piloto.




