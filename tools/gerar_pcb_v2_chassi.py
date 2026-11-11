#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reproduz em pasta temporária o layout físico histórico da PCB dedicada do Chassi no KiCad:
- docs/hardware/kicad/rover_pcb_v2_chassi/rover_pcb_v2_chassi.kicad_pcb

Características da PCB (v2_2esps):
- Dimensões compactas: 85.0 mm × 65.0 mm (redução de ~60% na área em relação à perfurada 90×150 mm)
- 4 Furos de fixação M3 nos cantos (H1 a H4) para parafusar no chassi 3D em ABS
- Todos os módulos encaixados em barras de pinos fêmea passo 2.54 mm (fácil troca se queimar)
- Todos os pads com as redes (nets) reais atribuídas, exibindo o Ratsnest e trilhas principais de potência e sinal no Pcbnew.
"""

import json
import tempfile
import uuid
from pathlib import Path

# Gerador histórico. A revisão de face simples é editada diretamente no KiCad.
OUT = Path(tempfile.gettempdir()) / "rover_kicad_v2_original"
OUT.mkdir(parents=True, exist_ok=True)

uid = lambda: str(uuid.uuid4())

# Origem da placa na folha A4 do Pcbnew
OX, OY = 60.0, 50.0
W, H = 85.0, 65.0
P = 2.54

# Lista oficial de Redes (Nets) sincronizada com o esquemático
NET_NAMES = [
    "",
    "GND",
    "+5V",
    "+3V3",
    "VCC_BAT",
    "BAT_RAW",
    "VBAT-SENSE",
    "TEMP-DATA",
    "MOT-STBY",
    "MOT-PWMA",
    "MOT-AIN1",
    "MOT-AIN2",
    "MOT-PWMB",
    "MOT-BIN1",
    "MOT-BIN2",
    "MOT_ESQ_AO1",
    "MOT_ESQ_AO2",
    "MOT_DIR_BO1",
    "MOT_DIR_BO2",
    "SERVO-PAN",
    "SERVO-TILT",
    "LED-DIN",
    "OLED-SDA",
    "OLED-SCL",
    "I2S-WS",
    "I2S-BCLK",
    "I2S-DOUT",
    "I2S-DIN",
    "SPK+",
    "SPK-"
]
NID = {name: idx for idx, name in enumerate(NET_NAMES)}

footprints = []
segments = []
graphics = []

def ax(x):
    return round(OX + x, 3)

def ay(y):
    return round(OY + y, 3)

def gr_rect(x1, y1, x2, y2, layer="Edge.Cuts", width=0.15):
    graphics.append(f"""\t(gr_rect
\t\t(start {ax(x1)} {ay(y1)})
\t\t(end {ax(x2)} {ay(y2)})
\t\t(stroke
\t\t\t(width {width})
\t\t\t(type default)
\t\t)
\t\t(fill no)
\t\t(layer "{layer}")
\t\t(uuid "{uid()}")
\t)""")

def gr_text(text, x, y, size=1.0, layer="F.SilkS", thickness=0.15):
    graphics.append(f"""\t(gr_text {json.dumps(text, ensure_ascii=False)}
\t\t(at {ax(x)} {ay(y)} 0)
\t\t(layer "{layer}")
\t\t(uuid "{uid()}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size} {size})
\t\t\t\t(thickness {thickness})
\t\t\t)
\t\t)
\t)""")

def add_mounting_hole(ref, x, y):
    footprints.append(f"""\t(footprint "MountingHole:MountingHole_3.2mm_M3"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at {ax(x)} {ay(y)} 0)
\t\t(descr "Mounting Hole 3.2mm, M3")
\t\t(property "Reference" "{ref}"
\t\t\t(at 0 -3.2 0)
\t\t\t(layer "F.SilkS")
\t\t\t(effects (font (size 0.8 0.8) (thickness 0.15)))
\t\t)
\t\t(property "Value" "M3"
\t\t\t(at 0 3.2 0)
\t\t\t(layer "F.Fab")
\t\t\t(effects (font (size 0.8 0.8) (thickness 0.15)))
\t\t)
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(fp_circle
\t\t\t(center 0 0)
\t\t\t(end 3.0 0)
\t\t\t(stroke (width 0.15) (type solid))
\t\t\t(fill no)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pad "1" np_thru_hole circle
\t\t\t(at 0 0)
\t\t\t(size 3.2 3.2)
\t\t\t(drill 3.2)
\t\t\t(layers "*.Cu" "*.Mask")
\t\t\t(uuid "{uid()}")
\t\t)
\t)""")

def add_module(ref, val, x, y, box_x1, box_y1, box_x2, box_y2, pads, ref_y=None, val_y=None):
    """
    Cria um footprint THT completo no padrão KiCad.
    pads: lista de tuplas (num_str, rel_x, rel_y, net_name, shape_opt, size_opt, drill_opt, label_opt)
    """
    ry = ref_y if ref_y is not None else (box_y1 - 1.5)
    vy = val_y if val_y is not None else (box_y2 + 1.5)

    fp_lines = []
    # Desenha contorno no F.SilkS e F.Fab
    for lyr, w in [("F.SilkS", 0.15), ("F.Fab", 0.10)]:
        fp_lines.append(f"""\t\t(fp_rect
\t\t\t(start {round(box_x1, 3)} {round(box_y1, 3)})
\t\t\t(end {round(box_x2, 3)} {round(box_y2, 3)})
\t\t\t(stroke (width {w}) (type solid))
\t\t\t(fill no)
\t\t\t(layer "{lyr}")
\t\t\t(uuid "{uid()}")
\t\t)""")

    pad_strs = []
    for item in pads:
        pnum, px, py, net = item[0], item[1], item[2], item[3]
        shape = item[4] if len(item) > 4 else ("rect" if pnum == "1" else "circle")
        sz = item[5] if len(item) > 5 else 1.75
        dr = item[6] if len(item) > 6 else 1.0
        lbl = item[7] if len(item) > 7 else ""

        net_id = NID.get(net, 0)
        net_clause = f'\n\t\t\t(net {net_id} {json.dumps(net)})' if net_id > 0 else ""

        pad_strs.append(f"""\t\t(pad {json.dumps(str(pnum))} thru_hole {shape}
\t\t\t(at {round(px, 3)} {round(py, 3)})
\t\t\t(size {sz} {sz})
\t\t\t(drill {dr})
\t\t\t(layers "*.Cu" "*.Mask"){net_clause}
\t\t\t(uuid "{uid()}")
\t\t)""")

        if lbl:
            # Adiciona silkscreen do nome do pino
            offset_x = -2.2 if px <= 0 else 2.2
            fp_lines.append(f"""\t\t(fp_text user {json.dumps(lbl, ensure_ascii=False)}
\t\t\t(at {round(px + offset_x, 3)} {round(py, 3)} 0)
\t\t\t(layer "F.SilkS")
\t\t\t(effects (font (size 0.65 0.65) (thickness 0.12)))
\t\t\t(uuid "{uid()}")
\t\t)""")

    footprints.append(f"""\t(footprint "Rover_Chassi:{ref}"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at {ax(x)} {ay(y)} 0)
\t\t(descr {json.dumps(val, ensure_ascii=False)})
\t\t(property "Reference" {json.dumps(ref)}
\t\t\t(at {round((box_x1 + box_x2)/2, 3)} {round(ry, 3)} 0)
\t\t\t(layer "F.SilkS")
\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15)))
\t\t)
\t\t(property "Value" {json.dumps(val, ensure_ascii=False)}
\t\t\t(at {round((box_x1 + box_x2)/2, 3)} {round(vy, 3)} 0)
\t\t\t(layer "F.Fab")
\t\t\t(effects (font (size 0.9 0.9) (thickness 0.15)))
\t\t)
\t\t(attr through_hole)
{chr(10).join(fp_lines)}
{chr(10).join(pad_strs)}
\t)""")

def track(net, pts, width=0.5, layer="B.Cu"):
    net_id = NID[net]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        segments.append(f"""\t(segment
\t\t(start {ax(x1)} {ay(y1)})
\t\t(end {ax(x2)} {ay(y2)})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net {net_id})
\t\t(uuid "{uid()}")
\t)""")

# ==============================================================================
# 1. CONTORNO DA PLACA (85.0 mm × 65.0 mm) E FUROS M3
# ==============================================================================
gr_rect(0, 0, W, H, "Edge.Cuts", 0.15)
gr_text("ROVER 4WD - PCB CHASSI v2_2esps (85x65mm)", 42.5, 2.2, 1.1, "F.SilkS", 0.18)

add_mounting_hole("H1", 4.0, 4.0)
add_mounting_hole("H2", W - 4.0, 4.0)
add_mounting_hole("H3", 4.0, H - 4.0)
add_mounting_hole("H4", W - 4.0, H - 4.0)

# ==============================================================================
# 2. U1: ESP32-DEVKIT-V1 (30 PINOS) — CENTRO DA PLACA
# Fileira Esquerda em X = 31.0 | Fileira Direita em X = 56.4 (Espaçamento 25.4mm)
# ==============================================================================
esp_x = 31.0
esp_y = 14.0

left_pins = [
    ("1", "EN", ""),
    ("2", "VP", ""),
    ("3", "VN", ""),
    ("4", "D34", "VBAT-SENSE"),
    ("5", "D35", "I2S-DIN"),
    ("6", "D32", "MOT-PWMA"),
    ("7", "D33", "MOT-AIN1"),
    ("8", "D25", "MOT-AIN2"),
    ("9", "D26", "MOT-PWMB"),
    ("10", "D27", "MOT-BIN1"),
    ("11", "D14", "MOT-BIN2"),
    ("12", "D12", ""),
    ("13", "D13", "MOT-STBY"),
    ("14", "GND1", "GND"),
    ("15", "VIN", "+5V"),
]

right_pins = [
    ("16", "D23", "I2S-DOUT"),
    ("17", "D22", "OLED-SCL"),
    ("18", "TX0", ""),
    ("19", "RX0", ""),
    ("20", "D21", "OLED-SDA"),
    ("21", "D19", "SERVO-TILT"),
    ("22", "D18", "SERVO-PAN"),
    ("23", "D5", "I2S-BCLK"),
    ("24", "TX2", ""),
    ("25", "RX2", ""),
    ("26", "D4", "TEMP-DATA"),
    ("27", "D2", "LED-DIN"),
    ("28", "D15", "I2S-WS"),
    ("29", "GND2", "GND"),
    ("30", "3V3", "+3V3"),
]

esp_pads = []
for i, (num, lbl, net) in enumerate(left_pins):
    esp_pads.append((num, 0.0, i * P, net, "rect" if i == 0 else "circle", 1.75, 1.0, lbl))
for i, (num, lbl, net) in enumerate(right_pins):
    esp_pads.append((num, 25.4, i * P, net, "circle", 1.75, 1.0, lbl))

add_module(
    "U1", "ESP32-DEVKIT-V1 (30p)",
    esp_x, esp_y,
    -2.0, -5.0, 27.4, 14 * P + 3.0,
    esp_pads,
    ref_y=16.0, val_y=20.0
)
gr_text("USB", esp_x + 12.7, esp_y - 3.5, 0.85, "F.SilkS")

# ==============================================================================
# 3. U2: DRIVER TB6612FNG (16 PINOS) — ESQUERDA (PRÓXIMO AOS PINOS D32..D13)
# Fileira Esquerda (Potência/Motores) em X = 11.0 | Fileira Direita (Controle) em X = 23.7
# ==============================================================================
tb_x = 11.0
tb_y = 26.7

tb_left = [
    ("1", "VM", "VCC_BAT"),
    ("2", "VCC", "+3V3"),
    ("3", "GND", "GND"),
    ("4", "AO1", "MOT_ESQ_AO1"),
    ("5", "AO2", "MOT_ESQ_AO2"),
    ("6", "BO2", "MOT_DIR_BO2"),
    ("7", "BO1", "MOT_DIR_BO1"),
    ("8", "GND2", "GND"),
]

tb_right = [
    ("9", "PWMA", "MOT-PWMA"),
    ("10", "AIN2", "MOT-AIN2"),
    ("11", "AIN1", "MOT-AIN1"),
    ("12", "STBY", "MOT-STBY"),
    ("13", "BIN1", "MOT-BIN1"),
    ("14", "BIN2", "MOT-BIN2"),
    ("15", "PWMB", "MOT-PWMB"),
    ("16", "GND3", "GND"),
]

tb_pads = []
for i, (num, lbl, net) in enumerate(tb_left):
    tb_pads.append((num, 0.0, i * P, net, "rect" if i == 0 else "circle", 1.75, 1.0, lbl))
for i, (num, lbl, net) in enumerate(tb_right):
    tb_pads.append((num, 12.7, i * P, net, "circle", 1.75, 1.0, lbl))

add_module(
    "U2", "TB6612FNG",
    tb_x, tb_y,
    -1.8, -2.0, 14.5, 7 * P + 2.0,
    tb_pads,
    ref_y=7.0, val_y=10.5
)

# ==============================================================================
# 4. CONECTORES DE POTÊNCIA & MOTORES (LADO ESQUERDO)
# ==============================================================================
# J1: Entrada Bateria 2S
add_module(
    "J1", "BAT_2S",
    4.5, 11.0,
    -1.5, -1.8, 1.5, P + 1.8,
    [
        ("1", 0.0, 0.0, "BAT_RAW", "rect", 2.0, 1.1, "BAT+"),
        ("2", 0.0, P, "GND", "circle", 2.0, 1.1, "GND"),
    ]
)

# SW1: Chave Geral Liga/Desliga
add_module(
    "SW1", "CHAVE_GERAL",
    11.5, 11.0,
    -1.5, -1.8, 1.5, P + 1.8,
    [
        ("1", 0.0, 0.0, "BAT_RAW", "rect", 2.0, 1.1, "IN"),
        ("2", 0.0, P, "VCC_BAT", "circle", 2.0, 1.1, "OUT"),
    ]
)

# U3: Regulador Step-Down Mini 560 (+5V / 5A)
add_module(
    "U3", "MINI_560_5V",
    17.5, 9.5,
    -1.5, -1.5, 9.5, 16.5,
    [
        ("1", 0.0, 0.0, "VCC_BAT", "rect", 2.0, 1.1, "IN+"),
        ("2", 0.0, 14.0, "GND", "circle", 2.0, 1.1, "IN-"),
        ("3", 8.0, 0.0, "+5V", "circle", 2.0, 1.1, "5V"),
        ("4", 8.0, 14.0, "GND", "circle", 2.0, 1.1, "GND"),
    ],
    ref_y=5.5, val_y=8.5
)

# J3: Motores Esquerdos
add_module(
    "J3", "MOT_ESQ",
    4.0, 34.3,
    -1.5, -1.8, 1.5, P + 1.8,
    [
        ("1", 0.0, 0.0, "MOT_ESQ_AO1", "rect", 1.9, 1.0, "AO1"),
        ("2", 0.0, P, "MOT_ESQ_AO2", "circle", 1.9, 1.0, "AO2"),
    ]
)

# J6: Motores Direitos
add_module(
    "J6", "MOT_DIR",
    4.0, 41.9,
    -1.5, -1.8, 1.5, P + 1.8,
    [
        ("1", 0.0, 0.0, "MOT_DIR_BO2", "rect", 1.9, 1.0, "BO2"),
        ("2", 0.0, P, "MOT_DIR_BO1", "circle", 1.9, 1.0, "BO1"),
    ]
)

# ==============================================================================
# 5. RESISTORES DO DIVISOR DE BATERIA (R3 10k / R4 4.7k) E SENSOR DS18B20 (U6)
# ==============================================================================
add_module(
    "R3", "10k",
    11.0, 50.0,
    -1.2, -1.2, 8.8, 1.2,
    [
        ("1", 0.0, 0.0, "VCC_BAT", "rect", 1.6, 0.9, ""),
        ("2", 7.62, 0.0, "VBAT-SENSE", "circle", 1.6, 0.9, ""),
    ]
)

add_module(
    "R4", "4.7k",
    11.0, 54.0,
    -1.2, -1.2, 8.8, 1.2,
    [
        ("1", 0.0, 0.0, "GND", "rect", 1.6, 0.9, ""),
        ("2", 7.62, 0.0, "VBAT-SENSE", "circle", 1.6, 0.9, ""),
    ]
)

# U6: Sensor Temperatura DS18B20 (TO-92) + R_PULL 4.7k
add_module(
    "U6", "DS18B20",
    64.5, 42.0,
    -1.5, -1.5, 1.5, 2 * P + 1.5,
    [
        ("1", 0.0, 0.0, "GND", "rect", 1.6, 0.9, "GND"),
        ("2", 0.0, P, "TEMP-DATA", "circle", 1.6, 0.9, "DQ"),
        ("3", 0.0, 2 * P, "+3V3", "circle", 1.6, 0.9, "3V3"),
    ]
)

add_module(
    "R_PULL", "4.7k",
    72.0, 44.5,
    -1.2, -1.2, 8.8, 1.2,
    [
        ("1", 0.0, 0.0, "TEMP-DATA", "rect", 1.6, 0.9, ""),
        ("2", 7.62, 0.0, "+3V3", "circle", 1.6, 0.9, ""),
    ]
)

# ==============================================================================
# 6. MÓDULOS DE ÁUDIO DIGITAL I2S (LADO DIREITO)
# ==============================================================================
# U4: Amplificador MAX98357A (3W)
u4_pins = [
    ("1", "Vin", "+5V"),
    ("2", "GND", "GND"),
    ("3", "SD", ""),
    ("4", "GAIN", ""),
    ("5", "DIN", "I2S-DOUT"),
    ("6", "BCLK", "I2S-BCLK"),
    ("7", "LRC", "I2S-WS"),
]
add_module(
    "U4", "MAX98357A",
    69.0, 12.0,
    -1.8, -1.8, 10.5, 6 * P + 1.8,
    [(n, 0.0, i * P, net, "rect" if i == 0 else "circle", 1.7, 1.0, lbl) for i, (n, lbl, net) in enumerate(u4_pins)],
    ref_y=5.5, val_y=8.5
)

# J_SPK: Saída Alto-Falante (Bornes do MAX98357A)
add_module(
    "J_SPK", "SPEAKER",
    80.5, 17.0,
    -1.5, -1.8, 1.5, P + 1.8,
    [
        ("1", 0.0, 0.0, "SPK+", "rect", 1.9, 1.0, "SPK+"),
        ("2", 0.0, P, "SPK-", "circle", 1.9, 1.0, "SPK-"),
    ]
)

# U5: Microfone Digital MEMS INMP441
u5_pins = [
    ("1", "VDD", "+3V3"),
    ("2", "GND", "GND"),
    ("3", "L/R", "GND"),
    ("4", "WS", "I2S-WS"),
    ("5", "SCK", "I2S-BCLK"),
    ("6", "SD", "I2S-DIN"),
]
add_module(
    "U5", "INMP441",
    76.0, 29.5,
    -1.8, -1.8, 5.5, 5 * P + 1.8,
    [(n, 0.0, i * P, net, "rect" if i == 0 else "circle", 1.7, 1.0, lbl) for i, (n, lbl, net) in enumerate(u5_pins)]
)

# ==============================================================================
# 7. CONECTORES FRONTAIS / PERIFÉRICOS (BORDA INFERIOR DA PLACA)
# ==============================================================================
# J_CAM: Alimentação 2 fios para o ESP32-S3-CAM na cabeça Pan/Tilt
add_module(
    "J_CAM", "CAM_5V (2p)",
    14.0, 60.0,
    -1.5, -1.5, P + 1.5, 1.5,
    [
        ("1", 0.0, 0.0, "+5V", "rect", 1.8, 1.0, ""),
        ("2", P, 0.0, "GND", "circle", 1.8, 1.0, ""),
    ]
)

# J4: Servo Pan (SG90)
add_module(
    "J4", "SERVO_PAN",
    25.0, 60.0,
    -1.5, -1.5, 2 * P + 1.5, 1.5,
    [
        ("1", 0.0, 0.0, "+5V", "rect", 1.8, 1.0, ""),
        ("2", P, 0.0, "SERVO-PAN", "circle", 1.8, 1.0, ""),
        ("3", 2 * P, 0.0, "GND", "circle", 1.8, 1.0, ""),
    ]
)

# J5: Servo Tilt (SG90)
add_module(
    "J5", "SERVO_TILT",
    38.0, 60.0,
    -1.5, -1.5, 2 * P + 1.5, 1.5,
    [
        ("1", 0.0, 0.0, "+5V", "rect", 1.8, 1.0, ""),
        ("2", P, 0.0, "SERVO-TILT", "circle", 1.8, 1.0, ""),
        ("3", 2 * P, 0.0, "GND", "circle", 1.8, 1.0, ""),
    ]
)

# J_LED: Barra 8 LEDs RGB WS2812B
add_module(
    "J_LED", "WS2812B",
    51.0, 60.0,
    -1.5, -1.5, 2 * P + 1.5, 1.5,
    [
        ("1", 0.0, 0.0, "+5V", "rect", 1.8, 1.0, ""),
        ("2", P, 0.0, "LED-DIN", "circle", 1.8, 1.0, ""),
        ("3", 2 * P, 0.0, "GND", "circle", 1.8, 1.0, ""),
    ]
)

# J_OLED: Display OLED 0.96" I2C (4 Pinos)
add_module(
    "J_OLED", "OLED_I2C",
    65.0, 60.0,
    -1.5, -1.5, 3 * P + 1.5, 1.5,
    [
        ("1", 0.0, 0.0, "GND", "rect", 1.8, 1.0, ""),
        ("2", P, 0.0, "+3V3", "circle", 1.8, 1.0, ""),
        ("3", 2 * P, 0.0, "OLED-SCL", "circle", 1.8, 1.0, ""),
        ("4", 3 * P, 0.0, "OLED-SDA", "circle", 1.8, 1.0, ""),
    ]
)

# ==============================================================================
# 8. TRILHAS PRINCIPAIS ROTEADAS (COBRE INFERIOR B.Cu E SUPERIOR F.Cu)
# ==============================================================================
# Alimentação Bateria -> Chave -> Mini 560 -> TB6612 VM (Trilhas largas de 1.0 mm)
track("BAT_RAW", [(4.5, 11.0), (11.5, 11.0)], width=1.0, layer="B.Cu")
track("VCC_BAT", [(11.5, 13.54), (17.5, 9.5)], width=1.0, layer="B.Cu")
track("VCC_BAT", [(11.5, 13.54), (11.0, 26.7)], width=1.0, layer="B.Cu")
track("VCC_BAT", [(11.0, 26.7), (11.0, 50.0)], width=0.5, layer="B.Cu")

# Saída +5V do Mini 560 -> ESP32 VIN (Pino 15) -> Conectores inferiores
track("+5V", [(25.5, 9.5), (28.0, 9.5), (28.0, 49.56), (31.0, 49.56)], width=1.0, layer="F.Cu")
track("+5V", [(31.0, 49.56), (31.0, 57.5), (14.0, 57.5), (14.0, 60.0)], width=0.8, layer="F.Cu")
track("+5V", [(25.0, 57.5), (25.0, 60.0)], width=0.8, layer="F.Cu")
track("+5V", [(38.0, 57.5), (38.0, 60.0)], width=0.8, layer="F.Cu")
track("+5V", [(31.0, 57.5), (51.0, 57.5), (51.0, 60.0)], width=0.8, layer="F.Cu")

# Saídas de Motores do TB6612 -> Conectores J3 e J6 (Trilhas de 0.8 mm)
track("MOT_ESQ_AO1", [(11.0, 34.32), (4.0, 34.3)], width=0.8, layer="B.Cu")
track("MOT_ESQ_AO2", [(11.0, 36.86), (4.0, 36.84)], width=0.8, layer="B.Cu")
track("MOT_DIR_BO2", [(11.0, 39.40), (4.0, 41.9)], width=0.8, layer="B.Cu")
track("MOT_DIR_BO1", [(11.0, 41.94), (4.0, 44.44)], width=0.8, layer="B.Cu")

# Sinais PWM/Controle do ESP32 -> TB6612 (Diretos lado a lado!)
track("MOT-PWMA", [(31.0, 26.70), (23.7, 26.70)], width=0.4, layer="B.Cu")
track("MOT-AIN1", [(31.0, 29.24), (23.7, 31.78)], width=0.4, layer="B.Cu")
track("MOT-AIN2", [(31.0, 31.78), (23.7, 29.24)], width=0.4, layer="F.Cu")
track("MOT-PWMB", [(31.0, 34.32), (23.7, 41.94)], width=0.4, layer="F.Cu")
track("MOT-BIN1", [(31.0, 36.86), (23.7, 36.86)], width=0.4, layer="B.Cu")
track("MOT-BIN2", [(31.0, 39.40), (23.7, 39.40)], width=0.4, layer="B.Cu")
track("MOT-STBY", [(31.0, 44.48), (26.5, 44.48), (26.5, 34.32), (23.7, 34.32)], width=0.4, layer="B.Cu")

# Divisor de Bateria (R3/R4 -> D34)
track("VBAT-SENSE", [(18.62, 50.0), (18.62, 54.0)], width=0.4, layer="B.Cu")
track("VBAT-SENSE", [(18.62, 50.0), (29.0, 50.0), (29.0, 21.62), (31.0, 21.62)], width=0.4, layer="B.Cu")

# Sensor DS18B20 + Pull-up -> D4
track("TEMP-DATA", [(56.4, 39.40), (64.5, 44.54), (72.0, 44.5)], width=0.4, layer="B.Cu")
track("+3V3", [(64.5, 47.08), (79.62, 44.5)], width=0.5, layer="B.Cu")
track("+3V3", [(56.4, 49.56), (64.5, 47.08)], width=0.6, layer="F.Cu")

# Servos, WS2812B e OLED I2C
track("SERVO-PAN", [(56.4, 29.24), (59.5, 29.24), (59.5, 55.0), (27.54, 55.0), (27.54, 60.0)], width=0.4, layer="B.Cu")
track("SERVO-TILT", [(56.4, 26.70), (60.5, 26.70), (60.5, 56.0), (40.54, 56.0), (40.54, 60.0)], width=0.4, layer="B.Cu")
track("LED-DIN", [(56.4, 41.94), (53.54, 54.0), (53.54, 60.0)], width=0.4, layer="B.Cu")
track("OLED-SDA", [(56.4, 24.16), (62.0, 24.16), (62.0, 54.0), (72.62, 54.0), (72.62, 60.0)], width=0.4, layer="F.Cu")
track("OLED-SCL", [(56.4, 16.54), (63.0, 16.54), (63.0, 55.0), (70.08, 55.0), (70.08, 60.0)], width=0.4, layer="F.Cu")

# Áudio I2S (ESP32 -> MAX98357A e INMP441)
track("I2S-DOUT", [(56.4, 14.0), (65.0, 14.0), (65.0, 22.16), (69.0, 22.16)], width=0.4, layer="B.Cu")
track("I2S-BCLK", [(56.4, 31.78), (69.0, 24.70), (76.0, 39.66)], width=0.4, layer="B.Cu")
track("I2S-WS", [(56.4, 44.48), (69.0, 27.24), (76.0, 37.12)], width=0.4, layer="F.Cu")
track("I2S-DIN", [(31.0, 24.16), (31.0, 8.0), (74.0, 8.0), (74.0, 42.20), (76.0, 42.20)], width=0.4, layer="B.Cu")

# ==============================================================================
# MONTAGEM DO ARQUIVO .kicad_pcb
# ==============================================================================
nets_header = "\n".join([f'\t(net {i} {json.dumps(n)})' for i, n in enumerate(NET_NAMES)])

pcb_content = f"""(kicad_pcb
\t(version 20240108)
\t(generator "pcbnew")
\t(generator_version "8.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(31 "B.Cu" signal)
\t\t(32 "B.Adhes" user "B.Adhesive")
\t\t(33 "F.Adhes" user "F.Adhesive")
\t\t(34 "B.Paste" user)
\t\t(35 "F.Paste" user)
\t\t(36 "B.SilkS" user "B.Silkscreen")
\t\t(37 "F.SilkS" user "F.Silkscreen")
\t\t(38 "B.Mask" user)
\t\t(39 "F.Mask" user)
\t\t(40 "Dwgs.User" user "User.Drawings")
\t\t(41 "Cmts.User" user "User.Comments")
\t\t(42 "Eco1.User" user "User.Eco1")
\t\t(43 "Eco2.User" user "User.Eco2")
\t\t(44 "Edge.Cuts" user)
\t\t(45 "Margin" user)
\t\t(46 "B.CrtYd" user "B.Courtyard")
\t\t(47 "F.CrtYd" user "F.Courtyard")
\t\t(48 "B.Fab" user)
\t\t(49 "F.Fab" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(pcbplotparams
\t\t\t(layerselection 0x00010fc_ffffffff)
\t\t\t(outputdirectory "")
\t\t)
\t)
{nets_header}
{chr(10).join(footprints)}
{chr(10).join(graphics)}
{chr(10).join(segments)}
)
"""

pcb_path = OUT / "rover_pcb_v2_chassi.kicad_pcb"
pcb_path.write_text(pcb_content, encoding="utf-8")
print(f"Layout da PCB gerado com sucesso: {pcb_path}")
