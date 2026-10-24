#pragma once
// ====================================================================================
// ESP32: REDE (STA com fallback para AP) + mDNS
// ====================================================================================
// Credenciais ficam em credenciais.h (NAO versionado, ver .gitignore). Modelo: credenciais.exemplo.h
// Sem credenciais ou sem rede: sobe o proprio AP "Rover-POCn" (senha 12345678) em 192.168.4.1.
// So um modo de radio fica ativo (STA ou AP): menos tempo de radio no ar = menos calor.
// ====================================================================================
#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include "esp_config.h"

#if __has_include("credenciais.h")
  #include "credenciais.h"
#else
  #define WIFI_SSID ""
  #define WIFI_PASS ""
#endif

static String redeEndereco = "";

static void redeIniciar(const char *apSsid) {
  WiFi.persistent(false);
  bool sta = false;
  if (strlen(WIFI_SSID) > 0) {
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    uint32_t t0 = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - t0 < 8000) delay(100);
    sta = WiFi.status() == WL_CONNECTED;
  }
  if (!sta) {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(apSsid, "12345678");
    redeEndereco = WiFi.softAPIP().toString();
  } else {
    redeEndereco = WiFi.localIP().toString();
  }
  WiFi.setSleep(false);
  WiFi.setTxPower(REDE_TX_POWER);
  if (MDNS.begin("rover")) MDNS.addService("http", "tcp", 80);
  Serial.printf("[REDE] %s  http://%s/  (ou http://rover.local/)\n", sta ? "STA" : "AP", redeEndereco.c_str());
}
