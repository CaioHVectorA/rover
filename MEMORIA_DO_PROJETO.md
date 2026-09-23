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

## 📝 5. Próximos Passos Imediatos
- [ ] Mapear os links e códigos exatos dos produtos na RoboCore para fechar o carrinho de compras.
- [ ] Elaborar o esquema unifilar/diagrama de ligação dos pinos do ESP32-S3 CAM.
- [ ] Definir se o chassi será comercial de acrílico/alumínio ou modelado para impressão 3D.
