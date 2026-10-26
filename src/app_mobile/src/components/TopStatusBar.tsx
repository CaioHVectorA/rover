import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { OperationMode, RoverTelemetry } from '../types';
import { theme } from '../theme';

interface TopStatusBarProps {
  telemetry: RoverTelemetry;
  onRecenter: () => void;
  onReconnect?: () => void;
  onToggleMode?: (nextMode: OperationMode) => void;
}

export const TopStatusBar: React.FC<TopStatusBarProps> = ({
  telemetry,
  onRecenter,
  onReconnect,
  onToggleMode,
}) => {
  const insets = useSafeAreaInsets();
  const [justCalibrated, setJustCalibrated] = useState(false);

  const handlePress = () => {
    onRecenter();
    setJustCalibrated(true);
    setTimeout(() => setJustCalibrated(false), 1200);
  };

  const isSim = telemetry.operationMode === 'simulation';

  return (
    <View style={[styles.header, { paddingTop: Math.max(insets.top, 12) }]}>
      <View style={styles.leftGroup}>
        {/* Seletor Rápido Simulação vs ESP32 */}
        <TouchableOpacity
          style={[styles.modePill, isSim ? styles.modePillSim : styles.modePillEsp]}
          onPress={() => onToggleMode && onToggleMode(isSim ? 'esp32' : 'simulation')}
          activeOpacity={0.75}
        >
          <Text style={[styles.modePillText, isSim ? styles.modeTextSim : styles.modeTextEsp]}>
            {isSim ? '🧪 SIM' : '📡 ESP'}
          </Text>
        </TouchableOpacity>

        {/* Status da Conexão */}
        <TouchableOpacity
          style={styles.statusPill}
          onPress={onReconnect}
          activeOpacity={0.7}
        >
          <View
            style={[
              styles.dot,
              { backgroundColor: telemetry.connected ? theme.colors.success : theme.colors.danger },
            ]}
          />
          <Text style={styles.statusText}>
            {telemetry.connected ? `${telemetry.pingMs}ms` : 'Offline'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Ângulos Pan / Tilt + Bateria */}
      <View style={styles.angleDisplay}>
        <Text style={styles.angleText}>
          {Math.round(telemetry.panAngle)}° <Text style={styles.dotSeparator}>·</Text>{' '}
          {Math.round(telemetry.tiltAngle)}°
          {telemetry.batteryVoltage ? (
            <Text style={styles.vbatText}> · {telemetry.batteryVoltage.toFixed(1)}V</Text>
          ) : null}
        </Text>
      </View>

      {/* Botão Calibrar */}
      <TouchableOpacity
        style={[styles.calBtn, justCalibrated && styles.calBtnActive]}
        onPress={handlePress}
        activeOpacity={0.7}
      >
        <Text style={[styles.calBtnText, justCalibrated && styles.calBtnTextActive]}>
          {justCalibrated ? 'Zerado' : 'Calibrar'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingBottom: 10,
    backgroundColor: '#000000',
  },
  leftGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  modePill: {
    paddingVertical: 4,
    paddingHorizontal: 9,
    borderRadius: theme.radius.full,
    borderWidth: 1,
  },
  modePillSim: {
    backgroundColor: 'rgba(0, 229, 255, 0.14)',
    borderColor: 'rgba(0, 229, 255, 0.45)',
  },
  modePillEsp: {
    backgroundColor: 'rgba(34, 197, 94, 0.14)',
    borderColor: 'rgba(34, 197, 94, 0.45)',
  },
  modePillText: {
    fontSize: 11,
    fontWeight: '800',
  },
  modeTextSim: {
    color: '#00e5ff',
  },
  modeTextEsp: {
    color: '#4ade80',
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingVertical: 4,
    paddingHorizontal: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: theme.radius.full,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  statusText: {
    color: theme.colors.textMuted,
    fontSize: 11,
    fontWeight: '600',
  },
  angleDisplay: {
    paddingVertical: 4,
    paddingHorizontal: 6,
  },
  angleText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
    fontVariant: ['tabular-nums'],
  },
  vbatText: {
    color: '#4ade80',
    fontSize: 11,
    fontWeight: '600',
  },
  dotSeparator: {
    color: theme.colors.textSubtle,
  },
  calBtn: {
    paddingVertical: 5,
    paddingHorizontal: 11,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: theme.radius.full,
  },
  calBtnActive: {
    backgroundColor: theme.colors.success,
  },
  calBtnText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '600',
  },
  calBtnTextActive: {
    color: '#000000',
    fontWeight: '700',
  },
});
