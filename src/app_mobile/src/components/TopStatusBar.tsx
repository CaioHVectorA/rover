import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { RoverTelemetry } from '../types';
import { theme } from '../theme';

interface TopStatusBarProps {
  telemetry: RoverTelemetry;
  onRecenter: () => void;
  onReconnect?: () => void;
}

export const TopStatusBar: React.FC<TopStatusBarProps> = ({
  telemetry,
  onRecenter,
  onReconnect,
}) => {
  const insets = useSafeAreaInsets();
  const [justCalibrated, setJustCalibrated] = useState(false);

  const handlePress = () => {
    onRecenter();
    setJustCalibrated(true);
    setTimeout(() => setJustCalibrated(false), 1200);
  };

  return (
    <View style={[styles.header, { paddingTop: Math.max(insets.top, 12) }]}>
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
          {telemetry.connected ? `${telemetry.pingMs} ms` : 'Offline'}
        </Text>
      </TouchableOpacity>

      {/* Ângulos Pan / Tilt */}
      <View style={styles.angleDisplay}>
        <Text style={styles.angleText}>
          {Math.round(telemetry.panAngle)}° <Text style={styles.dotSeparator}>·</Text> {Math.round(telemetry.tiltAngle)}°
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
    paddingHorizontal: 16,
    paddingBottom: 10,
    backgroundColor: '#000000',
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
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
    fontSize: 12,
    fontWeight: '500',
  },
  angleDisplay: {
    paddingVertical: 4,
    paddingHorizontal: 10,
  },
  angleText: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '600',
    fontVariant: ['tabular-nums'],
  },
  dotSeparator: {
    color: theme.colors.textSubtle,
  },
  calBtn: {
    paddingVertical: 5,
    paddingHorizontal: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: theme.radius.full,
  },
  calBtnActive: {
    backgroundColor: theme.colors.success,
  },
  calBtnText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  calBtnTextActive: {
    color: '#000000',
    fontWeight: '700',
  },
});
