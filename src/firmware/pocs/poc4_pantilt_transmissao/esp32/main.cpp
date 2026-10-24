// POC 4 - ESP32: PAN/TILT + TRANSMISSAO (configuravel, com metricas de desempenho da imagem)
// Painel unico: video + metricas + presets + Pan/Tilt. O modo ECO (poucos quadros) entra apos 8 s sem comandos.
// Nano: o mesmo do POC 2  ->  pio run -e poc2_nano -t upload
#define POC_NOME        "poc4_pantilt_transmissao"
#define POC_AP          "Rover-POC4"
#define POC_CAM         1
#define POC_SERVO       1
#define POC_ECO_APOS_S  8
#include "esp_app.h"
