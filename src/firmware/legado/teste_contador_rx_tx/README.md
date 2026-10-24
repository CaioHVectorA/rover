# 🧪 Teste de Bancada: Contador Sequencial TX / RX (ESP32-S3 ➔ Arduino Nano)

Este teste valida a integridade física do canal serial entre o **ESP32-S3** (TX pino IO43) e o **Arduino Nano** (RX pino D2 via transistor inversor BC337).

---

## 🔌 Esquema Elétrico de Ligação

```
 [ ESP32-S3-CAM ]                                          [ ARDUINO NANO V3 ]
+------------------+                                      +-------------------+
|                  |                                      |                   |
|              GND +======================================+ GND               |
|                  |       (GND Comum Obrigatório)        |                   |
|                  |                                      |     +5V (Pull-up) |
|                  |       1k             BC337           |      |            |
|                  |    +-------+        +-----+          |     [10k]         |
|        IO43 (TX) +--->| R 1k  +------->| B   |          |      |            |
|                  |    +-------+        |   C +----------+------+ Pino D2    |
|                  |                  +--+ E   |          |                   |
|                  |                  |  +-----+          |                   |
|                  |                  V                   |     [LED D13]     |
|                  |                 GND                  |                   |
|                  |                                      |                   |
|        IO44 (RX) +<-------------------------------------+ Pino D3 (ACK TX)  |
|                  |                                      |                   |
+------------------+                                      +-------------------+
```

---

## ⚡ Como Funciona o Inversor BC337:
1. **Idle da Serial (Nível Alto / 3.3V):**
   - A saída IO43 do ESP32 fica em nível ALTO (3.3V).
   - A corrente flui para a base do BC337 -> o transistor satura (liga).
   - O coletor vai para GND (~0.1V a 0.2V).
   - **Resultado no multímetro em D2:** Leitura próxima de **0V** em repouso.
2. **Transmissão de Dados (Start Bit / Nível Baixo):**
   - O ESP32 coloca IO43 em nível BAIXO (0V).
   - O transistor corta (desliga).
   - O resistor de pull-up (10k ligado em 5V) puxa o pino D2 para **5V**.
   - **No Nano:** O `SoftwareSerial s3Serial(2, 3, true);` com `inverse_logic = true` decodifica isso perfeitamente.

---

## 📊 O Que Cada Placa Faz

- **ESP32-S3:**
  - A cada 1 segundo, incrementa um contador e envia `<CNT:1>`, `<CNT:2>`, etc. pelo pino IO43 (9600 baud).
  - No monitor USB (115200 baud), exibe: `[ESP32 TX -> IO43] Pacote enviado: <CNT:x>`.
- **Arduino Nano:**
  - Escuta no pino D2 via `SoftwareSerial` invertido.
  - A cada pacote `<CNT:x>` recebido:
    - Alterna o LED D13 (pisca a cada segundo).
    - Exibe no monitor USB (9600 baud): `[NANO RX OK] Pacote recebido: <CNT:x> | Total de pacotes: x`.
    - Responde `<ACK:x>` de volta para o ESP32.
  - A cada 2 segundos, exibe um relatório de status informando a contagem atual e o nível lógico lido no pino D2.
