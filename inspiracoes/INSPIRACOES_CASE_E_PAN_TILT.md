# 🎨 Galeria Visual de Inspirações (Cases, Pan/Tilt & Chassi 3D)

Esta pasta reúne **imagens de referência e conceitos visuais** para guiar a modelagem em 3D do robô móvel ESP32, da carcaça da câmera e do mecanismo Pan & Tilt com servos SG90.

---

## 🏆 CONCEITO PRINCIPAL ALINHADO: Chassi Fechado + Rodas Sumô + Cabeça Encapsulada

![Chassi Fechado com Rodas Sumo](/home/usuario/Documentos/rover/inspiracoes/04_chassi_fechado_sumo.jpg)

* **Design Aprovado:**
  * **Carcaça Fechada (Carenagem):** Eletrônica, bateria 7.4V e motores protegidos internamente. Visual limpo e industrial, sem fios soltos nem placas expostas.
  * **Rodas de Borracha Tipo Sumô:** Rodas compactas de alta aderência (estilo StickyMAX).
  * **Cabeça Móvel Encapsulada:** O ESP32 fica 100% alojado dentro da cabeça. Apenas o círculo da lente da câmera e a barra de 8 LEDs RGB logo abaixo ficam expostos.
  * **Ordem dos Servos:** **Pan na base** (giro horizontal) e **Tilt no topo** (inclinação vertical).

---

## 📸 1. Conceito do Case da Câmera (ESP32-S3 + Lente + 8 LEDs RGB)

![Case da Câmera ESP32-S3](/home/usuario/Documentos/rover/inspiracoes/01_case_camera_esp32_s3.jpg)

* **Características-chave:**
  * Abertura frontal circular sob medida para a lente da câmera OV5640 5MP.
  * **Slot frontal para a barra de 8 LEDs WS2812B:** Os LEDs ficam logo abaixo da lente, atuando como farol direcional (a luz aponta para onde a câmera olha).
  * Abertura lateral para acesso à porta USB-C (permite programar sem tirar a placa do case).
  * Grelha de ventilação lateral/traseira para resfriamento do chip ESP32-S3.
  * Suporte lateral/traseiro para fixação direta da cruzeta (servo horn) do micro servo SG90.

---

## 🔄 2. Mecanismo de 2 Eixos Pan & Tilt (Micro Servos SG90)

![Mecanismo Pan Tilt 2 Eixos com SG90](/home/usuario/Documentos/rover/inspiracoes/02_mecanismo_pan_tilt_sg90.jpg)

* **Características-chave:**
  * **Eixo Pan (Base):** Servo SG90 montado verticalmente, girando a plataforma horizontal em até 180°.
  * **Eixo Tilt (Elevação):** Servo SG90 montado no braço em "U", inclinando a câmera para cima e para baixo.
  * **Alça de Alívio (Strain Relief):** Laço flexível nos fios elétricos para permitir rotação completa sem prender nem forçar o servo.

---

## 🏎️ 3. Conceito do Rover 4WD Completo em Impressão 3D

![Conceito do Carrinho 4WD com Pan Tilt](/home/usuario/Documentos/rover/inspiracoes/03_chassi_carrinho_4wd_completo.jpg)

* **Características-chave:**
  * **Dois Conveses (Andares):**
    * **Andar Inferior:** Alojamento central da bateria Li-Ion 7.4V (centro de gravidade baixo), suportes dos 4 micromotores JGA-050 e recorte traseiro para a chave gangorra liga/desliga.
    * **Andar Superior:** Torre dianteira com o sistema Pan & Tilt, deixando a câmera avançada para enxergar o piso à frente sem filmar as rodas.
  * Estilo robusto, modular e com parafusos de fácil acesso para manutenção.

---

## 🛠️ 4. Referências Reais da Comunidade Maker

### Montagem Clássica Pan & Tilt com ESP32-CAM e SG90
![Montagem Clássica Pan Tilt ESP32-CAM](/home/usuario/Documentos/rover/inspiracoes/esp32_cam_pan_tilt_assembled.jpg)

### Suporte Articulado Comercial / Padrão Mini Pan-Tilt
![Mecanismo Articulado SG90](/home/usuario/Documentos/rover/inspiracoes/pan_tilt_sg90_mechanism.jpg)
