import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, View, StatusBar } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as ScreenOrientation from 'expo-screen-orientation';
import { AppTab, ConnectionConfig, HeadTrackingConfig, RoverTelemetry } from './src/types';
import { roverWS } from './src/services/websocket';
import { headTracking } from './src/services/sensors';
import { TopStatusBar } from './src/components/TopStatusBar';
import { FloatingNavBar } from './src/components/FloatingNavBar';
import { DriveScreen } from './src/components/DriveScreen';
import { VRView } from './src/components/VRView';
import { SettingsScreen } from './src/components/SettingsScreen';
import { theme } from './src/theme';

const STORAGE_KEY_CONFIG = '@rover_config_v2';

function MainApp() {
  const [currentTab, setCurrentTab] = useState<AppTab>('drive');

  const [connectionConfig, setConnectionConfig] = useState<ConnectionConfig>({
    ip: '192.168.4.1',
    wsPort: 81,
    streamPort: 80,
    streamPath: '/stream',
  });

  const [telemetry, setTelemetry] = useState<RoverTelemetry>({
    connected: false,
    pingMs: 0,
    panAngle: 90,
    tiltAngle: 90,
    speed: 0,
    direction: 'STOP',
  });

  const [headConfig, setHeadConfig] = useState<HeadTrackingConfig>(headTracking.getConfig());

  // Carregar configurações de conexão do armazenamento local
  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem(STORAGE_KEY_CONFIG);
        if (saved) {
          const parsed = JSON.parse(saved);
          setConnectionConfig(parsed);
          roverWS.connect(parsed.ip, parsed.wsPort);
        } else {
          roverWS.connect(connectionConfig.ip, connectionConfig.wsPort);
        }
      } catch {
        roverWS.connect(connectionConfig.ip, connectionConfig.wsPort);
      }
    })();
  }, []);

  // Monitorar conexão WebSocket
  useEffect(() => {
    roverWS.onStatus((connected, pingMs) => {
      setTelemetry((prev) => ({ ...prev, connected, pingMs }));
    });

    roverWS.onMessage((data) => {
      if (data.type === 'telemetry') {
        setTelemetry((prev) => ({
          ...prev,
          batteryVoltage: data.vbat ?? prev.batteryVoltage,
          batteryPercent: data.pct ?? prev.batteryPercent,
          lastResponse: JSON.stringify(data),
        }));
      }
    });

    return () => {
      roverWS.disconnect();
    };
  }, []);

  // Controle de orientação de tela
  useEffect(() => {
    async function handleOrientation() {
      if (currentTab === 'vr') {
        await ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE_RIGHT);
      } else {
        await ScreenOrientation.unlockAsync();
      }
    }
    handleOrientation();
  }, [currentTab]);

  // Listener do Giroscópio
  const handleHeadMotion = useCallback((pan: number, tilt: number) => {
    setTelemetry((prev) => ({ ...prev, panAngle: pan, tiltAngle: tilt }));
    roverWS.sendServoPanTilt(pan, tilt);
  }, []);

  // Iniciar/Parar Giroscópio
  useEffect(() => {
    if (headConfig.enabled && (currentTab === 'vr' || currentTab === 'drive')) {
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
    setTelemetry((prev) => ({ ...prev, panAngle: 90, tiltAngle: 90 }));
    roverWS.sendServoPanTilt(90, 90);
  };

  const handleManualServoChange = (pan: number, tilt: number) => {
    const clampedPan = Math.max(headConfig.panMin, Math.min(headConfig.panMax, pan));
    const clampedTilt = Math.max(headConfig.tiltMin, Math.min(headConfig.tiltMax, tilt));
    setTelemetry((prev) => ({ ...prev, panAngle: clampedPan, tiltAngle: clampedTilt }));
    roverWS.sendServoPanTilt(clampedPan, clampedTilt);
  };

  const handleDriveCommand = (cmd: 'F' | 'B' | 'L' | 'R' | 'S') => {
    roverWS.sendDrive(cmd, 220);
    setTelemetry((prev) => ({ ...prev, direction: cmd }));
  };

  const handleSaveConnection = async (newConfig: ConnectionConfig) => {
    setConnectionConfig(newConfig);
    await AsyncStorage.setItem(STORAGE_KEY_CONFIG, JSON.stringify(newConfig));
    roverWS.connect(newConfig.ip, newConfig.wsPort);
  };

  const handleReconnect = () => {
    roverWS.connect(connectionConfig.ip, connectionConfig.wsPort);
  };

  const streamUrl = `http://${connectionConfig.ip}:${connectionConfig.streamPort}${connectionConfig.streamPath}`;

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#09090b" translucent={false} />

      {/* Barra de Status no Topo (oculta no modo VR para não quebrar a visão estéreo) */}
      {currentTab !== 'vr' && (
        <TopStatusBar
          telemetry={telemetry}
          onRecenter={handleRecenter}
          onReconnect={handleReconnect}
        />
      )}

      {/* Conteúdo da Aba */}
      {currentTab === 'drive' && (
        <DriveScreen
          streamUrl={streamUrl}
          panAngle={telemetry.panAngle}
          tiltAngle={telemetry.tiltAngle}
          headTrackingActive={headConfig.enabled}
          onToggleHeadTracking={() => {
            const next = !headConfig.enabled;
            setHeadConfig((prev) => ({ ...prev, enabled: next }));
            headTracking.updateConfig({ enabled: next });
          }}
          onDriveCommand={handleDriveCommand}
          activeDirection={telemetry.direction}
        />
      )}

      {currentTab === 'vr' && (
        <VRView
          streamUrl={streamUrl}
          panAngle={telemetry.panAngle}
          tiltAngle={telemetry.tiltAngle}
          onRecenter={handleRecenter}
          onExitVR={() => setCurrentTab('drive')}
        />
      )}

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

      {/* Dock Flutuante de Navegação Inferior (oculta no modo VR) */}
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
