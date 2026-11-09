#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera imagens (prints de alta resolução) do Esquemático e do Layout da PCB do Chassi (v2_2esps):
- docs/hardware/kicad/rover_pcb_v2_chassi/preview_pcb_top.png
- docs/hardware/kicad/rover_pcb_v2_chassi/preview_esquematico.png
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/hardware/kicad/rover_pcb_v2_chassi"
OUT.mkdir(parents=True, exist_ok=True)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def fnt(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

# ==============================================================================
# 1. RENDERIZAÇÃO DA PCB COMPACTA (85 mm × 65 mm) — ESTILO KICAD PCBNEW
# ==============================================================================
SCALE = 18  # 18 pixels por mm
MARGIN_X = 95
MARGIN_Y = 125
W_MM, H_MM = 85.0, 65.0
P = 2.54

IMG_W = int(W_MM * SCALE + MARGIN_X * 2)
IMG_H = int(H_MM * SCALE + MARGIN_Y * 2 + 65)

im = Image.new("RGB", (IMG_W, IMG_H), "#0f172a")
d = ImageDraw.Draw(im)

def px(x_mm):
    return int(MARGIN_X + x_mm * SCALE)

def py(y_mm):
    return int(MARGIN_Y + y_mm * SCALE)

# Cabeçalho da imagem
d.text((MARGIN_X, 20), "ROVER 4WD — LAYOUT DA PCB COMPACTA DO CHASSI (85,0 × 65,0 mm)", fill="#f8fafc", font=fnt(25, True))
d.text((MARGIN_X, 55), "Arquitetura v2_2esps • ESP32 DevKit V1 (30p) + TB6612FNG + Mini 560 + Áudio I2S (MAX98357A / INMP441) + OLED + WS2812B", fill="#94a3b8", font=fnt(15))

# Corpo verde-escuro de máscara de solda da PCB
d.rectangle([px(0), py(0), px(W_MM), py(H_MM)], fill="#113624", outline="#eab308", width=4)

# Grade sutil de 2.54 mm
cx = 0.0
while cx <= W_MM:
    d.line([px(cx), py(0), px(cx), py(H_MM)], fill="#16422d", width=1)
    cx += P
cy = 0.0
while cy <= H_MM:
    d.line([px(0), py(cy), px(W_MM), py(cy)], fill="#16422d", width=1)
    cy += P

# Cotas externas
d.text((px(W_MM / 2), py(-1.6)), "←  85,0 mm  →", fill="#eab308", font=fnt(15, True), anchor="mm")
d.text((px(-2.2), py(H_MM / 2)), "65,0\nmm", fill="#eab308", font=fnt(15, True), anchor="rm")

# Furos M3 nos 4 cantos
for hx, hy in [(4.0, 4.0), (W_MM - 4.0, 4.0), (4.0, H_MM - 4.0), (W_MM - 4.0, H_MM - 4.0)]:
    r_ext = int(3.0 * SCALE)
    r_int = int(1.6 * SCALE)
    d.ellipse([px(hx) - r_ext, py(hy) - r_ext, px(hx) + r_ext, py(hy) + r_ext], fill="#d4af37", outline="#f8fafc", width=2)
    d.ellipse([px(hx) - r_int, py(hy) - r_int, px(hx) + r_int, py(hy) + r_int], fill="#0f172a")

# Trilhas roteadas (B.Cu em Azul/Ciano e F.Cu em Vermelho)
tracks = [
    # B.Cu (Cobre Inferior)
    ("B.Cu", 1.0, [(4.5, 11.0), (11.5, 11.0)]),
    ("B.Cu", 1.0, [(11.5, 13.54), (17.5, 9.5)]),
    ("B.Cu", 1.0, [(11.5, 13.54), (11.0, 26.7)]),
    ("B.Cu", 0.5, [(11.0, 26.7), (11.0, 50.0)]),
    ("B.Cu", 0.8, [(11.0, 34.32), (4.0, 34.3)]),
    ("B.Cu", 0.8, [(11.0, 36.86), (4.0, 36.84)]),
    ("B.Cu", 0.8, [(11.0, 39.40), (4.0, 41.9)]),
    ("B.Cu", 0.8, [(11.0, 41.94), (4.0, 44.44)]),
    ("B.Cu", 0.45, [(31.0, 26.70), (23.7, 26.70)]),
    ("B.Cu", 0.45, [(31.0, 29.24), (23.7, 31.78)]),
    ("B.Cu", 0.45, [(31.0, 36.86), (23.7, 36.86)]),
    ("B.Cu", 0.45, [(31.0, 39.40), (23.7, 39.40)]),
    ("B.Cu", 0.45, [(31.0, 44.48), (26.5, 44.48), (26.5, 34.32), (23.7, 34.32)]),
    ("B.Cu", 0.45, [(18.62, 50.0), (18.62, 54.0)]),
    ("B.Cu", 0.45, [(18.62, 50.0), (29.0, 50.0), (29.0, 21.62), (31.0, 21.62)]),
    ("B.Cu", 0.45, [(56.4, 39.40), (63.5, 44.54), (71.5, 49.0)]),
    ("B.Cu", 0.5, [(63.5, 47.08), (79.12, 49.0)]),
    ("B.Cu", 0.45, [(56.4, 29.24), (59.2, 29.24), (59.2, 55.0), (27.54, 55.0), (27.54, 60.0)]),
    ("B.Cu", 0.45, [(56.4, 26.70), (60.2, 26.70), (60.2, 56.0), (40.54, 56.0), (40.54, 60.0)]),
    ("B.Cu", 0.45, [(56.4, 41.94), (53.54, 54.0), (53.54, 60.0)]),
    ("B.Cu", 0.45, [(56.4, 14.0), (65.0, 14.0), (65.0, 20.66), (69.0, 20.66)]),
    ("B.Cu", 0.45, [(56.4, 31.78), (69.0, 23.20), (76.0, 41.16)]),
    ("B.Cu", 0.45, [(31.0, 24.16), (31.0, 7.2), (83.2, 7.2), (83.2, 43.70), (76.0, 43.70)]),
    # F.Cu (Cobre Superior)
    ("F.Cu", 1.0, [(25.5, 9.5), (28.0, 9.5), (28.0, 49.56), (31.0, 49.56)]),
    ("F.Cu", 0.8, [(31.0, 49.56), (31.0, 57.5), (14.0, 57.5), (14.0, 60.0)]),
    ("F.Cu", 0.8, [(25.0, 57.5), (25.0, 60.0)]),
    ("F.Cu", 0.8, [(38.0, 57.5), (38.0, 60.0)]),
    ("F.Cu", 0.8, [(31.0, 57.5), (51.0, 57.5), (51.0, 60.0)]),
    ("F.Cu", 0.45, [(31.0, 31.78), (23.7, 29.24)]),
    ("F.Cu", 0.45, [(31.0, 34.32), (23.7, 41.94)]),
    ("F.Cu", 0.6, [(56.4, 49.56), (63.5, 47.08)]),
    ("F.Cu", 0.45, [(56.4, 24.16), (61.5, 24.16), (61.5, 54.0), (72.62, 54.0), (72.62, 60.0)]),
    ("F.Cu", 0.45, [(56.4, 16.54), (62.5, 16.54), (62.5, 55.0), (70.08, 55.0), (70.08, 60.0)]),
    ("F.Cu", 0.45, [(56.4, 44.48), (69.0, 25.74), (76.0, 38.62)]),
]

for layer, w_mm, pts in tracks:
    color = "#ef4444" if layer == "F.Cu" else "#38bdf8"
    w_px = max(2, int(w_mm * SCALE * 0.75))
    xy_pts = [(px(x), py(y)) for x, y in pts]
    d.line(xy_pts, fill=color, width=w_px)

def draw_pad(x_mm, y_mm, shape="circle", lbl="", lbl_dir="L"):
    r = int(0.82 * SCALE)
    r_hole = int(0.40 * SCALE)
    cx, cy = px(x_mm), py(y_mm)
    if shape == "rect":
        d.rectangle([cx - r, cy - r, cx + r, cy + r], fill="#eab308", outline="#ca8a04", width=1)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#eab308", outline="#ca8a04", width=1)
    d.ellipse([cx - r_hole, cy - r_hole, cx + r_hole, cy + r_hole], fill="#0f172a")
    if lbl:
        if lbl_dir == "L":
            d.text((cx - r - 4, cy), lbl, fill="#e2e8f0", font=fnt(11), anchor="rm")
        elif lbl_dir == "R":
            d.text((cx + r + 4, cy), lbl, fill="#e2e8f0", font=fnt(11), anchor="lm")

def draw_box(x1, y1, x2, y2, title="", subtitle="", title_pos="center"):
    d.rectangle([px(x1), py(y1), px(x2), py(y2)], outline="#f8fafc", width=2)
    if title:
        if title_pos == "center":
            mx, my = px((x1 + x2) / 2), py((y1 + y2) / 2)
            d.text((mx, my - (8 if subtitle else 0)), title, fill="#ffffff", font=fnt(13, True), anchor="mm")
            if subtitle:
                d.text((mx, my + 10), subtitle, fill="#cbd5e1", font=fnt(11), anchor="mm")
        elif title_pos == "top":
            mx = px((x1 + x2) / 2)
            d.text((mx, py(y1) - 10), title, fill="#fde047", font=fnt(12, True), anchor="mb")

# U1: ESP32-DEVKIT-V1 (30 pinos)
draw_box(29.0, 9.0, 58.4, 52.5, "U1: ESP32-DEVKIT-V1", "30 Pinos (Chassi)")
d.rectangle([px(39.7), py(8.2), px(47.7), py(11.5)], fill="#94a3b8", outline="#f8fafc", width=1)
d.text((px(43.7), py(9.8)), "USB", fill="#0f172a", font=fnt(11, True), anchor="mm")

left_lbls = ["EN", "VP", "VN", "D34", "D35", "D32", "D33", "D25", "D26", "D27", "D14", "D12", "D13", "GND", "VIN"]
right_lbls = ["D23", "D22", "TX0", "RX0", "D21", "D19", "D18", "D5", "TX2", "RX2", "D4", "D2", "D15", "GND", "3V3"]
for i, l in enumerate(left_lbls):
    draw_pad(31.0, 14.0 + i * P, "rect" if i == 0 else "circle", l, "R")
for i, l in enumerate(right_lbls):
    draw_pad(56.4, 14.0 + i * P, "circle", l, "L")

# U2: TB6612FNG
draw_box(9.2, 24.7, 25.5, 46.5, "U2: TB6612", "Ponte H 4WD")
tb_l = ["VM", "VCC", "GND", "AO1", "AO2", "BO2", "BO1", "GND"]
tb_r = ["PWMA", "AIN2", "AIN1", "STBY", "BIN1", "BIN2", "PWMB", "GND"]
for i, l in enumerate(tb_l):
    draw_pad(11.0, 26.7 + i * P, "rect" if i == 0 else "circle", l, "R")
for i, l in enumerate(tb_r):
    draw_pad(23.7, 26.7 + i * P, "circle", l, "L")

# J1, SW1, U3 (Mini 560)
draw_box(2.5, 9.2, 6.5, 15.5, "J1 BAT", title_pos="top")
draw_pad(4.5, 11.0, "rect")
draw_pad(4.5, 11.0 + P, "circle")

draw_box(9.8, 9.2, 13.2, 15.5, "SW1", title_pos="top")
draw_pad(11.5, 11.0, "rect")
draw_pad(11.5, 11.0 + P, "circle")

draw_box(16.0, 8.0, 27.0, 24.5, "U3: MINI 560", "Step-Down 5V")
draw_pad(17.5, 9.5, "rect", "IN+", "R")
draw_pad(17.5, 23.0, "circle", "IN-", "R")
draw_pad(25.5, 9.5, "circle", "5V", "L")
draw_pad(25.5, 23.0, "circle", "GND", "L")

# J3 e J6 (Motores)
draw_box(2.2, 32.5, 5.8, 38.6, "J3 ESQ", title_pos="top")
draw_pad(4.0, 34.3, "rect")
draw_pad(4.0, 34.3 + P, "circle")

draw_box(2.2, 40.1, 5.8, 46.2)
d.text((px(4.0), py(47.8)), "J6 DIR", fill="#86efac", font=fnt(12, True), anchor="mm")
draw_pad(4.0, 41.9, "rect")
draw_pad(4.0, 41.9 + P, "circle")

# Divisor R3 e R4
draw_box(9.8, 48.8, 19.8, 51.2, "R3 10k")
draw_pad(11.0, 50.0, "rect")
draw_pad(18.62, 50.0, "circle")

draw_box(9.8, 52.8, 19.8, 55.2, "R4 4.7k")
draw_pad(11.0, 54.0, "rect")
draw_pad(18.62, 54.0, "circle")

# U4: MAX98357A + J_SPK + U5: INMP441
draw_box(67.2, 9.0, 77.5, 27.2, "U4: MAX98357A", title_pos="top")
for i, l in enumerate(["Vin", "GND", "SD", "GAIN", "DIN", "BCLK", "LRC"]):
    draw_pad(69.0, 10.5 + i * P, "rect" if i == 0 else "circle", l, "R")

draw_box(79.0, 14.2, 82.2, 20.4, "J_SPK", title_pos="top")
draw_pad(80.6, 16.0, "rect")
draw_pad(80.6, 16.0 + P, "circle")

draw_box(71.5, 29.5, 81.5, 45.2, "U5: INMP441", title_pos="top")
for i, l in enumerate(["VDD", "GND", "L/R", "WS", "SCK", "SD"]):
    draw_pad(76.0, 31.0 + i * P, "rect" if i == 0 else "circle", l, "L")

# U6: DS18B20 + R_PULL
draw_box(61.8, 40.5, 65.2, 48.6, "U6 TEMP", title_pos="top")
for i in range(3):
    draw_pad(63.5, 42.0 + i * P, "rect" if i == 0 else "circle")

draw_box(70.3, 47.8, 80.3, 50.2, "R_PULL 4.7k")
draw_pad(71.5, 49.0, "rect")
draw_pad(79.12, 49.0, "circle")

# Conectores Inferiores (J_CAM, J4, J5, J_LED, J_OLED)
bottom_conns = [
    ("J_CAM (5V/GND)", 14.0, 2),
    ("J4 SERVO PAN", 25.0, 3),
    ("J5 SERVO TILT", 38.0, 3),
    ("J_LED WS2812B", 51.0, 3),
    ("J_OLED I2C", 65.0, 4),
]
for title, bx, npins in bottom_conns:
    draw_box(bx - 1.5, 58.5, bx + (npins - 1) * P + 1.5, 61.5, "")
    d.text((px(bx + (npins - 1) * P / 2), py(63.2)), title, fill="#fde047", font=fnt(11, True), anchor="mm")
    for i in range(npins):
        draw_pad(bx + i * P, 60.0, "rect" if i == 0 else "circle")

# Legenda no rodapé
leg_y = IMG_H - 42
d.rectangle([MARGIN_X, leg_y - 18, IMG_W - MARGIN_X, leg_y + 20], fill="#1e293b", outline="#334155", width=1)
d.text((MARGIN_X + 20, leg_y + 1), "LEGENDA DE CAMADAS:", fill="#f8fafc", font=fnt(14, True), anchor="lm")
d.line([MARGIN_X + 210, leg_y + 1, MARGIN_X + 250, leg_y + 1], fill="#ef4444", width=5)
d.text((MARGIN_X + 260, leg_y + 1), "F.Cu (Trilhas Topo - 5V / 3V3 / I2C)", fill="#fca5a5", font=fnt(14), anchor="lm")
d.line([MARGIN_X + 560, leg_y + 1, MARGIN_X + 600, leg_y + 1], fill="#38bdf8", width=5)
d.text((MARGIN_X + 610, leg_y + 1), "B.Cu (Trilhas Fundo - Potência / Motores / PWM / I2S)", fill="#7dd3fc", font=fnt(14), anchor="lm")
d.ellipse([MARGIN_X + 1030, leg_y - 7, MARGIN_X + 1046, leg_y + 9], fill="#eab308")
d.text((MARGIN_X + 1055, leg_y + 1), "Pads THT 2.54mm (Quadrado = Pino 1)", fill="#fde047", font=fnt(14), anchor="lm")

pcb_img_path = OUT / "preview_pcb_top.png"
im.save(pcb_img_path)
print(f"Print da PCB salvo em: {pcb_img_path}")
