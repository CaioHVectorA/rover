import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { WebView } from 'react-native-webview';
import { Camera, RefreshCw, Cpu, Radio } from 'lucide-react-native';
import { OperationMode } from '../types';

interface CameraStreamProps {
  streamUrl: string;
  operationMode?: OperationMode;
  isVR?: boolean;
  panAngle?: number;
  tiltAngle?: number;
  motorLeftPwm?: number;
  motorRightPwm?: number;
  camSleeping?: boolean;
  camMode?: string;
  chipTemp?: number;
  vbat?: number;
  showHUD?: boolean;
}

const SIMULATOR_3D_HTML = `<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; background: #05070a; overflow: hidden; user-select: none; }
  html, body, canvas { width: 100%; height: 100%; display: block; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
let W = window.innerWidth || 360;
let H = window.innerHeight || 280;

function resize() {
  W = window.innerWidth || 360;
  H = window.innerHeight || 280;
  canvas.width = W * window.devicePixelRatio;
  canvas.height = H * window.devicePixelRatio;
  ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
}
window.addEventListener('resize', resize);
resize();

window.roverState = {
  pan: 90,
  tilt: 90,
  motL: 0,
  motR: 0,
  sleeping: false,
  camMode: 'ATIVO',
  temp: 44.5,
  vbat: 8.15
};

let smoothPan = 90;
let smoothTilt = 90;
let worldZ = 0;
let worldX = 0;
let heading = 0;

const beacons = [
  { angle: 90, label: 'NORTE (90°)', color: '#00e5ff' },
  { angle: 45, label: 'ESQ (45°)', color: '#22c55e' },
  { angle: 135, label: 'DIR (135°)', color: '#f59e0b' },
  { angle: 15, label: 'LIMITE ESQ', color: '#ec4899' },
  { angle: 165, label: 'LIMITE DIR', color: '#a855f7' },
];

const obstacles = [
  { x: -1.8, z: 4.5, w: 0.7, h: 0.9, c: '#22c55e', name: 'CAIXA A' },
  { x: 1.6, z: 7.0, w: 0.8, h: 1.1, c: '#38bdf8', name: 'BALIZA B' },
  { x: 0.0, z: 10.5, w: 0.9, h: 1.3, c: '#f59e0b', name: 'ALVO CENTRAL' },
  { x: -2.2, z: 13.5, w: 0.8, h: 1.0, c: '#a855f7', name: 'TORRE D' },
  { x: 2.1, z: 16.0, w: 0.8, h: 1.0, c: '#ef4444', name: 'BALIZA E' },
];

function draw() {
  requestAnimationFrame(draw);
  const st = window.roverState;

  if (st.sleeping) {
    ctx.fillStyle = '#06090e';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('❄️ SENSOR OV5640 EM SONECA TÉRMICA (0x3008 = 0x42)', W / 2, H / 2 - 10);
    ctx.fillStyle = '#64748b';
    ctx.font = '12px monospace';
    ctx.fillText('Consumo reduzido · Chip esfriando (' + st.temp.toFixed(1) + ' °C)', W / 2, H / 2 + 14);
    return;
  }

  smoothPan += (st.pan - smoothPan) * 0.22;
  smoothTilt += (st.tilt - smoothTilt) * 0.22;

  const avgMot = (st.motL + st.motR) / 2;
  const diffMot = (st.motL - st.motR) / 2;
  heading += diffMot * 0.008;
  worldZ += (avgMot / 255) * 0.14;
  worldX += Math.sin(heading * Math.PI / 180) * (avgMot / 255) * 0.08;

  // Tilt: 90 = centro. Olhar para cima (>90) desce o horizonte na tela; olhar para baixo (<90) sobe o horizonte.
  const horizonY = (H * 0.48) + (smoothTilt - 90) * (H * 0.0085);
  // Pan: 90 = centro. Olhar para esquerda (<90) ou direita (>90) desloca o cenário
  const viewYaw = (smoothPan - 90) + heading;

  // 1. Céu com gradiente espacial
  const skyGrad = ctx.createLinearGradient(0, 0, 0, Math.max(10, horizonY));
  skyGrad.addColorStop(0, '#040814');
  skyGrad.addColorStop(0.6, '#0a1628');
  skyGrad.addColorStop(1, '#112842');
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, W, Math.max(0, horizonY));

  // 2. Piso com perspectiva 3D
  const groundGrad = ctx.createLinearGradient(0, Math.max(0, horizonY), 0, H);
  groundGrad.addColorStop(0, '#09131c');
  groundGrad.addColorStop(1, '#05080c');
  ctx.fillStyle = groundGrad;
  ctx.fillRect(0, Math.max(0, horizonY), W, H - Math.max(0, horizonY));

  // Linhas radiais de perspectiva no chão (eixo X)
  ctx.strokeStyle = 'rgba(0, 229, 255, 0.18)';
  ctx.lineWidth = 1;
  const vanishX = (W / 2) - viewYaw * (W * 0.011);
  for (let i = -18; i <= 18; i++) {
    ctx.beginPath();
    ctx.moveTo(vanishX + i * 8, horizonY);
    ctx.lineTo(vanishX + i * 95, H);
    ctx.stroke();
  }

  // Linhas horizontais de profundidade no chão (eixo Z movendo-se com as rodas 4WD)
  const zPhase = ((worldZ % 1) + 1) % 1;
  for (let i = 1; i <= 14; i++) {
    const t = (i - zPhase) / 14;
    if (t <= 0.02) continue;
    const py = horizonY + Math.pow(t, 1.9) * (H - horizonY);
    if (py >= horizonY && py <= H) {
      ctx.strokeStyle = 'rgba(0, 229, 255, ' + (0.06 + t * 0.25).toFixed(2) + ')';
      ctx.beginPath();
      ctx.moveTo(0, py);
      ctx.lineTo(W, py);
      ctx.stroke();
    }
  }

  // Linha brilhante do horizonte
  ctx.strokeStyle = 'rgba(0, 229, 255, 0.65)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(0, horizonY);
  ctx.lineTo(W, horizonY);
  ctx.stroke();

  // 3. Balizas angulares no horizonte (servem para testar precisão de Pan/Tilt e VR)
  for (const b of beacons) {
    const bx = (W / 2) + (b.angle - 90 - (smoothPan - 90) - heading * 0.5) * (W * 0.011);
    if (bx > -50 && bx < W + 50) {
      ctx.fillStyle = b.color;
      ctx.fillRect(bx - 2, horizonY - 34, 4, 34);
      ctx.beginPath();
      ctx.arc(bx, horizonY - 38, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.font = 'bold 9px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(b.label, bx, horizonY - 48);
    }
  }

  // 4. Objetos 3D na arena que se aproximam/afastam ao andar com os motores 4WD
  for (const ob of obstacles) {
    let relZ = ((ob.z - worldZ) % 18 + 18) % 18;
    if (relZ < 0.8) relZ += 18;
    const scale = 140 / relZ;
    const ox = vanishX + (ob.x * 1.4) * scale;
    const oy = horizonY + (22 / relZ);
    const ow = ob.w * scale;
    const oh = ob.h * scale;

    if (ox + ow > 0 && ox - ow < W && oy > horizonY - 40) {
      ctx.fillStyle = 'rgba(10, 20, 32, 0.85)';
      ctx.strokeStyle = ob.c;
      ctx.lineWidth = 1.5;
      ctx.fillRect(ox - ow / 2, oy - oh, ow, oh);
      ctx.strokeRect(ox - ow / 2, oy - oh, ow, oh);

      if (relZ < 12) {
        ctx.fillStyle = ob.c;
        ctx.font = 'bold 9px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(ob.name + ' (' + relZ.toFixed(1) + 'm)', ox, oy - oh - 5);
      }
    }
  }

  // 5. Fita de Bússola Superior (Azimute Pan)
  ctx.fillStyle = 'rgba(0, 0, 0, 0.55)';
  ctx.fillRect(W * 0.2, 8, W * 0.6, 20);
  ctx.strokeStyle = 'rgba(255,255,255,0.15)';
  ctx.strokeRect(W * 0.2, 8, W * 0.6, 20);
  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 10px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('SIMULADOR 3D E2E · AZIMUTE ' + Math.round(smoothPan) + '° · PITCH ' + Math.round(smoothTilt) + '°', W / 2, 22);
}
requestAnimationFrame(draw);
</script>
</body>
</html>`;

export const CameraStream: React.FC<CameraStreamProps> = ({
  streamUrl,
  operationMode = 'simulation',
  isVR = false,
  panAngle = 90,
  tiltAngle = 90,
  motorLeftPwm = 0,
  motorRightPwm = 0,
  camSleeping = false,
  camMode = 'ATIVO',
  chipTemp = 44.5,
  vbat = 8.15,
  showHUD = true,
}) => {
  const [reloadKey, setReloadKey] = useState(0);
  const [hasError, setHasError] = useState(false);
  const [useMjpegInSim, setUseMjpegInSim] = useState(false);
  const webviewRef = useRef<any>(null);

  const isCanvas3D = operationMode === 'simulation' && !useMjpegInSim;

  // Converte /stream ou /capture para a página nativa otimizada /view do ESP32
  const viewUrl = streamUrl
    .replace(/\/capture\/?$/, '/view')
    .replace(/\/stream\/?$/, '/view');

  useEffect(() => {
    if (isCanvas3D && webviewRef.current) {
      const payload = JSON.stringify({
        pan: panAngle,
        tilt: tiltAngle,
        motL: motorLeftPwm,
        motR: motorRightPwm,
        sleeping: camSleeping,
        camMode,
        temp: chipTemp,
        vbat,
      });
      webviewRef.current.injectJavaScript(`window.roverState = ${payload}; true;`);
    }
  }, [isCanvas3D, panAngle, tiltAngle, motorLeftPwm, motorRightPwm, camSleeping, camMode, chipTemp, vbat]);

  const handleRefresh = () => {
    setHasError(false);
    setReloadKey((prev) => prev + 1);
  };

  return (
    <View style={[styles.container, isVR && styles.vrContainer]}>
      {!isCanvas3D && hasError ? (
        <View style={styles.errorContainer}>
          <Camera size={36} color="#64748b" />
          <Text style={styles.errorText}>Stream do ESP32 Indisponível</Text>
          <Text style={styles.errorSubtext}>{viewUrl}</Text>
          <View style={styles.errorBtnRow}>
            <TouchableOpacity style={styles.retryBtn} onPress={handleRefresh}>
              <RefreshCw size={14} color="#0f172a" />
              <Text style={styles.retryText}>Reconectar</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.streamWrapper}>
          <WebView
            ref={webviewRef}
            key={`${operationMode}-${useMjpegInSim}-${reloadKey}`}
            source={isCanvas3D ? { html: SIMULATOR_3D_HTML } : { uri: viewUrl }}
            originWhitelist={['*']}
            mixedContentMode="always"
            style={styles.webview}
            scrollEnabled={false}
            bounces={false}
            javaScriptEnabled={true}
            allowsInlineMediaPlayback={true}
            mediaPlaybackRequiresUserAction={false}
            androidHardwareAccelerationDisabled={false}
            androidLayerType="hardware"
            onError={() => {
              if (!isCanvas3D) setHasError(true);
            }}
          />
        </View>
      )}

      {/* Botão sutil para alternar entre Render 3D 60fps e Stream MJPEG do Mock quando em Simulação */}
      {operationMode === 'simulation' && !isVR && (
        <TouchableOpacity
          style={styles.simSourceBadge}
          onPress={() => {
            setHasError(false);
            setUseMjpegInSim((prev) => !prev);
          }}
          activeOpacity={0.8}
        >
          {isCanvas3D ? <Cpu size={11} color="#00e5ff" /> : <Radio size={11} color="#4ade80" />}
          <Text style={styles.simSourceText}>
            {isCanvas3D ? '3D 60FPS Nativo' : 'MJPEG Mock PC'}
          </Text>
        </TouchableOpacity>
      )}

      {/* HUD de Mira e Ângulos */}
      {showHUD && (
        <View style={styles.hudOverlay} pointerEvents="none">
          <View style={styles.crosshairCenter}>
            <View style={styles.crosshairH} />
            <View style={styles.crosshairV} />
            <View style={styles.crosshairDot} />
          </View>

          <View style={styles.anglesHUD}>
            <Text style={styles.hudText}>PAN: {Math.round(panAngle)}° · TILT: {Math.round(tiltAngle)}°</Text>
            <Text style={[styles.hudText, { color: '#cbd5e1' }]}>
              4WD: L {Math.round(motorLeftPwm)} | R {Math.round(motorRightPwm)}
            </Text>
            <Text style={[styles.hudText, { color: camSleeping ? '#38bdf8' : '#4ade80' }]}>
              {camSleeping ? '❄️ SONECA 0x3008' : `CAM ${camMode} · ${chipTemp.toFixed(1)}°C · ${vbat.toFixed(2)}V`}
            </Text>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    position: 'relative',
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  vrContainer: {
    borderRadius: 0,
    borderWidth: 0,
  },
  streamWrapper: {
    width: '100%',
    height: '100%',
    backgroundColor: '#000000',
    position: 'relative',
  },
  webview: {
    flex: 1,
    backgroundColor: '#000000',
    width: '100%',
    height: '100%',
  },
  errorContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    gap: 8,
  },
  errorText: {
    color: '#94a3b8',
    fontSize: 14,
    fontWeight: '700',
  },
  errorSubtext: {
    color: '#475569',
    fontSize: 11,
    textAlign: 'center',
    fontFamily: 'monospace',
  },
  errorBtnRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 4,
  },
  retryBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#38bdf8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  retryText: {
    color: '#0f172a',
    fontSize: 12,
    fontWeight: '700',
  },
  simSourceBadge: {
    position: 'absolute',
    top: 12,
    left: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingHorizontal: 9,
    paddingVertical: 5,
    backgroundColor: 'rgba(0, 0, 0, 0.72)',
    borderRadius: 999,
    borderWidth: 1,
    borderColor: 'rgba(0, 229, 255, 0.35)',
  },
  simSourceText: {
    color: '#e2e8f0',
    fontSize: 10,
    fontWeight: '700',
  },
  hudOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  crosshairCenter: {
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  crosshairH: {
    position: 'absolute',
    width: 28,
    height: 1,
    backgroundColor: 'rgba(0, 229, 255, 0.5)',
  },
  crosshairV: {
    position: 'absolute',
    height: 28,
    width: 1,
    backgroundColor: 'rgba(0, 229, 255, 0.5)',
  },
  crosshairDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#00e5ff',
  },
  anglesHUD: {
    position: 'absolute',
    bottom: 12,
    left: 12,
    backgroundColor: 'rgba(0, 0, 0, 0.72)',
    paddingHorizontal: 9,
    paddingVertical: 5,
    borderRadius: 6,
    gap: 2,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.12)',
  },
  hudText: {
    color: '#38bdf8',
    fontSize: 10,
    fontWeight: '700',
    fontFamily: 'monospace',
  },
});
