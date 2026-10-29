#include <Arduino.h>
#include <WebServer.h>
#include "esp_rede.h"
#include "../protocolo.h"

static WebServer web(80);
static uint32_t enviados = 0;

static const char PAGINA[] PROGMEM = R"HTML(<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rover — LED e motores D0</title>
<style>
body{background:#07080b;color:#d7dde8;font:16px system-ui;max-width:560px;margin:auto;padding:20px}
section{background:#10131a;padding:16px;border:1px solid #232833;border-radius:8px;margin:16px 0}
h1{font-size:21px}h2{font-size:17px}.botoes{display:flex;gap:8px;flex-wrap:wrap}
button{flex:1;min-width:130px;padding:16px;border:1px solid #3b4650;border-radius:6px;background:#1a1f29;color:#fff;font:inherit;cursor:pointer}
.stop{background:#7f2020;width:100%;margin-top:12px;font-weight:bold}small{color:#adb5c1}
#resultado{min-height:3em;overflow-wrap:anywhere}
</style></head><body>
<h1>LED D13 e motores</h1>
<p>Comando: ESP IO43 → BC337 → Nano D0. 9600 baud.</p>
<section><h2>LED do Nano</h2><div class="botoes">
<button onclick="enviar('led_ligar')">Ligar LED</button>
<button onclick="enviar('led_desligar')">Desligar LED</button>
<button onclick="enviar('led_piscar')">Piscar 5 vezes</button>
</div></section>
<section><h2>Motores — PWM 120</h2>
<p>Rodas suspensas. Cada toque produz um pulso de 1 segundo, encerrado pelo Nano.</p>
<div class="botoes"><button onclick="enviar('frente')">Frente · 1 segundo</button>
<button onclick="enviar('re')">Ré · 1 segundo</button></div>
<button class="stop" onclick="enviar('parar')">PARAR MOTORES</button>
</section>
<p id="resultado" role="status" aria-live="polite">Pronto para enviar comandos.</p>
<small>O enlace tem apenas ida. A resposta da página confirma o envio pelo ESP;
confirme a recepção olhando o D13 e as rodas.</small>
<script>
async function enviar(acao) {
  const el = document.getElementById('resultado');
  const abortar = new AbortController();
  const tempo = setTimeout(() => abortar.abort(), 3000);
  el.textContent = 'Enviando…';
  try {
    const r = await fetch('/api/acao', {
      method: 'POST', body: new URLSearchParams({acao}), signal: abortar.signal
    });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const d = await r.json();
    el.textContent = 'Enviado pelo ESP: ' + d.quadro + '. Confirme no robô.';
  } catch (e) {
    el.textContent = 'Não foi possível confirmar o envio. O pulso, se recebido, termina no Nano em 1 segundo.';
  } finally { clearTimeout(tempo); }
}
function pararAoSair() {
  navigator.sendBeacon('/api/acao', new URLSearchParams({acao: 'parar'}));
}
window.addEventListener('pagehide', pararAoSair);
document.addEventListener('visibilitychange', () => { if (document.hidden) pararAoSair(); });
</script></body></html>)HTML";

static void acaoWeb() {
  const String acao = web.arg("acao");
  ProtoFrame f = {};
  if (acao == "led_ligar" || acao == "led_desligar" || acao == "led_piscar") {
    f.cmd = 'L';
    f.n = 1;
    f.arg[0] = acao == "led_ligar" ? 1 : (acao == "led_piscar" ? 2 : 0);
  } else if (acao == "frente" || acao == "re") {
    f.cmd = 'M';
    f.n = 2;
    f.arg[0] = f.arg[1] = acao == "frente" ? TesteD0::PWM : -TesteD0::PWM;
  } else if (acao == "parar") {
    f.cmd = 'X';
  } else {
    web.send(400, "text/plain", "acao invalida");
    return;
  }
  if (!TesteD0::valido(f)) {
    web.send(400, "text/plain", "quadro invalido");
    return;
  }
  char quadro[44];
  protoFormatar(quadro, f.cmd, f.arg, f.n);
  Serial2.println(quadro);  // Mesmo envio do POC 1 que acendeu o D13.
  ++enviados;
  web.send(200, "application/json", String("{\"quadro\":\"") + quadro
           + "\",\"enviados\":" + String(enviados) + "}");
}

void setup() {
  logIniciar();
  // Copia exata da inicializacao que funcionou no POC 1:
  // TX invertido no ESP + inversao do BC337 = UART normal no D0 do Nano.
  Serial2.begin(TesteD0::BAUD, SERIAL_8N1, 44, 43, true);
  redeIniciar("Rover-LED-Motores");
  web.on("/", HTTP_GET, []() {
    web.sendHeader("Cache-Control", "no-store");
    web.send_P(200, "text/html; charset=utf-8", PAGINA);
  });
  web.on("/api/acao", HTTP_POST, acaoWeb);
  web.on("/api/info", HTTP_GET, []() {
    web.send(200, "application/json", String("{\"firmware\":\"led_motores_d0\",\"ip\":\"")
             + redeEndereco + "\",\"baud\":9600,\"nano_rx\":\"D0\",\"tx_invertido\":true,\"retorno\":false}");
  });
  web.onNotFound([]() { web.send(404, "text/plain", "rota inexistente"); });
  web.begin();
}

void loop() { web.handleClient(); }
