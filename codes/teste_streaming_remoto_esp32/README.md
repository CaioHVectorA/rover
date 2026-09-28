# 📹 Teste de Streaming Remoto do ESP32 via Servidor Relay (WebSocket)

Este diretório contém o teste e extensão do **CameraWebServer** para **transmissão de vídeo em tempo real do ESP32 via redes externas (4G/LTE ou Wi-Fi remoto)**.

---

## 📐 Arquitetura do Sistema

Para conseguir visualizar a câmera do ESP32 estando em **outra rede ou dados móveis (4G)**, superamos a limitação do **CGNAT** das operadoras móveis utilizando uma **Arquitetura de Servidor Relay Central**:

```
 ┌──────────────────────┐          WebSocket (Binary JPEG)        ┌───────────────────────────────┐
 │   ESP32-CAM / S3     │ ──────────────────────────────────────> │  Servidor Relay (Node.js)     │
 │  (Rede Local / 4G)   │   ws://seu-servidor.com/ws?role=esp32   │  (VPS / Nuvem / Local / ngrok)│
 └──────────────────────┘                                         └──────────────┬────────────────┘
                                                                                 │
                                                                                 │ WebSocket (Drop-Frame)
                                                                                 │ wss://.../ws?role=viewer
                                                                                 ▼
                                                                  ┌───────────────────────────────┐
                                                                  │   Navegador Web / Mobile      │
                                                                  │   (Qualquer lugar do mundo)   │
                                                                  └───────────────────────────────┘
```

---

## 📂 Estrutura de Arquivos

```
codes/teste_streaming_remoto_esp32/
├── README.md                          # Este guia de uso e documentacao tecnica
├── esp32_camera_relay/                # Firmware para o microcontrolador ESP32
│   ├── camera_pins.h                  # Mapeamento de pinos (ESP32-CAM AI-Thinker e ESP32-S3-CAM)
│   └── esp32_camera_relay.ino         # Codigo estendido do CameraWebServer com cliente WebSocket
└── server/                            # Servidor Web e Relay em Node.js
    ├── package.json                   # Dependencias (express, ws)
    ├── server.js                      # Servidor WebSocket Relay
    └── public/                        # Interface Web em Dark Mode
        ├── index.html                 # Layout e HUD de telemetria
        ├── style.css                  # Estilizacao responsiva
        └── app.js                     # Cliente JS com renderizacao HTML5 Canvas e Drop-Frame
```

---

## 🚀 Passo a Passo: Como Executar o Teste

### 1. Iniciar o Servidor Relay (Node.js)

No terminal, navegue até a pasta do servidor e instale as dependências:

```bash
cd codes/teste_streaming_remoto_esp32/server
npm install
npm start
```

O servidor iniciará na porta `3000`:
* 🌐 **Interface Web:** `http://localhost:3000`
* 📡 **Endpoint WebSocket ESP32:** `ws://localhost:3000/ws?role=esp32`
* 📺 **Endpoint WebSocket Viewer:** `ws://localhost:3000/ws?role=viewer`

---

### 2. Expor o Servidor para a Internet (Para Testar em Outra Rede / 4G)

Para testar o acesso vindo de redes externas (ex: 4G do celular):

#### Opção A: Usando `ngrok` (Mais fácil)
```bash
ngrok http 3000
```
O `ngrok` gerará um link público seguro (ex: `https://abcd-123.ngrok-free.app`).

#### Opção B: VPS / Nuvem (AWS, DigitalOcean, Hetzner, etc.)
Instale o Node.js na sua VPS, suba o arquivo `server.js` e execute em background via `pm2` ou `nohup`.

---

### 3. Gravar o Firmware no ESP32

1. Abra o arquivo [`esp32_camera_relay.ino`](file:///home/usuario/Documentos/rover/codes/teste_streaming_remoto_esp32/esp32_camera_relay/esp32_camera_relay.ino) na **Arduino IDE**.
2. No menu **Tools / Placa**, selecione **ESP32 Wrover Module** (para ESP32-CAM) ou **ESP32S3 Dev Module** (para ESP32-S3-CAM).
3. Ative a opção **PSRAM: Enabled**.
4. Instale a biblioteca necessária no Gerenciador de Bibliotecas da Arduino IDE:
   * **`WebSockets`** por *Markus Sattler (Links2004)*.
5. Edite as variáveis no início do código:
   ```cpp
   const char* WIFI_SSID     = "SUA_REDE_WIFI";
   const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";
   const char* RELAY_HOST    = "192.168.1.100"; // Ou o IP/Dominio da sua VPS / ngrok
   const uint16_t RELAY_PORT = 3000;
   ```
6. Grave no ESP32.

---

## ⚙️ Características Técnicas & Otimizações

1. **Latência Mínima (Drop-Frame):**
   * O cliente JavaScript no navegador descarta quadros atrasados (*Drop-Frame*) se a placa de vídeo ainda estiver renderizando o quadro anterior, eliminando o acúmulo de lag (*Buffer Lag*).
2. **Duplo Buffer na PSRAM (`fb_count = 2`):**
   * O ESP32 utiliza DMA e PSRAM para capturar o próximo quadro enquanto transmite o atual pela rede.
3. **Economia de Energia de Wi-Fi Desativada (`WIFI_PS_NONE`):**
   * Garante tempo de resposta tátil imediato do rádio Wi-Fi.
4. **Resoluções Sugeridas:**
   * `FRAMESIZE_QVGA` (320x240): **25-30 FPS** (Ideal para teleoperação rápida).
   * `FRAMESIZE_CIF` (400x296): **20-25 FPS** (Maior nitidez para inspeção).
