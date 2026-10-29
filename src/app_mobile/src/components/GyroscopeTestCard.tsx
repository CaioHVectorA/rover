import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Compass, RotateCcw, Activity, ShieldCheck, ArrowUpDown, ArrowLeftRight } from 'lucide-react-native';
import { headTracking } from '../services/sensors';
import { GyroDiagnostics, HeadTrackingConfig } from '../types';
import { theme } from '../theme';

interface GyroscopeTestCardProps {
  onRecenter: () => void;
  onServoChange?: (pan: number, tilt: number) => void;
  headConfig: HeadTrackingConfig;
  onUpdateHeadConfig: (config: Partial<HeadTrackingConfig>) => void;
}

export const GyroscopeTestCard: React.FC<GyroscopeTestCardProps> = ({
  onRecenter,
  onServoChange,
  headConfig,
  onUpdateHeadConfig,
}) => {
  const [diag, setDiag] = useState<GyroDiagnostics>(headTracking.getDiagnostics());
  const [calibratedBadge, setCalibratedBadge] = useState(false);

  useEffect(() => {
    headTracking.onDiagnostics((newDiag) => {
      setDiag(newDiag);
    });

    return () => {
      headTracking.onDiagnostics(null);
    };
  }, []);

  const handleRecenter = () => {
    onRecenter();
    setCalibratedBadge(true);
    setTimeout(() => setCalibratedBadge(false), 1200);
  };

  // Coordenadas normalizadas do radar (-1 a +1)
  // Pan varia de 30° a 150° (centro 90°)
  // Tilt varia de 40° a 140° (centro 90°)
  const normX = Math.max(-1, Math.min(1, (diag.smoothPan - 90) / 60));
  const normY = Math.max(-1, Math.min(1, (diag.smoothTilt - 90) / 50));

  // Tamanho da mira no radar
  const RADAR_SIZE = 120;
  const dotX = RADAR_SIZE / 2 + normX * (RADAR_SIZE / 2 - 12) - 8;
  const dotY = RADAR_SIZE / 2 - normY * (RADAR_SIZE / 2 - 12) - 8;

  const backendName =
    diag.backend === 'device-motion'
      ? 'DeviceMotion (Fusão 3D)'
      : diag.backend === 'gyro-accel'
      ? 'Giroscópio + Acelerômetro'
      : diag.backend === 'simulated'
      ? 'Simulação / Emulador'
      : 'Sensor Inativo';

  const backendColor =
    diag.backend === 'device-motion'
      ? theme.colors.success
      : diag.backend === 'gyro-accel'
      ? theme.colors.accent
      : '#f59e0b';

  return (
    <View style={styles.card}>
      {/* Cabeçalho */}
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Compass size={18} color={theme.colors.accent} />
          <Text style={styles.title}>TESTE DO GIROSCÓPIO & PAN/TILT</Text>
        </View>
        <View style={[styles.badge, { borderColor: backendColor }]}>
          <Activity size={12} color={backendColor} />
          <Text style={[styles.badgeText, { color: backendColor }]}>
            {diag.hz > 0 ? `${diag.hz} Hz` : 'Pronto'}
          </Text>
        </View>
      </View>

      <Text style={styles.backendText}>
        Backend ativo: <Text style={{ color: backendColor, fontWeight: '700' }}>{backendName}</Text>
      </Text>

      {/* Área Central: Radar Visual + Indicadores Numéricos */}
      <View style={styles.mainContent}>
        {/* Radar da Mira da Cabeça */}
        <View style={[styles.radarBox, { width: RADAR_SIZE, height: RADAR_SIZE }]}>
          <View style={styles.radarCrosshairH} />
          <View style={styles.radarCrosshairV} />
          <View style={styles.radarCircleInner} />
          <View style={[styles.radarDot, { left: dotX, top: dotY }]} />
        </View>

        {/* Leituras Numéricas dos Servos */}
        <View style={styles.readingsCol}>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>SERVO PAN (HORIZONTAL)</Text>
            <Text style={[styles.metricValue, { color: theme.colors.accent }]}>
              {diag.smoothPan}°
            </Text>
            <Text style={styles.metricSub}>Limites: {headConfig.panMin}° a {headConfig.panMax}°</Text>
          </View>

          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>SERVO TILT (VERTICAL)</Text>
            <Text style={[styles.metricValue, { color: theme.colors.success }]}>
              {diag.smoothTilt}°
            </Text>
            <Text style={styles.metricSub}>Limites: {headConfig.tiltMin}° a {headConfig.tiltMax}°</Text>
          </View>
        </View>
      </View>

      {/* Status da Orientação Bruta */}
      <View style={styles.rawAnglesRow}>
        <Text style={styles.rawText}>Yaw: {diag.rawYaw}°</Text>
        <Text style={styles.rawText}>Pitch: {diag.rawPitch}°</Text>
        <Text style={styles.rawText}>Modo: {diag.isLandscape ? 'VR Horizontal' : 'Vertical'}</Text>
      </View>

      {/* Botões de Ação Rápida */}
      <View style={styles.actionRow}>
        <TouchableOpacity
          style={[styles.btnAction, styles.btnRecenter, calibratedBadge && styles.btnRecenterActive]}
          onPress={handleRecenter}
          activeOpacity={0.7}
        >
          <RotateCcw size={16} color="#ffffff" />
          <Text style={styles.btnActionText}>
            {calibratedBadge ? 'Centro Gravado!' : 'Centralizar (90°/90°)'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.btnAction,
            headConfig.enabled ? styles.btnGyroActive : styles.btnGyroInactive,
          ]}
          onPress={() => onUpdateHeadConfig({ enabled: !headConfig.enabled })}
          activeOpacity={0.7}
        >
          <ShieldCheck size={16} color={headConfig.enabled ? '#000000' : '#ffffff'} />
          <Text
            style={[
              styles.btnActionText,
              headConfig.enabled ? { color: '#000000' } : { color: '#ffffff' },
            ]}
          >
            {headConfig.enabled ? 'Giroscópio Ligado' : 'Ligar Giroscópio'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Controles de Inversão de Eixos */}
      <View style={styles.inversionRow}>
        <TouchableOpacity
          style={[styles.inversionChip, headConfig.invertPan && styles.inversionChipActive]}
          onPress={() => onUpdateHeadConfig({ invertPan: !headConfig.invertPan })}
          activeOpacity={0.7}
        >
          <ArrowLeftRight size={14} color={headConfig.invertPan ? theme.colors.accent : theme.colors.textMuted} />
          <Text style={[styles.inversionText, headConfig.invertPan && styles.inversionTextActive]}>
            Inverter Pan {headConfig.invertPan ? '(Invertido)' : '(Normal)'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.inversionChip, headConfig.invertTilt && styles.inversionChipActive]}
          onPress={() => onUpdateHeadConfig({ invertTilt: !headConfig.invertTilt })}
          activeOpacity={0.7}
        >
          <ArrowUpDown size={14} color={headConfig.invertTilt ? theme.colors.accent : theme.colors.textMuted} />
          <Text style={[styles.inversionText, headConfig.invertTilt && styles.inversionTextActive]}>
            Inverter Tilt {headConfig.invertTilt ? '(Invertido)' : '(Normal)'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Botões Rápidos de Teste para Emulador / Sem Mover Fisicamente */}
      <View style={styles.quickTestBox}>
        <Text style={styles.quickTestTitle}>Teste Interativo Rápido (ou sem giroscópio físico):</Text>
        <View style={styles.quickTestButtons}>
          <TouchableOpacity
            style={styles.btnQuick}
            onPress={() => headTracking.simulateMotion(-15, 0)}
          >
            <Text style={styles.btnQuickText}>◀ Esq (-15°)</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.btnQuick}
            onPress={() => headTracking.simulateMotion(0, 15)}
          >
            <Text style={styles.btnQuickText}>▲ Cima (+15°)</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.btnQuick}
            onPress={() => headTracking.simulateMotion(0, -15)}
          >
            <Text style={styles.btnQuickText}>▼ Baixo (-15°)</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.btnQuick}
            onPress={() => headTracking.simulateMotion(15, 0)}
          >
            <Text style={styles.btnQuickText}>Dir (+15°) ▶</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    padding: 14,
    marginVertical: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  title: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.text,
    letterSpacing: 0.5,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
    borderWidth: 1,
    backgroundColor: '#0c121e',
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
  },
  backendText: {
    fontSize: 11,
    color: theme.colors.textMuted,
    marginBottom: 12,
  },
  mainContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    marginBottom: 12,
    gap: 12,
  },
  radarBox: {
    backgroundColor: '#090d15',
    borderRadius: 60,
    borderWidth: 1.5,
    borderColor: '#1e293b',
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  radarCrosshairH: {
    position: 'absolute',
    width: '100%',
    height: 1,
    backgroundColor: 'rgba(56, 189, 248, 0.25)',
  },
  radarCrosshairV: {
    position: 'absolute',
    height: '100%',
    width: 1,
    backgroundColor: 'rgba(56, 189, 248, 0.25)',
  },
  radarCircleInner: {
    position: 'absolute',
    width: 60,
    height: 60,
    borderRadius: 30,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.2)',
  },
  radarDot: {
    position: 'absolute',
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: theme.colors.accent,
    borderWidth: 2,
    borderColor: '#ffffff',
    shadowColor: theme.colors.accent,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 6,
    elevation: 4,
  },
  readingsCol: {
    flex: 1,
    gap: 8,
  },
  metricItem: {
    backgroundColor: '#0c111c',
    borderRadius: theme.radius.sm,
    borderWidth: 1,
    borderColor: '#1c2638',
    padding: 8,
  },
  metricLabel: {
    fontSize: 9,
    fontWeight: '700',
    color: theme.colors.textMuted,
    letterSpacing: 0.5,
  },
  metricValue: {
    fontSize: 22,
    fontWeight: '800',
    marginVertical: 2,
  },
  metricSub: {
    fontSize: 9,
    color: '#64748b',
  },
  rawAnglesRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#0c111c',
    padding: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#1e293b',
    marginBottom: 10,
  },
  rawText: {
    fontSize: 10,
    color: theme.colors.textMuted,
    fontFamily: 'monospace',
  },
  actionRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 8,
  },
  btnAction: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 10,
    borderRadius: 6,
  },
  btnRecenter: {
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
  },
  btnRecenterActive: {
    backgroundColor: theme.colors.success,
    borderColor: theme.colors.success,
  },
  btnGyroActive: {
    backgroundColor: theme.colors.accent,
  },
  btnGyroInactive: {
    backgroundColor: '#1c2638',
    borderWidth: 1,
    borderColor: '#334155',
  },
  btnActionText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#ffffff',
  },
  inversionRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  inversionChip: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 7,
    paddingHorizontal: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#1e293b',
    backgroundColor: '#0c111c',
  },
  inversionChipActive: {
    borderColor: theme.colors.accent,
    backgroundColor: 'rgba(56, 189, 248, 0.12)',
  },
  inversionText: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.colors.textMuted,
  },
  inversionTextActive: {
    color: theme.colors.accent,
  },
  quickTestBox: {
    backgroundColor: '#070a10',
    borderRadius: 6,
    padding: 8,
    borderWidth: 1,
    borderColor: '#1e293b',
  },
  quickTestTitle: {
    fontSize: 10,
    color: theme.colors.textMuted,
    marginBottom: 6,
  },
  quickTestButtons: {
    flexDirection: 'row',
    gap: 6,
  },
  btnQuick: {
    flex: 1,
    backgroundColor: '#1a2333',
    paddingVertical: 6,
    borderRadius: 4,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#2d3b52',
  },
  btnQuickText: {
    fontSize: 9,
    fontWeight: '700',
    color: '#e2e8f0',
  },
});
