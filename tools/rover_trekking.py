#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================================================================
ROVER TREKKING AUTONOMOUS MISSION CONTROL - ZERO-DELAY UDP + YOLOv8 + GEMINI
===================================================================================
Estudo de caso para Robótica de Trekking e Desafio de Cones / Garrafas:
  1. ZERO-DELAY UDP: Drena socket sem atrasos acumulados, forçando resolução VGA.
  2. MODO RADAR (Varredura Ativa com o Pan/Tilt de 40° a 140° buscando o alvo)
  3. LOCK & ATTACK (Alinhamento do chassi e avanço tático com rampa de velocidade)
  4. CONTROLE ADAPTATIVO NÃO-LINEAR: Rastreamento ágil do obstáculo
  5. SCAN DE BORDA & DESVIO (Contorno do obstáculo sem colisão)
  6. IA MULTIMODAL COGNITIVA (Gemini 3.5 Flash descreve o trajeto ao apertar ESPAÇO)

Controles:
  [ESPACO] Aciona Consulta Cognitiva (Gemini 3.5 Flash)
  [M] Alterna Modo Autonomo ON / Standby (Parada de Emergencia)
  [A] Alternar classe alvo (Garrafa / Pessoa / Copo)
  [F] Alternar Tela Cheia / Janela
  [Q] Encerrar
===================================================================================
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import argparse
import ctypes
import json
import urllib.request
import numpy as np
import cv2

from zero_delay_udp import (
    ZeroDelayUdpReceiver, PanTiltTracker, RESOLUCOES_CAM,
    get_screen_size, render_to_canvas, draw_bottom_banner, GeminiVisionClient
)

GEMINI_PROMPT_TREKKING = (
    "Você é o co-piloto cognitivo do Rover móvel 4WD na pista de trekking. "
    "Analise esta imagem frontal da câmera e responda em 2 frases curtas e diretas em português: "
    "1. Quais obstáculos, garrafas ou copos estão visíveis e a sua posição relativa. "
    "2. O caminho livre sugerido para contornar ou avançar com segurança."
)

# Classes COCO (80 classes)
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]

# Estados da Missao Trekking
ESTADO_STANDBY       = 0  # Parado / Manual
ESTADO_RADAR_SCAN    = 1  # Varrendo o horizonte com o Pan/Tilt (chassi parado)
ESTADO_TARGET_LOCKED = 2  # Achou: centraliza a garrafa no quadro usando so a cabeca
ESTADO_ALIGN         = 3  # Gira o chassi ate ficar de frente para o alvo
ESTADO_APPROACH      = 4  # Avanca ate a distancia de rodeio
ESTADO_ORBIT         = 5  # Rodeio: contorna o alvo mantendo distancia, olhando para ele
ESTADO_AVOID_ORBIT   = ESTADO_ORBIT

ESTADOS_NOMES = {
    ESTADO_RADAR_SCAN:    "1. RADAR: VARRENDO (CHASSI PARADO)",
    ESTADO_TARGET_LOCKED: "2. ALVO ACHADO: CENTRALIZANDO COM A CABECA",
    ESTADO_ALIGN:         "3. ALINHANDO O CHASSI COM O ALVO",
    ESTADO_APPROACH:      "4. APROXIMANDO ATE A DISTANCIA DE RODEIO",
    ESTADO_ORBIT:         "5. RODEIO (CONTORNANDO O ALVO)",
    ESTADO_STANDBY:       "STANDBY (MOTORES DESLIGADOS)"
}

# Parametros da manobra (ajuste na pista)
DIST_RODEIO_CM   = 45.0    # raio do rodeio
DIST_INICIO_CM   = 60.0    # abaixo disso a aproximacao termina e comeca o rodeio
DIST_EMERGENCIA  = 22.0    # abaixo disso: para (nunca encosta)
ORBIT_SEGUNDOS   = 14.0    # duracao do rodeio (sem IMU nao ha como medir a volta completa)
ORBIT_BEARING    = -45.0   # alvo mantido a 45 graus a ESQUERDA do eixo do chassi (+ = direita)


# ===================================================================================
# DETECTOR YOLOV8n NATIVO COM LETTERBOX E DETECCAO ESPECIFICA POR CLASSE
# ===================================================================================
def _letterbox(img, new_shape=(640, 640), color=(114, 114, 114)):
    """Mantem a proporcao geometrica exata sem esticar a imagem (evita deformar garrafas)."""
    shape = img.shape[:2]  # [h, w]
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
    dw = (new_shape[1] - new_unpad[0]) / 2.0
    dh = (new_shape[0] - new_unpad[1]) / 2.0
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    resized = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return padded, r, (dw, dh)


class YoloV8Detector:
    def __init__(self, model_path="tools/models/yolov8n.onnx", conf_thresh=0.28, nms_thresh=0.45):
        self.conf_thresh = conf_thresh
        self.nms_thresh = nms_thresh
        self.net = None
        if os.path.exists(model_path):
            try:
                self.net = cv2.dnn.readNet(model_path)
                print(f"[YOLOv8] Modelo neural carregado com sucesso: {model_path}")
            except Exception as e:
                print(f"[ERRO] Falha ao ler YOLOv8: {e}")

    def detect(self, img, target_class="bottle", min_conf=None):
        if self.net is None:
            return []

        h, w, _ = img.shape
        padded, r, (dw, dh) = _letterbox(img, (640, 640))
        blob = cv2.dnn.blobFromImage(padded, 1.0 / 255.0, (640, 640), swapRB=True)
        self.net.setInput(blob)
        preds = self.net.forward()

        # Saida do YOLOv8: [1, 84, 8400] -> transpor para [8400, 84]
        preds = np.squeeze(preds, axis=0).T

        boxes = []
        confidences = []
        class_ids = []

        limiar = min_conf if min_conf is not None else self.conf_thresh
        target_is_all = (target_class == "all")
        target_is_bottle = (target_class == "bottle")

        # Sub-indices aceitos para "bottle" em pista (recipientes cilíndricos comumente confundidos)
        SUB_BOTTLE = [39, 41, 40, 75]  # bottle, cup, wine glass, vase

        for pred in preds:
            cx, cy, bw, bh = pred[:4]
            scores = pred[4:]

            if target_is_all:
                cid = int(np.argmax(scores))
                sc = float(scores[cid])
                cname = COCO_CLASSES[cid] if cid < len(COCO_CLASSES) else "unknown"
            elif target_is_bottle:
                # Avalia o melhor score entre as classes do grupo garrafa/copo
                sub_sc = [scores[idx] for idx in SUB_BOTTLE]
                best_sub = int(np.argmax(sub_sc))
                cid = SUB_BOTTLE[best_sub]
                sc = float(sub_sc[best_sub])
                cname = COCO_CLASSES[cid]
            else:
                if target_class in COCO_CLASSES:
                    cid = COCO_CLASSES.index(target_class)
                    sc = float(scores[cid])
                    cname = target_class
                else:
                    cid = int(np.argmax(scores))
                    sc = float(scores[cid])
                    cname = COCO_CLASSES[cid] if cid < len(COCO_CLASSES) else "unknown"

            if sc >= limiar:
                # Reverte coordenadas do espaco letterbox para a imagem original
                orig_cx = (cx - dw) / r
                orig_cy = (cy - dh) / r
                orig_w = bw / r
                orig_h = bh / r

                bx = int(max(0, orig_cx - orig_w / 2.0))
                by = int(max(0, orig_cy - orig_h / 2.0))
                bw_box = int(min(w - bx, orig_w))
                bh_box = int(min(h - by, orig_h))

                if bw_box > 8 and bh_box > 8:
                    boxes.append([bx, by, bw_box, bh_box])
                    confidences.append(sc)
                    class_ids.append(cid)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, limiar, self.nms_thresh)

        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                results.append({
                    "box": boxes[i],
                    "conf": confidences[i],
                    "class_name": COCO_CLASSES[class_ids[i]] if class_ids[i] < len(COCO_CLASSES) else "unknown"
                })
        return results

    def detect_all(self, img, min_conf=0.20):
        """Retorna todos os objetos detectados para o modo de Debug visual [D]."""
        if self.net is None:
            return []
        return self.detect(img, target_class="all", min_conf=min_conf)


# ===================================================================================
# RAMPA DE PWM 4WD (SLEW RATE LIMITER - PREVENCAO DE TRANCO MECANICO)
# ===================================================================================
class MotorRamp:
    def __init__(self, max_delta=12):
        self.cur_left = 0.0
        self.cur_right = 0.0
        self.max_delta = float(max_delta)  # variacao maxima de PWM por tick

    def update(self, target_left, target_right):
        dl = float(target_left) - self.cur_left
        if abs(dl) <= self.max_delta:
            self.cur_left = float(target_left)
        else:
            self.cur_left += self.max_delta if dl > 0 else -self.max_delta

        dr = float(target_right) - self.cur_right
        if abs(dr) <= self.max_delta:
            self.cur_right = float(target_right)
        else:
            self.cur_right += self.max_delta if dr > 0 else -self.max_delta

        return int(round(self.cur_left)), int(round(self.cur_right))

    def reset(self):
        self.cur_left = 0.0
        self.cur_right = 0.0


def desenhar_hud_trekking(canvas, estado, pan, tilt, dist_cm, fps, mbps, alvo_nome, ai_texto, autonomo,
                          coasting=False, debug_mode=False, conf_limiar=0.28, res_label="VGA 640x480",
                          gemini_ocupado=False):
    ch, cw, _ = canvas.shape

    # 1. Barra Superior Tática Otimizada (ROI Blending - 91% menos CPU)
    bar_h = 95
    if ch > bar_h:
        roi = canvas[0:bar_h, 0:cw]
        overlay = np.full_like(roi, (16, 16, 18))
        cv2.addWeighted(overlay, 0.85, roi, 0.15, 0, roi)

    if coasting:
        cor_estado = (0, 210, 255)
        sufixo = " [FILTRO ANTI-VIBRACAO ATIVO]"
    else:
        cor_estado = (0, 255, 128) if autonomo else (0, 180, 255)
        sufixo = ""

    t1 = f"TREKKING MISSAO: {ESTADOS_NOMES[estado]}{sufixo} | MODO: {'AUTONOMO (4WD)' if autonomo else 'STANDBY'}"
    cv2.putText(canvas, t1, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, cor_estado, 2, cv2.LINE_AA)

    dist_txt = f"{dist_cm:.0f} cm" if dist_cm is not None else "-- cm"
    dbg_str = "DEBUG: ON" if debug_mode else "DEBUG: OFF"
    t2 = (f"FPS: {fps:.1f} | Banda: {mbps:.2f} Mbps | Res: {res_label} | Alvo: [{alvo_nome.upper()}] | "
          f"Sens: {conf_limiar*100:.0f}% | Dist: {dist_txt} | Pan: {pan:.0f}* Tilt: {tilt:.0f}* | {dbg_str}")
    cv2.putText(canvas, t2, (20, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (240, 240, 240), 1, cv2.LINE_AA)

    t3 = "[M] Autonomo | [A/O] Alvo | [D] Debug | [ [/] ] Sensib | [1..9,0,K,Z] Res | [+/-] Q | [ESPACO/G] Gemini | [Q] Sair"
    cv2.putText(canvas, t3, (20, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (185, 185, 185), 1, cv2.LINE_AA)

    # 2. Mostrador de Radar Pan/Tilt (Canto Superior Direito)
    rx, ry, rr = cw - 70, 50, 36
    cv2.circle(canvas, (rx, ry), rr, (35, 35, 35), -1)
    cv2.circle(canvas, (rx, ry), rr, (0, 220, 120), 1)
    ang_rad = np.radians(180.0 - pan)
    px = int(rx + (rr - 4) * np.cos(ang_rad))
    py = int(ry - (rr - 4) * np.sin(ang_rad))
    cv2.line(canvas, (rx, ry), (px, py), (0, 255, 128), 2)
    cv2.putText(canvas, f"{pan:.0f}*", (rx - 15, ry + rr + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

    # 3. Barra Vertical de Proximidade (Lado Esquerdo)
    bx, by, bw, bh = 20, 120, 18, ch - 220
    cv2.rectangle(canvas, (bx, by), (bx + bw, by + bh), (40, 40, 40), -1)
    cv2.rectangle(canvas, (bx, by), (bx + bw, by + bh), (120, 120, 120), 1)

    if dist_cm is not None:
        norm_dist = max(0.0, min(1.0, (dist_cm - 15.0) / 150.0))
        fill_h = int((1.0 - norm_dist) * bh)
        cor_prox = (0, 255, 128) if dist_cm > 60 else ((0, 180, 255) if dist_cm > 30 else (60, 60, 255))
        cv2.rectangle(canvas, (bx, by + bh - fill_h), (bx + bw, by + bh), cor_prox, -1)
        cv2.putText(canvas, f"{dist_cm:.0f}cm", (bx + bw + 8, by + bh - fill_h + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.48, cor_prox, 2)

    # 4. Banner Inferior de Cognição Gemini com quebra de linha
    if ai_texto:
        cor_bg = (0, 120, 200) if gemini_ocupado else (16, 16, 20)
        draw_bottom_banner(canvas, ai_texto, prefix="[GEMINI FLASH]: ", bg_color=cor_bg)


def main():
    sys.stdout.reconfigure(line_buffering=True)
    parser = argparse.ArgumentParser(description="Rover Trekking Autonomous Mission Control")
    parser.add_argument("--ip", type=str, default="", help="IP do ESP32 (vazio = descoberta automatica)")
    parser.add_argument("--porta", type=int, default=5005)
    args = parser.parse_args()

    porta = args.porta
    target_ip = args.ip
    screen_w, screen_h = get_screen_size()

    gemini = GeminiVisionClient(
        GEMINI_PROMPT_TREKKING,
        tag="GEMINI RESPOSTA",
        default_text="Pressione [ESPACO] ou [G] para o Gemini descrever a trilha.",
    )
    receiver = ZeroDelayUdpReceiver(target_ip=target_ip, porta=porta, auto_vga=True)

    print("=" * 70)
    print("   ROVER TREKKING AUTONOMOUS MISSION CONTROL (ZERO-DELAY UDP)")
    print("=" * 70)
    print(f"Ouvindo na porta UDP: {porta}")
    print(f"Alvo ESP32: {target_ip}")
    print("Modos:")
    print("  [M] Ligar/Pausar Modo Autonomo (Start/Stop)")
    print("  [A] Alternar Alvo (bottle / person / cup)")
    print("  [ESPACO] Consultar Gemini 3.5 Flash")
    print("  [F] Tela Cheia  |  [Q] Sair")
    print("=" * 70)

    yolo = YoloV8Detector("tools/models/yolov8n.onnx")

    # Tracker Pan/Tilt com amortecimento macio contra tremelique de servos SG90
    tracker = PanTiltTracker(gain=0.60, deadband_deg=2.2, max_lead=6.0, pan_limits=(35.0, 145.0))
    motor_ramp = MotorRamp(max_delta=10)  # Rampa suave de PWM (10 PWM/tick -> ~350ms para cruzeiro)

    # Parametros do Filtro de Rastreamento Sensivel com Letterbox (Histerese + Coasting Temporal)
    CONF_AQUISICAO = 0.28      # Confianca sensivel para adquirir novo alvo (evita perder garrafas)
    CONF_TRACKING  = 0.18      # Confianca minima para reter alvo sob movimento
    MAX_COAST_FRAMES = 8       # Sustenta ate 8 quadros (~350ms) se o alvo sumir por tremor/blur

    # Lista expandida de alvos favoritos para o Trekking
    alvos_disponiveis = [
        "bottle",        # Garrafa / Recipientes de bebida (inclui copo/lata)
        "cup",           # Copo descartavel ou latinha
        "person",        # Pessoa / Piloto
        "chair",         # Cadeira / Obstaculo de solo
        "sports ball",   # Bola
        "backpack",      # Mochila / Obstaculo volumoso
        "cell phone",    # Celular
        "potted plant",  # Vaso de planta
        "all"            # Modo Universal: detecta qualquer um dos 80 objetos COCO
    ]
    alvo_idx = 0
    alvo_atual = alvos_disponiveis[alvo_idx]

    res_atual_label = "VGA 640x480"
    debug_mode = False

    estado_missao = ESTADO_STANDBY
    autonomo = False
    radar_sentido = 1.0
    radar_vel_deg_s = 35.0
    t_ultimo_alvo = 0.0
    t_centrado_desde = None
    t_orbit_ini = 0.0
    t_prev = time.time()
    t_aviso_perto = 0.0

    # Variaveis de rastreamento com filtro passa-baixas (EMA)
    alvo_em_tracking = False
    frames_sem_alvo = 0
    tcx_filtrado = None
    tcy_filtrado = None
    dist_filtrada = None
    dist_estimada_cm = None

    target_pwm_esq = 0
    target_pwm_dir = 0

    last_motor_cmd_t = 0
    last_scan_cmd_t = 0

    window_name = "Rover Trekking Mission Control"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    is_fullscreen = True

    try:
        while True:
            now = time.time()
            img, fps, mbps, drop_pct, rtt_ms = receiver.get_frame(timeout=0.05)

            if img is not None:
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                h, w, _ = img.shape
                cx, cy = w // 2, h // 2

                # -------------------------------------------------------------
                # MODO DEBUG VISUAL: Exibe todos os objetos reconhecidos na cena
                # -------------------------------------------------------------
                if debug_mode:
                    todos_objs = yolo.detect_all(img, min_conf=0.18)
                    for d in todos_objs:
                        dbx, dby, dbw, dbh = d["box"]
                        dcname = d["class_name"]
                        dconf = d["conf"]
                        cv2.rectangle(img, (dbx, dby), (dbx + dbw, dby + dbh), (80, 180, 240), 1)
                        cv2.putText(img, f"{dcname} {dconf*100:.0f}%", (dbx, max(12, dby - 4)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (80, 180, 240), 1)

                # -------------------------------------------------------------
                # INFERÊNCIA YOLOV8 COM LETTERBOX, HISTERESE E FILTRO ANTI-VIBRACAO
                # -------------------------------------------------------------
                limiar_conf = CONF_TRACKING if alvo_em_tracking else CONF_AQUISICAO
                detections = yolo.detect(img, target_class=alvo_atual, min_conf=limiar_conf)
                deteccao_frame = len(detections) > 0

                alvo_valido = False
                alvo_coasting = False
                tcx, tcy = cx, cy

                if deteccao_frame:
                    best_target = max(detections, key=lambda d: d["box"][2] * d["box"][3])
                    bx, by, bw, bh = best_target["box"]
                    conf = best_target["conf"]
                    cname_det = best_target["class_name"]
                    raw_tcx = bx + bw // 2
                    raw_tcy = by + bh // 2

                    focal_pixels = 520.0
                    raw_dist = (22.0 * focal_pixels) / max(1, bh)
                    raw_dist = max(10.0, min(250.0, raw_dist))

                    # Filtro EMA nas coordenadas e distancia
                    if tcx_filtrado is None:
                        tcx_filtrado = float(raw_tcx)
                        tcy_filtrado = float(raw_tcy)
                        dist_filtrada = float(raw_dist)
                    else:
                        tcx_filtrado = 0.65 * tcx_filtrado + 0.35 * float(raw_tcx)
                        tcy_filtrado = 0.65 * tcy_filtrado + 0.35 * float(raw_tcy)
                        dist_filtrada = 0.70 * dist_filtrada + 0.30 * float(raw_dist)

                    tcx = int(round(tcx_filtrado))
                    tcy = int(round(tcy_filtrado))
                    dist_estimada_cm = dist_filtrada

                    frames_sem_alvo = 0
                    alvo_em_tracking = True
                    alvo_valido = True
                    t_ultimo_alvo = now

                    cor_alvo = (0, 255, 128) if dist_estimada_cm > 40 else (0, 160, 255)
                    if dist_estimada_cm <= 25:
                        cor_alvo = (60, 60, 255)

                    cv2.rectangle(img, (bx, by), (bx + bw, by + bh), cor_alvo, 2)
                    cv2.drawMarker(img, (tcx, tcy), cor_alvo, cv2.MARKER_CROSS, 22, 2)
                    cv2.line(img, (cx, cy), (tcx, tcy), (80, 80, 255), 1)

                    rotulo_alvo = f"{cname_det.upper()} ({conf*100:.0f}%) | {dist_estimada_cm:.0f}cm"
                    cv2.putText(img, rotulo_alvo, (bx, max(20, by - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, cor_alvo, 2)

                else:
                    frames_sem_alvo += 1
                    # Tolerancia temporal: mantem rastreamento ativo em caso de dropout momentaneo por tremor
                    if alvo_em_tracking and frames_sem_alvo <= MAX_COAST_FRAMES and tcx_filtrado is not None:
                        alvo_valido = True
                        alvo_coasting = True
                        tcx = int(round(tcx_filtrado))
                        tcy = int(round(tcy_filtrado))
                        dist_estimada_cm = dist_filtrada

                        # Indicador visual de coasting anti-vibracao
                        cv2.drawMarker(img, (tcx, tcy), (0, 210, 255), cv2.MARKER_CROSS, 22, 1)
                        cv2.circle(img, (tcx, tcy), 25, (0, 210, 255), 1)
                        cv2.putText(img, f"[COAST {frames_sem_alvo}/{MAX_COAST_FRAMES}]", (tcx - 40, tcy - 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 210, 255), 1)
                    else:
                        alvo_em_tracking = False
                        alvo_valido = False

                # -------------------------------------------------------------
                # MAQUINA DE ESTADOS: RADAR -> CENTRALIZAR -> ALINHAR -> APROXIMAR -> RODEIO
                # -------------------------------------------------------------
                dt_loop = max(0.001, min(0.2, now - t_prev))
                t_prev = now
                target_pwm_esq = 0
                target_pwm_dir = 0
                cmd_servo = None
                bearing = (tracker.pan - 90.0) * tracker.pan_sign

                if not autonomo:
                    estado_missao = ESTADO_STANDBY
                    tracker.reset_track()
                    motor_ramp.reset()
                    t_centrado_desde = None
                    if alvo_valido:
                        cmd_servo = tracker.update(tcx - cx, tcy - cy, now)
                else:
                    if alvo_valido:
                        if estado_missao in (ESTADO_STANDBY, ESTADO_RADAR_SCAN):
                            estado_missao = ESTADO_TARGET_LOCKED
                            tracker.reset_track()
                            t_centrado_desde = None
                            print(f"[TREKKING] Alvo [{alvo_atual}] localizado -> centralizando com amortecimento")

                        err_x = tcx - cx
                        err_y = tcy - cy
                        cmd_servo = tracker.update(err_x, err_y, now)

                        if dist_estimada_cm is not None and dist_estimada_cm <= DIST_EMERGENCIA and estado_missao in (ESTADO_ALIGN, ESTADO_APPROACH, ESTADO_ORBIT):
                            target_pwm_esq = 0
                            target_pwm_dir = 0
                            if now - t_aviso_perto > 2.0:
                                print("[TREKKING] Distancia de emergencia: parada suave")
                                t_aviso_perto = now

                        elif estado_missao == ESTADO_TARGET_LOCKED:
                            centrado = abs(err_x) <= 28 and abs(err_y) <= 45
                            if centrado:
                                if t_centrado_desde is None:
                                    t_centrado_desde = now
                                elif now - t_centrado_desde >= 0.4 and tracker.settled(now):
                                    estado_missao = ESTADO_ALIGN
                                    print("[TREKKING] Cabeca centralizada -> alinhando chassi")
                            else:
                                t_centrado_desde = None

                        elif estado_missao == ESTADO_ALIGN:
                            if abs(bearing) > 8.0:
                                pwm = int(max(40, min(70, 35 + abs(bearing) * 0.6)))
                                if bearing > 0:
                                    target_pwm_esq, target_pwm_dir = pwm, -pwm
                                else:
                                    target_pwm_esq, target_pwm_dir = -pwm, pwm
                            else:
                                estado_missao = ESTADO_APPROACH
                                print("[TREKKING] Chassi alinhado -> aproximando com rampa suave")

                        elif estado_missao == ESTADO_APPROACH:
                            if abs(bearing) > 25.0:
                                estado_missao = ESTADO_ALIGN
                            elif dist_estimada_cm is not None and dist_estimada_cm > DIST_INICIO_CM:
                                ajuste = max(-25, min(25, bearing * 0.7))
                                target_pwm_esq = int(75 + ajuste)
                                target_pwm_dir = int(75 - ajuste)
                            else:
                                estado_missao = ESTADO_ORBIT
                                t_orbit_ini = now
                                print("[TREKKING] Distancia de rodeio atingida -> contornando obstaculo")

                        elif estado_missao == ESTADO_ORBIT:
                            if now - t_orbit_ini > ORBIT_SEGUNDOS:
                                autonomo = False
                                estado_missao = ESTADO_STANDBY
                                target_pwm_esq, target_pwm_dir = 0, 0
                                print("[TREKKING] Manobra de rodeio concluida -> STANDBY")
                            else:
                                dist_ref = dist_estimada_cm if dist_estimada_cm is not None else DIST_RODEIO_CM
                                steer = 0.9 * (bearing - ORBIT_BEARING) + 1.2 * (DIST_RODEIO_CM - dist_ref)
                                steer = max(-40.0, min(40.0, steer))
                                target_pwm_esq = int(65 + steer)
                                target_pwm_dir = int(65 - steer)

                    else:
                        # Alvo nao detectado nem em coasting
                        target_pwm_esq = 0
                        target_pwm_dir = 0

                        if now - t_ultimo_alvo > 0.6:
                            if estado_missao != ESTADO_RADAR_SCAN:
                                print(f"[TREKKING] Alvo [{alvo_atual}] fora da mira -> iniciando Busca Ativa")
                            estado_missao = ESTADO_RADAR_SCAN
                            dist_estimada_cm = None
                            t_centrado_desde = None
                            tcx_filtrado = None
                            tcy_filtrado = None
                            dist_filtrada = None
                            tracker.reset_track()

                            # Varredura Pan/Tilt de 40 a 140 graus
                            pan_novo = tracker.pan + radar_sentido * radar_vel_deg_s * dt_loop
                            if pan_novo >= 140.0:
                                pan_novo, radar_sentido = 140.0, -1.0
                            elif pan_novo <= 40.0:
                                pan_novo, radar_sentido = 40.0, 1.0
                            tracker.set_position(pan_novo, 90.0)
                            if now - last_scan_cmd_t > 0.08:
                                cmd_servo = tracker.command(radar_vel_deg_s * 1.3, now)
                                last_scan_cmd_t = now

                            # Busca Ativa 360° no Chassi:
                            # Se passou mais de 1.8s sem achar o alvo na frente, o chassi gira suavemente
                            # para fazer a busca em 360 graus por toda a sala / pista!
                            if autonomo and (now - t_ultimo_alvo > 1.8):
                                giro_pwm = 42
                                if radar_sentido > 0:
                                    target_pwm_esq, target_pwm_dir = -giro_pwm, giro_pwm
                                else:
                                    target_pwm_esq, target_pwm_dir = giro_pwm, -giro_pwm

                # Aplica rampa de slew rate nos motores
                pwm_esq_rampa, pwm_dir_rampa = motor_ramp.update(target_pwm_esq, target_pwm_dir)
                cmd_motor = f"<M,{pwm_esq_rampa},{pwm_dir_rampa}>"

                if cmd_servo is None:
                    cmd_servo = tracker.keepalive(now)
                receiver.send_cmd(cmd_servo)

                if now - last_motor_cmd_t > 0.07:
                    receiver.send_cmd(cmd_motor.encode("ascii"))
                    last_motor_cmd_t = now

                pan, tilt = tracker.pan, tracker.tilt

                # Canvas de Tela Cheia
                canvas_w = screen_w if is_fullscreen else 1280
                canvas_h = screen_h if is_fullscreen else 720
                canvas = render_to_canvas(img, canvas_w, canvas_h)

                desenhar_hud_trekking(
                    canvas, estado_missao, pan, tilt,
                    dist_estimada_cm, fps, mbps,
                    alvo_atual, gemini.texto_hud, autonomo,
                    coasting=alvo_coasting,
                    debug_mode=debug_mode,
                    conf_limiar=CONF_AQUISICAO,
                    res_label=f"{w}x{h} ({res_atual_label})",
                    gemini_ocupado=gemini.ocupado,
                )

                cv2.imshow(window_name, canvas)
            else:
                receiver.draw_waiting(window_name, screen_w if is_fullscreen else 1280, screen_h if is_fullscreen else 720)

            key = cv2.waitKey(1) & 0xFF
            char_key = chr(key).lower() if 32 <= key <= 126 else ""

            if char_key == "q" or key == 27:
                break
            elif char_key == "m":
                autonomo = not autonomo
                t_centrado_desde = None
                if autonomo:
                    estado_missao = ESTADO_RADAR_SCAN
                    t_ultimo_alvo = now - 1.0
                    print("\n" + "=" * 60)
                    print(">>> [TREKKING] MODO AUTONOMO ATIVADO (4WD LIGADO)! <<<")
                    print(f">>> Procurando alvo [{alvo_atual.upper()}] em 360° <<<")
                    print("=" * 60 + "\n")
                else:
                    estado_missao = ESTADO_STANDBY
                    target_pwm_esq = 0
                    target_pwm_dir = 0
                    motor_ramp.reset()
                    receiver.send_cmd(b"<M,0,0>")
                    print("\n>>> [TREKKING] MODO AUTONOMO DESATIVADO (STANDBY) <<<\n")
            elif char_key == "i":
                tracker.pan_sign = -tracker.pan_sign
                print(f"[PAN] Sentido: {'+' if tracker.pan_sign > 0 else '-'}")
            elif char_key == "y":
                tracker.tilt_sign = -tracker.tilt_sign
                print(f"[TILT] Sentido: {'+' if tracker.tilt_sign > 0 else '-'}")
            elif char_key == "a":
                alvo_idx = (alvo_idx + 1) % len(alvos_disponiveis)
                alvo_atual = alvos_disponiveis[alvo_idx]
                tcx_filtrado = tcy_filtrado = dist_filtrada = None
                alvo_em_tracking = False
                print(f"\n[ALVO] Novo alvo rapido: [{alvo_atual.upper()}]")
            elif char_key == "o":
                print("\n" + "=" * 50)
                print(f"Alvo atual: {alvo_atual}")
                print("Classes comuns: bottle, cup, person, chair, backpack, cell phone, cat, dog...")
                novo = input("Digite o nome da classe COCO desejada (ou 'all'): ").strip().lower()
                if novo:
                    if novo in COCO_CLASSES or novo == "all":
                        alvo_atual = novo
                        tcx_filtrado = tcy_filtrado = dist_filtrada = None
                        alvo_em_tracking = False
                        print(f"[SUCESSO] Alvo alterado para: [{alvo_atual.upper()}]")
                    else:
                        print(f"[AVISO] Classe '{novo}' nao reconhecida no COCO (mantido: {alvo_atual})")
                print("=" * 50 + "\n")
            elif char_key == "d":
                debug_mode = not debug_mode
                print(f"[DEBUG IA] Exibicao de todos os objetos: {'ATIVADA' if debug_mode else 'DESATIVADA'}")
            elif key == ord("["):
                CONF_AQUISICAO = max(0.12, round(CONF_AQUISICAO - 0.04, 2))
                CONF_TRACKING = max(0.08, round(CONF_AQUISICAO - 0.08, 2))
                print(f"[SENSIBILIDADE] Mais sensivel -> Aquisicao: {CONF_AQUISICAO*100:.0f}% | Retencao: {CONF_TRACKING*100:.0f}%")
            elif key == ord("]"):
                CONF_AQUISICAO = min(0.70, round(CONF_AQUISICAO + 0.04, 2))
                CONF_TRACKING = max(0.10, round(CONF_AQUISICAO - 0.08, 2))
                print(f"[SENSIBILIDADE] Mais estrito -> Aquisicao: {CONF_AQUISICAO*100:.0f}% | Retencao: {CONF_TRACKING*100:.0f}%")
            elif char_key in RESOLUCOES_CAM:
                res_nome, cmd_byte = RESOLUCOES_CAM[char_key]
                receiver.set_resolution_cmd(cmd_byte)
                res_atual_label = res_nome
                print(f"[CAMERA] Comando de resolucao enviado para o Rover: {res_nome}")
            elif char_key in ("+", "="):
                receiver.send_cmd(b"+")
                print("[CAMERA] Qualidade JPEG aumentada no Rover (menos compressao)")
            elif char_key == "-":
                receiver.send_cmd(b"-")
                print("[CAMERA] Qualidade JPEG reduzida no Rover (mais compressao / mais FPS)")
            elif char_key == "f":
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(window_name, 1280, 720)
            elif key == ord(" ") or char_key == "g":
                if 'img' in locals() and img is not None:
                    gemini.disparar(img)

    finally:
        receiver.send_cmd(b"<M,0,0>")
        receiver.close()
        cv2.destroyAllWindows()
        print("\nMissao Trekking encerrada. Motores desativados.")


if __name__ == "__main__":
    main()
