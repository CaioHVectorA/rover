import React from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Compass } from 'lucide-react-native';
import { CameraStream } from './CameraStream';
import { theme } from '../theme';

interface DriveScreenProps {
  streamUrl: string;
  panAngle: number;
  tiltAngle: number;
  headTrackingActive: boolean;
  onToggleHeadTracking: () => void;
  onDriveCommand: (cmd: 'F' | 'B' | 'L' | 'R' | 'S') => void;
  activeDirection: string;
}

export const DriveScreen: React.FC<DriveScreenProps> = ({
  streamUrl,
  panAngle,
  tiltAngle,
  headTrackingActive,
  onToggleHeadTracking,
  onDriveCommand,
  activeDirection,
}) => {
  return (
    <View style={styles.container}>
      {/* Imagem da Câmera em Destaque */}
      <View style={styles.cameraBox}>
        <CameraStream
          streamUrl={streamUrl}
          panAngle={panAngle}
          tiltAngle={tiltAngle}
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
            color={headTrackingActive ? '#000000' : 'rgba(255, 255, 255, 0.7)'}
          />
          <Text style={[styles.gyroBtnText, headTrackingActive && styles.gyroBtnTextActive]}>
            Giroscópio
          </Text>
        </TouchableOpacity>
      </View>

      {/* Controles 4WD no Rodapé */}
      <View style={styles.footerControls}>
        <View style={styles.dpad}>
          {/* Frente */}
          <TouchableOpacity
            style={[styles.padBtn, activeDirection === 'F' && styles.padBtnActive]}
            onPressIn={() => onDriveCommand('F')}
            onPressOut={() => onDriveCommand('S')}
            activeOpacity={0.6}
          >
            <ArrowUp size={20} color="#ffffff" />
          </TouchableOpacity>

          {/* Esquerda / Centro / Direita */}
          <View style={styles.dpadMid}>
            <TouchableOpacity
              style={[styles.padBtn, activeDirection === 'L' && styles.padBtnActive]}
              onPressIn={() => onDriveCommand('L')}
              onPressOut={() => onDriveCommand('S')}
              activeOpacity={0.6}
            >
              <ArrowLeft size={20} color="#ffffff" />
            </TouchableOpacity>

            <View style={styles.padCenter} />

            <TouchableOpacity
              style={[styles.padBtn, activeDirection === 'R' && styles.padBtnActive]}
              onPressIn={() => onDriveCommand('R')}
              onPressOut={() => onDriveCommand('S')}
              activeOpacity={0.6}
            >
              <ArrowRight size={20} color="#ffffff" />
            </TouchableOpacity>
          </View>

          {/* Ré */}
          <TouchableOpacity
            style={[styles.padBtn, activeDirection === 'B' && styles.padBtnActive]}
            onPressIn={() => onDriveCommand('B')}
            onPressOut={() => onDriveCommand('S')}
            activeOpacity={0.6}
          >
            <ArrowDown size={20} color="#ffffff" />
          </TouchableOpacity>
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
  },
  gyroBtn: {
    position: 'absolute',
    top: 12,
    right: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
    backgroundColor: 'rgba(0, 0, 0, 0.65)',
    borderRadius: theme.radius.full,
  },
  gyroBtnActive: {
    backgroundColor: '#ffffff',
  },
  gyroBtnText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  gyroBtnTextActive: {
    color: '#000000',
    fontWeight: '700',
  },
  footerControls: {
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dpad: {
    alignItems: 'center',
    gap: 6,
  },
  dpadMid: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  padBtn: {
    width: 60,
    height: 50,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  padBtnActive: {
    backgroundColor: 'rgba(255, 255, 255, 0.25)',
  },
  padCenter: {
    width: 44,
    height: 50,
  },
});
