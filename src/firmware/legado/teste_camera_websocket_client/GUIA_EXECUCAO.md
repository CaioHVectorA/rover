# 🛸 Guia de Gravação e Execução: Cliente WebSocket FPV no ESP32-S3

Este teste valida a conexão segura via WebSocket (`wss://`) do ESP32-S3 com o nosso Servidor Relay no Fly.io (`rover-relay-fpv-sp.fly.dev`), transmitindo frames em formato binário e medindo latência real.

---

## 📋 Pré-requisitos na Arduino IDE

Se for gravar pela **Arduino IDE**, siga estes passos de configuração:

1. **Instalar a Biblioteca WebSocket:**
   * Vá em **Sketch -> Incluir Biblioteca -> Gerenciar Bibliotecas...**
   * Busque por: `WebSockets` (por Markus Sattler / `Links2004`). Instale a versão mais recente.
   * Busque por: `ArduinoJson` (por Benoit Blanchon). Instale a versão 7.x.

2. **Configuração da Placa no Menu Ferramentas:**
   * **Placa:** `"ESP32S3 Dev Module"`
   * **USB CDC On Boot:** `"Enabled"` *(Fundamental para que o Monitor Serial funcione pela porta USB-C nativa)*
   * **Flash Size:** `"16MB (128Mb)"`
   * **Partition Scheme:** `"16M Flash (3MB APP/9.9MB FATFS)"` ou `"Huge APP (3MB No OTA)"`
   * **PSRAM:** `"OPI PSRAM"` *(O chip N16R8 possui 8MB de Octal PSRAM - obrigatório para buffers da câmera)*
   * **Upload Speed:** `921600`
   * **Porta:** Selecione a porta COM correspondente ao ESP32-S3.

3. **Gravação:**
   * Abra [`teste_camera_websocket_client.ino`](file:///c:/Users/caihe/Documents/develop/rover/testes/teste_camera_websocket_client/teste_camera_websocket_client.ino)
   * Clique em **Carregar (Upload)**.
   * Abra o **Monitor Serial** configurado em **115200 baud**.

---

## ⚡ Ou Gravação via PlatformIO (Linha de Comando)

Se preferir usar o PlatformIO já instalado:

```bash
cd testes/teste_camera_websocket_client
pio run -t upload
pio device monitor
```

---

## 👁️ Como Testar e Visualizar

1. Abra o painel do piloto no seu navegador:
   👉 **https://rover-relay-fpv-sp.fly.dev/**
2. Quando o ESP32-S3 conectar ao Wi-Fi e à nuvem:
   * O indicador **ROBÔ** mudará de `OFFLINE` para `TRANSMITINDO` (verde).
   * O vídeo aparecerá imediatamente na tela.
   * O HUD exibirá o FPS dinâmico, Bitrate e a latência precisa do link.
3. Teste abrir o mesmo link no **4G/5G do seu celular** para comprovar o funcionamento fora da rede local!
