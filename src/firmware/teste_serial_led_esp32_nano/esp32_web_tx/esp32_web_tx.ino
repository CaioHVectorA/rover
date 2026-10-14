/*
 * ====================================================================================
 * ROVER ESP32 - TESTE DE COMUNICAÇÃO SERIAL (TX) CONTROLADA POR PÁGINA WEB
 * ====================================================================================
 * Este firmware roda no ESP32 (ESP32-S3-CAM ou ESP32-CAM).
 * Ele cria um Ponto de Acesso Wi-Fi ("Rover-Control-Test") e serve uma página Web.
 * Ao clicar nos botões da página, o ESP32 envia comandos pela porta Serial (TX)
 * diretamente para o pino RX do Arduino Nano a 115200 baud.
 *
 * Conexão de Bancada:
 * - GND do ESP32 ---- ligado ao ---- GND do Arduino Nano (Obrigatório)
 * - Pino TX do ESP32 - ligado ao ---- Pino RX (D0) do Arduino Nano
 * ====================================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <esp_wifi.h>

// ------------------------------------------------------------------------------------
// SELEÇÃO DO MODELO DE PLACA ESP32
// Descomente apenas a linha da placa que você estiver utilizando para o teste:
// ------------------------------------------------------------------------------------
#define PLACA_ESP32_S3_CAM    // ESP32-S3-CAM N16R8 (Pino TX = IO43)
// #define PLACA_ESP32_CAM_CLASSIC // ESP32-CAM AI-Thinker / RoboCore (Pino TX = GPIO 1)

#if defined(PLACA_ESP32_S3_CAM)
  #define PINO_TX_PARA_NANO  43 // Pino TX nativo do ESP32-S3 (Header J1)
  #define PINO_RX_DO_NANO    44 // Pino RX nativo do ESP32-S3
  HardwareSerial SerialNano(1);
#else
  #define PINO_TX_PARA_NANO  1  // Pino TX0 nativo do ESP32 clássico
  #define PINO_RX_DO_NANO    3  // Pino RX0 nativo do ESP32 clássico
  #define SerialNano Serial
#endif

// ------------------------------------------------------------------------------------
// CONFIGURAÇÕES DO WI-FI (Conexão na mesma rede do seu computador)
// ------------------------------------------------------------------------------------
const char *ssid = "Apple Network fdd7b9"; // Rede do PC (aberta / sem senha)

WebServer server(80);

// Estado atual do LED para feedback na página
bool estadoLed = false;

// ------------------------------------------------------------------------------------
// PÁGINA WEB EMBUTIDA (HTML5 + CSS Moderno Dark Mode + JavaScript Assíncrono)
// ------------------------------------------------------------------------------------
const char PAGINA_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rover ESP32 -> Nano Serial Test</title>
  <style>
    :root {
      --bg: #0f172a;
      --card: #1e293b;
      --primary: #38bdf8;
      --success: #22c55e;
      --danger: #ef4444;
      --text: #f8fafc;
      --subtext: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
    body {
      background-color: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 20px;
    }
    .card {
      background-color: var(--card);
      border-radius: 16px;
      padding: 30px;
      max-width: 420px;
      width: 100%;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      border: 1px solid #334155;
      text-align: center;
    }
    h1 { font-size: 1.5rem; margin-bottom: 8px; color: var(--primary); }
    p.desc { font-size: 0.9rem; color: var(--subtext); margin-bottom: 25px; }
    
    .status-box {
      background: #0f172a;
      border-radius: 12px;
      padding: 15px;
      margin-bottom: 25px;
      border: 1px solid #334155;
    }
    .led-indicator {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      margin: 0 auto 10px;
      background-color: #334155;
      transition: all 0.3s ease;
      box-shadow: 0 0 0 rgba(0,0,0,0);
    }
    .led-indicator.on {
      background-color: var(--success);
      box-shadow: 0 0 20px var(--success);
    }
    .status-text { font-weight: 600; font-size: 1.1rem; }
    
    .btn-group { display: flex; gap: 12px; }
    button {
      flex: 1;
      padding: 16px 20px;
      font-size: 1rem;
      font-weight: 700;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: transform 0.1s ease, filter 0.2s ease;
    }
    button:active { transform: scale(0.97); }
    .btn-on { background-color: var(--success); color: #022c22; }
    .btn-off { background-color: var(--danger); color: #450a0a; }
    
    .footer {
      margin-top: 25px;
      font-size: 0.8rem;
      color: var(--subtext);
      line-height: 1.4;
    }
    .badge {
      display: inline-block;
      background: #334155;
      padding: 3px 8px;
      border-radius: 6px;
      font-family: monospace;
      color: var(--primary);
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>🚀 Rover ESP32 &rarr; Nano</h1>
    <p class="desc">Teste de Comunicação Serial RX/TX (115200 baud)</p>
    
    <div class="status-box">
      <div id="ledIndicator" class="led-indicator"></div>
      <div id="statusLabel" class="status-text">LED DO NANO: APAGADO</div>
    </div>
    
    <div class="btn-group">
      <button class="btn-on" onclick="enviarComando(1)">LIGAR</button>
      <button class="btn-off" onclick="enviarComando(0)">DESLIGAR</button>
    </div>
    
    <div class="footer">
      Sinal enviado via Wi-Fi ao ESP32 &rarr; cuspidor serial no pino <span class="badge">TX</span> &rarr; pino <span class="badge">RX</span> do Arduino Nano.
    </div>
  </div>

  <script>
    async function enviarComando(estado) {
      try {
        const resp = await fetch(`/led?state=${estado}`);
        const data = await resp.json();
        atualizarUI(data.led);
      } catch (err) {
        console.error('Erro de comunicacao:', err);
      }
    }
    
    function atualizarUI(ativo) {
      const ind = document.getElementById('ledIndicator');
      const lbl = document.getElementById('statusLabel');
      if (ativo) {
        ind.classList.add('on');
        lbl.innerText = 'LED DO NANO: ACESO';
        lbl.style.color = 'var(--success)';
      } else {
        ind.classList.remove('on');
        lbl.innerText = 'LED DO NANO: APAGADO';
        lbl.style.color = 'var(--text)';
      }
    }
  </script>
</body>
</html>
)rawliteral";

// ------------------------------------------------------------------------------------
// HANDLERS DO SERVIDOR WEB
// ------------------------------------------------------------------------------------
void handleRoot() {
  server.send_P(200, "text/html", PAGINA_HTML);
}

void handleLed() {
  if (server.hasArg("state")) {
    String state = server.arg("state");
    
    if (state == "1") {
      estadoLed = true;
      // Envia o caractere '1' e o pacote estruturado pela porta Serial conectada ao Nano
      SerialNano.write('1');
      Serial.println("[ESP32] Enviado comando: '1' (Ligar LED Nano)");
    } else {
      estadoLed = false;
      // Envia o caractere '0' pela porta Serial
      SerialNano.write('0');
      Serial.println("[ESP32] Enviado comando: '0' (Desligar LED Nano)");
    }
    
    // Retorna resposta JSON rápida para o navegador atualizar o status visual
    String jsonResponse = "{\"success\":true,\"led\":" + String(estadoLed ? "true" : "false") + "}";
    server.send(200, "application/json", jsonResponse);
  } else {
    server.send(400, "text/plain", "Parametro 'state' ausente");
  }
}

// ------------------------------------------------------------------------------------
// SETUP E LOOP
// ------------------------------------------------------------------------------------
void setup() {
  // Serial de Debug USB do ESP32
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- [INICIANDO ROVER ESP32 SERIAL TEST] ---");

  // Inicializa a Serial de comunicação física com o Arduino Nano
#if defined(PLACA_ESP32_S3_CAM)
  // No ESP32-S3 usamos HardwareSerial(1) mapeada nos pinos desejados
  SerialNano.begin(115200, SERIAL_8N1, PINO_RX_DO_NANO, PINO_TX_PARA_NANO);
  Serial.printf("[ESP32-S3] Serial UART1 iniciada no TX pino IO%d a 115200 baud\n", PINO_TX_PARA_NANO);
#else
  // No ESP32 clássico usamos a Serial padrão
  SerialNano.begin(115200);
  Serial.println("[ESP32] Serial iniciada no TX GPIO 1 a 115200 baud");
#endif

  // Conecta na mesma rede Wi-Fi do computador (modo Estação - STA)
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid); // Conexão aberta / sem senha

  Serial.print("[WI-FI] Conectando a rede: ");
  Serial.println(ssid);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 30) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }

  // Otimização de baixa latência: desativa suspensão de energia no rádio Wi-Fi
  esp_wifi_set_ps(WIFI_PS_NONE);

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WI-FI] Conectado com sucesso!");
    Serial.print("[WI-FI] Acesse pelo navegador: http://");
    Serial.println(WiFi.localIP());

    // Inicia o serviço mDNS para permitir acesso por http://rover.local
    if (MDNS.begin("rover")) {
      Serial.println("[mDNS] Ou acesse diretamente por: http://rover.local");
    }
  } else {
    Serial.println("\n[WI-FI] Falha ao conectar. Verifique o alcance da rede.");
  }

  // Configuração das rotas HTTP
  server.on("/", HTTP_GET, handleRoot);
  server.on("/led", HTTP_GET, handleLed);
  server.begin();
  Serial.println("[HTTP] Servidor Web ativo e aguardando comandos!");
}

void loop() {
  // Atende as requisições web do celular
  server.handleClient();
}
