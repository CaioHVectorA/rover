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
#hudCv {
  position: absolute; inset: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 6; display: none;
}
.cam-btn-overlay { position: absolute; top: 6px; right: 6px; display: flex; gap: 5px; z-index: 10; flex-wrap: wrap; justify-content: flex-end; }
.cv-hud-bar {
  position: absolute; bottom: 6px; left: 6px; right: 6px;
  display: none; align-items: center; justify-content: space-between; gap: 6px;
  z-index: 10; pointer-events: none;
}
.cv-hud-bar.active { display: flex; }
.cv-badge {
  background: rgba(9, 12, 18, 0.82); border: 1px solid rgba(56, 189, 248, 0.45);
  color: #e6edf7; padding: 3px 7px; border-radius: 4px;
  font: 600 10px ui-monospace, SFMono-Regular, Consolas, monospace;
  letter-spacing: 0.3px; pointer-events: auto;
}
.btn-track-hud {
  background: rgba(15, 23, 42, 0.85); border: 1px solid var(--border);
  color: var(--sub); padding: 4px 8px; border-radius: 4px;
  font: 700 10px ui-monospace, SFMono-Regular, Consolas, monospace;
  cursor: pointer; pointer-events: auto;
}
.btn-track-hud.on {
  background: rgba(20, 83, 45, 0.9); border-color: var(--green); color: #86efac;
}
.btn-mini {
  background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer;
  backdrop-filter: blur(4px);
}
.btn-mini.active { background: rgba(56, 189, 248, 0.22); border-color: var(--accent); color: var(--accent); font-weight: 700; }
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
  <div class="video-card" id="vidCard">
    <div class="cam-btn-overlay">
      <button class="btn-mini" id="btnCvQuick" onclick="toggleCardCv()" title="Visão Computacional & Seguir Rosto">🎯 Visão IA</button>
      <button class="btn-mini" id="btnCamPresetQuick" onclick="ciclarPresetCam()" title="Qualidade da Câmera">❄️ Frio</button>
      <button class="btn-mini" onclick="girarRotacao()">↻ Girar</button>
      <button class="btn-mini" onclick="recarregarVideo()">▶ Vídeo</button>
    </div>
    <img id="vid" crossorigin="anonymous" src="" alt="Vídeo ao vivo">
    <canvas id="hudCv"></canvas>
    <div class="cv-hud-bar" id="cvHudBar">
      <span class="cv-badge" id="cvHudTxt">IA: OFF</span>
      <button class="btn-track-hud" id="btnTrackHud" onclick="toggleAutoTrack()">🎯 SEGUIR: OFF</button>
    </div>
  </div>

  <!-- Painel de Visão Computacional & Auto-Tracking (retrátil) -->
  <details class="ctrl-card diag-card" id="cardCv" style="width:100%;padding:6px 10px;">
    <summary style="display:flex;justify-content:space-between;align-items:center;width:100%;cursor:pointer;list-style:none;">
      <span class="ctrl-title">🎯 Visão Computacional & Seguir Rosto/Objeto ▾</span>
      <span id="stCvPill" class="status-pill">IA OFF</span>
    </summary>
    <div style="width:100%;margin-top:6px;display:flex;flex-direction:column;gap:6px;">
      <div style="display:flex;gap:5px;width:100%;">
        <button id="btnCvFace" class="btn-preset" style="flex:1" onclick="setCvModo('face')">😊 Rosto (IA)</button>
        <button id="btnCvObj" class="btn-preset" style="flex:1" onclick="setCvModo('obj')">📦 Objetos (IA)</button>
        <button id="btnCvCor" class="btn-preset" style="flex:1" onclick="setCvModo('cor')" title="Funciona offline sem internet (segue objeto vermelho/laranja)">🔴 Cor (Offline)</button>
        <button id="btnCvOff" class="btn-preset" style="flex:0.7" onclick="setCvModo('off')">🛑 Off</button>
      </div>
      <div id="rowObjFiltro" style="display:none;gap:6px;width:100%;align-items:center;">
        <span style="font-size:10px;color:var(--sub);white-space:nowrap">Alvo Objeto:</span>
        <select id="selObjFiltro" onchange="cvObjFiltro=this.value" style="flex:1;background:#1c2638;color:#fff;border:1px solid var(--border);padding:4px;border-radius:4px;font-size:11px">
          <option value="person">Pessoa (person)</option>
          <option value="all">Qualquer Objeto (80 classes)</option>
          <option value="cell phone">Celular (cell phone)</option>
          <option value="bottle,cup">Garrafa / Copo</option>
          <option value="cat,dog,bird">Pet (Gato / Cachorro)</option>
        </select>
      </div>
      <div style="display:flex;gap:6px;width:100%;align-items:center;">
        <button id="btnAutoTrack" class="btn-preset" style="flex:1.4;padding:7px 6px;font-weight:700;font-size:11px;border-color:#334155" onclick="toggleAutoTrack()">🎯 SEGUIR COM PAN/TILT: OFF</button>
        <label style="font-size:10px;color:var(--sub);display:flex;align-items:center;gap:3px;cursor:pointer"><input type="checkbox" id="chkCvInvPan" onchange="syncInvPan(this.checked)"> Inv.Pan</label>
        <label style="font-size:10px;color:var(--sub);display:flex;align-items:center;gap:3px;cursor:pointer"><input type="checkbox" id="chkCvInvTilt" onchange="syncInvTilt(this.checked)"> Inv.Tilt</label>
      </div>
      <div class="slider-item">
        <label style="width:65px">Ganho Track</label>
        <input type="range" id="rngCvGanho" min="2" max="12" step="1" value="5" oninput="cvGanho=parseInt(this.value); outCvGanho.value=this.value+'°'">
        <output id="outCvGanho">5°</output>
      </div>
    </div>
  </details>

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
      <label><input type="checkbox" id="chkInvPan" onchange="syncInvPan(this.checked)"> Inverter Pan (Horizontal)</label>
      <label><input type="checkbox" id="chkInvTilt" onchange="syncInvTilt(this.checked)"> Inverter Tilt (Vertical)</label>
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

function syncInvPan(v) {
  invPan = !!v;
  const c1 = document.getElementById('chkInvPan');
  const c2 = document.getElementById('chkCvInvPan');
  if (c1) c1.checked = invPan;
  if (c2) c2.checked = invPan;
}
function syncInvTilt(v) {
  invTilt = !!v;
  const c1 = document.getElementById('chkInvTilt');
  const c2 = document.getElementById('chkCvInvTilt');
  if (c1) c1.checked = invTilt;
  if (c2) c2.checked = invTilt;
}

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

function toggleCardCv() {
  const c = document.getElementById('cardCv');
  if (!c) return;
  c.open = !c.open;
  if (c.open && cvModo === 'off') setCvModo('face');
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
  img.crossOrigin = 'anonymous';
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
  if (typeof autoTrack !== 'undefined' && autoTrack) {
    autoTrack = false;
    atualizarUiAutoTrack();
  }
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

// ---------------- Visão Computacional & Auto-Tracking (No Navegador) ----------------
let cvModo = 'off';           // 'off' | 'face' | 'obj' | 'cor'
let cvObjFiltro = 'person';   // filtro de classe no modo 'obj'
let autoTrack = false;        // Seguir alvo com Pan/Tilt
let cvGanho = 5;              // Ganho proporcional (graus por ciclo para erro = 100%)
const cvDeadzone = 0.08;      // 8% de zona morta central para não oscilar
let faceModel = null;
let objModel = null;
let cvCarregando = false;
let cvTimer = null;
let ultTrackMs = 0;
let cvFps = 0, cvInfMs = 0;
let errSuaveX = 0, errSuaveY = 0;

const cvProc = document.createElement('canvas');
const pCtx = cvProc.getContext('2d', { willReadFrequently: true });

const TRAD_OBJ = {
  'person': 'PESSOA', 'cell phone': 'CELULAR', 'bottle': 'GARRAFA', 'cup': 'COPO',
  'cat': 'GATO', 'dog': 'CACHORRO', 'bird': 'AVE', 'chair': 'CADEIRA',
  'tv': 'TELA/TV', 'laptop': 'NOTEBOOK', 'mouse': 'MOUSE', 'keyboard': 'TECLADO',
  'book': 'LIVRO', 'backpack': 'MOCHILA', 'car': 'CARRO', 'remote': 'CONTROLE'
};

function carregarScriptCDN(url) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${url}"]`)) { resolve(); return; }
    const s = document.createElement('script');
    s.src = url;
    s.async = true;
    s.onload = resolve;
    s.onerror = () => reject(new Error('Sem internet p/ CDN'));
    document.head.appendChild(s);
  });
}

function atualizarUiCv() {
  const ativo = cvModo !== 'off';
  const hud = document.getElementById('hudCv');
  const bar = document.getElementById('cvHudBar');
  const btnQ = document.getElementById('btnCvQuick');
  const pill = document.getElementById('stCvPill');
  const rowF = document.getElementById('rowObjFiltro');

  if (hud) hud.style.display = ativo ? 'block' : 'none';
  if (bar) bar.className = ativo ? 'cv-hud-bar active' : 'cv-hud-bar';
  if (btnQ) btnQ.className = ativo ? 'btn-mini active' : 'btn-mini';
  if (rowF) rowF.style.display = (cvModo === 'obj') ? 'flex' : 'none';

  for (const [id, m] of [['btnCvFace','face'],['btnCvObj','obj'],['btnCvCor','cor'],['btnCvOff','off']]) {
    const el = document.getElementById(id);
    if (el) {
      el.style.borderColor = (cvModo === m && m !== 'off') ? 'var(--accent)' : 'var(--border)';
      el.style.color = (cvModo === m && m !== 'off') ? 'var(--accent)' : 'var(--text)';
    }
  }
  if (pill) {
    pill.className = 'status-pill ' + (ativo ? 'ok' : '');
    pill.textContent = ativo ? ('IA: ' + cvModo.toUpperCase()) : 'IA OFF';
  }
  atualizarUiAutoTrack();
}

function atualizarUiAutoTrack() {
  const b1 = document.getElementById('btnAutoTrack');
  const b2 = document.getElementById('btnTrackHud');
  if (b1) {
    b1.textContent = autoTrack ? '🎯 SEGUINDO ALVO (Pan/Tilt): ON' : '🎯 SEGUIR COM PAN/TILT: OFF';
    b1.style.background = autoTrack ? '#14532d' : '#1c2638';
    b1.style.borderColor = autoTrack ? 'var(--green)' : '#334155';
    b1.style.color = autoTrack ? '#86efac' : 'var(--text)';
  }
  if (b2) {
    b2.textContent = autoTrack ? '🎯 SEGUINDO: ON' : '🎯 SEGUIR: OFF';
    b2.className = autoTrack ? 'btn-track-hud on' : 'btn-track-hud';
  }
}

function toggleAutoTrack() {
  if (cvModo === 'off') {
    setCvModo('face').then(() => {
      autoTrack = true;
      atualizarUiAutoTrack();
    });
    return;
  }
  autoTrack = !autoTrack;
  errSuaveX = 0; errSuaveY = 0;
  atualizarUiAutoTrack();
}

async function setCvModo(m) {
  if (cvTimer) { clearTimeout(cvTimer); cvTimer = null; }
  cvModo = m;
  if (m === 'off') {
    autoTrack = false;
    const hud = document.getElementById('hudCv');
    if (hud) { const ctx = hud.getContext('2d'); ctx.clearRect(0, 0, hud.width, hud.height); }
    atualizarUiCv();
    return;
  }
  atualizarUiCv();
  const txt = document.getElementById('cvHudTxt');
  try {
    cvCarregando = true;
    if (m === 'face' && !faceModel) {
      if (txt) txt.textContent = '⏳ Baixando IA Rosto (BlazeFace)...';
      if (!window.tf) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js');
      if (!window.blazeface) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.1.0/dist/blazeface.min.js');
      faceModel = await window.blazeface.load({ maxFaces: 3, scoreThreshold: 0.65 });
    } else if (m === 'obj' && !objModel) {
      if (txt) txt.textContent = '⏳ Baixando IA Objetos (COCO-SSD)...';
      if (!window.tf) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js');
      if (!window.cocoSsd) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd@2.2.3/dist/coco-ssd.min.js');
      objModel = await window.cocoSsd.load({ base: 'lite_mobilenet_v2' });
    }
    cvCarregando = false;
    loopVisao();
  } catch (err) {
    cvCarregando = false;
    if (txt) txt.textContent = '⚠️ Sem Internet p/ IA -> Usando modo Cor Offline';
    cvModo = 'cor';
    atualizarUiCv();
    loopVisao();
  }
}

// Detector offline de objeto vermelho/laranja vivo (não exige internet)
function detectarCorOffline(pw, ph) {
  const data = pCtx.getImageData(0, 0, pw, ph).data;
  let sumX = 0, sumY = 0, count = 0;
  let minX = pw, minY = ph, maxX = 0, maxY = 0;
  const passo = 2;
  for (let y = 0; y < ph; y += passo) {
    for (let x = 0; x < pw; x += passo) {
      const i = (y * pw + x) * 4;
      const r = data[i], g = data[i + 1], b = data[i + 2];
      if (r > 145 && r > g * 1.45 && r > b * 1.45 && (r - Math.max(g, b)) > 45) {
        sumX += x; sumY += y; count++;
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (count < 12) return [];
  const bw = Math.max(16, maxX - minX);
  const bh = Math.max(16, maxY - minY);
  const cx = (sumX / count) / pw;
  const cy = (sumY / count) / ph;
  return [{
    label: 'ALVO COR',
    score: Math.min(0.99, 0.5 + count / 200),
    nx: minX / pw, ny: minY / ph, nw: bw / pw, nh: bh / ph,
    cx, cy, area: (bw * bh) / (pw * ph)
  }];
}

async function loopVisao() {
  if (cvModo === 'off' || cvCarregando) return;
  const img = document.getElementById('vid');
  if (!img || !img.complete || !img.naturalWidth || !img.naturalHeight) {
    cvTimer = setTimeout(loopVisao, 150);
    return;
  }

  const t0 = performance.now();
  const rawW = img.naturalWidth, rawH = img.naturalHeight;
  // Redimensiona para no máx 320px no maior lado e rotaciona conforme rotAtual (imagem em pé!)
  const esc = Math.min(1, 320 / Math.max(rawW, rawH));
  const sw = Math.max(1, Math.round(rawW * esc));
  const sh = Math.max(1, Math.round(rawH * esc));
  const trocado = (rotAtual % 180 !== 0);
  const pw = trocado ? sh : sw;
  const ph = trocado ? sw : sh;

  if (cvProc.width !== pw || cvProc.height !== ph) {
    cvProc.width = pw; cvProc.height = ph;
  }

  let dets = [];
  try {
    pCtx.save();
    pCtx.translate(pw / 2, ph / 2);
    pCtx.rotate((rotAtual * Math.PI) / 180);
    pCtx.drawImage(img, -sw / 2, -sh / 2, sw, sh);
    pCtx.restore();

    if (cvModo === 'face' && faceModel) {
      const preds = await faceModel.estimateFaces(cvProc, false);
      for (const p of preds) {
        const x1 = p.topLeft[0], y1 = p.topLeft[1];
        const bw = p.bottomRight[0] - x1, bh = p.bottomRight[1] - y1;
        const sc = Array.isArray(p.probability) ? p.probability[0] : (p.probability || 0.9);
        dets.push({
          label: 'ROSTO', score: sc,
          nx: x1 / pw, ny: y1 / ph, nw: bw / pw, nh: bh / ph,
          cx: (x1 + bw / 2) / pw, cy: (y1 + bh / 2) / ph,
          area: (bw * bh) / (pw * ph)
        });
      }
    } else if (cvModo === 'obj' && objModel) {
      const preds = await objModel.detect(cvProc, 6, 0.42);
      const filtros = cvObjFiltro === 'all' ? null : cvObjFiltro.split(',');
      for (const p of preds) {
        if (filtros && !filtros.includes(p.class)) continue;
        const [bx, by, bw, bh] = p.bbox;
        dets.push({
          label: TRAD_OBJ[p.class] || p.class.toUpperCase(),
          score: p.score,
          nx: bx / pw, ny: by / ph, nw: bw / pw, nh: bh / ph,
          cx: (bx + bw / 2) / pw, cy: (by + bh / 2) / ph,
          area: (bw * bh) / (pw * ph)
        });
      }
    } else if (cvModo === 'cor') {
      dets = detectarCorOffline(pw, ph);
    }
  } catch (e) {
    const txt = document.getElementById('cvHudTxt');
    if (txt) txt.textContent = '⚠️ Aguardando stream CORS (:82)...';
    cvTimer = setTimeout(loopVisao, 300);
    return;
  }

  // Ordena pelo maior alvo na tela (prioriza o rosto/objeto principal mais próximo)
  dets.sort((a, b) => (b.area * b.score) - (a.area * a.score));
  const alvo = dets.length > 0 ? dets[0] : null;

  const dtInf = performance.now() - t0;
  cvInfMs = cvInfMs ? (cvInfMs * 0.7 + dtInf * 0.3) : dtInf;
  const intervaloAlvo = (cvModo === 'obj') ? 95 : 70;
  const cicloTotal = Math.max(intervaloAlvo, dtInf);
  cvFps = 1000 / cicloTotal;

  desenharHudCv(dets, alvo, rawW, rawH, trocado);
  if (autoTrack && alvo) aplicarAutoTrack(alvo);

  const txt = document.getElementById('cvHudTxt');
  if (txt) {
    const nomeModo = cvModo === 'face' ? 'ROSTO' : (cvModo === 'obj' ? 'OBJ' : 'COR');
    const stAlvo = alvo ? `🎯 ${alvo.label} ${Math.round(alvo.score * 100)}%` : 'BUSCANDO...';
    txt.textContent = `${nomeModo} | ${stAlvo} | ${Math.round(cvInfMs)}ms (${cvFps.toFixed(0)} FPS)`;
  }

  const espera = Math.max(15, intervaloAlvo - Math.round(dtInf));
  cvTimer = setTimeout(loopVisao, espera);
}

function desenharHudCv(dets, alvo, rawW, rawH, trocado) {
  const hud = document.getElementById('hudCv');
  const card = document.getElementById('vidCard');
  const img = document.getElementById('vid');
  if (!hud || !card || !img) return;

  const cw = card.clientWidth, ch = card.clientHeight;
  if (hud.width !== cw || hud.height !== ch) { hud.width = cw; hud.height = ch; }
  const ctx = hud.getContext('2d');
  ctx.clearRect(0, 0, cw, ch);

  const fit = Math.min((img.clientWidth || cw) / rawW, (img.clientHeight || ch) / rawH);
  const visW = trocado ? (rawH * fit) : (rawW * fit);
  const visH = trocado ? (rawW * fit) : (rawH * fit);
  const offX = (cw - visW) / 2;
  const offY = (ch - visH) / 2;
  const midX = offX + visW / 2;
  const midY = offY + visH / 2;

  // Retículo central (zona morta de travamento)
  const dzW = visW * cvDeadzone;
  const dzH = visH * cvDeadzone;
  ctx.strokeStyle = autoTrack ? 'rgba(34, 197, 94, 0.45)' : 'rgba(129, 145, 171, 0.35)';
  ctx.lineWidth = 1;
  ctx.strokeRect(midX - dzW, midY - dzH, dzW * 2, dzH * 2);
  ctx.beginPath();
  ctx.moveTo(midX - 8, midY); ctx.lineTo(midX + 8, midY);
  ctx.moveTo(midX, midY - 8); ctx.lineTo(midX, midY + 8);
  ctx.stroke();

  dets.forEach((d, idx) => {
    const x = offX + d.nx * visW;
    const y = offY + d.ny * visH;
    const w = d.nw * visW;
    const h = d.nh * visH;
    const cx = x + w / 2;
    const cy = y + h / 2;
    const principal = (idx === 0);
    const cor = principal ? (autoTrack ? '#22c55e' : '#38bdf8') : '#f59e0b';

    // Caixa translúcida + cantoneiras estilo HUD Aviônica
    ctx.strokeStyle = cor;
    ctx.lineWidth = principal ? 1.5 : 1;
    ctx.strokeRect(x, y, w, h);

    if (principal) {
      const cLen = Math.max(8, Math.min(18, Math.min(w, h) * 0.25));
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x, y + cLen); ctx.lineTo(x, y); ctx.lineTo(x + cLen, y);
      ctx.moveTo(x + w - cLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + cLen);
      ctx.moveTo(x, y + h - cLen); ctx.lineTo(x, y + h); ctx.lineTo(x + cLen, y + h);
      ctx.moveTo(x + w - cLen, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - cLen);
      ctx.stroke();

      // Linha de vetor do centro até o alvo
      ctx.lineWidth = 1.2;
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.moveTo(midX, midY);
      ctx.lineTo(cx, cy);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = cor;
      ctx.beginPath();
      ctx.arc(cx, cy, 3.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // Etiqueta superior do alvo
    const txt = `${d.label} ${Math.round(d.score * 100)}%`;
    ctx.font = '700 10px ui-monospace, SFMono-Regular, Consolas, monospace';
    const tw = ctx.measureText(txt).width + 8;
    const ty = Math.max(offY + 14, y);
    ctx.fillStyle = 'rgba(9, 12, 18, 0.85)';
    ctx.fillRect(x, ty - 14, tw, 14);
    ctx.fillStyle = cor;
    ctx.fillText(txt, x + 4, ty - 3);
  });
}

function aplicarAutoTrack(alvo) {
  const agora = performance.now();
  if (agora - ultTrackMs < 85) return; // Máx ~11 comandos/s para proteger o link 9600 bps
  if (ptTimer || joyPTTimer) return;   // Prioridade ao toque manual do usuário

  // Erro normalizado de -1.0 a +1.0 em relação ao centro do quadro
  const ex = (alvo.cx - 0.5) * 2;
  const ey = (alvo.cy - 0.5) * 2;

  // Filtro exponencial leve para suavizar ruído da caixa (bounding box jitter)
  errSuaveX = errSuaveX * 0.35 + ex * 0.65;
  errSuaveY = errSuaveY * 0.35 + ey * 0.65;

  const foraX = Math.abs(errSuaveX) > cvDeadzone;
  const foraY = Math.abs(errSuaveY) > cvDeadzone;
  if (!foraX && !foraY) return;

  // ex > 0 (alvo à direita) -> gira p/ direita (mesmo sinal do botão ►: stepPan(-1))
  // ey < 0 (alvo acima)     -> inclina p/ cima (mesmo sinal do botão ▲: stepTilt(1))
  const sPan = invPan ? 1 : -1;
  const sTilt = invTilt ? -1 : 1;

  let dPan = foraX ? (sPan * errSuaveX * cvGanho) : 0;
  let dTilt = foraY ? (sTilt * (-errSuaveY) * cvGanho) : 0;

  // Limita o degrau máximo por ciclo a 8 graus para movimento orgânico sem overshoot
  dPan = Math.max(-8, Math.min(8, dPan));
  dTilt = Math.max(-8, Math.min(8, dTilt));

  if (Math.abs(dPan) < 0.45 && Math.abs(dTilt) < 0.45) return;

  pan = Math.max(limites.panMin, Math.min(limites.panMax, pan + dPan));
  tilt = Math.max(limites.tiltMin, Math.min(limites.tiltMax, tilt + dTilt));
  ultTrackMs = agora;
  enviarPT();
}

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
