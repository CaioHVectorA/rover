document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('video-canvas');
  const ctx = canvas.getContext('2d');
  const placeholder = document.getElementById('video-placeholder');
  const placeholderText = document.getElementById('placeholder-text');

  // Badges
  const badgeEsp = document.getElementById('status-badge-esp');
  const badgeRelay = document.getElementById('status-badge-relay');

  // HUD
  const hudFps = document.getElementById('hud-fps');
  const hudRes = document.getElementById('hud-res');
  const hudSize = document.getElementById('hud-size');
  const hudLatency = document.getElementById('hud-latency');

  // Stats
  const statFps = document.getElementById('stat-fps');
  const statTotalFrames = document.getElementById('stat-total-frames');
  const statFrameSize = document.getElementById('stat-frame-size');
  const statBandwidth = document.getElementById('stat-bandwidth');

  let ws = null;
  let frameCount = 0;
  let totalFrames = 0;
  let bytesInLastSecond = 0;
  let currentFps = 0;
  let currentBandwidth = 0;

  let isRendering = false;
  let currentObjectUrl = null;

  // Atualizar contadores a cada 1 segundo
  setInterval(() => {
    currentFps = frameCount;
    currentBandwidth = (bytesInLastSecond / 1024).toFixed(1);

    hudFps.textContent = `FPS: ${currentFps}`;
    statFps.textContent = `${currentFps} FPS`;
    statBandwidth.textContent = `${currentBandwidth} KB/s`;

    frameCount = 0;
    bytesInLastSecond = 0;
  }, 1000);

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws?role=viewer`;

    badgeRelay.className = 'badge badge-connecting';
    badgeRelay.textContent = 'Relay: Conectando...';

    ws = new WebSocket(wsUrl);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
      console.log('[VIEWER] Conectado ao Servidor Relay!');
      badgeRelay.className = 'badge badge-online';
      badgeRelay.textContent = 'Relay: Online';
    };

    ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        // Mensagem de controle/status JSON
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'status') {
            updateEsp32Status(msg.esp32Connected);
          }
        } catch (e) {
          console.error('Erro ao interpretar JSON:', e);
        }
      } else if (event.data instanceof ArrayBuffer) {
        // Quadro binario JPEG do ESP32
        const frameSize = event.data.byteLength;
        const frameSizeKB = (frameSize / 1024).toFixed(1);

        frameCount++;
        totalFrames++;
        bytesInLastSecond += frameSize;

        hudSize.textContent = `Tamanho: ${frameSizeKB} KB`;
        statFrameSize.textContent = `${frameSizeKB} KB`;
        statTotalFrames.textContent = totalFrames;

        // Regra do Descarte (Drop-Frame): Se o navegador ainda esta desenhando o frame anterior,
        // descarta o frame acumulado e desenha apenas o mais recente!
        if (isRendering) {
          return;
        }

        isRendering = true;
        const blob = new Blob([event.data], { type: 'image/jpeg' });

        if (currentObjectUrl) {
          URL.revokeObjectURL(currentObjectUrl);
        }
        currentObjectUrl = URL.createObjectURL(blob);

        const img = new Image();
        img.onload = () => {
          // Ajustar dimensao do canvas se mudou a resolucao
          if (canvas.width !== img.width || canvas.height !== img.height) {
            canvas.width = img.width;
            canvas.height = img.height;
            hudRes.textContent = `Resolução: ${img.width}x${img.height}`;
          }

          ctx.drawImage(img, 0, 0);
          placeholder.style.display = 'none';
          isRendering = false;
        };

        img.onerror = () => {
          isRendering = false;
        };

        img.src = currentObjectUrl;
      }
    };

    ws.onclose = () => {
      console.log('[VIEWER] Conexão com Relay perdida. Reconectando em 2s...');
      badgeRelay.className = 'badge badge-offline';
      badgeRelay.textContent = 'Relay: Offline';
      updateEsp32Status(false);
      setTimeout(connect, 2000);
    };

    ws.onerror = (err) => {
      console.error('[VIEWER WS Error]:', err);
      ws.close();
    };
  }

  function updateEsp32Status(online) {
    if (online) {
      badgeEsp.className = 'badge badge-online';
      badgeEsp.textContent = 'ESP32: Transmitindo';
      placeholderText.textContent = 'Carregando vídeo...';
    } else {
      badgeEsp.className = 'badge badge-offline';
      badgeEsp.textContent = 'ESP32: Offline';
      placeholder.style.display = 'flex';
      placeholderText.textContent = 'Aguardando transmissão do ESP32...';
    }
  }

  connect();
});
