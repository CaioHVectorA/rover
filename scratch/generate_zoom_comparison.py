#!/usr/bin/env python3
"""
Gera um comparativo de zoom em detalhe (crop 1:1 na pata da cadeira e no piso)
para ver exatamente o grau de nitidez de borda e pixelizacao.
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE_IMAGE_PATH = "/home/usuario/.gemini/antigravity-ide/brain/e8fe204c-ffd4-4cc0-91d5-c6645484746e/rover_floor_view_base_1790432852275.jpg"
OUTPUT_DIR = "/home/usuario/Documentos/rover/knowledge/images"

FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def get_font(size, bold=False):
    path = FONT_PATH_BOLD if bold else FONT_PATH_REG
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def generate_zoom_crop():
    base_img = Image.open(BASE_IMAGE_PATH).convert("RGB")
    
    # Vamos recortar a regiao da pata da cadeira (coordenadas relativas)
    # Foto original é aprox 1024x768 ou similar
    bw, bh = base_img.size
    
    # Caixa de recorte: pata da cadeira tocando o piso
    # ~20% a 45% na largura, 15% a 65% na altura
    crop_box_rel = (0.18, 0.15, 0.42, 0.65)
    
    res_list = [
        ("qqvga", 160, 120, "1. QQVGA (160x120)", "#ef4444", "Borda borrada / Blocos de pixels visíveis"),
        ("qvga", 320, 240, "2. QVGA (320x240)", "#10b981", "Borda nítida / Risco e parafuso visíveis"),
        ("cif", 400, 296, "3. CIF (400x296)", "#38bdf8", "Textura da madeira perfeitamente nítida"),
        ("vga", 640, 480, "4. VGA (640x480)", "#f59e0b", "Alta fidelidade / Definição fotográfica")
    ]
    
    panel_w = 1360
    panel_h = 520
    panel = Image.new("RGB", (panel_w, panel_h), color="#090d16")
    draw = ImageDraw.Draw(panel)
    
    # Header
    draw_rounded_rect(draw, (30, 15, panel_w - 30, 85), radius=10, fill="#131c2e", outline="#3b82f6", width=2)
    draw.text((panel_w // 2, 38), "AMPLIAÇÃO EM DETALHE: O QUE O PILOTO REALMENTE ENXERGA", fill="#38bdf8", font=get_font(20, bold=True), anchor="mm")
    draw.text((panel_w // 2, 65), "Zoom de 300% no mesmo obstáculo (pata da cadeira e ranhuras do piso) para comparar nitidez", fill="#94a3b8", font=get_font(13, bold=False), anchor="mm")
    
    crop_display_w = 300
    crop_display_h = 330
    
    for i, (key, rw, rh, title, color, desc) in enumerate(res_list):
        # Downscale para resolucao nativa
        low_res = base_img.resize((rw, rh), Image.Resampling.BILINEAR)
        
        # Crop na versao low res
        cw_start = int(rw * crop_box_rel[0])
        ch_start = int(rh * crop_box_rel[1])
        cw_end = int(rw * crop_box_rel[2])
        ch_end = int(rh * crop_box_rel[3])
        
        cropped = low_res.crop((cw_start, ch_start, cw_end, ch_end))
        
        # Upscale com nearest neighbor para mostrar os pixels reais no display
        scaled_crop = cropped.resize((crop_display_w, crop_display_h), Image.Resampling.NEAREST)
        
        col_x = 35 + i * (crop_display_w + 25)
        col_y = 100
        
        # Box ao redor
        draw_rounded_rect(draw, (col_x, col_y, col_x + crop_display_w, col_y + crop_display_h + 75), radius=10, fill="#0f172a", outline=color, width=2)
        draw.text((col_x + crop_display_w // 2, col_y + 20), title, fill=color, font=get_font(14, bold=True), anchor="mm")
        
        # Imagem
        panel.paste(scaled_crop, (col_x, col_y + 35))
        
        # Descrição
        draw.text((col_x + crop_display_w // 2, col_y + crop_display_h + 52), desc, fill="#e2e8f0", font=get_font(10, bold=False), anchor="mm")
        
    out_file = os.path.join(OUTPUT_DIR, "comparativo_zoom_detalhe.png")
    panel.save(out_file, quality=95)
    print("Salvo:", out_file)

if __name__ == "__main__":
    generate_zoom_crop()
