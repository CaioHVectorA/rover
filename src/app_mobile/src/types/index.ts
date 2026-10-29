export type AppTab = 'drive' | 'pocs' | 'calibrate' | 'vr' | 'settings';
export type AppMode = AppTab; // Retrocompatibilidade
export type OperationMode = 'simulation' | 'esp32';
export type FirmwareProtocol = 'hybrid' | 'poc_ascii' | 'gateway_json';

export interface PocStats {
  sys: {
    temp: number;
    cpu: number;
    heap: number;
    psram: number;
    rssi: number;
    up: number;
  };
  link: {
    tx: number;
    rx: number;
    err: number;
    hb_age: number;
    vbat: number; // mV
    vmin: number; // mV
    mot_e: number; // -255 a 255
    mot_d: number; // -255 a 255
    reset: number; // MCUSR flags: 1=Power-on, 2=Ext, 4=Brown-Out, 8=Watchdog
    nano_up: number;
  };
  cam: {
    modo: 'ATIVO' | 'ECO' | 'DORMINDO' | 'TERMICO';
    forcado: boolean;
    fps: number;
    teto_fps: number;
    kbps: number;
    kb_frame: number;
    cap_ms: number;
    xclk: number;
    res_px: string;
    clientes: number;
    dormindo: boolean;
    preset: 'frio' | 'equilibrado' | 'qualidade';
  };
}

export interface RoverTelemetry {
  connected: boolean;
  operationMode: OperationMode;
  pingMs: number;
  batteryVoltage?: number;
  batteryMinVoltage?: number;
  batteryPercent?: number;
  lastResponse?: string;
  panAngle: number;
  tiltAngle: number;
  targetPanAngle: number;
  targetTiltAngle: number;
  speed: number;
  motorLeftPwm: number;
  motorRightPwm: number;
  direction: 'STOP' | 'F' | 'B' | 'L' | 'R' | 'S';
  poc5AutoRunning?: boolean;
  stats?: PocStats;
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

export interface GyroDiagnostics {
  active: boolean;
  backend: 'device-motion' | 'gyro-accel' | 'simulated' | 'none';
  rawYaw: number;
  rawPitch: number;
  rawRoll: number;
  smoothPan: number;
  smoothTilt: number;
  sentPan: number;
  sentTilt: number;
  hz: number;
  samplesCount: number;
  lastUpdateMs: number;
  isLandscape: boolean;
}

export interface ConnectionConfig {
  mode: OperationMode;
  protocol: FirmwareProtocol;
  ip: string;
  wsPort: number;
  streamPort: number;
  streamPath: string;
  mockServerIp: string;
  mockWsPort: number;
  mockHttpPort: number;
}
