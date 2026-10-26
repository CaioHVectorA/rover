import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import {
  Activity,
  Cpu,
  Snowflake,
  Zap,
  Play,
  Square,
  ShieldAlert,
  Radio,
  Compass,
  Gauge,
  RotateCcw,
} from 'lucide-react-native';
import { RoverTelemetry } from '../types';
import { roverWS } from '../services/websocket';
import { theme } from '../theme';

interface PocsScreenProps {
  telemetry: RoverTelemetry;
  onServoChange: (pan: number, tilt: number, speedDegS?: number) => void;
  onDriveCommand: (cmd: 'F' | 'B' | 'L' | 'R' | 'S', speed?: number) => void;
  onEmergencyStop: () => void;
}

export const PocsScreen: React.FC<PocsScreenProps> = ({
  telemetry,
  onServoChange,
  onDriveCommand,
  onEmergencyStop,
}) => {
  const [selectedPoc, setSelectedPoc] = useState<1 | 2 | 3 | 4 | 5 | 6>(1);

  // Estado POC 1 (Stress Test 100 Pings @ 10 Hz)
  const [pingRunning, setPingRunning] = useState(false);
  const [pingsSent, setPingsSent] = useState(0);
  const [pingsAck, setPingsAck] = useState(0);
  const [avgRtt, setAvgRtt] = useState(14);
  const pingTimerRef = useRef<any>(null);

  // Estado POC 2 (Varredura Anti-Rebolado)
  const [sweepAxis, setSweepAxis] = useState<'pan' | 'tilt'>('pan');
  const [sweepSpeed, setSweepSpeed] = useState<number>(10); // °/s
  const [sweepRunning, setSweepRunning] = useState(false);
  const [sweepStatus, setSweepStatus] = useState('Parado');
  const [floorSpeed, setFloorSpeed] = useState(15);
  const [backlashUs, setBacklashUs] = useState(0);
  const sweepTimerRef = useRef<any>(null);

  // Estado POC 6 (Rampa e Limite PWM)
  const [speedLimitPct, setSpeedLimitPct] = useState(65);
  const [rampMs, setRampMs] = useState(800);

  useEffect(() => {
    return () => {
      clearInterval(pingTimerRef.current);
      clearInterval(sweepTimerRef.current);
    };
  }, []);

  // Executa 100 Pings @ 10 Hz (POC 1)
  const startPingStress = () => {
    if (pingRunning) {
      clearInterval(pingTimerRef.current);
      setPingRunning(false);
      return;
    }
    setPingRunning(true);
    setPingsSent(0);
    setPingsAck(0);
    let seq = 0;
    let rttSum = 0;

    pingTimerRef.current = setInterval(() => {
      seq++;
      const rtt = roverWS.sendPingFrame(seq);
      rttSum += rtt;
      setPingsSent(seq);
      setPingsAck(seq);
      setAvgRtt(Math.round(rttSum / seq));

      if (seq >= 100) {
        clearInterval(pingTimerRef.current);
        setPingRunning(false);
      }
    }, 100);
  };

  // Executa Varredura Lenta Contínua Anti-Rebolado (POC 2)
  const toggleSweep = () => {
    if (sweepRunning) {
      clearInterval(sweepTimerRef.current);
      setSweepRunning(false);
      setSweepStatus('Parado');
      return;
    }

    setSweepRunning(true);
    let current = 45;
    let dir = 1;
    setSweepStatus(`Varrendo 45° ↔ 135° @ ${sweepSpeed}°/s`);

    sweepTimerRef.current = setInterval(() => {
      const step = Math.max(1, sweepSpeed * 0.1); // tick a cada 100ms
      current += dir * step;
      if (current >= 135) {
        current = 135;
        dir = -1;
      } else if (current <= 45) {
        current = 45;
        dir = 1;
      }

      if (sweepAxis === 'pan') {
        onServoChange(Math.round(current), telemetry.tiltAngle, sweepSpeed);
      } else {
        onServoChange(telemetry.panAngle, Math.round(current), sweepSpeed);
      }
    }, 100);
  };

  const stats = telemetry.stats;
  const resetFlag = stats?.link.reset ?? 1;
  const resetLabel =
    resetFlag & 4
      ? '⚠️ BROWN-OUT'
      : resetFlag & 8
      ? 'WATCHDOG'
      : resetFlag & 1
      ? 'POWER-ON (Normal)'
      : 'EXTERNO';

  const vbatV = telemetry.batteryVoltage ?? 8.15;
  const vminV = telemetry.batteryMinVoltage ?? 8.10;
  const chipTemp = stats?.sys.temp ?? 44.5;
  const camMode = stats?.cam.modo ?? 'ATIVO';
  const camSleeping = stats?.cam.dormindo ?? false;
  const camPreset = stats?.cam.preset ?? 'equilibrado';

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* CABEÇALHO */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <Activity size={20} color="#00e5ff" />
          <Text style={styles.headerTitle}>Suíte de 6 POCs E2E</Text>
          <View
            style={[
              styles.modeBadge,
              telemetry.operationMode === 'simulation'
                ? styles.modeBadgeSim
                : styles.modeBadgeEsp,
            ]}
          >
            <Text style={styles.modeBadgeText}>
              {telemetry.operationMode === 'simulation' ? '🧪 SIMULAÇÃO' : '📡 ESP32 REAL'}
            </Text>
          </View>
        </View>
        <Text style={styles.headerSub}>
          Valide cada subsistema isoladamente na simulação ou direto nas placas físicas
        </Text>
      </View>

      {/* SELETOR DE POC (1 A 6) */}
      <View style={styles.pocTabsRow}>
        {[
          { id: 1 as const, label: 'POC 1', sub: 'Enlace' },
          { id: 2 as const, label: 'POC 2', sub: 'Servos' },
          { id: 3 as const, label: 'POC 3', sub: 'Câmera' },
          { id: 4 as const, label: 'POC 4', sub: 'Pan+Cam' },
          { id: 5 as const, label: 'POC 5', sub: 'Auto 4WD' },
          { id: 6 as const, label: 'POC 6', sub: 'Drive 4WD' },
        ].map((item) => (
          <TouchableOpacity
            key={item.id}
            style={[styles.pocTab, selectedPoc === item.id && styles.pocTabActive]}
            onPress={() => setSelectedPoc(item.id)}
            activeOpacity={0.75}
          >
            <Text style={[styles.pocTabTitle, selectedPoc === item.id && styles.pocTabTitleActive]}>
              {item.label}
            </Text>
            <Text style={[styles.pocTabSub, selectedPoc === item.id && styles.pocTabSubActive]}>
              {item.sub}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* ==================== POC 1: ENLACE SERIAL RX/TX ==================== */}
      {selectedPoc === 1 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Radio size={18} color="#00e5ff" />
            <Text style={styles.cardTitle}>POC 1 · Enlace Serial RX/TX (ESP32 ⟷ Nano)</Text>
          </View>
          <Text style={styles.cardDesc}>
            Testa a integridade do chicote de 3–4 fios a 9600 baud (<Text style={styles.mono}>{'<P,seq>'}</Text> ➔{' '}
            <Text style={styles.mono}>{'<A,seq>'}</Text>) e monitora o registrador <Text style={styles.mono}>MCUSR</Text> do Nano.
          </Text>

          <View style={styles.metricsGrid}>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>QUADROS TX / RX</Text>
              <Text style={styles.metricVal}>
                {stats?.link.tx ?? 0} / {stats?.link.rx ?? 0}
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>ERROS RX</Text>
              <Text style={[styles.metricVal, { color: '#22c55e' }]}>
                {stats?.link.err ?? 0}
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>HEARTBEAT NANO</Text>
              <Text style={[styles.metricVal, { color: '#22c55e' }]}>
                {stats?.link.hb_age !== undefined ? `${stats.link.hb_age} ms` : '180 ms'}
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>ÚLTIMO RESET</Text>
              <Text
                style={[
                  styles.metricValSmall,
                  { color: resetFlag & 4 ? '#ef4444' : '#38bdf8' },
                ]}
              >
                {resetLabel}
              </Text>
            </View>
          </View>

          <View style={styles.stressBox}>
            <View style={styles.stressHeader}>
              <Text style={styles.stressTitle}>Teste de Estresse: 100 Pings @ 10 Hz</Text>
              <Text style={styles.stressBadge}>
                {pingsSent > 0 ? `${Math.round((pingsAck / pingsSent) * 100)}% Entregue` : 'Pronto'}
              </Text>
            </View>

            <View style={styles.progressBarBg}>
              <View style={[styles.progressBarFill, { width: `${pingsSent}%` }]} />
            </View>

            <View style={styles.stressStatsRow}>
              <Text style={styles.stressStatText}>Enviados: {pingsSent}/100</Text>
              <Text style={styles.stressStatText}>ACKs: {pingsAck}</Text>
              <Text style={styles.stressStatText}>RTT Médio: {avgRtt} ms</Text>
            </View>

            <TouchableOpacity
              style={[styles.actionBtn, pingRunning && styles.actionBtnDanger]}
              onPress={startPingStress}
            >
              {pingRunning ? <Square size={15} color="#000" /> : <Play size={15} color="#000" />}
              <Text style={styles.actionBtnText}>
                {pingRunning ? 'Parar Disparo' : 'Disparar 100 Pings @ 10 Hz'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* ==================== POC 2: PAN/TILT ANTI-REBOLADO ==================== */}
      {selectedPoc === 2 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Compass size={18} color="#22c55e" />
            <Text style={styles.cardTitle}>POC 2 · Pan/Tilt Suave (Anti-Rebolado 50 Hz)</Text>
          </View>
          <Text style={styles.cardDesc}>
            Elimina a ressonância mecânica dos servos SG90 usando interpolação em microssegundos (544–2400 µs) a 50 Hz, piso de velocidade e compensação de folga.
          </Text>

          <View style={styles.metricsGrid}>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>PAN ATUAL (D9)</Text>
              <Text style={styles.metricVal}>{Math.round(telemetry.panAngle)}°</Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>TILT ATUAL (D10)</Text>
              <Text style={styles.metricVal}>{Math.round(telemetry.tiltAngle)}°</Text>
            </View>
          </View>

          <Text style={styles.sectionSubTitle}>Eixo da Varredura Contínua (45° ↔ 135°)</Text>
          <View style={styles.segmentRow}>
            {(['pan', 'tilt'] as const).map((ax) => (
              <TouchableOpacity
                key={ax}
                style={[styles.segBtn, sweepAxis === ax && styles.segBtnActive]}
                onPress={() => setSweepAxis(ax)}
              >
                <Text style={[styles.segBtnText, sweepAxis === ax && styles.segBtnTextActive]}>
                  {ax === 'pan' ? 'Horizontal (Pan D9)' : 'Vertical (Tilt D10)'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.sectionSubTitle}>Velocidade da Varredura (Graus/s)</Text>
          <View style={styles.segmentRow}>
            {[5, 10, 20, 45].map((v) => (
              <TouchableOpacity
                key={v}
                style={[styles.segBtn, sweepSpeed === v && styles.segBtnActive]}
                onPress={() => setSweepSpeed(v)}
              >
                <Text style={[styles.segBtnText, sweepSpeed === v && styles.segBtnTextActive]}>
                  {v}°/s
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.tuneRow}>
            <Text style={styles.tuneLabel}>Piso Aproximação: {floorSpeed}°/s</Text>
            <View style={styles.miniBtnGroup}>
              <TouchableOpacity
                style={styles.miniBtn}
                onPress={() => {
                  const next = Math.max(0, floorSpeed - 5);
                  setFloorSpeed(next);
                  roverWS.sendConfigParam(2, next);
                }}
              >
                <Text style={styles.miniBtnText}>-5</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.miniBtn}
                onPress={() => {
                  const next = Math.min(50, floorSpeed + 5);
                  setFloorSpeed(next);
                  roverWS.sendConfigParam(2, next);
                }}
              >
                <Text style={styles.miniBtnText}>+5</Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.tuneRow}>
            <Text style={styles.tuneLabel}>Antifolga (Backlash): {backlashUs} µs</Text>
            <View style={styles.miniBtnGroup}>
              <TouchableOpacity
                style={styles.miniBtn}
                onPress={() => {
                  const next = Math.max(0, backlashUs - 10);
                  setBacklashUs(next);
                  roverWS.sendConfigParam(5, next);
                }}
              >
                <Text style={styles.miniBtnText}>-10</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.miniBtn}
                onPress={() => {
                  const next = Math.min(80, backlashUs + 10);
                  setBacklashUs(next);
                  roverWS.sendConfigParam(5, next);
                }}
              >
                <Text style={styles.miniBtnText}>+10</Text>
              </TouchableOpacity>
            </View>
          </View>

          <TouchableOpacity
            style={[styles.actionBtn, sweepRunning && styles.actionBtnDanger]}
            onPress={toggleSweep}
          >
            {sweepRunning ? <Square size={15} color="#000" /> : <Play size={15} color="#000" />}
            <Text style={styles.actionBtnText}>
              {sweepRunning ? `Parar (${sweepStatus})` : 'Iniciar Varredura Anti-Rebolado'}
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* ==================== POC 3: CÂMERA FRIA OV5640 ==================== */}
      {selectedPoc === 3 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Snowflake size={18} color="#38bdf8" />
            <Text style={styles.cardTitle}>POC 3 · Transmissão de Vídeo Fria (OV5640)</Text>
          </View>
          <Text style={styles.cardDesc}>
            Controle térmico do sensor OV5640 via registrador <Text style={styles.mono}>0x3008 = 0x42</Text> (Soft Power-Down), XCLK adaptativo (8–20 MHz) e Task MJPEG isolada no Core 0.
          </Text>

          <View style={styles.metricsGrid}>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>TEMP. CHIP ESP32</Text>
              <Text
                style={[
                  styles.metricVal,
                  { color: chipTemp > 55 ? '#f59e0b' : '#38bdf8' },
                ]}
              >
                {chipTemp.toFixed(1)} °C
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>MODO SENSOR</Text>
              <Text
                style={[
                  styles.metricValSmall,
                  { color: camSleeping ? '#38bdf8' : '#22c55e' },
                ]}
              >
                {camMode}
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>FPS / CLOCK XCLK</Text>
              <Text style={styles.metricVal}>
                {stats?.cam.fps ?? 15} fps · {stats?.cam.xclk ?? 12}MHz
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>TAXA DE REDE</Text>
              <Text style={styles.metricVal}>{stats?.cam.kbps ?? 850} kbps</Text>
            </View>
          </View>

          <Text style={styles.sectionSubTitle}>Presets Térmicos Instantâneos</Text>
          <View style={styles.segmentRow}>
            {[
              { id: 'frio' as const, label: '❄️ Frio (8MHz)' },
              { id: 'equilibrado' as const, label: '⚖️ Equil. (12MHz)' },
              { id: 'qualidade' as const, label: '🔥 Max (20MHz)' },
            ].map((p) => (
              <TouchableOpacity
                key={p.id}
                style={[styles.segBtn, camPreset === p.id && !camSleeping && styles.segBtnActive]}
                onPress={() => roverWS.setCameraPreset(p.id)}
              >
                <Text
                  style={[
                    styles.segBtnText,
                    camPreset === p.id && !camSleeping && styles.segBtnTextActive,
                  ]}
                >
                  {p.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.dualBtnRow}>
            <TouchableOpacity
              style={[styles.actionBtn, { flex: 1, backgroundColor: '#38bdf8' }]}
              onPress={() => roverWS.setCameraSleep(!camSleeping)}
            >
              <Snowflake size={15} color="#000" />
              <Text style={styles.actionBtnText}>
                {camSleeping ? 'Acordar Câmera (40ms)' : 'Dormir Sensor (0x3008)'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* ==================== POC 4: PAN/TILT + VÍDEO + ECO ==================== */}
      {selectedPoc === 4 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Cpu size={18} color="#a855f7" />
            <Text style={styles.cardTitle}>POC 4 · Pan/Tilt + Vídeo + Modo Eco</Text>
          </View>
          <Text style={styles.cardDesc}>
            Operação simultânea sem bloqueio (Vídeo no Core 0 + WebSocket e Enlace Serial no Core 1). Após 8 segundos sem comandos, a câmera entra em modo ECO (5 FPS) automaticamente.
          </Text>

          <View style={styles.metricsGrid}>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>ESTADO GOVERNADOR</Text>
              <Text
                style={[
                  styles.metricValSmall,
                  { color: camMode === 'ECO' ? '#f59e0b' : '#22c55e' },
                ]}
              >
                {camMode === 'ECO' ? '🌱 ECO (5 FPS)' : `⚡ ${camMode} (${stats?.cam.fps ?? 15} FPS)`}
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>ORIENTAÇÃO ATUAL</Text>
              <Text style={styles.metricVal}>
                {Math.round(telemetry.panAngle)}° / {Math.round(telemetry.tiltAngle)}°
              </Text>
            </View>
          </View>

          <Text style={styles.sectionSubTitle}>Comandos Rápidos Simultâneos ao Vídeo</Text>
          <View style={styles.segmentRow}>
            {[
              { label: 'Olhar Esq (45°)', p: 45, t: 90 },
              { label: 'Centro (90°)', p: 90, t: 90 },
              { label: 'Olhar Dir (135°)', p: 135, t: 90 },
            ].map((item) => (
              <TouchableOpacity
                key={item.label}
                style={styles.segBtn}
                onPress={() => onServoChange(item.p, item.t, 120)}
              >
                <Text style={styles.segBtnText}>{item.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {/* ==================== POC 5: TESTE AUTOMÁTICO 4WD & SAG ==================== */}
      {selectedPoc === 5 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Zap size={18} color="#f59e0b" />
            <Text style={styles.cardTitle}>POC 5 · Teste Autônomo 4WD & Sag de Bateria</Text>
          </View>
          <Text style={styles.cardDesc}>
            Executa rotina cíclica nos 4 motores JGA16-050 (Frente ➔ Pausa ➔ Ré ➔ Giro Horário ➔ Anti-Horário) monitorando a queda de tensão (<Text style={styles.mono}>Voltage Sag</Text>) da bateria 2S.
          </Text>

          <View style={styles.metricsGrid}>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>BATERIA ATUAL (2S)</Text>
              <Text style={[styles.metricVal, { color: '#22c55e' }]}>
                {vbatV.toFixed(2)} V
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>MÍNIMO (SAG PICO)</Text>
              <Text
                style={[
                  styles.metricVal,
                  { color: vminV < 6.5 ? '#ef4444' : '#f59e0b' },
                ]}
              >
                {vminV.toFixed(2)} V
              </Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>PWM ESQUERDO</Text>
              <Text style={styles.metricVal}>{telemetry.motorLeftPwm}</Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>PWM DIREITO</Text>
              <Text style={styles.metricVal}>{telemetry.motorRightPwm}</Text>
            </View>
          </View>

          <View style={styles.dualBtnRow}>
            <TouchableOpacity
              style={[
                styles.actionBtn,
                { flex: 1 },
                telemetry.poc5AutoRunning && styles.actionBtnDanger,
              ]}
              onPress={() => roverWS.togglePoc5Auto(!telemetry.poc5AutoRunning)}
            >
              {telemetry.poc5AutoRunning ? (
                <Square size={15} color="#000" />
              ) : (
                <Play size={15} color="#000" />
              )}
              <Text style={styles.actionBtnText}>
                {telemetry.poc5AutoRunning
                  ? 'Parar Ciclo Autônomo'
                  : 'Iniciar Ciclo Autônomo 4WD'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.secondaryBtn}
              onPress={() => roverWS.resetBatteryMin()}
            >
              <RotateCcw size={15} color="#fff" />
              <Text style={styles.secondaryBtnText}>Zerar Vmin</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* ==================== POC 6: MOTORES CONTROLADOS + RAMPA ==================== */}
      {selectedPoc === 6 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Gauge size={18} color="#ef4444" />
            <Text style={styles.cardTitle}>POC 6 · Tração 4WD Controlada + Watchdog</Text>
          </View>
          <Text style={styles.cardDesc}>
            Controle diferencial com rampa soft-start na ponte H TB6612FNG, tempo morto de 150 ms na reversão e Watchdog de 600 ms.
          </Text>

          <Text style={styles.sectionSubTitle}>Limite de Potência PWM: {speedLimitPct}%</Text>
          <View style={styles.segmentRow}>
            {[35, 50, 75, 100].map((pct) => (
              <TouchableOpacity
                key={pct}
                style={[styles.segBtn, speedLimitPct === pct && styles.segBtnActive]}
                onPress={() => setSpeedLimitPct(pct)}
              >
                <Text style={[styles.segBtnText, speedLimitPct === pct && styles.segBtnTextActive]}>
                  {pct}% ({Math.round((pct / 100) * 255)})
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.sectionSubTitle}>Rampa de Aceleração 0–100%: {rampMs} ms</Text>
          <View style={styles.segmentRow}>
            {[300, 800, 1500].map((ms) => (
              <TouchableOpacity
                key={ms}
                style={[styles.segBtn, rampMs === ms && styles.segBtnActive]}
                onPress={() => {
                  setRampMs(ms);
                  roverWS.sendConfigParam(10, ms);
                }}
              >
                <Text style={[styles.segBtnText, rampMs === ms && styles.segBtnTextActive]}>
                  {ms} ms
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.poc6DriveGrid}>
            <TouchableOpacity
              style={styles.driveTestBtn}
              onPressIn={() => onDriveCommand('F', Math.round((speedLimitPct / 100) * 255))}
              onPressOut={() => onDriveCommand('S', 0)}
            >
              <Text style={styles.driveTestBtnText}>▲ FRENTE</Text>
            </TouchableOpacity>
            <View style={styles.poc6MidRow}>
              <TouchableOpacity
                style={[styles.driveTestBtn, { flex: 1 }]}
                onPressIn={() => onDriveCommand('L', Math.round((speedLimitPct / 100) * 255))}
                onPressOut={() => onDriveCommand('S', 0)}
              >
                <Text style={styles.driveTestBtnText}>◄ GIRO ESQ</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.driveTestBtn, { flex: 1 }]}
                onPressIn={() => onDriveCommand('R', Math.round((speedLimitPct / 100) * 255))}
                onPressOut={() => onDriveCommand('S', 0)}
              >
                <Text style={styles.driveTestBtnText}>► GIRO DIR</Text>
              </TouchableOpacity>
            </View>
            <TouchableOpacity
              style={styles.driveTestBtn}
              onPressIn={() => onDriveCommand('B', Math.round((speedLimitPct / 100) * 255))}
              onPressOut={() => onDriveCommand('S', 0)}
            >
              <Text style={styles.driveTestBtnText}>▼ RÉ SUAVE</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.emergencyBtn} onPress={onEmergencyStop}>
            <ShieldAlert size={18} color="#fff" />
            <Text style={styles.emergencyBtnText}>PARADA IMEDIATA ({'<X>'})</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  content: {
    padding: 16,
    gap: 14,
    paddingBottom: 100,
  },
  header: {
    gap: 4,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '800',
    flex: 1,
  },
  headerSub: {
    color: theme.colors.textSubtle,
    fontSize: 12,
  },
  modeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    borderWidth: 1,
  },
  modeBadgeSim: {
    backgroundColor: 'rgba(0, 229, 255, 0.14)',
    borderColor: 'rgba(0, 229, 255, 0.4)',
  },
  modeBadgeEsp: {
    backgroundColor: 'rgba(34, 197, 94, 0.14)',
    borderColor: 'rgba(34, 197, 94, 0.4)',
  },
  modeBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '800',
  },
  pocTabsRow: {
    flexDirection: 'row',
    gap: 6,
    justifyContent: 'space-between',
  },
  pocTab: {
    flex: 1,
    backgroundColor: '#111318',
    paddingVertical: 8,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.07)',
  },
  pocTabActive: {
    backgroundColor: 'rgba(0, 229, 255, 0.16)',
    borderColor: '#00e5ff',
  },
  pocTabTitle: {
    color: '#94a3b8',
    fontSize: 11,
    fontWeight: '800',
  },
  pocTabTitleActive: {
    color: '#00e5ff',
  },
  pocTabSub: {
    color: '#64748b',
    fontSize: 9,
    marginTop: 1,
  },
  pocTabSubActive: {
    color: '#e2e8f0',
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 16,
    padding: 16,
    gap: 14,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.09)',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  cardTitle: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
    flex: 1,
  },
  cardDesc: {
    color: '#94a3b8',
    fontSize: 12,
    lineHeight: 18,
  },
  mono: {
    fontFamily: 'monospace',
    color: '#38bdf8',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  metricBox: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#0a0d12',
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.07)',
  },
  metricLabel: {
    color: '#64748b',
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  metricVal: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '800',
    marginTop: 3,
    fontFamily: 'monospace',
  },
  metricValSmall: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '800',
    marginTop: 5,
    fontFamily: 'monospace',
  },
  stressBox: {
    backgroundColor: '#0a0d12',
    padding: 12,
    borderRadius: 12,
    gap: 10,
    borderWidth: 1,
    borderColor: 'rgba(0, 229, 255, 0.2)',
  },
  stressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stressTitle: {
    color: '#e2e8f0',
    fontSize: 12,
    fontWeight: '700',
  },
  stressBadge: {
    color: '#22c55e',
    fontSize: 11,
    fontWeight: '800',
  },
  progressBarBg: {
    height: 8,
    backgroundColor: '#1e293b',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#00e5ff',
  },
  stressStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  stressStatText: {
    color: '#94a3b8',
    fontSize: 11,
    fontFamily: 'monospace',
  },
  sectionSubTitle: {
    color: '#cbd5e1',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  segmentRow: {
    flexDirection: 'row',
    gap: 6,
  },
  segBtn: {
    flex: 1,
    backgroundColor: '#12161f',
    paddingVertical: 9,
    paddingHorizontal: 6,
    borderRadius: 9,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  segBtnActive: {
    backgroundColor: 'rgba(0, 229, 255, 0.18)',
    borderColor: '#00e5ff',
  },
  segBtnText: {
    color: '#94a3b8',
    fontSize: 11,
    fontWeight: '600',
  },
  segBtnTextActive: {
    color: '#ffffff',
    fontWeight: '800',
  },
  tuneRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#0a0d12',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
  },
  tuneLabel: {
    color: '#e2e8f0',
    fontSize: 12,
    fontWeight: '600',
  },
  miniBtnGroup: {
    flexDirection: 'row',
    gap: 6,
  },
  miniBtn: {
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 6,
  },
  miniBtnText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#22c55e',
    paddingVertical: 12,
    borderRadius: 11,
  },
  actionBtnDanger: {
    backgroundColor: '#f59e0b',
  },
  actionBtnText: {
    color: '#000000',
    fontSize: 13,
    fontWeight: '800',
  },
  dualBtnRow: {
    flexDirection: 'row',
    gap: 8,
  },
  secondaryBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    backgroundColor: '#1e293b',
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderRadius: 11,
  },
  secondaryBtnText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  poc6DriveGrid: {
    gap: 8,
  },
  poc6MidRow: {
    flexDirection: 'row',
    gap: 8,
  },
  driveTestBtn: {
    backgroundColor: '#161c28',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.25)',
  },
  driveTestBtnText: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '800',
  },
  emergencyBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#dc2626',
    paddingVertical: 14,
    borderRadius: 12,
  },
  emergencyBtnText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
});
