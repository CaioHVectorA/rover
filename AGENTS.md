# 🤖 Instruções para Agentes de IA (AGENTS.md)

Este documento contém as **diretrizes obrigatórias de comportamento, regras de engenharia e contexto permanente** para qualquer agente de IA trabalhando no repositório do **Rover Móvel ESP32 4WD**.

---

## 🚫 1. Regra de Git (Apenas com Autorização Explícita do Usuário)

* **Proibido usar Git de forma automática:** **NUNCA** execute comandos como `git commit`, `git push`, `git add` ou crie branches automaticamente durante as trocas de mensagens normais de brainstorm e desenvolvimento.
* **Motivo:** O usuário solicitou explicitamente controle manual do fluxo:
  > *"Para de ficar subindo no git a cada coisa, nao faça nada no git."*
* **Quando usar Git:** Execute `git add`, `git commit` e `git push` **exclusivamente quando o usuário solicitar de forma explícita** (ex: *"coloque tudo no git"*, *"sessão terminada por agora"*, etc.). Em todos os outros momentos, mantenha as alterações estritamente locais.

---

## 📖 2. Memória Central do Projeto (`README.md`)

* O arquivo [`README.md`](file:///home/usuario/Documentos/rover/README.md) é a **única fonte da verdade** e a memória contínua de longo prazo do projeto.
* **Atualização Obrigatória:** A cada troca de mensagens relevante ou decisão técnica tomada, incremente o `README.md` de forma orgânica.
* **Fidelidade Real:** Não invente circuitos prontos, códigos ou montagens que ainda não foram feitas ou testadas. O projeto está na fase de planejamento e aguardando a chegada dos componentes.

---

## ⚙️ 3. Hardware Adquirido & Diretrizes Físicas Fixas

Nunca volte atrás ou altere os seguintes componentes já adquiridos e validados:

1. **Motores de Tração:**
   * **Modelo:** DC **JGA16-050 / JGA-050** com Caixa de Redução Metálica (16 mm de diâmetro, eixo D de 3 mm em aço).
   * **Atenção:** **NÃO são micromotores N20**. O projeto foi migrado definitivamente para a série JGA-050 cilíndrica.
2. **Rodas:**
   * **Modelo:** **StickyMAX S20 Macia (RoboCore)**, diâmetro externo de **22 mm** (raio = 11 mm).
   * **Cubo de Fixação:** O kit já vem de fábrica com o **cubo usinado em alumínio CNC 6351-T6** e parafuso de fixação M3. O usuário **não** precisa comprar cubo separado.
3. **Cálculo de Vão Livre (Ground Clearance) = 3,0 mm:**
   * $\text{Raio da Roda (11 mm)} - \text{Raio do Motor JGA (8 mm)} = \mathbf{3,0\text{ mm}}$.
   * **Regra de Modelagem 3D:** O chassi não pode ter assoalho plástico passando por baixo do motor. O motor deve ser abraçado por cima e pelas laterais, mantendo a folga de 3 mm livre para o piso.
4. **Montagem da Roda Invertida:**
   * Orientação do orientador: cubo e roda virados para fora do chassi; motor 100% interno.
5. **Placas de Controle & Comunicação Serial:**
   * **Cabeça Pan/Tilt (Móvel):** Placa ESP32 (câmera + Wi-Fi).
   * **Chassi (Fixo):** Arduino Nano V3 (5V nativo, comanda TB6612FNG, 2 servos SG90, LEDs WS2812B, Buzzer e lê bateria).
   * **Comunicação:** Chicote flexível de **4 fios** (`5V`, `GND`, `ESP TX -> Nano RX`, `Nano TX -> Divisor -> ESP RX`).
6. **Alimentação:**
   * Bateria Li-Ion 2S 7.4V 2500mAh com BMS.
   * Regulador Step-Down Mini 560 (5V / até 5A).
   * Driver duplo MOSFET TB6612FNG.

---

## 📂 4. Organização de Arquivos e Pastas

Mantenha a separação estrita entre documentos técnicos e referências conceituais:

* [`imagens_importantes/`](file:///home/usuario/Documentos/rover/imagens_importantes/ESPECIFICACOES_TECNICAS.md):
  * Apenas desenhos técnicos oficiais com cotas milimétricas, plantas e diagramas elétricos para modelagem CAD 3D e elétrica.
  * Arquivo índice: `ESPECIFICACOES_TECNICAS.md`.
* [`inspiracoes/`](file:///home/usuario/Documentos/rover/inspiracoes/INSPIRACOES_CASE_E_PAN_TILT.md):
  * Apenas fotos reais de componentes e montagens de referência da comunidade maker.
  * **Proibido:** Renders ou imagens falsas de IA que distorcem a realidade.
* [`tabela_pinagem_esp32_nano.xlsx`](file:///home/usuario/Documentos/rover/tabela_pinagem_esp32_nano.xlsx):
  * Planilha limpa, editável pelo usuário, com representação visual/física intuitiva dos pinos do ESP32 e do Nano (estilo bancada).

---

## 💬 5. Estilo de Comunicação & Tom

* Seja direto, prático e conciso.
* Sempre utilize links clicáveis no padrão markdown (`[Nome do Arquivo](file:///caminho/completo)`).
* Responda em Português (Brasil).
