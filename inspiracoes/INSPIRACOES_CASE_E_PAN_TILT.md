# 🎨 Inspirações de Cases & Mecanismos Pan/Tilt para ESP32-S3-CAM / WROOM

Compilado de referências, links, modelos 3D e padrões de design encontrados na comunidade (Printables, Thingiverse, MakerWorld e GrabCAD) para guiar a modelagem do nosso case em 3D.

---

## 📸 1. Padrões de Cases para Placas ESP32-S3-CAM / WROOM

As placas com ESP32-S3-WROOM (como a Freenove N16R8 do Mercado Livre) possuem formato retangular com a lente da câmera no topo e portas USB-C na base. Os cases mais bem-sucedidos na comunidade seguem três abordagens:

### A. Case Bipartido "Snap-Fit" (Encaixe por Pressão)
* **Como funciona:** Duas metades (frente e traseira) que se encaixam sob pressão com pequenas travas nos cantos, dispensando parafusos finos.
* **Aberturas:**
  * Furo circular ou quadrado frontal de 8.5mm a 10mm para a lente OV5640/OV2640.
  * Abertura inferior para o conector USB-C (permite carregar/gravar sem desmontar).
  * Fendas ou ranhuras traseiras para ventilação (o ESP32-S3 dissipa calor durante streaming de vídeo).
* **Referência na comunidade:** *ESP32-S3 CAM Case SnapFit* no Printables.

### B. Case com Parafusos M2 / M2.5 e Acesso aos GPIOs
* **Como funciona:** O case fecha com 4 parafusos rosqueados diretamente no plástico ou em insertos de latão (heat-set inserts).
* **Vantagem para robótica:** Deixa aberturas laterais para passagem dos cabos dos sensores e alimentação (5V e GND).
* **Referência:** Modelos criados por *SouthernKY3D* no MakerWorld e Printables para as placas Freenove ESP32-S3-WROOM.

### C. Case Integrado com Suporte de Servo Horn (Cruzeta do SG90)
* **Como funciona:** A tampa traseira ou lateral do próprio case da câmera já possui em relevo o encaixe exato da cruzeta plástica (braço do servo SG90).
* **Vantagem brutal:** Dispensa adaptadores adicionais. O próprio case da câmera já é o elemento móvel do eixo de inclinação (Tilt).

---

## 🔄 2. Mecanismos Pan/Tilt de 2 Eixos com Servos SG90

Para movimentar a câmera em Pan (horizontal 180°) e Tilt (vertical), os designs mais populares são:

### 1. Sistema "Mini Pan-Tilt" Clássico Adaptado
* **Base (Pan):** Um servo SG90 fica em pé, fixo na estrutura do chassi. Uma cruzeta rotaciona uma plataforma em "U".
* **Braço (Tilt):** O segundo servo SG90 fica deitado horizontalmente dentro do "U". A cruzeta dele segura o berço onde a câmera é montada.
* **Projetos de Referência:**
  * **ESP32CAMBOX (Printables):** Ecossistema modular com suportes para servos SG90 e braços articulados.
  * **ESP32-CAM Pan & Tilt (Random Nerd Tutorials / Thingiverse):** O projeto mais replicado do mundo maker para visão com micro servos.

### 2. Berço Monobloco com Berço para LEDs
* **Como funciona:** Um berço frontal que segura a placa ESP32-S3 e, logo abaixo (ou acima) da lente, possui um rebaixo retangular para colar ou parafusar a barra de 8 LEDs WS2812B.
* **Vantagem:** O feixe de luz dos LEDs vira junto com a câmera, iluminando exatamente onde a lente está apontando.

---

## 🔗 3. Links e Modelos para Download / Consulta

| Projeto / Referência | Plataforma | Link Direto / Busca |
|---|---|---|
| **ESP32-S3 CAM Case SnapFit** | Printables | [printables.com/model/499645-esp32-s3-cam-case](https://www.printables.com/model/499645-esp32-s3-cam-case) |
| **Freenove ESP32-S3 WROOM Camera Case** | Printables | [printables.com/model/591632](https://www.printables.com/model/591632) |
| **Freenove ESP32-S3 WROOM Enclosure** | MakerWorld | [makerworld.com/en/models/185250](https://makerworld.com/en/models/185250) |
| **ESP32-CAM Pan-Tilt 2-Axis (SG90)** | Thingiverse | [thingiverse.com/thing:4375008](https://www.thingiverse.com/thing:4375008) |
| **ESP32-CAM Pan and Tilt Mount** | Printables | [printables.com/model/139045](https://www.printables.com/model/139045) |
| **Modelo 3D CAD ESP32-S3 WROOM** | GrabCAD | [grabcad.com/library/esp32-s3-wroom-1-cam-1](https://grabcad.com/library/esp32-s3-wroom-1-cam-1) |

---

## 💡 4. Diretrizes para o Nosso Chassi / Case

Com base nas melhores práticas encontradas nesses projetos:

1. **Dimensões e Folgas:** Dar folga de **0.3mm a 0.4mm** nas paredes internas do case para a placa ESP32-S3 entrar suavemente sem forçar os componentes SMD.
2. **Ventilação:** Adicionar fendas na parte traseira do case da câmera, pois o chip ESP32-S3 esquenta bastante processando MJPEG em tempo real.
3. **Passagem de Cabos:** Deixar uma canaleta na base traseira do berço da câmera para os cabos de alimentação (5V, GND) e dados dos LEDs descerem sem dobrar o servo.
4. **Fixação dos Servos:** Alojamentos nos quais os micro servos SG90 encaixam justos com trava por pressão ou com parafusos autorroscantes M2 (que já acompanham os próprios servos).
