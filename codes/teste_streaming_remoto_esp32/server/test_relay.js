const { spawn } = require('child_process');
const WebSocket = require('ws');
const http = require('http');

console.log('🧪 Iniciando Testes de Validação do Servidor Relay...');

// 1. Iniciar Servidor Relay
const serverProcess = spawn('node', ['server.js'], {
  cwd: __dirname,
  env: { ...process.env, PORT: '3099' }
});

serverProcess.stdout.on('data', (data) => {
  // console.log(`[SERVER]: ${data.toString().trim()}`);
});

serverProcess.stderr.on('data', (data) => {
  console.error(`[SERVER ERR]: ${data.toString().trim()}`);
});

// Aguardar inicializacao do servidor
setTimeout(async () => {
  try {
    // 2. Testar API HTTP /api/status
    console.log('🔍 Testando endpoint GET /api/status...');
    const statusData = await new Promise((resolve, reject) => {
      http.get('http://localhost:3099/api/status', (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => resolve(JSON.parse(body)));
      }).on('error', reject);
    });

    console.log('✅ Response API status:', statusData);
    if (typeof statusData.esp32Connected !== 'boolean') {
      throw new Error('Campo esp32Connected invalido!');
    }

    // 3. Conectar cliente Viewer
    console.log('📺 Conectando cliente Viewer via WebSocket...');
    const viewerWs = new WebSocket('ws://localhost:3099/ws?role=viewer');

    let receivedFrames = 0;
    viewerWs.on('message', (data, isBinary) => {
      if (isBinary || Buffer.isBuffer(data)) {
        receivedFrames++;
      }
    });

    await new Promise(resolve => viewerWs.on('open', resolve));
    console.log('✅ Viewer conectado!');

    // 4. Conectar emulador de ESP32
    console.log('🤖 Conectando emulador de ESP32 via WebSocket...');
    const esp32Ws = new WebSocket('ws://localhost:3099/ws?role=esp32');

    await new Promise(resolve => esp32Ws.on('open', resolve));
    console.log('✅ ESP32 conectado!');

    // 5. Simular envio de 10 quadros JPEG
    console.log('📸 Enviando quadros simulados do ESP32 para o Relay...');
    const dummyJpegBuffer = Buffer.from([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0xFF, 0xD9]); // Head & Tail do JPEG

    for (let i = 0; i < 10; i++) {
      esp32Ws.send(dummyJpegBuffer, { binary: true });
      await new Promise(r => setTimeout(r, 20));
    }

    // Aguardar entrega do relay
    await new Promise(r => setTimeout(r, 200));

    console.log(`📊 Quadros recebidos pelo Viewer: ${receivedFrames}`);
    if (receivedFrames >= 8) {
      console.log('🎉 TESTE PASSOU COM SUCESSO! Transmissão em tempo real verificada.');
    } else {
      throw new Error(`Falha na transmissão: Apenas ${receivedFrames} quadros recebidos.`);
    }

    // Limpeza
    viewerWs.close();
    esp32Ws.close();
    serverProcess.kill();
    process.exit(0);

  } catch (err) {
    console.error('❌ ERRO NO TESTE:', err);
    serverProcess.kill();
    process.exit(1);
  }
}, 1000);
