import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { ConnectionConfig, HeadTrackingConfig, RoverTelemetry } from '../types';
import { theme } from '../theme';

interface SettingsScreenProps {
  connectionConfig: ConnectionConfig;
  onSaveConnection: (config: ConnectionConfig) => void;
  telemetry: RoverTelemetry;
  headConfig: HeadTrackingConfig;
  onUpdateHeadConfig: (config: Partial<HeadTrackingConfig>) => void;
  onManualServoChange: (pan: number, tilt: number) => void;
  onRecenter: () => void;
  onDriveCommand: (cmd: 'F' | 'B' | 'L' | 'R' | 'S') => void;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({
  connectionConfig,
  onSaveConnection,
  telemetry,
  headConfig,
  onUpdateHeadConfig,
  onManualServoChange,
}) => {
  const [ip, setIp] = useState(connectionConfig.ip);
  const [wsPort, setWsPort] = useState(String(connectionConfig.wsPort));
  const [streamPort, setStreamPort] = useState(String(connectionConfig.streamPort));
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    onSaveConnection({
      ip: ip.trim(),
      wsPort: parseInt(wsPort, 10) || 81,
      streamPort: parseInt(streamPort, 10) || 80,
      streamPath: connectionConfig.streamPath,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* SEÇÃO 1: CONEXÃO */}
      <View style={styles.group}>
        <Text style={styles.groupTitle}>Conexão com o Robô</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.label}>Endereço IP</Text>
            <TextInput
              style={styles.input}
              value={ip}
              onChangeText={setIp}
              placeholder="10.0.1.6"
              placeholderTextColor={theme.colors.textSubtle}
              autoCapitalize="none"
            />
          </View>

          <View style={styles.divider} />

          <View style={styles.row}>
            <Text style={styles.label}>Porta WebSocket</Text>
            <TextInput
              style={styles.inputSmall}
              value={wsPort}
              onChangeText={setWsPort}
              placeholder="8082"
              placeholderTextColor={theme.colors.textSubtle}
              keyboardType="number-pad"
            />
          </View>

          <View style={styles.divider} />

          <View style={styles.row}>
            <Text style={styles.label}>Porta de Vídeo</Text>
            <TextInput
              style={styles.inputSmall}
              value={streamPort}
              onChangeText={setStreamPort}
              placeholder="8080"
              placeholderTextColor={theme.colors.textSubtle}
              keyboardType="number-pad"
            />
          </View>
        </View>

        <TouchableOpacity
          style={[styles.primaryBtn, saved && styles.primaryBtnSaved]}
          onPress={handleSave}
          activeOpacity={0.8}
        >
          <Text style={[styles.primaryBtnText, saved && styles.primaryBtnTextSaved]}>
            {saved ? 'Conexão Atualizada' : 'Salvar e Conectar'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* SEÇÃO 2: GIROSCÓPIO */}
      <View style={styles.group}>
        <Text style={styles.groupTitle}>Sensibilidade do Giroscópio</Text>
        <View style={styles.card}>
          <View style={styles.segmentContainer}>
            {[
              { label: 'Suave', val: 0.16 },
              { label: 'Padrão', val: 0.25 },
              { label: 'Rápido', val: 0.38 },
            ].map((opt) => (
              <TouchableOpacity
                key={opt.label}
                style={[
                  styles.segmentItem,
                  headConfig.emaAlpha === opt.val && styles.segmentItemActive,
                ]}
                onPress={() => onUpdateHeadConfig({ emaAlpha: opt.val })}
                activeOpacity={0.7}
              >
                <Text
                  style={[
                    styles.segmentItemText,
                    headConfig.emaAlpha === opt.val && styles.segmentItemTextActive,
                  ]}
                >
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={[styles.card, { marginTop: 8 }]}>
          <View style={styles.row}>
            <Text style={styles.label}>Inverter Horizontal (Pan)</Text>
            <TouchableOpacity
              style={[styles.toggleBtn, headConfig.invertPan && styles.toggleBtnActive]}
              onPress={() => onUpdateHeadConfig({ invertPan: !headConfig.invertPan })}
              activeOpacity={0.7}
            >
              <Text style={[styles.toggleBtnText, headConfig.invertPan && styles.toggleBtnTextActive]}>
                {headConfig.invertPan ? 'Invertido' : 'Normal'}
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.divider} />

          <View style={styles.row}>
            <Text style={styles.label}>Inverter Vertical (Tilt)</Text>
            <TouchableOpacity
              style={[styles.toggleBtn, headConfig.invertTilt && styles.toggleBtnActive]}
              onPress={() => onUpdateHeadConfig({ invertTilt: !headConfig.invertTilt })}
              activeOpacity={0.7}
            >
              <Text style={[styles.toggleBtnText, headConfig.invertTilt && styles.toggleBtnTextActive]}>
                {headConfig.invertTilt ? 'Invertido' : 'Normal'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* SEÇÃO 3: TESTE MANUAL */}
      <View style={styles.group}>
        <Text style={styles.groupTitle}>Teste Manual da Câmera</Text>
        <View style={styles.card}>
          <View style={styles.servoRow}>
            <Text style={styles.label}>Horizontal (Pan)</Text>
            <View style={styles.servoControls}>
              <TouchableOpacity
                style={styles.adjustBtn}
                onPress={() => onManualServoChange(telemetry.panAngle - 10, telemetry.tiltAngle)}
              >
                <Text style={styles.adjustBtnText}>-10°</Text>
              </TouchableOpacity>
              <Text style={styles.servoAngle}>{Math.round(telemetry.panAngle)}°</Text>
              <TouchableOpacity
                style={styles.adjustBtn}
                onPress={() => onManualServoChange(telemetry.panAngle + 10, telemetry.tiltAngle)}
              >
                <Text style={styles.adjustBtnText}>+10°</Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.divider} />

          <View style={styles.servoRow}>
            <Text style={styles.label}>Vertical (Tilt)</Text>
            <View style={styles.servoControls}>
              <TouchableOpacity
                style={styles.adjustBtn}
                onPress={() => onManualServoChange(telemetry.panAngle, telemetry.tiltAngle - 10)}
              >
                <Text style={styles.adjustBtnText}>-10°</Text>
              </TouchableOpacity>
              <Text style={styles.servoAngle}>{Math.round(telemetry.tiltAngle)}°</Text>
              <TouchableOpacity
                style={styles.adjustBtn}
                onPress={() => onManualServoChange(telemetry.panAngle, telemetry.tiltAngle + 10)}
              >
                <Text style={styles.adjustBtnText}>+10°</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </View>
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
    gap: 20,
    paddingBottom: 90,
  },
  group: {
    gap: 8,
  },
  groupTitle: {
    color: theme.colors.textSubtle,
    fontSize: 12,
    fontWeight: '600',
    paddingLeft: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 14,
    overflow: 'hidden',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  label: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  input: {
    color: '#ffffff',
    fontSize: 14,
    textAlign: 'right',
    flex: 1,
    paddingLeft: 10,
  },
  inputSmall: {
    color: '#ffffff',
    fontSize: 14,
    textAlign: 'right',
    width: 80,
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
    marginLeft: 16,
  },
  primaryBtn: {
    backgroundColor: '#ffffff',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 6,
  },
  primaryBtnSaved: {
    backgroundColor: theme.colors.success,
  },
  primaryBtnText: {
    color: '#000000',
    fontSize: 14,
    fontWeight: '600',
  },
  primaryBtnTextSaved: {
    color: '#000000',
  },
  segmentContainer: {
    flexDirection: 'row',
    padding: 4,
  },
  segmentItem: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
  },
  segmentItemActive: {
    backgroundColor: 'rgba(255, 255, 255, 0.14)',
  },
  segmentItemText: {
    color: theme.colors.textMuted,
    fontSize: 13,
    fontWeight: '500',
  },
  segmentItemTextActive: {
    color: '#ffffff',
    fontWeight: '600',
  },
  servoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  servoControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  adjustBtn: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  adjustBtnText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  servoAngle: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
    minWidth: 38,
    textAlign: 'center',
  },
  toggleBtn: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
  },
  toggleBtnActive: {
    backgroundColor: 'rgba(56, 189, 248, 0.25)',
  },
  toggleBtnText: {
    color: theme.colors.textMuted,
    fontSize: 12,
    fontWeight: '600',
  },
  toggleBtnTextActive: {
    color: '#38bdf8',
  },
});
