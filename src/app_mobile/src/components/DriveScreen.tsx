import React from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import {
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Compass,
  RotateCcw,
  Octagon,
} from 'lucide-react-native';
import { CameraStream } from './CameraStream';
import { OperationMode, RoverTelemetry } from '../types';
import { theme } from '../theme';

interface DriveScreenProps {
  streamUrl: string;
  operationMode: OperationMode;
  telemetry: RoverTelemetry;
  headTrackingActive: boolean;
  onToggleHeadTracking: () => void;
  onDriveCommand: (cmd: 'F' | 'B' | 'L' | 'R' | 'S') => void;
  onManualServoChange: (pan: number, tilt: number) => void;
  onRecenter: () => void;
  onEmergencyStop: () => void;
}

export const DriveScreen: React.FC<DriveScreenProps> = ({
  streamUrl,
  operationMode,
  telemetry,
  headTrackingActive,
  onToggleHeadTracking,
  onDriveCommand,
  onManualServoChange,
  onRecenter,
  onEmergencyStop,
}) => {
  const { panAngle, tiltAngle, direction } = telemetry;

  return (
    <View style={styles.container}>
      {/* Imagem da Câmera / Simulador 3D em Destaque */}
      <View style={styles.cameraBox}>
        <CameraStream
          streamUrl={streamUrl}
          operationMode={operationMode}
          panAngle={panAngle}
          tiltAngle={tiltAngle}
          motorLeftPwm={telemetry.motorLeftPwm}
          motorRightPwm={telemetry.motorRightPwm}
          camSleeping={telemetry.stats?.cam.dormindo ?? false}
          camMode={telemetry.stats?.cam.modo ?? 'ATIVO'}
          chipTemp={telemetry.stats?.sys.temp ?? 44.5}
          vbat={telemetry.batteryVoltage ?? 8.15}
          showHUD={true}
        />

        {/* Toggle do Giroscópio flutuante no canto */}
        <TouchableOpacity
          style={[styles.gyroBtn, headTrackingActive && styles.gyroBtnActive]}
          onPress={onToggleHeadTracking}
          activeOpacity={0.8}
        >
          <Compass
            size={14}
            color={headTrackingActive ? '#000000' : 'rgba(255, 255, 255, 0.85)'}
          />
          <Text style={[styles.gyroBtnText, headTrackingActive && styles.gyroBtnTextActive]}>
            {headTrackingActive ? 'Giroscópio ON' : 'Giroscópio'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Painel Duplo Inferior: Tração 4WD (Esquerda) + Pan/Tilt Manual (Direita) */}
      <View style={styles.footerControls}>
        {/* Bloco 1: D-Pad de Tração 4WD */}
        <View style={styles.controlCluster}>
          <Text style={styles.clusterLabel}>TRAÇÃO 4WD</Text>
          <View style={styles.dpad}>
            <TouchableOpacity
              style={[styles.padBtn, direction === 'F' && styles.padBtnActive]}
              onPressIn={() => onDriveCommand('F')}
              onPressOut={() => onDriveCommand('S')}
              activeOpacity={0.6}
            >
              <ArrowUp size={20} color="#ffffff" />
            </TouchableOpacity>

            <View style={styles.dpadMid}>
              <TouchableOpacity
                style={[styles.padBtn, direction === 'L' && styles.padBtnActive]}
                onPressIn={() => onDriveCommand('L')}
                onPressOut={() => onDriveCommand('S')}
                activeOpacity={0.6}
              >
                <ArrowLeft size={20} color="#ffffff" />
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.padStopCenter}
                onPress={onEmergencyStop}
                activeOpacity={0.7}
              >
                <Octagon size={16} color="#ef4444" />
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.padBtn, direction === 'R' && styles.padBtnActive]}
                onPressIn={() => onDriveCommand('R')}
                onPressOut={() => onDriveCommand('S')}
                activeOpacity={0.6}
              >
                <ArrowRight size={20} color="#ffffff" />
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[styles.padBtn, direction === 'B' && styles.padBtnActive]}
              onPressIn={() => onDriveCommand('B')}
              onPressOut={() => onDriveCommand('S')}
              activeOpacity={0.6}
            >
              <ArrowDown size={20} color="#ffffff" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Bloco 2: Controle Manual Pan/Tilt da Cabeça */}
        <View style={styles.controlCluster}>
          <Text style={styles.clusterLabel}>CABEÇA PAN / TILT</Text>
          <View style={styles.dpad}>
            <TouchableOpacity
              style={styles.padBtnCam}
              onPress={() => onManualServoChange(panAngle, tiltAngle - 12)}
              activeOpacity={0.6}
            >
              <Text style={styles.camDirText}>▲ CIMA</Text>
            </TouchableOpacity>

            <View style={styles.dpadMid}>
              <TouchableOpacity
                style={styles.padBtnCam}
                onPress={() => onManualServoChange(panAngle - 15, tiltAngle)}
                activeOpacity={0.6}
              >
                <Text style={styles.camDirText}>◀ ESQ</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.padCenterCam}
                onPress={onRecenter}
                activeOpacity={0.7}
              >
                <RotateCcw size={14} color="#00e5ff" />
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.padBtnCam}
                onPress={() => onManualServoChange(panAngle + 15, tiltAngle)}
                activeOpacity={0.6}
              >
                <Text style={styles.camDirText}>DIR ▶</Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={styles.padBtnCam}
              onPress={() => onManualServoChange(panAngle, tiltAngle + 12)}
              activeOpacity={0.6}
            >
              <Text style={styles.camDirText}>▼ BAIXO</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
    paddingHorizontal: 12,
    paddingBottom: 74,
  },
  cameraBox: {
    flex: 1,
    backgroundColor: '#0a0a0c',
    borderRadius: 16,
    overflow: 'hidden',
    position: 'relative',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  gyroBtn: {
    position: 'absolute',
    top: 12,
    right: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 11,
    paddingVertical: 6,
    backgroundColor: 'rgba(0, 0, 0, 0.72)',
    borderRadius: theme.radius.full,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  gyroBtnActive: {
    backgroundColor: '#22c55e',
    borderColor: '#22c55e',
  },
  gyroBtnText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '700',
  },
  gyroBtnTextActive: {
    color: '#000000',
    fontWeight: '800',
  },
  footerControls: {
    paddingVertical: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  controlCluster: {
    alignItems: 'center',
    gap: 4,
  },
  clusterLabel: {
    color: '#64748b',
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.8,
  },
  dpad: {
    alignItems: 'center',
    gap: 5,
  },
  dpadMid: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  padBtn: {
    width: 52,
    height: 42,
    backgroundColor: 'rgba(255, 255, 255, 0.09)',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  padBtnActive: {
    backgroundColor: '#22c55e',
    borderColor: '#4ade80',
  },
  padStopCenter: {
    width: 42,
    height: 42,
    borderRadius: 10,
    backgroundColor: 'rgba(239, 68, 68, 0.14)',
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.35)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  padBtnCam: {
    width: 56,
    height: 42,
    backgroundColor: 'rgba(0, 229, 255, 0.08)',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(0, 229, 255, 0.2)',
  },
  padCenterCam: {
    width: 42,
    height: 42,
    borderRadius: 10,
    backgroundColor: 'rgba(0, 229, 255, 0.16)',
    borderWidth: 1,
    borderColor: 'rgba(0, 229, 255, 0.4)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  camDirText: {
    color: '#e2e8f0',
    fontSize: 10,
    fontWeight: '800',
  },
});
