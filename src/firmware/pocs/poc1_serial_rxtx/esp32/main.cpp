// ====================================================================================
// POC 1 - ESP32: CONTROLE DO LED DO NANO VIA SERIAL (IO43 TX -> BC337 -> NANO D2)
// ====================================================================================
#include <Arduino.h>
#include <WebServer.h>
#include <driver/gpio.h>
#include "esp_config.h"
#include "esp_rede.h"

static WebServer web(80);
static uint32_t comandosEnviados = 0;
static String ultimoComando = "Nenhum";

static void enviarQuadroNano(const char *quadro) {
  Serial2.println(quadro);
  comandosEnviados++;
  ultimoComando = String(quadro);
  Serial.printf("[TX -> Nano] %s (total: %lu)\n", quadro, (unsigned long)comandosEnviados);
}

static const char PAGINA[] PROGMEM = R"HTML(<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>POC 1 - Controle LED Nano</title><style>
:root{--bg:#07080b;--p:#10131a;--b:#232833;--t:#d7dde8;--a:#5fd38d;--e:#ef6b6b;--w:#e6b450}
body{background:var(--bg);color:var(--t);font:14px ui-monospace,Consolas,monospace;max-width:540px;margin:auto;padding:16px}
h1{font-size:16px;margin-bottom:12px;letter-spacing:.5px}
.box{background:var(--p);border:1px solid var(--b);border-radius:6px;padding:16px;margin-bottom:12px}
.row{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}
button{flex:1;min-width:130px;background:#1a1f29;color:var(--t);border:1px solid #2d3441;border-radius:4px;padding:14px;font:inherit;font-weight:700;cursor:pointer}
button:active{opacity:0.8}
button.on{background:#1f3a2b;border-color:#2b5a40;color:var(--a)}
button.off{background:#3a1f1f;border-color:#5a2b2b;color:var(--e)}
button.blink{background:#3a321f;border-color:#5a4d2b;color:var(--w)}
.stat{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--b)}
.stat:last-child{border-bottom:none}
.stat span{color:#7d8798}
.stat b{color:var(--a)}
</style></head><body>
<h1>⚡ POC 1 &mdash; Controle de LED via BC337</h1>
<div class="box">
 <div><b>Comandar pino D13 do Arduino Nano:</b></div>
 <div class="row">
  <button class="on" onclick="cmd(1)">💡 LIGAR LED</button>
  <button class="off" onclick="cmd(0)">⚫ DESLIGAR LED</button>
 </div>
 <div class="row">
  <button class="blink" onclick="cmd(2)">✨ PISCAR 5 VEZES</button>
 </div>
</div>
<div class="box">
 <div class="stat"><span>Canal TX:</span><b>ESP32 IO43 &rarr; BC337 &rarr; Nano D2</b></div>
 <div class="stat"><span>Baud Rate:</span><b>9600 baud</b></div>
 <div class="stat"><span>Comandos Enviados:</span><b id="tot">0</b></div>
 <div class="stat"><span>Último Quadro:</span><b id="ult">-</b></div>
</div>
<script>
async function cmd(v){
  const r = await fetch('/api/led?v='+v);
  const j = await r.json();
  document.getElementById('tot').textContent = j.tot;
  document.getElementById('ult').textContent = j.ult;
}
</script>
</body></html>)HTML";

void setup() {
  logIniciar();
  Serial.println("\n== POC1 ESP: Controle LED Nano ==");

  // UART2 no ESP32: IO43 TX, IO44 RX a 9600 baud, invertido (true)
  // Como o BC337 inverte o sinal, invertendo aqui no ESP32 o sinal chega normal no D0 do Nano!
  Serial2.begin(9600, SERIAL_8N1, 44, 43, true);

  redeIniciar("Rover-POC1");

  web.on("/", []() { web.send_P(200, "text/html; charset=utf-8", PAGINA); });
  web.on("/api/led", []() {
    int v = web.arg("v").toInt();
    if (v == 1)      enviarQuadroNano("<L,1>");
    else if (v == 2) enviarQuadroNano("<L,2>");
    else             enviarQuadroNano("<L,0>");
    
    String json = "{\"ok\":true,\"tot\":" + String(comandosEnviados) + ",\"ult\":\"" + ultimoComando + "\"}";
    web.send(200, "application/json", json);
  });
  
  web.begin();
  Serial.println("[PRONTO] Acesse o painel para controlar o LED do Nano");
}

void loop() {
  web.handleClient();
}
