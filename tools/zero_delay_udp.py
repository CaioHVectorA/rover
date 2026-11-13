#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================================================================
ROVER - INFRA COMPARTILHADA: UDP ZERO-DELAY + RASTREADOR PAN/TILT COM LATENCIA
===================================================================================
1. ZeroDelayUdpReceiver
   - Thread dedicada drena o socket; o loop de IA sempre pega o quadro MAIS RECENTE
     (nenhuma fila => nenhum atraso acumulativo).
   - Se o IP fixo nao responde, tambem faz broadcast de descoberta (o DHCP pode mudar o IP).
   - Forca VGA 640x480 ao conectar. Mostra tela "aguardando Rover" enquanto nao ha video.

2. PanTiltTracker  (substitui o antigo ganho "exponencial", que oscilava)
   Problema do controle anterior: a cada quadro (22 FPS) ele somava um passo proporcional ao erro
   medido numa imagem que ja estava ATRASADA (rede + camera + servo ~ 150-250 ms). O servo ainda
   nao tinha chegado, o erro continuava grande, o passo era somado de novo => overshoot e perda
   do alvo. Agora:
     a) O erro em pixels vira ERRO EM GRAUS (campo de visao do OV5640, ~0,095 grau/px).
     b) Posicao-alvo ABSOLUTA = posicao comandada + erro em graus (nao incremental).
     c) TEMPO MORTO: depois de comandar, ignora as medidas ate o servo chegar
        (latencia + distancia/velocidade) => nunca corrige com imagem velha.
     d) PREDICAO: estima a velocidade angular do alvo e adianta o comando (lead).
     e) VELOCIDADE ADAPTATIVA: a velocidade do servo (3o argumento de <S,pan,tilt,vel>)
        e proporcional ao tamanho do salto: movimento rapido do alvo => servo rapido.
===================================================================================
"""

import os
import json
import base64
import ctypes
import urllib.request
import time
import socket
import struct
import threading
import numpy as np
import cv2

MAGIC = 0x52565231          # 'RVR1'
HEADER_FORMAT = "<IHHHHI"   # 16 bytes
HEADER_SIZE = 16

RESOLUCOES_CAM = {
    "1": ("QVGA 320x240",    b"1"),
    "2": ("CIF 400x296",     b"2"),
    "3": ("VGA 640x480",     b"3"),
    "4": ("SVGA 800x600",    b"4"),
    "5": ("XGA 1024x768",    b"5"),
    "6": ("HD 1280x720",     b"6"),
    "7": ("SXGA 1280x1024",  b"7"),
    "8": ("UXGA 1600x1200",  b"8"),
    "9": ("FHD 1920x1080",   b"9"),
    "0": ("QXGA 2048x1536",  b"0"),
    "k": ("QHD 2560x1440",   b"k"),
    "z": ("QSXGA 2560x1920", b"z"),
}


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ===================================================================================
# RASTREADOR PAN/TILT COM FILTRO DE TREMOR E AMORTECIMENTO MECANICO
# ===================================================================================
class _Axis:
    def __init__(self, pos, lo, hi, sign):
        self.pos = pos            # posicao comandada (graus)
        self.lo, self.hi = lo, hi
        self.sign = sign
        self.vel_est = 0.0        # velocidade angular estimada do alvo (graus/s)
        self.prev_abs = None
        self.prev_t = None
        self.wait_until = 0.0

    def reset_track(self):
        self.vel_est = 0.0
        self.prev_abs = None
        self.prev_t = None

    def update(self, err_px, now, p):
        """Retorna (nova_pos, velocidade_graus_s) ou None se deve manter."""
        if now < self.wait_until:
            return None                       # servo ainda em transito ou assentando: ignora

        err_deg = err_px * p.deg_per_px * self.sign
        target_abs = self.pos + err_deg       # onde o alvo realmente esta (angulo absoluto)

        # Filtro passa-baixas na velocidade angular estimada (suprime ruido de trepidacao)
        if self.prev_t is not None and 0.05 <= now - self.prev_t <= 0.8:
            dt = now - self.prev_t
            v = (target_abs - self.prev_abs) / dt
            # Filtro IIR mais forte para nao amplificar vibracao do chassi/piso
            self.vel_est = 0.70 * self.vel_est + 0.30 * v
        else:
            self.vel_est *= 0.3
        self.prev_abs, self.prev_t = target_abs, now

        # Banda morta: se o erro angular for menor que a tolerancia, nao move o servo!
        # Evita a "caca" (hunting) que gera o tremelique constante no SG90
        if abs(err_deg) < p.deadband_deg:
            return None

        # Supressao de LEAD em baixa velocidade / erros moderados:
        # Derivada numerica em robo trepidante gera saltos violentos artificiais.
        # So injetamos predicao se o erro for relevante e a velocidade real for evidente.
        if abs(err_deg) < 3.5 or abs(self.vel_est) < 12.0:
            lead = 0.0
        else:
            lead = _clamp(self.vel_est * p.latency, -p.max_lead, p.max_lead)

        new = _clamp(self.pos + p.gain * err_deg + lead, self.lo, self.hi)
        real = new - self.pos

        # Se o deslocamento comandado for menor que a folga mecanica do SG90 (~0.4°), ignora
        if abs(real) < 0.45:
            return None

        # Velocidade adaptativa suave:
        # Micro-ajustes usam velocidade baixa (25-45°/s) para nao sacudir a camera.
        # Deslocamentos maiores usam ate 130°/s (teto seguro para nao quebrar horn de plastico).
        speed = _clamp(abs(real) * 4.0 + 20.0, 25.0, 130.0)

        # Tempo morto inclui latencia de transmissao + tempo de curso + margem de assentamento mecanico
        settling_margin = 0.040  # 40 ms para absorver inercia pendular do mastro
        self.wait_until = now + p.latency + abs(real) / speed + settling_margin
        self.pos = new
        return new, speed


class PanTiltTracker:
    def __init__(self, deg_per_px=0.095, gain=0.65, latency=0.15, deadband_deg=2.0,
                 max_lead=8.0, pan_limits=(30.0, 150.0), tilt_limits=(40.0, 140.0),
                 pan_sign=+1, tilt_sign=-1):
        self.deg_per_px = deg_per_px
        self.gain = gain
        self.latency = latency
        self.deadband_deg = deadband_deg
        self.max_lead = max_lead
        self.pan_axis = _Axis(90.0, pan_limits[0], pan_limits[1], pan_sign)
        self.tilt_axis = _Axis(90.0, tilt_limits[0], tilt_limits[1], tilt_sign)
        self.last_send_t = 0.0

    # --- propriedades de conveniencia ---
    @property
    def pan(self):
        return self.pan_axis.pos

    @property
    def tilt(self):
        return self.tilt_axis.pos

    @property
    def pan_sign(self):
        return self.pan_axis.sign

    @pan_sign.setter
    def pan_sign(self, v):
        self.pan_axis.sign = v

    @property
    def tilt_sign(self):
        return self.tilt_axis.sign

    @tilt_sign.setter
    def tilt_sign(self, v):
        self.tilt_axis.sign = v

    def reset_track(self):
        self.pan_axis.reset_track()
        self.tilt_axis.reset_track()

    def set_position(self, pan=None, tilt=None):
        """Posiciona manualmente (varredura de radar, recentralizar...)."""
        if pan is not None:
            self.pan_axis.pos = _clamp(pan, self.pan_axis.lo, self.pan_axis.hi)
            self.pan_axis.wait_until = 0.0
        if tilt is not None:
            self.tilt_axis.pos = _clamp(tilt, self.tilt_axis.lo, self.tilt_axis.hi)
            self.tilt_axis.wait_until = 0.0
        self.reset_track()

    def command(self, vel_deg_s=0.0, now=None):
        """Monta <S,pan10,tilt10,vel10> (decimos de grau, como o Nano espera)."""
        self.last_send_t = now if now is not None else time.time()
        vel10 = int(_clamp(vel_deg_s * 10.0, 0, 6000))
        return f"<S,{int(round(self.pan * 10))},{int(round(self.tilt * 10))},{vel10}>".encode("ascii")

    def update(self, err_x_px, err_y_px, now):
        """Processa uma medida de erro. Retorna bytes do comando ou None."""
        rx = self.pan_axis.update(err_x_px, now, self)
        ry = self.tilt_axis.update(err_y_px, now, self)
        if rx is None and ry is None:
            return None
        speeds = [r[1] for r in (rx, ry) if r is not None]
        return self.command(max(speeds), now)

    def keepalive(self, now, every=1.0):
        """Reenvia a posicao atual (UDP pode perder pacote). Retorna bytes ou None."""
        if now - self.last_send_t >= every:
            return self.command(0.0, now)
        return None

    def settled(self, now):
        return now >= self.pan_axis.wait_until and now >= self.tilt_axis.wait_until


# ===================================================================================
# RECEPTOR UDP ZERO-DELAY
# ===================================================================================
class ZeroDelayUdpReceiver:
    def __init__(self, target_ip="", porta=5005, auto_vga=True, init_cmd=None):
        self.target_ip = target_ip
        self.porta = porta
        if init_cmd is not None:
            self.active_res_cmd = init_cmd
        elif auto_vga:
            self.active_res_cmd = b"3"
        else:
            self.active_res_cmd = None
        self.auto_vga = self.active_res_cmd is not None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
        self.sock.bind(("", porta))
        self.sock.settimeout(0.05)

        self.esp_address = (target_ip, porta) if target_ip else None
        self.lock = threading.Lock()
        self.running = True

        self.latest_jpeg = None
        self.frame_kb = 0.0
        self.new_frame_event = threading.Event()
        self.last_frame_t = 0.0
        self.frames_total = 0

        self.fps = 0.0
        self.mbps = 0.0
        self.drop_pct = 0.0
        self.rtt_ms = 0.0
        self.last_ping_t = 0
        self.ping_in_flight = False

        self.thread = threading.Thread(target=self._worker, daemon=True, name="UDP-Drainer")
        self.thread.start()

    def _hello(self, broadcast):
        if self.target_ip:
            try:
                self.sock.sendto(b"HELLO", (self.target_ip, self.porta))
            except Exception:
                pass
        if broadcast or not self.target_ip:
            for bcast in ["255.255.255.255", "192.168.7.255", "<broadcast>"]:
                try:
                    self.sock.sendto(b"HELLO", (bcast, self.porta))
                except Exception:
                    pass

    def _worker(self):
        last_hello = 0
        chunks = {}
        curr_f_id = None
        tot_chunks = 0
        bytes_sec = frames_sec = dropped_sec = 0
        stat_t = time.time()
        config_enviada = False

        while self.running:
            now = time.time()

            if now - last_hello > 2.0:
                # sem video ha mais de 3 s => tambem varre a rede por broadcast
                sem_video = (now - self.last_frame_t) > 3.0
                self._hello(broadcast=sem_video)
                last_hello = now

            if self.esp_address and now - self.last_ping_t > 1.5 and not self.ping_in_flight:
                try:
                    self.sock.sendto(b"P" + struct.pack("<d", now), self.esp_address)
                    self.ping_in_flight = True
                    self.last_ping_t = now
                except Exception:
                    pass
            if self.ping_in_flight and now - self.last_ping_t > 3.0:
                self.ping_in_flight = False

            try:
                data, addr = self.sock.recvfrom(2048)

                # O broadcast de descoberta volta para o proprio socket: ignora eco proprio.
                if data.startswith(b"HELLO"):
                    continue

                eh_rover = data.startswith(b"READY") or (
                    len(data) >= HEADER_SIZE and struct.unpack("<I", data[:4])[0] == MAGIC)
                if not eh_rover and not (data.startswith(b"P") and len(data) == 9):
                    continue

                if eh_rover and (self.esp_address is None or self.esp_address[0] != addr[0]):
                    self.esp_address = addr
                    print(f"\n[CONEXAO] ESP32-S3 detectado em {addr[0]}:{addr[1]}")
                    config_enviada = False

                if self.active_res_cmd and not config_enviada and self.esp_address:
                    try:
                        self.sock.sendto(self.active_res_cmd, self.esp_address)
                        config_enviada = True
                        print(f"[CONEXAO] Resolucao inicial ({self.active_res_cmd.decode()}) sincronizada com o Rover.")
                    except Exception:
                        pass

                if data.startswith(b"P") and len(data) == 9:
                    sent_ts = struct.unpack("<d", data[1:9])[0]
                    self.rtt_ms = (now - sent_ts) * 1000.0
                    self.ping_in_flight = False
                    continue

                if len(data) < HEADER_SIZE:
                    continue

                magic, f_id, c_id, total, p_len, _ = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
                if magic != MAGIC:
                    continue

                bytes_sec += len(data)
                payload = data[HEADER_SIZE: HEADER_SIZE + p_len]

                if f_id != curr_f_id:
                    if curr_f_id is not None and len(chunks) < tot_chunks:
                        dropped_sec += 1
                    curr_f_id = f_id
                    chunks.clear()
                    tot_chunks = total

                chunks[c_id] = payload

                if len(chunks) == tot_chunks and tot_chunks > 0:
                    jpeg = bytearray()
                    for idx in range(tot_chunks):
                        if idx in chunks:
                            jpeg.extend(chunks[idx])
                    frames_sec += 1
                    with self.lock:
                        self.latest_jpeg = jpeg          # sobrescreve: Zero-Buffer
                        self.frame_kb = len(jpeg) / 1024.0
                        self.last_frame_t = time.time()
                        self.frames_total += 1
                    self.new_frame_event.set()
                    chunks.clear()
                    curr_f_id = None

            except socket.timeout:
                pass
            except Exception:
                pass

            dt = now - stat_t
            if dt >= 1.0:
                self.fps = frames_sec / dt
                self.mbps = (bytes_sec * 8.0) / (dt * 1e6)
                tot = frames_sec + dropped_sec
                self.drop_pct = (dropped_sec * 100.0 / tot) if tot > 0 else 0.0
                bytes_sec = frames_sec = dropped_sec = 0
                stat_t = now

    def get_frame(self, timeout=0.1):
        """(img, fps, mbps, drop_pct, rtt_ms). img=None se nao chegou quadro novo."""
        if not self.new_frame_event.wait(timeout=timeout):
            return None, self.fps, self.mbps, self.drop_pct, self.rtt_ms
        with self.lock:
            jpeg = self.latest_jpeg
            self.new_frame_event.clear()
        if jpeg is None:
            return None, self.fps, self.mbps, self.drop_pct, self.rtt_ms
        img = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)
        return img, self.fps, self.mbps, self.drop_pct, self.rtt_ms

    def send_cmd(self, cmd_bytes):
        if self.esp_address and cmd_bytes:
            try:
                self.sock.sendto(cmd_bytes, self.esp_address)
            except Exception:
                pass

    def set_resolution_cmd(self, cmd_bytes):
        """Envia comando de resolucao e memoriza caso haja reconexao."""
        self.active_res_cmd = cmd_bytes
        self.send_cmd(cmd_bytes)

    def draw_waiting(self, window_name, canvas_w, canvas_h):
        """Tela de espera (a janela nunca fica preta/travada sem explicacao)."""
        if time.time() - self.last_frame_t < 0.6 and self.frames_total > 0:
            return
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        alvo = self.esp_address[0] if self.esp_address else (self.target_ip or "broadcast")
        linhas = [
            ("AGUARDANDO VIDEO DO ROVER...", 1.0, (0, 220, 255)),
            (f"Alvo: {alvo}:{self.porta}  |  descoberta por broadcast ativa", 0.6, (200, 200, 200)),
            ("Verifique: ESP32 ligado, mesma rede Wi-Fi, firmware poc_udp_camera gravado.", 0.55, (160, 160, 160)),
            ("[Q] Sair", 0.5, (160, 160, 160)),
        ]
        y = canvas_h // 2 - 40
        for txt, esc, cor in linhas:
            (tw, _), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, esc, 2)
            cv2.putText(canvas, txt, ((canvas_w - tw) // 2, y), cv2.FONT_HERSHEY_SIMPLEX, esc, cor, 2)
            y += 42
        cv2.imshow(window_name, canvas)

    def close(self):
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass


# ===================================================================================
# HELPERS COMPARTILHADOS DE CANVAS, TELA E CO-PILOTO GEMINI FLASH
# ===================================================================================
def get_screen_size():
    """Retorna (largura, altura) do monitor principal sem estourar fora do Windows."""
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080


def render_to_canvas(img, canvas_w, canvas_h):
    """Encaixa `img` no canvas mantendo proporcao original com interpolacao otima."""
    h, w = img.shape[:2]
    scale = min(canvas_w / w, canvas_h / h)
    new_w, new_h = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    # INTER_AREA evita serrilhado ao reduzir imagens 2MP/5MP para o monitor
    interp = cv2.INTER_AREA if scale < 0.95 else cv2.INTER_LINEAR
    scaled = cv2.resize(img, (new_w, new_h), interpolation=interp)
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    ox = (canvas_w - new_w) // 2
    oy = (canvas_h - new_h) // 2
    canvas[oy : oy + new_h, ox : ox + new_w] = scaled
    return canvas


def draw_bottom_banner(canvas, texto, prefix="", bg_color=(20, 20, 26), text_color=(0, 240, 255), font_scale=0.50):
    """Desenha banner inferior com quebra automatica de linha para caber na largura do canvas."""
    if not texto:
        return
    ch, cw = canvas.shape[:2]
    full_txt = f"{prefix}{texto}" if prefix else texto
    max_w = max(200, cw - 40)
    words = full_txt.split(" ")
    lines, cur = [], ""
    for word in words:
        cand = f"{cur} {word}".strip() if cur else word
        (tw, _), _ = cv2.getTextSize(cand, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
        if tw <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    lines = lines[:3]

    line_h = 24
    bar_h = 18 + len(lines) * line_h
    y0 = max(0, ch - bar_h)
    cv2.rectangle(canvas, (0, y0), (cw, ch), bg_color, -1)
    for i, ln in enumerate(lines):
        cv2.putText(canvas, ln, (20, y0 + 22 + i * line_h),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 1, cv2.LINE_AA)


def carregar_env():
    """Carrega variaveis chave=valor do arquivo .env na raiz do projeto."""
    env_vars = {}
    caminho_env = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(caminho_env):
        with open(caminho_env, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    k, v = linha.split("=", 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars


class GeminiVisionClient:
    """Cliente assincrono multimodal Gemini para consulta de imagem sem bloquear o loop de video."""

    def __init__(self, prompt, tag="GEMINI", default_text=""):
        env = carregar_env()
        self.api_key = env.get("GEMINI_API_KEY", "")
        self.model = env.get("GEMINI_MODEL", "gemini-3.5-flash")
        self.prompt = prompt
        self.tag = tag
        self.ocupado = False
        self.texto_hud = default_text
        self.t_resposta = 0.0

    def _worker(self, img_cv):
        try:
            h, w = img_cv.shape[:2]
            fator = min(1.0, 480.0 / max(h, w))
            if fator < 1.0:
                img_peq = cv2.resize(img_cv, (int(w * fator), int(h * fator)), interpolation=cv2.INTER_AREA)
            else:
                img_peq = img_cv
            _, buffer = cv2.imencode(".jpg", img_peq, [cv2.IMWRITE_JPEG_QUALITY, 72])
            b64_image = base64.b64encode(buffer).decode("utf-8")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": self.prompt},
                        {"inlineData": {"mimeType": "image/jpeg", "data": b64_image}},
                    ]
                }]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                texto = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                self.texto_hud = texto
                self.t_resposta = time.time()
                print(f"\n[{self.tag}]: {texto}\n")
        except Exception as e:
            self.texto_hud = f"Erro Gemini: {e}"
            self.t_resposta = time.time()
            print(f"\n[{self.tag} ERRO]: {e}\n")
        finally:
            self.ocupado = False

    def disparar(self, img_cv):
        """Dispara consulta em thread de fundo e retorna True se iniciada."""
        if img_cv is None:
            return False
        if self.ocupado:
            print(f"[{self.tag}] Consulta ja em andamento...")
            return False
        if not self.api_key:
            self.texto_hud = "Chave GEMINI_API_KEY nao configurada no .env"
            self.t_resposta = time.time()
            print(f"[{self.tag}]: {self.texto_hud}")
            return False
        self.ocupado = True
        self.texto_hud = f"Consultando {self.model} em segundo plano..."
        self.t_resposta = time.time()
        print(f"\n[{self.tag}] Disparando analise visual ({self.model})...")
        threading.Thread(target=self._worker, args=(img_cv.copy(),), daemon=True).start()
        return True
