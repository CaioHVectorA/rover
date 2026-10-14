import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { CameraStream } from './CameraStream';
import { X } from 'lucide-react-native';

interface VRViewProps {
  streamUrl: string;
  panAngle: number;
  tiltAngle: number;
  onRecenter: () => void;
  onExitVR: () => void;
}

export const VRView: React.FC<VRViewProps> = ({
  streamUrl,
  panAngle,
  tiltAngle,
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
          isVR={true}
          panAngle={panAngle}
          tiltAngle={tiltAngle}
          showHUD={true}
        />
      </View>

      {/* Linha Divisória */}
      <View style={styles.separator} />

      {/* Olho Direito */}
      <View style={styles.eyeContainer}>
        <CameraStream
          streamUrl={streamUrl}
          isVR={true}
          panAngle={panAngle}
          tiltAngle={tiltAngle}
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
            {calibrated ? 'Zerado' : 'Centralizar'}
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
    width: 1,
    height: '100%',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
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
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  recenterBtnActive: {
    backgroundColor: '#ffffff',
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
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
});
