/**
 * ====================================================================================
 * ROVER MOCK SERVER - STREAM DE VÍDEO INTERATIVO 3D & TELEMETRIA
 * ====================================================================================
 *  - Servidor HTTP (Porta 8080):
 *      GET /         -> Dashboard Web 3D para testar pelo PC
 *      GET /stream   -> Stream MJPEG DINÂMICO INTERATIVO que reage em tempo real
 *                       aos ângulos Pan e Tilt do celular!
 *  - Servidor WebSocket (Porta 8082):
 *      Recebe Pan/Tilt e comandos 4WD do celular.
 * ====================================================================================
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const WebSocket = require('ws');
const jpeg = require('./node_modules/jpeg-js');

const WS_PORT = 8082;
const HTTP_PORT = 8080;

function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '127.0.0.1';
}

const localIP = getLocalIP();
const dashboardPath = path.join(__dirname, 'mock_dashboard.html');

// Estado compartilhado dos servos simulados
let state = {
  pan: 90,
  tilt: 90,
  direction: 'STOP',
  speed: 0,
};

// -------------------------------------------------------------
// GERADOR DE CÂMERA DINÂMICA INTERATIVA (320x240)
// -------------------------------------------------------------
const W = 320;
const H = 240;
const rawBuffer = Buffer.alloc(W * H * 4);

function renderDynamicCameraFrame(pan, tilt) {
  // Cálculo da linha do horizonte baseada no Tilt (50° a 130°, centro 90°)
  // Ao olhar para cima (tilt < 90), o horizonte desce. Ao olhar para baixo (tilt > 90), o horizonte sobe.
  const horizonY = Math.round((H / 2) - (tilt - 90) * 2.2);

  // Deslocamento horizontal dos objetos no cenário baseado no Pan
  const panOffset = Math.round((pan - 90) * 2.8);

  for (let y = 0; y < H; y++) {
    const isSky = y < horizonY;
    for (let x = 0; x < W; x++) {
      const idx = (y * W + x) * 4;

      if (isSky) {
        // Céu com gradiente vertical escuro
        const skyGrad = Math.min(45, Math.max(12, Math.round(18 + (y / H) * 28)));
        rawBuffer[idx] = 10;
        rawBuffer[idx + 1] = skyGrad;
        rawBuffer[idx + 2] = skyGrad + 15;
        rawBuffer[idx + 3] = 255;
      } else {
        // Chão escuro com grade de perspectiva
        const dist = y - horizonY + 1;
        const gridX = Math.abs((x - (W / 2) - panOffset) % Math.max(10, Math.round(dist * 0.7)));
        const gridZ = Math.abs((dist * 6) % 35);
        const isGridLine = gridX < 2 || gridZ < 2;

        if (isGridLine) {
          rawBuffer[idx] = 30;
          rawBuffer[idx + 1] = 65;
          rawBuffer[idx + 2] = 80;
        } else {
          rawBuffer[idx] = 16;
          rawBuffer[idx + 1] = 18;
          rawBuffer[idx + 2] = 22;
        }
        rawBuffer[idx + 3] = 255;
      }

      // Linha do horizonte (ciano sutil)
      if (Math.abs(y - horizonY) <= 1) {
        rawBuffer[idx] = 0;
        rawBuffer[idx + 1] = 180;
        rawBuffer[idx + 2] = 220;
      }

      // Alvos de referência espacial no horizonte (marcadores virtuais)
      // Centro (90°), Esquerda (45°) e Direita (135°)
      const targets = [
        { x: (W / 2) + panOffset, color: [0, 229, 255] },       // Centro
        { x: (W / 2) - 120 + panOffset, color: [16, 185, 129] }, // Esquerda (Verde)
        { x: (W / 2) + 120 + panOffset, color: [245, 158, 11] }, // Direita (Laranja)
      ];

      for (const t of targets) {
        if (Math.abs(x - t.x) <= 3 && y >= horizonY - 25 && y <= horizonY) {
          rawBuffer[idx] = t.color[0];
          rawBuffer[idx + 1] = t.color[1];
          rawBuffer[idx + 2] = t.color[2];
        }
      }

      // Retículo central óptico (Mira na tela da câmera)
      const cx = W / 2;
      const cy = H / 2;
      const isCrosshair =
        (Math.abs(y - cy) <= 1 && Math.abs(x - cx) <= 14) ||
        (Math.abs(x - cx) <= 1 && Math.abs(y - cy) <= 14);

      if (isCrosshair) {
        rawBuffer[idx] = 255;
        rawBuffer[idx + 1] = 255;
        rawBuffer[idx + 2] = 255;
      }
    }
  }

  // Codifica para JPEG de alta velocidade (qualidade 55 = ultra leve)
  return jpeg.encode({ data: rawBuffer, width: W, height: H }, 55).data;
}

// -------------------------------------------------------------
// 1. SERVIDOR HTTP (Stream MJPEG Dinâmico + Dashboard Web)
// -------------------------------------------------------------
const httpServer = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.url === '/' || req.url === '/dashboard') {
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

  if (req.url.startsWith('/stream')) {
    // Inicia stream MJPEG dinâmico e interativo
    res.writeHead(200, {
      'Content-Type': 'multipart/x-mixed-replace; boundary=--frame',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Connection': 'close',
    });

    const interval = setInterval(() => {
      try {
        const frameJpeg = renderDynamicCameraFrame(state.pan, state.tilt);
        res.write(`--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ${frameJpeg.length}\r\n\r\n`);
        res.write(frameJpeg);
        res.write('\r\n');
      } catch (err) {
        clearInterval(interval);
      }
    }, 80); // ~12 FPS dinâmico

    req.on('close', () => {
      clearInterval(interval);
    });
    return;
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

httpServer.listen(HTTP_PORT, '0.0.0.0', () => {
  console.log(`\n🖥️  [DASHBOARD WEB 3D] http://${localIP}:${HTTP_PORT}`);
  console.log(`📹 [STREAM INTERATIVO] http://${localIP}:${HTTP_PORT}/stream`);
});

// -------------------------------------------------------------
// 2. SERVIDOR WEBSOCKET
// -------------------------------------------------------------
const wss = new WebSocket.Server({ port: WS_PORT });

console.log(`📡 [WEBSOCKET] ws://${localIP}:${WS_PORT}`);
console.log('='.repeat(70));
console.log('Servidor pronto e aguardando conexões...\n');

function broadcast(data, senderWs) {
  const msg = JSON.stringify(data);
  wss.clients.forEach((client) => {
    if (client !== senderWs && client.readyState === WebSocket.OPEN) {
      client.send(msg);
    }
  });
}

wss.on('connection', (ws, req) => {
  const clientIP = req.socket.remoteAddress;
  console.log(`\n🟢 [CONEXÃO] Cliente: ${clientIP}`);

  ws.send(JSON.stringify({
    type: 'telemetry',
    status: 'online',
    vbat: 8.2,
    pct: 95,
  }));

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message.toString());

      if (data.type === 'ping') {
        ws.send(JSON.stringify({ type: 'pong' }));
        return;
      }

      // Atualiza estado dos servos para o gerador de vídeo em tempo real
      if (data.type === 'servo') {
        state.pan = data.pan;
        state.tilt = data.tilt;
        broadcast(data, ws);
        return;
      }

      if (data.type === 'drive') {
        state.direction = data.cmd;
        state.speed = data.speed || 0;
        broadcast(data, ws);
        return;
      }
    } catch (e) {}
  });

  ws.on('close', () => {
    console.log(`\n🔴 [DESCONECTADO] Cliente desconectou.`);
  });
});
