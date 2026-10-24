// POC 6 - ESP32: MOTORES CONTROLADOS PELO CELULAR (joystick / D-pad / teclado)
// Sem camera de proposito: isola o teste de tracao e o consumo. Ao perder o WebSocket envia <X> ao Nano.
// Nano: pio run -e poc6_nano -t upload
#define POC_NOME   "poc6_motores_controlado"
#define POC_AP     "Rover-POC6"
#define POC_MOTOR  1
#include "esp_app.h"
