import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, View, StatusBar } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as ScreenOrientation from 'expo-screen-orientation';
import {
  AppTab,
  ConnectionConfig,
  HeadTrackingConfig,
  OperationMode,
  RoverTelemetry,
} from './src/types';
import { roverWS } from './src/services/websocket';
import { headTracking } from './src/services/sensors';
import { TopStatusBar } from './src/components/TopStatusBar';
import { FloatingNavBar } from './src/components/FloatingNavBar';
import { DriveScreen } from './src/components/DriveScreen';
import { PocsScreen } from './src/components/PocsScreen';
import { CalibrateScreen } from './src/components/CalibrateScreen';
import { VRView } from './src/components/VRView';
import { SettingsScreen } from './src/components/SettingsScreen';
import { theme } from './src/theme';

const STORAGE_KEY_CONFIG = '@rover_config_e2e_v2';

const DEFAULT_CONFIG: ConnectionConfig = {
  mode: 'esp32',
  protocol: 'hybrid',
  ip: '192.168.137.72',
  wsPort: 81,
  streamPort: 82,
  streamPath: '/stream',
  mockServerIp: '192.168.7.60',
  mockWsPort: 8082,
  mockHttpPort: 8080,
};

function MainApp() {
  const [currentTab, setCurrentTab] = useState<AppTab>('drive');
  const [connectionConfig, setConnectionConfig] = useState<ConnectionConfig>(DEFAULT_CONFIG);

  const [telemetry, setTelemetry] = useState<RoverTelemetry>({
    connected: true,
    operationMode: 'simulation',
    pingMs: 12,
    batteryVoltage: 8.15,
    batteryMinVoltage: 8.15,
    batteryPercent: 92,
    panAngle: 90,
    tiltAngle: 90,
    targetPanAngle: 90,
    targetTiltAngle: 90,
    speed: 0,
    motorLeftPwm: 0,
    motorRightPwm: 0,
    direction: 'STOP',
    poc5AutoRunning: false,
  });

  const [headConfig, setHeadConfig] = useState<HeadTrackingConfig>(headTracking.getConfig());

  const applyConnection = useCallback((cfg: ConnectionConfig) => {
    setTelemetry((prev) => ({ ...prev, operationMode: cfg.mode }));
    if (cfg.mode === 'simulation') {
      roverWS.configure('simulation', cfg.mockServerIp || '192.168.7.60', cfg.mockWsPort || 8082, cfg.mockHttpPort || 8080, 'hybrid');
    } else {
      roverWS.configure('esp32', cfg.ip, cfg.wsPort, cfg.streamPort === 82 ? 80 : cfg.streamPort, cfg.protocol);
    }
  }, []);

  // Carregar configurações salvas (iniciando por padrão em Simulação E2E)
  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem(STORAGE_KEY_CONFIG);
        if (saved) {
          const parsed: ConnectionConfig = { ...DEFAULT_CONFIG, ...JSON.parse(saved) };
          setConnectionConfig(parsed);
          applyConnection(parsed);
        } else {
          applyConnection(DEFAULT_CONFIG);
        }
      } catch {
        applyConnection(DEFAULT_CONFIG);
      }
    })();
  }, [applyConnection]);

  // Monitorar WebSocket e Simulador
  useEffect(() => {
    roverWS.onStatus((connected, pingMs) => {
      setTelemetry((prev) => ({ ...prev, connected, pingMs }));
    });

    roverWS.onMessage((data) => {
      if (data.type === 'telemetry') {
        setTelemetry((prev) => ({
          ...prev,
          batteryVoltage: data.vbat ?? prev.batteryVoltage,
          batteryMinVoltage: data.vmin ?? prev.batteryMinVoltage,
          batteryPercent: data.pct ?? prev.batteryPercent,
          panAngle: data.pan !== undefined ? data.pan : prev.panAngle,
          tiltAngle: data.tilt !== undefined ? data.tilt : prev.tiltAngle,
          motorLeftPwm: data.motL !== undefined ? data.motL : prev.motorLeftPwm,
          motorRightPwm: data.motR !== undefined ? data.motR : prev.motorRightPwm,
          poc5AutoRunning: data.poc5AutoRunning ?? prev.poc5AutoRunning,
          stats: data.stats ?? prev.stats,
          lastResponse: JSON.stringify(data),
        }));
      }
    });

    return () => {
      roverWS.disconnect();
    };
  }, []);

  // Controle de orientação de tela no Modo VR
  useEffect(() => {
    async function handleOrientation() {
      try {
        if (currentTab === 'vr') {
          await ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE_RIGHT);
        } else {
          await ScreenOrientation.unlockAsync();
        }
      } catch {}
    }
    handleOrientation();
  }, [currentTab]);

  // Listener do Giroscópio (Head-Tracking)
  const handleHeadMotion = useCallback((pan: number, tilt: number) => {
    setTelemetry((prev) => ({ ...prev, panAngle: pan, tiltAngle: tilt, targetPanAngle: pan, targetTiltAngle: tilt }));
    roverWS.sendServoPanTilt(pan, tilt);
  }, []);

  useEffect(() => {
    if (headConfig.enabled && (currentTab === 'vr' || currentTab === 'drive' || currentTab === 'calibrate')) {
      headTracking.start(handleHeadMotion);
    } else {
      headTracking.stop();
    }
    return () => {
      headTracking.stop();
    };
  }, [headConfig.enabled, currentTab, handleHeadMotion]);

  const handleRecenter = () => {
    headTracking.recenter();
    setTelemetry((prev) => ({ ...prev, panAngle: 90, tiltAngle: 90, targetPanAngle: 90, targetTiltAngle: 90 }));
    roverWS.sendServoPanTilt(90, 90);
  };

  const handleManualServoChange = (pan: number, tilt: number, speedDegS: number = 0) => {
    const clampedPan = Math.max(0, Math.min(180, Math.round(pan)));
    const clampedTilt = Math.max(0, Math.min(180, Math.round(tilt)));
    setTelemetry((prev) => ({
      ...prev,
      panAngle: clampedPan,
      tiltAngle: clampedTilt,
      targetPanAngle: clampedPan,
      targetTiltAngle: clampedTilt,
    }));
    roverWS.sendServoPanTilt(clampedPan, clampedTilt, speedDegS);
  };

  const handleDriveCommand = (cmd: 'F' | 'B' | 'L' | 'R' | 'S', speed: number = 210) => {
    roverWS.sendDrive(cmd, speed);
    setTelemetry((prev) => ({ ...prev, direction: cmd }));
  };

  const handleEmergencyStop = () => {
    roverWS.emergencyStop();
    setTelemetry((prev) => ({
      ...prev,
      direction: 'S',
      motorLeftPwm: 0,
      motorRightPwm: 0,
      poc5AutoRunning: false,
    }));
  };

  const handleSaveConnection = async (newConfig: ConnectionConfig) => {
    setConnectionConfig(newConfig);
    await AsyncStorage.setItem(STORAGE_KEY_CONFIG, JSON.stringify(newConfig));
    applyConnection(newConfig);
  };

  const handleToggleMode = async (nextMode: OperationMode) => {
    const updated: ConnectionConfig = { ...connectionConfig, mode: nextMode };
    setConnectionConfig(updated);
    await AsyncStorage.setItem(STORAGE_KEY_CONFIG, JSON.stringify(updated));
    applyConnection(updated);
  };

  const handleReconnect = () => {
    applyConnection(connectionConfig);
  };

  const streamUrl =
    connectionConfig.mode === 'simulation'
      ? `http://${connectionConfig.mockServerIp}:${connectionConfig.mockHttpPort}/view`
      : `http://${connectionConfig.ip}:${connectionConfig.streamPort}${connectionConfig.streamPath}`;

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />

      {/* Barra de Status no Topo (com Switch Simulação / ESP32) */}
      {currentTab !== 'vr' && (
        <TopStatusBar
          telemetry={telemetry}
          onRecenter={handleRecenter}
          onReconnect={handleReconnect}
          onToggleMode={handleToggleMode}
        />
      )}

      {/* Aba 1: Pilotar / Câmera 3D */}
      {currentTab === 'drive' && (
        <DriveScreen
          streamUrl={streamUrl}
          operationMode={connectionConfig.mode}
          telemetry={telemetry}
          headTrackingActive={headConfig.enabled}
          onToggleHeadTracking={() => {
            const next = !headConfig.enabled;
            setHeadConfig((prev) => ({ ...prev, enabled: next }));
            headTracking.updateConfig({ enabled: next });
          }}
          onDriveCommand={handleDriveCommand}
          onManualServoChange={handleManualServoChange}
          onRecenter={handleRecenter}
          onEmergencyStop={handleEmergencyStop}
        />
      )}

      {/* Aba 2: Suíte de 6 POCs E2E */}
      {currentTab === 'pocs' && (
        <PocsScreen
          telemetry={telemetry}
          onServoChange={handleManualServoChange}
          onDriveCommand={handleDriveCommand}
          onEmergencyStop={handleEmergencyStop}
        />
      )}

      {/* Aba 3: Calibração Fina dos Servos SG90 */}
      {currentTab === 'calibrate' && (
        <CalibrateScreen
          telemetry={telemetry}
          onServoChange={handleManualServoChange}
          onRecenter={handleRecenter}
          headConfig={headConfig}
          onUpdateHeadConfig={(cfg) => {
            setHeadConfig((prev) => ({ ...prev, ...cfg }));
            headTracking.updateConfig(cfg);
          }}
        />
      )}

      {/* Aba 4: Modo Estereoscópico VR */}
      {currentTab === 'vr' && (
        <VRView
          streamUrl={streamUrl}
          operationMode={connectionConfig.mode}
          panAngle={telemetry.panAngle}
          tiltAngle={telemetry.tiltAngle}
          motorLeftPwm={telemetry.motorLeftPwm}
          motorRightPwm={telemetry.motorRightPwm}
          onRecenter={handleRecenter}
          onExitVR={() => setCurrentTab('drive')}
        />
      )}

      {/* Aba 5: Rede, Modos & Giroscópio */}
      {currentTab === 'settings' && (
        <SettingsScreen
          connectionConfig={connectionConfig}
          onSaveConnection={handleSaveConnection}
          telemetry={telemetry}
          headConfig={headConfig}
          onUpdateHeadConfig={(cfg) => {
            setHeadConfig((prev) => ({ ...prev, ...cfg }));
            headTracking.updateConfig(cfg);
          }}
          onManualServoChange={handleManualServoChange}
          onRecenter={handleRecenter}
          onDriveCommand={handleDriveCommand}
        />
      )}

      {/* Dock Flutuante Inferior */}
      {currentTab !== 'vr' && (
        <FloatingNavBar currentTab={currentTab} onSelectTab={setCurrentTab} />
      )}
    </View>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <MainApp />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.bg,
  },
});
