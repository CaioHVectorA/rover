#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o projeto KiCad da nova PCB do Chassi do Rover 4WD (v2_2esps):
- docs/hardware/kicad/rover_pcb_v2_chassi/rover_pcb_v2_chassi.kicad_pro
- docs/hardware/kicad/rover_pcb_v2_chassi/rover_pcb_v2_chassi.kicad_sch

Componentes da placa:
- U1: ESP32-DEVKIT-V1 (30 pinos)
- U2: TB6612FNG (Driver MOSFET duplo de tração 4WD)
- U3: Step-Down Mini 560 / MP1584 (+5.0V / 5A)
- U4: MAX98357A (Amplificador de Áudio I2S 3W)
- U5: INMP441 (Microfone Digital MEMS I2S)
- U6: DS18B20 (Sensor de temperatura do chassi) + R_TEMP 4.7k
- Divisor Bateria: R3 10k + R4 4.7k -> D34 (VBAT-SENSE)
- Conectores:
  - J1: Bateria 2S (BAT+, GND)
  - J_CAM: Cabeça Pan/Tilt (2 pinos: +5V, GND)
  - J4: Servo Pan (3 pinos: +5V, D18, GND)
  - J5: Servo Tilt (3 pinos: +5V, D19, GND)
  - J_LED: Barra WS2812B (3 pinos: +5V, D2, GND)
  - J_OLED: Display OLED 0.96" I2C (4 pinos: GND, 3V3, D22 SCL, D21 SDA)
  - J3: Motores Esquerdos (AO1, AO2)
  - J6: Motores Direitos (BO1, BO2)
  - J_SPK: Alto-Falante (SPK+, SPK-)
"""

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/hardware/kicad/rover_pcb_v2_chassi"
OUT.mkdir(parents=True, exist_ok=True)

uid = lambda: str(uuid.uuid4())
root_uuid = uid()

libs = []
parts = []
wires = []
labels = []
texts = []
junctions = []
audit = []

def q(s):
    return json.dumps(s, ensure_ascii=False)

def font(size=1.5):
    return f"(font (size {size} {size}))"

def note(s, x, y, size=1.5, bold=False):
    b = " (bold yes)" if bold else ""
    texts.append(f'(text {q(s)} (at {x} {y} 0) (effects {font(size)}{b} (justify left top)) (uuid "{uid()}"))')

def block(ref, title, x, y, w, h, pins):
    """
    Cria um bloco esquemático modular compatível com KiCad 7, 8, 9 e 10.
    pins: lista de tuplas (terminal_name, side ['L'/'R'], y_offset)
    """
    name = "Rover:" + ref
    pinlib = []
    pp = {}
    for terminal, side, off in pins:
        px = -5 if side == 'L' else w + 5
        py = -off
        ang = 0 if side == 'L' else 180
        pinlib.append(
            f'(pin passive line (at {px} {py} {ang}) (length 5) '
            f'(name {q(terminal)} (effects {font(1.15)})) '
            f'(number {q(terminal)} (effects {font(0.8)})))'
        )
        pp[terminal] = (x + px, y + off)

    libs.append(f'''(symbol {q(name)} (pin_numbers hide) (pin_names (offset 1)) (in_bom yes) (on_board yes)
(property "Reference" "{ref}" (at 0 3 0) (effects {font()}))
(property "Value" {q(title)} (at {w/2} {-h/2} 0) (effects {font()}))
(symbol "{ref}_0_1" (rectangle (start 0 0) (end {w} {-h}) (stroke (width .3) (type default)) (fill (type background))))
(symbol "{ref}_1_1" {' '.join(pinlib)}))''')

    parts.append(f'''(symbol (lib_id {q(name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")
(property "Reference" {q(ref)} (at {x+w/2} {y-3} 0) (effects {font()}))
(property "Value" {q(title)} (at {x+w/2} {y+h/2} 0) (effects {font(1.3)} (hide yes)))
(instances (project "rover_pcb_v2_chassi" (path "/{root_uuid}" (reference {q(ref)}) (unit 1)))))''')

    note(title, x + 3, y + 2, 1.3, bold=True)
    return pp

def wire(*points):
    for a, b in zip(points, points[1:]):
        if a == b:
            continue
        wires.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid()}"))')

def lab(net, pt):
    labels.append(f'(label {q(net)} (at {pt[0]} {pt[1]} 0) (effects {font(1.25)} (justify left bottom)) (uuid "{uid()}"))')

def stub(p, net, side='R', length=8):
    e = (p[0] + (-length if side == 'L' else length), p[1])
    wire(p, e)
    lab(net, e)
    return e

def tie(a, b, net, *middle):
    wire(a, *middle, b)
    audit.append([net, a, b])

def dot(p):
    junctions.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))')

# ==============================================================================
# TÍTULO E CABEÇALHO DO ESQUEMÁTICO
# ==============================================================================
note("ROVER 4WD — NOVA PCB DO CHASSI (v2_2esps)", 15, 8, 2.5, bold=True)
note("ARQUITETURA DE 2 ESPs • ESP32 DevKit V1 no Chassi + ESP32-S3-CAM na Cabeça (Wi-Fi Direto)\n"
     "Tração 4WD (TB6612FNG) • Servos SG90 • Áudio I2S (MAX98357A + INMP441) • OLED 0.96\" • Temp DS18B20 • 8 LEDs WS2812B", 15, 16, 1.25)

# ==============================================================================
# BLOCO 1: ENTRADA DE ALIMENTAÇÃO & STEP-DOWN (SUPERIOR ESQUERDO)
# ==============================================================================
BT = block('J1', 'CONECTOR BATERIA 2S\n(Entrada JST-RCY)', 20, 35, 36, 22, [('BAT+', 'R', 7), ('GND', 'R', 17)])
SW = block('SW1', 'CHAVE GERAL\nKCD1-101', 75, 35, 24, 18, [('IN', 'L', 7), ('OUT', 'R', 7)])
REG = block('U3', 'STEP-DOWN MINI 560\n(Saída 5.0V / até 5A)', 125, 35, 36, 32, [('IN+', 'L', 7), ('IN-', 'L', 22), ('OUT+ 5V', 'R', 7), ('OUT- GND', 'R', 22)])

tie(BT['BAT+'], SW['IN'], 'BAT_RAW')
tie(SW['OUT'], REG['IN+'], 'VCC_BAT')
stub(SW['OUT'], 'VCC_BAT', 'R', 6)
dot((SW['OUT'][0] + 6, SW['OUT'][1]))

tie(BT['GND'], REG['IN-'], 'GND', (65, 52), (65, 57))
dot((65, 57))
stub(REG['OUT+ 5V'], '+5V', 'R', 10)
stub(REG['OUT- GND'], 'GND', 'R', 10)

# ==============================================================================
# BLOCO 2: DIVISOR RESISTIVO DE BATERIA 2S (VBAT-SENSE)
# ==============================================================================
R3 = block('R3', '10k (1%)', 190, 35, 20, 14, [('1', 'L', 7), ('2', 'R', 7)])
R4 = block('R4', '4.7k (1%)', 225, 42, 20, 14, [('1', 'L', 7), ('2', 'R', 7)])

stub(R3['1'], 'VCC_BAT', 'L', 6)
wire(R3['2'], (218, R3['2'][1]))
dot((218, R3['2'][1]))
stub((218, R3['2'][1]), 'VBAT-SENSE', 'R', 18)
wire((218, R3['2'][1]), (218, R4['1'][1]), R4['1'])
stub(R4['2'], 'GND', 'R', 6)

note("Divisor 10k / 4.7k:\nEm 8.4V (máx 2S) -> entrega 2.68V no pino D34 (ADC1).\nLinear e seguro dentro da faixa 3.3V do ESP32.", 190, 60, 1.1)

# ==============================================================================
# BLOCO 3: SENSOR DE TEMPERATURA DS18B20 (CHASSI)
# ==============================================================================
TEMP = block('U6', 'SENSOR TEMP\nDS18B20 (TO-92)', 275, 35, 28, 28, [('VDD 3V3', 'L', 7), ('DQ', 'R', 7), ('GND', 'L', 20)])
R_P = block('R_PULL', '4.7k Pull-up', 320, 35, 20, 14, [('1', 'L', 7), ('2', 'R', 7)])

stub(TEMP['VDD 3V3'], '+3V3', 'L', 6)
stub(TEMP['GND'], 'GND', 'L', 6)
stub(R_P['2'], '+3V3', 'R', 6)

wire(TEMP['DQ'], R_P['1'])
dot((TEMP['DQ'][0] + 6, TEMP['DQ'][1]))
stub((TEMP['DQ'][0] + 6, TEMP['DQ'][1]), 'TEMP-DATA', 'R', 30)

# ==============================================================================
# BLOCO 4: ESP32-DEVKIT-V1 (30 PINOS) — MICROCONTROLADOR CENTRAL DO CHASSI
# ==============================================================================
# Posicionado centralmente na folha
# Lado L: Alimentação e Pinos 16 a 30 (Lado Esquerdo do DevKit)
# Lado R: Pinos 1 a 15 (Lado Direito do DevKit)
esp_pins_L = [
    ('VIN (5V)', 'L', 12),
    ('GND_L', 'L', 22),
    ('D13 (STBY)', 'L', 32),
    ('D14 (BIN2)', 'L', 42),
    ('D27 (BIN1)', 'L', 52),
    ('D26 (PWMB)', 'L', 62),
    ('D25 (AIN2)', 'L', 72),
    ('D33 (AIN1)', 'L', 82),
    ('D32 (PWMA)', 'L', 92),
    ('D35 (I2S-DIN)', 'L', 102),
    ('D34 (VBAT-ADC)', 'L', 112),
]

esp_pins_R = [
    ('3V3', 'R', 12),
    ('GND_R', 'R', 22),
    ('D15 (I2S-WS)', 'R', 32),
    ('D2 (WS2812B)', 'R', 42),
    ('D4 (TEMP)', 'R', 52),
    ('D5 (I2S-BCLK)', 'R', 62),
    ('D18 (PAN)', 'R', 72),
    ('D19 (TILT)', 'R', 82),
    ('D21 (SDA)', 'R', 92),
    ('D22 (SCL)', 'R', 102),
    ('D23 (I2S-DOUT)', 'R', 112),
]

ESP = block('U1', 'ESP32-DEVKIT-V1\n(30 PINOS - CHASSI)', 160, 95, 55, 125, esp_pins_L + esp_pins_R)

# Conexões do ESP32 Lado L
stub(ESP['VIN (5V)'], '+5V', 'L', 10)
stub(ESP['GND_L'], 'GND', 'L', 10)
stub(ESP['D13 (STBY)'], 'MOT-STBY', 'L', 10)
stub(ESP['D14 (BIN2)'], 'MOT-BIN2', 'L', 10)
stub(ESP['D27 (BIN1)'], 'MOT-BIN1', 'L', 10)
stub(ESP['D26 (PWMB)'], 'MOT-PWMB', 'L', 10)
stub(ESP['D25 (AIN2)'], 'MOT-AIN2', 'L', 10)
stub(ESP['D33 (AIN1)'], 'MOT-AIN1', 'L', 10)
stub(ESP['D32 (PWMA)'], 'MOT-PWMA', 'L', 10)
stub(ESP['D35 (I2S-DIN)'], 'I2S-DIN', 'L', 10)
stub(ESP['D34 (VBAT-ADC)'], 'VBAT-SENSE', 'L', 10)

# Conexões do ESP32 Lado R
stub(ESP['3V3'], '+3V3', 'R', 10)
stub(ESP['GND_R'], 'GND', 'R', 10)
stub(ESP['D15 (I2S-WS)'], 'I2S-WS', 'R', 10)
stub(ESP['D2 (WS2812B)'], 'LED-DIN', 'R', 10)
stub(ESP['D4 (TEMP)'], 'TEMP-DATA', 'R', 10)
stub(ESP['D5 (I2S-BCLK)'], 'I2S-BCLK', 'R', 10)
stub(ESP['D18 (PAN)'], 'SERVO-PAN', 'R', 10)
stub(ESP['D19 (TILT)'], 'SERVO-TILT', 'R', 10)
stub(ESP['D21 (SDA)'], 'OLED-SDA', 'R', 10)
stub(ESP['D22 (SCL)'], 'OLED-SCL', 'R', 10)
stub(ESP['D23 (I2S-DOUT)'], 'I2S-DOUT', 'R', 10)

note("PINOS LIVRES P/ EXPANSÃO:\n"
     "- D2 (Barra WS2812B)\n"
     "- RX2 (GPIO 16) / TX2 (GPIO 17)\n"
     "- VP (GPIO 36) / VN (GPIO 39)\n"
     "- D12 (NC - Proteção de Boot)", 163, 226, 1.05)

# ==============================================================================
# BLOCO 5: DRIVER DE MOTORES TB6612FNG (TRAÇÃO 4WD) — LADO ESQUERDO
# ==============================================================================
tb_pins = [
    ('STBY', 'R', 10),
    ('PWMA', 'R', 20),
    ('AIN1', 'R', 30),
    ('AIN2', 'R', 40),
    ('PWMB', 'R', 50),
    ('BIN1', 'R', 60),
    ('BIN2', 'R', 70),
    ('VM', 'L', 12),
    ('VCC', 'L', 24),
    ('GND', 'L', 36),
    ('AO1', 'L', 52),
    ('AO2', 'L', 62),
    ('BO1', 'L', 76),
    ('BO2', 'L', 86),
]

TB = block('U2', 'DRIVER TB6612FNG\n(Ponte H Dupla MOSFET)', 50, 110, 48, 98, tb_pins)

stub(TB['STBY'], 'MOT-STBY', 'R', 8)
stub(TB['PWMA'], 'MOT-PWMA', 'R', 8)
stub(TB['AIN1'], 'MOT-AIN1', 'R', 8)
stub(TB['AIN2'], 'MOT-AIN2', 'R', 8)
stub(TB['PWMB'], 'MOT-PWMB', 'R', 8)
stub(TB['BIN1'], 'MOT-BIN1', 'R', 8)
stub(TB['BIN2'], 'MOT-BIN2', 'R', 8)

stub(TB['VM'], 'VCC_BAT', 'L', 8)
stub(TB['VCC'], '+3V3', 'L', 8)
stub(TB['GND'], 'GND', 'L', 8)

stub(TB['AO1'], 'MOT_ESQ_AO1', 'L', 8)
stub(TB['AO2'], 'MOT_ESQ_AO2', 'L', 8)
stub(TB['BO1'], 'MOT_DIR_BO1', 'L', 8)
stub(TB['BO2'], 'MOT_DIR_BO2', 'L', 8)

# Conectores dos motores J3 e J6
J_M_ESQ = block('J3', 'MOTORES ESQUERDOS\n(2x JGA-050 Paralelo)', 15, 155, 24, 20, [('AO1', 'R', 6), ('AO2', 'R', 14)])
J_M_DIR = block('J6', 'MOTORES DIREITOS\n(2x JGA-050 Paralelo)', 15, 185, 24, 20, [('BO1', 'R', 6), ('BO2', 'R', 14)])

stub(J_M_ESQ['AO1'], 'MOT_ESQ_AO1', 'R', 4)
stub(J_M_ESQ['AO2'], 'MOT_ESQ_AO2', 'R', 4)
stub(J_M_DIR['BO1'], 'MOT_DIR_BO1', 'R', 4)
stub(J_M_DIR['BO2'], 'MOT_DIR_BO2', 'R', 4)

# ==============================================================================
# BLOCO 6: ÁUDIO DIGITAL I2S (MAX98357A + INMP441) — LADO DIREITO
# ==============================================================================
AMP = block('U4', 'AMP ÁUDIO I2S\nMAX98357A (3W)', 270, 95, 38, 52, [
    ('Vin (+5V)', 'L', 8),
    ('GND', 'L', 18),
    ('BCLK', 'L', 28),
    ('LRC (WS)', 'L', 38),
    ('DIN', 'L', 46),
    ('SPK+', 'R', 15),
    ('SPK-', 'R', 35),
])

stub(AMP['Vin (+5V)'], '+5V', 'L', 8)
stub(AMP['GND'], 'GND', 'L', 8)
stub(AMP['BCLK'], 'I2S-BCLK', 'L', 8)
stub(AMP['LRC (WS)'], 'I2S-WS', 'L', 8)
stub(AMP['DIN'], 'I2S-DOUT', 'L', 8)

J_SPK = block('J_SPK', 'ALTO-FALANTE\n(4Ω / 8Ω 3W)', 340, 102, 26, 32, [('+', 'L', 8), ('-', 'L', 24)])
tie(AMP['SPK+'], J_SPK['+'], 'SPK+')
tie(AMP['SPK-'], J_SPK['-'], 'SPK-')

MIC = block('U5', 'MIC DIGITAL I2S\nINMP441 (MEMS)', 270, 160, 38, 48, [
    ('VDD (3V3)', 'L', 8),
    ('GND', 'L', 16),
    ('SD', 'L', 24),
    ('WS', 'L', 32),
    ('SCK (BCLK)', 'L', 40),
    ('L/R (GND)', 'R', 20),
])

stub(MIC['VDD (3V3)'], '+3V3', 'L', 8)
stub(MIC['GND'], 'GND', 'L', 8)
stub(MIC['SD'], 'I2S-DIN', 'L', 8)
stub(MIC['WS'], 'I2S-WS', 'L', 8)
stub(MIC['SCK (BCLK)'], 'I2S-BCLK', 'L', 8)
stub(MIC['L/R (GND)'], 'GND', 'R', 8)

# ==============================================================================
# BLOCO 7: CONECTORES DE PERIFÉRICOS EXTERNOS (RODAPÉ DA PLACA)
# ==============================================================================
# 1. Conector Chicote Cabeça Pan/Tilt (2 pinos: +5V, GND)
J_CAM = block('J_CAM', 'CABEÇA PAN/TILT\n(ESP32-S3-CAM Wi-Fi)', 20, 235, 36, 24, [('5V', 'R', 8), ('GND', 'R', 18)])
stub(J_CAM['5V'], '+5V', 'R', 8)
stub(J_CAM['GND'], 'GND', 'R', 8)

# 2. Servos Pan e Tilt (SG90)
J_PAN = block('J4', 'SERVO PAN\nSG90 (3 Pinos)', 80, 235, 30, 28, [('5V', 'R', 7), ('SINAL', 'R', 14), ('GND', 'R', 21)])
stub(J_PAN['5V'], '+5V', 'R', 8)
stub(J_PAN['SINAL'], 'SERVO-PAN', 'R', 8)
stub(J_PAN['GND'], 'GND', 'R', 8)

J_TILT = block('J5', 'SERVO TILT\nSG90 (3 Pinos)', 135, 235, 30, 28, [('5V', 'R', 7), ('SINAL', 'R', 14), ('GND', 'R', 21)])
stub(J_TILT['5V'], '+5V', 'R', 8)
stub(J_TILT['SINAL'], 'SERVO-TILT', 'R', 8)
stub(J_TILT['GND'], 'GND', 'R', 8)

# 3. Barra 8 LEDs WS2812B
J_LED = block('J_LED', 'FAROL WS2812B\n(Barra 8 LEDs RGB)', 190, 235, 32, 28, [('5V', 'R', 7), ('DIN', 'R', 14), ('GND', 'R', 21)])
stub(J_LED['5V'], '+5V', 'R', 8)
stub(J_LED['DIN'], 'LED-DIN', 'R', 8)
stub(J_LED['GND'], 'GND', 'R', 8)

# 4. Display OLED 0.96" I2C
J_OLED = block('J_OLED', 'DISPLAY OLED 0.96"\nSSD1306 (I2C 4 Pinos)', 245, 235, 34, 32, [
    ('GND', 'R', 7),
    ('3V3', 'R', 14),
    ('SCL', 'R', 21),
    ('SDA', 'R', 28)
])
stub(J_OLED['GND'], 'GND', 'R', 8)
stub(J_OLED['3V3'], '+3V3', 'R', 8)
stub(J_OLED['SCL'], 'OLED-SCL', 'R', 8)
stub(J_OLED['SDA'], 'OLED-SDA', 'R', 8)

# ==============================================================================
# MONTAGEM FINAL DO ESQUEMÁTICO (.kicad_sch)
# ==============================================================================
sch_body = f'''(kicad_sch (version 20251024) (generator "eeschema") (generator_version "10.0") (uuid "{root_uuid}") (paper "A3")
(lib_symbols {' '.join(libs)})
{' '.join(parts + wires + labels + junctions + texts)}
(sheet_instances (path "/" (page "1"))) (embedded_fonts no))'''

sch_path = OUT / "rover_pcb_v2_chassi.kicad_sch"
sch_path.write_text(sch_body, encoding="utf-8")
print(f"Esquemático gerado com sucesso: {sch_path}")

# ==============================================================================
# PROJETO KICAD (.kicad_pro)
# ==============================================================================
pro_content = {
    "meta": {
        "filename": "rover_pcb_v2_chassi.kicad_pro",
        "version": 1
    },
    "project": {
        "files": ["rover_pcb_v2_chassi.kicad_sch"]
    },
    "schematic": {
        "annotate_start_num": 1,
        "drawing": {
            "dashed_lines_dash_length_ratio": 12.0,
            "dashed_lines_gap_length_ratio": 3.0,
            "default_line_thickness": 0.15,
            "default_text_size": 1.5,
            "field_names": [],
            "pin_symbol_size": 0.0,
            "text_offset_ratio": 0.08
        }
    },
    "boards": []
}

pro_path = OUT / "rover_pcb_v2_chassi.kicad_pro"
pro_path.write_text(json.dumps(pro_content, indent=2), encoding="utf-8")
print(f"Projeto KiCad gerado com sucesso: {pro_path}")

# Salva arquivo de auditoria das redes
audit_path = OUT / "auditoria_redes.json"
audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(f"Auditoria de redes salva: {audit_path}")
