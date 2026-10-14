import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { WebView } from 'react-native-webview';
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
  const [reloadKey, setReloadKey] = useState(0);
  const [hasError, setHasError] = useState(false);

  // Converte /stream ou /capture para a página nativa otimizada /view do ESP32
  const viewUrl = streamUrl
    .replace(/\/capture\/?$/, '/view')
    .replace(/\/stream\/?$/, '/view');

  const handleRefresh = () => {
    setHasError(false);
    setReloadKey((prev) => prev + 1);
  };

  return (
    <View style={[styles.container, isVR && styles.vrContainer]}>
      {hasError ? (
        <View style={styles.errorContainer}>
          <Camera size={36} color="#64748b" />
          <Text style={styles.errorText}>Vídeo Indisponível</Text>
          <Text style={styles.errorSubtext}>{viewUrl}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={handleRefresh}>
            <RefreshCw size={14} color="#0f172a" />
            <Text style={styles.retryText}>Reconectar</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.streamWrapper}>
          <WebView
            key={reloadKey}
            source={{ uri: viewUrl }}
            originWhitelist={['*']}
            mixedContentMode="always"
            style={styles.webview}
            scrollEnabled={false}
            bounces={false}
            allowsInlineMediaPlayback={true}
            mediaPlaybackRequiresUserAction={false}
            androidHardwareAccelerationDisabled={false}
            androidLayerType="hardware"
            onError={() => setHasError(true)}
          />
        </View>
      )}

      {/* HUD de Mira e Ângulos */}
      {showHUD && (
        <View style={styles.hudOverlay} pointerEvents="none">
          <View style={styles.crosshairCenter}>
            <View style={styles.crosshairH} />
            <View style={styles.crosshairV} />
            <View style={styles.crosshairDot} />
          </View>

          <View style={styles.anglesHUD}>
            <Text style={styles.hudText}>PAN: {Math.round(panAngle)}°</Text>
            <Text style={styles.hudText}>TILT: {Math.round(tiltAngle)}°</Text>
            <Text style={[styles.hudText, { color: '#4ade80' }]}>FPV 30 FPS</Text>
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
  streamWrapper: {
    width: '100%',
    height: '100%',
    backgroundColor: '#000000',
    position: 'relative',
  },
  webview: {
    flex: 1,
    backgroundColor: '#000000',
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
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#00e5ff',
  },
  anglesHUD: {
    position: 'absolute',
    bottom: 12,
    left: 12,
    backgroundColor: 'rgba(0, 0, 0, 0.65)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    gap: 2,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  hudText: {
    color: '#38bdf8',
    fontSize: 10,
    fontWeight: '700',
    fontFamily: 'monospace',
  },
});
