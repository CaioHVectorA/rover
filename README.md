# 🤖 Robô Móvel ESP32-S3 (4WD & Pan/Tilt)

Projeto de engenharia e desenvolvimento de uma plataforma robótica móvel didática com **tração 4WD**, **visão computacional/streaming em tempo real com Pan & Tilt**, **iluminação RGB** e **saída sonora**, controlada integralmente pelo microcontrolador **ESP32-S3 CAM**.

---

## 🎯 Objetivo Imediato: MVP no Wi-Fi Local
O desenvolvimento está focado na entrega rápida do **MVP (Produto Mínimo Viável)** contendo:
* 🚗 **Tração 4WD Skid-Steer:** 4 micromotores DC com redução acionados remotamente.
* 📷 **Streaming de Vídeo:** Câmera OV5640 5MP transmitindo via Wi-Fi direto para o navegador de qualquer celular ou PC (MJPEG por hardware com 8MB de PSRAM).
* 🔄 **Mecanismo Pan & Tilt:** 2 micro servos movimentando a placa com a câmera em 2 eixos em tempo real.
* 📱 **Interface Web Embarcada:** Servidor web rodando dentro do próprio ESP32 com botões e joysticks virtuais via WebSockets.

---

## 📁 Documentos de Engenharia do Repositório

Todos os documentos estão sincronizados e organizados para consulta e desenvolvimento:

| Documento | Descrição e Finalidade |
|---|---|
| ⚡ [**`PROJETO_ELETRICA_E_PINAGEM.md`**](file:///home/usuario/Documentos/rover/PROJETO_ELETRICA_E_PINAGEM.md) | **Esquemático Elétrico & Distribuição de Energia:** Conexão da bateria 7.4V, chave gangorra, step-down 5V, driver TB6612FNG, pinagem dos GPIOs do ESP32-S3 e proteção contra brownouts. |
| 🏎️ [**`PROJETO_MECANICA_E_CASE.md`**](file:///home/usuario/Documentos/rover/PROJETO_MECANICA_E_CASE.md) | **Case, Chassi & Mecânica do Pan/Tilt:** Estrutura em dois andares, posicionamento dos motores JGA-050, montagem da placa no berço do Pan/Tilt, alívio de cabos e integração dos controles. |
| 🗺️ [**`ROADMAP.md`**](file:///home/usuario/Documentos/rover/ROADMAP.md) | **Canvas do MVP, fluxo visual em Mermaid e cronograma em 5 fases** (da bancada à pilotagem FPV via Wi-Fi e telepresença). |
| 🧠 [**`MEMORIA_DO_PROJETO.md`**](file:///home/usuario/Documentos/rover/MEMORIA_DO_PROJETO.md) | **Memória viva e diário de decisões:** Histórico das conversas, justificativas técnicas e registro de hardware adquirido. |

---

## 🧰 Hardware Adquirido (Em Trânsito / Preparação de Bancada)
1. **Controle & Visão:** ESP32-S3-CAM N16R8 (Câmera OV5640 5MP) + ESP32-CAM (RoboCore) + Arduino Nano V3.
2. **Tração 4WD:** 4x Micromotores de redução metálica (série JGA-050) + Rodas de borracha de alta aderência + Suportes em L.
3. **Ponte H:** Driver TB6612FNG (MOSFET duplo, eficiente e sem perda de tensão).
4. **Visão Articulada:** Mecanismo Pan & Tilt 2 eixos acionado por 2 micro servos SG90.
5. **Alimentação:** Pack Bateria Li-Ion 2S 7.4V 2500mAh com BMS integrado + Chave Gangorra + Regulador Step-Down 5.0V.
6. **Sinalização:** Barra 8 LEDs RGB WS2812B + Módulo Buzzer passivo 5V.

