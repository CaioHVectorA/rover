import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  SlidersHorizontal,
  RotateCcw,
  Crosshair,
  Check,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ShieldAlert,
  Save,
} from 'lucide-react-native';
import { RoverTelemetry, HeadTrackingConfig } from '../types';
import { theme } from '../theme';
import { GyroscopeTestCard } from './GyroscopeTestCard';

interface CalibrateScreenProps {
  telemetry: RoverTelemetry;
  onServoChange: (pan: number, tilt: number) => void;
  onRecenter: () => void;
  headConfig?: HeadTrackingConfig;
  onUpdateHeadConfig?: (config: Partial<HeadTrackingConfig>) => void;
}

const STORAGE_KEY_SERVO_TRIM = '@rover_servo_trim_v1';

export const CalibrateScreen: React.FC<CalibrateScreenProps> = ({
  telemetry,
  onServoChange,
  onRecenter,
  headConfig,
  onUpdateHeadConfig,
}) => {
  const [panAngle, setPanAngle] = useState(telemetry.panAngle || 90);
  const [tiltAngle, setTiltAngle] = useState(telemetry.tiltAngle || 90);

  // Calibração / Trim de deslocamento mecânico (offset)
  const [panTrim, setPanTrim] = useState(0);
  const [tiltTrim, setTiltTrim] = useState(0);
  const [trimSaved, setTrimSaved] = useState(false);

  // Carrega trim salvo
  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem(STORAGE_KEY_SERVO_TRIM);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (typeof parsed.panTrim === 'number') setPanTrim(parsed.panTrim);
          if (typeof parsed.tiltTrim === 'number') setTiltTrim(parsed.tiltTrim);
        }
      } catch {}
    })();
  }, []);

  // Mantém sincronizado com a telemetria caso mude externamente
  useEffect(() => {
    if (telemetry.panAngle !== undefined) setPanAngle(telemetry.panAngle);
    if (telemetry.tiltAngle !== undefined) setTiltAngle(telemetry.tiltAngle);
  }, [telemetry.panAngle, telemetry.tiltAngle]);

  const aplicarMovimento = useCallback(
    (novoPan: number, novoTilt: number) => {
      const p = Math.max(0, Math.min(180, Math.round(novoPan)));
      const t = Math.max(0, Math.min(180, Math.round(novoTilt)));
      setPanAngle(p);
      setTiltAngle(t);
      // Envia a posição efetiva compensada pelo trim
      onServoChange(p + panTrim, t + tiltTrim);
    },
    [onServoChange, panTrim, tiltTrim]
  );

  const salvarTrim = async () => {
    try {
      await AsyncStorage.setItem(
        STORAGE_KEY_SERVO_TRIM,
        JSON.stringify({ panTrim, tiltTrim })
      );
      setTrimSaved(true);
      setTimeout(() => setTrimSaved(false), 2000);
    } catch {}
  };

  const zerarTrim = async () => {
    setPanTrim(0);
    setTiltTrim(0);
    try {
      await AsyncStorage.removeItem(STORAGE_KEY_SERVO_TRIM);
    } catch {}
    aplicarMovimento(90, 90);
  };

  // Coordenadas calculadas para o indicador visual da mira (Crosshair)
  // Pan varia de 0 (esquerda) a 180 (direita). Centro = 90.
  // Tilt varia de 0 (baixo) a 180 (cima). Centro = 90.
  const crosshairSize = 160;
  const dotX = ((panAngle - 0) / 180) * (crosshairSize - 24);
  const dotY = ((180 - tiltAngle) / 180) * (crosshairSize - 24);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* CABEÇALHO COM STATUS DE SINCRONIA */}
      <View style={styles.header}>
        <View style={styles.headerTitleRow}>
          <SlidersHorizontal size={22} color={theme.colors.accent} />
          <Text style={styles.headerTitle}>Calibração & Controle Manual</Text>
        </View>
        <Text style={styles.headerSubtitle}>
          Sincronização milimétrica e ajuste fino grau a grau dos servos SG90
        </Text>
      </View>

      {/* CARD DE TESTE DO GIROSCÓPIO & HEAD-TRACKING */}
      {headConfig && onUpdateHeadConfig && (
        <GyroscopeTestCard
          onRecenter={onRecenter}
          onServoChange={onServoChange}
          headConfig={headConfig}
          onUpdateHeadConfig={onUpdateHeadConfig}
        />
      )}

      {/* PAINEL DE VISUALIZAÇÃO GRÁFICA / MIRA (CROSSHAIR) */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <View style={styles.cardTitleRow}>
            <Crosshair size={16} color={theme.colors.accent} />
            <Text style={styles.cardTitle}>Orientação Espacial da Câmera</Text>
          </View>
          <View
            style={[
              styles.statusPill,
              telemetry.connected ? styles.statusPillOnline : styles.statusPillOffline,
            ]}
          >
            <View
              style={[
                styles.statusDot,
                telemetry.connected ? styles.statusDotOnline : styles.statusDotOffline,
              ]}
            />
            <Text style={styles.statusText}>
              {telemetry.connected ? 'Sincronizado' : 'Desconectado'}
            </Text>
          </View>
        </View>

        <View style={styles.visualizerRow}>
          {/* Mira 2D Interativa */}
          <View style={[styles.crosshairBox, { width: crosshairSize, height: crosshairSize }]}>
            {/* Linhas de grade da mira */}
            <View style={styles.crosshairGridH} />
            <View style={styles.crosshairGridV} />
            <View style={styles.crosshairCenterRing} />

            {/* Ponto indicador do servo */}
            <View
              style={[
                styles.crosshairDot,
                { transform: [{ translateX: dotX }, { translateY: dotY }] },
              ]}
            >
              <View style={styles.crosshairDotInner} />
            </View>

            {/* Rótulos dos eixos */}
            <Text style={styles.axisLabelTop}>CIMA (180°)</Text>
            <Text style={styles.axisLabelBottom}>BAIXO (0°)</Text>
            <Text style={styles.axisLabelLeft}>ESQ</Text>
            <Text style={styles.axisLabelRight}>DIR</Text>
          </View>

          {/* Ângulos Atuais Grandes */}
          <View style={styles.gaugesContainer}>
            <View style={styles.gaugeBox}>
              <Text style={styles.gaugeTitle}>HORIZONTAL (PAN)</Text>
              <Text style={styles.gaugeValue}>
                {panAngle}
                <Text style={styles.gaugeUnit}>°</Text>
              </Text>
              <Text style={styles.gaugeSubtitle}>Pino D9 (Arduino Nano)</Text>
            </View>

            <View style={styles.gaugeBox}>
              <Text style={styles.gaugeTitle}>VERTICAL (TILT)</Text>
              <Text style={styles.gaugeValue}>
                {tiltAngle}
                <Text style={styles.gaugeUnit}>°</Text>
              </Text>
              <Text style={styles.gaugeSubtitle}>Pino D10 (Arduino Nano)</Text>
            </View>
          </View>
        </View>

        {/* Botão de Centralização Rápida */}
        <TouchableOpacity
          style={styles.recenterMainBtn}
          onPress={() => {
            aplicarMovimento(90, 90);
            onRecenter();
          }}
          activeOpacity={0.8}
        >
          <RotateCcw size={16} color="#000000" />
          <Text style={styles.recenterMainBtnText}>Centralizar Ambos em 90°, 90°</Text>
        </TouchableOpacity>
      </View>

      {/* CONTROLE DE ALTA PRECISÃO: PAN (HORIZONTAL) */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Ajuste Fino: Pan Horizontal (D9)</Text>
          <Text style={styles.badgeAngle}>{panAngle}°</Text>
        </View>

        {/* Barra Visual de Posição */}
        <View style={styles.sliderTrack}>
          <View style={styles.sliderCenterMark} />
          <View
            style={[
              styles.sliderThumb,
              { left: `${(panAngle / 180) * 100}%` },
            ]}
          />
        </View>
        <View style={styles.sliderLimitsRow}>
          <Text style={styles.limitText}>0° (Esq)</Text>
          <Text style={styles.limitText}>90° (Centro)</Text>
          <Text style={styles.limitText}>180° (Dir)</Text>
        </View>

        {/* Botões Passo a Passo (Micro Ajustes) */}
        <View style={styles.stepControlsRow}>
          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle - 10, tiltAngle)}
          >
            <ChevronsLeft size={16} color={theme.colors.text} />
            <Text style={styles.stepBtnText}>-10°</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle - 1, tiltAngle)}
          >
            <ChevronLeft size={16} color={theme.colors.text} />
            <Text style={styles.stepBtnText}>-1°</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.stepBtn, styles.stepBtnCenter]}
            onPress={() => aplicarMovimento(90, tiltAngle)}
          >
            <Text style={styles.stepBtnCenterText}>90°</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle + 1, tiltAngle)}
          >
            <Text style={styles.stepBtnText}>+1°</Text>
            <ChevronRight size={16} color={theme.colors.text} />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle + 10, tiltAngle)}
          >
            <Text style={styles.stepBtnText}>+10°</Text>
            <ChevronsRight size={16} color={theme.colors.text} />
          </TouchableOpacity>
        </View>

        {/* Presets de Pan */}
        <View style={styles.presetsRow}>
          {[
            { label: '0° Esq', p: 0 },
            { label: '45°', p: 45 },
            { label: '90° Centro', p: 90 },
            { label: '135°', p: 135 },
            { label: '180° Dir', p: 180 },
          ].map((item) => (
            <TouchableOpacity
              key={item.label}
              style={[
                styles.presetChip,
                panAngle === item.p && styles.presetChipActive,
              ]}
              onPress={() => aplicarMovimento(item.p, tiltAngle)}
            >
              <Text
                style={[
                  styles.presetChipText,
                  panAngle === item.p && styles.presetChipTextActive,
                ]}
              >
                {item.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* CONTROLE DE ALTA PRECISÃO: TILT (VERTICAL) */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Ajuste Fino: Tilt Vertical (D10)</Text>
          <Text style={styles.badgeAngle}>{tiltAngle}°</Text>
        </View>

        {/* Barra Visual de Posição */}
        <View style={styles.sliderTrack}>
          <View style={styles.sliderCenterMark} />
          <View
            style={[
              styles.sliderThumb,
              { left: `${(tiltAngle / 180) * 100}%` },
            ]}
          />
        </View>
        <View style={styles.sliderLimitsRow}>
          <Text style={styles.limitText}>0° (Chão)</Text>
          <Text style={styles.limitText}>90° (Nível)</Text>
          <Text style={styles.limitText}>180° (Céu)</Text>
        </View>

        {/* Botões Passo a Passo (Micro Ajustes) */}
        <View style={styles.stepControlsRow}>
          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle, tiltAngle - 10)}
          >
            <ChevronsLeft size={16} color={theme.colors.text} />
            <Text style={styles.stepBtnText}>-10°</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle, tiltAngle - 1)}
          >
            <ChevronLeft size={16} color={theme.colors.text} />
            <Text style={styles.stepBtnText}>-1°</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.stepBtn, styles.stepBtnCenter]}
            onPress={() => aplicarMovimento(panAngle, 90)}
          >
            <Text style={styles.stepBtnCenterText}>90°</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle, tiltAngle + 1)}
          >
            <Text style={styles.stepBtnText}>+1°</Text>
            <ChevronRight size={16} color={theme.colors.text} />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.stepBtn}
            onPress={() => aplicarMovimento(panAngle, tiltAngle + 10)}
          >
            <Text style={styles.stepBtnText}>+10°</Text>
            <ChevronsRight size={16} color={theme.colors.text} />
          </TouchableOpacity>
        </View>

        {/* Presets de Tilt */}
        <View style={styles.presetsRow}>
          {[
            { label: '45° Baixo', t: 45 },
            { label: '70° Solo', t: 70 },
            { label: '90° Centro', t: 90 },
            { label: '115° Horizonte', t: 115 },
            { label: '140° Cima', t: 140 },
          ].map((item) => (
            <TouchableOpacity
              key={item.label}
              style={[
                styles.presetChip,
                tiltAngle === item.t && styles.presetChipActive,
              ]}
              onPress={() => aplicarMovimento(panAngle, item.t)}
            >
              <Text
                style={[
                  styles.presetChipText,
                  tiltAngle === item.t && styles.presetChipTextActive,
                ]}
              >
                {item.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* COMPENSAÇÃO ELETRÔNICA DE MONTAGEM DO HORN (TRIM / OFFSET) */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <View style={styles.cardTitleRow}>
            <ShieldAlert size={16} color={theme.colors.accent} />
            <Text style={styles.cardTitle}>Compensação Mecânica de Horn (Trim)</Text>
          </View>
        </View>
        <Text style={styles.cardDescription}>
          Se ao encaixar a cruzeta plástica no estriado do SG90 ela ficou ligeiramente desalinhada (ex: torta em 2° ou 3°), ajuste o Trim eletrônico abaixo para corrigir o zero sem precisar desparafusar o case:
        </Text>

        <View style={styles.trimRow}>
          <Text style={styles.trimLabel}>Trim Pan (Horizontal):</Text>
          <View style={styles.trimControls}>
            <TouchableOpacity
              style={styles.trimBtn}
              onPress={() => setPanTrim((prev) => Math.max(-15, prev - 1))}
            >
              <Text style={styles.trimBtnText}>-1°</Text>
            </TouchableOpacity>
            <Text style={styles.trimValue}>
              {panTrim > 0 ? `+${panTrim}` : panTrim}°
            </Text>
            <TouchableOpacity
              style={styles.trimBtn}
              onPress={() => setPanTrim((prev) => Math.min(15, prev + 1))}
            >
              <Text style={styles.trimBtnText}>+1°</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.trimRow}>
          <Text style={styles.trimLabel}>Trim Tilt (Vertical):</Text>
          <View style={styles.trimControls}>
            <TouchableOpacity
              style={styles.trimBtn}
              onPress={() => setTiltTrim((prev) => Math.max(-15, prev - 1))}
            >
              <Text style={styles.trimBtnText}>-1°</Text>
            </TouchableOpacity>
            <Text style={styles.trimValue}>
              {tiltTrim > 0 ? `+${tiltTrim}` : tiltTrim}°
            </Text>
            <TouchableOpacity
              style={styles.trimBtn}
              onPress={() => setTiltTrim((prev) => Math.min(15, prev + 1))}
            >
              <Text style={styles.trimBtnText}>+1°</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.trimActionsRow}>
          <TouchableOpacity
            style={[styles.saveTrimBtn, trimSaved && styles.saveTrimBtnSaved]}
            onPress={salvarTrim}
            activeOpacity={0.8}
          >
            {trimSaved ? (
              <Check size={16} color="#000000" />
            ) : (
              <Save size={16} color="#000000" />
            )}
            <Text style={styles.saveTrimBtnText}>
              {trimSaved ? 'Trim Salvo na Memória!' : 'Salvar Calibração de Horn'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.resetTrimBtn} onPress={zerarTrim}>
            <Text style={styles.resetTrimBtnText}>Zerar</Text>
          </TouchableOpacity>
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
    gap: 16,
    paddingBottom: 100,
  },
  header: {
    gap: 4,
    paddingHorizontal: 4,
    paddingTop: 8,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
  },
  headerSubtitle: {
    color: theme.colors.textSubtle,
    fontSize: 12,
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 16,
    padding: 16,
    gap: 14,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  cardTitle: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  cardDescription: {
    color: theme.colors.textSubtle,
    fontSize: 12,
    lineHeight: 18,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusPillOnline: {
    backgroundColor: 'rgba(0, 230, 118, 0.15)',
    borderColor: 'rgba(0, 230, 118, 0.3)',
    borderWidth: 1,
  },
  statusPillOffline: {
    backgroundColor: 'rgba(255, 82, 82, 0.15)',
    borderColor: 'rgba(255, 82, 82, 0.3)',
    borderWidth: 1,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  statusDotOnline: {
    backgroundColor: theme.colors.accent,
  },
  statusDotOffline: {
    backgroundColor: theme.colors.danger,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '600',
  },
  visualizerRow: {
    flexDirection: 'row',
    gap: 16,
    alignItems: 'center',
  },
  crosshairBox: {
    backgroundColor: '#0a0d12',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.12)',
    position: 'relative',
    overflow: 'hidden',
  },
  crosshairGridH: {
    position: 'absolute',
    top: '50%',
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
  },
  crosshairGridV: {
    position: 'absolute',
    left: '50%',
    top: 0,
    bottom: 0,
    width: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
  },
  crosshairCenterRing: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    width: 36,
    height: 36,
    marginTop: -18,
    marginLeft: -18,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: 'rgba(41, 182, 246, 0.3)',
  },
  crosshairDot: {
    position: 'absolute',
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: 'rgba(0, 230, 118, 0.35)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  crosshairDotInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: theme.colors.accent,
    shadowColor: theme.colors.accent,
    shadowOpacity: 0.8,
    shadowRadius: 6,
  },
  axisLabelTop: {
    position: 'absolute',
    top: 4,
    alignSelf: 'center',
    fontSize: 8,
    fontWeight: '700',
    color: theme.colors.textSubtle,
  },
  axisLabelBottom: {
    position: 'absolute',
    bottom: 4,
    alignSelf: 'center',
    fontSize: 8,
    fontWeight: '700',
    color: theme.colors.textSubtle,
  },
  axisLabelLeft: {
    position: 'absolute',
    left: 4,
    top: '45%',
    fontSize: 8,
    fontWeight: '700',
    color: theme.colors.textSubtle,
  },
  axisLabelRight: {
    position: 'absolute',
    right: 4,
    top: '45%',
    fontSize: 8,
    fontWeight: '700',
    color: theme.colors.textSubtle,
  },
  gaugesContainer: {
    flex: 1,
    gap: 10,
  },
  gaugeBox: {
    backgroundColor: '#0a0d12',
    borderRadius: 12,
    padding: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  gaugeTitle: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.colors.textSubtle,
  },
  gaugeValue: {
    fontSize: 26,
    fontWeight: '800',
    color: theme.colors.accent,
  },
  gaugeUnit: {
    fontSize: 14,
    fontWeight: '400',
    color: theme.colors.textSubtle,
  },
  gaugeSubtitle: {
    fontSize: 9,
    color: theme.colors.textSubtle,
    marginTop: 2,
  },
  recenterMainBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: theme.colors.accent,
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 4,
  },
  recenterMainBtnText: {
    color: '#000000',
    fontSize: 13,
    fontWeight: '700',
  },
  badgeAngle: {
    fontSize: 14,
    fontWeight: '800',
    color: theme.colors.accent,
    backgroundColor: 'rgba(0, 230, 118, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(0, 230, 118, 0.25)',
  },
  sliderTrack: {
    height: 10,
    backgroundColor: '#181b20',
    borderRadius: 5,
    position: 'relative',
    justifyContent: 'center',
    marginVertical: 4,
  },
  sliderCenterMark: {
    position: 'absolute',
    left: '50%',
    width: 2,
    height: 14,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    marginTop: -2,
  },
  sliderThumb: {
    position: 'absolute',
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: theme.colors.accent,
    marginLeft: -9,
    borderWidth: 2,
    borderColor: '#ffffff',
  },
  sliderLimitsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  limitText: {
    fontSize: 10,
    color: theme.colors.textSubtle,
    fontWeight: '500',
  },
  stepControlsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 6,
    marginTop: 6,
  },
  stepBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#161a22',
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  stepBtnText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  stepBtnCenter: {
    backgroundColor: 'rgba(41, 182, 246, 0.15)',
    borderColor: 'rgba(41, 182, 246, 0.3)',
  },
  stepBtnCenterText: {
    color: '#29b6f6',
    fontSize: 12,
    fontWeight: '800',
  },
  presetsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 4,
    marginTop: 4,
  },
  presetChip: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 7,
    borderRadius: 8,
    backgroundColor: '#12151b',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
  },
  presetChipActive: {
    backgroundColor: 'rgba(0, 230, 118, 0.15)',
    borderColor: theme.colors.accent,
  },
  presetChipText: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.colors.textSubtle,
  },
  presetChipTextActive: {
    color: theme.colors.accent,
    fontWeight: '700',
  },
  trimRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  trimLabel: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '500',
  },
  trimControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  trimBtn: {
    backgroundColor: '#161a22',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  trimBtnText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  trimValue: {
    color: theme.colors.accent,
    fontSize: 14,
    fontWeight: '800',
    minWidth: 32,
    textAlign: 'center',
  },
  trimActionsRow: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 8,
  },
  saveTrimBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    backgroundColor: theme.colors.accent,
    paddingVertical: 12,
    borderRadius: 10,
  },
  saveTrimBtnSaved: {
    backgroundColor: '#29b6f6',
  },
  saveTrimBtnText: {
    color: '#000000',
    fontSize: 12,
    fontWeight: '700',
  },
  resetTrimBtn: {
    backgroundColor: '#161a22',
    paddingHorizontal: 16,
    justifyContent: 'center',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  resetTrimBtnText: {
    color: theme.colors.textSubtle,
    fontSize: 12,
    fontWeight: '600',
  },
});
