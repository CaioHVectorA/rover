# 🔬 Suíte de POCs Incrementais (Proof of Concept)

Esta pasta documenta a suíte completa de **6 POCs (Provas de Conceito)** desenvolvidas para validar cada subsistema do **Rover Móvel ESP32-S3 4WD & Pan/Tilt** de forma isolada, progressiva e segura na bancada de testes.

---

## 🎯 Por que POCs Isoladas?

Ao ligar câmera OV5640, Wi-Fi, dois micro servos SG90 e quatro micromotores DC JGA16-050 ao mesmo tempo, surgem conflitos difíceis de diagnosticar:
1. **Quedas de Tensão / Brown-Out:** Motores arrancando do zero puxam até 4A instantâneos e podem reiniciar o Arduino Nano.
2. **Superaquecimento:** O sensor OV5640 operando a 20 MHz contínuos dissipa calor desnecessário.
3. **Instabilidade Mecânica ("Rebolado"):** O servo de Pan comandado com saltos grosseiros de 2° entra em ressonância com a folga da bucha plástica.
4. **Travamento de Rede:** Um stream de vídeo com laço bloqueante congela o processamento de pacotes WebSocket.

A suíte de 6 POCs resolve cada um desses desafios em degraus independentes.

---

## 📋 Tabela Resumo dos Ambientes PlatformIO

Todos os ambientes são compilados diretamente a partir do [`platformio.ini`](file:///c:/Users/caihe/Documents/develop/rover/platformio.ini):

| POC | Nome da POC | Placa | Ambiente PlatformIO (`-e`) | Portas / Interface | Função Principal |
|---|---|---|---|---|---|
| **POC 1** | Enlace Serial RX/TX | **ESP32-S3** | `poc1_esp32` | HTTP `:80` | Servidor Web de diagnóstico de ping/RTT e monitoramento de heartbeat |
| | | **Arduino Nano** | `poc1_nano` | Serial 9600 | Responde pings `<P,n>` com `<A,n>` e envia `<H,...>` a 1 Hz |
| **POC 2** | Pan/Tilt Controlado | **ESP32-S3** | `poc2_esp32` | HTTP `:80` + WS `:81` | Sliders 0°–180°, teste de varredura lenta e sintonia de parâmetros |
| | (Sem Vídeo) | **Arduino Nano** | `poc2_nano` / `poc2_nano_hw` | D9 / D10 (SG90) | Controle suave anti-rebolado via microssegundos a 50 Hz |
| **POC 3** | Transmissão de Vídeo Fria | **ESP32-S3** | `poc3_esp32` | HTTP `:80` + Video `:82` | Câmera fria isolada (sem Nano), standby automático em 0x3008 e downclock XCLK |
| **POC 4** | Pan/Tilt + Transmissão | **ESP32-S3** | `poc4_esp32` | HTTP `:80` + WS `:81` + Video `:82` | Vídeo simultâneo aos servos com modo Eco automático e separação de núcleos FreeRTOS |
| | | **Arduino Nano** | `poc2_nano` | D9 / D10 (SG90) | O mesmo firmware do POC 2 é reaproveitado diretamente |
| **POC 5** | Teste Automático de Motores | **Arduino Nano** | `poc5_nano` | Serial Monitor 115200 | Sequência autônoma de vai-e-volta, giros e curvas com monitoramento de sag de bateria |
| **POC 6** | Motores Controlados | **ESP32-S3** | `poc6_esp32` | HTTP `:80` + WS `:81` | Joystick virtual touch, D-pad e controle por teclado (WASD / Setas) |
| | | **Arduino Nano** | `poc6_nano` / `poc6_nano_hw` | D3–D8, D12 (TB6612) | Rampa de aceleração, tempo morto na reversão e watchdog failsafe |

---

## ⚡ Comandos Rápidos de Gravação e Monitoramento

Substitua `COMx` pela porta serial detectada no seu computador:

```powershell
# POC 1: Enlace Serial
pio run -e poc1_esp32 -t upload --upload-port COM24
pio run -e poc1_nano  -t upload --upload-port COM18

# POC 2: Pan/Tilt Suave (Anti-Rebolado)
pio run -e poc2_esp32 -t upload --upload-port COM24
pio run -e poc2_nano  -t upload --upload-port COM18

# POC 3: Câmera Fria Isolada (Apenas ESP32)
pio run -e poc3_esp32 -t upload --upload-port COM24

# POC 4: Pan/Tilt + Vídeo Simultâneo
pio run -e poc4_esp32 -t upload --upload-port COM24
# Nano reutiliza poc2_nano!

# POC 5: Teste de Motores no Nano (Bancada com Rodas no Ar)
pio run -e poc5_nano -t upload --upload-port COM18
pio device monitor -e poc5_nano --port COM18

# POC 6: Motores Controlados via Web/Celular
pio run -e poc6_esp32 -t upload --upload-port COM24
pio run -e poc6_nano  -t upload --upload-port COM18
```

---

## 📖 Documentação Detalhada dos POCs

* [**Guia Completo de Execução dos POCs Passo a Passo**](file:///c:/Users/caihe/Documents/develop/rover/docs/pocs/GUIA_EXECUCAO_POCS.md)
* [**Engenharia Térmica da Câmera OV5640 via Software**](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/camera_calor_software.md)
* [**Eliminação do Efeito "Rebolado" nos Servos SG90**](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/ajuste_fino_servos_rebolado.md)
* [**Prevenção de Brown-Out e Rampa de Aceleração 4WD (TB6612FNG)**](file:///c:/Users/caihe/Documents/develop/rover/docs/guides/tracao_motores_anti_reset.md)
