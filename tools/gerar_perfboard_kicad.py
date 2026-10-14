#!/usr/bin/env python3
"""
Gera hardware/kicad/rover_serial_bridge/rover_perfboard_visual.kicad_pcb

Visualizacao LIMPA e REALISTA de montagem em PLACA PERFURADA:
  - Mantem APENAS os furos e ilhas reais dos componentes (Arduino Nano, conector J1, R1, R2, Q1).
  - Desenha uma grade suave no silkscreen (F.SilkS) representando a matriz de perfuracao (2.54 mm).
  - Elimina a matriz de pads de cobre sobrepostos que poluiam a tela e pareciam estar 'em cima' dos componentes.
  - Modelo 3D realista do Arduino Nano elevado em soquetes/headers fêmea.
"""
import glob
import math
import re
import uuid

FP = glob.glob('/home/usuario/.local/share/flatpak/runtime/org.kicad.KiCad.Library.Footprints/'
               'x86_64/stable/*/files/footprints')[0]
OUT = '/home/usuario/Documentos/rover/hardware/kicad/rover_serial_bridge/rover_perfboard_visual.kicad_pcb'
MODELS = '/home/usuario/Documentos/rover/hardware/kicad/rover_serial_bridge/models'
OX, OY = 60.96, 60.96
W, H = 40.64, 45.72      # 16 x 18 espacos de 2.54 mm
P = 2.54


def u():
    return str(uuid.uuid4())


NETS = ['', '+5V', 'GND', 'ESP_TX_3V3', 'BASE_Q1', 'NANO_D2']
NID = {n: i for i, n in enumerate(NETS)}


def wrl_box(x, y, z, sx, sy, sz, rgb):
    return (f'Transform {{ translation {x} {y} {z} children [ Shape {{ appearance Appearance {{ material Material '
            f'{{ diffuseColor {rgb[0]} {rgb[1]} {rgb[2]} specularColor 0.4 0.4 0.4 }} }} geometry Box {{ size {sx} {sy} {sz} }} }} ] }}\n')


def write_models():
    import os
    os.makedirs(MODELS, exist_ok=True)
    # Arduino Nano elevado (como se estivesse espetado em headers femea / soquetes na perfurada)
    n = '#VRML V2.0 utf8\n'
    cx, cy = 7.62, -15.24
    header_h = 8.5
    pcb_z = header_h + 0.8
    # Placa azul do Nano
    n += wrl_box(cx, -15.24, pcb_z, 17.78, 43.18, 1.6, (0.0, 0.32, 0.62))
    # Conector USB Mini/Micro
    n += wrl_box(cx, 0.0, pcb_z + 2.5, 7.6, 5.6, 3.5, (0.85, 0.85, 0.88))
    # ATmega328P
    n += wrl_box(cx, -15.24, pcb_z + 1.2, 8.5, 8.5, 1.0, (0.05, 0.05, 0.05))
    # Botao de Reset
    n += wrl_box(cx, -7.0, pcb_z + 1.4, 3.5, 3.5, 1.5, (0.75, 0.75, 0.75))
    # Pinos / Headers plasticos pretos de suporte
    for i in range(15):
        y_pos = -2.54 * i
        for px in (0.0, 15.24):
            # Corpo do header plastico na perfurada
            n += wrl_box(px, y_pos, header_h / 2, 2.5, 2.5, header_h, (0.1, 0.1, 0.1))
            # Pino metalico saindo para a placa
            n += wrl_box(px, y_pos, -1.0, 0.64, 0.64, 3.0, (0.85, 0.7, 0.2))
    open(f'{MODELS}/Arduino_Nano_simple.wrl', 'w').write(n)

    # 3 fios flexiveis do ESP32 chegando no conector J1
    w = '#VRML V2.0 utf8\n'
    # Fio 1: 5V (Vermelho), Fio 2: GND (Preto), Fio 3: TX (Amarelo)
    for k, (rgb, z_top) in enumerate([((0.9, 0.1, 0.1), 12.0), ((0.1, 0.1, 0.1), 14.0), ((0.95, 0.8, 0.1), 16.0)]):
        y_pos = -2.54 * k
        w += wrl_box(0, y_pos, z_top / 2, 1.0, 1.0, z_top, rgb)
        w += wrl_box(-18.0, y_pos, z_top, 36.0, 1.0, 1.0, rgb)
    open(f'{MODELS}/ESP_wires.wrl', 'w').write(w)


write_models()


def block_end(t, i):
    d = 0
    for j in range(i, len(t)):
        if t[j] == '(':
            d += 1
        elif t[j] == ')':
            d -= 1
            if d == 0:
                return j


def model_block(path):
    return (f'\t(model "${{KIPRJMOD}}/models/{path}"\n\t\t(offset\n\t\t\t(xyz 0 0 0)\n\t\t)\n\t\t(scale\n'
            f'\t\t\t(xyz 0.3937 0.3937 0.3937)\n\t\t)\n\t\t(rotate\n\t\t\t(xyz 0 0 0)\n\t\t)\n\t)\n')


def footprint(lib, name, ref, value, x, y, rot, padnets, model=None, extra_model=None):
    t = open(f'{FP}/{lib}.pretty/{name}.kicad_mod').read()
    t = re.sub(r'\n\t\(version [^)]*\)\n\t\(generator [^)]*\)\n\t\(generator_version [^)]*\)', '', t, 1)
    t = t.replace(f'(footprint "{name}"', f'(footprint "{lib}:{name}"', 1)
    t = t.replace('(layer "F.Cu")', f'(layer "F.Cu")\n\t(uuid "{u()}")\n\t(at {OX + x:.3f} {OY + y:.3f} {rot})', 1)
    t = t.replace('(property "Reference" "REF**"', f'(property "Reference" "{ref}"', 1)
    t = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{value}"', t, 1)
    spans = []
    for m in re.finditer(r'\(pad "([^"]+)"', t):
        spans.append((m.group(1), m.start(), block_end(t, m.start())))
    for num, s, e in reversed(spans):
        net = padnets.get(num)
        if net:
            t = t[:e] + f'\n\t\t(net {NID[net]} "{net}")\n\t' + t[e:]
    if model:
        t = re.sub(r'\(model "[^"]*"', f'(model "${{KIPRJMOD}}/models/{model}"', t, 1)
        t = re.sub(r'(\(model "[^"]*"\s*\(offset.*?\(scale\s*\(xyz )[\d. ]+\)', r'\g<1>0.3937 0.3937 0.3937)', t, 1, re.S)
    if extra_model:
        t = t.rstrip()[:-1] + model_block(extra_model) + ')'
    return '\t' + t.strip().replace('\n', '\n\t') + '\n'


def pt(x, y):
    return f'{OX + x:.3f} {OY + y:.3f}'


segs = []


def track(net, *pts, layer='B.Cu'):
    for a, b in zip(pts, pts[1:]):
        segs.append(f'\t(segment\n\t\t(start {pt(*a)})\n\t\t(end {pt(*b)})\n\t\t(width 0.8)\n'
                    f'\t\t(layer "{layer}")\n\t\t(net {NID[net]})\n\t\t(uuid "{u()}")\n\t)\n')


def wire_silk(*pts):
    out = ''
    for a, b in zip(pts, pts[1:]):
        out += (f'\t(gr_line\n\t\t(start {pt(*a)})\n\t\t(end {pt(*b)})\n\t\t(stroke\n\t\t\t(width 0.7)\n'
                f'\t\t\t(type default)\n\t\t)\n\t\t(layer "B.SilkS")\n\t\t(uuid "{u()}")\n\t)\n')
    return out


def gr_text(s, x, y, size=1.0, layer='F.SilkS'):
    return (f'\t(gr_text "{s}"\n\t\t(at {pt(x, y)} 0)\n\t\t(layer "{layer}")\n\t\t(uuid "{u()}")\n'
            f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size {size} {size})\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n')


def gr_rect(x1, y1, x2, y2):
    return (f'\t(gr_rect\n\t\t(start {pt(x1, y1)})\n\t\t(end {pt(x2, y2)})\n'
            f'\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type default)\n\t\t)\n\t\t(fill no)\n'
            f'\t\t(layer "Edge.Cuts")\n\t\t(uuid "{u()}")\n\t)\n')


# Posicionamento dos Componentes (grade de 2.54 mm)
NX, NY = 20.32, 5.08
parts = ''
# Arduino Nano V3
parts += footprint('Module', 'Arduino_Nano', 'A1', 'Arduino Nano V3', NX, NY, 0,
                   {'4': 'GND', '29': 'GND', '5': 'NANO_D2', '27': '+5V'}, model='Arduino_Nano_simple.wrl')
# Conector J1 (Fios do ESP)
parts += footprint('Connector_PinHeader_2.54mm', 'PinHeader_1x03_P2.54mm_Vertical', 'J1', 'Fios_do_ESP32',
                   2.54, 5.08, 0, {'1': '+5V', '2': 'GND', '3': 'ESP_TX_3V3'}, extra_model='ESP_wires.wrl')
# Resistor R1 (1k)
parts += footprint('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R1', '1k',
                   5.08, 12.7, 0, {'1': 'ESP_TX_3V3', '2': 'BASE_Q1'})
# Transistor BC337 (TO-92 largo)
parts += footprint('Package_TO_SOT_THT', 'TO-92_Inline_Wide', 'Q1', 'BC337', 7.62, 17.78, 0,
                   {'1': 'NANO_D2', '2': 'BASE_Q1', '3': 'GND'})
# Resistor R2 (10k pull-up)
parts += footprint('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R2', '10k',
                   17.78, 30.48, 90, {'1': '+5V', '2': 'NANO_D2'})

# Fios soldados por baixo (lado B.Cu / B.SilkS)
track('+5V', (2.54, 5.08), (2.54, 2.54), (38.1, 2.54), (38.1, 12.7), (35.56, 12.7))
track('+5V', (38.1, 12.7), (38.1, 43.18), (17.78, 43.18), (17.78, 30.48))
track('GND', (2.54, 7.62), (15.24, 7.62), (15.24, 12.7), (20.32, 12.7))
track('GND', (15.24, 12.7), (15.24, 17.78), (12.7, 17.78))
track('ESP_TX_3V3', (2.54, 10.16), (2.54, 12.7), (5.08, 12.7))
track('BASE_Q1', (12.7, 12.7), (12.7, 15.24), (10.16, 15.24), (10.16, 17.78))
track('NANO_D2', (20.32, 15.24), (17.78, 15.24), (17.78, 20.32), (7.62, 20.32), (7.62, 17.78))
track('NANO_D2', (17.78, 20.32), (17.78, 22.86))

# Contorno da placa e indicacoes visuais
art = gr_rect(0, 0, W, H)

# Grade sutil em silkscreen indicando os furos da placa perfurada (sem pads falsos)
for ix in range(1, int(round(W / P))):
    art += f'\t(gr_line (start {pt(ix * P, 0.5)}) (end {pt(ix * P, H - 0.5)}) (stroke (width 0.05) (type default)) (layer "F.SilkS") (uuid "{u()}"))\n'
for iy in range(1, int(round(H / P))):
    art += f'\t(gr_line (start {pt(0.5, iy * P)}) (end {pt(W - 0.5, iy * P)}) (stroke (width 0.05) (type default)) (layer "F.SilkS") (uuid "{u()}"))\n'

# Linhas de solda inferiores tambem em silkscreen traseiro para consulta
art += wire_silk((2.54, 5.08), (2.54, 2.54), (38.1, 2.54), (38.1, 12.7), (35.56, 12.7))
art += wire_silk((38.1, 12.7), (38.1, 43.18), (17.78, 43.18), (17.78, 30.48))
art += wire_silk((2.54, 7.62), (15.24, 7.62), (15.24, 12.7), (20.32, 12.7))
art += wire_silk((15.24, 12.7), (15.24, 17.78), (12.7, 17.78))
art += wire_silk((2.54, 10.16), (2.54, 12.7), (5.08, 12.7))
art += wire_silk((12.7, 12.7), (12.7, 15.24), (10.16, 15.24), (10.16, 17.78))
art += wire_silk((20.32, 15.24), (17.78, 15.24), (17.78, 20.32), (7.62, 20.32), (7.62, 17.78))
art += wire_silk((17.78, 20.32), (17.78, 22.86))

art += gr_text('FIOS DO ESP32', 9.0, 1.2, 0.8)
art += gr_text('5V', 5.6, 5.08, 0.8)
art += gr_text('GND', 6.0, 7.62, 0.8)
art += gr_text('TX', 5.6, 10.16, 0.8)
art += gr_text('D2 = RX (SoftwareSerial invertida)', 20.3, 44.6, 0.7)

net_decl = ''.join(f'\t(net {i} "{n_}")\n' for i, n_ in enumerate(NETS))
layers = ''.join(f'\t\t({i} "{nm}" {k}{(" " + chr(34) + a + chr(34)) if a else ""})\n' for i, nm, k, a in [
    (0, 'F.Cu', 'signal', ''), (2, 'B.Cu', 'signal', ''),
    (9, 'F.Adhes', 'user', 'F.Adhesive'), (11, 'B.Adhes', 'user', 'B.Adhesive'),
    (13, 'F.Paste', 'user', ''), (15, 'B.Paste', 'user', ''),
    (5, 'F.SilkS', 'user', 'F.Silkscreen'), (7, 'B.SilkS', 'user', 'B.Silkscreen'),
    (1, 'F.Mask', 'user', ''), (3, 'B.Mask', 'user', ''),
    (17, 'Dwgs.User', 'user', 'User.Drawings'), (19, 'Cmts.User', 'user', 'User.Comments'),
    (21, 'Eco1.User', 'user', 'User.Eco1'), (23, 'Eco2.User', 'user', 'User.Eco2'),
    (25, 'Edge.Cuts', 'user', ''), (27, 'Margin', 'user', ''),
    (31, 'F.CrtYd', 'user', 'F.Courtyard'), (29, 'B.CrtYd', 'user', 'B.Courtyard'),
    (35, 'F.Fab', 'user', ''), (33, 'B.Fab', 'user', '')])

pcb = f'''(kicad_pcb
\t(version 20260206)
\t(generator "pcbnew")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(layers
{layers}\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t)
{net_decl}{parts}{''.join(segs)}{art})
'''
open(OUT, 'w').write(pcb)
print('OK ->', OUT)
