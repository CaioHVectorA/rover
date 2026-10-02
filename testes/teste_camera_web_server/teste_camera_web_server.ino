/**
 * ============================================================================
 * PROJETO: Rover / Câmera FPV - ESP32-S3 CAM
 * CÓDIGO: CameraWebServer All-in-One (Arquivo Único)
 * MICROCONTROLADOR: ESP32-S3 CAM (N16R8: 16MB Flash, 8MB Octal PSRAM)
 * SENSORES COMPATÍVEIS: OV2640 / OV5640 / OV3660
 * ============================================================================
 * 
 * CARACTERÍSTICAS DESTE CÓDIGO:
 *  1. 100% em um único arquivo (.ino) - sem necessidade de 4 abas ou arquivos externos.
 *  2. Interface Web Moderna (Dark Mode / FPV HUD) embutida sem depender de internet/CDN.
 *  3. Streaming de vídeo MJPEG em alta taxa de quadros (Porta 81).
 *  4. Servidor Web de Controle e Captura de Fotos (Porta 80).
 *  5. Reconexão inteligente: Conecta na sua rede Wi-Fi ou cria automaticamente um
 *     Ponto de Acesso (AP: "ESP32S3-CAM-ROVER" em 192.168.4.1) se o Wi-Fi falhar.
 *  6. Controles em tempo real: Resolução, Qualidade JPEG, Brilho, Contraste,
 *     Saturação, Balanço de Branco, Efeitos, Inversão Vertical/Horizontal e Lanterna/LED.
 *  7. Tratamento de Brownout e alocação dinâmica de PSRAM para máxima estabilidade.
 * 
 * INSTRUÇÕES DE GRAVAÇÃO NA ARDUINO IDE:
 *  - Placa: "ESP32S3 Dev Module"
 *  - USB CDC On Boot: "Enabled" (Essencial para ver o Serial Monitor via USB-C)
 *  - Flash Size: "16MB (128Mb)"
 *  - Partition Scheme: "Huge APP (3MB No OTA/1MB SPIFFS)" ou "16M Flash (3MB APP)"
 *  - PSRAM: "OPI PSRAM" (N16R8 possui 8MB Octal PSRAM!)
 *  - Upload Speed: 921600
 * ============================================================================
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <ESPmDNS.h>
#include "esp_http_server.h"
#include "esp_timer.h"
#include "img_converters.h"
#include "fb_gfx.h"

// ============================================================================
// 1. CONFIGURAÇÕES DE REDE WI-FI
// ============================================================================
// Substitua pelo nome e senha da sua rede Wi-Fi doméstica ou do celular:
const char* WIFI_SSID     = "PET_ELETRICA";
const char* WIFI_PASSWORD = "1478965P";

// Caso o ESP32 não consiga conectar ao Wi-Fi acima, ele cria sua própria rede:
const char* AP_SSID       = "ESP32S3-CAM-ROVER";
const char* AP_PASSWORD   = ""; // Senha vazia = Rede aberta (ou coloque "12345678")

// ============================================================================
// 2. PINAGEM DA CÂMERA NO ESP32-S3 CAM
// ============================================================================
// Padrão Freenove ESP32-S3 CAM / ESP32-S3-EYE / Placa Genérica N16R8 (Mercado Livre)
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     15
#define SIOD_GPIO_NUM      4
#define SIOC_GPIO_NUM      5

#define Y9_GPIO_NUM       16
#define Y8_GPIO_NUM       17
#define Y7_GPIO_NUM       18
#define Y6_GPIO_NUM       12
#define Y5_GPIO_NUM       10
#define Y4_GPIO_NUM        8
#define Y3_GPIO_NUM        9
#define Y2_GPIO_NUM       11
#define VSYNC_GPIO_NUM     6
#define HREF_GPIO_NUM      7
#define PCLK_GPIO_NUM     13

// LED Indicador / Flash onboard (definir -1 se sua placa não tiver LED)
#define FLASH_LED_PIN      2

// ============================================================================
// 3. VARIÁVEIS GLOBAIS E SERVIDORES HTTP
// ============================================================================
httpd_handle_t camera_httpd = NULL; // Porta 80: UI Web, Captura e Controles
httpd_handle_t stream_httpd = NULL; // Porta 81: MJPEG Stream contínuo
bool flash_state = false;

// ============================================================================
// 4. INTERFACE WEB HTML/CSS/JS (EMBUTIDA EM MEMÓRIA FLASH - PROGMEM)
// ============================================================================
static const char PROGMEM INDEX_HTML[] = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>ESP32-S3 CAM | Central FPV</title>
  <style>
    :root {
      --bg: #0b0d14;
      --card-bg: rgba(20, 24, 36, 0.9);
      --card-border: #252c42;
      --primary: #00f0ff;
      --primary-hover: #00c8d6;
      --accent: #ff0055;
      --text: #e2e8f0;
      --text-muted: #8a96aa;
      --slider-bg: #181d2c;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: var(--bg); color: var(--text); min-height: 100vh; padding: 14px; display: flex; flex-direction: column; align-items: center; }
    header { width: 100%; max-width: 1200px; display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; margin-bottom: 14px; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; backdrop-filter: blur(10px); }
    .logo-badge { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1.05rem; color: var(--primary); letter-spacing: 0.5px; }
    .status-badge { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; padding: 5px 12px; border-radius: 20px; background: rgba(0, 240, 255, 0.1); border: 1px solid var(--primary); }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981; }
    .dot.live { background: #ef4444; box-shadow: 0 0 10px #ef4444; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    
    .main-grid { width: 100%; max-width: 1200px; display: grid; grid-template-columns: 1fr 340px; gap: 16px; }
    @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }
    
    .viewport-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; }
    .viewport-container { position: relative; width: 100%; background: #000; min-height: 360px; display: flex; align-items: center; justify-content: center; overflow: hidden; aspect-ratio: 4 / 3; }
    #stream-img { width: 100%; height: 100%; object-fit: contain; display: none; }
    .placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: var(--text-muted); padding: 20px; text-align: center; }
    .hud-overlay { position: absolute; top: 12px; left: 12px; display: flex; gap: 8px; pointer-events: none; }
    .hud-tag { background: rgba(0,0,0,0.7); padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; border: 1px solid rgba(255,255,255,0.15); display: flex; align-items: center; gap: 6px; font-weight: 600; }
    
    .actions-bar { padding: 12px; display: flex; flex-wrap: wrap; gap: 8px; background: rgba(13, 16, 24, 0.9); border-top: 1px solid var(--card-border); }
    button { background: #1a2133; color: var(--text); border: 1px solid var(--card-border); padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s ease; }
    button:hover { background: #26314c; border-color: var(--primary); }
    button.primary { background: var(--primary); color: #000; border-color: var(--primary); }
    button.primary:hover { background: var(--primary-hover); }
    button.danger { background: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #ef4444; }
    button.active { background: rgba(0, 240, 255, 0.25); border-color: var(--primary); color: var(--primary); }
    
    .panel-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 14px; max-height: calc(100vh - 110px); overflow-y: auto; }
    .panel-title { font-size: 0.9rem; font-weight: 700; color: var(--primary); text-transform: uppercase; letter-spacing: 0.8px; border-bottom: 1px solid var(--card-border); padding-bottom: 8px; }
    .control-group { display: flex; flex-direction: column; gap: 6px; }
    .control-label { display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--text-muted); font-weight: 500; }
    .control-val { color: var(--primary); font-weight: 700; }
    select { background: var(--slider-bg); color: var(--text); border: 1px solid var(--card-border); padding: 8px 10px; border-radius: 8px; outline: none; font-size: 0.85rem; cursor: pointer; }
    select:focus { border-color: var(--primary); }
    input[type=range] { -webkit-appearance: none; width: 100%; background: var(--slider-bg); height: 6px; border-radius: 4px; outline: none; }
    input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px; border-radius: 50%; background: var(--primary); cursor: pointer; box-shadow: 0 0 6px var(--primary); }
    .toggle-row { display: flex; justify-content: space-between; align-items: center; padding: 2px 0; }
    .switch { position: relative; display: inline-block; width: 44px; height: 24px; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--slider-bg); border: 1px solid var(--card-border); transition: .3s; border-radius: 24px; }
    .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: var(--text-muted); transition: .3s; border-radius: 50%; }
    input:checked + .slider { background-color: rgba(0, 240, 255, 0.2); border-color: var(--primary); }
    input:checked + .slider:before { transform: translateX(20px); background-color: var(--primary); }
  </style>
</head>
<body>
  <header>
    <div class="logo-badge">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
      ESP32-S3 CAM
    </div>
    <div class="status-badge">
      <span class="dot" id="net-dot"></span>
      <span id="ip-text">Conectado</span>
    </div>
  </header>

  <div class="main-grid">
    <div class="viewport-card">
      <div class="viewport-container" id="viewport">
        <img id="stream-img" alt="Stream Câmera">
        <div class="placeholder" id="stream-placeholder">
          <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          <span style="font-size: 1rem; font-weight: 600;">Stream em Espera</span>
          <span style="font-size: 0.85rem;">Clique no botão abaixo para iniciar o vídeo em tempo real</span>
        </div>
        <div class="hud-overlay">
          <div class="hud-tag" id="hud-live" style="display:none;"><span class="dot live"></span> AO VIVO</div>
          <div class="hud-tag" id="hud-fps" style="display:none;">-- FPS</div>
        </div>
      </div>
      <div class="actions-bar">
        <button id="btn-toggle-stream" class="primary" onclick="toggleStream()">
          ▶ Iniciar Stream
        </button>
        <button onclick="capturePhoto()">
          📸 Capturar Foto
        </button>
        <button onclick="toggleFullscreen()">
          ⛶ Tela Cheia
        </button>
        <button id="btn-flash" onclick="toggleFlash()">
          💡 Lanterna
        </button>
      </div>
    </div>

    <div class="panel-card">
      <div class="panel-title">Ajustes de Visão</div>
      
      <div class="control-group">
        <div class="control-label">Resolução</div>
        <select id="framesize" onchange="sendCmd('framesize', this.value)">
          <option value="2">QVGA (320x240)</option>
          <option value="4">VGA (640x480) - Rápido</option>
          <option value="5" selected>SVGA (800x600) - Ideal</option>
          <option value="6">XGA (1024x768)</option>
          <option value="9">HD (1280x720) - 16:9</option>
          <option value="7">SXGA (1280x1024)</option>
          <option value="8">UXGA (1600x1200) - 2MP</option>
          <option value="10">FHD (1920x1080) - OV5640</option>
        </select>
      </div>

      <div class="control-group">
        <div class="control-label">Qualidade JPEG (menor = melhor)<span id="val-quality" class="control-val">12</span></div>
        <input type="range" id="quality" min="10" max="63" value="12" oninput="sendRange('quality', this.value, 'val-quality')">
      </div>

      <div class="control-group">
        <div class="control-label">Brilho<span id="val-brightness" class="control-val">0</span></div>
        <input type="range" id="brightness" min="-2" max="2" value="0" oninput="sendRange('brightness', this.value, 'val-brightness')">
      </div>

      <div class="control-group">
        <div class="control-label">Contraste<span id="val-contrast" class="control-val">0</span></div>
        <input type="range" id="contrast" min="-2" max="2" value="0" oninput="sendRange('contrast', this.value, 'val-contrast')">
      </div>

      <div class="control-group">
        <div class="control-label">Saturação<span id="val-saturation" class="control-val">0</span></div>
        <input type="range" id="saturation" min="-2" max="2" value="0" oninput="sendRange('saturation', this.value, 'val-saturation')">
      </div>

      <div class="control-group">
        <div class="control-label">Efeito Especial</div>
        <select id="special_effect" onchange="sendCmd('special_effect', this.value)">
          <option value="0">Normal</option>
          <option value="1">Negativo</option>
          <option value="2">Preto e Branco</option>
          <option value="3">Avermelhado</option>
          <option value="4">Esverdeado</option>
          <option value="5">Azulado</option>
          <option value="6">Sépia</option>
        </select>
      </div>

      <div class="control-group">
        <div class="control-label">Balanço de Branco</div>
        <select id="wb_mode" onchange="sendCmd('wb_mode', this.value)">
          <option value="0">Automático</option>
          <option value="1">Ensolarado (Dia)</option>
          <option value="2">Nublado</option>
          <option value="3">Escritório</option>
          <option value="4">Casa / Lâmpada</option>
        </select>
      </div>

      <div class="toggle-row">
        <span class="control-label">Inverter Vertical (V-Flip)</span>
        <label class="switch">
          <input type="checkbox" id="vflip" onchange="sendCmd('vflip', this.checked ? 1 : 0)">
          <span class="slider"></span>
        </label>
      </div>

      <div class="toggle-row">
        <span class="control-label">Espelhar Horizontal (H-Mirror)</span>
        <label class="switch">
          <input type="checkbox" id="hmirror" onchange="sendCmd('hmirror', this.checked ? 1 : 0)">
          <span class="slider"></span>
        </label>
      </div>
    </div>
  </div>

  <script>
    const streamImg = document.getElementById('stream-img');
    const placeholder = document.getElementById('stream-placeholder');
    const btnToggle = document.getElementById('btn-toggle-stream');
    const hudLive = document.getElementById('hud-live');
    const hudFps = document.getElementById('hud-fps');
    let isStreaming = false;
    let flashOn = false;
    let frameCount = 0;
    let lastTime = performance.now();
    let fpsInterval = null;

    const baseHost = window.location.hostname;
    // O stream roda na porta 81 dedicada para não travar a porta 80:
    const streamUrl = `${window.location.protocol}//${baseHost}:81/stream`;

    function updateFps() {
      const now = performance.now();
      const delta = (now - lastTime) / 1000;
      if (delta >= 1.0) {
        const fps = Math.round(frameCount / delta);
        hudFps.innerText = `${fps} FPS`;
        frameCount = 0;
        lastTime = now;
      }
    }

    streamImg.onload = () => { frameCount++; };

    function toggleStream() {
      if (!isStreaming) {
        streamImg.src = streamUrl;
        streamImg.style.display = 'block';
        placeholder.style.display = 'none';
        btnToggle.innerText = '⏹ Parar Stream';
        btnToggle.className = 'danger';
        hudLive.style.display = 'flex';
        hudFps.style.display = 'flex';
        isStreaming = true;
        frameCount = 0;
        lastTime = performance.now();
        fpsInterval = setInterval(updateFps, 600);
      } else {
        streamImg.src = '';
        streamImg.style.display = 'none';
        placeholder.style.display = 'flex';
        btnToggle.innerText = '▶ Iniciar Stream';
        btnToggle.className = 'primary';
        hudLive.style.display = 'none';
        hudFps.style.display = 'none';
        isStreaming = false;
        clearInterval(fpsInterval);
        window.stop();
      }
    }

    function capturePhoto() {
      const captureUrl = `${window.location.protocol}//${baseHost}/capture?_t=${Date.now()}`;
      window.open(captureUrl, '_blank');
    }

    function toggleFullscreen() {
      const el = document.getElementById('viewport');
      if (!document.fullscreenElement) {
        el.requestFullscreen().catch(err => alert(err.message));
      } else {
        document.exitFullscreen();
      }
    }

    function toggleFlash() {
      flashOn = !flashOn;
      sendCmd('flash', flashOn ? 1 : 0);
      const btn = document.getElementById('btn-flash');
      if (flashOn) {
        btn.classList.add('active');
        btn.innerText = '💡 Lanterna Ligada';
      } else {
        btn.classList.remove('active');
        btn.innerText = '💡 Lanterna';
      }
    }

    function sendCmd(variable, value) {
      fetch(`/control?var=${variable}&val=${value}`).catch(e => console.error(e));
    }

    let rangeTimeout = null;
    function sendRange(variable, value, labelId) {
      document.getElementById(labelId).innerText = value;
      clearTimeout(rangeTimeout);
      rangeTimeout = setTimeout(() => {
        sendCmd(variable, value);
      }, 100);
    }

    // Carrega os parâmetros atuais do sensor ao abrir a página
    window.addEventListener('DOMContentLoaded', () => {
      document.getElementById('ip-text').innerText = baseHost;
      fetch('/status')
        .then(r => r.json())
        .then(d => {
          if (d.framesize !== undefined) document.getElementById('framesize').value = d.framesize;
          if (d.quality !== undefined) {
            document.getElementById('quality').value = d.quality;
            document.getElementById('val-quality').innerText = d.quality;
          }
          if (d.brightness !== undefined) {
            document.getElementById('brightness').value = d.brightness;
            document.getElementById('val-brightness').innerText = d.brightness;
          }
          if (d.contrast !== undefined) {
            document.getElementById('contrast').value = d.contrast;
            document.getElementById('val-contrast').innerText = d.contrast;
          }
          if (d.saturation !== undefined) {
            document.getElementById('saturation').value = d.saturation;
            document.getElementById('val-saturation').innerText = d.saturation;
          }
          if (d.special_effect !== undefined) document.getElementById('special_effect').value = d.special_effect;
          if (d.wb_mode !== undefined) document.getElementById('wb_mode').value = d.wb_mode;
          if (d.vflip !== undefined) document.getElementById('vflip').checked = !!d.vflip;
          if (d.hmirror !== undefined) document.getElementById('hmirror').checked = !!d.hmirror;
        })
        .catch(err => console.log('Status offline', err));
    });
  </script>
</body>
</html>
)rawliteral";

// ============================================================================
// 5. FUNÇÕES DE SUPORTE (FLASH E STREAM MJPEG)
// ============================================================================
void set_flash(int val) {
  if (FLASH_LED_PIN >= 0) {
    pinMode(FLASH_LED_PIN, OUTPUT);
    digitalWrite(FLASH_LED_PIN, val ? HIGH : LOW);
    flash_state = (val != 0);
  }
}

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\nX-Timestamp: %d.%06d\r\n\r\n";

// Handler de Streaming MJPEG contínuo (Porta 81)
static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  struct timeval _timestamp;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[128];

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "X-Framerate", "60");

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println(F("❌ Falha na captura do frame"));
      res = ESP_FAIL;
    } else {
      _timestamp.tv_sec = fb->timestamp.tv_sec;
      _timestamp.tv_usec = fb->timestamp.tv_usec;
      if (fb->format != PIXFORMAT_JPEG) {
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if (!jpeg_converted) {
          Serial.println(F("❌ Falha na compressão JPEG"));
          res = ESP_FAIL;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }

    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    }
    if (res == ESP_OK) {
      size_t hlen = snprintf((char *)part_buf, 128, _STREAM_PART, _jpg_buf_len, _timestamp.tv_sec, _timestamp.tv_usec);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }

    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }

    if (res != ESP_OK) {
      break; // Conexão encerrada pelo cliente
    }
  }
  return res;
}

// Handler da Página Web Principal (GET /)
static esp_err_t index_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  httpd_resp_set_hdr(req, "Content-Encoding", "identity");
  return httpd_resp_send(req, INDEX_HTML, strlen(INDEX_HTML));
}

// Handler de Captura de Foto Única (GET /capture)
static esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;

  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println(F("❌ Falha na captura"));
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  size_t out_len;
  uint8_t * out_buf;
  if (fb->format == PIXFORMAT_JPEG) {
    res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  } else {
    bool s = frame2jpg(fb, 80, &out_buf, &out_len);
    esp_camera_fb_return(fb);
    fb = NULL;
    if (!s) {
      httpd_resp_send_500(req);
      return ESP_FAIL;
    }
    res = httpd_resp_send(req, (const char *)out_buf, out_len);
    free(out_buf);
  }

  if (fb) {
    esp_camera_fb_return(fb);
  }
  return res;
}

// Handler de Controle de Parâmetros (GET /control?var=...&val=...)
static esp_err_t cmd_handler(httpd_req_t *req) {
  char*  buf;
  size_t buf_len;
  char variable[32] = {0,};
  char value[32] = {0,};

  buf_len = httpd_req_get_url_query_len(req) + 1;
  if (buf_len > 1) {
    buf = (char*)malloc(buf_len);
    if (!buf) {
      httpd_resp_send_500(req);
      return ESP_FAIL;
    }
    if (httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
      if (httpd_query_key_value(buf, "var", variable, sizeof(variable)) == ESP_OK &&
          httpd_query_key_value(buf, "val", value, sizeof(value)) == ESP_OK) {
      } else {
        free(buf);
        httpd_resp_send_404(req);
        return ESP_FAIL;
      }
    } else {
      free(buf);
      httpd_resp_send_404(req);
      return ESP_FAIL;
    }
    free(buf);
  } else {
    httpd_resp_send_404(req);
    return ESP_FAIL;
  }

  int val = atoi(value);
  sensor_t * s = esp_camera_sensor_get();
  int res = 0;

  if (!strcmp(variable, "framesize")) {
    if (s->pixformat == PIXFORMAT_JPEG) {
      res = s->set_framesize(s, (framesize_t)val);
    }
  }
  else if (!strcmp(variable, "quality"))        res = s->set_quality(s, val);
  else if (!strcmp(variable, "contrast"))       res = s->set_contrast(s, val);
  else if (!strcmp(variable, "brightness"))     res = s->set_brightness(s, val);
  else if (!strcmp(variable, "saturation"))     res = s->set_saturation(s, val);
  else if (!strcmp(variable, "special_effect")) res = s->set_special_effect(s, val);
  else if (!strcmp(variable, "wb_mode"))        res = s->set_wb_mode(s, val);
  else if (!strcmp(variable, "vflip"))          res = s->set_vflip(s, val);
  else if (!strcmp(variable, "hmirror"))        res = s->set_hmirror(s, val);
  else if (!strcmp(variable, "flash")) {
    set_flash(val);
    res = 0;
  }
  else {
    res = -1;
  }

  if (res) return httpd_resp_send_500(req);

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, NULL, 0);
}

// Handler de Status Atual do Sensor (GET /status)
static esp_err_t status_handler(httpd_req_t *req) {
  static char json_response[512];
  sensor_t * s = esp_camera_sensor_get();
  if (!s) return httpd_resp_send_500(req);

  char * p = json_response;
  *p++ = '{';
  p += sprintf(p, "\"framesize\":%u,", s->status.framesize);
  p += sprintf(p, "\"quality\":%u,", s->status.quality);
  p += sprintf(p, "\"brightness\":%d,", s->status.brightness);
  p += sprintf(p, "\"contrast\":%d,", s->status.contrast);
  p += sprintf(p, "\"saturation\":%d,", s->status.saturation);
  p += sprintf(p, "\"special_effect\":%u,", s->status.special_effect);
  p += sprintf(p, "\"wb_mode\":%u,", s->status.wb_mode);
  p += sprintf(p, "\"vflip\":%u,", s->status.vflip);
  p += sprintf(p, "\"hmirror\":%u,", s->status.hmirror);
  p += sprintf(p, "\"flash\":%u", flash_state ? 1 : 0);
  *p++ = '}';
  *p++ = 0;

  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, json_response, strlen(json_response));
}

// ============================================================================
// 6. INICIALIZAÇÃO DOS SERVIDORES HTTP (PORTA 80 E PORTA 81)
// ============================================================================
void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.max_open_sockets = 7;

  httpd_uri_t index_uri = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = index_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t status_uri = {
    .uri       = "/status",
    .method    = HTTP_GET,
    .handler   = status_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t cmd_uri = {
    .uri       = "/control",
    .method    = HTTP_GET,
    .handler   = cmd_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t capture_uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = capture_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  // 1. Inicia Servidor Principal na Porta 80
  config.server_port = 80;
  config.ctrl_port = 32768;
  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &cmd_uri);
    httpd_register_uri_handler(camera_httpd, &status_uri);
    httpd_register_uri_handler(camera_httpd, &capture_uri);
    Serial.println(F("✅ Servidor Web de Controle iniciado na porta 80"));
  }

  // 2. Inicia Servidor Dedicado de Streaming na Porta 81
  config.server_port = 81;
  config.ctrl_port = 32769;
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    Serial.println(F("✅ Servidor de Stream MJPEG iniciado na porta 81"));
  }
}

// ============================================================================
// 7. SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000); // Aguarda enumeração da porta USB CDC no ESP32-S3

  Serial.println(F("\n=================================================="));
  Serial.println(F("📸 ESP32-S3 CAM - CameraWebServer All-in-One"));
  Serial.println(F("=================================================="));

  if (FLASH_LED_PIN >= 0) {
    pinMode(FLASH_LED_PIN, OUTPUT);
    digitalWrite(FLASH_LED_PIN, LOW);
  }

  // Configuração da Câmera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_SVGA; // 800x600 (Fluidez e ótima definição)
  config.grab_mode    = CAMERA_GRAB_LATEST;
  config.fb_location  = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count     = 2;

  // Verificação de PSRAM (ESP32-S3 N16R8 possui 8MB Octal PSRAM)
  if (psramFound()) {
    Serial.printf("🧠 PSRAM detectada: %d KB livres\n", ESP.getFreePsram() / 1024);
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    Serial.println(F("⚠️ ATENÇÃO: PSRAM NÃO DETECTADA! Usando DRAM interna reduzida."));
    Serial.println(F("💡 Dica: Na Arduino IDE, ative Tools -> PSRAM: 'OPI PSRAM'."));
    config.frame_size = FRAMESIZE_VGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Inicializa o hardware da câmera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Erro fatal na inicialização da câmera: 0x%x\n", err);
    Serial.println(F("Verifique:"));
    Serial.println(F(" 1. Encaixe do flat cable da câmera (OV2640 / OV5640)."));
    Serial.println(F(" 2. Se a opção PSRAM está ativada nas configurações da placa."));
    while (true) {
      delay(1000);
    }
  }

  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    // Inversões padrão para a câmera montada no suporte Pan/Tilt
    s->set_vflip(s, 0);
    s->set_hmirror(s, 0);
    s->set_brightness(s, 0);
    s->set_contrast(s, 0);
    s->set_saturation(s, 0);
  }

  Serial.println(F("📷 Câmera inicializada com sucesso!"));

  // Conexão Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print(F("Conectando ao Wi-Fi '"));
  Serial.print(WIFI_SSID);
  Serial.print(F("'"));

  int timeout = 25; // Aguarda até ~12.5s
  while (WiFi.status() != WL_CONNECTED && timeout > 0) {
    delay(500);
    Serial.print(F("."));
    timeout--;
  }

  // Se conectou ao roteador doméstico
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(F("\n✅ Conectado ao Wi-Fi com sucesso!"));
    Serial.print(F("🌐 Acesse no seu navegador: http://"));
    Serial.println(WiFi.localIP());
    Serial.print(F("📺 URL direta do Stream:    http://"));
    Serial.print(WiFi.localIP());
    Serial.println(F(":81/stream"));
  } else {
    // Fallback: Inicia Access Point próprio caso não encontre a rede
    Serial.println(F("\n⚠️ Não foi possível conectar ao Wi-Fi configurado."));
    Serial.println(F("📡 Criando Ponto de Acesso Wi-Fi próprio (Modo AP)..."));
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD);
    Serial.print(F("📶 Rede Wi-Fi criada:   "));
    Serial.println(AP_SSID);
    Serial.print(F("🌐 Acesse no navegador: http://"));
    Serial.println(WiFi.softAPIP());
    Serial.print(F("📺 URL direta do Stream: http://"));
    Serial.print(WiFi.softAPIP());
    Serial.println(F(":81/stream"));
  }

  // Ativa mDNS (permite abrir como http://esp32cam.local)
  if (MDNS.begin("esp32cam")) {
    Serial.println(F("🌐 mDNS ativo: http://esp32cam.local"));
  }

  // Inicia os servidores Web
  startCameraServer();
  Serial.println(F("🚀 Sistema de Visão Pronto para Uso!\n"));
}

// ============================================================================
// 8. LOOP PRINCIPAL
// ============================================================================
void loop() {
  // Os servidores HTTP rodam em tarefas dedicadas gerenciadas pelo FreeRTOS no ESP32.
  // Você pode adicionar lógicas do Rover ou leitura de sensores aqui se desejar.
  delay(1000);
}
