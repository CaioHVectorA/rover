#!/usr/bin/env python3
"""
Gera hardware/kicad/rover_serial_bridge/rover_serial_bridge.kicad_pcb

Mini placa do estagio inversor serial (BC337) pensada para placa perfurada
(passo 2.54 mm, tudo THT) - serve como mapa de montagem:

  J1 (cabeca/ESP): 1=+5V 2=GND 3=ESP_TX_3V3
  R1 1k : ESP_TX_3V3 -> base Q1
  Q1 BC337 (TO-92 Wide 2.54mm: 1=C 2=B 3=E): emissor GND, coletor = NANO_D2
  R2 10k: pull-up +5V -> NANO_D2
  J2 (Nano): 1=+5V 2=GND 3=NANO_D2

Footprints copiados da biblioteca oficial do KiCad 10 (Flatpak).
"""
import glob
import re
import uuid

FP = glob.glob('/home/usuario/.local/share/flatpak/runtime/org.kicad.KiCad.Library.Footprints/'
               'x86_64/stable/*/files/footprints')[0]
OUT = '/home/usuario/Documentos/rover/hardware/kicad/rover_serial_bridge/rover_serial_bridge.kicad_pcb'
OX, OY = 60.96, 60.96          # origem da placa na folha (multiplo de 2.54)
W, H = 43.18, 25.4             # 17 x 10 furos


def u():
    return str(uuid.uuid4())


NETS = ['', '+5V', 'GND', 'ESP_TX_3V3', 'BASE_Q1', 'NANO_D2']
NID = {n: i for i, n in enumerate(NETS)}


def read_fp(lib, name):
    return open(f'{FP}/{lib}.pretty/{name}.kicad_mod').read()


def block_end(t, i):
    d = 0
    for j in range(i, len(t)):
        if t[j] == '(':
            d += 1
        elif t[j] == ')':
            d -= 1
            if d == 0:
                return j


def footprint(lib, name, ref, value, x, y, rot, padnets):
    t = read_fp(lib, name)
    t = re.sub(r'\n\t\(version [^)]*\)\n\t\(generator [^)]*\)\n\t\(generator_version [^)]*\)', '', t, 1)
    t = t.replace(f'(footprint "{name}"', f'(footprint "{lib}:{name}"', 1)
    t = t.replace('(layer "F.Cu")', f'(layer "F.Cu")\n\t(uuid "{u()}")\n\t(at {OX + x:.3f} {OY + y:.3f} {rot})', 1)
    t = t.replace('(property "Reference" "REF**"', f'(property "Reference" "{ref}"', 1)
    t = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{value}"', t, 1)
    # atribui redes aos pads (de tras pra frente para nao invalidar indices)
    spans = []
    for m in re.finditer(r'\(pad "([^"]+)"', t):
        spans.append((m.group(1), m.start(), block_end(t, m.start())))
    for num, s, e in reversed(spans):
        net = padnets.get(num)
        if net:
            t = t[:e] + f'\n\t\t(net {NID[net]} "{net}")\n\t' + t[e:]
    return '\t' + t.strip().replace('\n', '\n\t') + '\n'


def pt(x, y):
    return f'{OX + x:.3f} {OY + y:.3f}'


segs = []


def track(net, *pts):
    for a, b in zip(pts, pts[1:]):
        segs.append(f'\t(segment\n\t\t(start {pt(*a)})\n\t\t(end {pt(*b)})\n\t\t(width 0.6)\n'
                    f'\t\t(layer "B.Cu")\n\t\t(net {NID[net]})\n\t\t(uuid "{u()}")\n\t)\n')


def gr_text(s, x, y, size=1.0, layer='F.SilkS'):
    return (f'\t(gr_text "{s}"\n\t\t(at {pt(x, y)} 0)\n\t\t(layer "{layer}")\n\t\t(uuid "{u()}")\n'
            f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size {size} {size})\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n')


def gr_rect(x1, y1, x2, y2, layer='Edge.Cuts', width=0.1):
    return (f'\t(gr_rect\n\t\t(start {pt(x1, y1)})\n\t\t(end {pt(x2, y2)})\n'
            f'\t\t(stroke\n\t\t\t(width {width})\n\t\t\t(type default)\n\t\t)\n\t\t(fill no)\n'
            f'\t\t(layer "{layer}")\n\t\t(uuid "{u()}")\n\t)\n')


HDR = 'Connector_PinHeader_2.54mm'
parts = ''
parts += footprint(HDR, 'PinHeader_1x03_P2.54mm_Vertical', 'J1', 'Cabeca_ESP', 5.08, 5.08, 0,
                   {'1': '+5V', '2': 'GND', '3': 'ESP_TX_3V3'})
parts += footprint(HDR, 'PinHeader_1x03_P2.54mm_Vertical', 'J2', 'Nano', 35.56, 5.08, 0,
                   {'1': '+5V', '2': 'GND', '3': 'NANO_D2'})
parts += footprint('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R1', '1k',
                   5.08, 15.24, 0, {'1': 'ESP_TX_3V3', '2': 'BASE_Q1'})
parts += footprint('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R2', '10k',
                   30.48, 5.08, 270, {'1': '+5V', '2': 'NANO_D2'})
parts += footprint('Package_TO_SOT_THT', 'TO-92_Inline_Wide', 'Q1', 'BC337', 17.78, 17.78, 0,
                   {'1': 'NANO_D2', '2': 'BASE_Q1', '3': 'GND'})

# trilhas (B.Cu) - cada trilha = "fio" que voce faria na perfurada
track('+5V', (5.08, 5.08), (35.56, 5.08))
track('GND', (5.08, 7.62), (35.56, 7.62))
track('GND', (22.86, 17.78), (22.86, 7.62))
track('ESP_TX_3V3', (5.08, 10.16), (5.08, 15.24))
track('BASE_Q1', (12.7, 15.24), (20.32, 15.24), (20.32, 17.78))
track('NANO_D2', (17.78, 17.78), (17.78, 20.32), (33.02, 20.32), (33.02, 12.7), (30.48, 12.7))
track('NANO_D2', (33.02, 10.16), (35.56, 10.16))
track('NANO_D2', (33.02, 12.7), (33.02, 10.16))

art = ''
art += gr_rect(0, 0, W, H)
art += gr_text('+5V', 9.5, 5.08, 0.8)
art += gr_text('GND', 9.5, 7.62, 0.8)
art += gr_text('TX', 9.5, 10.16, 0.8)
art += gr_text('+5V', 39.3, 5.08, 0.8)
art += gr_text('GND', 39.3, 7.62, 0.8)
art += gr_text('D2', 39.3, 10.16, 0.8)
art += gr_text('ROVER SERIAL BC337', 20.3, 24.0, 1.0)
art += gr_text('ESP -> NANO', 20.3, 22.0, 0.8)

net_decl = ''.join(f'\t(net {i} "{n}")\n' for i, n in enumerate(NETS))
layers = ''.join(f'\t\t({i} "{n}" {k}{(" " + chr(34) + a + chr(34)) if a else ""})\n' for i, n, k, a in [
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
\t\t(pcbplotparams
\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)
\t\t\t(outputdirectory "")
\t\t)
\t)
{net_decl}{parts}{segs and ''.join(segs)}{art})
'''
open(OUT, 'w').write(pcb)
print('OK ->', OUT)
