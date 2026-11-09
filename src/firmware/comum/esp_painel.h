#pragma once
// ====================================================================================
// PAINEL WEB COMPACTO E DIRETO
// - Modos: D-Pad Tátil & Joystick Virtual Proporcional (sem bugs)
// - Configurações: Inversão de Eixos, Velocidade Fluida, Passo e Qualidade de Vídeo
// - Visão Computacional: Rosto (BlazeFace), Gestos (HandPose 21pts), Objetos (COCO-SSD) e Cor (HSV + Toque)
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
  <div class="video-card" id="vidCard" onclick="amostrarCorNoVideo(event)">
    <div class="cam-btn-overlay" onclick="event.stopPropagation()">
      <button class="btn-mini" id="btnCvQuick" onclick="toggleCardCv()" title="Visão Computacional & Seguir Rosto">🎯 Visão IA</button>
      <button class="btn-mini" id="btnCamPresetQuick" onclick="ciclarPresetCam()" title="Qualidade da Câmera">❄️ Frio</button>
      <button class="btn-mini" onclick="girarRotacao()">↻ Girar</button>
      <button class="btn-mini" onclick="recarregarVideo()">▶ Vídeo</button>
    </div>
    <img id="vid" crossorigin="anonymous" src="" alt="Vídeo ao vivo">
    <canvas id="hudCv"></canvas>
    <div class="cv-hud-bar" id="cvHudBar" onclick="event.stopPropagation()">
      <span class="cv-badge" id="cvHudTxt">IA: OFF</span>
      <button class="btn-track-hud" id="btnTrackHud" onclick="toggleAutoTrack()">🎯 SEGUIR: OFF</button>
    </div>
  </div>

  <!-- Painel de Visão Computacional & Auto-Tracking (retrátil) -->
  <details class="ctrl-card diag-card" id="cardCv" style="width:100%;padding:6px 10px;">
    <summary style="display:flex;justify-content:space-between;align-items:center;width:100%;cursor:pointer;list-style:none;">
      <span class="ctrl-title">🎯 Visão Computacional & Seguir Rosto/Mão/Objeto ▾</span>
      <span id="stCvPill" class="status-pill">IA OFF</span>
    </summary>
    <div style="width:100%;margin-top:6px;display:flex;flex-direction:column;gap:6px;">
      <div style="display:flex;gap:4px;width:100%;">
        <button id="btnCvFace" class="btn-preset" style="flex:1" onclick="setCvModo('face')">😊 Rosto</button>
        <button id="btnCvGesto" class="btn-preset" style="flex:1" onclick="setCvModo('gesto')">✋ Gestos</button>
        <button id="btnCvObj" class="btn-preset" style="flex:1" onclick="setCvModo('obj')">📦 Objetos</button>
        <button id="btnCvCor" class="btn-preset" style="flex:1" onclick="setCvModo('cor')" title="Funciona offline sem internet (ou toque no vídeo para escolher a cor)">🎨 Cor</button>
        <button id="btnCvOff" class="btn-preset" style="flex:0.65" onclick="setCvModo('off')">🛑 Off</button>
      </div>
      <div style="display:flex;gap:6px;width:100%;align-items:center;">
        <span style="font-size:10px;color:var(--sub);white-space:nowrap">Potência IA:</span>
        <select id="selCvPotencia" onchange="mudarPotenciaCv(this.value)" style="flex:1;background:#1c2638;color:#fff;border:1px solid var(--border);padding:4px;border-radius:4px;font-size:11px">
          <option value="auto" selected>🤖 Auto (Modelos Full + Adapta p/ Notebook Fraco)</option>
          <option value="ultra">🔥 Ultra (Full Range + MobileNetV2 + Zoom 2x)</option>
          <option value="leve">⚡ Leve (Rápido p/ Notebook Fraco / Navegador Simples)</option>
        </select>
      </div>
      <div id="rowGestoCfg" style="display:none;flex-direction:column;gap:4px;width:100%;background:#101622;border:1px solid var(--border);border-radius:6px;padding:6px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <label style="font-size:11px;color:var(--accent);font-weight:700;display:flex;align-items:center;gap:5px;cursor:pointer">
            <input type="checkbox" id="chkGestoCmd" checked onchange="cvGestoCmd=this.checked"> ⚡ Comandar Robô por Gestos
          </label>
          <span id="lblGestoAtivo" style="font-size:10px;color:var(--green);font-weight:700">Mostre a mão...</span>
        </div>
        <div style="font-size:9.5px;color:var(--sub);line-height:1.35">
          <b>☝️ 1 Dedo:</b> Mira na ponta do dedo &nbsp;|&nbsp; <b>✋ Aberta / ✊ Punho:</b> Parar<br>
          <b>👍 Joia:</b> Frente + LED ON &nbsp;|&nbsp; <b>👎 Baixo:</b> Ré + LED OFF &nbsp;|&nbsp; <b>✌️ Paz:</b> Centro + Piscar
        </div>
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
      <div id="rowCorFiltro" style="display:none;gap:6px;width:100%;align-items:center;">
        <span style="font-size:10px;color:var(--sub);white-space:nowrap">Cor Alvo:</span>
        <select id="selCorFiltro" onchange="cvCorAlvo=this.value;atualizarSwatchCor()" style="flex:1;background:#1c2638;color:#fff;border:1px solid var(--border);padding:4px;border-radius:4px;font-size:11px">
          <option value="vermelho">🔴 Vermelho / Laranja</option>
          <option value="verde">🟢 Verde</option>
          <option value="azul">🔵 Azul</option>
          <option value="amarelo">🟡 Amarelo</option>
          <option value="custom">👆 Cor Tocada no Vídeo</option>
        </select>
        <span id="corSwatch" title="Dica: toque em qualquer objeto no vídeo para capturar a cor dele!" style="width:18px;height:18px;border-radius:4px;border:1px solid #fff;background:#ef4444;display:inline-block;flex-shrink:0"></span>
      </div>
      <div style="display:flex;gap:6px;width:100%;align-items:center;">
        <button id="btnAutoTrack" class="btn-preset" style="flex:1.4;padding:7px 6px;font-weight:700;font-size:11px;border-color:#334155" onclick="toggleAutoTrack()">🎯 SEGUIR COM PAN/TILT: OFF</button>
        <label style="font-size:10px;color:var(--sub);display:flex;align-items:center;gap:3px;cursor:pointer"><input type="checkbox" id="chkCvInvPan" onchange="syncInvPan(this.checked)"> Inv.Pan</label>
        <label style="font-size:10px;color:var(--sub);display:flex;align-items:center;gap:3px;cursor:pointer"><input type="checkbox" id="chkCvInvTilt" onchange="syncInvTilt(this.checked)"> Inv.Tilt</label>
      </div>
      <div class="slider-item">
        <label style="width:65px">Ganho Track</label>
        <input type="range" id="rngCvGanho" min="2" max="45" step="1" value="20" oninput="cvGanho=parseInt(this.value); outCvGanho.value=this.value+'°'">
        <output id="outCvGanho">20°</output>
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
let ultCmdPT = '';
function enviarPT(velCustom) {
  const p10 = Math.round(pan * 10);
  const t10 = Math.round(tilt * 10);
  const pDeg = Math.round(pan);
  const tDeg = Math.round(tilt);
  document.getElementById('rngPan').value = pDeg;
  document.getElementById('outPan').value = pDeg + '°';
  document.getElementById('rngTilt').value = tDeg;
  document.getElementById('outTilt').value = tDeg + '°';
  document.getElementById('lblJoyPan').textContent = pDeg + '°';
  document.getElementById('lblJoyTilt').textContent = tDeg + '°';
  const v = velCustom ? velCustom : velServo;
  const cmd = `<S,${p10},${t10},${v * 10}>`;
  ultCmdPT = cmd;
  tx(cmd);
}

function stepPan(sinal) {
  stopPT();
  const d = (invPan ? -sinal : sinal) * passoGraus;
  pan = Math.max(limites.panMin, Math.min(limites.panMax, pan + d));
  enviarPT();
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
let cvModo = 'off';           // 'off' | 'face' | 'gesto' | 'obj' | 'cor'
let cvPotencia = 'auto';      // 'auto' | 'ultra' | 'leve'
let cvAutoRebaixado = false;  // true se o modo 'auto' detectou notebook fraco e ativou perfil Leve
let cvLentoCont = 0;          // Contador de quadros lentos consecutivos
let cvQuadroIdx = 0;          // Contador de quadros para busca Multi-Escala Zoom 2x
let cvObjFiltro = 'person';   // filtro de classe no modo 'obj'
let cvCorAlvo = 'vermelho';   // 'vermelho' | 'verde' | 'azul' | 'amarelo' | 'custom'
let cvCorCustom = { r: 220, g: 40, b: 40, h: 0, s: 0.8, v: 0.85 };
let cvGestoCmd = true;        // Executar comandos no robô ao manter um gesto firme
let gestoAnt = '';
let gestoCont = 0;
let ultGestoCmdMs = 0;
let autoTrack = false;        // Seguir alvo com Pan/Tilt
let cvGanho = 20;             // Ganho máximo (graus por ciclo na borda; reduz progressivamente perto do centro)
const cvDeadzone = 0.075;     // 7.5% de zona morta central de parada (com histerese até 12.5%)
let trackTravadoX = false, trackTravadoY = false;
let ultSinalX = 0, ultSinalY = 0;
let faceModel = null, faceModelUltra = null, faceModelLeve = null;
let handModel = null, handModelUltra = null, handModelLeve = null;
let objModel = null, objModelUltra = null, objModelLeve = null;
let cvCarregando = false;
let cvRodando = false;        // Trava estrita contra loops paralelos
let cvEpoch = 0;              // Token de geração para cancelar awaits antigos
let cvTimer = null;
let ultTrackMs = 0;
let cvFps = 0, cvInfMs = 0;
let errSuaveX = 0, errSuaveY = 0;

// Canvas GPU principal (sem willReadFrequently) para WebGL rápido
const cvProc = document.createElement ? document.createElement('canvas') : { width: 0, height: 0, getContext: () => null };
const pCtx = cvProc.getContext ? cvProc.getContext('2d') : null;

// Canvas GPU secundário para recorte Multi-Escala (Zoom Central 2x para alvos distantes/pequenos)
const cvZoom = document.createElement ? document.createElement('canvas') : { width: 0, height: 0, getContext: () => null };
const zCtx = cvZoom.getContext ? cvZoom.getContext('2d') : null;

// Canvas CPU compacto (máx 160px) exclusivo para leitura de pixels no modo Cor
const cvCorCanvas = document.createElement ? document.createElement('canvas') : { width: 0, height: 0, getContext: () => null };
const cCtx = cvCorCanvas.getContext ? cvCorCanvas.getContext('2d', { willReadFrequently: true }) : null;

const TRAD_OBJ = {
  'person': 'PESSOA', 'cell phone': 'CELULAR', 'bottle': 'GARRAFA', 'cup': 'COPO',
  'cat': 'GATO', 'dog': 'CACHORRO', 'bird': 'AVE', 'chair': 'CADEIRA',
  'tv': 'TELA/TV', 'laptop': 'NOTEBOOK', 'mouse': 'MOUSE', 'keyboard': 'TECLADO',
  'book': 'LIVRO', 'backpack': 'MOCHILA', 'car': 'CARRO', 'remote': 'CONTROLE',
  'potted plant': 'PLANTA', 'dining table': 'MESA', 'couch': 'SOFÁ', 'bed': 'CAMA',
  'clock': 'RELÓGIO', 'scissors': 'TESOURA', 'teddy bear': 'PELÚCIA', 'sports ball': 'BOLA'
};

function usarPerfilLeve() {
  return cvPotencia === 'leve' || (cvPotencia === 'auto' && cvAutoRebaixado);
}

function otimizarBackendTf(modoLeve) {
  if (!window.tf || !window.tf.env) return;
  try {
    // Libera texturas temporárias imediatamente para não estourar VRAM em notebooks integrados
    window.tf.env().set('WEBGL_DELETE_TEXTURE_THRESHOLD', 0);
    window.tf.env().set('WEBGL_PACK', true);
    if (modoLeve) {
      window.tf.env().set('WEBGL_FORCE_F16_TEXTURES', true);
      window.tf.env().set('WEBGL_FLUSH_THRESHOLD', 1);
    }
  } catch (_) {}
}

async function mudarPotenciaCv(val) {
  cvPotencia = val;
  cvAutoRebaixado = false;
  cvLentoCont = 0;
  cvInfMs = 0;
  if (cvModo !== 'off') {
    await setCvModo(cvModo);
  }
}

function carregarScriptCDN(url) {
  return new Promise((resolve, reject) => {
    const ex = document.querySelector ? document.querySelector(`script[src="${url}"]`) : null;
    if (ex && ex.dataset && ex.dataset.ok === '1') { resolve(); return; }
    if (ex && ex.remove) ex.remove();
    const s = document.createElement('script');
    s.src = url;
    s.async = true;
    s.onload = () => { if (s.dataset) s.dataset.ok = '1'; resolve(); };
    s.onerror = () => { if (s.remove) s.remove(); reject(new Error('Falha CDN')); };
    document.head.appendChild(s);
  });
}

function atualizarSwatchCor() {
  const sw = document.getElementById('corSwatch');
  if (!sw) return;
  const mapa = { vermelho: '#ef4444', verde: '#22c55e', azul: '#3b82f6', amarelo: '#eab308' };
  if (cvCorAlvo === 'custom') {
    sw.style.background = `rgb(${cvCorCustom.r},${cvCorCustom.g},${cvCorCustom.b})`;
  } else {
    sw.style.background = mapa[cvCorAlvo] || '#ef4444';
  }
}

function atualizarUiCv() {
  const ativo = cvModo !== 'off';
  const hud = document.getElementById('hudCv');
  const bar = document.getElementById('cvHudBar');
  const btnQ = document.getElementById('btnCvQuick');
  const pill = document.getElementById('stCvPill');
  const rowG = document.getElementById('rowGestoCfg');
  const rowF = document.getElementById('rowObjFiltro');
  const rowC = document.getElementById('rowCorFiltro');

  if (hud) hud.style.display = ativo ? 'block' : 'none';
  if (bar) bar.className = ativo ? 'cv-hud-bar active' : 'cv-hud-bar';
  if (btnQ) btnQ.className = ativo ? 'btn-mini active' : 'btn-mini';
  if (rowG) rowG.style.display = (cvModo === 'gesto') ? 'flex' : 'none';
  if (rowF) rowF.style.display = (cvModo === 'obj') ? 'flex' : 'none';
  if (rowC) rowC.style.display = (cvModo === 'cor') ? 'flex' : 'none';
  atualizarSwatchCor();

  for (const [id, m] of [['btnCvFace','face'],['btnCvGesto','gesto'],['btnCvObj','obj'],['btnCvCor','cor'],['btnCvOff','off']]) {
    const el = document.getElementById(id);
    if (el) {
      el.style.borderColor = (cvModo === m && m !== 'off') ? 'var(--accent)' : 'var(--border)';
      el.style.color = (cvModo === m && m !== 'off') ? 'var(--accent)' : 'var(--text)';
    }
  }
  if (pill) {
    const sufixo = usarPerfilLeve() ? ' LEVE' : ' ULTRA';
    pill.className = 'status-pill ' + (ativo ? 'ok' : '');
    pill.textContent = ativo ? ('IA: ' + cvModo.toUpperCase() + (cvModo === 'cor' ? '' : sufixo)) : 'IA OFF';
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

async function toggleAutoTrack() {
  errSuaveX = 0; errSuaveY = 0;
  trackTravadoX = false; trackTravadoY = false;
  ultSinalX = 0; ultSinalY = 0;
  if (cvModo === 'off') {
    autoTrack = true;
    atualizarUiAutoTrack();
    await setCvModo('face');
    return;
  }
  autoTrack = !autoTrack;
  atualizarUiAutoTrack();
}

async function garantirModeloFace(leve, txt) {
  if (!window.tf) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js');
  otimizarBackendTf(leve);
  // Sempre garante o BlazeFace carregado (usado tanto no modo Leve quanto como suporte rápido no Ultra)
  if (!faceModelLeve) {
    if (txt) txt.textContent = '⏳ Baixando IA Rosto (BlazeFace)...';
    if (!window.blazeface) {
      try {
        await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js');
      } catch (_) {
        await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.1.0/dist/blazeface.min.umd.js');
      }
    }
    faceModelLeve = await window.blazeface.load({ maxFaces: 4, scoreThreshold: 0.42 });
  }
  if (!leve && !faceModelUltra) {
    try {
      if (txt) txt.textContent = '⏳ Baixando IA Rosto Ultra (MediaPipe Full-Range 5m)...';
      if (!window.faceDetection) {
        await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/face-detection@1.0.3/dist/face-detection.min.js');
      }
      faceModelUltra = await window.faceDetection.createDetector(
        window.faceDetection.SupportedModels.MediaPipeFaceDetector,
        { runtime: 'tfjs', modelType: 'full', maxFaces: 5 }
      );
    } catch (_) {
      faceModelUltra = faceModelLeve;
    }
  }
  faceModel = (!leve && faceModelUltra) ? faceModelUltra : faceModelLeve;
}

async function garantirModeloMao(leve, txt) {
  if (!window.tf) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js');
  otimizarBackendTf(leve);
  if (!leve && !handModelUltra) {
    try {
      if (txt) txt.textContent = '⏳ Baixando IA Gestos Ultra (MediaPipe Hands Full 2 Mãos)...';
      if (!window.handPoseDetection) {
        await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/hand-pose-detection@2.0.1/dist/hand-pose-detection.min.js');
      }
      handModelUltra = await window.handPoseDetection.createDetector(
        window.handPoseDetection.SupportedModels.MediaPipeHands,
        { runtime: 'tfjs', modelType: 'full', maxHands: 2 }
      );
    } catch (_) {}
  }
  if ((leve || !handModelUltra) && !handModelLeve) {
    if (txt) txt.textContent = '⏳ Baixando IA Gestos Leve (HandPose 21pts)...';
    if (!window.handpose) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/handpose@0.0.7/dist/handpose.min.js');
    handModelLeve = await window.handpose.load({ detectionConfidence: 0.60 });
  }
  handModel = (!leve && handModelUltra) ? handModelUltra : (handModelLeve || handModelUltra);
}

async function garantirModeloObj(leve, txt) {
  if (!window.tf) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js');
  otimizarBackendTf(leve);
  if (!window.cocoSsd) await carregarScriptCDN('https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd@2.2.3/dist/coco-ssd.min.js');
  if (!leve && !objModelUltra) {
    try {
      if (txt) txt.textContent = '⏳ Baixando IA Objetos Ultra (COCO-SSD MobileNetV2 Full)...';
      objModelUltra = await window.cocoSsd.load({ base: 'mobilenet_v2' });
    } catch (_) {}
  }
  if ((leve || !objModelUltra) && !objModelLeve) {
    if (txt) txt.textContent = '⏳ Baixando IA Objetos Leve (COCO-SSD Lite)...';
    objModelLeve = await window.cocoSsd.load({ base: 'lite_mobilenet_v2' });
  }
  objModel = (!leve && objModelUltra) ? objModelUltra : (objModelLeve || objModelUltra);
}

async function setCvModo(m) {
  const myEpoch = ++cvEpoch;
  if (cvTimer) { clearTimeout(cvTimer); cvTimer = null; }
  cvModo = m;
  cvInfMs = 0;
  cvLentoCont = 0;
  cvQuadroIdx = 0;
  gestoAnt = ''; gestoCont = 0;
  if (m === 'off') {
    autoTrack = false;
    cvCarregando = false;
    const hud = document.getElementById('hudCv');
    if (hud && hud.getContext) { const ctx = hud.getContext('2d'); ctx.clearRect(0, 0, hud.width, hud.height); }
    atualizarUiCv();
    return;
  }
  atualizarUiCv();
  const txt = document.getElementById('cvHudTxt');
  const leve = usarPerfilLeve();
  try {
    cvCarregando = true;
    if (m === 'face') await garantirModeloFace(leve, txt);
    else if (m === 'gesto') await garantirModeloMao(leve, txt);
    else if (m === 'obj') await garantirModeloObj(leve, txt);
    if (myEpoch !== cvEpoch) return;
    cvCarregando = false;
    atualizarUiCv();
    loopVisao(myEpoch);
  } catch (err) {
    if (myEpoch !== cvEpoch) return;
    cvCarregando = false;
    if (txt) txt.textContent = '⚠️ Falha CDN IA -> Modo Cor Offline ativo';
    cvModo = 'cor';
    atualizarUiCv();
    loopVisao(myEpoch);
  }
}

// Classificador geométrico dos 21 pontos da mão (compatível com MediaPipe Hands Full e HandPose)
function classificarGestoMao(lm) {
  const d = (i, j) => Math.hypot(lm[i][0] - lm[j][0], lm[i][1] - lm[j][1]);
  const palma = Math.max(10, d(0, 9));

  // Dedos esticados se a ponta (TIP) estiver claramente mais longe do punho (0) que a articulação PIP/MCP
  const ind = d(0, 8) > d(0, 6) * 1.08 && d(0, 8) > d(0, 5) * 1.15;
  const med = d(0, 12) > d(0, 10) * 1.12 && d(0, 12) > d(0, 9) * 1.22;
  const ane = d(0, 16) > d(0, 14) * 1.10 && d(0, 16) > d(0, 13) * 1.20;
  const min = d(0, 20) > d(0, 18) * 1.10 && d(0, 20) > d(0, 17) * 1.18;
  const pol = d(4, 17) > d(2, 17) * 1.14 && d(4, 5) > palma * 0.46;
  const n4 = (ind ? 1 : 0) + (med ? 1 : 0) + (ane ? 1 : 0) + (min ? 1 : 0);

  // Detecta dedo indicador apontando mesmo que os outros dedos estejam apenas semi-dobrados
  const indDestacado = ind && (d(0, 8) > Math.max(d(0, 12), d(0, 16), d(0, 20)) * 1.14);

  if (n4 === 0 && !indDestacado) {
    if (d(4, 6) > palma * 0.48 && d(4, 2) > palma * 0.40) {
      if (lm[4][1] < lm[2][1] - palma * 0.16) return { id: 'joia', label: '👍 JOIA', mira: lm[4] };
      if (lm[4][1] > lm[2][1] + palma * 0.16) return { id: 'baixo', label: '👎 BAIXO', mira: lm[4] };
    }
    return { id: 'punho', label: '✊ PUNHO', mira: lm[9] };
  }
  if ((ind && !med && !ane && !min) || (indDestacado && n4 <= 2 && !min)) {
    return { id: 'apontar', label: '☝️ APONTAR', mira: lm[8] };
  }
  if (ind && med && !ane && !min)  return { id: 'paz', label: '✌️ PAZ (2)', mira: lm[8] };
  if (ind && !med && !ane && min)  return { id: 'rock', label: '🤟 ROCK', mira: lm[9] };
  if (n4 === 3)                    return { id: 'tres', label: '👌 TRÊS (3)', mira: lm[8] };
  if (n4 >= 4)                     return { id: 'aberta', label: '✋ ABERTA (5)', mira: lm[9] };
  return { id: 'mao', label: `✋ MÃO (${n4 + (pol ? 1 : 0)})`, mira: ind ? lm[8] : lm[9] };
}

function processarComandoGesto(gId) {
  const lbl = document.getElementById('lblGestoAtivo');
  if (gId === gestoAnt) gestoCont++;
  else { gestoAnt = gId; gestoCont = 1; }

  if (!cvGestoCmd) {
    if (lbl) lbl.textContent = 'Ações OFF';
    return;
  }
  if (gId === 'apontar') {
    if (lbl) lbl.textContent = '☝️ Seguindo ponta do dedo';
    return;
  }
  // Exige 3 quadros seguidos do mesmo gesto + cooldown de 1.2s para evitar disparos acidentais
  if (gestoCont < 3) return;
  const agora = performance.now();
  if (agora - ultGestoCmdMs < 1200) return;

  if (gId === 'aberta' || gId === 'punho') {
    cancelarTesteMotor();
    drive(0, 0);
    ultGestoCmdMs = agora;
    if (lbl) lbl.textContent = '🛑 Motores Parados';
  } else if (gId === 'paz') {
    centroPT();
    setLed(2);
    ultGestoCmdMs = agora;
    if (lbl) lbl.textContent = '✌️ Centro + Pisca LED';
  } else if (gId === 'joia') {
    setLed(1);
    testeMotor(120, 120, 400);
    ultGestoCmdMs = agora;
    if (lbl) lbl.textContent = '👍 LED ON + Frente 0.4s';
  } else if (gId === 'baixo') {
    setLed(0);
    testeMotor(-120, -120, 400);
    ultGestoCmdMs = agora;
    if (lbl) lbl.textContent = '👎 LED OFF + Ré 0.4s';
  } else if (gId === 'rock') {
    setLed(2);
    ultGestoCmdMs = agora;
    if (lbl) lbl.textContent = '🤟 Pisca LED D13';
  }
}

function rgbParaHsv(r, g, b) {
  const rf = r / 255, gf = g / 255, bf = b / 255;
  const max = Math.max(rf, gf, bf), min = Math.min(rf, gf, bf);
  const d = max - min;
  let h = 0;
  if (d > 0.0001) {
    if (max === rf) h = ((gf - bf) / d + (gf < bf ? 6 : 0)) * 60;
    else if (max === gf) h = ((bf - rf) / d + 2) * 60;
    else h = ((rf - gf) / d + 4) * 60;
  }
  const s = max === 0 ? 0 : d / max;
  return [h, s, max];
}

function diffAnguloHue(h1, h2) {
  const d = Math.abs(h1 - h2) % 360;
  return d > 180 ? 360 - d : d;
}

function pixelBateCor(r, g, b) {
  const [h, s, v] = rgbParaHsv(r, g, b);
  if (cvCorAlvo === 'vermelho') {
    return (s >= 0.35 && v >= 0.22 && (h <= 26 || h >= 338)) ||
           (r > 125 && r > g * 1.35 && r > b * 1.35 && (r - Math.max(g, b)) > 32);
  }
  if (cvCorAlvo === 'verde') {
    return (s >= 0.28 && v >= 0.20 && h >= 70 && h <= 168) ||
           (g > 105 && g > r * 1.25 && g > b * 1.20 && (g - Math.max(r, b)) > 25);
  }
  if (cvCorAlvo === 'azul') {
    return (s >= 0.30 && v >= 0.20 && h >= 185 && h <= 260) ||
           (b > 110 && b > r * 1.30 && b > g * 1.18 && (b - Math.max(r, g)) > 28);
  }
  if (cvCorAlvo === 'amarelo') {
    return (s >= 0.32 && v >= 0.32 && h >= 34 && h <= 69) ||
           (r > 135 && g > 120 && b < 95 && (Math.min(r, g) - b) > 45);
  }
  // Modo 'custom' (cor amostrada por toque no vídeo)
  const dh = diffAnguloHue(h, cvCorCustom.h);
  const ds = Math.abs(s - cvCorCustom.s);
  const dv = Math.abs(v - cvCorCustom.v);
  const drgb = Math.hypot(r - cvCorCustom.r, g - cvCorCustom.g, b - cvCorCustom.b);
  if (cvCorCustom.s < 0.2) return drgb < 48 && dv < 0.25;
  return (dh <= 24 && ds <= 0.35 && dv <= 0.40) || drgb <= 52;
}

// Permite tocar em qualquer objeto no vídeo quando no modo 'cor' para travar na cor dele
function amostrarCorNoVideo(ev) {
  if (cvModo !== 'cor' || !cCtx) return;
  const card = document.getElementById('vidCard');
  const img = document.getElementById('vid');
  if (!card || !img || !img.naturalWidth) return;

  const rect = card.getBoundingClientRect();
  const clickX = ev.clientX - rect.left;
  const clickY = ev.clientY - rect.top;

  const rawW = img.naturalWidth, rawH = img.naturalHeight;
  const trocado = (rotAtual % 180 !== 0);
  const cw = card.clientWidth, ch = card.clientHeight;
  const fit = Math.min((img.clientWidth || cw) / rawW, (img.clientHeight || ch) / rawH);
  const visW = trocado ? (rawH * fit) : (rawW * fit);
  const visH = trocado ? (rawW * fit) : (rawH * fit);
  const offX = (cw - visW) / 2;
  const offY = (ch - visH) / 2;

  const nx = (clickX - offX) / visW;
  const ny = (clickY - offY) / visH;
  if (nx < 0 || nx > 1 || ny < 0 || ny > 1) return;

  const cwProc = cvCorCanvas.width, chProc = cvCorCanvas.height;
  if (!cwProc || !chProc) return;
  const px = Math.max(2, Math.min(cwProc - 3, Math.round(nx * cwProc)));
  const py = Math.max(2, Math.min(chProc - 3, Math.round(ny * chProc)));
  try {
    const patch = cCtx.getImageData(px - 2, py - 2, 5, 5).data;
    let sr = 0, sg = 0, sb = 0, n = 0;
    for (let i = 0; i < patch.length; i += 4) {
      sr += patch[i]; sg += patch[i + 1]; sb += patch[i + 2]; n++;
    }
    const r = Math.round(sr / n), g = Math.round(sg / n), b = Math.round(sb / n);
    const [h, s, v] = rgbParaHsv(r, g, b);
    cvCorCustom = { r, g, b, h, s, v };
    cvCorAlvo = 'custom';
    const sel = document.getElementById('selCorFiltro');
    if (sel) sel.value = 'custom';
    atualizarSwatchCor();
  } catch (_) {}
}

// Detector offline de cor (2 passadas com filtro espacial contra ruído de fundo)
function detectarCorOffline(img, rawW, rawH, trocado) {
  if (!cCtx) return [];
  const esc = Math.min(1, 160 / Math.max(rawW, rawH));
  const sw = Math.max(1, Math.round(rawW * esc));
  const sh = Math.max(1, Math.round(rawH * esc));
  const pw = trocado ? sh : sw;
  const ph = trocado ? sw : sh;

  if (cvCorCanvas.width !== pw || cvCorCanvas.height !== ph) {
    cvCorCanvas.width = pw; cvCorCanvas.height = ph;
  }
  cCtx.save();
  cCtx.translate(pw / 2, ph / 2);
  cCtx.rotate((rotAtual * Math.PI) / 180);
  cCtx.drawImage(img, -sw / 2, -sh / 2, sw, sh);
  cCtx.restore();

  const data = cCtx.getImageData(0, 0, pw, ph).data;
  const pts = [];
  let sumX = 0, sumY = 0;
  const passo = 2;
  for (let y = 0; y < ph; y += passo) {
    for (let x = 0; x < pw; x += passo) {
      const i = (y * pw + x) * 4;
      if (pixelBateCor(data[i], data[i + 1], data[i + 2])) {
        pts.push([x, y]);
        sumX += x; sumY += y;
      }
    }
  }
  if (pts.length < 8) return [];

  // Passada 2: filtra apenas os pixels próximos ao centroide denso para ignorar ruído distante
  const mx = sumX / pts.length, my = sumY / pts.length;
  const raioMax = Math.max(pw, ph) * 0.36;
  let fSumX = 0, fSumY = 0, fCount = 0;
  let minX = pw, minY = ph, maxX = 0, maxY = 0;
  for (let k = 0; k < pts.length; k++) {
    const x = pts[k][0], y = pts[k][1];
    if (Math.hypot(x - mx, y - my) <= raioMax) {
      fSumX += x; fSumY += y; fCount++;
      if (x < minX) minX = x;
      if (x > maxX) maxX = x;
      if (y < minY) minY = y;
      if (y > maxY) maxY = y;
    }
  }
  if (fCount < 6) return [];

  const bw = Math.max(12, maxX - minX);
  const bh = Math.max(12, maxY - minY);
  const cx = (fSumX / fCount) / pw;
  const cy = (fSumY / fCount) / ph;
  const nomes = { vermelho: 'COR VERM', verde: 'COR VERDE', azul: 'COR AZUL', amarelo: 'COR AMAR', custom: 'COR ALVO' };
  return [{
    label: nomes[cvCorAlvo] || 'ALVO COR',
    score: Math.min(0.99, 0.55 + fCount / 140),
    nx: minX / pw, ny: minY / ph, nw: bw / pw, nh: bh / ph,
    cx, cy, area: (bw * bh) / (pw * ph)
  }];
}

// Prepara recorte central ampliado 2x (55% central do quadro) para detectar rostos/mãos/objetos distantes
function prepararZoomCentral(pw, ph) {
  if (!zCtx) return null;
  const zw = Math.max(128, Math.round(pw * 0.56));
  const zh = Math.max(128, Math.round(ph * 0.56));
  if (cvZoom.width !== zw || cvZoom.height !== zh) {
    cvZoom.width = zw; cvZoom.height = zh;
  }
  const sx = Math.round(pw * 0.22), sy = Math.round(ph * 0.22);
  const sw = Math.round(pw * 0.56), sh = Math.round(ph * 0.56);
  zCtx.drawImage(cvProc, sx, sy, sw, sh, 0, 0, zw, zh);
  return { zw, zh, offX: 0.22, offY: 0.22, scale: 0.56 };
}

// Converte predições de rosto (tanto MediaPipeFaceDetector Full quanto BlazeFace) para coordenadas normalizadas
function converterPredsRosto(preds, w, h, offX, offY, scale) {
  const res = [];
  if (!Array.isArray(preds)) return res;
  for (const p of preds) {
    let x1 = 0, y1 = 0, bw = 0, bh = 0, sc = 0.9, noseX = null, noseY = null;
    if (p.box) {
      // Formato @tensorflow-models/face-detection (MediaPipeFaceDetector Full-Range)
      x1 = p.box.xMin; y1 = p.box.yMin;
      bw = p.box.width; bh = p.box.height;
      sc = Array.isArray(p.score) ? p.score[0] : (p.score || 0.9);
      if (p.keypoints && p.keypoints.length > 0) {
        const nose = p.keypoints.find(k => k.name === 'noseTip') || p.keypoints[2];
        if (nose) { noseX = nose.x; noseY = nose.y; }
      }
    } else if (p.topLeft && p.bottomRight) {
      // Formato @tensorflow-models/blazeface
      x1 = p.topLeft[0]; y1 = p.topLeft[1];
      bw = p.bottomRight[0] - x1; bh = p.bottomRight[1] - y1;
      sc = Array.isArray(p.probability) ? p.probability[0] : (p.probability || 0.9);
      if (p.landmarks && p.landmarks.length >= 3) {
        noseX = p.landmarks[2][0]; noseY = p.landmarks[2][1];
      }
    } else continue;

    if (bw < 6 || bh < 6) continue;
    let cx = (x1 + bw / 2) / w;
    let cy = (y1 + bh / 2) / h;
    if (noseX !== null && noseY !== null) {
      cx = (cx * 0.35) + (noseX / w) * 0.65;
      cy = (cy * 0.35) + (noseY / h) * 0.65;
    }
    const nx = offX + (x1 / w) * scale;
    const ny = offY + (y1 / h) * scale;
    const nw = (bw / w) * scale;
    const nh = (bh / h) * scale;
    res.push({
      label: scale < 1 ? 'ROSTO (ZOOM)' : 'ROSTO',
      score: sc,
      nx, ny, nw, nh,
      cx: offX + cx * scale,
      cy: offY + cy * scale,
      area: nw * nh
    });
  }
  return res;
}

// Converte predições de mão (tanto MediaPipeHands Full 2 Mãos quanto HandPose)
function converterPredsMao(preds, w, h, offX, offY, scale) {
  const res = [];
  if (!Array.isArray(preds)) return res;
  for (const p of preds) {
    let lm = null, sc = 0.9;
    if (p.keypoints && p.keypoints.length >= 21) {
      // Formato @tensorflow-models/hand-pose-detection (MediaPipeHands Full)
      lm = p.keypoints.map(k => [k.x, k.y, k.z || 0]);
      sc = p.score || 0.92;
    } else if (p.landmarks && p.landmarks.length >= 21) {
      // Formato @tensorflow-models/handpose
      lm = p.landmarks;
      sc = p.handInViewConfidence || 0.9;
    } else continue;

    let minX = w, minY = h, maxX = 0, maxY = 0;
    for (let i = 0; i < 21; i++) {
      if (lm[i][0] < minX) minX = lm[i][0];
      if (lm[i][0] > maxX) maxX = lm[i][0];
      if (lm[i][1] < minY) minY = lm[i][1];
      if (lm[i][1] > maxY) maxY = lm[i][1];
    }
    const padX = Math.max(6, (maxX - minX) * 0.12);
    const padY = Math.max(6, (maxY - minY) * 0.12);
    const x1 = Math.max(0, minX - padX), y1 = Math.max(0, minY - padY);
    const bw = Math.max(12, Math.min(w - x1, (maxX - minX) + padX * 2));
    const bh = Math.max(12, Math.min(h - y1, (maxY - minY) + padY * 2));

    const g = classificarGestoMao(lm);
    processarComandoGesto(g.id);
    const ptsNorm = lm.map(pt => [offX + (pt[0] / w) * scale, offY + (pt[1] / h) * scale]);
    const nw = (bw / w) * scale;
    const nh = (bh / h) * scale;
    res.push({
      label: g.label,
      gestoId: g.id,
      score: sc,
      nx: offX + (x1 / w) * scale,
      ny: offY + (y1 / h) * scale,
      nw, nh,
      cx: offX + (g.mira[0] / w) * scale,
      cy: offY + (g.mira[1] / h) * scale,
      area: nw * nh,
      pts: ptsNorm
    });
  }
  return res;
}

function converterPredsObj(preds, filtros, w, h, offX, offY, scale) {
  const res = [];
  if (!Array.isArray(preds)) return res;
  for (const p of preds) {
    if (filtros && !filtros.includes(p.class)) continue;
    const [bx, by, bw, bh] = p.bbox;
    const isPerson = (p.class === 'person');
    const nw = (bw / w) * scale;
    const nh = (bh / h) * scale;
    res.push({
      label: TRAD_OBJ[p.class] || p.class.toUpperCase(),
      score: p.score,
      nx: offX + (bx / w) * scale,
      ny: offY + (by / h) * scale,
      nw, nh,
      cx: offX + ((bx + bw / 2) / w) * scale,
      cy: offY + ((by + bh * (isPerson ? 0.28 : 0.5)) / h) * scale,
      area: nw * nh
    });
  }
  return res;
}

async function loopVisao(epoch) {
  if (epoch !== cvEpoch || cvModo === 'off' || cvCarregando) return;
  if (cvRodando) {
    cvTimer = setTimeout(() => loopVisao(epoch), 60);
    return;
  }
  const img = document.getElementById('vid');
  if (!img || !img.complete || !img.naturalWidth || !img.naturalHeight) {
    cvTimer = setTimeout(() => loopVisao(epoch), 150);
    return;
  }

  cvRodando = true;
  cvQuadroIdx++;
  const t0 = performance.now();
  const rawW = img.naturalWidth, rawH = img.naturalHeight;
  const leve = usarPerfilLeve();

  // Resolução adaptativa: até 448px no Ultra/Auto rápido, 300px no intermediário e 224px no Notebook Fraco (Leve)
  let maxDim = 416;
  if (leve) maxDim = 224;
  else if (cvPotencia === 'ultra') maxDim = 480;
  else if (cvInfMs > 120) maxDim = 272;
  else if (cvInfMs > 75) maxDim = 336;

  const esc = Math.min(1, maxDim / Math.max(rawW, rawH));
  const sw = Math.max(1, Math.round(rawW * esc));
  const sh = Math.max(1, Math.round(rawH * esc));
  const trocado = (rotAtual % 180 !== 0);
  const pw = trocado ? sh : sw;
  const ph = trocado ? sw : sh;

  let dets = [];
  try {
    if (cvModo === 'cor') {
      dets = detectarCorOffline(img, rawW, rawH, trocado);
    } else if (pCtx) {
      if (cvProc.width !== pw || cvProc.height !== ph) {
        cvProc.width = pw; cvProc.height = ph;
      }
      pCtx.save();
      pCtx.imageSmoothingEnabled = true;
      pCtx.translate(pw / 2, ph / 2);
      pCtx.rotate((rotAtual * Math.PI) / 180);
      pCtx.drawImage(img, -sw / 2, -sh / 2, sw, sh);
      pCtx.restore();

      // Permite Zoom Central 2x em quadros alternados quando buscando alvo nos modos Ultra ou Auto rápido
      const podeZoom2x = !leve && (cvPotencia === 'ultra' || cvInfMs < 95) && (cvQuadroIdx % 2 === 0);

      if (cvModo === 'face') {
        const modAtivo = (!leve && faceModelUltra) ? faceModelUltra : faceModelLeve;
        if (modAtivo) {
          const preds = await modAtivo.estimateFaces(cvProc, false);
          dets = converterPredsRosto(preds, pw, ph, 0, 0, 1);
          // Se o detector Full não achou e temos o BlazeFace carregado, consulta o BlazeFace também
          if (dets.length === 0 && faceModelLeve && modAtivo !== faceModelLeve) {
            const p2 = await faceModelLeve.estimateFaces(cvProc, false);
            dets = converterPredsRosto(p2, pw, ph, 0, 0, 1);
          }
          // Busca Multi-Escala Zoom 2x para rostos pequenos/distantes
          if (dets.length === 0 && podeZoom2x) {
            const z = prepararZoomCentral(pw, ph);
            if (z) {
              const pz = await modAtivo.estimateFaces(cvZoom, false);
              dets = converterPredsRosto(pz, z.zw, z.zh, z.offX, z.offY, z.scale);
            }
          }
        }
      } else if (cvModo === 'gesto') {
        const modAtivo = (!leve && handModelUltra) ? handModelUltra : (handModelLeve || handModelUltra);
        if (modAtivo) {
          const preds = await modAtivo.estimateHands(cvProc);
          dets = converterPredsMao(preds, pw, ph, 0, 0, 1);
          if (dets.length === 0 && podeZoom2x) {
            const z = prepararZoomCentral(pw, ph);
            if (z) {
              const pz = await modAtivo.estimateHands(cvZoom);
              dets = converterPredsMao(pz, z.zw, z.zh, z.offX, z.offY, z.scale);
            }
          }
          if (dets.length === 0) {
            gestoAnt = ''; gestoCont = 0;
            const lbl = document.getElementById('lblGestoAtivo');
            if (lbl) lbl.textContent = 'Mostre a mão...';
          }
        }
      } else if (cvModo === 'obj') {
        const modAtivo = (!leve && objModelUltra) ? objModelUltra : (objModelLeve || objModelUltra);
        if (modAtivo) {
          const limScore = leve ? 0.38 : 0.30;
          const maxBoxes = leve ? 6 : 10;
          const filtros = cvObjFiltro === 'all' ? null : cvObjFiltro.split(',');
          const preds = await modAtivo.detect(cvProc, maxBoxes, limScore);
          dets = converterPredsObj(preds, filtros, pw, ph, 0, 0, 1);
          // Busca Multi-Escala Zoom 2x para objetos pequenos/distantes (ex: celular, copo, pessoa longe)
          if (dets.length === 0 && podeZoom2x) {
            const z = prepararZoomCentral(pw, ph);
            if (z) {
              const pz = await modAtivo.detect(cvZoom, 6, limScore);
              dets = converterPredsObj(pz, filtros, z.zw, z.zh, z.offX, z.offY, z.scale);
            }
          }
        }
      }
    }
  } catch (e) {
    cvRodando = false;
    if (epoch !== cvEpoch || cvModo === 'off') return;
    const txt = document.getElementById('cvHudTxt');
    if (txt) txt.textContent = '⚠️ Aguardando stream CORS (:82)...';
    cvTimer = setTimeout(() => loopVisao(epoch), 300);
    return;
  }

  cvRodando = false;
  if (epoch !== cvEpoch || cvModo === 'off') return;

  // Ordena pelo maior alvo na tela (prioriza o rosto/objeto principal mais próximo)
  dets.sort((a, b) => (b.area * b.score) - (a.area * a.score));
  const alvo = dets.length > 0 ? dets[0] : null;

  const dtInf = performance.now() - t0;
  // Ignora o pico único de compilação de shaders WebGL nos 2 primeiros quadros para não distorcer a média
  const dtUtil = (cvQuadroIdx <= 2 && dtInf > 160) ? 65 : dtInf;
  cvInfMs = cvInfMs ? (cvInfMs * 0.7 + dtUtil * 0.3) : dtUtil;

  // Auto-proteção para Notebook Fraco no modo 'auto':
  // Se após aquecer os shaders a máquina demorar > 210ms por 5 quadros seguidos, ativa automaticamente o perfil Leve
  if (cvPotencia === 'auto' && !cvAutoRebaixado && cvModo !== 'cor' && cvQuadroIdx > 2) {
    if (dtInf > 210) {
      cvLentoCont++;
      if (cvLentoCont >= 5) {
        cvAutoRebaixado = true;
        cvLentoCont = 0;
        atualizarUiCv();
        if (cvModo === 'face' && !faceModelLeve) garantirModeloFace(true, null).catch(() => {});
        else if (cvModo === 'gesto' && !handModelLeve) garantirModeloMao(true, null).catch(() => {});
        else if (cvModo === 'obj' && !objModelLeve) garantirModeloObj(true, null).catch(() => {});
      }
    } else {
      cvLentoCont = 0;
    }
  }

  // Pausa elástica: garante sempre tempo livre de CPU/GPU para o navegador do notebook nunca travar
  const pausaBase = (cvModo === 'obj' || cvModo === 'gesto') ? 50 : 38;
  const pausaMin = Math.max(pausaBase, Math.min(200, Math.round(dtInf * 0.55)));
  const intervaloAlvo = (cvModo === 'obj' || cvModo === 'gesto') ? 105 : 75;
  const espera = Math.max(pausaMin, intervaloAlvo - Math.round(dtInf));
  cvFps = 1000 / (dtInf + espera);

  desenharHudCv(dets, alvo, rawW, rawH, trocado);
  // Segue o alvo se o Auto-Track estiver ligado OU automaticamente ao apontar 1 dedo no modo Gestos
  const seguirDedoAuto = (cvModo === 'gesto' && cvGestoCmd && alvo && (alvo.gestoId === 'apontar' || alvo.gestoId === 'mao'));
  if ((autoTrack || seguirDedoAuto) && alvo) aplicarAutoTrack(alvo);

  const txt = document.getElementById('cvHudTxt');
  if (txt) {
    const mapaNome = { face: 'ROSTO', gesto: 'GESTO', obj: 'OBJ', cor: 'COR' };
    const tagPot = cvModo === 'cor' ? '' : (usarPerfilLeve() ? '⚡' : '🔥');
    const nomeModo = (mapaNome[cvModo] || 'IA') + tagPot;
    const stAlvo = alvo ? `🎯 ${alvo.label} ${Math.round(alvo.score * 100)}%` : 'BUSCANDO...';
    const stPt = autoTrack ? ` | P:${Math.round(pan)}° T:${Math.round(tilt)}°` : '';
    txt.textContent = `${nomeModo} | ${stAlvo}${stPt} | ${Math.round(cvInfMs)}ms (${cvFps.toFixed(0)} FPS)`;
  }

  cvTimer = setTimeout(() => loopVisao(epoch), espera);
}

const MAO_TRACOS = [
  [0,1,2,3,4], [0,5,6,7,8], [0,9,10,11,12],
  [0,13,14,15,16], [0,17,18,19,20], [5,9,13,17,0]
];

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
    const cx = offX + d.cx * visW;
    const cy = offY + d.cy * visH;
    const principal = (idx === 0);
    const cor = principal ? (autoTrack ? '#22c55e' : '#38bdf8') : '#f59e0b';

    // Desenha esqueleto de 21 pontos da mão (quando no modo Gestos)
    if (d.pts && d.pts.length === 21) {
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
      ctx.lineWidth = 1.6;
      for (const tr of MAO_TRACOS) {
        ctx.beginPath();
        for (let i = 0; i < tr.length; i++) {
          const px = offX + d.pts[tr[i]][0] * visW;
          const py = offY + d.pts[tr[i]][1] * visH;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();
      }
      for (let i = 0; i < 21; i++) {
        const px = offX + d.pts[i][0] * visW;
        const py = offY + d.pts[i][1] * visH;
        const ponta = (i === 4 || i === 8 || i === 12 || i === 16 || i === 20);
        ctx.fillStyle = ponta ? '#22c55e' : '#e6edf7';
        ctx.beginPath();
        ctx.arc(px, py, ponta ? 3.2 : 2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

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

      // Linha de vetor do centro até o ponto de mira do alvo
      ctx.lineWidth = 1.2;
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.moveTo(midX, midY);
      ctx.lineTo(cx, cy);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = cor;
      ctx.beginPath();
      ctx.arc(cx, cy, 4, 0, Math.PI * 2);
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
  // Intervalo de 125ms dá tempo para o servo mover fisicamente e o stream MJPEG entregar o novo quadro atualizado
  if (agora - ultTrackMs < 125) return;
  if (ptTimer || joyPTTimer) return;   // Prioridade ao toque manual do usuário

  // Erro normalizado de -1.0 a +1.0 em relação ao centro do quadro
  const ex = Math.max(-1, Math.min(1, (alvo.cx - 0.5) * 2));
  const ey = Math.max(-1, Math.min(1, (alvo.cy - 0.5) * 2));

  // Filtro exponencial anti-ruído: amortece variações bruscas de caixa/landmark de um quadro para outro
  errSuaveX = errSuaveX * 0.45 + ex * 0.55;
  errSuaveY = errSuaveY * 0.45 + ey * 0.55;

  const magX = Math.abs(errSuaveX);
  const magY = Math.abs(errSuaveY);

  // Histerese de zona morta central:
  // Quando chega perto do centro (< 7.5%), trava em repouso absoluto e só volta a corrigir se sair além de 12.5%
  if (magX < cvDeadzone) trackTravadoX = true;
  else if (magX > 0.125) trackTravadoX = false;

  if (magY < cvDeadzone) trackTravadoY = true;
  else if (magY > 0.125) trackTravadoY = false;

  const foraX = !trackTravadoX && magX > cvDeadzone;
  const foraY = !trackTravadoY && magY > cvDeadzone;
  if (!foraX && !foraY) return;

  // ex > 0 (alvo à direita) -> gira p/ direita (mesmo sinal do botão ►: stepPan(-1))
  // ey < 0 (alvo acima)     -> inclina p/ cima (mesmo sinal do botão ▲: stepTilt(1))
  const sPan = invPan ? 1 : -1;
  const sTilt = invTilt ? -1 : 1;

  // Lei de Controle com Ganho Variável Progressivo:
  // O ganho efetivo diminui quadraticamente conforme o erro se aproxima de zero (evita loop esquerda-direita!)
  let dPan = 0, dTilt = 0;
  if (foraX) {
    const uX = Math.min(1, (magX - cvDeadzone) / (1 - cvDeadzone));
    const ganhoEfetivoX = cvGanho * (0.15 * uX + 0.85 * uX * uX);
    const sinalX = Math.sign(errSuaveX);
    // Se acabou de cruzar o centro (inverteu esquerda <-> direita), freia 70% do passo para cortar oscilação
    const freioInvX = (ultSinalX !== 0 && sinalX !== ultSinalX) ? 0.30 : 1.0;
    ultSinalX = sinalX;
    dPan = sPan * sinalX * ganhoEfetivoX * freioInvX;
  }
  if (foraY) {
    const uY = Math.min(1, (magY - cvDeadzone) / (1 - cvDeadzone));
    const ganhoEfetivoY = cvGanho * (0.15 * uY + 0.85 * uY * uY);
    const sinalY = Math.sign(errSuaveY);
    const freioInvY = (ultSinalY !== 0 && sinalY !== ultSinalY) ? 0.30 : 1.0;
    ultSinalY = sinalY;
    dTilt = sTilt * (-sinalY) * ganhoEfetivoY * freioInvY;
  }

  // Limita o degrau máximo a 22 graus (rápido quando longe, milimétrico quando perto)
  dPan = Math.max(-22, Math.min(22, dPan));
  dTilt = Math.max(-22, Math.min(22, dTilt));

  if (Math.abs(dPan) < 0.25 && Math.abs(dTilt) < 0.25) return;

  pan = Math.max(limites.panMin, Math.min(limites.panMax, pan + dPan));
  tilt = Math.max(limites.tiltMin, Math.min(limites.tiltMax, tilt + dTilt));
  ultTrackMs = agora;
  // Comanda em alta velocidade (mínimo 480°/s) para o servo SG90 ir direto ao ponto sem tremer
  enviarPT(Math.max(velServo, 480));
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
