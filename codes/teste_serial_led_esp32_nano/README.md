# 🧪 Teste Prático de Comunicação Serial: ESP32 (Web) ➔ Arduino Nano (LED)

Este teste valida a arquitetura básica de comunicação entre a **placa de visão/rede (ESP32)** e a **placa de potência do chassi (Arduino Nano)** antes de montarmos os motores e servos.

---

## 🔌 1. Esquema de Ligação na Bancada (Apenas 2 Fios!)

Para este teste inicial, você só precisa de **2 jumpers**:

```
 [ ESP32-S3-CAM / ESP32 ]                          [ ARDUINO NANO V3 ]
+-------------------------+                       +-------------------+
|                         |                       |                   |
|           GND ----------+=======================+--- GND            |
|                         |      (Fio 1: Terra)   |                   |
|       IO43 (TX) --------+---------------------->+--- RX0 (Pino D0)  |
|   (ou GPIO 1 no Clássico)|    (Fio 2: Sinal)     |                   |
|                         |                       |     [LED D13]     |
+-------------------------+                       +-------------------+
```

> ⚠️ **REGRA DE OURO DO ARDUINO NANO (Gravação via USB):**
> O pino digital `D0 (RX)` do Arduino Nano é conectado internamente ao chip conversor USB da placa.
> Ao conectar o cabo USB no computador para gravar o código no Nano, **desconecte temporariamente o jumper do pino RX**.
> Se o ESP32 estiver conectado no RX durante a gravação, a IDE do Arduino dará erro de sincronização (`avrdude: stk500_recv(): programmer is not responding`). Assim que a gravação terminar, reconecte o fio no pino RX!

---

## 🚀 2. Passo a Passo de Teste

### Passo 1: Gravar o Arduino Nano
1. Abra o arquivo [`nano_rx_led.ino`](file:///home/usuario/Documentos/rover/codes/teste_serial_led_esp32_nano/nano_rx_led/nano_rx_led.ino) na Arduino IDE.
2. Em **Ferramentas ➔ Placa**, selecione **Arduino Nano**.
3. Em **Processador**, selecione **ATmega328P** (ou *Old Bootloader* se for o clone comum).
4. Conecte o cabo USB no Nano e faça o upload.
5. Ao ligar, o LED embutido no pino 13 piscará 3 vezes para confirmar que o firmware iniciou.

### Passo 2: Gravar o ESP32
1. Abra o arquivo [`esp32_web_tx.ino`](file:///home/usuario/Documentos/rover/codes/teste_serial_led_esp32_nano/esp32_web_tx/esp32_web_tx.ino) na Arduino IDE.
2. No topo do arquivo, verifique a placa selecionada (`PLACA_ESP32_S3_CAM` ou `PLACA_ESP32_CAM_CLASSIC`).
3. Conecte o cabo USB no ESP32 e faça o upload.

### Passo 3: Testar via Celular ou Notebook
1. Com as duas placas ligadas e os fios de GND e TX/RX conectados:
2. Como o ESP32 se conecta na mesma rede Wi-Fi do seu computador (`Apple Network fdd7b9`), você **não precisa trocar de rede Wi-Fi** no seu PC ou celular.
3. Abra o Serial Monitor da IDE do Arduino (a 115200 baud) no ESP32 para ver o IP atribuído, ou simplesmente acesse pelo navegador:
   * **Opção 1:** `http://rover.local`
   * **Opção 2:** `http://<IP_DO_ESP32>` (ex: `http://192.168.1.X`)
4. Você verá a interface web do Rover.
5. Clique no botão verde **LIGAR** ➔ o sinal trafega pela rede, sai pelo pino TX do ESP32, entra no pino RX do Nano e o LED acende instantaneamente!
6. Clique no botão vermelho **DESLIGAR** ➔ o LED do Arduino Nano apaga!
