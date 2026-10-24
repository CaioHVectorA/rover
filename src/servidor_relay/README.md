# 🛰️ Rover Cloud Relay & Cockpit FPV (Fly.io)

Servidor de retransmissão de vídeo de baixa latência e telemetria para o Rover FPV, hospedado no datacenter de São Paulo (`gru`) da Fly.io.

---

## 🏗️ Arquitetura Distribuída

```mermaid
sequenceDiagram
    autonumber
    actor Piloto as 🕹️ Piloto (Navegador Web)
    participant Relay as 🛰️ Relay Fly.io (gru)
    participant ESP32 as 🤖 ESP32-S3 CAM (Wi-Fi)

    Note over Piloto,ESP32: 1. Handshake & Conexões WebSocket
    ESP32->>Relay: Conecta wss://.../ws/robot
    Relay-->>Piloto: Notifica: ROBOT ONLINE
    Piloto->>Relay: Conecta wss://.../ws/pilot
    
    Note over Piloto,ESP32: 2. Streaming de Vídeo & RTT Robô
    ESP32->>Relay: Frame Binário [ID(4B) + Time(4B) + JPEG]
    Relay-->>ESP32: ACK [0x01, ID, Time] -> Calcula RTT_esp
    Relay->>Piloto: Injeta ServerTime(8B) + Frame -> Renderiza HUD

    Note over Piloto,ESP32: 3. Telemetria Piloto & Comandos
    Piloto->>Relay: Ping [timestamp] -> Pong -> Calcula RTT_piloto
    Piloto->>Relay: Comando Pilotagem [WASD / Pan / Tilt]
    Relay->>ESP32: Repassa Comando Instantâneo
```

---

## 📡 Endpoints Públicos

* **Interface Web do Cockpit (HUD):** `https://rover-relay-fpv-sp.fly.dev/`
* **Healthcheck:** `https://rover-relay-fpv-sp.fly.dev/health`
* **WebSocket do Robô (ESP32-S3):** `wss://rover-relay-fpv-sp.fly.dev/ws/robot`
* **WebSocket do Piloto (Navegador):** `wss://rover-relay-fpv-sp.fly.dev/ws/pilot`

---

## ⏱️ Protocolo de Medição de Latência (Two-Leg RTT)

1. **Perna Robô $\leftrightarrow$ Nuvem:**
   * O ESP32 envia `uint32_t millis()` junto ao frame.
   * O Relay responde imediatamente com o ACK de 9 bytes.
   * Latência de subida estimada: $\Delta t_{esp} = \frac{RTT_{esp}}{2}$.

2. **Perna Nuvem $\leftrightarrow$ Piloto:**
   * O navegador do piloto envia pacotes `{ type: "ping", t: performance.now() }` a cada 1 segundo.
   * O servidor responde instantaneamente `{ type: "pong", t: ... }`.
   * Latência de descida estimada: $\Delta t_{pilot} = \frac{RTT_{pilot}}{2}$.

3. **Latência Total Fim-a-Fim:**
   $$\Delta t_{total} \approx \Delta t_{esp} + \Delta t_{pilot}$$

---

## 🚀 Comandos de Gerenciamento

```bash
# Testar localmente:
npm start

# Visualizar logs em tempo real na nuvem:
fly logs -a rover-relay-fpv-sp

# Fazer novo deploy:
fly deploy
```
