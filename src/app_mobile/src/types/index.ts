export type AppTab = 'drive' | 'calibrate' | 'vr' | 'settings';
export type AppMode = AppTab; // Retrocompatibilidade

export interface RoverTelemetry {
  connected: boolean;
  pingMs: number;
  batteryVoltage?: number;
  batteryPercent?: number;
  lastResponse?: string;
  panAngle: number;
  tiltAngle: number;
  speed: number;
  direction: 'STOP' | 'F' | 'B' | 'L' | 'R' | 'S';
}

export interface HeadTrackingConfig {
  enabled: boolean;
  emaAlpha: number; // 0.15 (suave) a 0.40 (rápido)
  deadbandDeg: number; // 0.4° a 1.5°
  panMin: number;
  panMax: number;
  tiltMin: number;
  tiltMax: number;
  invertPan: boolean;
  invertTilt: boolean;
  updateRateHz: number;
}

export interface ConnectionConfig {
  ip: string;
  wsPort: number;
  streamPort: number;
  streamPath: string;
}
