# 📱 App Rover Expo (VR Head-Tracking & FPV Controller)

Aplicativo React Native / Expo para controle do **Rover 4WD ESP32-S3 + Arduino Nano**, com suporte a **FPV** e **Head-Tracking em Realidade Virtual (VR)** usando o giroscópio do celular.

---

## 🚀 Como Executar no seu Celular

### 1. Pré-requisitos
* Instale o aplicativo **Expo Go** no seu smartphone (disponível na Google Play Store ou Apple App Store).
* O computador e o celular devem estar conectados na **mesma rede Wi-Fi** (ou o celular conectado no Wi-Fi `Rover-Nano` gerado pelo ESP32).

### 2. Iniciar o Servidor de Desenvolvimento
No terminal do projeto:
```bash
cd app_rover_expo
npx expo start
```

### 3. Abrir no Celular
* Abra o **Expo Go** e escaneie o **QR Code** gerado no terminal.

---

## 🥽 Modos de Operação

1. **📊 Modo Painel (Dashboard):**
   * Ajuste fino dos servos Pan e Tilt (grau a grau).
   * Calibração de sensibilidade do giroscópio (Filtro EMA e Zona Morta *Anti-Jitter*).
   * Botões manuais de tração 4WD e telemetria com indicador de ping/latência.
2. **📱 Modo FPV Touch:**
   * Câmera ao vivo em tela cheia com mira HUD.
   * D-Pad virtual na tela para manobrar o carrinho com os dedos.
   * Ativação rápida de giroscópio e botão de centralização de visão.
3. **🕶️ Modo VR Head-Tracking (Side-by-Side):**
   * Tela dividida para encaixar em qualquer **óculos VR para smartphone** (Google Cardboard, VR Box, etc.).
   * Movimento da cabeça gira a câmera do robô em tempo real.
   * Botão de toque rápido na tela para calibrar o ponto central de visão.

---

## ⚙️ Configuração de Rede
No ícone de engrenagem ⚙️ do app, você pode configurar:
* **IP do ESP32:** Padrão `192.168.4.1` (Modo AP) ou o IP obtido na sua rede local (ex: `192.168.1.150`).
* **Porta WebSocket:** `81` (padrão para telemetria e giroscópio).
* **Porta do Stream:** `80` (caminho `/stream`).
