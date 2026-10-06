#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

const char* ssid     = "PET_ELETRICA";
const char* password = "1478965P";

WebServer server(80);

const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>Rover Pan-Tilt Controller</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --accent: #00e676;
      --accent-blue: #29b6f6;
      --text: #f0f6fc;
      --text-sub: #8b949e;
      --border: #30363d;
      --danger: #ff5252;
      --warning: #ffa726;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 15px; display: flex; justify-content: center; min-height: 100vh; }
    .container { width: 100%; max-width: 440px; display: flex; flex-direction: column; gap: 15px; }

    .header { text-align: center; padding: 10px 0; }
    .header h1 { font-size: 1.4rem; font-weight: 700; color: var(--text); }
    .header p { font-size: 0.8rem; color: var(--text-sub); margin-top: 4px; }

    /* Tabs */
    .tabs { display: flex; background: #21262d; padding: 4px; border-radius: 10px; gap: 4px; }
    .tab-btn { flex: 1; padding: 10px; border: none; background: transparent; color: var(--text-sub); font-size: 0.9rem; font-weight: 600; border-radius: 8px; cursor: pointer; transition: 0.2s; }
    .tab-btn.active { background: var(--card-bg); color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.4); }

    /* Cards */
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 18px; display: flex; flex-direction: column; gap: 15px; }
    .tab-content { display: none; }
    .tab-content.active { display: flex; flex-direction: column; gap: 15px; }

    /* Values Display */
    .angle-display { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .angle-box { background: #0d1117; border: 1px solid var(--border); border-radius: 10px; padding: 12px; text-align: center; }
    .angle-title { font-size: 0.75rem; font-weight: 600; color: var(--text-sub); text-transform: uppercase; }
    .angle-val { font-size: 2.2rem; font-weight: 800; color: var(--accent); margin-top: 2px; }
    .angle-val span { font-size: 1rem; color: var(--text-sub); font-weight: 400; }

    /* Controls */
    .control-group { display: flex; flex-direction: column; gap: 6px; }
    .control-header { display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; color: var(--text-sub); }
    .control-header span.val-label { color: var(--accent-blue); }

    input[type=range] {
      -webkit-appearance: none; width: 100%; height: 8px; background: #21262d; border-radius: 4px; outline: none;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%; background: var(--accent-blue); cursor: pointer; border: 2px solid #fff; box-shadow: 0 0 10px rgba(41, 182, 246, 0.5);
    }

    /* Buttons */
    .btn { width: 100%; padding: 12px; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 700; cursor: pointer; transition: 0.15s active; display: flex; align-items: center; justify-content: center; gap: 8px; }
    .btn-primary { background: var(--accent-blue); color: #000; }
    .btn-success { background: var(--accent); color: #000; }
    .btn-danger { background: var(--danger); color: #fff; }
    .btn-secondary { background: #21262d; color: var(--text); border: 1px solid var(--border); }
    .btn:active { transform: scale(0.98); opacity: 0.9; }

    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

    /* Status Badge */
    .badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; justify-content: center; }
    .badge-off { background: #21262d; color: var(--text-sub); }
    .badge-on { background: rgba(0,230,118,0.15); color: var(--accent); border: 1px solid rgba(0,230,118,0.3); }
    .badge-warn { background: rgba(255,167,38,0.15); color: var(--warning); border: 1px solid rgba(255,167,38,0.3); }

    /* Diagnostic Console */
    .console { background: #080b0f; border: 1px solid var(--border); border-radius: 8px; padding: 10px; font-family: monospace; font-size: 0.72rem; color: #8b949e; max-height: 100px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
    .console-line { word-break: break-all; }
    .console-line.info { color: var(--accent-blue); }
    .console-line.warn { color: var(--warning); }
    .console-line.err { color: var(--danger); }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Rover Pan-Tilt</h1>
      <p>Controle de Câmera & Estabilização</p>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('manual')">🕹️ Manual</button>
      <button class="tab-btn" onclick="switchTab('gyro')">📱 Giroscópio</button>
    </div>

    <!-- MAIN DISPLAY -->
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:0.85rem; font-weight:600; color:var(--text-sub);">Posição Atual TX</span>
        <div id="badgeStatus" class="badge badge-off">PRONTO</div>
      </div>

      <div class="angle-display">
        <div class="angle-box">
          <div class="angle-title">PAN (Horizontal)</div>
          <div class="angle-val"><span id="txtPan">90</span><span>°</span></div>
        </div>
        <div class="angle-box">
          <div class="angle-title">TILT (Vertical)</div>
          <div class="angle-val"><span id="txtTilt">90</span><span>°</span></div>
        </div>
      </div>
    </div>

    <!-- TAB 1: MANUAL CONTROL -->
    <div id="tabManual" class="card tab-content active">
      <div class="control-group">
        <div class="control-header">
          <span>PAN (0° - 180°)</span>
          <span class="val-label" id="lblManualPan">90°</span>
        </div>
        <input type="range" id="rngPan" min="0" max="180" value="90" oninput="onManualInput()">
      </div>

      <div class="control-group">
        <div class="control-header">
          <span>TILT (0° - 180°)</span>
          <span class="val-label" id="lblManualTilt">90°</span>
        </div>
        <input type="range" id="rngTilt" min="0" max="180" value="90" oninput="onManualInput()">
      </div>

      <div class="grid-2">
        <button class="btn btn-secondary" onclick="setPreset(90, 90)">🎯 Centralizar (90, 90)</button>
        <button class="btn btn-secondary" onclick="setPreset(0, 90)">◀ Esquerda</button>
        <button class="btn btn-secondary" onclick="setPreset(180, 90)">▶ Direita</button>
        <button class="btn btn-secondary" onclick="setPreset(90, 140)">▲ Cima</button>
      </div>
    </div>

    <!-- TAB 2: GYROSCOPE CONTROL -->
    <div id="tabGyro" class="card tab-content">
      <button id="btnAtivarGyro" class="btn btn-primary" onclick="toggleGyro()">⚡ Ativar Giroscópio do Celular</button>
      
      <div class="grid-2">
        <button id="btnCalib" class="btn btn-secondary" onclick="calibrarCentro()" disabled>🎯 Recalibrar Centro</button>
        <button class="btn btn-secondary" onclick="setPreset(90, 90)">Reset 90°</button>
      </div>

      <div class="control-group">
        <div class="control-header">
          <span>Sensibilidade do Giroscópio</span>
          <span class="val-label" id="lblSens">1.5x</span>
        </div>
        <input type="range" id="rngSens" min="0.5" max="3.0" step="0.1" value="1.5" oninput="document.getElementById('lblSens').innerText = this.value + 'x'">
      </div>

      <div class="control-group">
        <div class="control-header">
          <span>Intervalo de Envio (ms)</span>
          <span class="val-label" id="lblRate">80 ms</span>
        </div>
        <input type="range" id="rngRate" min="40" max="300" step="10" value="80" oninput="document.getElementById('lblRate').innerText = this.value + ' ms'">
      </div>

      <div style="font-size:0.75rem; color:var(--text-sub); background:#0d1117; padding:8px; border-radius:6px; border:1px solid var(--border);">
        <b>Sensores do Celular:</b><br>
        Gamma (Inclin. Lat.): <span id="rawGamma">0</span>° | Beta (Frente/Trás): <span id="rawBeta">0</span>°
      </div>
    </div>

    <!-- DIAGNOSTIC CONSOLE -->
    <div class="card">
      <div style="font-size:0.8rem; font-weight:600; color:var(--text-sub);">Log de Transmissão (TX)</div>
      <div class="console" id="logConsole">
        <div class="console-line info">Sistema inicializado. Escolha o modo de controle.</div>
      </div>
    </div>
  </div>

  <script>
    let panAtual = 90, tiltAtual = 90;
    let gyroAtivo = false;
    let enviando = false;
    let ultimoEnvio = 0;
    
    // Referencias de Calibracao do Giroscopio
    let refGamma = 0, refBeta = 0;
    let rawG = 0, rawB = 0;

    function log(msg, type = '') {
      const c = document.getElementById('logConsole');
      const div = document.createElement('div');
      div.className = 'console-line ' + type;
      const time = new Date().toLocaleTimeString().split(' ')[0];
      div.innerText = `[${time}] ${msg}`;
      c.appendChild(div);
      c.scrollTop = c.scrollHeight;
      if (c.children.length > 20) c.removeChild(c.children[0]);
    }

    function switchTab(tab) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      if (tab === 'manual') {
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        document.getElementById('tabManual').classList.add('active');
      } else {
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        document.getElementById('tabGyro').classList.add('active');
      }
    }

    // --- CONTROLE MANUAL ---
    function onManualInput() {
      const p = parseInt(document.getElementById('rngPan').value);
      const t = parseInt(document.getElementById('rngTilt').value);
      document.getElementById('lblManualPan').innerText = p + '°';
      document.getElementById('lblManualTilt').innerText = t + '°';
      solicitarEnvio(p, t);
    }

    function setPreset(p, t) {
      document.getElementById('rngPan').value = p;
      document.getElementById('rngTilt').value = t;
      document.getElementById('lblManualPan').innerText = p + '°';
      document.getElementById('lblManualTilt').innerText = t + '°';
      solicitarEnvio(p, t);
    }

    // --- TRANSMISSAO HTTP PARA ESP32 ---
    function solicitarEnvio(p, t, force = false) {
      panAtual = p;
      tiltAtual = t;
      document.getElementById('txtPan').innerText = p;
      document.getElementById('txtTilt').innerText = t;

      const agora = Date.now();
      const minIntervalo = parseInt(document.getElementById('rngRate')?.value || 80);

      if (!force && (agora - ultimoEnvio < minIntervalo)) return;
      if (enviando) return;

      enviando = true;
      ultimoEnvio = agora;

      fetch(`/set?p=${p}&t=${t}`)
        .then(res => {
          if (res.ok) {
            document.getElementById('badgeStatus').className = "badge badge-on";
            document.getElementById('badgeStatus').innerText = "ENVIADO TX";
          } else {
            log('Erro HTTP: ' + res.status, 'err');
          }
        })
        .catch(err => {
          log('Erro Conexao: ' + err.message, 'err');
        })
        .finally(() => {
          enviando = false;
        });
    }

    // --- CONTROLE POR GIROSCÓPIO ---
    function toggleGyro() {
      if (!gyroAtivo) {
        solicitarPermissaoGyro();
      } else {
        pararGyro();
      }
    }

    function solicitarPermissaoGyro() {
      // 1. iOS (Safari) que requer requestPermission
      if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
        log('Solicitando permissão de orientação (iOS)...', 'info');
        DeviceOrientationEvent.requestPermission()
          .then(res => {
            if (res === 'granted') {
              iniciarGyro();
            } else {
              log('Permissão negada no iOS.', 'err');
              alert('Permissão para sensores negada no iOS.');
            }
          })
          .catch(err => {
            log('Erro no iOS: ' + err, 'err');
            iniciarGyro(); // Tenta iniciar de qualquer forma
          });
        return;
      }

      // 2. Verificação de Suporte ou Origem Não Segura (HTTP em IP local)
      const temOrientation = ('ondeviceorientation' in window) || (typeof window.DeviceOrientationEvent !== 'undefined');
      const temMotion = ('ondevicemotion' in window) || (typeof window.DeviceMotionEvent !== 'undefined');

      if (temOrientation || temMotion) {
        log('Iniciando escuta dos sensores de movimento...', 'info');
        iniciarGyro();
      } else {
        log('Aviso: Navegador ocultou DeviceOrientation (provavelmente por ser conexão HTTP via IP).', 'warn');
        if (confirm('O Chrome/Navegador costuma bloquear o Giroscópio em conexões HTTP (IP local).\n\nDeseja tentar ativar a escuta assim mesmo?')) {
          iniciarGyro();
        } else {
          alert('DICA PARA CHROME NO ANDROID:\n1. Acesse chrome://flags no celular\n2. Busque por "unsafely-treat-insecure-origin-as-secure"\n3. Mude para Enabled e coloque o IP do ESP32.\n4. Reinicie o Chrome.');
        }
      }
    }

    function iniciarGyro() {
      window.addEventListener('deviceorientation', handleOrientation, true);
      window.addEventListener('deviceorientationabsolute', handleOrientation, true);
      window.addEventListener('devicemotion', handleMotion, true);
      gyroAtivo = true;
      const btn = document.getElementById('btnAtivarGyro');
      btn.innerText = "🛑 Parar Giroscópio";
      btn.className = "btn btn-danger";
      document.getElementById('btnCalib').disabled = false;
      document.getElementById('badgeStatus').className = "badge badge-warn";
      document.getElementById('badgeStatus').innerText = "GIROSCÓPIO ATIVO";
      log('Escutando sensores (orientation & motion)...', 'info');
    }

    function pararGyro() {
      window.removeEventListener('deviceorientation', handleOrientation, true);
      window.removeEventListener('deviceorientationabsolute', handleOrientation, true);
      window.removeEventListener('devicemotion', handleMotion, true);
      gyroAtivo = false;
      const btn = document.getElementById('btnAtivarGyro');
      btn.innerText = "⚡ Ativar Giroscópio do Celular";
      btn.className = "btn btn-primary";
      document.getElementById('btnCalib').disabled = true;
      document.getElementById('badgeStatus').className = "badge badge-off";
      document.getElementById('badgeStatus').innerText = "PRONTO";
      log('Giroscópio parado.', 'info');
    }

    function handleMotion(e) {
      if (!gyroAtivo || (rawG !== 0 || rawB !== 0)) return; // Prefere orientation
      if (e.accelerationIncludingGravity) {
        const ax = e.accelerationIncludingGravity.x || 0;
        const ay = e.accelerationIncludingGravity.y || 0;
        const az = e.accelerationIncludingGravity.z || 0;
        
        // Converte acelerometro para angulos aproximados
        const pitch = Math.atan2(ay, Math.sqrt(ax * ax + az * az)) * (180 / Math.PI);
        const roll = Math.atan2(-ax, az) * (180 / Math.PI);

        handleOrientation({ gamma: roll, beta: pitch });
      }
    }

    let calibrado = false;

    function calibrarCentro() {
      refGamma = rawG;
      refBeta = rawB;
      calibrado = true;
      log(`Centro calibrado: G=${Math.round(refGamma)}°, B=${Math.round(refBeta)}°`, 'info');
    }

    function handleOrientation(e) {
      if (e.gamma === null || e.beta === null) {
        log('Dados do sensor nulos.', 'warn');
        return;
      }

      rawG = e.gamma;
      rawB = e.beta;

      document.getElementById('rawGamma').innerText = Math.round(rawG);
      document.getElementById('rawBeta').innerText = Math.round(rawB);

      if (!calibrado) {
        calibrarCentro();
      }

      const sens = parseFloat(document.getElementById('rngSens').value);
      
      // Diferenca em relacao ao centro calibrado
      let dGamma = (rawG - refGamma) * sens;
      let dBeta = (rawB - refBeta) * sens;

      // Mapeamento para angulos dos servos (0 a 180)
      let calcPan = Math.round(90 + dGamma);
      let calcTilt = Math.round(90 - dBeta);

      // Trava de limites [0, 180]
      calcPan = Math.max(0, Math.min(180, calcPan));
      calcTilt = Math.max(0, Math.min(180, calcTilt));

      solicitarEnvio(calcPan, calcTilt);
    }
  </script>
</body>
</html>
)rawliteral";

void handleRoot() { server.send(200, "text/html", INDEX_HTML); }

void handleSet() {
  if (server.hasArg("p") && server.hasArg("t")) {
    int p = server.arg("p").toInt();
    int t = server.arg("t").toInt();

    // Protocolo serial: <Pan,Tilt>
    Serial2.print('<');
    Serial2.print(p);
    Serial2.print(',');
    Serial2.print(t);
    Serial2.println('>');

    Serial.printf("[TX NANO] Pan=%d | Tilt=%d\n", p, t);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "ERRO");
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Desativa protecao BOD
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, 44, 43); // RX=44, TX=43 para o transistor BC337

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) { delay(400); }

  Serial.println("\n[SISTEMA CONECTADO]");
  Serial.print("IP: http://");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/set", handleSet);
  server.begin();
}

void loop() {
  server.handleClient();
}
