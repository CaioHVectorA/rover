# 🛒 Lista de Compras - Robô Móvel ESP32-S3 CAM + Nano V3 + VR

Lista de componentes para a arquitetura baseada no microcontrolador **ESP32-S3 CAM N16R8** (Visão Wi-Fi, Câmera OV5640 5MP e Web Server) em conjunto com o **Arduino Nano V3** (Co-processador em tempo real para controle de 4 motores e 2 servos Pan/Tilt), tração 4WD com rodas de alta aderência, sensor de orientação VR (MPU-6050), sinalização luminosa e sonora.

> 📚 **Planilhas Excel Geradas:**
> * 📄 [**`LISTA_DE_COMPRAS_ROVER_ESP32.xlsx`**](file:///c:/Users/caihe/Documents/develop/rover/linha-esp32-s3/LISTA_DE_COMPRAS_ROVER_ESP32.xlsx) (Planilha minimalista na pasta do ESP32).
> * 📄 [**`LISTA_DE_COMPRAS_ROVER_ESP32_RESTAURADA.xlsx`**](file:///c:/Users/caihe/Documents/develop/rover/LISTA_DE_COMPRAS_ROVER_ESP32_RESTAURADA.xlsx) (Cópia minimalista na raiz do projeto).

---

## 1. Pedido Principal: RoboCore (`robocore.net`)

Carrinho composto por **23 unidades (15 linhas de produtos)**:

| Item | Produto | Qtd | Preço Unit. | Subtotal | Link Direto na Loja |
|:---:|---|:---:|:---:|:---:|---|
| 1 | Micro Servo 9g SG90 (TowerPro) | 2 | R$ 13,67 | R$ 27,34 | [Abrir na RoboCore](https://www.robocore.net/atuador/micro-servo-9g-sg90-towerpro) |
| 2 | Micro Motor com Redução Metálica 6V 100RPM (Eixo D 3mm) | 4 | R$ 29,90 | R$ 119,60 | [Abrir na RoboCore](https://www.robocore.net/motor-caixas-de-reducao/micro-motor-com-caixa-de-reducao-6v-100rpm) |
| 3 | StickyMAX - Roda S20 Macia (Silicone vulcanizado c/ cubo 3mm) | 4 | R$ 39,90 | R$ 159,60 | [Abrir na RoboCore](https://www.robocore.net/roda/roda-stickymax-s20-22mm) |
| 4 | Suporte para Micro Motores (Par Branco) | 2 pares (4 un) | R$ 9,90 | R$ 19,80 | [Abrir na RoboCore](https://www.robocore.net/item-mecanico/suporte-para-micro-motores) |
| 5 | Módulo Driver Ponte H - L298N (Driver 1: Motores Esq.) | 1 | R$ 14,90 | R$ 14,90 | [Abrir na RoboCore](https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n) |
| 6 | Módulo Driver Ponte H - L298N (Driver 2: Motores Dir.) | 1 | R$ 14,90 | R$ 14,90 | [Abrir na RoboCore](https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n) |
| 7 | Conversor DC/DC Step Down Mini 560 5V (até 5A síncrono) | 1 | R$ 7,50 | R$ 7,50 | [Abrir na RoboCore](https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v) |
| 8 | Pack Bateria Li-Ion 7,4V 2500mAh c/ BMS Integrado | 1 | R$ 69,90 | R$ 69,90 | [Abrir na RoboCore](https://www.robocore.net/baterias-fontes/pack-bateria-li-ion-7_4v-2500mah-com-bms) |
| 9 | Cabo JST-RCY 2 pinos Fêmea (Rabicho p/ Bateria) | 1 | R$ 1,90 | R$ 1,90 | [Abrir na RoboCore](https://www.robocore.net/cabo/cabo-jst-rcy-2-pinos-femea) |
| 10 | Módulo Buzzer 5V Passivo (Suporta PWM/Tons) | 1 | R$ 4,90 | R$ 4,90 | [Abrir na RoboCore](https://www.robocore.net/atuador/modulo-buzzer-5v-passivo) |
| 11 | Módulo WS2812 LED RGB Endereçável (Barra 8 LEDs) | 1 | R$ 9,90 | R$ 9,90 | [Abrir na RoboCore](https://www.robocore.net/led/modulo-ws2812-led-enderecavel-8-leds) |
| 12 | Chave Gangorra KCD1-101 2T (Liga/Desliga) | 1 | R$ 1,50 | R$ 1,50 | [Abrir na RoboCore](https://www.robocore.net/botao-chave/chave-gangorra-kcd1-101-2t) |
| 13 | Jumpers Fêmea-Fêmea x40 Unidades | 1 | R$ 6,90 | R$ 6,90 | [Abrir na RoboCore](https://www.robocore.net/cabo/jumpers-femea-femea-x40-unidades) |
| 14 | Jumpers Macho-Macho x40 Cabos | 1 | R$ 7,90 | R$ 7,90 | [Abrir na RoboCore](https://www.robocore.net/cabo/jumpers-macho-macho-x40-cabos) |
| 15 | Placa Arduino Nano V3 + Cabo USB | 1 | R$ 28,90 | R$ 28,90 | [Abrir na RoboCore](https://www.robocore.net/placa-arduino/placa-nano-v3-com-cabo-usb-para-arduino) |

### 💰 Totais RoboCore (Itens 1 a 15):
* **Subtotal dos Produtos:** R$ 495,44
* **Total com Desconto no PIX (5% off):** **`R$ 470,67`**
* **Total no Cartão de Crédito:** **`R$ 495,44`** (em até **3x de R$ 165,15 sem juros**)

---

## 2. Mercado Livre (ESP32-S3 CAM, Cartão MicroSD & Giroscópio VR)

| Item | Componente | Produto | Qtd | Preço Estimado | Link Direto do Produto |
|:---:|---|---|:---:|:---:|---|
| 16 | **Cérebro Wi-Fi + Câmera** | Placa ESP32-S3 CAM N16R8 (16MB Flash, 8MB PSRAM) + Câmera OV5640 5MP | 1 | R$ 119,00 | [Abrir Produto no ML](https://www.mercadolivre.com.br/p/MLB2061307865?matt_tool=38524122&pdp_filters=item_id:MLB5139266661) |
| 17 | **Armazenamento Local** | Cartão MicroSD 32GB SanDisk Ultra A1 (FAT32 p/ ESP32-CAM) | 1 | R$ 49,90 | [Abrir Produto no ML](https://www.mercadolivre.com.br/cartao-de-memoria-micro-sd-sandisk-ultra-32gb-120mbs-c10-a1/p/MLB20654826) |
| 18 | **Giroscópio / VR (Head Tracking)** | Módulo GY-521 MPU-6050 (Acelerômetro + Giroscópio 6DOF) | 1 | R$ 19,90 | [Abrir Produto no ML](https://www.mercadolivre.com.br/modulo-acelerometro-giroscopio-mpu6050-gy521/up/MLBU4448831937) |

* **Subtotal Mercado Livre (Itens 16 a 18):** R$ 188,80

---

## 💵 Custo Total Geral Estimado (Linha ESP32-S3 CAM)

* **Total Geral com RoboCore no PIX (-5%) + Mercado Livre:** **`R$ 659,47`**
* **Total Geral no Cartão de Crédito (3x sem juros na RoboCore) + Mercado Livre:** **`R$ 684,24`**
