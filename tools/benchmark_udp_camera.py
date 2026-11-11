#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROVER: Servidor e Benchmark de Transmissao de Video UDP de Baixa Latencia
-----------------------------------------------------------------------
- Recebe datagramas UDP diretos do ESP32-S3-CAM (porta 5005).
- Descarte automatico de frames velhos (Zero-Buffer / Real-Time).
- Mede em tempo real: FPS decodificado, Throughput (Mbps), Perda de Pacotes e RTT.
- Permite alternar resolucoes (QVGA, CIF, VGA, SVGA) e qualidade JPEG pelas teclas 1, 2, 3, 4, +, -.

Requisitos:
    pip install opencv-python numpy
Uso:
    python tools/benchmark_udp_camera.py [--ip <IP_DO_ESP32>] [--porta 5005]
"""

import sys
import time
import socket
import struct
import argparse
import numpy as np
import cv2

MAGIC = 0x52565231  # 'RVR1'
HEADER_FORMAT = "<IIHHHH"  # magic (4B), frame_id (2B), chunk_id (2B), total_chunks (2B), payload_size (2B), timestamp_us (4B) -> 16B
HEADER_SIZE = 16


def parse_args():
    parser = argparse.ArgumentParser(description="Rover UDP Camera Benchmark")
    parser.add_argument("--ip", type=str, default="", help="IP do ESP32 (se vazio, usa broadcast)")
    parser.add_argument("--porta", type=int, default=5005, help="Porta UDP (padrao 5005)")
    return parser.parse_args()


def main():
    args = parse_args()
    porta = args.porta
    target_ip = args.ip

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 * 1024 * 1024)  # 2MB buffer no SO
    sock.bind(("", porta))
    sock.settimeout(0.1)

    print("=" * 65)
    print("  ROVER: BENCHMARK DE VIDEO UDP DE ALTA PERFORMANCE")
    print("=" * 65)
    print(f"Ouvindo na porta UDP: {porta}")
    if target_ip:
        print(f"Conectando diretamente ao ESP32 no IP: {target_ip}")
    else:
        print("Modo Auto-Descoberta: Enviando broadcast 'HELLO' na rede local...")
    print("Controles na janela de video:")
    print("  [1] QVGA (320x240)   [2] CIF (400x296)")
    print("  [3] VGA  (640x480)   [4] SVGA (800x600)")
    print("  [+] Aumentar Qualidade   [-] Reduzir Qualidade")
    print("  [Q] Sair")
    print("=" * 65)

    esp_address = (target_ip, porta) if target_ip else None
    last_hello_time = 0

    # Estruturas de montagem de frame
    current_frame_id = None
    chunks_received = {}
    total_chunks_expected = 0

    # Metricas e estatisticas
    frames_decoded_sec = 0
    frames_dropped_sec = 0
    bytes_received_sec = 0
    last_stats_time = time.time()

    display_fps = 0.0
    display_drop_pct = 0.0
    display_mbps = 0.0
    display_avg_kb = 0.0
    display_res = "Aguardando..."
    display_rtt_ms = 0.0

    last_ping_time = 0
    ping_in_flight = False

    cv2.namedWindow("Rover UDP Camera Benchmark", cv2.WINDOW_AUTOSIZE)

    try:
        while True:
            now = time.time()

            # Envia HELLO periodicamente ate achar o ESP32 (ou a cada 2s para manter vivo)
            if now - last_hello_time > 2.0:
                if target_ip:
                    sock.sendto(b"HELLO", (target_ip, porta))
                else:
                    try:
                        sock.sendto(b"HELLO", ("<broadcast>", porta))
                    except Exception:
                        pass
                last_hello_time = now

            # Envia Ping para medir RTT a cada 1 segundo
            if esp_address and now - last_ping_time > 1.0 and not ping_in_flight:
                ping_payload = b"P" + struct.pack("<d", now)
                sock.sendto(ping_payload, esp_address)
                ping_in_flight = True
                last_ping_time = now

            # Leitura de pacotes UDP
            try:
                data, addr = sock.recvfrom(2048)
                if esp_address is None or esp_address[0] != addr[0]:
                    esp_address = addr
                    print(f"\n[OK] ESP32-S3-CAM localizado em {addr[0]}:{addr[1]}")

                # Resposta de Ping (RTT)
                if data.startswith(b"P") and len(data) == 1 + 8:
                    sent_ts = struct.unpack("<d", data[1:9])[0]
                    display_rtt_ms = (now - sent_ts) * 1000.0
                    ping_in_flight = False
                    continue

                if len(data) < HEADER_SIZE:
                    continue

                magic, f_id, c_id, tot_chunks, p_len, ts_us = struct.unpack(
                    HEADER_FORMAT, data[:HEADER_SIZE]
                )
                if magic != MAGIC:
                    continue

                payload = data[HEADER_SIZE : HEADER_SIZE + p_len]
                bytes_received_sec += len(data)

                # Novo frame detectado
                if f_id != current_frame_id:
                    if current_frame_id is not None and len(chunks_received) < total_chunks_expected:
                        frames_dropped_sec += 1  # Frame anterior ficou incompleto
                    current_frame_id = f_id
                    chunks_received = {}
                    total_chunks_expected = tot_chunks

                chunks_received[c_id] = payload

                # Frame completo recebido!
                if len(chunks_received) == total_chunks_expected and total_chunks_expected > 0:
                    # Remonta os bytes do JPEG
                    jpeg_bytes = bytearray()
                    for idx in range(total_chunks_expected):
                        if idx in chunks_received:
                            jpeg_bytes.extend(chunks_received[idx])

                    frames_decoded_sec += 1
                    avg_kb = len(jpeg_bytes) / 1024.0

                    # Decodifica JPEG com OpenCV
                    img = cv2.imdecode(np.frombuffer(jpeg_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if img is not None:
                        h, w, _ = img.shape
                        display_res = f"{w}x{h}"
                        display_avg_kb = avg_kb

                        # Desenha HUD Overlay no video
                        hud_h = 75
                        overlay = img.copy()
                        cv2.rectangle(overlay, (0, 0), (w, hud_h), (20, 20, 20), -1)
                        cv2.addWeighted(overlay, 0.70, img, 0.30, 0, img)

                        # Linha 1: FPS, Throughput, Resoluçao
                        t1 = f"FPS: {display_fps:.1f}  |  Banda: {display_mbps:.2f} Mbps  |  Res: {display_res} ({display_avg_kb:.1f} KB)"
                        cv2.putText(img, t1, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 128), 2)

                        # Linha 2: Perda de pacotes, RTT e Teclas
                        t2 = f"Drop: {display_drop_pct:.1f}%  |  RTT: {display_rtt_ms:.1f} ms  |  Teclas: [1..4] Res, [+/-] Qual, [Q] Sair"
                        cv2.putText(img, t2, (10, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)

                        cv2.imshow("Rover UDP Camera Benchmark", img)

                    # Limpa para proximo frame
                    chunks_received.clear()
                    current_frame_id = None

            except socket.timeout:
                pass

            # Atualizacao periodica das estatisticas a cada 1 segundo
            dt = now - last_stats_time
            if dt >= 1.0:
                display_fps = frames_decoded_sec / dt
                display_mbps = (bytes_received_sec * 8.0) / (dt * 1000000.0)
                tot_f = frames_decoded_sec + frames_dropped_sec
                display_drop_pct = (frames_dropped_sec * 100.0 / tot_f) if tot_f > 0 else 0.0

                frames_decoded_sec = 0
                frames_dropped_sec = 0
                bytes_received_sec = 0
                last_stats_time = now

            # Interacao pelo teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:  # ESC ou Q
                break
            elif key in [ord("1"), ord("2"), ord("3"), ord("4"), ord("+"), ord("-")]:
                if esp_address:
                    cmd = chr(key).encode("ascii")
                    sock.sendto(cmd, esp_address)
                    print(f"[CMD] Comando enviado para {esp_address[0]}: {chr(key)}")

    finally:
        sock.close()
        cv2.destroyAllWindows()
        print("\nBenchmark encerrado.")


if __name__ == "__main__":
    main()
