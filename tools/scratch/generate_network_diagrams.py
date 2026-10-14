#!/usr/bin/env python3
"""
Gera diagramas técnicos de rede para a pasta knowledge/images/:
1. topologia_redes_wifi_local_vs_4g_remoto.png
2. fluxo_streaming_mjpeg_buffer_vs_drop.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

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

def draw_arrow_h(draw, start_x, start_y, end_x, end_y, color, width=3, double=False):
    draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=width)
    # Head at end
    arrow_size = 8
    if end_x > start_x:
        draw.polygon([(end_x, end_y), (end_x - arrow_size, end_y - arrow_size//1.5), (end_x - arrow_size, end_y + arrow_size//1.5)], fill=color)
    else:
        draw.polygon([(end_x, end_y), (end_x + arrow_size, end_y - arrow_size//1.5), (end_x + arrow_size, end_y + arrow_size//1.5)], fill=color)
    if double:
        if end_x > start_x:
            draw.polygon([(start_x, start_y), (start_x + arrow_size, start_y - arrow_size//1.5), (start_x + arrow_size, start_y + arrow_size//1.5)], fill=color)
        else:
            draw.polygon([(start_x, start_y), (start_x - arrow_size, start_y - arrow_size//1.5), (start_x - arrow_size, start_y + arrow_size//1.5)], fill=color)

def generate_diagram_1():
    w, h = 1300, 840
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)

    # Header Banner
    draw_rounded_rect(draw, (30, 20, w - 30, 110), radius=12, fill="#131c2e", outline="#2563eb", width=2)
    draw.text((w // 2, 45), "ARQUITETURA DE REDES DO ROVER (NÃO É FPV ANALÓGICO / 5.8 GHz!)", fill="#38bdf8", font=get_font(23, bold=True), anchor="mm")
    draw.text((w // 2, 80), "Teleoperação de Robô Móvel em Redes IP Padronizadas: Wi-Fi Local (Baixa Latência) vs. 4G/LTE (Alcance Global)", fill="#94a3b8", font=get_font(15, bold=False), anchor="mm")

    # ==========================
    # CENÁRIO 1: WI-FI LOCAL
    # ==========================
    box1 = (30, 130, w - 30, 440)
    draw_rounded_rect(draw, box1, radius=12, fill="#0f172a", outline="#10b981", width=2)
    # Title badge
    draw_rounded_rect(draw, (50, 145, 480, 185), radius=6, fill="#064e3b", outline="#10b981", width=1)
    draw.text((65, 155), "CENÁRIO 1: REDE WI-FI LOCAL (Ponto de Acesso ou LAN)", fill="#34d399", font=get_font(15, bold=True))

    # Node: Piloto
    draw_rounded_rect(draw, (60, 215, 340, 395), radius=10, fill="#1e293b", outline="#475569", width=2)
    draw.text((200, 245), "📱 PILOTO / OPERADOR", fill="#f8fafc", font=get_font(17, bold=True), anchor="mm")
    draw.text((200, 275), "Smartphone / PC Web", fill="#38bdf8", font=get_font(14, bold=False), anchor="mm")
    draw.text((200, 310), "IP: 192.168.4.2", fill="#e2e8f0", font=get_font(14, bold=True), anchor="mm")
    draw.text((200, 345), "Navegador Web / App PWA", fill="#94a3b8", font=get_font(12, bold=False), anchor="mm")
    draw.text((200, 370), "Joystick Virtual + Tela", fill="#64748b", font=get_font(11, bold=False), anchor="mm")

    # Middle Connection Info: Wi-Fi
    draw_rounded_rect(draw, (440, 230, 830, 380), radius=10, fill="#0f2620", outline="#059669", width=1)
    draw.text((635, 255), "📶 LINK WI-FI DIRETO (Sem Internet)", fill="#34d399", font=get_font(15, bold=True), anchor="mm")
    draw.text((635, 285), "• Comandos: WebSocket (Full-Duplex ~15 ms)", fill="#f8fafc", font=get_font(13, bold=False), anchor="mm")
    draw.text((635, 310), "• Vídeo: MJPEG Stream HTTP (QVGA 30 fps)", fill="#f8fafc", font=get_font(13, bold=False), anchor="mm")
    draw.text((635, 335), "• Latência de Ponta a Ponta: 30 ms a 55 ms", fill="#a7f3d0", font=get_font(13, bold=True), anchor="mm")
    draw.text((635, 360), "• Alcance: 20 m a 60 m (Sem consumo de dados)", fill="#6ee7b7", font=get_font(12, bold=False), anchor="mm")

    draw_arrow_h(draw, 345, 305, 435, 305, "#34d399", width=3, double=True)
    draw_arrow_h(draw, 835, 305, 925, 305, "#34d399", width=3, double=True)

    # Node: Rover
    draw_rounded_rect(draw, (930, 215, 1240, 395), radius=10, fill="#1e293b", outline="#475569", width=2)
    draw.text((1085, 245), "🤖 ROVER (CABEÇA + CHASSI)", fill="#f8fafc", font=get_font(16, bold=True), anchor="mm")
    draw.text((1085, 275), "ESP32-S3 (SoftAP / STA)", fill="#38bdf8", font=get_font(14, bold=False), anchor="mm")
    draw.text((1085, 310), "IP: 192.168.4.1 (rover.local)", fill="#e2e8f0", font=get_font(14, bold=True), anchor="mm")
    draw.text((1085, 345), "Chicote TX ➔ RX Arduino Nano", fill="#fbbf24", font=get_font(12, bold=True), anchor="mm")
    draw.text((1085, 370), "4 Motores JGA-050 + 2 Servos", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")

    # ==========================
    # CENÁRIO 2: 4G / INTERNET
    # ==========================
    box2 = (30, 460, w - 30, 810)
    draw_rounded_rect(draw, box2, radius=12, fill="#0f172a", outline="#f59e0b", width=2)
    # Title badge
    draw_rounded_rect(draw, (50, 475, 570, 515), radius=6, fill="#78350f", outline="#f59e0b", width=1)
    draw.text((65, 485), "CENÁRIO 2: TELEOPERAÇÃO VIA 4G/LTE (Alcance Ilimitado / Qualquer Lugar)", fill="#fde68a", font=get_font(14, bold=True))

    # Node: Piloto em 4G/Fibra
    draw_rounded_rect(draw, (60, 545, 330, 765), radius=10, fill="#1e293b", outline="#475569", width=2)
    draw.text((195, 575), "📱 PILOTO REMOTO", fill="#f8fafc", font=get_font(16, bold=True), anchor="mm")
    draw.text((195, 605), "Em Qualquer Lugar do Mundo", fill="#38bdf8", font=get_font(13, bold=False), anchor="mm")
    draw.text((195, 635), "Conectado via 4G / 5G / Fibra", fill="#e2e8f0", font=get_font(12, bold=False), anchor="mm")
    draw.text((195, 680), "Abre conexão segura de saída:", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")
    draw.text((195, 705), "wss://servidor-rover.com", fill="#34d399", font=get_font(12, bold=True), anchor="mm")
    draw.text((195, 740), "Comandos ➔ | 🎦 Vídeo ⬅", fill="#f59e0b", font=get_font(12, bold=True), anchor="mm")

    draw_arrow_h(draw, 335, 655, 475, 655, "#f59e0b", width=3, double=True)

    # Node: Servidor Relay Nuvem (Resolve CGNAT)
    draw_rounded_rect(draw, (480, 535, 800, 785), radius=10, fill="#1e1b4b", outline="#818cf8", width=2)
    draw.text((640, 565), "☁️ SERVIDOR RELAY / BROKER", fill="#c7d2fe", font=get_font(16, bold=True), anchor="mm")
    draw.text((640, 595), "Nuvem (AWS / DigitalOcean / VPS / Tailscale)", fill="#a5b4fc", font=get_font(12, bold=False), anchor="mm")
    draw.text((640, 635), "POR QUE É OBRIGATÓRIO NO 4G?", fill="#f87171", font=get_font(13, bold=True), anchor="mm")
    draw.text((640, 665), "Operadoras 4G usam CGNAT:", fill="#e2e8f0", font=get_font(12, bold=False), anchor="mm")
    draw.text((640, 690), "O robô NÃO recebe IP público direto!", fill="#fca5a5", font=get_font(12, bold=True), anchor="mm")
    draw.text((640, 725), "Ambos conectam 'de dentro pra fora'", fill="#86efac", font=get_font(12, bold=False), anchor="mm")
    draw.text((640, 755), "O Relay repassa os bytes de vídeo e controle", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")

    draw_arrow_h(draw, 805, 655, 935, 655, "#f59e0b", width=3, double=True)

    # Node: Rover em 4G
    draw_rounded_rect(draw, (940, 545, 1240, 765), radius=10, fill="#1e293b", outline="#475569", width=2)
    draw.text((1090, 575), "🤖 ROVER NO CAMPO (4G)", fill="#f8fafc", font=get_font(16, bold=True), anchor="mm")
    draw.text((1090, 605), "ESP32-S3 + Módulo 4G/Roteador", fill="#38bdf8", font=get_font(13, bold=False), anchor="mm")
    draw.text((1090, 635), "Modem LTE (ex: SIM7600 ou MiFi)", fill="#e2e8f0", font=get_font(12, bold=False), anchor="mm")
    draw.text((1090, 680), "Transmissão de Vídeo:", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")
    draw.text((1090, 705), "MJPEG / WebSocket Drop-Frame", fill="#34d399", font=get_font(12, bold=True), anchor="mm")
    draw.text((1090, 735), "Latência Típica: 70 ms a 140 ms", fill="#fde68a", font=get_font(12, bold=True), anchor="mm")

    img.save("/home/usuario/Documentos/rover/knowledge/images/topologia_redes_wifi_local_vs_4g_remoto.png")
    print("Diagrama 1 gerado!")

def generate_diagram_2():
    w, h = 1300, 720
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)

    # Header Banner
    draw_rounded_rect(draw, (30, 20, w - 30, 110), radius=12, fill="#131c2e", outline="#3b82f6", width=2)
    draw.text((w // 2, 45), "FLUXO DE STREAMING DE VÍDEO EM REDES IP: BUFFER TRADICIONAL VS. DESCARTE DE FRAME", fill="#38bdf8", font=get_font(21, bold=True), anchor="mm")
    draw.text((w // 2, 80), "Como evitar o atraso acumulado ('vídeo elástico') quando a rede Wi-Fi oscila ou opera em 4G com latência variável", fill="#94a3b8", font=get_font(14, bold=False), anchor="mm")

    # Flow Steps
    # Step 1: Sensor & DMA
    draw_rounded_rect(draw, (40, 140, 310, 320), radius=10, fill="#1e293b", outline="#64748b", width=2)
    draw.text((175, 170), "1. CÂMERA & DMA", fill="#f8fafc", font=get_font(16, bold=True), anchor="mm")
    draw.text((175, 200), "Sensor OV2640 / OV5640", fill="#38bdf8", font=get_font(13, bold=False), anchor="mm")
    draw.text((175, 235), "Comprime JPEG em silício", fill="#e2e8f0", font=get_font(12, bold=False), anchor="mm")
    draw.text((175, 260), "Frame QVGA (~10 KB)", fill="#34d399", font=get_font(13, bold=True), anchor="mm")
    draw.text((175, 290), "Duplo Buffer (fb_count=2)", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")

    draw_arrow_h(draw, 315, 230, 375, 230, "#38bdf8", width=3)

    # Step 2: Segmentação TCP / Rádio
    draw_rounded_rect(draw, (380, 140, 670, 320), radius=10, fill="#1e293b", outline="#64748b", width=2)
    draw.text((525, 170), "2. TRANSPORTE TCP / IP", fill="#f8fafc", font=get_font(16, bold=True), anchor="mm")
    draw.text((525, 200), "Pilha LwIP (ESP32)", fill="#38bdf8", font=get_font(13, bold=False), anchor="mm")
    draw.text((525, 235), "Quebra em ~7 pacotes MTU", fill="#e2e8f0", font=get_font(12, bold=False), anchor="mm")
    draw.text((525, 260), "TCP_NODELAY (Sem Nagle)", fill="#34d399", font=get_font(13, bold=True), anchor="mm")
    draw.text((525, 290), "Rádio Wi-Fi ou Modem 4G", fill="#94a3b8", font=get_font(11, bold=False), anchor="mm")

    draw_arrow_h(draw, 675, 230, 735, 230, "#38bdf8", width=3)

    # Step 3: Recepção
    draw_rounded_rect(draw, (740, 140, 1260, 320), radius=10, fill="#1e293b", outline="#64748b", width=2)
    draw.text((1000, 170), "3. CHEGADA NO RECEPTOR (Celular / PC)", fill="#f8fafc", font=get_font(16, bold=True), anchor="mm")
    draw.text((1000, 205), "Pacotes chegam pelo rádio com jitter (variação de atraso)", fill="#cbd5e1", font=get_font(13, bold=False), anchor="mm")
    draw.text((1000, 240), "Aqui reside a decisão que define a pilotagem do robô:", fill="#fde68a", font=get_font(13, bold=True), anchor="mm")
    draw.text((1000, 275), "O que fazer quando um frame chega atrasado por oscilação do 4G?", fill="#94a3b8", font=get_font(12, bold=False), anchor="mm")

    # Bottom Comparison: Buffer vs Drop Frame
    # Bottom Left: Bad approach
    draw_rounded_rect(draw, (40, 360, 630, 680), radius=10, fill="#450a0a", outline="#ef4444", width=2)
    draw.text((335, 395), "❌ MÉTODO RUIM: BUFFER ACUMULATIVO", fill="#fca5a5", font=get_font(16, bold=True), anchor="mm")
    draw.text((335, 425), "Padrão de players de vídeo tradicionais (YouTube, tag <img> simples)", fill="#fecaca", font=get_font(12, bold=False), anchor="mm")
    
    draw.text((70, 465), "• Se o 4G oscilar por 1 segundo, o navegador enfileira os frames atrasados.", fill="#fee2e2", font=get_font(12, bold=False))
    draw.text((70, 500), "• Quando a conexão volta, ele reproduz tudo acelerado em fast-forward!", fill="#fee2e2", font=get_font(12, bold=False))
    draw.text((70, 535), "• Consequência no Robô: VOCÊ ENXERGA O PASSADO!", fill="#f87171", font=get_font(13, bold=True))
    draw.text((70, 570), "• Você manda o robô parar, mas ele bate na parede porque a imagem na", fill="#fca5a5", font=get_font(12, bold=False))
    draw.text((70, 595), "  tela estava atrasada em 2 segundos.", fill="#fca5a5", font=get_font(12, bold=False))
    draw.text((335, 645), "Latência acumulada: 1.500 ms a 3.000 ms (Inviável)", fill="#ef4444", font=get_font(14, bold=True), anchor="mm")

    # Bottom Right: Good approach
    draw_rounded_rect(draw, (670, 360, 1260, 680), radius=10, fill="#064e3b", outline="#10b981", width=2)
    draw.text((965, 395), "✅ MÉTODO OTIMIZADO: DESCARTE DE FRAME (DROP OLD)", fill="#a7f3d0", font=get_font(16, bold=True), anchor="mm")
    draw.text((965, 425), "Streaming via WebSocket / Canvas com descarte inteligente em JS", fill="#d1fae5", font=get_font(12, bold=False), anchor="mm")
    
    draw.text((700, 465), "• O JavaScript só desenha o frame se ele for o mais recente disponível.", fill="#ecfdf5", font=get_font(12, bold=False))
    draw.text((700, 500), "• Se o frame anterior atrasou, ele é SUMARIAMENTE DESCARTADO.", fill="#ecfdf5", font=get_font(12, bold=False))
    draw.text((700, 535), "• Consequência no Robô: TEMPO REAL PERFEITO E SINCRONIZADO!", fill="#34d399", font=get_font(13, bold=True))
    draw.text((700, 570), "• Pode haver um micro-salto na imagem, mas o piloto SEMPRE vê a", fill="#a7f3d0", font=get_font(12, bold=False))
    draw.text((700, 595), "  posição física real do robô no momento exato do comando.", fill="#a7f3d0", font=get_font(12, bold=False))
    draw.text((965, 645), "Latência mantida: 35 ms a 80 ms (Ideal para Teleoperação)", fill="#10b981", font=get_font(14, bold=True), anchor="mm")

    img.save("/home/usuario/Documentos/rover/knowledge/images/fluxo_streaming_mjpeg_buffer_vs_drop.png")
    print("Diagrama 2 gerado!")

if __name__ == "__main__":
    generate_diagram_1()
    generate_diagram_2()
