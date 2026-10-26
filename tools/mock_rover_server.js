/**
 * ====================================================================================
 * ROVER MOCK SERVER E2E - SIMULADOR COMPLETO (GATEWAY + SUÍTE 6 POCs + STREAM 3D)
 * ====================================================================================
 *  - Servidor HTTP (Porta 8080):
 *      GET /              -> Dashboard Web 3D para acompanhar pelo PC
 *      GET /view          -> Visualizador Fullscreen HTML para o WebView do App Expo
 *      GET /stream        -> Stream MJPEG 3D Dinâmico (reage a Pan, Tilt, Tração 4WD e Presets)
 *      GET /capture       -> Snapshot JPEG unitário
 *      GET /resolution    -> Altera resolução simulada (hqvga, qvga, vga)
 *      GET /api/info      -> Metadados de capacidades das POCs (cam, servo, motor)
 *      GET /api/stats     -> Telemetria completa E2E (Chip, Enlace Nano, Bateria, Câmera)
 *      GET /api/cam/*     -> Controle térmico da câmera OV5640 (preset, sleep 0x3008, cfg)
 *      GET /api/cmd       -> Fallback HTTP de quadros ASCII (<S,...>, <M,...>, <P,...>, <X>)
 *  - Servidor WebSocket (Porta 8082):
 *      Suporta simultaneamente o protocolo JSON (Gateway App) e ASCII (<S>, <M>, <P>, <X> das POCs).
 * ====================================================================================
 */

const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');
const os = require('os');
const WebSocket = require('ws');
const jpeg = require('./node_modules/jpeg-js');

const WS_PORT = 8082;
const HTTP_PORT = 8080;

function getLocalIP() {
  const interfaces = os.networkInterfaces();
  const candidates = [];
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal && !iface.address.startsWith('169.254')) {
        candidates.push({ name, address: iface.address });
      }
    }
  }
  const wifi = candidates.find((c) => /wi-?fi|wlan/i.test(c.name));
  return wifi ? wifi.address : (candidates[0]?.address || '127.0.0.1');
}

const localIP = getLocalIP();
const dashboardPath = path.join(__dirname, 'mock_dashboard.html');
const startTime = Date.now();

// ====================================================================================
// ESTADO FÍSICO SIMULADO DO ROVER (ESP32-S3 + ARDUINO NANO)
// ====================================================================================
const state = {
  // Servos SG90 (Pinos D9 e D10)
  targetPan: 90,
  targetTilt: 90,
  pan: 90,
  tilt: 90,
  servoSpeedDegS: 145,
  servoFloorDegS: 15,
  servoAccDegS2: 870,
  servoBacklashUs: 0,

  // Tração 4WD (TB6612FNG + 4x JGA16-050)
  direction: 'STOP',
  speed: 0,
  targetMotL: 0,
  targetMotR: 0,
  motL: 0,
  motR: 0,
  rampMs: 800,
  watchdogMs: 600,
  lastMotorCmdAt: Date.now(),
  poc5AutoRunning: false,
  poc5Step: 0,

  // Posição no mundo 3D simulado
  worldX: 0,
  worldZ: 0,
  worldHeading: 0, // graus

  // Enlace Serial ESP32 <-> Nano (POC 1)
  txFrames: 0,
  rxFrames: 0,
  rxErrors: 0,
  lastHbAt: Date.now(),
  resetFlags: 1, // 1 = Power-on, 4 = Brown-out
  lastPingSeq: 0,

  // Bateria 2S Li-Ion (7.4V nominal, 8.4V carregada)
  vbatBaseMv: 8150,
  vbatMv: 8150,
  vminMv: 8150,

  // Câmera OV5640 Térmica (POC 3 / POC 4)
  camSleeping: false, // Registrador 0x3008 = 0x42
  camPreset: 'equilibrado', // 'frio' | 'equilibrado' | 'qualidade'
  camRes: 'qvga', // 'hqvga' | 'qvga' | 'vga'
  camXclkMhz: 12,
  camTargetFps: 15,
  camActualFps: 15,
  camQuality: 20,
  chipTempC: 44.5,
  lastActivityAt: Date.now(),
  camClients: 0,
};

// Loop de Física de 50 Hz (20 ms) - Simula o Arduino Nano e Térmica do ESP32
setInterval(() => {
  const now = Date.now();
  const dt = 0.02; // 20ms

  // 1. Interpolação suave dos Servos SG90 a 50 Hz
  const maxStep = Math.max(state.servoFloorDegS, state.servoSpeedDegS) * dt;
  const diffPan = state.targetPan - state.pan;
  const diffTilt = state.targetTilt - state.tilt;

  if (Math.abs(diffPan) <= maxStep) state.pan = state.targetPan;
  else state.pan += Math.sign(diffPan) * maxStep;

  if (Math.abs(diffTilt) <= maxStep) state.tilt = state.targetTilt;
  else state.tilt += Math.sign(diffTilt) * maxStep;

  // 2. Sequência autônoma POC 5 (se ativa)
  if (state.poc5AutoRunning) {
    const cycleMs = (now - startTime) % 12000;
    if (cycleMs < 2500) {
      state.targetMotL = 180; state.targetMotR = 180; state.direction = 'F';
    } else if (cycleMs < 3500) {
      state.targetMotL = 0; state.targetMotR = 0; state.direction = 'S';
    } else if (cycleMs < 6000) {
      state.targetMotL = -180; state.targetMotR = -180; state.direction = 'B';
    } else if (cycleMs < 7000) {
      state.targetMotL = 0; state.targetMotR = 0; state.direction = 'S';
    } else if (cycleMs < 9000) {
      state.targetMotL = 160; state.targetMotR = -160; state.direction = 'R';
    } else if (cycleMs < 11000) {
      state.targetMotL = -160; state.targetMotR = 160; state.direction = 'L';
    } else {
      state.targetMotL = 0; state.targetMotR = 0; state.direction = 'S';
    }
    state.lastMotorCmdAt = now;
  }

  // 3. Watchdog dos motores (para se ficar sem comando por > watchdogMs)
  if (!state.poc5AutoRunning && (state.targetMotL !== 0 || state.targetMotR !== 0)) {
    if (now - state.lastMotorCmdAt > state.watchdogMs * 3) {
      // No app mobile os botões enviam onPressIn / onPressOut, então usamos janela generosa para botões manuais
    }
  }

  // 4. Rampa Soft-Start da Ponte H TB6612FNG
  const rampStep = (255 / Math.max(100, state.rampMs)) * 20;
  const dL = state.targetMotL - state.motL;
  const dR = state.targetMotR - state.motR;
  if (Math.abs(dL) <= rampStep) state.motL = state.targetMotL;
  else state.motL += Math.sign(dL) * rampStep;

  if (Math.abs(dR) <= rampStep) state.motR = state.targetMotR;
  else state.motR += Math.sign(dR) * rampStep;

  // 5. Movimento do Rover no Cenário 3D
  const avgPwm = (state.motL + state.motR) / 2;
  const turnPwm = (state.motL - state.motR) / 2;
  state.worldHeading = (state.worldHeading + turnPwm * 0.015 + 360) % 360;
  state.worldZ += avgPwm * 0.04;
  state.worldX += Math.sin((state.worldHeading * Math.PI) / 180) * avgPwm * 0.02;

  // 6. Simulação de Queda de Tensão (Voltage Sag) na Bateria 2S
  const motorLoad = (Math.abs(state.motL) + Math.abs(state.motR)) / 510; // 0 a 1
  const accelSurge = (Math.abs(dL) + Math.abs(dR)) / 510;
  const sagMv = Math.round(motorLoad * 420 + accelSurge * 310 + (Math.random() * 20 - 10));
  state.vbatMv = Math.max(6200, state.vbatBaseMv - sagMv);
  if (state.vbatMv < state.vminMv) state.vminMv = state.vbatMv;

  // 7. Heartbeat do Nano a 1 Hz
  if (now - state.lastHbAt >= 1000) {
    state.lastHbAt = now;
    state.rxFrames++;
  }

  // 8. Simulação Térmica do ESP32-S3 + OV5640
  const isEco = !state.camSleeping && (now - state.lastActivityAt > 8000);
  let targetTemp = 41.0;
  if (state.camSleeping) {
    targetTemp = 37.5;
    state.camActualFps = 0;
  } else if (isEco) {
    targetTemp = 42.0;
    state.camActualFps = 5;
  } else if (state.camPreset === 'frio') {
    targetTemp = 44.0;
    state.camActualFps = 12;
  } else if (state.camPreset === 'equilibrado') {
    targetTemp = 48.5;
    state.camActualFps = 15;
  } else {
    targetTemp = 58.0;
    state.camActualFps = 25;
  }
  state.chipTempC += (targetTemp - state.chipTempC) * 0.01;
}, 20);

// ====================================================================================
// GERADOR DE CÂMERA DINÂMICA INTERATIVA 3D (320x240)
// ====================================================================================
const W = 320;
const H = 240;
const rawBuffer = Buffer.alloc(W * H * 4);

function renderDynamicCameraFrame() {
  if (state.camSleeping) {
    // Modo Soneca (0x3008 = 0x42): Quadro escuro de standby térmico
    for (let i = 0; i < W * H * 4; i += 4) {
      rawBuffer[i] = 6;
      rawBuffer[i + 1] = 10;
      rawBuffer[i + 2] = 16;
      rawBuffer[i + 3] = 255;
    }
    return jpeg.encode({ data: rawBuffer, width: W, height: H }, 40).data;
  }

  const pan = state.pan;
  const tilt = state.tilt;
  const horizonY = Math.round((H / 2) - (tilt - 90) * 2.2);
  const panOffset = Math.round((pan - 90 + (state.worldHeading > 180 ? state.worldHeading - 360 : state.worldHeading) * 0.5) * 2.8);
  const forwardScroll = Math.round(state.worldZ);

  for (let y = 0; y < H; y++) {
    const isSky = y < horizonY;
    for (let x = 0; x < W; x++) {
      const idx = (y * W + x) * 4;

      if (isSky) {
        const skyGrad = Math.min(48, Math.max(12, Math.round(16 + (y / H) * 30)));
        rawBuffer[idx] = 10;
        rawBuffer[idx + 1] = skyGrad;
        rawBuffer[idx + 2] = skyGrad + 18;
        rawBuffer[idx + 3] = 255;
      } else {
        const dist = y - horizonY + 1;
        const stepX = Math.max(10, Math.round(dist * 0.7));
        const gridX = Math.abs(((x - (W / 2) - panOffset) % stepX + stepX) % stepX);
        const gridZ = Math.abs(((dist * 6 + forwardScroll) % 35 + 35) % 35);
        const isGridLine = gridX < 2 || gridZ < 2;

        if (isGridLine) {
          rawBuffer[idx] = 25;
          rawBuffer[idx + 1] = 85;
          rawBuffer[idx + 2] = 110;
        } else {
          rawBuffer[idx] = 14;
          rawBuffer[idx + 1] = 17;
          rawBuffer[idx + 2] = 22;
        }
        rawBuffer[idx + 3] = 255;
      }

      // Linha do horizonte
      if (Math.abs(y - horizonY) <= 1) {
        rawBuffer[idx] = 0;
        rawBuffer[idx + 1] = 210;
        rawBuffer[idx + 2] = 255;
      }

      // Balizas 3D no horizonte (Centro 90°, Esq 45°, Dir 135°)
      const targets = [
        { x: (W / 2) + panOffset, color: [0, 229, 255] },
        { x: (W / 2) - 120 + panOffset, color: [34, 197, 94] },
        { x: (W / 2) + 120 + panOffset, color: [245, 158, 11] },
      ];

      for (const t of targets) {
        if (Math.abs(x - t.x) <= 4 && y >= horizonY - 28 && y <= horizonY + 4) {
          rawBuffer[idx] = t.color[0];
          rawBuffer[idx + 1] = t.color[1];
          rawBuffer[idx + 2] = t.color[2];
        }
      }

      // Retículo central óptico
      const cx = W / 2;
      const cy = H / 2;
      const isCrosshair =
        (Math.abs(y - cy) <= 1 && Math.abs(x - cx) <= 12) ||
        (Math.abs(x - cx) <= 1 && Math.abs(y - cy) <= 12);

      if (isCrosshair) {
        rawBuffer[idx] = 255;
        rawBuffer[idx + 1] = 255;
        rawBuffer[idx + 2] = 255;
      }
    }
  }

  return jpeg.encode({ data: rawBuffer, width: W, height: H }, 60).data;
}

// ====================================================================================
// PARSER UNIFICADO DE COMANDOS (JSON GATEWAY + ASCII POCs)
// ====================================================================================
function handleIncomingCommand(rawStr, wsClient) {
  state.lastActivityAt = Date.now();
  const trimmed = rawStr.trim();

  // 1. Formato ASCII das POCs (<S,pan10,tilt10,vel10>, <M,esq,dir>, <P,seq>, <X>, <p,t>)
  if (trimmed.startsWith('<') && trimmed.endsWith('>')) {
    const inner = trimmed.slice(1, -1);
    const parts = inner.split(',');
    const cmd = parts[0];
    state.txFrames++;

    if (cmd === 'S') {
      // <S,900,900,0> (décimos de grau) ou <S,90,90>
      let p = parseFloat(parts[1] || '900');
      let t = parseFloat(parts[2] || '900');
      let v = parseFloat(parts[3] || '0');
      if (p > 180 || t > 180) { p /= 10; t /= 10; v /= 10; }
      state.targetPan = Math.max(0, Math.min(180, p));
      state.targetTilt = Math.max(0, Math.min(180, t));
      if (v > 0) state.servoSpeedDegS = v;
      state.rxFrames++;
      broadcast({ type: 'servo', pan: Math.round(state.targetPan), tilt: Math.round(state.targetTilt) });
      return true;
    }

    if (cmd === 'M') {
      // <M,esq,dir> (-255 a 255)
      const l = parseInt(parts[1] || '0', 10);
      const r = parseInt(parts[2] || '0', 10);
      state.targetMotL = Math.max(-255, Math.min(255, l));
      state.targetMotR = Math.max(-255, Math.min(255, r));
      state.lastMotorCmdAt = Date.now();
      state.speed = Math.round((Math.abs(l) + Math.abs(r)) / 2);
      if (l === 0 && r === 0) state.direction = 'S';
      else if (l > 0 && r > 0) state.direction = 'F';
      else if (l < 0 && r < 0) state.direction = 'B';
      else if (l < r) state.direction = 'L';
      else state.direction = 'R';
      state.rxFrames++;
      broadcast({ type: 'drive', cmd: state.direction, speed: state.speed, motL: l, motR: r });
      return true;
    }

    if (cmd === 'X') {
      // Parada imediata
      state.targetMotL = 0;
      state.targetMotR = 0;
      state.motL = 0;
      state.motR = 0;
      state.direction = 'S';
      state.speed = 0;
      state.poc5AutoRunning = false;
      state.rxFrames++;
      broadcast({ type: 'drive', cmd: 'S', speed: 0, motL: 0, motR: 0 });
      return true;
    }

    if (cmd === 'P') {
      // Ping de enlace <P,seq> -> Responde <A,seq>
      const seq = parseInt(parts[1] || '1', 10);
      state.lastPingSeq = seq;
      state.rxFrames++;
      if (wsClient && wsClient.readyState === WebSocket.OPEN) {
        wsClient.send(JSON.stringify({ type: 'ack', seq, rttMs: Math.floor(12 + Math.random() * 8) }));
      }
      return true;
    }

    if (cmd === 'C') {
      // Ajuste fino <C,id,val>
      const cid = parseInt(parts[1] || '0', 10);
      const val = parseInt(parts[2] || '0', 10);
      if (cid === 1) state.servoSpeedDegS = val;
      if (cid === 2) state.servoFloorDegS = val;
      if (cid === 3) state.servoAccDegS2 = val;
      if (cid === 5) state.servoBacklashUs = val;
      if (cid === 10) state.rampMs = val;
      if (cid === 14) state.watchdogMs = val;
      state.rxFrames++;
      return true;
    }

    // Formato simples <pan,tilt>
    if (!isNaN(parseInt(cmd, 10)) && parts.length === 2) {
      state.targetPan = Math.max(0, Math.min(180, parseInt(parts[0], 10)));
      state.targetTilt = Math.max(0, Math.min(180, parseInt(parts[1], 10)));
      state.rxFrames++;
      broadcast({ type: 'servo', pan: state.targetPan, tilt: state.targetTilt });
      return true;
    }
  }

  // 2. Formato JSON (App Mobile Expo / Gateway)
  try {
    const data = JSON.parse(trimmed);

    if (data.type === 'ping') {
      if (wsClient && wsClient.readyState === WebSocket.OPEN) {
        wsClient.send(JSON.stringify({ type: 'pong', t: data.t }));
      }
      return true;
    }

    if (data.type === 'servo') {
      state.targetPan = Math.max(0, Math.min(180, Number(data.pan ?? 90)));
      state.targetTilt = Math.max(0, Math.min(180, Number(data.tilt ?? 90)));
      if (data.speed) state.servoSpeedDegS = Number(data.speed);
      state.txFrames++;
      state.rxFrames++;
      broadcast({ type: 'servo', pan: Math.round(state.targetPan), tilt: Math.round(state.targetTilt) }, wsClient);
      return true;
    }

    if (data.type === 'drive') {
      const c = data.cmd || 'S';
      const spd = Number(data.speed ?? 220);
      state.direction = c;
      state.speed = (c === 'S' || c === 'STOP') ? 0 : spd;
      state.lastMotorCmdAt = Date.now();
      state.poc5AutoRunning = false;

      if (c === 'F') { state.targetMotL = spd; state.targetMotR = spd; }
      else if (c === 'B') { state.targetMotL = -spd; state.targetMotR = -spd; }
      else if (c === 'L') { state.targetMotL = -Math.round(spd * 0.8); state.targetMotR = Math.round(spd * 0.8); }
      else if (c === 'R') { state.targetMotL = Math.round(spd * 0.8); state.targetMotR = -Math.round(spd * 0.8); }
      else { state.targetMotL = 0; state.targetMotR = 0; }

      state.txFrames++;
      state.rxFrames++;
      broadcast({ type: 'drive', cmd: c, speed: state.speed, motL: state.targetMotL, motR: state.targetMotR }, wsClient);
      return true;
    }

    if (data.type === 'poc_action') {
      if (data.action === 'cam_sleep') {
        state.camSleeping = Boolean(data.sleep);
      } else if (data.action === 'cam_preset') {
        applyCamPreset(data.preset || 'equilibrado');
      } else if (data.action === 'poc5_auto') {
        state.poc5AutoRunning = Boolean(data.enable);
        if (!state.poc5AutoRunning) {
          state.targetMotL = 0;
          state.targetMotR = 0;
          state.direction = 'S';
        }
      } else if (data.action === 'reset_vmin') {
        state.vminMv = state.vbatMv;
      }
      return true;
    }
  } catch (e) {}

  return false;
}

function applyCamPreset(preset) {
  state.camPreset = preset;
  state.camSleeping = false;
  if (preset === 'frio') {
    state.camRes = 'qvga'; state.camXclkMhz = 8; state.camTargetFps = 12; state.camQuality = 26;
  } else if (preset === 'equilibrado') {
    state.camRes = 'vga'; state.camXclkMhz = 12; state.camTargetFps = 15; state.camQuality = 20;
  } else {
    state.camRes = 'svga'; state.camXclkMhz = 20; state.camTargetFps = 25; state.camQuality = 12;
  }
}

function buildStatsObject() {
  const now = Date.now();
  const isEco = !state.camSleeping && (now - state.lastActivityAt > 8000);
  const resMap = { hqvga: '240x176', qvga: '320x240', vga: '640x480', svga: '800x600' };
  const pct = Math.max(0, Math.min(100, Math.round(((state.vbatMv - 6400) / (8400 - 6400)) * 100)));

  return {
    type: 'telemetry',
    status: 'online',
    mode: 'simulation',
    vbat: Number((state.vbatMv / 1000).toFixed(2)),
    vmin: Number((state.vminMv / 1000).toFixed(2)),
    pct,
    pan: Math.round(state.pan),
    tilt: Math.round(state.tilt),
    motL: Math.round(state.motL),
    motR: Math.round(state.motR),
    poc5AutoRunning: state.poc5AutoRunning,
    sys: {
      temp: Number(state.chipTempC.toFixed(1)),
      cpu: 240,
      heap: 248500,
      psram: 8120000,
      rssi: -48,
      up: Math.floor((now - startTime) / 1000),
    },
    link: {
      tx: state.txFrames,
      rx: state.rxFrames,
      err: state.rxErrors,
      hb_age: now - state.lastHbAt,
      vbat: state.vbatMv,
      vmin: state.vminMv,
      mot_e: Math.round(state.motL),
      mot_d: Math.round(state.motR),
      reset: state.resetFlags,
      nano_up: Math.floor((now - startTime) / 1000),
    },
    cam: {
      modo: state.camSleeping ? 'DORMINDO' : (isEco ? 'ECO' : 'ATIVO'),
      forcado: false,
      fps: state.camActualFps,
      teto_fps: state.camTargetFps,
      kbps: state.camSleeping ? 0 : Math.round(state.camActualFps * 9.5 * 8),
      kb_frame: 9.5,
      cap_ms: 6.2,
      xclk: state.camXclkMhz,
      res_px: resMap[state.camRes] || '320x240',
      clientes: state.camClients,
      dormindo: state.camSleeping,
      preset: state.camPreset,
    },
  };
}

// ====================================================================================
// 1. SERVIDOR HTTP (Porta 8080)
// ====================================================================================
const httpServer = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname || '/';
  const query = parsedUrl.query || {};

  if (pathname === '/' || pathname === '/dashboard') {
    fs.readFile(dashboardPath, 'utf8', (err, html) => {
      if (err) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Erro ao carregar dashboard');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(html);
    });
    return;
  }

  // Endpoint /view usado pelo WebView do App Mobile Expo
  if (pathname === '/view') {
    const html = `<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>*{margin:0;padding:0;box-sizing:border-box;background:#000;overflow:hidden;}html,body{width:100%;height:100%;display:flex;align-items:center;justify-content:center;}img{width:100%;height:100%;object-fit:cover;}</style></head><body><img src='/stream' onerror="this.src='/capture?t='+Date.now()"></body></html>`;
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
    return;
  }

  if (pathname === '/capture') {
    const frameJpeg = renderDynamicCameraFrame();
    res.writeHead(200, {
      'Content-Type': 'image/jpeg',
      'Content-Length': frameJpeg.length,
      'Cache-Control': 'no-store',
    });
    res.end(frameJpeg);
    return;
  }

  if (pathname === '/stream') {
    state.camClients++;
    res.writeHead(200, {
      'Content-Type': 'multipart/x-mixed-replace; boundary=--frame',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Connection': 'close',
    });

    const interval = setInterval(() => {
      try {
        const frameJpeg = renderDynamicCameraFrame();
        res.write(`--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ${frameJpeg.length}\r\n\r\n`);
        res.write(frameJpeg);
        res.write('\r\n');
      } catch (err) {
        clearInterval(interval);
      }
    }, 66); // ~15 FPS fluido

    req.on('close', () => {
      state.camClients = Math.max(0, state.camClients - 1);
      clearInterval(interval);
    });
    return;
  }

  if (pathname === '/resolution') {
    const val = String(query.val || 'qvga').toLowerCase();
    state.camRes = val;
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('OK');
    return;
  }

  if (pathname === '/set') {
    if (query.p !== undefined && query.t !== undefined) {
      handleIncomingCommand(`<S,${Number(query.p) * 10},${Number(query.t) * 10},0>`);
    }
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('OK');
    return;
  }

  if (pathname === '/api/info') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      poc: 'simulacao_e2e_completa',
      ip: localIP,
      caps: ['cam', 'servo', 'motor'],
    }));
    return;
  }

  if (pathname === '/api/stats') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(buildStatsObject()));
    return;
  }

  if (pathname === '/api/cam/preset') {
    applyCamPreset(String(query.n || 'equilibrado'));
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true, preset: state.camPreset }));
    return;
  }

  if (pathname === '/api/cmd') {
    const f = String(query.f || '');
    const ok = handleIncomingCommand(f);
    res.writeHead(ok ? 200 : 400, { 'Content-Type': 'text/plain' });
    res.end(ok ? 'ok' : 'quadro invalido');
    return;
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

httpServer.listen(HTTP_PORT, '0.0.0.0', () => {
  console.log(`\n🖥️  [DASHBOARD WEB 3D] http://${localIP}:${HTTP_PORT}`);
  console.log(`📹 [VIEW / STREAM]    http://${localIP}:${HTTP_PORT}/view`);
  console.log(`📊 [API STATS POCs]   http://${localIP}:${HTTP_PORT}/api/stats`);
});

// ====================================================================================
// 2. SERVIDOR WEBSOCKET (Porta 8082)
// ====================================================================================
const wss = new WebSocket.Server({ port: WS_PORT });

console.log(`📡 [WEBSOCKET E2E]    ws://${localIP}:${WS_PORT}`);
console.log('='.repeat(70));
console.log('Simulador E2E Rover (Gateway + 6 POCs) ativo e aguardando conexões...\n');

function broadcast(data, senderWs) {
  const msg = JSON.stringify(data);
  wss.clients.forEach((client) => {
    if (client !== senderWs && client.readyState === WebSocket.OPEN) {
      client.send(msg);
    }
  });
}

// Envia telemetria contínua a 4 Hz para manter o App e o Dashboard sincronizados
setInterval(() => {
  if (wss.clients.size > 0) {
    const stats = buildStatsObject();
    const msg = JSON.stringify(stats);
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(msg);
      }
    });
  }
}, 250);

wss.on('connection', (ws, req) => {
  const clientIP = req.socket.remoteAddress;
  console.log(`🟢 [CONEXÃO] Cliente conectado: ${clientIP}`);

  ws.send(JSON.stringify(buildStatsObject()));

  ws.on('message', (message) => {
    handleIncomingCommand(message.toString(), ws);
  });

  ws.on('close', () => {
    console.log(`🔴 [DESCONECTADO] Cliente saiu.`);
  });
});
