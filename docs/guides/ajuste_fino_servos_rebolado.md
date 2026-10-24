# 🎯 Eliminação do Efeito "Rebolado" nos Servos SG90 (Pan/Tilt)

Este guia analisa a mecânica do micro servo **SG90 9g** no mecanismo Pan/Tilt do robô, explicando por que movimentos lentos tendem a oscilar lateralmente ("rebolar") e como a arquitetura de controle do [`nano_servos.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/nano_servos.h) elimina essa instabilidade via software.

---

## 🔬 A Física do Problema: Por que o encaixe "rebola" em baixa velocidade?

O movimento de oscilação lateral (*stick-slip*) surge da combinação de **limitações mecânicas do servo** com **discretização grosseira no software**:

```mermaid
flowchart LR
    A["Comando Lento em Graus Inteiros (1° em 1°)"] --> B["Degrau PWM Grosseiro (~10.3 µs)"]
    B --> C["Atrito Estático na Bucha Plástica"]
    C --> D["Motorzinho não vence atrito imediato"]
    D --> E["Erro de posição acumula"]
    E --> F["Dente pula bruscamente (Slip)"]
    F --> G["Peso da Câmera oscila como Pêndulo ('Rebola')"]
```

### 1. Ausência de Rolamento de Esferas no Eixo do SG90
* Servos econômicos da classe SG90 não utilizam rolamentos de esferas (*ball bearings*). O pino do horn é sustentado apenas por uma **bucha plástica seca** moldada na carcaça.
* No eixo de Pan (giro horizontal), o servo precisa sustentar todo o peso em balanço (*cantilever*) do suporte articulado, do segundo servo (Tilt), da placa ESP32 e da câmera.
* Quando o peso oscila lateralmente, a folga radial da bucha atua como pivô, amplificando qualquer tranco do motor em um balanço pendular visível.

### 2. O Fenômeno de Stick-Slip (Atrito Estático vs. Dinâmico)
* O atrito estático ($\mu_e$) entre as engrenagens plásticas é consideravelmente maior que o atrito cinético ($\mu_c$).
* Se o firmware envia passos muito lentos ou com pouca energia, o motor DC interno não recebe tensão suficiente para girar suavemente: a engrenagem fica "travada" (*stick*), o potenciômetro interno acumula erro até que a ponte H interna do servo injeta torque suficiente para vencer o atrito, provocando um salto brusco (*slip*). O servo ultrapassa o ponto alvo (*overshoot*), inverte a força e entra em ciclo de ressonância.

### 3. A Falha dos Graus Inteiros e da Banda Morta de 2°
* No firmware clássico com `servo.write(graus)`, existem apenas **180 degraus discretos** para toda a rotação. Cada grau representa um pulso de aproximadamente $10{,}3\ \mu\text{s}$.
* Se o código anterior aplicava um filtro como `if (abs(novo - atual) >= 2)`, o servo era forçado a saltar em degraus de **pelo menos $20{,}6\ \mu\text{s}$**. Em baixa velocidade, o robô recebia uma sucessão de micropancadas que excitavam a frequência natural do chassi.

---

## 🛠️ A Solução de Software no [`nano_servos.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/nano_servos.h)

Para transformar o movimento em uma transição suave e estável, o módulo implementa:

### 1. Resolução em Microssegundos (10x Mais Fina)
* Em vez de graus inteiros, o controlador opera internamente com números de ponto flutuante mapeados diretamente em microssegundos:
  $$\text{PWM} = 544\ \mu\text{s}\quad (0^\circ) \quad \text{até} \quad 2400\ \mu\text{s}\quad (180^\circ)$$
  Isso oferece uma resolução de **$1.856$ passos discretos** ao longo do curso (cerca de **$0{,}097^\circ$ por passo**), eliminando a "escadinha" perceptível.

### 2. Sincronismo com o Ciclo Físico do Servo (50 Hz / 20 ms)
* O pulso PPM dos servos analógicos SG90 possui frequência padrão de **50 Hz** (um ciclo a cada $20\text{ ms}$).
* O loop de atualização executa rigorosamente a cada $20\text{ ms}$ (`SERVO_TICK_MS = 20`), garantindo que cada pulso emitido pela biblioteca `Servo.h` reflita uma evolução suave da trajetória.

### 3. Perfil de Velocidade Trapezoidal com Piso Anti Stick-Slip (`velMin`)
* O algoritmo calcula a distância restante até o alvo ($d$).
* **Frenagem Suave:** A velocidade desejada de aproximação é calculada pela curva cinemática:
  $$v_{\text{desejada}} = \sqrt{2 \cdot a \cdot d}$$
* **Piso de Velocidade (`velMinUs`):** Durante a frenagem final, a velocidade de aproximação é limitada a um **piso mínimo** (ex: $15^\circ/\text{s}$). O servo nunca chega ao destino "se arrastando" na zona de atrito estático; ele finaliza o alinhamento com torque decidido e para de forma limpa.

### 4. Compensação Ativa de Antifolga (*Backlash Compensation*)
* Ao inverter o sentido de rotação de engrenagens plásticas, existe uma folga morta (*backlash*) entre os dentes.
* Se o parâmetro `backlashUs` estiver ativo ($> 0$), ao executar um movimento no sentido reverso, o código passa intencionalmente alguns microssegundos além do ponto final e retorna para o alvo exato. Dessa forma, o servo encerra o movimento **sempre encostando no mesmo flanco do dente**, eliminando oscilações causadas pelo vento ou inércia da cabeça.

---

## 🎛️ Tabela de Parâmetros de Calibração (Via Protocolo `<C,id,valor>`)

Estes parâmetros podem ser ajustados em tempo real pelo painel web do **POC 2** e do **POC 4**:

| ID | Parâmetro | Faixa Típica | Valor Padrão | Efeito Prático no Movimento |
|---|---|---|---|---|
| `1` | Velocidade Padrão | $50$ a $300^\circ/\text{s}$ | **$145^\circ/\text{s}$** | Velocidade de cruzeiro para grandes movimentações. |
| `2` | Piso de Aproximação | $5$ a $40^\circ/\text{s}$ | **$15^\circ/\text{s}$** | Impede o servo de desacelerar na faixa de stick-slip. |
| `3` | Aceleração | $200$ a $2000^\circ/\text{s}^2$ | **$870^\circ/\text{s}^2$** | Elimina chicoteios bruscos na arrancada e parada. |
| `4` | Banda Morta (*Deadband*) | $1$ a $5\ \mu\text{s}$ | **$2\ \mu\text{s}$** | Silencia o servo ao atingir o alvo (elimina zumbido/jitter). |
| `5` | Antifolga (*Backlash*) | $0$ a $40\ \mu\text{s}$ | **$0\ \mu\text{s}$** | Compensa a folga mecânica entre os dentes na reversão. |
| `6` | Desanexar Parado (*Detach*) | $0$ a $30\text{ s}$ | **$0$ (desligado)** | Desliga o sinal PWM após repouso para economizar energia e zerar ruído. |
