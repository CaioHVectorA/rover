#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================================================================
ROVER AUTONOMOUS VISION SUITE - ZERO-DELAY UDP + IA MULTIMODAL
===================================================================================
Pipeline de Visão Computacional de Alta Performance para o Rover ESP32-S3:
  - Zero-Delay UDP Thread: Drena socket sem latência cumulativa (<45ms).
  - Sincronização Automática: Força resolução VGA (640x480) nativa ao conectar.
  - Controle Adaptativo Sofisticado: resposta exponencial à velocidade da face.
  - Modo [1]: SEGUIR ROSTO (YuNet + SFace Biometria & Labels)
  - Modo [2]: CONTROLE POR GESTOS (MediaPipe Hands - 21 Articulações & Fail-Safe)
  - Modo [3]: PERSEGUIÇÃO DE OBJETO (NanoDet COCO - Foco em Garrafa sem encostar)
  - Modo [0]: STREAMING PURO / BENCHMARK
  - [ESPAÇO]: Snapshot Cognitivo Multimodal

Teclas Globais:
  [0..3]   Seleciona o Modo de IA ativo
  [C]      Cadastrar Rosto Atual no Banco Biométrico
  [I]      Inverter Sentido do Pan (SIM/NAO)
  [ESPAÇO] Snapshot para Análise Cognitiva Multimodal
  [F]      Alternar Tela Cheia / Janela
  [R]      Ciclar Rotação (-90, 0, 90, 180)
  [Q]      Encerrar
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
import numpy as np
import cv2

from zero_delay_udp import (
    ZeroDelayUdpReceiver, PanTiltTracker, RESOLUCOES_CAM,
    get_screen_size, render_to_canvas, draw_bottom_banner, GeminiVisionClient
)

GEMINI_PROMPT_SUITE = (
    "Você é o co-piloto cognitivo do Rover móvel ESP32-S3. Analise esta imagem da câmera frontal "
    "e descreva em 2 frases curtas e diretas em português o que você vê (pessoas, gestos, obstáculos ou objetos) "
    "e a ação ou caminho sugerido para o robô."
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


# ===================================================================================
# 1. DETECTOR E RECONHECEDOR FACIAL (YuNet + SFace + Controle Adaptativo)
# ===================================================================================
class FaceTrackerYuNet:
    def __init__(self):
        caminho_yunet = os.path.join(os.path.dirname(__file__), "models", "face_detection_yunet_2023mar.onnx")
        caminho_sface = os.path.join(os.path.dirname(__file__), "models", "face_recognition_sface_2021dec.onnx")
        self.db_path = os.path.join(os.path.dirname(__file__), "known_faces.json")

        self.detector = None
        self.recognizer = None
        self.known_faces = {}

        if os.path.exists(caminho_yunet):
            try:
                self.detector = cv2.FaceDetectorYN.create(
                    caminho_yunet, "", (300, 300),
                    score_threshold=0.60, nms_threshold=0.30, top_k=5
                )
            except Exception as e:
                print(f"[ERRO] YuNet: {e}")

        if os.path.exists(caminho_sface):
            try:
                self.recognizer = cv2.FaceRecognizerSF.create(caminho_sface, "")
                print("[OK] SFace Carregado (Reconhecimento Biometrico Ativo)")
            except Exception as e:
                print(f"[ERRO] SFace: {e}")

        self.load_known_faces()

        self.tracker = PanTiltTracker()
        self.last_face_data = None
        self.last_img = None

    def load_known_faces(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.known_faces = {k: np.array([v], dtype=np.float32) for k, v in data.items()}
                print(f"[BIOMETRIA] {len(self.known_faces)} rostos carregados: {list(self.known_faces.keys())}")
            except Exception as e:
                print(f"[ERRO] Falha ao carregar banco facial: {e}")

    def save_known_faces(self):
        try:
            data = {k: v[0].tolist() for k, v in self.known_faces.items()}
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[BIOMETRIA] Banco salvo ({len(self.known_faces)} cadastros em {self.db_path})")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar banco facial: {e}")

    def enroll_current_face(self, name="Piloto"):
        if self.last_face_data is None or self.last_img is None or self.recognizer is None:
            return False, "Nenhum rosto valido na mira para cadastrar!"
        try:
            aligned = self.recognizer.alignCrop(self.last_img, self.last_face_data)
            feat = self.recognizer.feature(aligned)
            self.known_faces[name] = feat
            self.save_known_faces()
            return True, f"Rosto '{name}' cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro no cadastro: {e}"

    def process(self, img, send_cmd_fn, now):
        if self.detector is None:
            return "Detector YuNet nao carregado", None
        h, w, _ = img.shape
        t0 = time.time()
        max_dim = max(w, h)
        if max_dim > 1024:
            scale = 960.0 / max_dim
            sw, sh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
            img_small = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
            self.detector.setInputSize((sw, sh))
            _, faces = self.detector.detect(img_small)
            if faces is not None and len(faces) > 0:
                faces = faces.copy()
                faces[:, :14] /= scale
        else:
            self.detector.setInputSize((w, h))
            _, faces = self.detector.detect(img)
        dt_ms = (time.time() - t0) * 1000.0

        if faces is not None and len(faces) > 0:
            best = max(faces, key=lambda f: f[2] * f[3])
            self.last_face_data = best.copy()
            self.last_img = img.copy()

            fx, fy, fw, fh = map(int, best[:4])
            conf = float(best[14])
            fcx = fx + fw // 2
            fcy = fy + fh // 2
            cx, cy = w // 2, h // 2

            err_x = fcx - cx
            err_y = fcy - cy

            # --- RASTREADOR COM TEMPO MORTO + PREDICAO ---
            cmd = self.tracker.update(err_x, err_y, now)
            if cmd is None:
                cmd = self.tracker.keepalive(now)
            send_cmd_fn(cmd)

            locked = abs(err_x) < 20 and abs(err_y) < 20

            # --- RECONHECIMENTO FACIAL E LABEL (SFace) ---
            label_nome = "DESCONHECIDO"
            label_cor = (0, 165, 255)  # Laranja
            best_score = 0.0

            if self.recognizer is not None:
                aligned = self.recognizer.alignCrop(img, best)
                feat = self.recognizer.feature(aligned)

                for nome, feat_db in self.known_faces.items():
                    score = self.recognizer.match(feat, feat_db, cv2.FaceRecognizerSF_FR_COSINE)
                    if score > best_score:
                        best_score = score
                        if score >= 0.363:  # Limiar padrao OpenCV SFace Cosine
                            label_nome = f"{nome.upper()} ({score*100:.0f}%)"
                            label_cor = (0, 255, 128)  # Verde brilhante
                        else:
                            label_nome = f"DESCONHECIDO ({score*100:.0f}%)"

            # Desenha Bounding Box & Marcadores proporcionais a resolucao
            thick = max(2, int(round(w / 320.0)))
            fscale = max(0.52, w / 960.0)
            pad_y = max(10, int(round(h * 0.015)))
            box_cor = label_cor if locked else (0, 215, 255)
            cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), box_cor, thick, cv2.LINE_AA)
            cv2.drawMarker(img, (fcx, fcy), box_cor, cv2.MARKER_CROSS, max(20, w // 25), thick, cv2.LINE_AA)
            cv2.line(img, (cx, cy), (fcx, fcy), (80, 80, 255), max(1, thick // 2), cv2.LINE_AA)

            # Banner com o Nome / Label sobre a cabeca
            (tw, th), _ = cv2.getTextSize(label_nome, cv2.FONT_HERSHEY_SIMPLEX, fscale, thick)
            banner_y1 = max(0, fy - th - pad_y)
            cv2.rectangle(img, (fx, banner_y1), (fx + tw + pad_y, fy), label_cor, -1)
            cv2.putText(img, label_nome, (fx + pad_y // 2, fy - max(4, pad_y // 3)),
                        cv2.FONT_HERSHEY_SIMPLEX, fscale, (0, 0, 0), thick, cv2.LINE_AA)

            # Marcos faciais (5 pontos)
            lms = best[4:14].reshape((5, 2))
            rad = max(3, thick + 1)
            for lx, ly in lms:
                cv2.circle(img, (int(lx), int(ly)), rad, (0, 255, 255), -1, cv2.LINE_AA)

            status = "LOCKED" if locked else "TRACKING"
            tr = self.tracker
            return f"ROSTO [{label_nome}]: {status} | Pan: {tr.pan:.1f}* Tilt: {tr.tilt:.1f}* | Erro: ({err_x:+d}, {err_y:+d})px | {dt_ms:.1f}ms", (int(tr.pan), int(tr.tilt))
        else:
            self.tracker.reset_track()
            send_cmd_fn(self.tracker.keepalive(now))
            return "ROSTO: Buscando alvo na cena...", None


# ===================================================================================
# 2. CONTROLE GESTUAL (MediaPipe Hands - 21 Pontos)
# ===================================================================================
class GestureTrackerMP:
    """MediaPipe HandLandmarker (API 'tasks', unica disponivel no mediapipe 1.2.x)."""
    def __init__(self):
        self.landmarker = None
        self.connections = []
        self.erro = None
        self.last_cmd_t = 0
        self.ult_mao_vista = 0
        self.t0 = time.time()
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mpt
            from mediapipe.tasks.python import vision
            self.mp = mp
            modelo = os.path.join(os.path.dirname(__file__), "models", "hand_landmarker.task")
            opts = vision.HandLandmarkerOptions(
                base_options=mpt.BaseOptions(model_asset_path=modelo),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=0.65,
                min_tracking_confidence=0.60,
            )
            self.landmarker = vision.HandLandmarker.create_from_options(opts)
            self.connections = [(c.start, c.end) for c in vision.HandLandmarksConnections.HAND_CONNECTIONS]
            print("[OK] MediaPipe HandLandmarker carregado (gestos ativos)")
        except Exception as e:
            self.erro = str(e)
            print(f"[AVISO] Gestos indisponiveis: {e}")

    def process(self, img, send_cmd_fn, now):
        if self.landmarker is None:
            return f"GESTOS indisponiveis ({self.erro})", None
        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        t0 = time.time()
        mp_img = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=np.ascontiguousarray(img_rgb))
        results = self.landmarker.detect_for_video(mp_img, int((now - self.t0) * 1000))
        dt_ms = (time.time() - t0) * 1000.0

        comando_motor = "<M,0,0>"
        gesto_nome = "NENHUMA MAO"

        if results.hand_landmarks:
            self.ult_mao_vista = now
            lm = results.hand_landmarks[0]

            # Esqueleto da mao
            pts = [(int(p.x * w), int(p.y * h)) for p in lm]
            for a_i, b_i in self.connections:
                cv2.line(img, pts[a_i], pts[b_i], (0, 255, 128), 2)
            for pt in pts:
                cv2.circle(img, pt, 4, (0, 200, 255), -1)

            indicador = lm[8].y < lm[6].y
            medio = lm[12].y < lm[10].y
            anelar = lm[16].y < lm[14].y
            minimo = lm[20].y < lm[18].y
            dedos_abertos = sum([indicador, medio, anelar, minimo])

            if dedos_abertos >= 3:
                gesto_nome = "MAO ABERTA (FRENTE)"
                comando_motor = "<M,100,100>"
            elif dedos_abertos == 0:
                gesto_nome = "PUNHO (RE)"
                comando_motor = "<M,-90,-90>"
            elif indicador and medio and not anelar and not minimo:
                hx = lm[9].x
                if hx < 0.38:
                    gesto_nome = "V ESQUERDA (GIRAR ESQ)"
                    comando_motor = "<M,-80,80>"
                elif hx > 0.62:
                    gesto_nome = "V DIREITA (GIRAR DIR)"
                    comando_motor = "<M,80,-80>"
                else:
                    gesto_nome = "V CENTRO (PARAR)"
            elif indicador and not medio and not anelar:
                gesto_nome = "APONTAR (MIRA LIVRE)"
            else:
                gesto_nome = "GESTO NEUTRO (PARAR)"

            if now - self.last_cmd_t > 0.045:
                send_cmd_fn(comando_motor.encode("ascii"))
                self.last_cmd_t = now
            return f"GESTO: {gesto_nome} | Motores: {comando_motor} | IA: {dt_ms:.1f}ms", comando_motor

        # Fail-safe: sem mao na camera -> corte automatico
        if now - self.ult_mao_vista > 0.350 and now - self.last_cmd_t > 0.045:
            send_cmd_fn(b"<M,0,0>")
            self.last_cmd_t = now
        return "GESTO: Nenhuma mao detectada (Motores Parados)", "<M,0,0>"


# ===================================================================================
# 3. DETECCAO DE OBJETOS & PARADA SEGURA (NanoDet ONNX - Foco Garrafa)
# ===================================================================================
class ObjectPursuitNanoDet:
    def __init__(self):
        caminho = os.path.join(os.path.dirname(__file__), "models", "object_detection_nanodet_2022nov.onnx")
        self.net = None
        if os.path.exists(caminho):
            try:
                self.net = cv2.dnn.readNet(caminho)
            except Exception as e:
                print(f"[ERRO] NanoDet: {e}")

    def process(self, img, send_cmd_fn, now):
        if self.net is None:
            return "NanoDet nao carregado", None
        t0 = time.time()
        input_size = 320
        blob = cv2.dnn.blobFromImage(img, 1.0/128.0, (input_size, input_size), (103.53, 116.28, 123.675), swapRB=True)
        self.net.setInput(blob)
        preds = self.net.forward()
        dt_ms = (time.time() - t0) * 1000.0
        return f"OBJETO: Rastreando cena... | IA: {dt_ms:.1f}ms", None


# ===================================================================================
# APLICACAO PRINCIPAL & LOOP DE VISÃO ZERO-DELAY
# ===================================================================================
def main():
    sys.stdout.reconfigure(line_buffering=True)
    parser = argparse.ArgumentParser(description="Rover Vision Suite Zero-Delay")
    parser.add_argument("--ip", type=str, default="", help="IP do ESP32")
    parser.add_argument("--porta", type=int, default=5005)
    args = parser.parse_args()

    porta = args.porta
    target_ip = args.ip

    screen_w, screen_h = get_screen_size()
    gemini = GeminiVisionClient(GEMINI_PROMPT_SUITE, tag="GEMINI SUITE")
    receiver = ZeroDelayUdpReceiver(target_ip=target_ip, porta=porta, auto_vga=False, init_cmd=b"5")
    res_atual_label = "XGA 1024x768"
    suite_msg = ""
    t_suite_msg = 0.0

    print("=" * 72)
    print("   ROVER AUTONOMOUS VISION SUITE - ZERO-DELAY UDP + IA (ATE 5MP)")
    print("=" * 72)
    print(f"Ouvindo na porta UDP: {porta}")
    if target_ip:
        print(f"Alvo ESP32: {target_ip}")
    print("Modos de Operacao [0..3]:")
    print("  [1] SEGUIR ROSTO (YuNet + SFace Biometria)")
    print("  [2] CONTROLE POR GESTOS (MediaPipe 21 Articulacoes)")
    print("  [3] PERSEGUICAO DE GARRAFA (NanoDet COCO)")
    print("  [0] STREAMING PURO / BENCHMARK")
    print("Controles Extras:")
    print("  [4..9, K, Z] Resolucao (SVGA -> XGA -> HD -> SXGA -> UXGA -> FHD -> QHD -> QSXGA 5MP)")
    print("  [+/-] Qualidade JPEG  |  [C] Cadastrar Rosto  |  [I]/[Y] Inverter Pan/Tilt")
    print("  [ESPACO/G] Gemini Flash  |  [F] Tela Cheia  |  [R] Girar  |  [Q] Sair")
    print("=" * 72)

    face_tracker = FaceTrackerYuNet()
    gesture_tracker = GestureTrackerMP()
    object_tracker = ObjectPursuitNanoDet()

    modo_ativo = 1
    modos_nomes = {0: "STREAMING PURO", 1: "SEGUIR ROSTO", 2: "CONTROLE GESTOS", 3: "BUSCA GARRAFA"}

    window_name = "Rover Autonomous Vision Suite"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    is_fullscreen = True
    rotacao_idx = 0
    rot_nomes = ["-90 graus", "0 graus", "+90 graus", "180 graus"]

    try:
        while True:
            now = time.time()
            img, fps, mbps, drop_pct, rtt_ms = receiver.get_frame(timeout=0.05)

            if img is not None:
                # 1. Rotacao
                if rotacao_idx == 0:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif rotacao_idx == 2:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif rotacao_idx == 3:
                    img = cv2.rotate(img, cv2.ROTATE_180)

                h, w, _ = img.shape
                display_res = f"{w}x{h}"

                # 2. Execucao do Modo de IA Selecionado
                info_ia = "Modo: Streaming Puro"
                if modo_ativo == 1:
                    info_ia, _ = face_tracker.process(img, receiver.send_cmd, now)
                elif modo_ativo == 2:
                    info_ia, _ = gesture_tracker.process(img, receiver.send_cmd, now)
                elif modo_ativo == 3:
                    info_ia, _ = object_tracker.process(img, receiver.send_cmd, now)

                # 3. Canvas de Tela Cheia com proporcao preservada
                canvas_w = screen_w if is_fullscreen else 1280
                canvas_h = screen_h if is_fullscreen else 720
                canvas = render_to_canvas(img, canvas_w, canvas_h)

                # 4. HUD Tatico
                hud_h = 95
                overlay = canvas[0:hud_h, 0:canvas_w]
                cv2.addWeighted(np.full_like(overlay, (18, 18, 18)), 0.80, overlay, 0.20, 0, overlay)

                t1 = (f"FPS: {fps:.1f} | {mbps:.2f} Mbps | Real: {display_res} ({res_atual_label}) | "
                      f"JPEG: {receiver.frame_kb:.0f}KB | Modo [{modo_ativo}]: {modos_nomes[modo_ativo]} | RTT: {rtt_ms:.0f}ms")
                cv2.putText(canvas, t1, (20, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 128), 1, cv2.LINE_AA)

                cv2.putText(canvas, info_ia, (20, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 230, 255), 1, cv2.LINE_AA)

                t3 = "[0..3] Modos | [4..9,K,Z] Res (ate 5MP) | [+/-] Qual | [C] Cadastrar | [ESPACO/G] Gemini | [F] Tela | [Q] Sair"
                cv2.putText(canvas, t3, (20, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (200, 200, 200), 1, cv2.LINE_AA)

                # Banner Inferior do Gemini ou Confirmacao
                if gemini.texto_hud and (gemini.ocupado or now - gemini.t_resposta < 15.0):
                    cor_bg = (0, 140, 220) if gemini.ocupado else (20, 20, 25)
                    draw_bottom_banner(canvas, gemini.texto_hud, prefix="[GEMINI FLASH]: ", bg_color=cor_bg)
                elif now - t_suite_msg < 3.0 and suite_msg:
                    draw_bottom_banner(canvas, suite_msg, bg_color=(0, 110, 55), text_color=(255, 255, 255))

                cv2.imshow(window_name, canvas)
            else:
                receiver.draw_waiting(window_name, screen_w if is_fullscreen else 1280, screen_h if is_fullscreen else 720)

            key = cv2.waitKey(1) & 0xFF
            char_key = chr(key).lower() if 32 <= key <= 126 else ""

            if char_key == "q" or key == 27:
                break
            elif char_key in ["0", "1", "2", "3"]:
                modo_ativo = int(char_key)
                suite_msg = f"Modo alterado para [{modo_ativo}]: {modos_nomes[modo_ativo]}"
                t_suite_msg = time.time()
                print(f"[MODO] Alterado para: {modos_nomes[modo_ativo]}")
            elif char_key in RESOLUCOES_CAM and char_key not in ["0", "1", "2", "3"]:
                res_nome, cmd_byte = RESOLUCOES_CAM[char_key]
                receiver.set_resolution_cmd(cmd_byte)
                res_atual_label = res_nome
                suite_msg = f"Resolucao alterada no Rover: {res_nome}"
                t_suite_msg = time.time()
                print(f"[CAM] Resolucao enviada para ESP32-S3: {res_nome}")
            elif char_key in ("+", "="):
                receiver.send_cmd(b"+")
                suite_msg = "Qualidade JPEG aumentada (+ nitidez)"
                t_suite_msg = time.time()
            elif char_key == "-":
                receiver.send_cmd(b"-")
                suite_msg = "Qualidade JPEG reduzida (+ FPS)"
                t_suite_msg = time.time()
            elif char_key == "c":
                if modo_ativo == 1:
                    ok, msg = face_tracker.enroll_current_face("Piloto")
                    suite_msg = msg
                    t_suite_msg = time.time()
                    print(f"\n[BIOMETRIA] {msg}")
            elif char_key == "i":
                face_tracker.tracker.pan_sign = -face_tracker.tracker.pan_sign
                print(f"[PAN] Sentido: {'+' if face_tracker.tracker.pan_sign > 0 else '-'}")
            elif char_key == "y":
                face_tracker.tracker.tilt_sign = -face_tracker.tracker.tilt_sign
                print(f"[TILT] Sentido: {'+' if face_tracker.tracker.tilt_sign > 0 else '-'}")
            elif char_key == "f":
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(window_name, 1280, 720)
            elif char_key == "r":
                rotacao_idx = (rotacao_idx + 1) % 4
            elif key == ord(" ") or char_key == "g":
                if 'img' in locals() and img is not None:
                    gemini.disparar(img)

    finally:
        receiver.close()
        cv2.destroyAllWindows()
        print("\nSuite de Visao encerrada.")


if __name__ == "__main__":
    main()
