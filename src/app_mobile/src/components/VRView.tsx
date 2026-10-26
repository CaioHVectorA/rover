import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { CameraStream } from './CameraStream';
import { X } from 'lucide-react-native';
import { OperationMode } from '../types';

interface VRViewProps {
  streamUrl: string;
  operationMode?: OperationMode;
  panAngle: number;
  tiltAngle: number;
  motorLeftPwm?: number;
  motorRightPwm?: number;
  onRecenter: () => void;
  onExitVR: () => void;
}

export const VRView: React.FC<VRViewProps> = ({
  streamUrl,
  operationMode = 'simulation',
  panAngle,
  tiltAngle,
  motorLeftPwm = 0,
  motorRightPwm = 0,
  onRecenter,
  onExitVR,
}) => {
  const [calibrated, setCalibrated] = useState(false);

  const handleRecenter = () => {
    onRecenter();
    setCalibrated(true);
    setTimeout(() => setCalibrated(false), 1200);
  };

  return (
    <View style={styles.container}>
      {/* Olho Esquerdo */}
      <View style={styles.eyeContainer}>
        <CameraStream
          streamUrl={streamUrl}
          operationMode={operationMode}
          isVR={true}
          panAngle={panAngle}
          tiltAngle={tiltAngle}
          motorLeftPwm={motorLeftPwm}
          motorRightPwm={motorRightPwm}
          showHUD={true}
        />
      </View>

      {/* Linha Divisória Estereoscópica */}
      <View style={styles.separator} />

      {/* Olho Direito */}
      <View style={styles.eyeContainer}>
        <CameraStream
          streamUrl={streamUrl}
          operationMode={operationMode}
          isVR={true}
          panAngle={panAngle}
          tiltAngle={tiltAngle}
          motorLeftPwm={motorLeftPwm}
          motorRightPwm={motorRightPwm}
          showHUD={true}
        />
      </View>

      {/* Controles Flutuantes Discretos */}
      <View style={styles.floatingControls}>
        <TouchableOpacity
          style={[styles.recenterBtn, calibrated && styles.recenterBtnActive]}
          onPress={handleRecenter}
          activeOpacity={0.7}
        >
          <Text style={[styles.recenterText, calibrated && styles.recenterTextActive]}>
            {calibrated ? 'Zerado (90°/90°)' : 'Centralizar VR'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.exitBtn} onPress={onExitVR} activeOpacity={0.7}>
          <X size={16} color="#ffffff" />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#000000',
    position: 'relative',
  },
  eyeContainer: {
    flex: 1,
    height: '100%',
    overflow: 'hidden',
  },
  separator: {
    width: 2,
    height: '100%',
    backgroundColor: 'rgba(0, 229, 255, 0.25)',
  },
  floatingControls: {
    position: 'absolute',
    bottom: 20,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
  },
  recenterBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  recenterBtnActive: {
    backgroundColor: '#22c55e',
  },
  recenterText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  recenterTextActive: {
    color: '#000000',
    fontWeight: '700',
  },
  exitBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
});
