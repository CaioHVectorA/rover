import React, { useState, useEffect } from 'react';
import { View, Image, Text, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Camera, RefreshCw } from 'lucide-react-native';

interface CameraStreamProps {
  streamUrl: string;
  isVR?: boolean;
  panAngle?: number;
  tiltAngle?: number;
  showHUD?: boolean;
}

export const CameraStream: React.FC<CameraStreamProps> = ({
  streamUrl,
  isVR = false,
  panAngle = 90,
  tiltAngle = 90,
  showHUD = true,
}) => {
  const [error, setError] = useState(false);
  const [key, setKey] = useState(Date.now());

  const handleRefresh = () => {
    setError(false);
    setKey(Date.now());
  };

  useEffect(() => {
    setError(false);
    setKey(Date.now());
  }, [streamUrl]);

  return (
    <View style={[styles.container, isVR && styles.vrContainer]}>
      {error ? (
        <View style={styles.errorContainer}>
          <Camera size={32} color="#64748b" />
          <Text style={styles.errorText}>Stream indisponível</Text>
          <Text style={styles.errorSubtext}>{streamUrl}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={handleRefresh}>
            <RefreshCw size={14} color="#0f172a" />
            <Text style={styles.retryText}>Reconectar</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <Image
          key={key}
          source={{ uri: `${streamUrl}?t=${key}` }}
          style={styles.image}
          resizeMode="cover"
          onError={() => setError(true)}
        />
      )}

      {/* HUD de Mira e Ângulos */}
      {showHUD && (
        <View style={styles.hudOverlay} pointerEvents="none">
          {/* Mira central */}
          <View style={styles.crosshairCenter}>
            <View style={styles.crosshairH} />
            <View style={styles.crosshairV} />
            <View style={styles.crosshairDot} />
          </View>

          {/* Indicadores angulares no canto */}
          <View style={styles.anglesHUD}>
            <Text style={styles.hudText}>PAN: {Math.round(panAngle)}°</Text>
            <Text style={styles.hudText}>TILT: {Math.round(tiltAngle)}°</Text>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    position: 'relative',
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  vrContainer: {
    borderRadius: 0,
    borderWidth: 0,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  errorContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    gap: 8,
  },
  errorText: {
    color: '#94a3b8',
    fontSize: 14,
    fontWeight: '700',
  },
  errorSubtext: {
    color: '#475569',
    fontSize: 11,
    textAlign: 'center',
    fontFamily: 'monospace',
  },
  retryBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#38bdf8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    marginTop: 4,
  },
  retryText: {
    color: '#0f172a',
    fontSize: 12,
    fontWeight: '700',
  },
  hudOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  crosshairCenter: {
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  crosshairH: {
    position: 'absolute',
    width: 28,
    height: 1,
    backgroundColor: 'rgba(0, 229, 255, 0.5)',
  },
  crosshairV: {
    position: 'absolute',
    height: 28,
    width: 1,
    backgroundColor: 'rgba(0, 229, 255, 0.5)',
  },
  crosshairDot: {
    width: 3,
    height: 3,
    borderRadius: 1.5,
    backgroundColor: '#00e5ff',
  },
  anglesHUD: {
    position: 'absolute',
    bottom: 8,
    left: 8,
    backgroundColor: 'rgba(7, 8, 11, 0.75)',
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 3,
    borderWidth: 1,
    borderColor: 'rgba(0, 229, 255, 0.25)',
  },
  hudText: {
    color: '#00e5ff',
    fontSize: 9,
    fontWeight: '800',
    fontFamily: 'monospace',
    letterSpacing: 0.5,
  },
});
