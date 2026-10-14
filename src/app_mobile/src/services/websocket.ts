type MessageCallback = (data: any) => void;
type StatusCallback = (connected: boolean, pingMs: number) => void;

export class RoverWebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private onMessageCb: MessageCallback | null = null;
  private onStatusCb: StatusCallback | null = null;
  private reconnectTimer: any = null;
  private pingIntervalTimer: any = null;
  private isConnecting: boolean = false;
  private lastPingSentAt: number = 0;
  private pingMs: number = 0;

  constructor() {}

  public connect(ip: string, port: number = 81) {
    this.url = `ws://${ip}:${port}`;
    this.cleanup();
    this.initWebSocket();
  }

  private initWebSocket() {
    if (!this.url) return;
    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnecting = false;
        if (this.onStatusCb) this.onStatusCb(true, this.pingMs);
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
          if (this.onMessageCb) this.onMessageCb(parsed);
        } catch {
          if (this.onMessageCb) this.onMessageCb({ raw: event.data });
        }
      };

      this.ws.onerror = () => {
        if (this.onStatusCb) this.onStatusCb(false, 0);
      };

      this.ws.onclose = () => {
        this.isConnecting = false;
        if (this.onStatusCb) this.onStatusCb(false, 0);
        this.scheduleReconnect();
      };
    } catch (e) {
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
        this.initWebSocket();
      }
    }, 3000);
  }

  public send(data: object | string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const msg = typeof data === 'string' ? data : JSON.stringify(data);
      this.ws.send(msg);
      return true;
    }
    return false;
  }

  public sendServoPanTilt(pan: number, tilt: number) {
    // Protocolo unificado: JSON leve ou texto direto
    return this.send({ type: 'servo', pan: Math.round(pan), tilt: Math.round(tilt) });
  }

  public sendDrive(command: 'F' | 'B' | 'L' | 'R' | 'S', speed: number = 200) {
    return this.send({ type: 'drive', cmd: command, speed: Math.round(speed) });
  }

  public onMessage(cb: MessageCallback) {
    this.onMessageCb = cb;
  }

  public onStatus(cb: StatusCallback) {
    this.onStatusCb = cb;
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public disconnect() {
    this.cleanup();
  }

  private cleanup() {
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
