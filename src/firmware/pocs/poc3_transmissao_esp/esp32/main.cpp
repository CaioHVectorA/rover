// POC 3 - ESP32: TRANSMISSAO DE VIDEO "FRIA" (ESP isolado, sem Nano)
// Painel + video em http://<ip>/  (video MJPEG na porta 82: http://<ip>:82/stream)
// Veja a tecnica de reducao de calor em src/firmware/comum/esp_camera_frio.h e docs/guides/camera_calor_software.md
#define POC_NOME   "poc3_transmissao_esp"
#define POC_AP     "Rover-POC3"
#define POC_CAM    1
#include "esp_app.h"
