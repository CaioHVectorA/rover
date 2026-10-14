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

* **Memória Técnica Contínua:** O arquivo [`docs/context.md`](file:///home/usuario/Documentos/rover/docs/context.md) é a memória técnica detalhada de longo prazo. A cada decisão técnica ou avanço prático relevante, atualize este documento organicamente.
* **Visão Geral Executiva:** O arquivo [`README.md`](file:///home/usuario/Documentos/rover/README.md) é a porta de entrada pública do repositório (status, quickstart, arquitetura limpa e links).
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
   * **Comunicação:** Chicote flexível de **4 fios** (`5V`, `GND`, `ESP IO43 TX -> Nano D0 RX`, `Nano D1 TX -> Divisor -> ESP IO44 RX`).
6. **Alimentação:**
   * Bateria Li-Ion 2S 7.4V 2500mAh com BMS.
   * Regulador Step-Down Mini 560 (5V / até 5A).
   * Driver duplo MOSFET TB6612FNG.

---

## 📂 4. Organização Oficial de Arquivos e Pastas

Mantenha a modularidade rigorosa da codebase:

* [`docs/`](file:///home/usuario/Documentos/rover/docs/):
  * [`context.md`](file:///home/usuario/Documentos/rover/docs/context.md): Registro contínuo de decisões e contexto geral.
  * [`hardware/`](file:///home/usuario/Documentos/rover/docs/hardware/): Desenhos técnicos oficiais milimétricos (`ESPECIFICACOES_TECNICAS.md`) e planilha oficial [`tabela_pinagem_esp32_nano.xlsx`](file:///home/usuario/Documentos/rover/docs/hardware/tabela_pinagem_esp32_nano.xlsx).
  * [`guides/`](file:///home/usuario/Documentos/rover/docs/guides/): Guias aprofundados de servos/VR, protocolos de rede e streaming de vídeo.
  * [`references/`](file:///home/usuario/Documentos/rover/docs/references/): Fotos reais dos produtos e referências maker ([`INSPIRACOES_CASE_E_PAN_TILT.md`](file:///home/usuario/Documentos/rover/docs/references/INSPIRACOES_CASE_E_PAN_TILT.md)). Proibido renders ou imagens falsas de IA.
* [`src/`](file:///home/usuario/Documentos/rover/src/):
  * [`firmware/`](file:///home/usuario/Documentos/rover/src/firmware/): Códigos C++/Arduino do ESP32 e Arduino Nano.
  * [`app_mobile/`](file:///home/usuario/Documentos/rover/src/app_mobile/): Aplicativo React Native / Expo (VR Head-Tracking, FPV, Dashboard).
* [`tools/`](file:///home/usuario/Documentos/rover/tools/):
  * Scripts auxiliares em Python e geradores de diagramas.

---

## 💬 5. Estilo de Comunicação & Tom

* Seja direto, prático e conciso.
* Sempre utilize links clicáveis no padrão markdown (`[Nome do Arquivo](file:///caminho/completo)`).
* Responda em Português (Brasil).
* **Guia de Estilo Vivo ([`style.md`](file:///home/usuario/Documentos/rover/style.md)):** O agente deve enriquecer continuamente o arquivo `style.md`, registrando o perfil de comunicação, ritmo das respostas e preferências do usuário, afinando o tom organicamente a cada conversa.
