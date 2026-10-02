const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer, WebSocket } = require('ws');

const PORT = process.env.PORT || 8080;
const PUBLIC_DIR = path.join(__dirname, 'public');

// --- SERVIDOR HTTP (Interface Web HUD e Healthcheck) ---
const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

  // Healthcheck para Fly.io
  if (url.pathname === '/health' || url.pathname === '/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({
      status: 'ok',
      robotConnected: robotWs !== null && robotWs.readyState === WebSocket.OPEN,
      pilotsConnected: pilots.size,
      uptimeSeconds: Math.floor(process.uptime()),
      timestamp: Date.now()
    }));
  }

  // Roteamento de arquivos estáticos da interface web
  let filePath = path.join(PUBLIC_DIR, url.pathname === '/' ? 'index.html' : url.pathname);

  // Previne Directory Traversal
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      filePath = path.join(PUBLIC_DIR, 'index.html');
    }

    const ext = path.extname(filePath).toLowerCase();
    const mimeTypes = {
      '.html': 'text/html; charset=utf-8',
      '.css': 'text/css; charset=utf-8',
      '.js': 'application/javascript; charset=utf-8',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.ico': 'image/x-icon',
      '.svg': 'image/svg+xml'
    };

    const contentType = mimeTypes[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
});

// --- SERVIDOR WEBSOCKET (Relay FPV & Telemetria) ---
const wss = new WebSocketServer({ server });

let robotWs = null;
const pilots = new Set();

// Métricas do servidor
let framesReceivedCount = 0;
let bytesReceivedCount = 0;
let lastMetricsReset = Date.now();
let currentServerFps = 0;
let currentBitrateKbps = 0;

// Atualiza cálculo de FPS e Bitrate a cada 1 segundo
setInterval(() => {
  const now = Date.now();
  const elapsedSec = (now - lastMetricsReset) / 1000;
  if (elapsedSec >= 1.0) {
    currentServerFps = (framesReceivedCount / elapsedSec).toFixed(1);
    currentBitrateKbps = ((bytesReceivedCount * 8) / (elapsedSec * 1024)).toFixed(1);
    framesReceivedCount = 0;
    bytesReceivedCount = 0;
    lastMetricsReset = now;

    // Transmite status periódico aos pilotos conectados
    broadcastToPilots(JSON.stringify({
      type: 'server_stats',
      fps: currentServerFps,
      bitrateKbps: currentBitrateKbps,
      robotOnline: robotWs !== null && robotWs.readyState === WebSocket.OPEN,
      pilotsCount: pilots.size
    }));
  }
}, 1000);

function broadcastToPilots(data, isBinary = false) {
  for (const pilot of pilots) {
    if (pilot.readyState === WebSocket.OPEN) {
      // Política de descarte de quadros se o buffer do cliente estiver sobrecarregado (> 256 KB)
      if (isBinary && pilot.bufferedAmount > 256 * 1024) {
        continue;
      }
      pilot.send(data, { binary: isBinary });
    }
  }
}

wss.on('connection', (ws, req) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const isRobot = url.pathname.includes('/robot') || url.searchParams.get('role') === 'robot';

  if (isRobot) {
    // --- CONEXÃO DO ROBÔ (ESP32-S3) ---
    console.log(`[ROBOT] Conectado a partir de ${req.socket.remoteAddress}`);
    if (robotWs && robotWs !== ws && robotWs.readyState === WebSocket.OPEN) {
      console.log('[ROBOT] Substituindo conexão anterior do robô...');
      robotWs.close();
    }
    robotWs = ws;

    // Avisa os pilotos que o robô está online
    broadcastToPilots(JSON.stringify({
      type: 'robot_status',
      online: true,
      timestamp: Date.now()
    }));

    ws.on('message', (message, isBinary) => {
      if (isBinary) {
        framesReceivedCount++;
        bytesReceivedCount += message.length;

        // O cabeçalho mínimo do ESP32 tem 8 bytes:
        // [0..3]: Frame ID (uint32BE)
        // [4..7]: ESP millis() (uint32BE)
        // [8..N]: JPEG payload
        if (message.length >= 8) {
          const frameId = message.readUInt32BE(0);
          const espTimestamp = message.readUInt32BE(4);

          // 1. Envia ACK de volta ao ESP32 para medição de RTT do lado do robô
          // Buffer ACK: 1 byte opcode (0x01) + 4 bytes frameId + 4 bytes timestamp
          const ackBuf = Buffer.allocUnsafe(9);
          ackBuf.writeUInt8(0x01, 0);
          ackBuf.writeUInt32BE(frameId, 1);
          ackBuf.writeUInt32BE(espTimestamp, 5);
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(ackBuf, { binary: true });
          }

          // 2. Encapsula o frame para os pilotos injetando o timestamp do servidor (8 bytes BigInt64)
          // Novo pacote para os pilotos:
          // [0..3]: Frame ID (uint32BE)
          // [4..7]: ESP millis() (uint32BE)
          // [8..15]: Server timestamp ms (BigInt64BE)
          // [16..N]: JPEG payload
          const relayed = Buffer.allocUnsafe(message.length + 8);
          message.copy(relayed, 0, 0, 8); // frameId e espTimestamp
          relayed.writeBigInt64BE(BigInt(Date.now()), 8); // carimbo do servidor
          message.copy(relayed, 16, 8); // JPEG bruto

          broadcastToPilots(relayed, true);
        } else {
          // Frame sem cabeçalho padronizado, repassa cru
          broadcastToPilots(message, true);
        }
      } else {
        // Mensagem de texto/JSON vinda do ESP32 (ex: telemetria de sensores, bateria)
        try {
          const text = message.toString();
          console.log(`[ROBOT TELEMETRY] ${text}`);
          broadcastToPilots(text, false);
        } catch (e) {
          console.error('[ROBOT ERROR]', e);
        }
      }
    });

    ws.on('close', () => {
      console.log('[ROBOT] Desconectado.');
      if (robotWs === ws) {
        robotWs = null;
      }
      broadcastToPilots(JSON.stringify({
        type: 'robot_status',
        online: false,
        timestamp: Date.now()
      }));
    });

    ws.on('error', (err) => {
      console.error('[ROBOT WS ERROR]', err.message);
    });

  } else {
    // --- CONEXÃO DO PILOTO (Interface Web) ---
    pilots.add(ws);
    console.log(`[PILOT] Novo piloto conectado (${pilots.size} ativo(s))`);

    // Envia estado inicial ao piloto conectado
    ws.send(JSON.stringify({
      type: 'initial_state',
      robotOnline: robotWs !== null && robotWs.readyState === WebSocket.OPEN,
      serverTime: Date.now()
    }));

    ws.on('message', (message, isBinary) => {
      if (!isBinary) {
        try {
          const data = JSON.parse(message.toString());

          // Protocolo Two-Leg RTT: Ping-Pong com o Piloto
          if (data.type === 'ping') {
            ws.send(JSON.stringify({
              type: 'pong',
              t: data.t, // Echo do timestamp local do piloto
              serverTime: Date.now()
            }));
            return;
          }

          // Comandos de pilotagem/teleoperação (throttle, steer, pan, tilt)
          if (data.type === 'cmd' || data.type === 'control') {
            if (robotWs && robotWs.readyState === WebSocket.OPEN) {
              // Encaminha comando instantaneamente para o robô
              robotWs.send(message.toString());
            }
          }
        } catch (err) {
          console.error('[PILOT MSG ERROR]', err.message);
        }
      }
    });

    ws.on('close', () => {
      pilots.delete(ws);
      console.log(`[PILOT] Piloto desconectado (${pilots.size} restante(s))`);
    });

    ws.on('error', (err) => {
      pilots.delete(ws);
      console.error('[PILOT WS ERROR]', err.message);
    });
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`====================================================`);
  console.log(`🛰️  ROVER CLOUD RELAY INICIADO`);
  console.log(`📡 Porta: ${PORT}`);
  console.log(`🌐 Interface HUD: http://localhost:${PORT}`);
  console.log(`🤖 Endpoint Robô: ws://localhost:${PORT}/ws/robot`);
  console.log(`🕹️  Endpoint Piloto: ws://localhost:${PORT}/ws/pilot`);
  console.log(`====================================================`);
});
