#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROVER: Servidor UDP de Alta Performance + Rastreamento Facial Deep Learning (YuNet)
-----------------------------------------------------------------------------------
- Zero-Delay UDP Thread: Drenagem contínua do socket, eliminando atrasos acumulados.
- Controle Adaptativo Sofisticado: resposta exponencial à velocidade do movimento.
- Visão Computacional de Alta Performance com YuNet (Deep Neural Network no OpenCV).
- Teclas interativas:
    [T] Ligar/Desligar Auto-Tracking de Rosto
    [I] Inverter Sentido do Pan (SIM/NAO)
    [F] Alternar Tela Cheia
    [R] Alternar Rotacao (-90, 0, +90, 180)
    [1..4] Resolucoes (QVGA, CIF, VGA, SVGA)
    [+] / [-] Qualidade JPEG
    [Q] Sair
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import argparse
import ctypes
import numpy as np
import cv2

from zero_delay_udp import ZeroDelayUdpReceiver, PanTiltTracker


def parse_args():
    parser = argparse.ArgumentParser(description="Rover UDP Camera + Face Tracking")
    parser.add_argument("--ip", type=str, default="", help="IP do ESP32 (se vazio, usa broadcast)")
    parser.add_argument("--porta", type=int, default=5005, help="Porta UDP (padrao 5005)")
    return parser.parse_args()


def carregar_detector_yunet():
    caminho_modelo = os.path.join(os.path.dirname(__file__), "models", "face_detection_yunet_2023mar.onnx")
    if not os.path.exists(caminho_modelo):
        print(f"[AVISO] Modelo YuNet nao encontrado em: {caminho_modelo}")
        return None
    try:
        detector = cv2.FaceDetectorYN.create(
            caminho_modelo, "", (300, 300),
            score_threshold=0.60,
            nms_threshold=0.30,
            top_k=5
        )
        print("[IA] Detector YuNet (Deep Neural Network) inicializado com sucesso!")
        return detector
    except Exception as e:
        print(f"[ERRO] Falha ao carregar YuNet: {e}")
        return None


def main():
    sys.stdout.reconfigure(line_buffering=True)
    args = parse_args()
    porta = args.porta
    target_ip = args.ip

    try:
        ctypes.windll.user32.SetProcessDPIAware()
        screen_w = ctypes.windll.user32.GetSystemMetrics(0)
        screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    except Exception:
        screen_w, screen_h = 1920, 1080

    face_detector = carregar_detector_yunet()
    receiver = ZeroDelayUdpReceiver(target_ip=target_ip, porta=porta, auto_vga=True)

    # Controladores P-D Não-Lineares de Velocidade Adaptativa
    tracker = PanTiltTracker()

    print("=" * 65)
    print("  ROVER: STREAMING UDP ZERO-DELAY + TRACKING FACIAL ADAPTATIVO")
    print("=" * 65)
    print(f"Ouvindo na porta UDP: {porta}")
    if target_ip:
        print(f"Conectando diretamente ao ESP32 no IP: {target_ip}")
    else:
        print("Modo Auto-Descoberta: Enviando broadcast 'HELLO' na rede local...")
    print(f"Resolucao da tela: {screen_w}x{screen_h}")
    print("Controles na janela de video:")
    print("  [T] Ativar/Desativar Auto-Tracking de Rosto")
    print("  [I] Inverter Sentido do Pan (SIM/NAO)")
    print("  [F] Alternar Tela Cheia       [R] Girar (-90, 0, 90, 180)")
    print("  [1] QVGA  [2] CIF  [3] VGA  [4] SVGA")
    print("  [+] Aumentar Qualidade        [-] Reduzir Qualidade")
    print("  [Q] Sair")
    print("=" * 65)

    tracking_ativo = True
    face_info_txt = "Tracking: Ativo (Buscando rosto)"

    window_name = "Rover UDP Camera - Deep Learning Face Tracking"
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

                # 2. Rastreamento Facial Deep Learning (YuNet)
                if tracking_ativo and face_detector is not None:
                    t_ai0 = time.time()
                    face_detector.setInputSize((w, h))
                    _, faces = face_detector.detect(img)
                    ai_ms = (time.time() - t_ai0) * 1000.0

                    if faces is not None and len(faces) > 0:
                        best = max(faces, key=lambda f: f[2] * f[3])
                        fx, fy, fw, fh = map(int, best[:4])
                        conf = float(best[14])

                        fcx = fx + fw // 2
                        fcy = fy + fh // 2
                        cx, cy = w // 2, h // 2

                        err_x = fcx - cx
                        err_y = fcy - cy

                        # --- RASTREADOR COM TEMPO MORTO + PREDICAO (ver zero_delay_udp.py) ---
                        cmd = tracker.update(err_x, err_y, now)
                        if cmd is None:
                            cmd = tracker.keepalive(now)
                        receiver.send_cmd(cmd)
                        pan_servo, tilt_servo = tracker.pan, tracker.tilt
                        step_x = tracker.pan_axis.vel_est
                        step_y = tracker.tilt_axis.vel_est

                        target_locked = abs(err_x) < 20 and abs(err_y) < 20
                        cor = (0, 255, 128) if target_locked else (0, 215, 255)

                        # Caixa de delimitacao estilizada
                        cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), cor, 2)
                        cv2.drawMarker(img, (fcx, fcy), cor, cv2.MARKER_CROSS, 24, 2, cv2.LINE_AA)
                        cv2.line(img, (cx, cy), (fcx, fcy), (80, 80, 255), 1, cv2.LINE_AA)

                        # Pontos faciais (olhos, nariz, boca)
                        lms = best[4:14].reshape((5, 2))
                        for lx, ly in lms:
                            cv2.circle(img, (int(lx), int(ly)), 3, (0, 255, 255), -1, cv2.LINE_AA)

                        status_lock = "LOCKED" if target_locked else "FAST-TRACK"
                        face_info_txt = f"ROSTO: {status_lock} ({conf*100:.0f}%) | Pan: {pan_servo:.1f}* Tilt: {tilt_servo:.1f}* | Erro: ({err_x:+d}, {err_y:+d})px | Alvo: ({step_x:+.0f}, {step_y:+.0f})*/s | IA: {ai_ms:.1f}ms"

                    else:
                        tracker.reset_track()
                        receiver.send_cmd(tracker.keepalive(now))
                        face_info_txt = "ROSTO: Buscando alvo na cena..."
                else:
                    face_info_txt = "Tracking: Desativado [Pressione T para ativar]"

                # 3. Centralizacao em tela cheia com proporcao preservada
                canvas_w = screen_w if is_fullscreen else 1280
                canvas_h = screen_h if is_fullscreen else 720
                scale = min(canvas_w / w, canvas_h / h)
                new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))

                scaled_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                ox = (canvas_w - new_w) // 2
                oy = (canvas_h - new_h) // 2
                canvas[oy : oy + new_h, ox : ox + new_w] = scaled_img

                # 4. HUD Overlay semitransparente no topo (3 linhas de informacoes)
                hud_h = 95
                overlay = canvas.copy()
                cv2.rectangle(overlay, (0, 0), (canvas_w, hud_h), (18, 18, 18), -1)
                cv2.addWeighted(overlay, 0.75, canvas, 0.25, 0, canvas)

                # Linha 1: Métricas de Streaming
                t1 = f"FPS: {fps:.1f}  |  Banda: {mbps:.2f} Mbps  |  Res: {display_res}  |  Rot: {rot_nomes[rotacao_idx]}  |  RTT: {rtt_ms:.1f} ms"
                cv2.putText(canvas, t1, (20, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 255, 128), 2)

                # Linha 2: Informações de Auto-Tracking Facial
                cor_info = (0, 255, 128) if "LOCKED" in face_info_txt else ((0, 255, 255) if "FAST" in face_info_txt else (200, 220, 200))
                cv2.putText(canvas, face_info_txt, (20, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.58, cor_info, 2)

                # Linha 3: Controles
                t3 = f"[T] Tracking: {'ON' if tracking_ativo else 'OFF'} | [I] Pan inv: {'SIM' if tracker.pan_sign > 0 else 'NAO'} | [Y] Tilt inv: {'SIM' if tracker.tilt_sign > 0 else 'NAO'} | [F] Tela | [R] Girar | [Q] Sair"
                cv2.putText(canvas, t3, (20, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1)

                cv2.imshow(window_name, canvas)

            else:
                receiver.draw_waiting(window_name, screen_w if is_fullscreen else 1280, screen_h if is_fullscreen else 720)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
            elif key == ord("t"):
                tracking_ativo = not tracking_ativo
                print(f"[TRACKING] Auto-tracking facial: {'LIGADO' if tracking_ativo else 'DESLIGADO'}")
            elif key == ord("i"):
                tracker.pan_sign = -tracker.pan_sign
                print(f"[PAN] Sentido do Pan: {'+' if tracker.pan_sign > 0 else '-'}")
            elif key == ord("y"):
                tracker.tilt_sign = -tracker.tilt_sign
                print(f"[TILT] Sentido do Tilt: {'+' if tracker.tilt_sign > 0 else '-'}")
            elif key == ord("f"):
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(window_name, 1280, 720)
            elif key == ord("r"):
                rotacao_idx = (rotacao_idx + 1) % 4
                print(f"[ROT] Rotacao: {rot_nomes[rotacao_idx]}")
            elif key in [ord("1"), ord("2"), ord("3"), ord("4"), ord("+"), ord("-")]:
                receiver.send_cmd(chr(key).encode("ascii"))
                print(f"[CMD] Enviado comando de configuracao: {chr(key)}")

    finally:
        receiver.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
