#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================================================================
ROVER BIOMETRIC AI - RECONHECIMENTO FACIAL E LABELING (YuNet + SFace)
===================================================================================
Módulo de Biometria Facial para o Rover ESP32-S3:
  1. Detecção Facial de Alta Precisão (YuNet ONNX - 60+ FPS)
  2. Alinhamento Anatômico 2D (5 pontos: olhos, nariz, boca)
  3. Extração de Embeddings 128-D (SFace ONNX - Deep Feature Vector)
  4. Comparação por Similaridade de Cosseno (Limiar padrão: 0.363)
  5. Identificação e Labeling Gráfico (Caixas Verdes/Laranjas + Banners de Nome)

Modos de Uso:
  - Stream UDP do Rover:    python tools/reconhecimento_facial.py --udp
  - Webcam do PC:           python tools/reconhecimento_facial.py --webcam 0
  - Cadastrar via Foto:     python tools/reconhecimento_facial.py --cadastrar "Caihe" foto.jpg
  - Testar em Foto:         python tools/reconhecimento_facial.py --reconhecer foto.jpg
  - Listar Cadastrados:     python tools/reconhecimento_facial.py --listar
===================================================================================
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import json
import socket
import struct
import argparse
import numpy as np
import cv2

from zero_delay_udp import (
    ZeroDelayUdpReceiver, PanTiltTracker, RESOLUCOES_CAM,
    get_screen_size, render_to_canvas, draw_bottom_banner, GeminiVisionClient
)

GEMINI_PROMPT_BIOMETRIA = (
    "Você é o co-piloto e assistente de IA biométrica do Rover ESP32-S3. "
    "Analise esta imagem frontal da câmera e responda em 2 frases curtas e diretas em português: "
    "1. Descreva a pessoa diante do robô (expressão facial, humor aparente e o que está fazendo). "
    "2. Descreva os objetos que ela está segurando e o ambiente ao redor."
)

MAGIC = 0x52565231
HEADER_FORMAT = "<IHHHHI"
HEADER_SIZE = 16

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
YUNET_PATH = os.path.join(MODEL_DIR, "face_detection_yunet_2023mar.onnx")
SFACE_PATH = os.path.join(MODEL_DIR, "face_recognition_sface_2021dec.onnx")
DB_PATH = os.path.join(os.path.dirname(__file__), "known_faces.json")
COSINE_THRESHOLD = 0.363  # Limiar de Cosseno recomendado pelo OpenCV SFace


class FaceEngine:
    def __init__(self, yunet_path=YUNET_PATH, sface_path=SFACE_PATH, db_path=DB_PATH):
        self.db_path = db_path
        self.known_faces = {}

        if not os.path.exists(yunet_path):
            raise FileNotFoundError(f"Modelo YuNet nao encontrado em: {yunet_path}")
        if not os.path.exists(sface_path):
            raise FileNotFoundError(f"Modelo SFace nao encontrado em: {sface_path}")

        print("[BIOMETRIA] Carregando Detector YuNet...")
        self.detector = cv2.FaceDetectorYN.create(
            yunet_path, "", (320, 320),
            score_threshold=0.60, nms_threshold=0.30, top_k=10
        )

        print("[BIOMETRIA] Carregando Reconhecedor SFace...")
        self.recognizer = cv2.FaceRecognizerSF.create(sface_path, "")

        self.carregar_banco()

    def carregar_banco(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.known_faces = {k: np.array([v], dtype=np.float32) for k, v in data.items()}
                print(f"[BIOMETRIA] Banco carregado: {len(self.known_faces)} identidade(s) cadastrada(s).")
            except Exception as e:
                print(f"[ERRO] Falha ao ler banco facial: {e}")
                self.known_faces = {}
        else:
            self.known_faces = {}

    def salvar_banco(self):
        try:
            data = {k: v[0].tolist() for k, v in self.known_faces.items()}
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[BIOMETRIA] Banco gravado com sucesso em: {self.db_path}")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao gravar banco facial: {e}")
            return False

    def detectar(self, img):
        h, w, _ = img.shape
        max_dim = max(w, h)
        # Em 2MP-5MP, detecta rapido em <=960px e projeta coordenadas para o frame original
        if max_dim > 1024:
            scale = 960.0 / max_dim
            sw, sh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
            img_small = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
            self.detector.setInputSize((sw, sh))
            _, faces = self.detector.detect(img_small)
            if faces is not None and len(faces) > 0:
                faces = faces.copy()
                faces[:, :14] /= scale
            return faces
        self.detector.setInputSize((w, h))
        _, faces = self.detector.detect(img)
        return faces

    def extrair_embedding(self, img, face_data):
        aligned = self.recognizer.alignCrop(img, face_data)
        feat = self.recognizer.feature(aligned)
        return feat

    def identificar(self, feat):
        melhor_nome = "DESCONHECIDO"
        melhor_score = 0.0

        for nome, feat_db in self.known_faces.items():
            score = self.recognizer.match(feat, feat_db, cv2.FaceRecognizerSF_FR_COSINE)
            if score > melhor_score:
                melhor_score = score
                if score >= COSINE_THRESHOLD:
                    melhor_nome = nome

        reconhecido = (melhor_nome != "DESCONHECIDO")
        return melhor_nome, melhor_score, reconhecido

    def cadastrar_face(self, nome, img, face_data):
        feat = self.extrair_embedding(img, face_data)
        self.known_faces[nome] = feat
        self.salvar_banco()
        return True

    def processar_frame(self, img, esp_sock=None, esp_addr=None):
        faces = self.detectar(img)
        h, w, _ = img.shape
        cx, cy = w // 2, h // 2
        thick = max(2, int(round(w / 320.0)))
        fscale = max(0.50, w / 960.0)
        pad_y = max(10, int(round(h * 0.015)))

        resultados = []
        if faces is not None and len(faces) > 0:
            for face in faces:
                fx, fy, fw, fh = map(int, face[:4])
                feat = self.extrair_embedding(img, face)
                nome, score, reconhecido = self.identificar(feat)

                # Definicao visual
                if reconhecido:
                    label = f"{nome.upper()} ({score*100:.0f}%)"
                    cor_box = (0, 255, 128)      # Verde neon tatico
                    cor_banner = (0, 180, 80)
                else:
                    label = f"DESCONHECIDO ({score*100:.0f}%)"
                    cor_box = (0, 140, 255)      # Laranja de alerta
                    cor_banner = (0, 110, 210)

                # Desenho do Bounding Box proporcional a resolucao
                cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), cor_box, thick, cv2.LINE_AA)

                # Banner com Nome proporcional
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fscale, thick)
                y_topo = max(0, fy - th - pad_y)
                cv2.rectangle(img, (fx, y_topo), (fx + tw + pad_y, fy), cor_banner, -1)
                cv2.putText(img, label, (fx + pad_y // 2, fy - max(4, pad_y // 3)),
                            cv2.FONT_HERSHEY_SIMPLEX, fscale, (255, 255, 255), thick, cv2.LINE_AA)

                # Marcadores de Alinhamento (5 pontos: Olhos, Nariz, Boca)
                lms = face[4:14].reshape((5, 2))
                rad = max(3, thick + 1)
                for lx, ly in lms:
                    cv2.circle(img, (int(lx), int(ly)), rad, (0, 255, 255), -1, cv2.LINE_AA)

                resultados.append({
                    "box": (fx, fy, fw, fh),
                    "nome": nome,
                    "score": score,
                    "reconhecido": reconhecido,
                    "face_data": face
                })

            # Mira central no maior rosto
            principal = max(resultados, key=lambda r: r["box"][2] * r["box"][3])
            p_fx, p_fy, p_fw, p_fh = principal["box"]
            p_cx = p_fx + p_fw // 2
            p_cy = p_fy + p_fh // 2
            cv2.drawMarker(img, (p_cx, p_cy), (0, 255, 255), cv2.MARKER_CROSS, max(20, w // 25), thick, cv2.LINE_AA)
            cv2.line(img, (cx, cy), (p_cx, p_cy), (100, 100, 255), max(1, thick // 2), cv2.LINE_AA)

        return img, resultados


def modo_udp(engine, target_ip="", porta=5005):
    sys.stdout.reconfigure(line_buffering=True)
    screen_w, screen_h = get_screen_size()
    gemini = GeminiVisionClient(GEMINI_PROMPT_BIOMETRIA, tag="GEMINI BIOMETRIA")

    print("=" * 72)
    print("   ROVER BIOMETRIC AI - STREAM ZERO-DELAY UDP + YUNET + SFACE (HD-5MP)")
    print("=" * 72)
    print(f"Ouvindo na porta UDP: {porta}")
    if target_ip:
        print(f"Alvo ESP32 fixo: {target_ip}")
    else:
        print("Modo de descoberta automatica por broadcast ativo.")
    print("Controles:")
    print("  [C]       Cadastrar Rosto Atual no Banco (usa resolucao cheia atual)")
    print("  [T]       Alternar Auto-Tracking Pan/Tilt da Cabeca (ON/OFF)")
    print("  [ESPACO]  Consultar Gemini Flash (Analise de Humor, Pessoa e Cena)")
    print("  [1..9,0,K,Z] Alternar Resolucao da Camera OV5640 no Rover:")
    print("        [1] QVGA (320x240) | [2] CIF (400x296)   | [3] VGA (640x480)   | [4] SVGA (800x600)")
    print("        [5] XGA (1024x768) | [6] HD (1280x720)   | [7] SXGA (1280x1024)| [8] UXGA 2MP (1600x1200)")
    print("        [9] FHD (1920x1080)| [0] QXGA 3MP        | [K] QHD 2.5K        | [Z] QSXGA 5MP (2560x1920)")
    print("  [+/-]     Ajustar Qualidade JPEG (menor compressao = mais nitido)")
    print("  [F]       Alternar Tela Cheia / Janela  |  [R] Girar Rotacao")
    print("  [I] / [Y] Inverter Sentido Pan / Tilt   |  [L] Listar Cadastrados  |  [Q] Sair")
    print("=" * 72)

    window_name = "Rover Biometric AI (YuNet + SFace) - Zero-Delay UDP"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    is_fullscreen = False

    # Inicia em XGA (1024x768, 4:3 FOV completo, ~19 FPS) em vez de VGA baixo
    receiver = ZeroDelayUdpReceiver(target_ip=target_ip, porta=porta, auto_vga=False, init_cmd=b"5")
    tracker = PanTiltTracker(gain=0.60, deadband_deg=2.2, max_lead=6.0)

    res_atual_label = "XGA 1024x768"
    rotacao_idx = 0
    rot_nomes = ["-90*", "0*", "+90*", "180*"]

    tracking_ativo = False
    ultimo_resultado = []
    ultimo_frame_bruto = None
    ultimo_cad_msg = ""
    t_cad_msg = 0.0

    try:
        while True:
            now = time.time()
            img, fps, mbps, drop_pct, rtt_ms = receiver.get_frame(timeout=0.05)

            if img is not None:
                if rotacao_idx == 0:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif rotacao_idx == 2:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif rotacao_idx == 3:
                    img = cv2.rotate(img, cv2.ROTATE_180)

                ultimo_frame_bruto = img.copy()
                ih, iw, _ = img.shape
                cx, cy = iw // 2, ih // 2

                # Processamento Facial Neural (YuNet rapido + SFace nativo)
                t_ia0 = time.time()
                img, ultimo_resultado = engine.processar_frame(img)
                ia_ms = (time.time() - t_ia0) * 1000.0

                # Rastreamento Pan/Tilt opcional da Cabeca
                if tracking_ativo and len(ultimo_resultado) > 0:
                    principal = max(ultimo_resultado, key=lambda r: r["box"][2] * r["box"][3])
                    fx, fy, fw, fh = principal["box"]
                    fcx = fx + fw // 2
                    fcy = fy + fh // 2
                    cmd_servo = tracker.update(fcx - cx, fcy - cy, now)
                else:
                    cmd_servo = tracker.keepalive(now)

                if cmd_servo:
                    receiver.send_cmd(cmd_servo)

                # Renderizacao limpa em Canvas fixo (evita corte/encolhimento de HUD em 2MP-5MP)
                canvas_w = screen_w if is_fullscreen else 1280
                canvas_h = screen_h if is_fullscreen else 720
                canvas = render_to_canvas(img, canvas_w, canvas_h)

                hud_h = 88
                overlay = canvas[0:hud_h, 0:canvas_w]
                cv2.addWeighted(np.full_like(overlay, (18, 18, 22)), 0.82, overlay, 0.18, 0, overlay)

                status_track = "ON" if tracking_ativo else "OFF"
                cor_track = (0, 255, 128) if tracking_ativo else (0, 220, 255)
                t1 = (f"BIOMETRIA | Real: {iw}x{ih} ({res_atual_label}) | JPEG: {receiver.frame_kb:.0f}KB | "
                      f"FPS: {fps:.1f} | {mbps:.2f} Mbps | RTT: {rtt_ms:.0f}ms | Drop: {drop_pct:.0f}% | IA: {ia_ms:.0f}ms")
                cv2.putText(canvas, t1, (20, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.52, cor_track, 1, cv2.LINE_AA)

                faces_n = len(ultimo_resultado)
                t2 = (f"Rostos: {faces_n} | Track [T]: {status_track} | Pan Inv [I]: {'SIM' if tracker.pan_sign > 0 else 'NAO'} | "
                      f"Rot [R]: {rot_nomes[rotacao_idx]}")
                cv2.putText(canvas, t2, (20, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (240, 240, 240), 1, cv2.LINE_AA)

                t3 = "[C] Cadastrar | [T] Track | [ESPACO/G] Gemini | [1..9,0,K,Z] Res (ate 5MP) | [+/-] Qualid | [F] Tela | [Q] Sair"
                cv2.putText(canvas, t3, (20, 76), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (190, 235, 190), 1, cv2.LINE_AA)

                # Banner inferior unificado: Gemini tem prioridade quando ativo/recente, senao status local
                if gemini.texto_hud and (gemini.ocupado or now - gemini.t_resposta < 15.0):
                    cor_bg = (0, 120, 200) if gemini.ocupado else (20, 20, 26)
                    draw_bottom_banner(canvas, gemini.texto_hud, prefix="[GEMINI FLASH]: ", bg_color=cor_bg)
                elif now - t_cad_msg < 3.0 and ultimo_cad_msg:
                    draw_bottom_banner(canvas, ultimo_cad_msg, bg_color=(0, 110, 55), text_color=(255, 255, 255))

                cv2.imshow(window_name, canvas)
            else:
                receiver.draw_waiting(window_name, screen_w if is_fullscreen else 1280, screen_h if is_fullscreen else 720)

            key = cv2.waitKey(1) & 0xFF
            char_key = chr(key).lower() if 32 <= key <= 126 else ""

            if char_key == "q" or key == 27:
                break
            elif char_key in RESOLUCOES_CAM:
                res_nome, cmd_byte = RESOLUCOES_CAM[char_key]
                receiver.set_resolution_cmd(cmd_byte)
                res_atual_label = res_nome
                ultimo_cad_msg = f"Resolucao alterada para: {res_nome}"
                t_cad_msg = time.time()
                print(f"[CAM] Resolucao enviada para ESP32-S3: {res_nome}")
            elif char_key in ("+", "="):
                receiver.send_cmd(b"+")
                ultimo_cad_msg = "Qualidade JPEG aumentada (+ nitidez)"
                t_cad_msg = time.time()
                print("[CAM] Qualidade JPEG aumentada no Rover")
            elif char_key == "-":
                receiver.send_cmd(b"-")
                ultimo_cad_msg = "Qualidade JPEG reduzida (+ FPS / menos banda)"
                t_cad_msg = time.time()
                print("[CAM] Qualidade JPEG reduzida no Rover")
            elif char_key == "t":
                tracking_ativo = not tracking_ativo
                tracker.reset_track()
                estado_str = "ATIVADO" if tracking_ativo else "DESATIVADO"
                ultimo_cad_msg = f"Tracking Pan/Tilt Facial: {estado_str}"
                t_cad_msg = time.time()
                print(f"[TRACKING] Pan/Tilt da Cabeca {estado_str}")
            elif char_key == "i":
                tracker.pan_sign = -tracker.pan_sign
                ultimo_cad_msg = f"Pan invertido: {'SIM' if tracker.pan_sign > 0 else 'NAO'}"
                t_cad_msg = time.time()
            elif char_key == "y":
                tracker.tilt_sign = -tracker.tilt_sign
                ultimo_cad_msg = f"Tilt invertido: {'SIM' if tracker.tilt_sign > 0 else 'NAO'}"
                t_cad_msg = time.time()
            elif char_key == "r":
                rotacao_idx = (rotacao_idx + 1) % 4
                ultimo_cad_msg = f"Rotacao da camera: {rot_nomes[rotacao_idx]}"
                t_cad_msg = time.time()
            elif char_key == "f":
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(window_name, 1280, 720)
            elif char_key == "c":
                if len(ultimo_resultado) > 0 and ultimo_frame_bruto is not None:
                    alvo = max(ultimo_resultado, key=lambda r: r["box"][2] * r["box"][3])
                    nome = input("\n[CADASTRO BIOMETRICO] Digite o nome para a pessoa na mira: ").strip()
                    if nome:
                        engine.cadastrar_face(nome, ultimo_frame_bruto, alvo["face_data"])
                        msg = f"Rosto de '{nome}' cadastrado ({iw}x{ih})!"
                        ultimo_cad_msg = msg
                        t_cad_msg = time.time()
                        print(f"[OK] {msg}")
                else:
                    print("\n[AVISO] Nenhum rosto detectado na mira no momento para cadastro.")
            elif char_key == "l":
                print("\n--- ROSTOS CADASTRADOS NO BANCO ---")
                if len(engine.known_faces) == 0:
                    print(" (Nenhum rosto cadastrado ainda)")
                else:
                    for n in engine.known_faces.keys():
                        print(f" - {n}")
                print("-----------------------------------\n")
            elif key == ord(" ") or char_key == "g":
                gemini.disparar(ultimo_frame_bruto)

    finally:
        receiver.close()
        cv2.destroyAllWindows()


def modo_imagem(engine, caminho_img, cadastrar_nome=None):
    if not os.path.exists(caminho_img):
        print(f"[ERRO] Arquivo nao encontrado: {caminho_img}")
        return

    img = cv2.imread(caminho_img)
    if img is None:
        print(f"[ERRO] Falha ao carregar imagem: {caminho_img}")
        return

    faces = engine.detectar(img)
    if faces is None or len(faces) == 0:
        print("[AVISO] Nenhum rosto detectado na imagem fornecida.")
        return

    print(f"[OK] {len(faces)} rosto(s) detectado(s) na imagem.")

    if cadastrar_nome:
        principal = max(faces, key=lambda f: f[2] * f[3])
        engine.cadastrar_face(cadastrar_nome, img, principal)
        print(f"[SUCESSO] Rosto '{cadastrar_nome}' cadastrado a partir de: {caminho_img}")
        return

    img_anotada, resultados = engine.processar_frame(img)
    for r in resultados:
        status = f"RECONHECIDO ({r['score']*100:.1f}%)" if r["reconhecido"] else f"DESCONHECIDO ({r['score']*100:.1f}%)"
        print(f" -> Rosto em {r['box']}: {r['nome'].upper()} | {status}")

    out_path = "resultado_reconhecimento.jpg"
    cv2.imwrite(out_path, img_anotada)
    print(f"[OK] Imagem com labels gravada em: {out_path}")

    # Exibe janela se possivel
    try:
        cv2.imshow("Reconhecimento Facial Rover", img_anotada)
        print("Pressione qualquer tecla na janela da imagem para fechar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Rover Biometric AI (YuNet + SFace)")
    parser.add_argument("--udp", action="store_true", help="Iniciar recebimento por stream UDP do Rover")
    parser.add_argument("--ip", type=str, default="", help="IP do ESP32 para stream UDP")
    parser.add_argument("--porta", type=int, default=5005, help="Porta UDP (padrao: 5005)")
    parser.add_argument("--cadastrar", type=str, default="", help="Nome para cadastrar junto com --foto")
    parser.add_argument("--foto", type=str, default="", help="Caminho para imagem estatica (teste ou cadastro)")
    parser.add_argument("--reconhecer", type=str, default="", help="Caminho para imagem para identificar")
    parser.add_argument("--listar", action="store_true", help="Listar nomes cadastrados no banco")
    parser.add_argument("--limpar", type=str, default="", help="Remover nome do banco biometrico")
    args = parser.parse_args()

    engine = FaceEngine()

    if args.listar:
        print("\n=== BANCO BIOMETRICO DE ROSTOS ===")
        if len(engine.known_faces) == 0:
            print(" Nenhum rosto cadastrado no momento.")
        else:
            for i, nome in enumerate(engine.known_faces.keys(), 1):
                print(f" {i}. {nome}")
        print("==================================\n")
        return

    if args.limpar:
        nome = args.limpar
        if nome in engine.known_faces:
            del engine.known_faces[nome]
            engine.salvar_banco()
            print(f"[OK] Rosto '{nome}' removido do banco.")
        else:
            print(f"[AVISO] '{nome}' nao encontrado no banco.")
        return

    if args.cadastrar and args.foto:
        modo_imagem(engine, args.foto, cadastrar_nome=args.cadastrar)
        return

    if args.reconhecer:
        modo_imagem(engine, args.reconhecer)
        return

    # Se nenhum argumento especifico foi dado, padrao e abrir UDP do Rover
    modo_udp(engine, target_ip=args.ip, porta=args.porta)


if __name__ == "__main__":
    main()
