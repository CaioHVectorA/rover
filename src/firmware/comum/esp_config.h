#pragma once
// ====================================================================================
// ESP32-S3-CAM: PINOS E CONSTANTES GLOBAIS (comum a todos os POCs)
// ====================================================================================
#include <Arduino.h>

// ---- Enlace com o Nano (UART1 remapeada em IO43/IO44) ----
#define PIN_LINK_TX   43     // -> (BC337 inversor) -> Nano D2   |  modo LINK_HW: direto no Nano D0
#define PIN_LINK_RX   44     // <- (divisor 1k/2k) <- Nano D1 TX
#ifndef LINK_BAUD
#define LINK_BAUD     9600
#endif
#define LINK_INTERVALO_MS 30     // intervalo minimo entre quadros de servo / de motor (ultimo valor vence)

// ---- Camera OV5640/OV2640 (ESP32-S3-CAM N16R8, mesma pinagem validada no gateway anterior) ----
#define CAM_PWDN   -1
#define CAM_RESET  -1
#define CAM_XCLK   15
#define CAM_SIOD    4
#define CAM_SIOC    5
#define CAM_Y9     16
#define CAM_Y8     17
#define CAM_Y7     18
#define CAM_Y6     12
#define CAM_Y5     10
#define CAM_Y4      8
#define CAM_Y3      9
#define CAM_Y2     11
#define CAM_VSYNC   6
#define CAM_HREF    7
#define CAM_PCLK   13

// ---- Calor da propria placa ----
#ifndef POC_CPU_MHZ
#define POC_CPU_MHZ 160      // 240 -> 160 MHz: menos calor, sobra CPU (o JPEG e feito pelo sensor)
#endif
#ifndef REDE_TX_POWER
#define REDE_TX_POWER WIFI_POWER_15dBm   // padrao 19,5 dBm; 15 dBm basta em casa e esquenta menos
#endif

// Serial (USB CDC) sem travar quando nao ha monitor aberto.
static inline void logIniciar() {
  Serial.begin(115200);
#if ARDUINO_USB_CDC_ON_BOOT
  Serial.setTxTimeoutMs(0);
#endif
}
