const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');

const PORT = process.env.PORT || 3000;
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Servir arquivos estaticos da pasta public
app.use(express.static(path.join(__dirname, 'public')));

// Estado e estatisticas da conexao
let esp32Socket = null;
const viewerSockets = new Set();

let stats = {
  esp32Connected: false,
  connectedViewers: 0,
  totalFramesReceived: 0,
  lastFrameBytes: 0,
  currentFps: 0,
  lastFrameTimestamp: 0,
  startTime: Date.now()
};

// Medicao de FPS
let frameCounter = 0;
setInterval(() => {
  stats.currentFps = frameCounter;
  frameCounter = 0;
  stats.connectedViewers = viewerSockets.size;
  stats.esp32Connected = esp32Socket !== null && esp32Socket.readyState === WebSocket.OPEN;
}, 1000);

// Endpoint HTTP de API para status
app.get('/api/status', (req, res) => {
  res.json({
    ...stats,
    uptimeSeconds: Math.floor((Date.now() - stats.startTime) / 1000)
  });
});

// Tratamento de conexoes WebSocket
wss.on('connection', (ws, req) => {
  const urlParams = new URLSearchParams(req.url.includes('?') ? req.url.split('?')[1] : '');
  let role = urlParams.get('role');

  // Suporte a caminhos /ws/esp32 e /ws/viewer
  if (req.url.startsWith('/ws/esp32') || req.url.startsWith('/esp32')) {
    role = 'esp32';
  } else if (req.url.startsWith('/ws/viewer') || req.url.startsWith('/viewer')) {
    role = 'viewer';
  }

  // Se nao especificado, padrao e auto-detectar ou assumir viewer se nao for identificacao de esp32
  if (role === 'esp32') {
    console.log('[RELAY] ESP32 Conectado!');
    if (esp32Socket && esp32Socket !== ws) {
      console.log('[RELAY] Fechando conexao ESP32 antiga...');
      esp32Socket.close();
    }
    esp32Socket = ws;
    stats.esp32Connected = true;

    // Notificar viewers que a camera conectou
    broadcastToViewers(JSON.stringify({ type: 'status', esp32Connected: true }));

    ws.on('message', (data, isBinary) => {
      if (isBinary || Buffer.isBuffer(data)) {
        frameCounter++;
        stats.totalFramesReceived++;
        stats.lastFrameBytes = data.length;
        stats.lastFrameTimestamp = Date.now();

        // Transmitir o quadro binario JPEG imediatamente para todos os clientes web conectados
        broadcastToViewers(data, true);
      } else {
        // Mensagem de texto/metadados do ESP32
        try {
          const msg = JSON.parse(data.toString());
          console.log('[ESP32 Text Msg]:', msg);
          broadcastToViewers(JSON.stringify({ type: 'esp32_info', payload: msg }));
        } catch (e) {
          console.log('[ESP32 Raw Text]:', data.toString());
        }
      }
    });

    ws.on('close', () => {
      console.log('[RELAY] ESP32 Desconectado!');
      if (esp32Socket === ws) {
        esp32Socket = null;
        stats.esp32Connected = false;
        broadcastToViewers(JSON.stringify({ type: 'status', esp32Connected: false }));
      }
    });

    ws.on('error', (err) => {
      console.error('[RELAY Error - ESP32]:', err.message);
    });

  } else {
    // Cliente Viewer (Navegador Web)
    viewerSockets.add(ws);
    stats.connectedViewers = viewerSockets.size;
    console.log(`[RELAY] Novo Viewer conectado. Total: ${viewerSockets.size}`);

    // Enviar estado inicial do ESP32 para o novo viewer
    ws.send(JSON.stringify({
      type: 'status',
      esp32Connected: stats.esp32Connected,
      currentFps: stats.currentFps
    }));

    ws.on('message', (message) => {
      // Se o viewer enviar comandos (ex: mudanca de resolucao/qualidade)
      if (esp32Socket && esp32Socket.readyState === WebSocket.OPEN) {
        esp32Socket.send(message);
      }
    });

    ws.on('close', () => {
      viewerSockets.delete(ws);
      stats.connectedViewers = viewerSockets.size;
      console.log(`[RELAY] Viewer desconectado. Total: ${viewerSockets.size}`);
    });

    ws.on('error', (err) => {
      console.error('[RELAY Error - Viewer]:', err.message);
      viewerSockets.delete(ws);
    });
  }
});

// Funcao auxiliar para retransmitir dados para todos os viewers
function broadcastToViewers(data, isBinary = false) {
  for (const client of viewerSockets) {
    if (client.readyState === WebSocket.OPEN) {
      // Se o buffer do cliente estiver acumulando mais de 2 frames (Drop-Frame),
      // ignora o envio desse frame para esse cliente especifico, evitando lag!
      if (isBinary && client.bufferedAmount > stats.lastFrameBytes * 2) {
        continue;
      }
      client.send(data, { binary: isBinary });
    }
  }
}

server.listen(PORT, () => {
  console.log(`===================================================`);
  console.log(`🚀 Servidor Relay de Video ESP32 rodando na porta ${PORT}`);
  console.log(`🌐 Interface Web: http://localhost:${PORT}`);
  console.log(`📡 WebSocket ESP32: ws://localhost:${PORT}/ws?role=esp32`);
  console.log(`📺 WebSocket Viewer: ws://localhost:${PORT}/ws?role=viewer`);
  console.log(`===================================================`);
});
