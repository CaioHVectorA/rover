# 🤖 Instruções para Agentes de IA (AGENTS.md)

Este documento contém as **diretrizes obrigatórias de comportamento, regras de engenharia e contexto permanente** para qualquer agente de IA trabalhando no repositório do **Rover Móvel ESP32-S3 4WD**.

---

## 🚫 1. Regra de Git (Apenas com Autorização Explícita do Usuário)

* **Proibido usar Git de forma automática:** **NUNCA** execute comandos como `git commit`, `git push`, `git add` ou crie branches automaticamente durante as trocas de mensagens normais de brainstorm e desenvolvimento.
* **Motivo:** O usuário solicitou explicitamente controle manual do fluxo:
  > *"Para de ficar subindo no git a cada coisa, nao faça nada no git."*
* **Quando usar Git:** Execute `git add`, `git commit` e `git push` **exclusivamente quando o usuário solicitar de forma explícita** (ex: *"coloque tudo no git"*, *"sessão terminada por agora"*, etc.). Em todos os outros momentos, mantenha as alterações estritamente locais.

---

## 📖 2. Memória Contínua & Documentação (`docs/context.md` e `README.md`)

* **Memória Técnica Contínua:** O arquivo [`docs/context.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/context.md) é a memória técnica detalhada de longo prazo. A cada decisão técnica ou avanço prático relevante, atualize este documento organicamente.
* **Visão Geral Executiva:** O arquivo [`README.md`](file:///c:/Users/caihe/Documents/develop/rover/README.md) é a porta de entrada pública do repositório (status, quickstart, arquitetura limpa e links).
* **Fidelidade Real ao Status do Projeto:**
  * **STATUS ATUAL:** **Todos os componentes físicos já chegaram e estão em mãos na bancada de testes.**
  * O projeto está na fase de **testes ativos de bancada (firmware, comunicação serial e app mobile)** e validação para modelagem CAD 3D do chassi.
  * Não invente circuitos ou testes que não foram de fato validados.

---

## ⚙️ 3. Hardware Adquirido & Diretrizes Físicas Fixas

Nunca volte atrás ou altere os seguintes componentes já adquiridos e validados:

1. **Motores de Tração:**
   * **Modelo:** DC **JGA16-050 / JGA-050** com Caixa de Redução Metálica (16 mm de diâmetro, eixo D de 3 mm em aço).
   * **Atenção:** **NÃO são micromotores N20**. O projeto migrou definitivamente para a série JGA-050 cilíndrica.
2. **Rodas:**
   * **Modelo:** **StickyMAX S20 Macia (RoboCore)**, diâmetro externo de **22 mm** (raio = 11 mm).
   * **Cubo de Fixação:** O kit já vem de fábrica com o **cubo usinado em alumínio CNC 6351-T6** e parafuso de fixação M3. O usuário **não** precisa de cubo separado.
3. **Cálculo de Vão Livre (Ground Clearance) = 3,0 mm:**
   * $\text{Raio da Roda (11 mm)} - \text{Raio do Motor JGA (8 mm)} = \mathbf{3{,}0\text{ mm}}$.
   * **Regra de Modelagem 3D:** O chassi não pode ter assoalho plástico passando por baixo do motor. O motor deve ser abraçado por cima e pelas laterais, mantendo a folga de 3 mm livre para o piso.
4. **Montagem da Roda Invertida:**
   * Orientação do orientador: cubo e roda virados para fora do chassi; motor 100% interno.
5. **Placas de Controle & Comunicação Serial:**
   * **Cabeça Pan/Tilt (Móvel):** Placa ESP32-S3-CAM (câmera + Wi-Fi + WebSocket Server).
   * **Chassi (Fixo):** Arduino Nano V3 (5V nativo, comanda TB6612FNG, 2 servos SG90, LEDs WS2812B, Buzzer e lê bateria).
   * **Comunicação:** Chicote flexível de **3 a 4 fios** (`5V`, `GND`, `ESP IO43 TX -> Nano D2 RX via BC337 ou D0 direto`, `Nano D1 TX -> Divisor -> ESP IO44 RX`).
6. **Alimentação:**
   * Bateria Li-Ion 2S 7.4V 2500mAh com BMS.
   * Regulador Step-Down Mini 560 (5V / até 5A).
   * Driver duplo MOSFET TB6612FNG.

---

## 📂 4. Organização Oficial de Arquivos e Pastas

Mantenha a modularidade rigorosa da codebase e a raiz (`/`) estritamente limpa (sem pastas soltas de testes ou compras):

* [`docs/`](file:///c:/Users/caihe/Documents/develop/rover/docs/):
  * [`context.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/context.md): Registro contínuo de decisões e contexto geral.
  * [`pocs/`](file:///c:/Users/caihe/Documents/develop/rover/docs/pocs/): Documentação e guias de execução da suíte de 6 POCs incrementais ([`README.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/pocs/README.md), [`GUIA_EXECUCAO_POCS.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/pocs/GUIA_EXECUCAO_POCS.md)).
  * [`hardware/`](file:///c:/Users/caihe/Documents/develop/rover/docs/hardware/): Desenhos técnicos oficiais milimétricos (`ESPECIFICACOES_TECNICAS.md`), planilha oficial [`tabela_pinagem_esp32_nano.xlsx`](file:///c:/Users/caihe/Documents/develop/rover/docs/hardware/tabela_pinagem_esp32_nano.xlsx) e projetos KiCad em `kicad/`.
  * [`guides/`](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/): Guias aprofundados de engenharia:
    * [`camera_calor_software.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/camera_calor_software.md): Otimização térmica do OV5640 (soneca em 0x3008, XCLK adaptativo, FreeRTOS Core 0).
    * [`ajuste_fino_servos_rebolado.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/ajuste_fino_servos_rebolado.md): Eliminação do rebolado nos servos SG90 (microssegundos a 50Hz, rampa e antifolga).
    * [`tracao_motores_anti_reset.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/tracao_motores_anti_reset.md): Prevenção de Brown-Out e rampa de PWM 4WD na TB6612FNG.
    * [`controle_servos_head_tracking_vr.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/controle_servos_head_tracking_vr.md): Guia de head-tracking VR para o app mobile.
    * [`http_vs_websocket_redes.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/http_vs_websocket_redes.md): Arquitetura de rede.
    * [`streaming_video_baixa_latencia.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/streaming_video_baixa_latencia.md): Pipeline de vídeo.
  * [`compras/`](file:///c:/Users/caihe/Documents/develop/rover/docs/compras/): Histórico consolidado de compras, planilhas orçamentárias e fotos das lojas.
  * [`references/`](file:///c:/Users/caihe/Documents/develop/rover/docs/references/): Fotos reais dos produtos e referências maker ([`INSPIRACOES_CASE_E_PAN_TILT.md`](file:///c:/Users/caihe/Documents/develop/rover/docs/references/INSPIRACOES_CASE_E_PAN_TILT.md)). Proibido renders ou imagens falsas de IA.
* [`src/`](file:///c:/Users/caihe/Documents/develop/rover/src/):
  * [`firmware/`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/):
    * `comum/`: Módulos de hardware unificados e reutilizáveis (`esp_camera_frio.h`, `esp_painel.h`, `esp_enlace.h`, `nano_servos.h`, `nano_motores.h`, `nano_diag.h`, `rover_protocolo.h`).
    * `pocs/`: Suíte dos 6 POCs incrementais (`poc1` a `poc6`), cada um com pasta própria para ESP32 e/ou Nano.
    * `gateway_app/`: Firmware completo de produção integrado ao aplicativo mobile Expo.
    * `legado/`: Sketches e testes históricos arquivados.
  * [`app_mobile/`](file:///c:/Users/caihe/Documents/develop/rover/src/app_mobile/): Aplicativo React Native / Expo (VR Head-Tracking, FPV, Dashboard).
  * [`servidor_relay/`](file:///c:/Users/caihe/Documents/develop/rover/src/servidor_relay/): Servidor Node.js / Docker para relay de teleoperação em nuvem.
* [`tools/`](file:///c:/Users/caihe/Documents/develop/rover/tools/):
  * Scripts auxiliares em Python e geradores de diagramas KiCad/Docx.

---

## ⚡ 5. Ambientes de Compilação PlatformIO (`platformio.ini`)

Ao compilar ou gravar qualquer firmware, sempre use o ambiente específico com `pio run -e <env>`:
* POC 1: `poc1_esp32` | `poc1_nano`
* POC 2: `poc2_esp32` | `poc2_nano` (ou `poc2_nano_hw`)
* POC 3: `poc3_esp32`
* POC 4: `poc4_esp32` | `poc2_nano`
* POC 5: `poc5_nano` (baud rate 115200)
* POC 6: `poc6_esp32` | `poc6_nano` (ou `poc6_nano_hw`)
* Produção App: `gateway_esp32` | `gateway_nano`

---

## 💬 6. Estilo de Comunicação & Tom

* Seja direto, prático e conciso.
* Sempre utilize links clicáveis no padrão markdown (`[Nome do Arquivo](file:///caminho/completo)`).
* Responda em Português (Brasil).
* **Guia de Estilo Vivo ([`style.md`](file:///c:/Users/caihe/Documents/develop/rover/style.md)):** O agente deve enriquecer continuamente o arquivo `style.md`, registrando o perfil de comunicação, ritmo das respostas e preferências do usuário, afinando o tom organicamente a cada conversa.
