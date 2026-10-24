// ====================================================================================
// POC 1 - ESP32: TESTE DE ENLACE RX/TX COM SERVIDOR WEB
// ====================================================================================
// Objetivo: provar o fio serial nos DOIS sentidos antes de ligar qualquer motor/servo.
//   ESP TX (IO43) -> Nano   : ping <P,n> / resposta <A,n>  => perda de pacotes e tempo de ida e volta
//   Nano TX (D1)  -> ESP RX (IO44, via divisor 1k/2k) : heartbeat <H,...> a 1 Hz (se chegar, o retorno funciona)
// Abra http://<ip>/  (ou http://rover.local/). Sem rede conhecida o ESP cria o AP "Rover-POC1" (192.168.4.1).
// Grave o Nano com:  pio run -e poc1_nano -t upload
// ====================================================================================
#include <Arduino.h>
#include <WebServer.h>
#include "esp_config.h"
#include "esp_rede.h"
#include "esp_enlace.h"

static EnlaceNano enlace;
static WebServer web(80);

static uint32_t testeRestantes = 0, testeIntervaloMs = 100, ultPing = 0;

static const char PAGINA[] PROGMEM = R"HTML(<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>POC1 enlace</title><style>
body{background:#07080b;color:#d7dde8;font:14px ui-monospace,Consolas,monospace;max-width:640px;margin:auto;padding:12px}
h1{font-size:15px;margin:6px 0 10px}button,input{background:#1a1f29;color:#d7dde8;border:1px solid #2d3441;border-radius:3px;padding:9px 12px;font:inherit;margin:3px 3px 3px 0}
button.p{background:#1f3a2b;border-color:#2b5a40;color:#5fd38d}.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:6px;margin:10px 0}
.k{border:1px solid #232833;padding:6px 8px;border-radius:3px}.k i{display:block;font-style:normal;color:#7d8798;font-size:10px;text-transform:uppercase;letter-spacing:1px}.k b{font-size:17px}
pre{border:1px solid #232833;padding:8px;min-height:120px;color:#9fb3c8;overflow:auto}.ok{color:#5fd38d}.bad{color:#ef6b6b}</style></head><body>
<h1>POC 1 &mdash; enlace serial ESP32 &#8596; Nano</h1>
<div><button class="p" onclick="a('/api/ping?n=1&hz=1')">Ping x1</button><button class="p" onclick="a('/api/ping?n=100&hz=10')">100 pings @10 Hz</button>
<button onclick="a('/api/ping?n=300&hz=30')">300 pings @30 Hz (estresse)</button><button onclick="a('/api/zero')">Zerar contadores</button></div>
<div><input id="f" value="&lt;S,900,900&gt;" size="18"><button onclick="a('/api/send?f='+encodeURIComponent(f.value))">Enviar quadro bruto</button></div>
<div class="g" id="g"></div><b>Ultimos quadros recebidos do Nano</b><pre id="log">-</pre>
<small style="color:#7d8798">Sentido ESP&rarr;Nano ok = acks voltando. Sentido Nano&rarr;ESP ok = heartbeat com idade &lt; 2 s. Reset do Nano: BROWN-OUT = queda de tensao.</small>
<script>
const f=document.getElementById('f');f.value='<S,900,900>';
const a=u=>fetch(u).then(r=>r.text()).then(s=>{if(s!=='ok')alert(s)});
const kv=(k,v,c)=>`<div class="k"><i>${k}</i><b class="${c||''}">${v}</b></div>`;
const RST=x=>x<0?'-':(x&4?'BROWN-OUT':x&8?'watchdog':x&1?'power-on':x&2?'externo':'?');
async function t(){try{const s=await (await fetch('/api/stats')).json();
 const perda=s.pings?((s.pings-s.acks)/s.pings*100):0, hb=s.hb_age;
 document.getElementById('g').innerHTML=kv('Pings enviados',s.pings)+kv('Acks recebidos',s.acks)+kv('Perda',perda.toFixed(1)+' %',perda>2?'bad':(s.pings?'ok':''))
 +kv('RTT ultimo',(s.rtt_ult/1000).toFixed(1)+' ms')+kv('RTT medio',(s.rtt_med/1000).toFixed(1)+' ms')+kv('RTT min / max',(s.rtt_min/1000).toFixed(1)+' / '+(s.rtt_max/1000).toFixed(1)+' ms')
 +kv('Nano -> ESP (heartbeat)',hb<0?'NADA':(hb<2500?'ok ('+hb+' ms)':'PARADO'),hb>=0&&hb<2500?'ok':'bad')+kv('Quadros TX / RX',s.tx+' / '+s.rx)+kv('Erros de quadro (ESP)',s.err)
 +kv('Nano: recebidos / erros',s.nano_rx+' / '+s.nano_err)+kv('Nano ligado ha',s.nano_up<0?'-':s.nano_up+' s')+kv('Ultimo reset do Nano',RST(s.reset),s.reset&4?'bad':'');
 document.getElementById('log').textContent=s.log.join('\n')||'-'}catch(e){}}
t();setInterval(t,500);</script></body></html>)HTML";

static void apiStats() {
  const EnlaceStats &e = enlace.st;
  uint32_t agora = millis();
  uint32_t hb = enlace.idadeHbMs(agora);
  String s = "{";
  s += "\"pings\":" + String(e.pings) + ",\"acks\":" + String(e.acks);
  s += ",\"rtt_ult\":" + String(e.rttUltUs) + ",\"rtt_med\":" + String(e.acks ? (uint32_t)(e.rttSomaUs / e.acks) : 0);
  s += ",\"rtt_min\":" + String(e.acks ? e.rttMinUs : 0) + ",\"rtt_max\":" + String(e.rttMaxUs);
  s += ",\"hb_age\":" + String(hb == 0xFFFFFFFF ? -1L : (long)hb);
  s += ",\"tx\":" + String(e.tx) + ",\"rx\":" + String(e.rx) + ",\"err\":" + String(e.rxErros);
  s += ",\"nano_rx\":" + String(e.nanoRx) + ",\"nano_err\":" + String(e.nanoErr) + ",\"nano_up\":" + String(e.nanoUp);
  s += ",\"reset\":" + String(e.resetFlags) + ",\"log\":[";
  bool primeiro = true;
  for (uint8_t i = 0; i < ENLACE_LOG_N; i++) {
    const String &l = enlace.logRx[(enlace.logPos + ENLACE_LOG_N - 1 - i) % ENLACE_LOG_N];   // mais novo primeiro
    if (l.length() == 0) continue;
    if (!primeiro) s += ",";
    primeiro = false;
    s += "\"" + l + "\"";
  }
  s += "]}";
  web.send(200, "application/json", s);
}

void setup() {
  logIniciar();
  setCpuFrequencyMhz(POC_CPU_MHZ);
  Serial.println("\n== POC1 ESP: teste de enlace ==");
  enlace.begin();
  redeIniciar("Rover-POC1");

  web.on("/", []() { web.send_P(200, "text/html; charset=utf-8", PAGINA); });
  web.on("/api/stats", apiStats);
  web.on("/api/zero", []() { enlace.zerarPing(); web.send(200, "text/plain", "ok"); });
  web.on("/api/ping", []() {
    enlace.zerarPing();
    testeRestantes = constrain(web.arg("n").toInt(), 1, 5000);
    int hz = constrain(web.arg("hz").toInt(), 1, 50);
    testeIntervaloMs = 1000 / hz;
    web.send(200, "text/plain", "ok");
  });
  web.on("/api/send", []() {
    String f = web.arg("f");
    ProtoParser p;
    ProtoFrame fr;
    bool ok = false;
    for (size_t i = 0; i < f.length(); i++) if (p.feed(f[i], fr)) ok = enlace.despachar(fr);
    web.send(ok ? 200 : 400, "text/plain", ok ? "ok" : "quadro invalido (use <P>, <S,p,t>, <M,e,d>, <X>, <C,id,v>)");
  });
  web.begin();
}

void loop() {
  uint32_t agora = millis();
  web.handleClient();
  enlace.loop(agora);
  if (testeRestantes > 0 && agora - ultPing >= testeIntervaloMs) {
    ultPing = agora;
    testeRestantes--;
    enlace.ping();
  }
}
