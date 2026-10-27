// ====================================================================================
// ROVER - FIRMWARE INTEGRADO DE TESTES DE BANCADA (ESP32-S3)
// ====================================================================================
// Roda no ESP32-S3-CAM com todos os subsistemas ativos:
// - Porta 80: Painel Web com diagnostico de LED D13, Pan/Tilt, Motores 4WD e Ping
// - Porta 81: WebSocket em tempo real
// - Porta 82: Stream MJPEG da camera OV5640 com gestao de calor
// ====================================================================================
#define POC_NOME   "testes_bancada"
#define POC_AP     "Rover-Bancada"
#define POC_CAM    1
#define POC_SERVO  1
#define POC_MOTOR  1
#include "esp_app.h"
