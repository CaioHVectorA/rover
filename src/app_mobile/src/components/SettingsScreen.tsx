import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  ConnectionConfig,
  FirmwareProtocol,
  HeadTrackingConfig,
  OperationMode,
  RoverTelemetry,
} from '../types';
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
  const [mode, setMode] = useState<OperationMode>(connectionConfig.mode);
  const [protocol, setProtocol] = useState<FirmwareProtocol>(connectionConfig.protocol);
  const [ip, setIp] = useState(connectionConfig.ip);
  const [wsPort, setWsPort] = useState(String(connectionConfig.wsPort));
  const [streamPort, setStreamPort] = useState(String(connectionConfig.streamPort));
  const [streamPath, setStreamPath] = useState(connectionConfig.streamPath);
  const [mockIp, setMockIp] = useState(connectionConfig.mockServerIp || '192.168.7.60');
  const [saved, setSaved] = useState(false);
  const [selectedResolution, setSelectedResolution] = useState<'hqvga' | 'qvga' | 'vga'>('qvga');

  useEffect(() => {
    setMode(connectionConfig.mode);
    setProtocol(connectionConfig.protocol);
    setIp(connectionConfig.ip);
    setWsPort(String(connectionConfig.wsPort));
    setStreamPort(String(connectionConfig.streamPort));
    setStreamPath(connectionConfig.streamPath);
    if (connectionConfig.mockServerIp) setMockIp(connectionConfig.mockServerIp);
  }, [connectionConfig]);

  useEffect(() => {
    AsyncStorage.getItem('@rover_camera_res').then((val) => {
      if (val === 'hqvga' || val === 'qvga' || val === 'vga') {
        setSelectedResolution(val);
      }
    });
  }, []);

  const applyPresetProfile = (preset: 'sim' | 'poc_ap' | 'esp_lan') => {
    if (preset === 'sim') {
      const cfg: ConnectionConfig = {
        ...connectionConfig,
        mode: 'simulation',
        protocol: 'hybrid',
        mockServerIp: mockIp.trim() || '192.168.7.60',
        mockWsPort: 8082,
        mockHttpPort: 8080,
      };
      onSaveConnection(cfg);
      setSaved(true);
      setTimeout(() => setSaved(false), 1800);
    } else if (preset === 'poc_ap') {
      const cfg: ConnectionConfig = {
        ...connectionConfig,
        mode: 'esp32',
        protocol: 'poc_ascii',
        ip: '192.168.4.1',
        wsPort: 81,
        streamPort: 82,
        streamPath: '/stream',
      };
      onSaveConnection(cfg);
      setSaved(true);
      setTimeout(() => setSaved(false), 1800);
    } else {
      const cfg: ConnectionConfig = {
        ...connectionConfig,
        mode: 'esp32',
        protocol: 'hybrid',
        ip: ip.trim() === '192.168.4.1' ? '192.168.7.25' : ip.trim(),
        wsPort: 81,
        streamPort: 80,
        streamPath: '/view',
      };
      onSaveConnection(cfg);
      setSaved(true);
      setTimeout(() => setSaved(false), 1800);
    }
  };

  const handleSelectResolution = async (res: 'hqvga' | 'qvga' | 'vga') => {
    setSelectedResolution(res);
    await AsyncStorage.setItem('@rover_camera_res', res);
    const targetHost = mode === 'simulation' ? mockIp : ip;
    const targetPort = mode === 'simulation' ? 8080 : streamPort;
    try {
      fetch(`http://${targetHost}:${targetPort}/resolution?val=${res}`);
    } catch {}
  };

  const handleSave = () => {
    onSaveConnection({
      mode,
      protocol,
      ip: ip.trim(),
      wsPort: parseInt(wsPort, 10) || 81,
      streamPort: parseInt(streamPort, 10) || 80,
      streamPath: streamPath.trim() || '/view',
      mockServerIp: mockIp.trim() || '192.168.7.60',
      mockWsPort: 8082,
      mockHttpPort: 8080,
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
      {/* SEÇÃO 0: PERFIS RÁPIDOS DE 1 TOQUE (SIMULAÇÃO vs ESP32) */}
      <View style={styles.group}>
        <Text style={styles.groupTitle}>Modo de Operação (Troca Rápida E2E)</Text>
        <View style={styles.presetsGrid}>
          <TouchableOpacity
            style={[
              styles.presetCard,
              mode === 'simulation' && styles.presetCardActiveSim,
            ]}
            onPress={() => applyPresetProfile('sim')}
            activeOpacity={0.8}
          >
            <Text style={styles.presetCardTitle}>🧪 Simulação E2E (Sem ESP)</Text>
            <Text style={styles.presetCardDesc}>
              Física 50 Hz + Câmera 3D 60 FPS no celular + Sincronia com PC ({mockIp}:8080)
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.presetCard,
              mode === 'esp32' && ip === '192.168.4.1' && styles.presetCardActiveEsp,
            ]}
            onPress={() => applyPresetProfile('poc_ap')}
            activeOpacity={0.8}
          >
            <Text style={styles.presetCardTitle}>🤖 ESP32 · Wi-Fi Direto POCs (1 a 6)</Text>
            <Text style={styles.presetCardDesc}>
              Rede AP Rover-POCx · IP 192.168.4.1 · WS :81 · Stream :82/stream
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.presetCard,
              mode === 'esp32' && ip !== '192.168.4.1' && styles.presetCardActiveEsp,
            ]}
            onPress={() => applyPresetProfile('esp_lan')}
            activeOpacity={0.8}
          >
            <Text style={styles.presetCardTitle}>🚀 ESP32 · Gateway / Rede Local</Text>
            <Text style={styles.presetCardDesc}>
              IP {ip} · WS :81 · Vídeo :80/view · Protocolo Híbrido (JSON + ASCII)
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* SEÇÃO 1: CONFIGURAÇÃO DETALHADA DE REDE */}
      <View style={styles.group}>
        <Text style={styles.groupTitle}>Parâmetros de Rede ({mode === 'simulation' ? 'Simulador' : 'ESP32 Real'})</Text>
        <View style={styles.card}>
          {mode === 'simulation' ? (
            <View style={styles.row}>
              <Text style={styles.label}>IP do PC (Mock Server 3D)</Text>
              <TextInput
                style={styles.input}
                value={mockIp}
                onChangeText={setMockIp}
                placeholder="192.168.7.60"
                placeholderTextColor={theme.colors.textSubtle}
                autoCapitalize="none"
              />
            </View>
          ) : (
            <>
              <View style={styles.row}>
                <Text style={styles.label}>Endereço IP do ESP32</Text>
                <TextInput
                  style={styles.input}
                  value={ip}
                  onChangeText={setIp}
                  placeholder="192.168.7.25"
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
                  placeholder="81"
                  placeholderTextColor={theme.colors.textSubtle}
                  keyboardType="number-pad"
                />
              </View>

              <View style={styles.divider} />

              <View style={styles.row}>
                <Text style={styles.label}>Porta de Vídeo (80 ou 82)</Text>
                <TextInput
                  style={styles.inputSmall}
                  value={streamPort}
                  onChangeText={setStreamPort}
                  placeholder="80"
                  placeholderTextColor={theme.colors.textSubtle}
                  keyboardType="number-pad"
                />
              </View>

              <View style={styles.divider} />

              <View style={styles.row}>
                <Text style={styles.label}>Caminho do Stream</Text>
                <TextInput
                  style={styles.inputSmall}
                  value={streamPath}
                  onChangeText={setStreamPath}
                  placeholder="/view"
                  placeholderTextColor={theme.colors.textSubtle}
                  autoCapitalize="none"
                />
              </View>
            </>
          )}
        </View>

        <TouchableOpacity
          style={[styles.primaryBtn, saved && styles.primaryBtnSaved]}
          onPress={handleSave}
          activeOpacity={0.8}
        >
          <Text style={[styles.primaryBtnText, saved && styles.primaryBtnTextSaved]}>
            {saved ? 'Configuração Aplicada!' : 'Salvar e Reconectar'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* SEÇÃO 2: RESOLUÇÃO DA CÂMERA */}
      <View style={styles.group}>
        <Text style={styles.groupTitle}>Resolução da Câmera FPV</Text>
        <View style={styles.card}>
          <View style={styles.segmentContainer}>
            {[
              { label: 'HQVGA (240p)', val: 'hqvga' as const },
              { label: 'QVGA (320p)', val: 'qvga' as const },
              { label: 'VGA (480p)', val: 'vga' as const },
            ].map((opt) => (
              <TouchableOpacity
                key={opt.val}
                style={[
                  styles.segmentItem,
                  selectedResolution === opt.val && styles.segmentItemActive,
                ]}
                onPress={() => handleSelectResolution(opt.val)}
                activeOpacity={0.7}
              >
                <Text
                  style={[
                    styles.segmentItemText,
                    selectedResolution === opt.val && styles.segmentItemTextActive,
                  ]}
                >
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={[styles.subLabel, { marginTop: 10, paddingBottom: 10, textAlign: 'center' }]}>
            {selectedResolution === 'hqvga' && '240 × 176 px · 30 FPS · Ultra fluido (menor latência)'}
            {selectedResolution === 'qvga' && '320 × 240 px · 25 FPS · Equilíbrio ideal entre nitidez e fluidez'}
            {selectedResolution === 'vga' && '640 × 480 px · 15 FPS · Alta definição (maior nitidez)'}
          </Text>
        </View>
      </View>

      {/* SEÇÃO 3: GIROSCÓPIO */}
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

      {/* SEÇÃO 4: TESTE MANUAL */}
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
    paddingBottom: 95,
  },
  group: {
    gap: 8,
  },
  groupTitle: {
    color: theme.colors.textSubtle,
    fontSize: 12,
    fontWeight: '700',
    paddingLeft: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  presetsGrid: {
    gap: 8,
  },
  presetCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
    gap: 4,
  },
  presetCardActiveSim: {
    backgroundColor: 'rgba(0, 229, 255, 0.12)',
    borderColor: '#00e5ff',
  },
  presetCardActiveEsp: {
    backgroundColor: 'rgba(34, 197, 94, 0.12)',
    borderColor: '#22c55e',
  },
  presetCardTitle: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '800',
  },
  presetCardDesc: {
    color: '#94a3b8',
    fontSize: 11,
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
    width: 90,
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
    fontWeight: '700',
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
  subLabel: {
    color: theme.colors.textSubtle,
    fontSize: 12,
  },
});
