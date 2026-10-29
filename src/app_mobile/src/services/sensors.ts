import {
  DeviceMotion,
  DeviceMotionMeasurement,
  Gyroscope,
  GyroscopeMeasurement,
  Accelerometer,
  AccelerometerMeasurement,
} from 'expo-sensors';
import { HeadTrackingConfig, GyroDiagnostics } from '../types';

export type HeadTrackingListener = (pan: number, tilt: number) => void;
export type DiagnosticsListener = (diag: GyroDiagnostics) => void;

export class HeadTrackingService {
  private motionSub: { remove: () => void } | null = null;
  private gyroSub: { remove: () => void } | null = null;
  private accelSub: { remove: () => void } | null = null;

  private isRunning: boolean = false;
  private backend: 'device-motion' | 'gyro-accel' | 'simulated' | 'none' = 'none';

  private listener: HeadTrackingListener | null = null;
  private diagListener: DiagnosticsListener | null = null;

  // Orientação absoluta bruta (° graus)
  private latestRawYaw: number = 0;
  private latestRawPitch: number = 0;
  private latestRawRoll: number = 0;
  private hasFirstSample: boolean = false;

  // Centro calibrado (recenter)
  private offsetYaw: number = 0;
  private offsetPitch: number = 0;

  // Saídas suavizadas e filtradas (graus de servo)
  private smoothPan: number = 90;
  private smoothTilt: number = 90;

  // Últimos valores efetivamente transmitidos ao Rover
  private lastSentPan: number = 90;
  private lastSentTilt: number = 90;

  // Estado do filtro complementar de emergência (Gyroscope + Accelerometer)
  private lastGyroTimestamp: number = 0;
  private integratedYaw: number = 0;
  private integratedPitch: number = 0;
  private accelPitch: number = 0;

  // Métricas de diagnóstico
  private samplesCount: number = 0;
  private lastSampleTimestamp: number = 0;
  private hzCounter: number = 0;
  private hzTimer: any = null;
  private calculatedHz: number = 0;
  private isLandscape: boolean = false;

  private config: HeadTrackingConfig = {
    enabled: false,
    emaAlpha: 0.18,      // Resposta ágil com amortecimento de micro-tremores
    deadbandDeg: 1.2,    // Elimina ruído de repouso dos servos SG90
    panMin: 30,          // Limites mecânicos seguros para a cabeça Pan/Tilt
    panMax: 150,
    tiltMin: 40,
    tiltMax: 140,
    invertPan: false,
    invertTilt: true, // Invertido por padrao para orientacao natural (erguer celular = olhar para cima)
    updateRateHz: 25,    // 25 Hz = latência de ~40 ms (ideal para Wi-Fi sem saturar buffers)
  };

  constructor() {}

  public updateConfig(newConfig: Partial<HeadTrackingConfig>) {
    this.config = { ...this.config, ...newConfig };
    const intervalMs = Math.round(1000 / Math.max(5, Math.min(60, this.config.updateRateHz)));

    if (this.isRunning) {
      try {
        DeviceMotion.setUpdateInterval(intervalMs);
        Gyroscope.setUpdateInterval(intervalMs);
        Accelerometer.setUpdateInterval(intervalMs);
      } catch {}
    }
  }

  public getConfig(): HeadTrackingConfig {
    return { ...this.config };
  }

  public getDiagnostics(): GyroDiagnostics {
    return {
      active: this.isRunning,
      backend: this.backend,
      rawYaw: Math.round(this.latestRawYaw * 10) / 10,
      rawPitch: Math.round(this.latestRawPitch * 10) / 10,
      rawRoll: Math.round(this.latestRawRoll * 10) / 10,
      smoothPan: Math.round(this.smoothPan),
      smoothTilt: Math.round(this.smoothTilt),
      sentPan: this.lastSentPan,
      sentTilt: this.lastSentTilt,
      hz: this.calculatedHz,
      samplesCount: this.samplesCount,
      lastUpdateMs: this.lastSampleTimestamp,
      isLandscape: this.isLandscape,
    };
  }

  public onDiagnostics(diagListener: DiagnosticsListener | null) {
    this.diagListener = diagListener;
  }

  /**
   * Inicia o monitoramento dos sensores com seleção resiliente do melhor backend
   */
  public async start(listener: HeadTrackingListener) {
    this.listener = listener;
    if (this.isRunning) return;

    this.samplesCount = 0;
    this.calculatedHz = 0;
    this.hzCounter = 0;
    this.startHzTimer();

    const intervalMs = Math.round(1000 / this.config.updateRateHz);

    // 1. Tenta inicializar DeviceMotion (fusão completa de 3 eixos / rotação de quaternions)
    let deviceMotionReady = false;
    try {
      const dmAvail = await DeviceMotion.isAvailableAsync();
      if (dmAvail) {
        DeviceMotion.setUpdateInterval(intervalMs);
        this.motionSub = DeviceMotion.addListener(this.handleDeviceMotion);
        deviceMotionReady = true;
        this.backend = 'device-motion';
      }
    } catch (e) {
      console.warn('[HeadTracking] DeviceMotion indisponível:', e);
    }

    // 2. Fallback de hardware: se DeviceMotion não responder ou não existir, ativa Giroscópio + Acelerômetro
    if (!deviceMotionReady) {
      try {
        const gyroAvail = await Gyroscope.isAvailableAsync();
        const accelAvail = await Accelerometer.isAvailableAsync();

        if (gyroAvail && accelAvail) {
          Gyroscope.setUpdateInterval(intervalMs);
          Accelerometer.setUpdateInterval(intervalMs);
          this.gyroSub = Gyroscope.addListener(this.handleGyroscope);
          this.accelSub = Accelerometer.addListener(this.handleAccelerometer);
          this.backend = 'gyro-accel';
        } else {
          // 3. Fallback para simulação interativa (Web / Emulador de PC)
          this.backend = 'simulated';
        }
      } catch (e) {
        this.backend = 'simulated';
      }
    }

    this.isRunning = true;
    this.notifyDiagnostics();
  }

  /**
   * Interrompe as assinaturas de sensores
   */
  public stop() {
    if (this.motionSub) {
      this.motionSub.remove();
      this.motionSub = null;
    }
    if (this.gyroSub) {
      this.gyroSub.remove();
      this.gyroSub = null;
    }
    if (this.accelSub) {
      this.accelSub.remove();
      this.accelSub = null;
    }

    clearInterval(this.hzTimer);
    this.hzTimer = null;
    this.isRunning = false;
    this.backend = 'none';
    this.notifyDiagnostics();
  }

  /**
   * Centraliza e grava a pose atual da cabeça como horizonte neutro (90°, 90°)
   */
  public recenter() {
    this.offsetYaw = this.latestRawYaw;
    this.offsetPitch = this.latestRawPitch;
    this.integratedYaw = 0;
    this.integratedPitch = 0;

    this.smoothPan = 90;
    this.smoothTilt = 90;
    this.lastSentPan = 90;
    this.lastSentTilt = 90;

    if (this.listener) {
      this.listener(90, 90);
    }
    this.notifyDiagnostics();
  }

  /**
   * Permite injeção de movimento para testes na interface, emulador ou testes unitários
   */
  public simulateMotion(deltaYaw: number, deltaPitch: number) {
    if (!this.isRunning) return;
    this.backend = 'simulated';
    this.processAngles(
      this.latestRawYaw + deltaYaw,
      this.latestRawPitch + deltaPitch,
      0,
      true
    );
  }

  // ---------------- Processamento do Backend 1: DeviceMotion ----------------
  private handleDeviceMotion = (measurement: DeviceMotionMeasurement) => {
    // Se o dispositivo reportar DeviceMotion mas rotation vier nulo, chaveia para Gyroscope fallback
    if (!measurement.rotation) {
      if (this.backend === 'device-motion') {
        this.fallbackToGyroscope();
      }
      return;
    }

    const { alpha, beta, gamma } = measurement.rotation;
    const orientation = measurement.orientation ?? 0;
    const landscape = Math.abs(orientation) === 90;

    let rawYaw: number;
    let rawPitch: number;
    let rawRoll: number;

    if (landscape) {
      // MODO HORIZONTAL / VR (Óculos ou celular deitado):
      // Rotação horizontal do pescoço (Yaw) mapeada diretamente por alpha
      // Inclinação para cima/baixo (Pitch) mapeada por gamma compensando a orientação
      const sign = orientation > 0 ? 1 : -1;
      rawYaw = (alpha * 180) / Math.PI;
      rawPitch = ((gamma * 180) / Math.PI) * sign;
      rawRoll = (beta * 180) / Math.PI;
    } else {
      // MODO VERTICAL (Em pé):
      // Inclinação frontal (Pitch) por beta
      // Azimute por alpha com desacoplamento de Euler
      rawPitch = (beta * 180) / Math.PI;
      const cosPitch = Math.abs(Math.cos(beta));
      rawYaw = ((alpha * 180) / Math.PI) * Math.max(0.2, cosPitch);
      rawRoll = (gamma * 180) / Math.PI;
    }

    this.processAngles(rawYaw, rawPitch, rawRoll, landscape);
  };

  // ---------------- Processamento do Backend 2: Giroscópio + Acelerômetro ----------------
  private handleAccelerometer = (measurement: AccelerometerMeasurement) => {
    const { x, y, z } = measurement;
    // Calcula ângulo gravitacional de Pitch de forma absoluta e sem deriva
    const pitchRad = Math.atan2(y, Math.sqrt(x * x + z * z));
    this.accelPitch = (pitchRad * 180) / Math.PI;
  };

  private handleGyroscope = (measurement: GyroscopeMeasurement) => {
    const now = Date.now();
    if (!this.lastGyroTimestamp) this.lastGyroTimestamp = now;
    const dt = Math.min(0.1, (now - this.lastGyroTimestamp) / 1000);
    this.lastGyroTimestamp = now;

    const { x, y, z } = measurement;

    // Filtro de Zona Morta em Repouso do Giroscópio (evita deriva estática)
    const deadbandVel = 0.03; // rad/s (~1.7°/s)
    const gz = Math.abs(z) > deadbandVel ? z : 0;
    const gx = Math.abs(x) > deadbandVel ? x : 0;

    this.integratedYaw += gz * dt * (180 / Math.PI);
    this.integratedPitch += gx * dt * (180 / Math.PI);

    // Fusão Complementar com Acelerômetro no Pitch (96% Gyro + 4% Acelerômetro)
    // Isso garante resposta instantânea sem acumular erro angular com o tempo
    this.integratedPitch = 0.96 * this.integratedPitch + 0.04 * this.accelPitch;

    this.processAngles(this.integratedYaw, this.integratedPitch, 0, true);
  };

  private fallbackToGyroscope() {
    console.warn('[HeadTracking] Chaveando para fallback Gyroscope + Accelerometer');
    if (this.motionSub) {
      this.motionSub.remove();
      this.motionSub = null;
    }
    const intervalMs = Math.round(1000 / this.config.updateRateHz);
    try {
      Gyroscope.setUpdateInterval(intervalMs);
      Accelerometer.setUpdateInterval(intervalMs);
      this.gyroSub = Gyroscope.addListener(this.handleGyroscope);
      this.accelSub = Accelerometer.addListener(this.handleAccelerometer);
      this.backend = 'gyro-accel';
    } catch {
      this.backend = 'simulated';
    }
    this.notifyDiagnostics();
  }

  // ---------------- Pipeline Central de Normalização & Filtragem ----------------
  private processAngles(rawYaw: number, rawPitch: number, rawRoll: number, isLandscape: boolean) {
    this.samplesCount++;
    this.hzCounter++;
    this.lastSampleTimestamp = Date.now();
    this.isLandscape = isLandscape;

    this.latestRawYaw = rawYaw;
    this.latestRawPitch = rawPitch;
    this.latestRawRoll = rawRoll;

    if (!this.hasFirstSample) {
      this.offsetYaw = rawYaw;
      this.offsetPitch = rawPitch;
      this.hasFirstSample = true;
    }

    let deltaYaw = rawYaw - this.offsetYaw;
    let deltaPitch = rawPitch - this.offsetPitch;

    // Normalização circular periódica [-180°, +180°] para evitar saltos
    while (deltaYaw > 180) deltaYaw -= 360;
    while (deltaYaw < -180) deltaYaw += 360;
    while (deltaPitch > 180) deltaPitch -= 360;
    while (deltaPitch < -180) deltaPitch += 360;

    // Amortecimento de desvio lateral espúrio em movimentos puramente verticais
    if (!isLandscape && Math.abs(deltaPitch) > 15 && Math.abs(deltaYaw) < Math.abs(deltaPitch) * 0.4) {
      deltaYaw *= 0.3;
    }

    if (this.config.invertPan) deltaYaw = -deltaYaw;
    if (this.config.invertTilt) deltaPitch = -deltaPitch;

    // Mapeamento para o sistema de coordenadas do Rover: Centro neutro = 90°
    const targetPan = 90 + deltaYaw;
    const targetTilt = 90 + deltaPitch;

    // Filtro EMA (Exponential Moving Average) anti-tremedeira
    const alpha = Math.max(0.05, Math.min(0.8, this.config.emaAlpha));
    this.smoothPan = alpha * targetPan + (1 - alpha) * this.smoothPan;
    this.smoothTilt = alpha * targetTilt + (1 - alpha) * this.smoothTilt;

    // Clamping rígido de proteção física dos limites mecânicos dos servos
    const clampedPan = Math.max(this.config.panMin, Math.min(this.config.panMax, this.smoothPan));
    const clampedTilt = Math.max(this.config.tiltMin, Math.min(this.config.tiltMax, this.smoothTilt));

    // Zona Morta (Deadband): só despacha pacote via Wi-Fi se houver mudança perceptível
    const panDiff = Math.abs(clampedPan - this.lastSentPan);
    const tiltDiff = Math.abs(clampedTilt - this.lastSentTilt);

    if (panDiff >= this.config.deadbandDeg || tiltDiff >= this.config.deadbandDeg) {
      this.lastSentPan = Math.round(clampedPan);
      this.lastSentTilt = Math.round(clampedTilt);

      if (this.listener) {
        this.listener(this.lastSentPan, this.lastSentTilt);
      }
    }

    this.notifyDiagnostics();
  }

  private startHzTimer() {
    clearInterval(this.hzTimer);
    this.hzTimer = setInterval(() => {
      this.calculatedHz = this.hzCounter;
      this.hzCounter = 0;
      this.notifyDiagnostics();
    }, 1000);
  }

  private notifyDiagnostics() {
    if (this.diagListener) {
      this.diagListener(this.getDiagnostics());
    }
  }
}

export const headTracking = new HeadTrackingService();
