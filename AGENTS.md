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
  * **STATUS ATUAL (V1 Montado):** O robô V1 já está montado fisicamente (chassi 3D protótipo, rodas de 32 mm, placa perfurada com ESP32-S3 + Nano) e validado com testes práticos de tração e visão computacional por gestos.
  * **PRÓXIMO PASSO (V2 PCB & Robô Inteligente):** Avançar diretamente para a **PCB definitiva (`rover_pcb_v2_chassi`)** (sem novas placas perfuradas), migrando o controle do chassi do Nano para um **ESP32 interno (DevKit 30 pinos)** comunicando via **ESP-NOW**, com áudio I2S (microfone INMP441 + amplificador MAX98357A), OLED externo e transmissão de vídeo de baixa latência (UDP) para servidor de IA.
  * Não invente circuitos ou testes que não foram de fato validados.

---

## ⚙️ 3. Hardware Adquirido & Diretrizes Físicas Fixas

Nunca volte atrás ou altere os seguintes componentes já adquiridos e validados:

1. **Motores de Tração:**
   * **Modelo:** DC **JGA16-050 / JGA-050** com Caixa de Redução Metálica (16 mm de diâmetro, eixo D de 3 mm em aço).
   * **Atenção:** **NÃO são micromotores N20**. O projeto migrou definitivamente para a série JGA-050 cilíndrica.
2. **Rodas:**
   * **Montagem Atual no Robô:** Rodas de **32 mm de diâmetro externo** (raio = 16 mm).
   * **Cálculo de Vão Livre Real (Ground Clearance) = 8,0 mm:**
     * $\text{Raio da Roda (16 mm)} - \text{Raio do Motor JGA (8 mm)} = \mathbf{8{,}0\text{ mm}}$.
     * A elevação para 32 mm resolveu o vão livre crítico de 3 mm das rodas de 22 mm anteriores, permitindo rodar em pisos reais sem raspar o motor.
3. **Chassi:**
   * **Versão Atual:** Chassi impresso em 3D de validação (protótipo funcional, não definitivo).
   * Será redesenhado conforme as dimensões finais e furações da PCB V2 (85 × 65 mm, furos M3 a 77 × 57 mm).
4. **Montagem da Roda Invertida:**
   * Orientação do orientador: cubo e roda virados para fora do chassi; motor 100% interno.
5. **Placas de Controle & Comunicação (Transição V1 $\rightarrow$ V2):**
   * **Cabeça Pan/Tilt (Móvel):** Placa ESP32-S3-CAM (OV5640, dedicada ao vídeo de baixa latência).
   * **Chassi V1 (Protótipo Atual em Placa Perfurada):** Arduino Nano V3 (comanda TB6612FNG, servos SG90 e LEDs via serial D0/BC337).
   * **Chassi V2 (Próximo Passo — PCB Definitiva `rover_pcb_v2_chassi`):** **ESP32 DevKit interno (30 pinos)** substituindo o Nano, comunicando com a cabeça via **UART Serial Direta 3.3V** (`IO_TX <-> IO_RX`, sem transistores ou divisores, livre de conflitos de rádio Wi-Fi), além de gerenciar TB6612FNG, servos SG90, microfone I2S (INMP441), amplificador I2S (MAX98357A), display OLED I2C, sensor DS18B20 e LEDs WS2812B.
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
