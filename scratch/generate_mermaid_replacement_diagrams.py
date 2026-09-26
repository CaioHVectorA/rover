#!/usr/bin/env python3
"""
Gera os diagramas visuais em PNG para substituir os blocos ```mermaid
que não renderizam em certos visualizadores de Markdown:
1. diagrama_modelo_osi_protocolos.png
2. diagrama_comparativo_protocolos_streaming.png
3. diagrama_sequencia_http_ws_webrtc.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/home/usuario/Documentos/rover/knowledge/images"
FONT_PATH_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def get_font(size, bold=False):
    path = FONT_PATH_BOLD if bold else FONT_PATH_REG
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow_v(draw, start_x, start_y, end_x, end_y, color, width=3):
    draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=width)
    arrow_size = 8
    draw.polygon([
        (end_x, end_y),
        (end_x - arrow_size//1.5, end_y - arrow_size),
        (end_x + arrow_size//1.5, end_y - arrow_size)
    ], fill=color)

def draw_arrow_h(draw, start_x, start_y, end_x, end_y, color, width=3, double=False):
    draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=width)
    arrow_size = 8
    if end_x > start_x:
        draw.polygon([(end_x, end_y), (end_x - arrow_size, end_y - arrow_size//1.5), (end_x - arrow_size, end_y + arrow_size//1.5)], fill=color)
    else:
        draw.polygon([(end_x, end_y), (end_x + arrow_size, end_y - arrow_size//1.5), (end_x + arrow_size, end_y + arrow_size//1.5)], fill=color)

def generate_osi_diagram():
    w, h = 1200, 620
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)

    # Header
    draw_rounded_rect(draw, (30, 15, w - 30, 85), radius=10, fill="#131c2e", outline="#2563eb", width=2)
    draw.text((w // 2, 38), "ONDE OS PROTOCOLOS OPERAM NA PILHA DE REDE (TCP/IP & OSI)", fill="#38bdf8", font=get_font(20, bold=True), anchor="mm")
    draw.text((w // 2, 65), "Mapeamento das camadas de Aplicação, Transporte e Rede no Robô Móvel", fill="#94a3b8", font=get_font(13, bold=False), anchor="mm")

    # Layer 7: Aplicacao
    draw_rounded_rect(draw, (30, 105, w - 30, 260), radius=12, fill="#0f172a", outline="#64748b", width=2)
    draw.text((50, 125), "CAMADA 7: APLICAÇÃO (Semântica dos Dados)", fill="#f8fafc", font=get_font(14, bold=True))

    # 3 Boxes: HTTP, WebSocket, WebRTC
    # Box HTTP
    draw_rounded_rect(draw, (50, 150, 390, 245), radius=8, fill="#1e293b", outline="#ef4444", width=2)
    draw.text((220, 175), "1. HTTP / 1.1", fill="#fca5a5", font=get_font(16, bold=True), anchor="mm")
    draw.text((220, 205), "Request-Response / Half-Duplex", fill="#cbd5e1", font=get_font(12, bold=False), anchor="mm")
    draw.text((220, 225), "REST APIs + MJPEG Stream", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")

    # Box WebSocket
    draw_rounded_rect(draw, (430, 150, 770, 245), radius=8, fill="#1e293b", outline="#10b981", width=2)
    draw.text((600, 175), "2. WebSocket (RFC 6455)", fill="#6ee7b7", font=get_font(16, bold=True), anchor="mm")
    draw.text((600, 205), "Full-Duplex Persistente Único", fill="#cbd5e1", font=get_font(12, bold=False), anchor="mm")
    draw.text((600, 225), "Comandos Rápidos + Frames Binários", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")

    # Box WebRTC
    draw_rounded_rect(draw, (810, 150, 1150, 245), radius=8, fill="#1e293b", outline="#818cf8", width=2)
    draw.text((980, 175), "3. WebRTC / RTSP", fill="#c7d2fe", font=get_font(16, bold=True), anchor="mm")
    draw.text((980, 205), "Peer-to-Peer em Tempo Real", fill="#cbd5e1", font=get_font(12, bold=False), anchor="mm")
    draw.text((980, 225), "Fluxo de Mídia RTP + DataChannels", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")

    # Layer 4: Transporte
    draw_rounded_rect(draw, (30, 300, w - 30, 440), radius=12, fill="#0f172a", outline="#64748b", width=2)
    draw.text((50, 318), "CAMADA 4: TRANSPORTE (Garantia de Entrega vs. Tempo Real)", fill="#f8fafc", font=get_font(14, bold=True))

    # Box TCP
    draw_rounded_rect(draw, (50, 340, 770, 425), radius=8, fill="#1e293b", outline="#3b82f6", width=2)
    draw.text((410, 365), "TCP (Transmission Control Protocol)", fill="#93c5fd", font=get_font(16, bold=True), anchor="mm")
    draw.text((410, 395), "Conexão Segura e Ordenada | Confirmação (ACK) | Retransmissão automática de pacotes perdidos", fill="#cbd5e1", font=get_font(12, bold=False), anchor="mm")

    # Box UDP
    draw_rounded_rect(draw, (810, 340, 1150, 425), radius=8, fill="#1e293b", outline="#a855f7", width=2)
    draw.text((980, 365), "UDP (User Datagram Protocol)", fill="#d8b4fe", font=get_font(16, bold=True), anchor="mm")
    draw.text((980, 395), "Sem confirmação (Fire-and-forget)", fill="#cbd5e1", font=get_font(12, bold=False), anchor="mm")

    # Layer 3: Rede
    draw_rounded_rect(draw, (30, 480, w - 30, 590), radius=12, fill="#0f172a", outline="#64748b", width=2)
    draw.text((50, 498), "CAMADA 3: REDE (Endereçamento e Roteamento Físico)", fill="#f8fafc", font=get_font(14, bold=True))
    draw_rounded_rect(draw, (50, 520, w - 50, 575), radius=8, fill="#1e293b", outline="#475569", width=1)
    draw.text((w // 2, 547), "PROTOCOLO IP (IPv4 / IPv6)  ➔  Rádio Wi-Fi Local (802.11 b/g/n)  ou  Móvel 4G/LTE", fill="#e2e8f0", font=get_font(14, bold=True), anchor="mm")

    # Arrows between layers
    draw_arrow_v(draw, 220, 247, 220, 338, "#ef4444", width=3)
    draw_arrow_v(draw, 600, 247, 600, 338, "#10b981", width=3)
    draw_arrow_v(draw, 980, 247, 980, 338, "#818cf8", width=3)

    draw_arrow_v(draw, 410, 427, 410, 518, "#3b82f6", width=3)
    draw_arrow_v(draw, 980, 427, 980, 518, "#a855f7", width=3)

    out_file = os.path.join(OUTPUT_DIR, "diagrama_modelo_osi_protocolos.png")
    img.save(out_file, quality=95)
    print("Salvo:", out_file)

def generate_streaming_protocols_diagram():
    w, h = 1300, 680
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)

    # Header
    draw_rounded_rect(draw, (30, 15, w - 30, 85), radius=10, fill="#131c2e", outline="#3b82f6", width=2)
    draw.text((w // 2, 38), "PIPELINE DE STREAMING DE VÍDEO NO ESP32: COMPARAÇÃO DOS 3 PROTOCOLOS", fill="#38bdf8", font=get_font(20, bold=True), anchor="mm")
    draw.text((w // 2, 65), "Da captura do sensor OV2640/OV5640 à renderização na tela do operador (Wi-Fi e 4G)", fill="#94a3b8", font=get_font(13, bold=False), anchor="mm")

    # Top Node: Câmera & PSRAM
    draw_rounded_rect(draw, (400, 105, 900, 185), radius=10, fill="#1e293b", outline="#38bdf8", width=2)
    draw.text((650, 130), "📸 SENSOR OV2640 / OV5640 + PSRAM (ESP32-S3)", fill="#f8fafc", font=get_font(15, bold=True), anchor="mm")
    draw.text((650, 160), "Gera JPEG comprimido por Hardware (Q=12) ➔ Gravado por DMA na PSRAM", fill="#94a3b8", font=get_font(12, bold=False), anchor="mm")

    # 3 Branches
    # 1. MJPEG over HTTP
    draw_rounded_rect(draw, (35, 230, 415, 640), radius=10, fill="#0f172a", outline="#ef4444", width=2)
    draw.text((225, 255), "1. MJPEG OVER HTTP", fill="#fca5a5", font=get_font(16, bold=True), anchor="mm")
    draw.text((225, 280), "multipart/x-mixed-replace (TCP)", fill="#f87171", font=get_font(11, bold=True), anchor="mm")
    
    draw.text((50, 315), "• Mecânica:", fill="#94a3b8", font=get_font(12, bold=True))
    draw.text((50, 335), "  Stream infinito de JPEGs em resposta", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((50, 355), "  HTTP contínua.", fill="#cbd5e1", font=get_font(11, bold=False))
    
    draw.text((50, 390), "• Vantagem:", fill="#34d399", font=get_font(12, bold=True))
    draw.text((50, 410), "  Abre em qualquer navegador com", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((50, 430), "  uma simples tag <img src='/stream'>.", fill="#cbd5e1", font=get_font(11, bold=False))
    
    draw.text((50, 465), "• O Gargalo Crítico:", fill="#f87171", font=get_font(12, bold=True))
    draw.text((50, 485), "  Como usa TCP, se um pacote falhar,", fill="#fca5a5", font=get_font(11, bold=False))
    draw.text((50, 505), "  o navegador enfileira tudo (Buffer Lag).", fill="#fca5a5", font=get_font(11, bold=False))
    draw.text((50, 525), "  Você assiste o robô 2s no passado!", fill="#ef4444", font=get_font(11, bold=True))
    
    draw_rounded_rect(draw, (50, 565, 400, 620), radius=6, fill="#450a0a", outline="#ef4444", width=1)
    draw.text((225, 582), "Latência: 120 ms a 400 ms + Delay", fill="#fca5a5", font=get_font(11, bold=True), anchor="mm")
    draw.text((225, 603), "Veredito: Inviável para pilotagem ágil", fill="#f87171", font=get_font(11, bold=False), anchor="mm")

    # 2. WebSocket Binary Streaming
    draw_rounded_rect(draw, (440, 230, 860, 640), radius=10, fill="#0f172a", outline="#10b981", width=2)
    draw.text((650, 255), "2. WEBSOCKET BINARY STREAM", fill="#6ee7b7", font=get_font(16, bold=True), anchor="mm")
    draw.text((650, 280), "Frames Binários com Drop-Frame (TCP)", fill="#34d399", font=get_font(11, bold=True), anchor="mm")
    
    draw.text((455, 315), "• Mecânica:", fill="#94a3b8", font=get_font(12, bold=True))
    draw.text((455, 335), "  JPEGs enviados em frames binários crus", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((455, 355), "  pelo mesmo canal de comandos.", fill="#cbd5e1", font=get_font(11, bold=False))
    
    draw.text((455, 390), "• Vantagem (A Grande Sacada):", fill="#34d399", font=get_font(12, bold=True))
    draw.text((455, 410), "  Descarte inteligente no JavaScript:", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((455, 430), "  se um frame atrasar no 4G, ele é", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((455, 450), "  descartado na hora. Zero buffer lag!", fill="#34d399", font=get_font(11, bold=True))
    
    draw.text((455, 485), "• Impacto no ESP32:", fill="#38bdf8", font=get_font(12, bold=True))
    draw.text((455, 505), "  Usa apenas 1 socket aberto constante.", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((455, 525), "  Consumo de memória RAM mínimo.", fill="#cbd5e1", font=get_font(11, bold=False))
    
    draw_rounded_rect(draw, (455, 565, 845, 620), radius=6, fill="#064e3b", outline="#10b981", width=1)
    draw.text((650, 582), "Latência: 40 ms a 65 ms (Wi-Fi) | 75-115 ms (4G)", fill="#a7f3d0", font=get_font(11, bold=True), anchor="mm")
    draw.text((650, 603), "Veredito: 🥇 VENCEDOR GERAL (Equilíbrio)", fill="#34d399", font=get_font(11, bold=True), anchor="mm")

    # 3. WebRTC / RTSP sobre UDP
    draw_rounded_rect(draw, (885, 230, 1265, 640), radius=10, fill="#0f172a", outline="#818cf8", width=2)
    draw.text((1075, 255), "3. WEBRTC / RTSP (UDP)", fill="#c7d2fe", font=get_font(16, bold=True), anchor="mm")
    draw.text((1075, 280), "Datagramas em Tempo Real P2P", fill="#a5b4fc", font=get_font(11, bold=True), anchor="mm")
    
    draw.text((900, 315), "• Mecânica:", fill="#94a3b8", font=get_font(12, bold=True))
    draw.text((900, 335), "  Transmissão via UDP sem retransmissão.", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((900, 355), "  Pacote perdido no ar é ignorado.", fill="#cbd5e1", font=get_font(11, bold=False))
    
    draw.text((900, 390), "• Vantagem:", fill="#34d399", font=get_font(12, bold=True))
    draw.text((900, 410), "  Menor latência teórica possível.", fill="#cbd5e1", font=get_font(11, bold=False))
    draw.text((900, 430), "  Excelente para áudio e vídeo síncronos.", fill="#cbd5e1", font=get_font(11, bold=False))
    
    draw.text((900, 465), "• O Gargalo no ESP32:", fill="#f87171", font=get_font(12, bold=True))
    draw.text((900, 485), "  ESP32 não tem H.264 por hardware!", fill="#fca5a5", font=get_font(11, bold=True))
    draw.text((900, 505), "  Criptografia DTLS/SRTP esgota a CPU.", fill="#fca5a5", font=get_font(11, bold=False))
    draw.text((900, 525), "  Furar CGNAT exige servidores STUN/TURN.", fill="#fca5a5", font=get_font(11, bold=False))
    
    draw_rounded_rect(draw, (900, 565, 1250, 620), radius=6, fill="#1e1b4b", outline="#818cf8", width=1)
    draw.text((1075, 582), "Latência: 30 ms a 55 ms (Ultra-Baixa)", fill="#c7d2fe", font=get_font(11, bold=True), anchor="mm")
    draw.text((1075, 603), "Veredito: Complexidade excessiva para ESP32", fill="#a5b4fc", font=get_font(11, bold=False), anchor="mm")

    # Arrows from top node to the 3 branches
    draw_arrow_v(draw, 500, 187, 225, 228, "#ef4444", width=3)
    draw_arrow_v(draw, 650, 187, 650, 228, "#10b981", width=3)
    draw_arrow_v(draw, 800, 187, 1075, 228, "#818cf8", width=3)

    out_file = os.path.join(OUTPUT_DIR, "diagrama_comparativo_protocolos_streaming.png")
    img.save(out_file, quality=95)
    print("Salvo:", out_file)

def generate_sequence_diagram():
    w, h = 1300, 750
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)

    # Header
    draw_rounded_rect(draw, (30, 15, w - 30, 85), radius=10, fill="#131c2e", outline="#3b82f6", width=2)
    draw.text((w // 2, 38), "COMPORTAMENTO DE REDE: CICLO DE ENVIOS (HTTP vs. WEBSOCKET vs. WEBRTC)", fill="#38bdf8", font=get_font(20, bold=True), anchor="mm")
    draw.text((w // 2, 65), "O que acontece nos buffers do microcontrolador a cada ciclo de comando e streaming", fill="#94a3b8", font=get_font(13, bold=False), anchor="mm")

    # 3 Horizontal comparison sections
    # 1. HTTP Sequence
    draw_rounded_rect(draw, (30, 105, w - 30, 290), radius=10, fill="#2a0d0d", outline="#ef4444", width=2)
    draw.text((50, 125), "1. FLUXO HTTP TRADICIONAL (A cada comando gera ciclo completo de handshake e parser de texto)", fill="#fca5a5", font=get_font(14, bold=True))
    
    # Flow line HTTP
    draw.text((60, 160), "📱 Celular", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((550, 160), "🧠 ESP32 (LwIP / Heap)", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((1050, 160), "⚡ Nano (Motores)", fill="#f8fafc", font=get_font(13, bold=True))

    draw_arrow_h(draw, 140, 190, 530, 190, "#f87171", width=2)
    draw.text((330, 180), "POST /move (800B Headers) + SYN/ACK", fill="#fecaca", font=get_font(11, bold=False), anchor="mb")

    draw_arrow_h(draw, 740, 190, 1030, 190, "#f87171", width=2)
    draw.text((885, 180), "TX: envia comando atrasado", fill="#fecaca", font=get_font(11, bold=False), anchor="mb")

    draw_arrow_h(draw, 530, 230, 140, 230, "#f87171", width=2)
    draw.text((330, 220), "HTTP/1.1 200 OK  ➔  Socket entra em TIME_WAIT (2 min retido no Heap)", fill="#fca5a5", font=get_font(11, bold=True), anchor="mb")

    draw.text((60, 260), "⚠️ Se você enviar 20 comandos/s, o ESP32 esgota os sockets livres do LwIP e trava com 'Connection Refused'.", fill="#f87171", font=get_font(12, bold=False))

    # 2. WebSocket Sequence
    draw_rounded_rect(draw, (30, 310, w - 30, 510), radius=10, fill="#063828", outline="#10b981", width=2)
    draw.text((50, 330), "2. FLUXO WEBSOCKET (1 Handshake inicial ➔ Canal permanente de dados puros e bidirecionais)", fill="#6ee7b7", font=get_font(14, bold=True))

    draw.text((60, 365), "📱 Celular", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((550, 365), "🧠 ESP32 (Buffer Fixo)", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((1050, 365), "⚡ Nano (Motores)", fill="#f8fafc", font=get_font(13, bold=True))

    draw_arrow_h(draw, 140, 395, 530, 395, "#34d399", width=2)
    draw.text((330, 385), "Frame Binário: <180,180,90> (Apenas 6B overhead)", fill="#a7f3d0", font=get_font(11, bold=False), anchor="mb")

    draw_arrow_h(draw, 740, 395, 1030, 395, "#34d399", width=2)
    draw.text((885, 385), "TX: repassa em < 1 ms via UART", fill="#a7f3d0", font=get_font(11, bold=True), anchor="mb")

    draw_arrow_h(draw, 530, 440, 140, 440, "#34d399", width=2)
    draw.text((330, 430), "Frame JPEG Binário (Opcode 0x2) ➔ Renderiza no Canvas com Drop-Frame", fill="#6ee7b7", font=get_font(11, bold=True), anchor="mb")

    draw.text((60, 480), "✅ 1 único socket alocado do início ao fim. Zero risco de vazamento de memória RAM ou travamento.", fill="#34d399", font=get_font(12, bold=True))

    # 3. WebRTC Sequence
    draw_rounded_rect(draw, (30, 530, w - 30, 725), radius=10, fill="#1e1b4b", outline="#818cf8", width=2)
    draw.text((50, 550), "3. FLUXO WEBRTC / RTSP (UDP Datagramas P2P com criptografia DTLS/SRTP)", fill="#c7d2fe", font=get_font(14, bold=True))

    draw.text((60, 585), "📱 Celular", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((550, 585), "🧠 ESP32 (CPU Alta)", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((1050, 585), "⚡ Nano (Motores)", fill="#f8fafc", font=get_font(13, bold=True))

    draw_arrow_h(draw, 140, 615, 530, 615, "#a5b4fc", width=2)
    draw.text((330, 605), "DataChannel UDP (SCTP sobre DTLS)", fill="#c7d2fe", font=get_font(11, bold=False), anchor="mb")

    draw_arrow_h(draw, 740, 615, 1030, 615, "#a5b4fc", width=2)
    draw.text((885, 605), "TX: repassa comando", fill="#c7d2fe", font=get_font(11, bold=False), anchor="mb")

    draw_arrow_h(draw, 530, 660, 140, 660, "#a5b4fc", width=2)
    draw.text((330, 650), "Pacote RTP UDP (Se perder pacote, não retransmite - latência pura)", fill="#c7d2fe", font=get_font(11, bold=True), anchor="mb")

    draw.text((60, 695), "⚠️ Excelente latência física, mas o processador do ESP32 atinge 85% de uso apenas mantendo a criptografia DTLS.", fill="#a5b4fc", font=get_font(12, bold=False))

    out_file = os.path.join(OUTPUT_DIR, "diagrama_sequencia_http_ws_webrtc.png")
    img.save(out_file, quality=95)
    print("Salvo:", out_file)

if __name__ == "__main__":
    generate_osi_diagram()
    generate_streaming_protocols_diagram()
    generate_sequence_diagram()
