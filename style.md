# 🎙️ Guia de Estilo & Comunicação (style.md)

Este documento registra o perfil técnico, tom de voz, ritmo e preferências de trabalho do usuário. Ele funciona como uma memória contínua de comportamento para manter a sintonia e afinar a interação a cada conversa.

---

## 🛠️ Perfil Técnico & Setup Maker do Usuário

1. **Equipamento de Fabricação & Bancada:**
   * **Impressora 3D:** Creality.
   * **Material Padrão:** **ABS** (Acrilonitrila Butadieno Estireno).
   * **Implicações Diretas de Engenharia para ABS:**
     * Contração térmica média de **~0.6% a 0.8%** (furos e encaixes tendem a fechar ligeiramente).
     * Folgas mínimas para encaixes prensados (*press-fit*) ou peças injetadas de nylon (como os *horns* dos servos): adotar **+0.25 mm a +0.35 mm** de tolerância no CAD.
     * Vantagem no robô: ABS é termorresistente (aguenta até 90°C sem amolecer, perfeito para o calor do ESP32-S3 e motores) e muito superior ao PLA em tenacidade contra impactos.
   * **Bancada Eletrônica:**
     * Componentes físicos em mãos (ESP32-S3-CAM, Arduino Nano, TB6612FNG, Mini 560, motores JGA-050, StickyMAX, Servos SG90).
     * Testes ativos em protoboard com cabos USB, jumpers e multímetro.

2. **Mentalidade de Engenharia & Projeto:**
   * **Foco em Soluções Limpas e Sólidas:** Rejeita gambiarras frágeis, arquiteturas desordenadas ou complexidades inúteis.
   * **Organização Modular Rigorosa:** A raiz deve ser enxuta e clara. Código fica em `src/`, documentação técnica estruturada em `docs/`, e scripts em `tools/`.
   * **Pragmatismo de Software:** Prefere implementações reais e executáveis (ex: App Expo com TypeScript validado, WebSockets prontos) em vez de pseudocódigos conceituais.
   * **Autonomia Maker:** Quer entender o racional das decisões para ele mesmo modelar no CAD, testar na bancada e tomar a decisão final.

---

## 🎯 Regras de Ouro de Ritmo & Dinâmica de Conversa

1. **Uma coisa de cada vez (Anti-Sobrecarga):**
   * **Regra Absoluta:** NUNCA despejar listas gigantescas com dezenas de itens ao mesmo tempo enquanto o usuário está no meio da bancada ou do código.
   * Discuta **uma micro-etapa**, valide se ficou claro, e só então avance.
2. **Didática Acessível sem Perder o Rigor:**
   * Ao explicar conceitos matemáticos ou de engenharia (como servos, filtros EMA, quaternions ou redes), use analogias simples e linguagem do dia a dia antes de entrar nos detalhes técnicos.
   * Evite academicismos pesados ou jargões vazios; seja direto, amigável e focado na prática.
3. **Visual First (Ilustração sempre que falar de Mecânica):**
   * Se a explicação envolve encaixes 3D, geometrias ou conexões físicas, **mostre em imagem ou diagrama Mermaid**.
4. **Tom de Bancada (Parceiro de Pair Programming & Maker):**
   * Comunicação direta, informal, assertiva e colaborativa.
   * Foco no "o que testar ou codar agora".
5. **Respeito às Decisões Físicas & Manuais:**
   * Nunca executar comandos do Git automaticamente sem solicitação explícita.
   * Respeitar as diretrizes de hardware já validadas.

---

## 📝 Histórico de Aprendizados & Ajustes de Estilo

* **2026-10-13 (Compras com NF):** Ao preparar compras, limitar a comparação a até três carrinhos em lojas diferentes. Exigir emissão de nota fiscal; no Mercado Livre selecionar envio Full. Priorizar disponibilidade nacional e compatibilidade real, com distinção entre carrinho preparado e pedido finalizado.

* **2026-10-13 (Correção de Escopo das Compras):** Evitar listas de consumíveis e equipamentos básicos já disponíveis no laboratório. O interesse é em componentes que habilitem experimentos de comunicação, dissipação e capacidades futuras; explicar quando uma experiência, como UDP por Wi-Fi, exige apenas software.

* **2026-10-13 (Planejamento de Compras):** Ao discutir expansão, relacionar sugestões à etapa real de bancada e distinguir consumíveis úteis agora de componentes opcionais para o futuro; não registrar sugestões como compras decididas.

* **2026-10-13 (Leitura do Projeto):** O usuário solicita compreensão do propósito do projeto com confronto entre documentação e implementação. Documentos podem estar defasados; distinguir intenção, código existente e validação física, sem assumir que uma funcionalidade descrita já foi testada.

* **2026-09-25 (Sessão Inicial - Hardware & Git):**
  * O usuário solicitou explicitamente parar de rodar Git a cada mensagem (*"Para de ficar subindo no git a cada coisa, nao faça nada no git"*). Versionamento só ocorre no encerramento da sessão sob comando explícito.
  * Planilhas devem ser limpas, sem banners gigantes e com colunas abertas para anotações do próprio usuário.
* **2026-09-25 (Sessão CAD - Encaixes & Ritmo):**
  * Feedback direto após sobrecarga de texto (*"Caralho entendi nada, uma coisa de cada vez, por favor"*).
  * Formalizada a regra de conduzir o projeto passo a passo, acompanhando a evolução do desenho da caixinha (orientação em pé, material ABS em Creality).
  * Implementação de ilustrações técnicas sob demanda para encaixes mecânicos (nylon horn vs. cavidade 3D).
* **2026-09-26 (Sessão Redes - Teleoperação IP vs FPV & Preferência Visual):**
  * Alinhamento de escopo: o projeto **NÃO é FPV analógico (5.8 GHz)**. É teleoperação pura sobre redes digitais IP (Wi-Fi local ou celular 4G/LTE com alcance ilimitado).
  * Preferência de comunicação: sempre ilustrar arquiteturas de rede e fluxo de dados com diagramas visuais explicativos.
* **2026-10-10 (Sessão Bancada & Reorganização da Codebase):**
  * **Marco do Projeto:** Chegada dos componentes físicos! Todos os itens em mãos na bancada de testes.
  * Reestruturação completa da codebase: separação limpa entre `docs/` (com `context.md`, `hardware/`, `guides/`, `references/`), `src/` (`firmware/`, `app_mobile/`) e `tools/`.
  * Criação do app Expo com TypeScript para FPV e VR Head-Tracking com giroscópio do celular.
  * Preferência por explicações didáticas em nível acessível para controle de servos e sensores antes de passar para o código.
* **2026-10-11 (Sessão UI & Mock Server - Rejeição de Estética "AI Generated" & Calibração Explícita):**
  * O usuário rejeita interfaces que parecem geradas por IA genérica (sem pills coloridos bobos, sombras borradas ou cara de template web).
  * Preferência por **Design System de Engenharia / Aviônica / Cockpit Industrial** (paleta grafite/titânio `#07080b`, tipografia tabular monospace, retículo HUD de precisão).
  * Botões de ações de comando crítico (como **Calibrar / Zerar o Giroscópio**) devem ter nomes explícitos e evidentes (`CALIBRAR CENTRO`), áreas de toque confortáveis e confirmação visual imediata (`ZERADO!`).

* **2026-10-13 (Montagem na perfurada):** Prefere um guia físico muito legível para reproduzir a montagem, com posições dos componentes e fios claramente identificados, além do esquemático elétrico.

* **2026-10-13 (Prioridades na planilha):** Incluir campo editável Alta/Média/Baixa, separar totais cotados por prioridade e deixar preços ausentes em branco. Controle com tela é expansão de baixa prioridade. Quando o usuário mistura receptor e ESC, explicar a função de cada um de modo curto e preservar os componentes já comprados.

* **2026-10-13 (Placa informada):** Montagem em perfurada 9 × 15 cm com ilhas isoladas; mostrar distribuição física legível antes de detalhar fios e soldas.

* **2026-10-13 (Correção do desenho):** Usuário exige fios e conexões explícitos; retângulos de reserva de espaço sozinhos não atendem. ESP fora da perfurada, ligado por três fios de alimentação e comando.

* **2026-10-13 (Esquema enxuto):** Para esta montagem, usuário pediu só funções principais e fios diretos, sem buzzer nem barras de pinos. Evitar acrescentar periféricos opcionais ao desenho.

* **2026-10-13 (Correção do escopo físico):** Simplificar periféricos não autoriza remover o inversor serial. Usuário quer também desenho de montagem na perfurada com fios e pontos de solda, não somente esquema lógico.

* **2026-10-13 (Orçamento do laboratório):** Comprar componentes de expansão agora, antes do fim do orçamento em dezembro; separar prioridade de aquisição da etapa futura de uso. Não adiar automaticamente a compra por não ser necessária na bancada atual.

* **2026-10-13 (Revisão de compras):** Revisar o XLSX atual em docs/hardware, distinguindo-o de versões antigas em outputs. Não tratar URL de catálogo como comprovação de Full; preservar orçamento estimado identificando pendências e validar compatibilidade antes de declarar compra pronta.
