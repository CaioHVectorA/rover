#pragma once
// ====================================================================================
// PAINEL WEB COMPACTO E DIRETO
// - Modos: D-Pad Tátil & Joystick Virtual Proporcional (sem bugs)
// - Configurações: Inversão de Eixos, Velocidade Fluida, Passo e Qualidade de Vídeo
// ====================================================================================
#include <Arduino.h>

static const char PAINEL_HTML[] PROGMEM = R"HTML(<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Rover FPV Cockpit</title>
<style>
:root {
  --bg: #090c12; --card: #121824; --border: #243044;
  --text: #e6edf7; --sub: #8191ab; --accent: #38bdf8;
  --green: #22c55e; --red: #ef4444; --orange: #f59e0b;
}
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
body {
  background: var(--bg); color: var(--text);
  font: 13px system-ui, -apple-system, sans-serif;
  min-height: 100vh; display: flex; flex-direction: column; align-items: center;
  padding: 8px;
}
.app-container {
  width: 100%; max-width: 480px; display: flex; flex-direction: column; gap: 8px;
}
/* Top bar */
header {
  display: flex; justify-content: space-between; align-items: center;
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 12px;
}
header .title { font-weight: 700; font-size: 14px; color: var(--accent); }
.status-pill {
  padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;
  border: 1px solid #334155; color: var(--sub);
}
.status-pill.ok { color: var(--green); border-color: #166534; }
.status-pill.bad { color: var(--red); border-color: #991b1b; }

.btn-cfg {
  background: #1e293b; border: 1px solid var(--border); color: var(--text);
  padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer;
}
.btn-cfg:active { background: var(--accent); color: #000; }

/* Bloco do Vídeo Compacto */
.video-card {
  background: #000; border: 1px solid var(--border); border-radius: 8px;
  overflow: hidden; position: relative; display: flex; align-items: center;
  justify-content: center; min-height: 200px; max-height: 36vh;
}
#vid { width: 100%; height: 100%; object-fit: contain; display: block; }
.cam-btn-overlay { position: absolute; top: 6px; right: 6px; display: flex; gap: 6px; z-index: 10; }
.btn-mini {
  background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer;
  backdrop-filter: blur(4px);
}
.btn-mini:active { background: var(--accent); color: #000; }

/* Seletor de Modo (D-Pad vs Joystick) */
.mode-switch {
  display: flex; gap: 6px; width: 100%; background: #101622;
  border: 1px solid var(--border); border-radius: 6px; padding: 3px;
}
.btn-mode {
  flex: 1; background: transparent; border: none; color: var(--sub);
  padding: 6px; border-radius: 4px; font-weight: 700; font-size: 11px; cursor: pointer;
}
.btn-mode.active {
  background: #1e293b; color: var(--accent); box-shadow: 0 1px 3px rgba(0,0,0,0.4);
}

/* Grid de Controles Lado a Lado */
.controls-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; width: 100%; }
.ctrl-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: 8px; display: flex; flex-direction: column; align-items: center; gap: 6px;
}
.ctrl-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--sub); letter-spacing: 0.5px; }

/* D-pad 3x3 */
.dpad {
  display: grid; grid-template-columns: repeat(3, 44px); grid-template-rows: repeat(3, 42px);
  gap: 4px; justify-content: center;
}
.dpad button {
  height: 42px; background: #1c2638; border: 1px solid var(--border);
  color: var(--text); border-radius: 6px; font-size: 16px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  touch-action: none; user-select: none;
}
.dpad button:active { background: var(--accent); color: #000; border-color: #38bdf8; }
.dpad-center { background: #232f45 !important; font-size: 11px !important; color: var(--sub) !important; }

/* Joysticks Virtuais */
.joy-zone {
  width: 120px; height: 120px; border-radius: 50%; background: radial-gradient(#1c2638 40%, #101622 100%);
  border: 2px solid var(--border); position: relative; touch-action: none;
  display: flex; align-items: center; justify-content: center; user-select: none;
}
.joy-knob {
  width: 44px; height: 44px; border-radius: 50%; background: #2a384f;
  border: 2px solid var(--accent); position: absolute; pointer-events: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.6);
}

/* Sliders Rápidos */
.slider-group { width: 100%; display: flex; flex-direction: column; gap: 6px; }
.slider-item { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
.slider-item label { font-size: 11px; color: var(--sub); width: 45px; }
.slider-item input[type=range] { flex: 1; height: 5px; accent-color: var(--accent); }
.slider-item output { font-size: 11px; font-weight: 600; min-width: 35px; text-align: right; color: var(--accent); }

/* Barra Inferior com Botões Rápidos */
.bottom-bar { display: flex; gap: 8px; width: 100%; }
.btn-stop {
  flex: 1; background: #7f1d1d; border: 1px solid #dc2626; color: #fecaca;
  padding: 10px; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;
}
.btn-stop:active { background: #b91c1c; }
.btn-center {
  flex: 1; background: #1e293b; border: 1px solid var(--border); color: var(--text);
  padding: 10px; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;
}
.btn-center:active { background: #334155; }

/* Modal de Configurações */
.modal-overlay {
  display: none; position: fixed; inset: 0; background: rgba(0, 0, 0, 0.75);
  z-index: 100; align-items: center; justify-content: center; padding: 16px;
}
.modal-overlay.active { display: flex; }
.modal-box {
  background: var(--card); border: 1px solid var(--border); border-radius: 10px;
  width: 100%; max-width: 380px; padding: 14px; display: flex; flex-direction: column; gap: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.6); max-height: 90vh; overflow-y: auto;
}
.modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
.modal-header h3 { font-size: 13px; font-weight: 700; color: var(--accent); }
.modal-close { background: transparent; border: none; color: var(--sub); font-size: 18px; cursor: pointer; padding: 2px 6px; }
.modal-close:hover { color: #fff; }

.cfg-sec { font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase; margin-top: 4px; }
.chk-row { display: flex; gap: 12px; align-items: center; font-size: 11px; color: var(--text); }
.chk-row label { display: flex; align-items: center; gap: 4px; cursor: pointer; }
.preset-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-top: 2px; }
.btn-preset {
  background: #1c2638; border: 1px solid var(--border); color: var(--text);
  padding: 5px 2px; border-radius: 4px; font-size: 10px; cursor: pointer; text-align: center;
}
.btn-preset:active { background: var(--accent); color: #000; font-weight: 700; }
.controls-grid.hidden { display: none !important; }

/* Cockpit FPV em Modo Horizontal (Mobile Landscape) */
@media (orientation: landscape) {
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    overflow: hidden !important;
  }
  .app-container {
    max-width: 100vw !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    display: grid !important;
    grid-template-columns: minmax(130px, 180px) minmax(0, 1fr) minmax(130px, 180px) !important;
    grid-template-rows: 32px minmax(0, 1fr) 34px !important;
    gap: 4px !important;
    padding: 4px !important;
    box-sizing: border-box !important;
  }
  header {
    grid-column: 2 !important;
    grid-row: 1 !important;
    padding: 2px 8px !important;
    height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
  }
  header .title { font-size: 11px !important; }
  .video-card {
    grid-column: 2 !important;
    grid-row: 2 !important;
    min-height: 0 !important;
    min-width: 0 !important;
    max-height: 100% !important;
    height: 100% !important;
    width: 100% !important;
    border-radius: 6px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
    background: #000 !important;
  }
  #vid {
    max-width: 100% !important;
    max-height: 100% !important;
    width: auto !important;
    height: auto !important;
    object-fit: contain !important;
    display: block !important;
  }
  .bottom-bar {
    grid-column: 2 !important;
    grid-row: 3 !important;
    gap: 6px !important;
    height: 34px !important;
    margin: 0 !important;
  }
  .btn-stop, .btn-center {
    padding: 6px 4px !important;
    font-size: 11px !important;
  }
  .mode-switch {
    display: none !important;
  }
  .header-mode-switch {
    display: inline-flex !important;
  }
  #btnHdrDiag {
    display: inline-block !important;
  }
  .controls-grid {
    display: contents !important;
  }
  .controls-grid.hidden {
    display: none !important;
  }
  .card-drive {
    grid-column: 1 !important;
    grid-row: 1 / 4 !important;
    height: 100% !important;
    max-height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-evenly !important;
    align-items: center !important;
    padding: 4px !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
  }
  .card-pt {
    grid-column: 3 !important;
    grid-row: 1 / 4 !important;
    height: 100% !important;
    max-height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-evenly !important;
    align-items: center !important;
    padding: 4px !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
  }
  .dpad {
    display: grid !important;
    grid-template-columns: repeat(3, 38px) !important;
    grid-template-rows: repeat(3, 35px) !important;
    gap: 3px !important;
    justify-content: center !important;
  }
  .dpad button { height: 35px !important; font-size: 14px !important; }
  .joy-zone {
    width: 100px !important;
    height: 100px !important;
  }
  .joy-knob {
    width: 38px !important;
    height: 38px !important;
  }
  .slider-group {
    width: 90% !important;
    margin-top: 2px !important;
    gap: 2px !important;
  }
  .slider-item {
    font-size: 10px !important;
    gap: 4px !important;
  }
  .slider-item label {
    font-size: 10px !important;
    width: 28px !important;
  }
  .slider-item output {
    font-size: 10px !important;
    min-width: 26px !important;
  }
  .diag-card {
    position: absolute !important;
    top: 36px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 90% !important;
    max-width: 440px !important;
    z-index: 50 !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.85) !important;
  }
  .diag-card:not([open]) {
    display: none !important;
  }
}
</style>
</head>
<body>

<div class="app-container">
  <header>
    <div style="display:flex;align-items:center;gap:6px">
      <div class="title">🚀 ROVER</div>
      <div class="header-mode-switch" style="display:none;gap:3px">
        <button id="btnHdrDpad" class="btn-mode active" style="padding:2px 6px;font-size:10px" onclick="setModo('dpad')">🔲 D-Pad</button>
        <button id="btnHdrJoy" class="btn-mode" style="padding:2px 6px;font-size:10px" onclick="setModo('joy')">🕹️ Joy</button>
      </div>
    </div>
    <div style="display:flex;gap:5px;align-items:center">
      <button class="btn-cfg" id="btnHdrDiag" onclick="toggleDiag()" title="Diagnóstico de Bancada" style="display:none">🔧</button>
      <span class="status-pill" id="stNano">NANO</span>
      <span id="stBat" style="font-weight:700;color:var(--green)">-- V</span>
      <span class="status-pill" id="stWs">WS</span>
      <button class="btn-cfg" onclick="toggleModal(true)">⚙️ Config</button>
    </div>
  </header>

  <!-- Janela de Vídeo -->
  <div class="video-card">
    <div class="cam-btn-overlay">
      <button class="btn-mini" id="btnCamPresetQuick" onclick="ciclarPresetCam()" title="Qualidade da Câmera">❄️ Frio</button>
      <button class="btn-mini" onclick="girarRotacao()">↻ Girar</button>
      <button class="btn-mini" onclick="recarregarVideo()">▶ Vídeo</button>
    </div>
    <img id="vid" src="" alt="Vídeo ao vivo">
  </div>

  <!-- Barra de Diagnóstico de Bancada (retrátil) -->
  <details class="ctrl-card diag-card" id="cardDiag" style="width:100%;padding:6px 10px;">
    <summary style="display:flex;justify-content:space-between;align-items:center;width:100%;cursor:pointer;list-style:none;">
      <span class="ctrl-title">🔧 Diagnóstico Bancada & LED (D13) ▾</span>
      <span id="stLed" class="status-pill">LED OFF</span>
    </summary>
    <div style="width:100%;margin-top:6px;display:flex;flex-direction:column;gap:6px;">
      <div style="display:flex;gap:6px;width:100%;">
        <button class="btn-preset" style="flex:1" onclick="setLed(1)">Ligar LED</button>
        <button class="btn-preset" style="flex:1" onclick="setLed(0)">Desligar LED</button>
        <button id="btnLed2" class="btn-preset" style="flex:1" onclick="setLed(2)">Alternar</button>
        <button id="btnPing" class="btn-preset" style="flex:1" onclick="pingNano()">Ping <span id="rttPing"></span></button>
      </div>
      <div style="display:flex;gap:6px;width:100%;">
        <button class="btn-preset" style="flex:1;background:#1e3a2b;color:#4ade80" onclick="testeMotor(150,150,1000)">4 Motores 1s</button>
        <button class="btn-preset" style="flex:1" onclick="testeMotor(-150,-150,1000)">Ré 1s</button>
        <button class="btn-preset" style="flex:1" onclick="testeMotor(-150,150,800)">Giro Esq</button>
        <button class="btn-preset" style="flex:1" onclick="testeMotor(150,-150,800)">Giro Dir</button>
      </div>
      <div style="display:flex;gap:6px;width:100%;align-items:center;">
        <span style="font-size:10px;color:var(--sub);white-space:nowrap">Fio TX ESP &rarr; Nano:</span>
        <button id="btnTxInv" class="btn-preset" style="flex:1;font-size:10px" onclick="alternarTxInv()">Polaridade: carregando...</button>
      </div>
    </div>
  </details>

  <!-- Alternador de Modo de Pilotagem -->
  <div class="mode-switch">
    <button id="btnModoDpad" class="btn-mode active" onclick="setModo('dpad')">🔲 Modo Botões D-Pad</button>
    <button id="btnModoJoy" class="btn-mode" onclick="setModo('joy')">🕹️ Modo Joysticks Virtuais</button>
  </div>

  <!-- MODO 1: D-PAD TÁTIL -->
  <div id="viewDpad" class="controls-grid">
    <!-- Tração 4WD -->
    <div class="ctrl-card card-drive">
      <div class="ctrl-title">Tração 4WD</div>
      <div class="dpad">
        <span></span>
        <button id="btnFrente" onpointerdown="drive(1,0)" onpointerup="drive(0,0)" onpointerleave="drive(0,0)" onpointercancel="drive(0,0)">▲</button>
        <span></span>
        <button id="btnEsq" onpointerdown="drive(0,-1)" onpointerup="drive(0,0)" onpointerleave="drive(0,0)" onpointercancel="drive(0,0)">◄</button>
        <button class="dpad-center" onclick="drive(0,0)">■</button>
        <button id="btnDir" onpointerdown="drive(0,1)" onpointerup="drive(0,0)" onpointerleave="drive(0,0)" onpointercancel="drive(0,0)">►</button>
        <span></span>
        <button id="btnRe" onpointerdown="drive(-1,0)" onpointerup="drive(0,0)" onpointerleave="drive(0,0)" onpointercancel="drive(0,0)">▼</button>
        <span></span>
      </div>
      <div class="slider-group" style="margin-top:4px">
        <div class="slider-item">
          <label>PWM</label>
          <input type="range" id="rngPwm" min="0" max="255" value="120" oninput="outPwm.value=this.value; rngPwmJoy.value=this.value; outPwmJoy.value=this.value;">
          <output id="outPwm">120</output>
        </div>
      </div>
    </div>

    <!-- Pan / Tilt -->
    <div class="ctrl-card card-pt">
      <div class="ctrl-title">Pan / Tilt</div>
      <div class="dpad">
        <span></span>
        <button onpointerdown="stepTilt(1)" onpointerup="stopPT()" onpointerleave="stopPT()" onpointercancel="stopPT()">▲</button>
        <span></span>
        <button onpointerdown="stepPan(1)" onpointerup="stopPT()" onpointerleave="stopPT()" onpointercancel="stopPT()">◄</button>
        <button class="dpad-center" onclick="centroPT()">⌖</button>
        <button onpointerdown="stepPan(-1)" onpointerup="stopPT()" onpointerleave="stopPT()" onpointercancel="stopPT()">►</button>
        <span></span>
        <button onpointerdown="stepTilt(-1)" onpointerup="stopPT()" onpointerleave="stopPT()" onpointercancel="stopPT()">▼</button>
        <span></span>
      </div>
      <div class="slider-group" style="margin-top:4px">
        <div class="slider-item">
          <label>Pan</label>
          <input type="range" id="rngPan" min="30" max="150" value="90" oninput="setPanDirect(this.value)">
          <output id="outPan">90°</output>
        </div>
        <div class="slider-item">
          <label>Tilt</label>
          <input type="range" id="rngTilt" min="0" max="155" value="90" oninput="setTiltDirect(this.value)">
          <output id="outTilt">90°</output>
        </div>
      </div>
    </div>
  </div>

  <!-- MODO 2: JOYSTICKS VIRTUAIS PROPORCIONAIS (OCULTO POR PADRÃO) -->
  <div id="viewJoy" class="controls-grid hidden">
    <!-- Joy Tração 4WD -->
    <div class="ctrl-card card-drive">
      <div class="ctrl-title">Tração 4WD</div>
      <div class="joy-zone" id="joyDriveBase">
        <div class="joy-knob" id="joyDriveKnob"></div>
      </div>
      <div class="slider-group" style="margin-top:4px">
        <div class="slider-item">
          <label>PWM</label>
          <input type="range" id="rngPwmJoy" min="0" max="255" value="120" oninput="outPwmJoy.value=this.value; rngPwm.value=this.value; outPwm.value=this.value;">
          <output id="outPwmJoy">120</output>
        </div>
      </div>
    </div>

    <!-- Joy Pan / Tilt -->
    <div class="ctrl-card card-pt">
      <div class="ctrl-title">Pan / Tilt</div>
      <div class="joy-zone" id="joyPTBase">
        <div class="joy-knob" id="joyPTKnob"></div>
      </div>
      <div style="display:flex;width:100%;justify-content:space-between;margin-top:4px;font-size:11px;color:var(--accent)">
        <span>Pan: <b id="lblJoyPan">90°</b></span>
        <span>Tilt: <b id="lblJoyTilt">90°</b></span>
      </div>
    </div>
  </div>

  <!-- Barra Inferior de Ações -->
  <div class="bottom-bar">
    <button class="btn-center" onclick="centroPT()">⌖ Centralizar Câmera</button>
    <button class="btn-stop" onclick="parada()">PARADA IMEDIATA</button>
  </div>
</div>

<!-- Modal / Tooltip de Configurações Avançadas -->
<div class="modal-overlay" id="modalCfg" onclick="if(event.target===this) toggleModal(false)">
  <div class="modal-box">
    <div class="modal-header">
      <h3>⚙️ Configurações do Rover</h3>
      <button class="modal-close" onclick="toggleModal(false)">✕</button>
    </div>

    <!-- Seção de Vídeo -->
    <div class="cfg-sec">📹 Qualidade de Vídeo (OV5640)</div>
    <div class="slider-item">
      <label style="width:70px">Resolução</label>
      <select id="selPresetCam" onchange="mudarPresetCam(this.value)" style="flex:1;background:#1c2638;color:#fff;border:1px solid var(--border);padding:5px;border-radius:4px;font-size:11px">
        <option value="frio">Frio (QVGA 320x240)</option>
        <option value="equilibrado">Equilibrado (VGA 640x480)</option>
        <option value="qualidade">Qualidade (SVGA 800x600)</option>
        <option value="maximo">Máximo (HD 1280x720 - Alta Def.)</option>
      </select>
    </div>

    <!-- Seção de Inversão de Eixos -->
    <div class="cfg-sec">🔄 Inversão de Eixos dos Servos</div>
    <div class="chk-row">
      <label><input type="checkbox" id="chkInvPan" onchange="invPan=this.checked"> Inverter Pan (Horizontal)</label>
      <label><input type="checkbox" id="chkInvTilt" onchange="invTilt=this.checked"> Inverter Tilt (Vertical)</label>
    </div>

    <!-- Seção de Velocidade e Fluidez dos Servos -->
    <div class="cfg-sec">⚡ Velocidade e Movimento dos Servos</div>
    <div class="slider-item">
      <label style="width:75px">Velocidade</label>
      <input type="range" id="rngVel" min="60" max="600" step="20" value="420" oninput="aplicarVel(this.value)">
      <output id="outVel">420°/s</output>
    </div>
    <div class="preset-row">
      <button class="btn-preset" onclick="aplicarVel(150)">150°/s</button>
      <button class="btn-preset" onclick="aplicarVel(280)">280°/s</button>
      <button class="btn-preset" onclick="aplicarVel(420)">420°/s</button>
      <button class="btn-preset" onclick="aplicarVel(600)">Máx 600°/s</button>
    </div>

    <div class="slider-item" style="margin-top:6px">
      <label style="width:75px">Passo D-Pad</label>
      <input type="range" id="rngPasso" min="2" max="25" step="1" value="8" oninput="passoGraus=parseInt(this.value); outPasso.value=this.value+'°'">
      <output id="outPasso">8°</output>
    </div>
    <div style="font-size:10px;color:var(--sub)">
      * Passo maior + repetição rápida tornam o movimento do D-Pad muito mais veloz e contínuo.
    </div>
  </div>
</div>

<script>
let ws = null;
let pan = 90;
let tilt = 90;
let velServo = 420;   // Velocidade padrao dos servos (graus/s)
let passoGraus = 8;   // Passo por toque no D-Pad (graus)
let invPan = false;   // Inversao Pan
let invTilt = false;  // Inversao Tilt
let rotAtual = 270;
let ptTimer = null;
let modoAtual = 'dpad';
let limites = {panMin:30, panMax:150, tiltMin:0, tiltMax:155};
let soIda = false;
let testeMotorTimer = null;
let testeMotorFim = null;

function setModo(m) {
  modoAtual = m;
  parada();
  const isDpad = (m === 'dpad');
  document.getElementById('btnModoDpad').className = isDpad ? 'btn-mode active' : 'btn-mode';
  document.getElementById('btnModoJoy').className = isDpad ? 'btn-mode' : 'btn-mode active';
  const hDpad = document.getElementById('btnHdrDpad');
  const hJoy = document.getElementById('btnHdrJoy');
  if (hDpad) hDpad.className = isDpad ? 'btn-mode active' : 'btn-mode';
  if (hJoy) hJoy.className = isDpad ? 'btn-mode' : 'btn-mode active';
  const vDpad = document.getElementById('viewDpad');
  const vJoy = document.getElementById('viewJoy');
  if (isDpad) {
    vDpad.classList.remove('hidden');
    vJoy.classList.add('hidden');
  } else {
    vDpad.classList.add('hidden');
    vJoy.classList.remove('hidden');
  }
}

function toggleDiag() {
  const d = document.getElementById('cardDiag');
  if (d) d.open = !d.open;
}

const presetsCam = ['frio', 'equilibrado', 'qualidade'];
async function ciclarPresetCam() {
  const sel = document.getElementById('selPresetCam');
  let idx = presetsCam.indexOf(sel.value);
  idx = (idx + 1) % presetsCam.length;
  const novo = presetsCam[idx];
  sel.value = novo;
  await mudarPresetCam(novo);
}
function atualizarBtnPresetQuick(n) {
  const b = document.getElementById('btnCamPresetQuick');
  if (b) {
    if (n === 'frio') b.textContent = '❄️ Frio';
    else if (n === 'equilibrado') b.textContent = '⚖️ VGA';
    else if (n === 'qualidade') b.textContent = '✨ SVGA';
    else b.textContent = 'HD';
  }
}

function toggleModal(show) {
  document.getElementById('modalCfg').className = show ? 'modal-overlay active' : 'modal-overlay';
}

function aplicarVel(v) {
  velServo = parseInt(v);
  document.getElementById('rngVel').value = velServo;
  document.getElementById('outVel').value = velServo + '°/s';
  tx(`<C,1,${velServo}>`);
}

async function mudarPresetCam(n) {
  atualizarBtnPresetQuick(n);
  await fetch(`/api/cam/preset?n=${n}`);
  recarregarVideo();
}

function conectarWS() {
  ws = new WebSocket('ws://' + location.hostname + ':81/');
  const pill = document.getElementById('stWs');
  ws.onopen = () => { parada(); pill.textContent = 'ONLINE'; pill.className = 'status-pill ok'; };
  ws.onclose = () => { parada(); pill.textContent = 'OFF'; pill.className = 'status-pill bad'; setTimeout(conectarWS, 1500); };
}
function tx(cmd) {
  if (ws && ws.readyState === 1) { ws.send(cmd); return; }
  // Movimento so por WebSocket: evita requisicoes HTTP atrasadas apos uma parada.
  if (cmd.startsWith('<S,') || (cmd.startsWith('<M,') && cmd !== '<M,0,0>')) return;
  fetch('/api/cmd?f=' + encodeURIComponent(cmd)).catch(() => {});
}
function setLed(v) { tx(`<L,${v}>`); }
function pingNano() { tx('<P,1>'); const el = document.getElementById('rttPing'); if (el) el.textContent = '...'; }
function cancelarTesteMotor() {
  if (testeMotorTimer) clearInterval(testeMotorTimer);
  if (testeMotorFim) clearTimeout(testeMotorFim);
  testeMotorTimer = testeMotorFim = null;
}
function testeMotor(e, d, ms) {
  parada();
  if (!ws || ws.readyState !== 1) return;
  const max = parseInt(document.getElementById('rngPwm').value);
  const cmd = `<M,${Math.max(-max,Math.min(max,e))},${Math.max(-max,Math.min(max,d))}>`;
  tx(cmd);
  testeMotorTimer = setInterval(() => tx(cmd), 100);
  testeMotorFim = setTimeout(() => { cancelarTesteMotor(); tx('<M,0,0>'); }, ms);
}
async function alternarTxInv() {
  try {
    const r = await fetch('/api/link/invert');
    const d = await r.json();
    atualizarBtnTxInv(d.tx_inv);
    setLed(1);
  } catch(e) {}
}
function atualizarBtnTxInv(inv) {
  const btn = document.getElementById('btnTxInv');
  if (btn) {
    btn.textContent = inv ? 'Modo BC337 (Invertido)' : 'Fio Direto D0 (Normal)';
    btn.style.color = inv ? 'var(--accent)' : 'var(--green)';
  }
}

function recarregarVideo() {
  const img = document.getElementById('vid');
  img.src = 'http://' + location.hostname + ':82/stream?t=' + Date.now();
  img.style.transform = `rotate(${rotAtual}deg)`;
}

async function girarRotacao() {
  rotAtual = (rotAtual + 90) % 360;
  document.getElementById('vid').style.transform = `rotate(${rotAtual}deg)`;
  await fetch(`/api/cam/set?rot=${rotAtual}`);
}

// ---------------- Tração 4WD ----------------
let driveHeartbeat = null;
let driveCmd = null;
function drive(fwd, turn) {
  cancelarTesteMotor();
  const maxVal = parseInt(document.getElementById('rngPwm').value);
  if (fwd === 0 && turn === 0) {
    if (driveHeartbeat) clearInterval(driveHeartbeat);
    driveHeartbeat = null; driveCmd = null;
    tx('<M,0,0>'); return;
  }
  if (!ws || ws.readyState !== 1) { parada(); return; }
  let left = fwd * maxVal + turn * (maxVal * 0.7);
  let right = fwd * maxVal - turn * (maxVal * 0.7);
  left = Math.round(Math.max(-maxVal, Math.min(maxVal, left)));
  right = Math.round(Math.max(-maxVal, Math.min(maxVal, right)));
  const cmd = `<M,${left},${right}>`;
  if (cmd !== driveCmd) tx(cmd);
  driveCmd = cmd;
  if (!driveHeartbeat) driveHeartbeat = setInterval(() => {
    if (!ws || ws.readyState !== 1) { parada(); return; }
    tx(driveCmd);
  }, 100);
}

function parada() {
  cancelarTesteMotor();
  window.dispatchEvent(new Event('roverstop'));
  stopPT();
  if (joyDriveTimer) { clearInterval(joyDriveTimer); joyDriveTimer = null; }
  if (joyPTTimer) { clearInterval(joyPTTimer); joyPTTimer = null; }
  curDriveX = curDriveY = curPTX = curPTY = 0;
  drive(0, 0);
  tx('<X>');
}

// ---------------- Pan / Tilt ----------------
function enviarPT() {
  document.getElementById('rngPan').value = Math.round(pan);
  document.getElementById('outPan').value = Math.round(pan) + '°';
  document.getElementById('rngTilt').value = Math.round(tilt);
  document.getElementById('outTilt').value = Math.round(tilt) + '°';
  document.getElementById('lblJoyPan').textContent = Math.round(pan) + '°';
  document.getElementById('lblJoyTilt').textContent = Math.round(tilt) + '°';
  tx(`<S,${Math.round(pan * 10)},${Math.round(tilt * 10)},${velServo * 10}>`);
}

function stepPan(sinal) {
  stopPT();
  const d = (invPan ? -sinal : sinal) * passoGraus;
  pan = Math.max(limites.panMin, Math.min(limites.panMax, pan + d));
  enviarPT();
  // Repetição rápida a cada 60 ms para movimento ágil e contínuo
  ptTimer = setInterval(() => {
    pan = Math.max(limites.panMin, Math.min(limites.panMax, pan + d));
    enviarPT();
  }, 60);
}

function stepTilt(sinal) {
  stopPT();
  const d = (invTilt ? -sinal : sinal) * passoGraus;
  tilt = Math.max(limites.tiltMin, Math.min(limites.tiltMax, tilt + d));
  enviarPT();
  ptTimer = setInterval(() => {
    tilt = Math.max(limites.tiltMin, Math.min(limites.tiltMax, tilt + d));
    enviarPT();
  }, 60);
}

function stopPT() { if (ptTimer) { clearInterval(ptTimer); ptTimer = null; } }

function setPanDirect(v) {
  stopPT(); pan = parseInt(v);
  enviarPT();
}

function setTiltDirect(v) {
  stopPT(); tilt = parseInt(v);
  enviarPT();
}

function centroPT() { stopPT(); pan = 90; tilt = 90; enviarPT(); }

// ---------------- Lógica dos Joysticks Virtuais ----------------
let joyDriveTimer = null;
let curDriveX = 0, curDriveY = 0;
let joyPTTimer = null;
let curPTX = 0, curPTY = 0;

function setupJoystick(baseId, knobId, onMove, onEnd) {
  const base = document.getElementById(baseId);
  const knob = document.getElementById(knobId);
  const R = 38;
  let active = false;
  let pointer = null;

  base.addEventListener('pointerdown', e => {
    if (active) return;
    active = true;
    pointer = e.pointerId;
    base.setPointerCapture(e.pointerId);
    handle(e);
  });

  base.addEventListener('pointermove', e => {
    if (!active || e.pointerId !== pointer) return;
    handle(e);
  });

  function stop(e) {
    if (!active) return;
    if (e && e.pointerId !== undefined && e.pointerId !== pointer) return;
    active = false;
    pointer = null;
    knob.style.transform = 'translate(0px, 0px)';
    if (onEnd) onEnd();
  }

  base.addEventListener('pointerup', stop);
  base.addEventListener('pointercancel', stop);
  base.addEventListener('lostpointercapture', stop);
  window.addEventListener('roverstop', stop);

  function handle(e) {
    const rect = base.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    let dx = e.clientX - cx;
    let dy = e.clientY - cy;
    const dist = Math.hypot(dx, dy);
    if (dist > R) {
      dx = (dx / dist) * R;
      dy = (dy / dist) * R;
    }
    knob.style.transform = `translate(${dx}px, ${dy}px)`;
    // nx: -1 (esq) a +1 (dir), ny: +1 (frente) a -1 (re)
    const nx = dx / R;
    const ny = -dy / R;
    if (onMove) onMove(nx, ny);
  }
}

function initJoysticks() {
  // Joystick Tração
  setupJoystick('joyDriveBase', 'joyDriveKnob', (nx, ny) => {
    curDriveX = nx;
    curDriveY = ny;
    if (!joyDriveTimer) {
      joyDriveTimer = setInterval(joyDriveTick, 50);
      joyDriveTick();
    }
  }, () => {
    if (joyDriveTimer) { clearInterval(joyDriveTimer); joyDriveTimer = null; }
    curDriveX = 0; curDriveY = 0;
    drive(0, 0);
  });

  // Joystick Pan/Tilt
  setupJoystick('joyPTBase', 'joyPTKnob', (nx, ny) => {
    curPTX = nx;
    curPTY = ny;
    if (!joyPTTimer) {
      joyPTTimer = setInterval(joyPTTick, 60);
      joyPTTick();
    }
  }, () => {
    if (joyPTTimer) { clearInterval(joyPTTimer); joyPTTimer = null; }
    curPTX = 0; curPTY = 0;
  });
}

function joyDriveTick() {
  if (Math.abs(curDriveY) < 0.08 && Math.abs(curDriveX) < 0.08) {
    drive(0, 0);
    return;
  }
  drive(curDriveY, curDriveX);
}

function joyPTTick() {
  if (Math.abs(curPTX) < 0.08 && Math.abs(curPTY) < 0.08) return;
  const dt = 0.06;
  const dirPan = (invPan ? -1 : 1) * curPTX;
  const dirTilt = (invTilt ? -1 : 1) * curPTY;
  
  // Taxa contínua proporcional à deflexão do joystick
  pan = Math.max(limites.panMin, Math.min(limites.panMax, pan + dirPan * velServo * dt));
  tilt = Math.max(limites.tiltMin, Math.min(limites.tiltMax, tilt + dirTilt * velServo * dt));
  enviarPT();
}

// ---------------- Proteção Global de Toque ----------------
window.addEventListener('pointerup', () => { stopPT(); if (modoAtual === 'dpad') drive(0, 0); });
window.addEventListener('pointercancel', () => { stopPT(); if (modoAtual === 'dpad') drive(0, 0); });
window.addEventListener('blur', parada);
document.addEventListener('visibilitychange', () => { if (document.hidden) parada(); });

async function atualizarStats() {
  try {
    const r = await fetch('/api/stats');
    const d = await r.json();
    if (d.link) {
      const l = d.link;
      if (l.retorno === false) soIda = true;
      const ok = l.hb_age >= 0 && l.hb_age < 2500;
      const stNano = document.getElementById('stNano');
      if (stNano) {
        stNano.className = 'status-pill ' + (soIda ? '' : (ok ? 'ok' : 'bad'));
        stNano.textContent = soIda ? 'ENVIO → NANO' : (ok ? 'NANO ok' : 'NANO off');
      }
      if (l.vbat) {
        document.getElementById('stBat').textContent = (l.vbat / 1000).toFixed(2) + ' V';
      }
      const stLed = document.getElementById('stLed');
      if (stLed && soIda) {
        stLed.className = 'status-pill'; stLed.textContent = 'CONFIRA D13';
      } else if (stLed && l.led !== undefined) {
        stLed.className = 'status-pill ' + (l.led ? 'ok' : '');
        stLed.textContent = l.led ? 'LED ON' : 'LED OFF';
      }
      const rttPing = document.getElementById('rttPing');
      if (rttPing && l.rtt_ult > 0) {
        rttPing.textContent = '(' + (l.rtt_ult / 1000).toFixed(0) + 'ms)';
      }
      if (l.tx_inv !== undefined) atualizarBtnTxInv(l.tx_inv);
    }
    if (d.cam && d.cam.res) {
      const sel = document.getElementById('selPresetCam');
      if (document.activeElement !== sel) {
        let p = 'frio';
        if (d.cam.res === 'qvga') p = 'frio';
        else if (d.cam.res === 'vga') p = 'equilibrado';
        else if (d.cam.res === 'svga') p = 'qualidade';
        else if (d.cam.res === 'hd') p = 'maximo';
        sel.value = p;
        atualizarBtnPresetQuick(p);
      }
    }
  } catch (e) {}
}

window.onload = async () => {
  let joyInicial = false;
  try {
    const info = await (await fetch('/api/info')).json();
    if (info.controle) {
      const c = info.controle;
      soIda = c.retorno === false;
      limites = {panMin:c.pan_min, panMax:c.pan_max, tiltMin:c.tilt_min, tiltMax:c.tilt_max};
      for (const id of ['rngPwm', 'rngPwmJoy']) {
        document.getElementById(id).max = c.pwm_max;
        document.getElementById(id).value = c.pwm_max;
      }
      document.getElementById('outPwm').value = c.pwm_max;
      document.getElementById('outPwmJoy').value = c.pwm_max;
      document.getElementById('rngPan').min = c.pan_min;
      document.getElementById('rngPan').max = c.pan_max;
      document.getElementById('rngTilt').min = c.tilt_min;
      document.getElementById('rngTilt').max = c.tilt_max;
      velServo = c.vel_servo;
      document.getElementById('rngVel').value = velServo;
      document.getElementById('outVel').value = velServo + '°/s';
      if (soIda) {
        document.getElementById('btnPing').hidden = true;
        document.getElementById('stBat').hidden = true;
        document.getElementById('btnLed2').textContent = 'Piscar 5x';
        document.getElementById('btnTxInv').parentElement.style.display = 'none';
        document.getElementById('stNano').textContent = 'ENVIO → NANO';
        document.getElementById('stLed').textContent = 'CONFIRA D13';
      }
      joyInicial = true;
    }
  } catch (e) {}
  conectarWS();
  recarregarVideo();
  initJoysticks();
  if (joyInicial) setModo('joy');
  setInterval(atualizarStats, 2000);
};
</script>
</body>
</html>
)HTML";
