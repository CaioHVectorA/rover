/*
 * ====================================================================================
 * ROVER ESP32 - PAINEL WEB PARA CONTROLAR TODOS OS PINOS DO ARDUINO NANO
 * ====================================================================================
 * Sobe um servidor web. A página lista D2..D13 e A0..A7 e, para cada pino, permite
 * escolher o modo (saída, PWM, servo, entrada, pullup, leitura analógica).
 * Cada ação vira uma linha de texto enviada ao Nano pela serial (veja o protocolo em
 * nano_pinos_serial.ino) e a resposta do Nano aparece na página.
 *
 * Ligações (bancada, 1 USB no ESP):
 *   ESP 5V  -> Nano 5V      ESP GND -> Nano GND
 *   ESP IO43 (TX) -> Nano D2 (RX, SoftwareSerial 38400)
 *   ESP IO44 (RX) <- Nano D1 (TX) via divisor 1k/2k (opcional; sem ele não há respostas)
 *
 * Se não conectar no Wi-Fi configurado, cria o Wi-Fi próprio "Rover-Nano" (sem senha)
 * e a página fica em http://192.168.4.1
 * ====================================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <esp_wifi.h>

// Descomente só a placa que estiver usando
#define PLACA_ESP32_S3_CAM
// #define PLACA_ESP32_CAM_CLASSIC

#if defined(PLACA_ESP32_S3_CAM)
  #define PINO_TX_PARA_NANO 43
  #define PINO_RX_DO_NANO   44
  HardwareSerial SerialNano(1);
#else
  #define PINO_TX_PARA_NANO 1
  #define PINO_RX_DO_NANO   3
  #define SerialNano Serial
#endif

// Wi-Fi (rede aberta, igual ao teste anterior). Se a rede tiver senha, preencha.
const char *ssid = "Apple Network fdd7b9";
const char *senha = "";

WebServer server(80);

const char PAGINA_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel Nano</title>
<style>
  :root{--bg:#0f172a;--card:#1e293b;--pri:#38bdf8;--ok:#22c55e;--bad:#ef4444;--txt:#f8fafc;--sub:#94a3b8}
  *{box-sizing:border-box;font-family:system-ui,sans-serif}
  body{margin:0;padding:16px;background:var(--bg);color:var(--txt)}
  h1{font-size:1.3rem;color:var(--pri);margin:0 0 4px}
  .top{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
  #log{font:12px monospace;color:var(--sub);flex:1;min-width:200px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
  .pin{background:var(--card);border:1px solid #334155;border-radius:12px;padding:10px}
  .pin b{color:var(--pri)} select,button,input{font-size:.9rem}
  select{width:100%;margin:6px 0;background:#0f172a;color:var(--txt);border:1px solid #334155;border-radius:6px;padding:5px}
  button{border:0;border-radius:6px;padding:8px 10px;font-weight:700;cursor:pointer}
  .on{background:var(--ok)} .off{background:var(--bad);color:#fff} .neu{background:var(--pri);color:#082f49}
  .row{display:flex;gap:6px} .row button{flex:1}
  input[type=range]{width:100%} .val{font-family:monospace;color:var(--ok)}
</style></head><body>
<h1>🔌 Painel de pinos do Arduino Nano</h1>
<div class="top"><button class="neu" onclick="cmd('X')">Resetar todos (X)</button><span id="log">pronto</span></div>
<div class="grid" id="grid"></div>
<script>
const PWM=[3,5,6,9,10,11];
const pinos=[];
for(let i=2;i<=13;i++)pinos.push({n:i,nome:'D'+i,dig:true,pwm:PWM.includes(i)});
for(let i=0;i<=5;i++)pinos.push({n:14+i,nome:'A'+i,dig:true,pwm:false,an:i});
pinos.push({n:-1,nome:'A6',dig:false,pwm:false,an:6},{n:-1,nome:'A7',dig:false,pwm:false,an:7});

async function cmd(q){
  const log=document.getElementById('log');
  try{
    const r=await (await fetch('/c?q='+encodeURIComponent(q))).text();
    log.textContent=q+'  →  '+(r||'(sem resposta)');
    return r;
  }catch(e){log.textContent='erro de rede';return ''}
}
function modos(p){
  let o='<option value="">— modo —</option>';
  if(p.dig){o+='<option value="out">Saída digital</option><option value="in">Entrada</option><option value="pull">Entrada pull-up</option><option value="servo">Servo</option>';}
  if(p.pwm)o+='<option value="pwm">PWM</option>';
  if(p.an!==undefined)o+='<option value="ana">Leitura analógica</option>';
  return o;
}
function render(){
  const g=document.getElementById('grid');
  pinos.forEach((p,i)=>{
    const d=document.createElement('div');d.className='pin';
    d.innerHTML=`<b>${p.nome}</b>${p.n>=0?' <small>(pino '+p.n+')</small>':''}
      <select onchange="setModo(${i},this.value)">${modos(p)}</select><div id="c${i}"></div>`;
    g.appendChild(d);
  });
}
function setModo(i,m){
  const p=pinos[i],c=document.getElementById('c'+i);
  if(m==='out'){cmd(`M ${p.n} 1`);
    c.innerHTML=`<div class="row"><button class="on" onclick="cmd('W ${p.n} 1')">HIGH</button><button class="off" onclick="cmd('W ${p.n} 0')">LOW</button></div>`;}
  else if(m==='pwm'){cmd(`M ${p.n} 1`);
    c.innerHTML=`<input type="range" min="0" max="255" value="0" oninput="this.nextElementSibling.textContent=this.value" onchange="cmd('P ${p.n} '+this.value)"><span class="val">0</span>`;}
  else if(m==='servo'){
    c.innerHTML=`<input type="range" min="0" max="180" value="90" oninput="this.nextElementSibling.textContent=this.value+'°'" onchange="cmd('S ${p.n} '+this.value)"><span class="val">90°</span>`;}
  else if(m==='in'||m==='pull'){cmd(`M ${p.n} ${m==='pull'?2:0}`);
    c.innerHTML=`<button class="neu" onclick="ler(${i},'D ${p.n}')">Ler</button> <span class="val" id="v${i}">-</span>`;}
  else if(m==='ana'){
    c.innerHTML=`<button class="neu" onclick="ler(${i},'A ${p.an}')">Ler</button> <span class="val" id="v${i}">-</span>`;}
  else c.innerHTML='';
}
async function ler(i,q){
  const r=await cmd(q);
  document.getElementById('v'+i).textContent=r.trim().split(' ').pop()||'-';
}
render();
</script></body></html>
)rawliteral";

void handleRoot() {
  server.send_P(200, "text/html", PAGINA_HTML);
}

// Envia uma linha ao Nano e devolve a linha de resposta (ou "" se não houver)
String enviaAoNano(const String &linha) {
  while (SerialNano.available()) SerialNano.read();   // limpa lixo antigo
  SerialNano.print(linha);
  SerialNano.print('\n');

  String resp = "";
  unsigned long ini = millis();
  while (millis() - ini < 200) {
    while (SerialNano.available()) {
      char c = SerialNano.read();
      if (c == '\n') { resp.trim(); return resp; }
      if (c != '\r') resp += c;
    }
  }
  resp.trim();
  return resp;
}

void handleComando() {
  if (!server.hasArg("q")) {
    server.send(400, "text/plain", "falta q");
    return;
  }
  String q = server.arg("q");
  if (q.length() > 24) {
    server.send(400, "text/plain", "ERR");
    return;
  }
  String resp = enviaAoNano(q);
  Serial.println("[ESP->NANO] " + q + "  [NANO] " + resp);
  server.send(200, "text/plain", resp);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

#if defined(PLACA_ESP32_S3_CAM)
  SerialNano.begin(38400, SERIAL_8N1, PINO_RX_DO_NANO, PINO_TX_PARA_NANO);
#else
  SerialNano.begin(38400);
#endif

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, senha);
  Serial.print("[WI-FI] Conectando em ");
  Serial.println(ssid);
  for (int i = 0; i < 30 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("\n[WI-FI] Acesse: http://");
    Serial.println(WiFi.localIP());
    if (MDNS.begin("rover")) Serial.println("[mDNS] ou http://rover.local");
  } else {
    WiFi.mode(WIFI_AP);
    WiFi.softAP("Rover-Nano");
    Serial.print("\n[WI-FI] Falhou. AP 'Rover-Nano' criado: http://");
    Serial.println(WiFi.softAPIP());
  }
  esp_wifi_set_ps(WIFI_PS_NONE);

  server.on("/", HTTP_GET, handleRoot);
  server.on("/c", HTTP_GET, handleComando);
  server.begin();
  Serial.println("[HTTP] Servidor ativo");
}

void loop() {
  server.handleClient();
}
