// POC 2 - ESP32: PAN/TILT CONTROLADO PELO CELULAR (sem video)
// Painel em http://<ip>/ : sliders Pan/Tilt, teste de varredura lenta (anti-rebolado) e ajuste fino.
// Grave o Nano com: pio run -e poc2_nano -t upload   (ou poc2_nano_hw, ver docs/pocs/poc2_pantilt_controlado.md)
#define POC_NOME   "poc2_pantilt_controlado"
#define POC_AP     "Rover-POC2"
#define POC_SERVO  1
#include "esp_app.h"
