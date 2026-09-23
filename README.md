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

## 📁 Documentos Ativos do Repositório

Todos os documentos foram sincronizados e estão interligados para consulta:

| Documento | Descrição e Finalidade |
|---|---|
| 🗺️ [**`ROADMAP.md`**](file:///home/usuario/Documentos/rover/ROADMAP.md) | **Canvas do MVP, fluxo visual em Mermaid e cronograma em 5 fases** (desde a bancada até a teleoperação de longa distância via internet). |
| 🧠 [**`MEMORIA_DO_PROJETO.md`**](file:///home/usuario/Documentos/rover/MEMORIA_DO_PROJETO.md) | **Memória viva e diário de decisões:** Histórico das conversas, solução mecânica do Pan/Tilt com placa montada, prevenção de *brownout* e boas práticas elétricas. |
| 🛒 [**`linha-esp32-s3/LISTA_DE_COMPRAS.md`**](file:///home/usuario/Documentos/rover/linha-esp32-s3/LISTA_DE_COMPRAS.md) | **Lista consolidada de compras:** Placa ESP32-S3 no Mercado Livre e kit de peças mecânicas, tração, servos e energia na RoboCore. |

---

## ⚡ Estratégia de Compras
1. **Mercado Livre:** [Placa ESP32-S3 CAM N16R8 (16MB Flash / 8MB PSRAM + Câmera 5MP OV5640 + USB-C)](https://www.mercadolivre.com.br/p/MLB2061307865?matt_tool=38524122&pdp_filters=item_id:MLB5139266661).
2. **RoboCore (`robocore.net`):** Micromotores de redução metálica (~200 RPM), rodas emborrachadas StickyMAX, servos SG90, suporte Pan/Tilt, driver de motor, step-down, baterias 18650, buzzer e LEDs WS2812B.
# rover
