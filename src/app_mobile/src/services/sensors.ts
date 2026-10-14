import { DeviceMotion, DeviceMotionMeasurement } from 'expo-sensors';
import { HeadTrackingConfig } from '../types';

export type HeadTrackingListener = (pan: number, tilt: number) => void;

export class HeadTrackingService {
  private subscription: any = null;
  private isRunning: boolean = false;
  private listener: HeadTrackingListener | null = null;

  private latestRawYaw: number = 0;
  private latestRawPitch: number = 0;
  private hasFirstSample: boolean = false;

  private offsetYaw: number = 0;
  private offsetPitch: number = 0;

  private smoothPan: number = 90;
  private smoothTilt: number = 90;

  private lastSentPan: number = 90;
  private lastSentTilt: number = 90;

  private config: HeadTrackingConfig = {
    enabled: true,
    emaAlpha: 0.25,
    deadbandDeg: 0.5,
    panMin: 20,
    panMax: 160,
    tiltMin: 50,
    tiltMax: 130,
    invertPan: false,
    invertTilt: false,
    updateRateHz: 40,
  };

  constructor() {}

  public updateConfig(newConfig: Partial<HeadTrackingConfig>) {
    this.config = { ...this.config, ...newConfig };
    if (this.isRunning && newConfig.updateRateHz) {
      DeviceMotion.setUpdateInterval(Math.round(1000 / this.config.updateRateHz));
    }
  }

  public getConfig(): HeadTrackingConfig {
    return { ...this.config };
  }

  public async start(listener: HeadTrackingListener) {
    this.listener = listener;
    if (this.isRunning) return;

    try {
      const isAvailable = await DeviceMotion.isAvailableAsync();
      if (!isAvailable) {
        console.warn('[HeadTracking] Sensor DeviceMotion não disponível');
        return;
      }

      DeviceMotion.setUpdateInterval(Math.round(1000 / this.config.updateRateHz));
      this.subscription = DeviceMotion.addListener(this.handleMotionUpdate);
      this.isRunning = true;
    } catch (e) {
      console.error('[HeadTracking] Erro ao ligar sensor:', e);
    }
  }

  public stop() {
    if (this.subscription) {
      this.subscription.remove();
      this.subscription = null;
    }
    this.isRunning = false;
  }

  /**
   * ZERA a orientação atual como o novo centro (90°, 90°)
   */
  public recenter() {
    this.offsetYaw = this.latestRawYaw;
    this.offsetPitch = this.latestRawPitch;
    this.smoothPan = 90;
    this.smoothTilt = 90;
    this.lastSentPan = 90;
    this.lastSentTilt = 90;

    if (this.listener) {
      this.listener(90, 90);
    }
  }

  private handleMotionUpdate = (measurement: DeviceMotionMeasurement) => {
    if (!measurement.rotation) return;

    const { alpha, beta, gamma } = measurement.rotation;
    const orientation = measurement.orientation ?? 0;
    const isLandscape = Math.abs(orientation) === 90;

    let rawYaw: number;
    let rawPitch: number;

    if (isLandscape) {
      // MODO VR (Paisagem): Eixos naturais do pescoço sem Gimbal Lock
      const sign = orientation > 0 ? 1 : -1;
      rawYaw = (alpha * 180) / Math.PI;
      rawPitch = ((gamma * 180) / Math.PI) * sign;
    } else {
      // MODO EM PÉ (Portrait):
      // Inclinar para frente/trás (Pitch) é medido por beta
      rawPitch = (beta * 180) / Math.PI;

      // Compensação de Gimbal Lock em Portrait:
      // Quando beta inclina para trás, alpha sofre acoplamento cruzado na esfera de Euler.
      // Projetamos o azimute no plano da mão com amortecimento de Pitch cruzado
      const cosPitch = Math.abs(Math.cos(beta));
      const uncoupledAlpha = ((alpha * 180) / Math.PI) * Math.max(0.3, cosPitch);
      rawYaw = uncoupledAlpha;
    }

    this.latestRawYaw = rawYaw;
    this.latestRawPitch = rawPitch;

    if (!this.hasFirstSample) {
      this.offsetYaw = rawYaw;
      this.offsetPitch = rawPitch;
      this.hasFirstSample = true;
    }

    let deltaYaw = rawYaw - this.offsetYaw;
    let deltaPitch = rawPitch - this.offsetPitch;

    // Normalização circular 360
    while (deltaYaw > 180) deltaYaw -= 360;
    while (deltaYaw < -180) deltaYaw += 360;

    // No modo portrait, se o usuário estiver fazendo movimento puramente vertical (olhando pra cima),
    // desacoplamos micro-desvios de mão no Pan para não dar puxão na diagonal
    if (!isLandscape && Math.abs(deltaPitch) > 15 && Math.abs(deltaYaw) < Math.abs(deltaPitch) * 0.4) {
      deltaYaw *= 0.3; // Amortece o desvio lateral espúrio
    }

    if (this.config.invertPan) deltaYaw = -deltaYaw;
    if (this.config.invertTilt) deltaPitch = -deltaPitch;

    const targetPan = 90 + deltaYaw;
    const targetTilt = 90 + deltaPitch;

    // Filtro EMA
    const alphaEMA = this.config.emaAlpha;
    this.smoothPan = alphaEMA * targetPan + (1 - alphaEMA) * this.smoothPan;
    this.smoothTilt = alphaEMA * targetTilt + (1 - alphaEMA) * this.smoothTilt;

    const clampedPan = Math.max(this.config.panMin, Math.min(this.config.panMax, this.smoothPan));
    const clampedTilt = Math.max(this.config.tiltMin, Math.min(this.config.tiltMax, this.smoothTilt));

    const panDiff = Math.abs(clampedPan - this.lastSentPan);
    const tiltDiff = Math.abs(clampedTilt - this.lastSentTilt);

    if (panDiff >= this.config.deadbandDeg || tiltDiff >= this.config.deadbandDeg) {
      this.lastSentPan = clampedPan;
      this.lastSentTilt = clampedTilt;

      if (this.listener) {
        this.listener(Math.round(clampedPan), Math.round(clampedTilt));
      }
    }
  };
}

export const headTracking = new HeadTrackingService();
