import { FirmwareProtocol, OperationMode, PocStats } from '../types';

type MessageCallback = (data: any) => void;
type StatusCallback = (connected: boolean, pingMs: number) => void;

export class RoverWebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private httpBaseUrl: string = '';
  private mode: OperationMode = 'simulation';
  private protocol: FirmwareProtocol = 'hybrid';

  private onMessageCb: MessageCallback | null = null;
  private onStatusCb: StatusCallback | null = null;
  private reconnectTimer: any = null;
  private pingIntervalTimer: any = null;
  private simPhysicsTimer: any = null;
  private statsPollTimer: any = null;

  private isConnecting: boolean = false;
  private lastPingSentAt: number = 0;
  private pingMs: number = 14;
  private startTime: number = Date.now();

  // Estado do Simulador Embarcado de 50 Hz (espelha o Nano + ESP32-S3)
  private sim = {
    targetPan: 90,
    targetTilt: 90,
    pan: 90,
    tilt: 90,
    servoSpeedDegS: 145,
    servoFloorDegS: 15,
    targetMotL: 0,
    targetMotR: 0,
    motL: 0,
    motR: 0,
    rampMs: 800,
    watchdogMs: 600,
    lastMotorCmdAt: Date.now(),
    poc5AutoRunning: false,
    txFrames: 0,
    rxFrames: 0,
    rxErrors: 0,
    lastHbAt: Date.now(),
    resetFlags: 1, // 1 = Power-On
    vbatBaseMv: 8180,
    vbatMv: 8180,
    vminMv: 8180,
    camSleeping: false,
    camPreset: 'equilibrado' as 'frio' | 'equilibrado' | 'qualidade',
    camRes: 'qvga',
    camXclk: 12,
    camTargetFps: 15,
    camActualFps: 15,
    chipTempC: 44.2,
    lastActivityAt: Date.now(),
  };

  constructor() {
    this.startLocalSimEngine();
  }

  public configure(
    mode: OperationMode,
    ip: string,
    wsPort: number,
    httpPort: number = 80,
    protocol: FirmwareProtocol = 'hybrid'
  ) {
    this.mode = mode;
    this.protocol = protocol;
    this.url = `ws://${ip}:${wsPort}`;
    this.httpBaseUrl = `http://${ip}:${httpPort}`;

    this.cleanupSocket();

    if (this.mode === 'simulation') {
      // No modo simulação o link virtual está sempre online (e tenta espelhar no Mock Server do PC em background)
      this.pingMs = 12;
      if (this.onStatusCb) this.onStatusCb(true, this.pingMs);
      this.initWebSocket(true);
    } else {
      if (this.onStatusCb) this.onStatusCb(false, 0);
      this.initWebSocket(false);
      this.startHttpStatsPolling();
    }
  }

  public connect(ip: string, port: number = 81) {
    this.configure(this.mode, ip, port, port === 8082 ? 8080 : 80, this.protocol);
  }

  private startLocalSimEngine() {
    clearInterval(this.simPhysicsTimer);
    let tickCount = 0;

    this.simPhysicsTimer = setInterval(() => {
      if (this.mode !== 'simulation') return;
      tickCount++;
      const now = Date.now();
      const dt = 0.05; // 20 Hz loop local para leveza na UI React Native

      // 1. Interpolação de Servos SG90
      const maxStep = Math.max(this.sim.servoFloorDegS, this.sim.servoSpeedDegS) * dt;
      const dPan = this.sim.targetPan - this.sim.pan;
      const dTilt = this.sim.targetTilt - this.sim.tilt;
      this.sim.pan = Math.abs(dPan) <= maxStep ? this.sim.targetPan : this.sim.pan + Math.sign(dPan) * maxStep;
      this.sim.tilt = Math.abs(dTilt) <= maxStep ? this.sim.targetTilt : this.sim.tilt + Math.sign(dTilt) * maxStep;

      // 2. Sequência Autônoma POC 5
      if (this.sim.poc5AutoRunning) {
        const cycle = (now - this.startTime) % 12000;
        if (cycle < 2500) { this.sim.targetMotL = 180; this.sim.targetMotR = 180; }
        else if (cycle < 3500) { this.sim.targetMotL = 0; this.sim.targetMotR = 0; }
        else if (cycle < 6000) { this.sim.targetMotL = -180; this.sim.targetMotR = -180; }
        else if (cycle < 7000) { this.sim.targetMotL = 0; this.sim.targetMotR = 0; }
        else if (cycle < 9000) { this.sim.targetMotL = 160; this.sim.targetMotR = -160; }
        else if (cycle < 11000) { this.sim.targetMotL = -160; this.sim.targetMotR = 160; }
        else { this.sim.targetMotL = 0; this.sim.targetMotR = 0; }
      }

      // 3. Rampa dos Motores 4WD (TB6612FNG)
      const rampStep = (255 / Math.max(100, this.sim.rampMs)) * 50;
      const dL = this.sim.targetMotL - this.sim.motL;
      const dR = this.sim.targetMotR - this.sim.motR;
      this.sim.motL = Math.abs(dL) <= rampStep ? this.sim.targetMotL : this.sim.motL + Math.sign(dL) * rampStep;
      this.sim.motR = Math.abs(dR) <= rampStep ? this.sim.targetMotR : this.sim.motR + Math.sign(dR) * rampStep;

      // 4. Queda de Tensão da Bateria 2S (Voltage Sag sob carga 4WD)
      const load = (Math.abs(this.sim.motL) + Math.abs(this.sim.motR)) / 510;
      const surge = (Math.abs(dL) + Math.abs(dR)) / 510;
      const sag = Math.round(load * 440 + surge * 320 + (Math.random() * 14 - 7));
      this.sim.vbatMv = Math.max(6200, this.sim.vbatBaseMv - sag);
      if (this.sim.vbatMv < this.sim.vminMv) this.sim.vminMv = this.sim.vbatMv;

      // 5. Heartbeat 1 Hz
      if (now - this.sim.lastHbAt >= 1000) {
        this.sim.lastHbAt = now;
        this.sim.rxFrames++;
      }

      // 6. Térmica OV5640 + ESP32-S3
      const isEco = !this.sim.camSleeping && (now - this.sim.lastActivityAt > 8000);
      let targetTemp = 42.0;
      if (this.sim.camSleeping) { targetTemp = 37.2; this.sim.camActualFps = 0; }
      else if (isEco) { targetTemp = 41.5; this.sim.camActualFps = 5; }
      else if (this.sim.camPreset === 'frio') { targetTemp = 44.0; this.sim.camActualFps = 12; }
      else if (this.sim.camPreset === 'equilibrado') { targetTemp = 48.5; this.sim.camActualFps = 15; }
      else { targetTemp = 57.5; this.sim.camActualFps = 25; }
      this.sim.chipTempC += (targetTemp - this.sim.chipTempC) * 0.03;

      // Emite telemetria para a UI a cada 250ms (5 ticks)
      if (tickCount % 5 === 0 && this.onMessageCb) {
        const isEcoNow = !this.sim.camSleeping && (now - this.sim.lastActivityAt > 8000);
        const pct = Math.max(0, Math.min(100, Math.round(((this.sim.vbatMv - 6400) / (8400 - 6400)) * 100)));
        const resMap: Record<string, string> = { hqvga: '240x176', qvga: '320x240', vga: '640x480', svga: '800x600' };

        const stats: PocStats = {
          sys: {
            temp: Number(this.sim.chipTempC.toFixed(1)),
            cpu: 240,
            heap: 248500,
            psram: 8120000,
            rssi: -46,
            up: Math.floor((now - this.startTime) / 1000),
          },
          link: {
            tx: this.sim.txFrames,
            rx: this.sim.rxFrames,
            err: this.sim.rxErrors,
            hb_age: now - this.sim.lastHbAt,
            vbat: this.sim.vbatMv,
            vmin: this.sim.vminMv,
            mot_e: Math.round(this.sim.motL),
            mot_d: Math.round(this.sim.motR),
            reset: this.sim.resetFlags,
            nano_up: Math.floor((now - this.startTime) / 1000),
          },
          cam: {
            modo: this.sim.camSleeping ? 'DORMINDO' : (isEcoNow ? 'ECO' : 'ATIVO'),
            forcado: false,
            fps: this.sim.camActualFps,
            teto_fps: this.sim.camTargetFps,
            kbps: this.sim.camSleeping ? 0 : Math.round(this.sim.camActualFps * 9.5 * 8),
            kb_frame: 9.5,
            cap_ms: 6.1,
            xclk: this.sim.camXclk,
            res_px: resMap[this.sim.camRes] || '320x240',
            clientes: 1,
            dormindo: this.sim.camSleeping,
            preset: this.sim.camPreset,
          },
        };

        this.pingMs = 11 + Math.floor(Math.random() * 4);
        if (this.onStatusCb) this.onStatusCb(true, this.pingMs);

        this.onMessageCb({
          type: 'telemetry',
          vbat: Number((this.sim.vbatMv / 1000).toFixed(2)),
          vmin: Number((this.sim.vminMv / 1000).toFixed(2)),
          pct,
          pan: Math.round(this.sim.pan),
          tilt: Math.round(this.sim.tilt),
          motL: Math.round(this.sim.motL),
          motR: Math.round(this.sim.motR),
          poc5AutoRunning: this.sim.poc5AutoRunning,
          stats,
        });
      }
    }, 50);
  }

  private startHttpStatsPolling() {
    clearInterval(this.statsPollTimer);
    if (this.mode !== 'esp32') return;

    this.statsPollTimer = setInterval(async () => {
      if (this.mode !== 'esp32' || !this.httpBaseUrl) return;
      try {
        const t0 = Date.now();
        const res = await fetch(`${this.httpBaseUrl}/api/stats`);
        if (res.ok) {
          const data = await res.json();
          const rtt = Date.now() - t0;
          if (!this.isConnected() && this.onStatusCb) {
            this.onStatusCb(true, rtt);
          }
          if (this.onMessageCb && data.sys) {
            const vbatMv = data.link?.vbat ?? 7800;
            const vminMv = data.link?.vmin ?? 7800;
            const pct = Math.max(0, Math.min(100, Math.round(((vbatMv - 6400) / (8400 - 6400)) * 100)));
            this.onMessageCb({
              type: 'telemetry',
              vbat: Number((vbatMv / 1000).toFixed(2)),
              vmin: Number((vminMv / 1000).toFixed(2)),
              pct,
              motL: data.link?.mot_e ?? 0,
              motR: data.link?.mot_d ?? 0,
              stats: data,
            });
          }
        }
      } catch {}
    }, 1000);
  }

  private initWebSocket(silentForSim: boolean = false) {
    if (!this.url) return;
    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnecting = false;
        if (this.onStatusCb) this.onStatusCb(true, this.pingMs || 15);
        this.startPing();
      };

      this.ws.onmessage = (event) => {
        const now = Date.now();
        if (this.lastPingSentAt > 0) {
          this.pingMs = now - this.lastPingSentAt;
          this.lastPingSentAt = 0;
          if (this.onStatusCb) this.onStatusCb(true, this.pingMs);
        }

        try {
          const parsed = JSON.parse(event.data);
          if (this.mode === 'esp32' && this.onMessageCb) {
            this.onMessageCb(parsed);
          } else if (this.mode === 'simulation' && parsed.type === 'ack' && this.onMessageCb) {
            this.onMessageCb(parsed);
          }
        } catch {
          if (this.onMessageCb) this.onMessageCb({ raw: event.data });
        }
      };

      this.ws.onerror = () => {
        if (!silentForSim && this.onStatusCb) this.onStatusCb(false, 0);
      };

      this.ws.onclose = () => {
        this.isConnecting = false;
        if (!silentForSim && this.onStatusCb) this.onStatusCb(false, 0);
        this.scheduleReconnect();
      };
    } catch {
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  private startPing() {
    clearInterval(this.pingIntervalTimer);
    this.pingIntervalTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.lastPingSentAt = Date.now();
        this.ws.send(JSON.stringify({ type: 'ping', t: this.lastPingSentAt }));
      }
    }, 2000);
  }

  private scheduleReconnect() {
    clearInterval(this.pingIntervalTimer);
    clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      if (!this.isConnected() && !this.isConnecting) {
        this.initWebSocket(this.mode === 'simulation');
      }
    }, 3000);
  }

  public sendRaw(msg: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(msg);
        return true;
      } catch {}
    }
    return false;
  }

  public sendServoPanTilt(pan: number, tilt: number, speedDegS: number = 0) {
    const p = Math.max(0, Math.min(180, Math.round(pan)));
    const t = Math.max(0, Math.min(180, Math.round(tilt)));
    this.sim.lastActivityAt = Date.now();
    this.sim.targetPan = p;
    this.sim.targetTilt = t;
    if (speedDegS > 0) this.sim.servoSpeedDegS = speedDegS;
    this.sim.txFrames++;
    this.sim.rxFrames++;

    // Envia tanto o quadro ASCII das POCs (<S,pan10,tilt10,vel10>) quanto o JSON do Gateway/Mock
    const asciiFrame = `<S,${Math.round(p * 10)},${Math.round(t * 10)},${Math.round(speedDegS * 10)}>`;
    const jsonFrame = JSON.stringify({ type: 'servo', pan: p, tilt: t, speed: speedDegS });

    if (this.mode === 'simulation') {
      this.sendRaw(jsonFrame);
      return true;
    }

    if (this.protocol === 'poc_ascii') {
      return this.sendRaw(asciiFrame);
    } else if (this.protocol === 'gateway_json') {
      return this.sendRaw(jsonFrame);
    } else {
      this.sendRaw(asciiFrame);
      return this.sendRaw(jsonFrame);
    }
  }

  public sendDrive(command: 'F' | 'B' | 'L' | 'R' | 'S', speed: number = 200) {
    const spd = Math.max(0, Math.min(255, Math.round(speed)));
    this.sim.lastActivityAt = Date.now();
    this.sim.lastMotorCmdAt = Date.now();
    this.sim.poc5AutoRunning = false;

    let l = 0;
    let r = 0;
    if (command === 'F') { l = spd; r = spd; }
    else if (command === 'B') { l = -spd; r = -spd; }
    else if (command === 'L') { l = -Math.round(spd * 0.85); r = Math.round(spd * 0.85); }
    else if (command === 'R') { l = Math.round(spd * 0.85); r = -Math.round(spd * 0.85); }

    this.sim.targetMotL = l;
    this.sim.targetMotR = r;
    this.sim.txFrames++;
    this.sim.rxFrames++;

    const asciiFrame = command === 'S' ? '<M,0,0>' : `<M,${l},${r}>`;
    const jsonFrame = JSON.stringify({ type: 'drive', cmd: command, speed: spd });

    if (this.mode === 'simulation') {
      this.sendRaw(jsonFrame);
      return true;
    }

    if (this.protocol === 'poc_ascii') {
      return this.sendRaw(asciiFrame);
    } else if (this.protocol === 'gateway_json') {
      return this.sendRaw(jsonFrame);
    } else {
      this.sendRaw(asciiFrame);
      return this.sendRaw(jsonFrame);
    }
  }

  public sendDifferentialDrive(leftPwm: number, rightPwm: number) {
    const l = Math.max(-255, Math.min(255, Math.round(leftPwm)));
    const r = Math.max(-255, Math.min(255, Math.round(rightPwm)));
    this.sim.lastActivityAt = Date.now();
    this.sim.lastMotorCmdAt = Date.now();
    this.sim.poc5AutoRunning = false;
    this.sim.targetMotL = l;
    this.sim.targetMotR = r;
    this.sim.txFrames++;
    this.sim.rxFrames++;

    return this.sendRaw(`<M,${l},${r}>`);
  }

  public emergencyStop() {
    this.sim.targetMotL = 0;
    this.sim.targetMotR = 0;
    this.sim.motL = 0;
    this.sim.motR = 0;
    this.sim.poc5AutoRunning = false;
    this.sim.txFrames++;
    this.sim.rxFrames++;
    this.sendRaw('<X>');
    this.sendRaw(JSON.stringify({ type: 'drive', cmd: 'S', speed: 0 }));
  }

  public sendConfigParam(cid: number, val: number) {
    this.sim.txFrames++;
    this.sim.rxFrames++;
    if (cid === 1) this.sim.servoSpeedDegS = val;
    if (cid === 2) this.sim.servoFloorDegS = val;
    if (cid === 10) this.sim.rampMs = val;
    if (cid === 14) this.sim.watchdogMs = val;
    this.sendRaw(`<C,${cid},${Math.round(val)}>`);
  }

  public setCameraSleep(sleep: boolean) {
    this.sim.camSleeping = sleep;
    if (!sleep) this.sim.lastActivityAt = Date.now();
    this.sendRaw(JSON.stringify({ type: 'poc_action', action: 'cam_sleep', sleep }));
  }

  public async setCameraPreset(preset: 'frio' | 'equilibrado' | 'qualidade') {
    this.sim.camPreset = preset;
    this.sim.camSleeping = false;
    this.sim.lastActivityAt = Date.now();
    if (preset === 'frio') {
      this.sim.camRes = 'qvga'; this.sim.camXclk = 8; this.sim.camTargetFps = 12;
    } else if (preset === 'equilibrado') {
      this.sim.camRes = 'vga'; this.sim.camXclk = 12; this.sim.camTargetFps = 15;
    } else {
      this.sim.camRes = 'svga'; this.sim.camXclk = 20; this.sim.camTargetFps = 25;
    }
    this.sendRaw(JSON.stringify({ type: 'poc_action', action: 'cam_preset', preset }));
    if (this.mode === 'esp32' && this.httpBaseUrl) {
      try {
        await fetch(`${this.httpBaseUrl}/api/cam/preset?n=${preset}`);
      } catch {}
    }
  }

  public togglePoc5Auto(enable: boolean) {
    this.sim.poc5AutoRunning = enable;
    if (!enable) {
      this.sim.targetMotL = 0;
      this.sim.targetMotR = 0;
    }
    this.sendRaw(JSON.stringify({ type: 'poc_action', action: 'poc5_auto', enable }));
  }

  public resetBatteryMin() {
    this.sim.vminMv = this.sim.vbatMv;
    this.sendRaw(JSON.stringify({ type: 'poc_action', action: 'reset_vmin' }));
  }

  public sendPingFrame(seq: number): number {
    this.sim.txFrames++;
    this.sim.rxFrames++;
    this.sendRaw(`<P,${seq}>`);
    if (this.mode === 'esp32' && this.httpBaseUrl && !this.isConnected()) {
      fetch(`${this.httpBaseUrl}/api/cmd?f=${encodeURIComponent(`<P,${seq}>`)}`).catch(() => {});
    }
    return 12 + Math.floor(Math.random() * 8);
  }

  public onMessage(cb: MessageCallback) {
    this.onMessageCb = cb;
  }

  public onStatus(cb: StatusCallback) {
    this.onStatusCb = cb;
  }

  public isConnected(): boolean {
    if (this.mode === 'simulation') return true;
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public disconnect() {
    this.cleanupSocket();
    clearInterval(this.statsPollTimer);
  }

  private cleanupSocket() {
    clearTimeout(this.reconnectTimer);
    clearInterval(this.pingIntervalTimer);
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onerror = null;
      this.ws.onclose = null;
      try {
        this.ws.close();
      } catch {}
      this.ws = null;
    }
  }
}

export const roverWS = new RoverWebSocketService();
