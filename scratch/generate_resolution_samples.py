#!/usr/bin/env python3
"""
Gera amostras reais de resolução da câmera do ESP32 a partir da foto base do rover.
Simula o redimensionamento nativo do sensor OV2640/OV5640 e a compressão JPEG (Q=12).
Cria também um painel comparativo lado a lado em alta resolução.
"""

import os
import io
from PIL import Image, ImageDraw, ImageFont

BASE_IMAGE_PATH = "/home/usuario/.gemini/antigravity-ide/brain/e8fe204c-ffd4-4cc0-91d5-c6645484746e/rover_floor_view_base_1790432852275.jpg"
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

def process_and_save():
    base_img = Image.open(BASE_IMAGE_PATH).convert("RGB")
    
    # Resolucao base 4:3
    resolutions = [
        ("qqvga", 160, 120, "QQVGA (160x120)", "35-40 fps", "~4 KB", "30-45 ms", "#ef4444", "Severamente Pixelado (Só enxerga vultos grandes)"),
        ("qvga", 320, 240, "QVGA (320x240)", "25-30 fps", "~10 KB", "40-65 ms", "#10b981", "Padrão de Ouro: Vê piso, batente e obstáculos com fluidez total"),
        ("cif", 400, 296, "CIF (400x296)", "22-25 fps", "~14 KB", "50-80 ms", "#38bdf8", "Excelente Nitidez: Ótimo balanço entre textura e velocidade"),
        ("vga", 640, 480, "VGA (640x480)", "15-20 fps", "~32 KB", "90-140 ms", "#f59e0b", "Alta Definição: Texturas finas nítidas, mas taxa de quadros cai")
    ]

    processed = {}
    
    for key, rw, rh, title, fps, size_kb, lat, color, desc in resolutions:
        # Downscale para o tamanho nativo do sensor
        low_res = base_img.resize((rw, rh), Image.Resampling.BILINEAR)
        
        # Simula compressao JPEG hardware OV2640 (Quality factor ~ 12 / 85%)
        buffer = io.BytesIO()
        low_res.save(buffer, format="JPEG", quality=82)
        buffer.seek(0)
        
        # Salva o arquivo individual nativo
        out_path = os.path.join(OUTPUT_DIR, f"amostra_{key}_{rw}x{rh}.jpg")
        with open(out_path, "wb") as f:
            f.write(buffer.read())
            
        buffer.seek(0)
        simulated_img = Image.open(buffer).convert("RGB")
        processed[key] = {
            "img": simulated_img,
            "title": title,
            "fps": fps,
            "size": size_kb,
            "lat": lat,
            "color": color,
            "desc": desc,
            "w": rw,
            "h": rh
        }
        print(f"Salvo: {out_path}")

    # ========================================================
    # GERAÇÃO DO PAINEL COMPARATIVO LADO A LADO
    # ========================================================
    # Mostra cada uma expandida no mesmo tamanho de tela (como você vê no celular ou PC)
    # Largura total: 1360 px, Altura: 1100 px
    board_w = 1360
    board_h = 1120
    board = Image.new("RGB", (board_w, board_h), color="#090d16")
    bdraw = ImageDraw.Draw(board)

    # Header
    draw_rounded_rect(bdraw, (30, 20, board_w - 30, 110), radius=12, fill="#131c2e", outline="#2563eb", width=2)
    bdraw.text((board_w // 2, 45), "COMPARAÇÃO REAL DE RESOLUÇÕES DE STREAMING NO ROVER (ESP32)", fill="#38bdf8", font=get_font(22, bold=True), anchor="mm")
    bdraw.text((board_w // 2, 80), "Como cada resolução é exibida na tela do celular/computador e o impacto direto no FPS e na latência de pilotagem", fill="#94a3b8", font=get_font(14, bold=False), anchor="mm")

    # Layout de 4 cards em grade 2x2
    # Card width: 625, Card height: 460
    cards_pos = [
        ("qqvga", 35, 130),
        ("qvga", 695, 130),
        ("cif", 35, 615),
        ("vga", 695, 615),
    ]

    display_img_w = 600
    display_img_h = 320 # crop central 4:3 adaptado

    for key, x, y in cards_pos:
        data = processed[key]
        card_w = 630
        card_h = 465
        
        # Borda do card com cor do status
        draw_rounded_rect(bdraw, (x, y, x + card_w, y + card_h), radius=12, fill="#0f172a", outline=data["color"], width=2)
        
        # Header do card
        bdraw.text((x + 20, y + 25), data["title"], fill="#f8fafc", font=get_font(18, bold=True))
        
        # Tag de FPS e Latencia
        badge_text = f"FPS: {data['fps']} | Latência: {data['lat']} | Pacote: {data['size']}"
        bdraw.text((x + card_w - 20, y + 25), badge_text, fill=data["color"], font=get_font(12, bold=True), anchor="ra")
        
        # Imagem re-escalada para tamanho de tela (Nearest Neighbor para simular os pixels reais vistos na tela)
        # O navegador estica o vídeo para caber no player:
        scaled_img = data["img"].resize((display_img_w, display_img_h), Image.Resampling.NEAREST)
        board.paste(scaled_img, (x + 15, y + 55))
        
        # Barra inferior com análise técnica
        draw_rounded_rect(bdraw, (x + 15, y + 385, x + card_w - 15, y + 450), radius=8, fill="#1e293b", outline="#334155", width=1)
        bdraw.text((x + 25, y + 400), "Diagnóstico Visual:", fill="#94a3b8", font=get_font(11, bold=True))
        bdraw.text((x + 25, y + 422), data["desc"], fill="#f1f5f9", font=get_font(12, bold=False))

    board_path = os.path.join(OUTPUT_DIR, "comparativo_visual_resolucoes_esp32.png")
    board.save(board_path, quality=95)
    print(f"Painel comparativo gerado em: {board_path}")

if __name__ == "__main__":
    process_and_save()
