#!/usr/bin/env python3
"""
Gera hardware/kicad/rover_serial_bridge/rover_serial_bridge.kicad_sch

Chicote serial de 4 fios entre ESP32-S3-CAM (cabeça) e Arduino Nano V3 (chassi):
  Fio 1: +5V | Fio 2: GND
  Fio 3: ESP GPIO43 (TX 3.3V) -> R1 1k -> base BC337; coletor -> Nano D2 + pull-up 10k no +5V

Os símbolos (ESP32-S3-WROOM-1, Arduino_Nano, Q_NPN_CBE, R) são copiados da
biblioteca oficial do KiCad 10 (Flatpak org.kicad.KiCad.Library.Symbols).
"""
import glob
import re
import uuid

LIB = glob.glob('/home/usuario/.local/share/flatpak/runtime/'
                'org.kicad.KiCad.Library.Symbols/x86_64/stable/*/files/symbols')[0]
OUT = '/home/usuario/Documentos/rover/hardware/kicad/rover_serial_bridge/rover_serial_bridge.kicad_sch'
ROOT = 'a6ec2726-0e9e-4a6c-9407-35393c0da275'
PROJ = 'rover_serial_bridge'


def u():
    return str(uuid.uuid4())


def extract(lib, name):
    t = open(f'{LIB}/{lib}.kicad_sym').read()
    m = re.search(r'\n\t\(symbol "%s"\n' % re.escape(name), t)
    i = m.start() + 1
    d = 0
    for j in range(i, len(t)):
        if t[j] == '(':
            d += 1
        elif t[j] == ')':
            d -= 1
            if d == 0:
                return t[i:j + 1]


def pins_of(s):
    out = {}
    for m in re.finditer(r'\(pin (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)'
                         r'.*?\(name "([^"]*)".*?\(number "([^"]*)"', s, re.S):
        out[m.group(7)] = (float(m.group(3)), float(m.group(4)), m.group(6))
    return out


def prop(s, key):
    m = re.search(r'\(property "%s" "([^"]*)"' % key, s)
    return m.group(1) if m else ''


def indent(s, n=2):
    return '\n'.join(('\t' * n + l) if l.strip() else l for l in s.split('\n'))


# ---------------------------------------------------------------- símbolos
esp = extract('RF_Module', 'ESP32-S3-WROOM-1')
nano = extract('MCU_Module', 'Arduino_Nano_v2.x').replace('Arduino_Nano_v2.x', 'Arduino_Nano_v3.x')
npn = extract('Transistor_BJT', 'Q_NPN_CBE')
res = extract('Device', 'R')

LIBS = {
    'RF_Module:ESP32-S3-WROOM-1': esp,
    'MCU_Module:Arduino_Nano_v3.x': nano,
    'Transistor_BJT:Q_NPN_CBE': npn,
    'Device:R': res,
}


def lib_block(lib_id, body):
    short = lib_id.split(':')[1]
    body = body.replace('(symbol "%s"' % short, '(symbol "%s"' % lib_id, 1)
    return indent(body, 2)


parts = []
wires = []
labels = []
junctions = []
texts = []


def rot(px, py, a):
    a %= 360
    if a == 0:
        return px, py
    if a == 90:
        return -py, px
    if a == 180:
        return -px, -py
    return py, -px  # 270


def place(lib_id, ref, value, ox, oy, angle=0, footprint=None):
    body = LIBS[lib_id]
    pins = pins_of(body)
    fp = footprint if footprint is not None else prop(body, 'Footprint')
    pin_pos = {}
    pin_lines = ''
    for num, (px, py, _) in pins.items():
        rx, ry = rot(px, py, angle)
        pin_pos[num] = (round(ox + rx, 3), round(oy - ry, 3))
        pin_lines += f'\t\t(pin "{num}"\n\t\t\t(uuid "{u()}")\n\t\t)\n'

    def p(name, val, dx, dy, hide=False):
        h = '\n\t\t\t\t(hide yes)' if hide else ''
        return (f'\t\t(property "{name}" "{val}"\n\t\t\t(at {ox + dx} {oy + dy} 0)\n'
                f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t){h}\n\t\t\t)\n\t\t)\n')

    s = (f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {ox} {oy} {angle})\n\t\t(unit 1)\n'
         f'\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n'
         f'\t\t(uuid "{u()}")\n')
    if 'Arduino' in lib_id or 'ESP' in lib_id:
        rpos, vpos = (-20, -32), (-20, 34)
    elif lib_id == 'Device:R' and angle == 0:
        rpos, vpos = (4.5, -1.5), (4.5, 1.5)
    else:
        rpos, vpos = (0, -7), (0, 7)
    s += p('Reference', ref, *rpos)
    s += p('Value', value, *vpos)
    s += p('Footprint', fp, 0, 0, True)
    s += p('Datasheet', '~', 0, 0, True)
    s += pin_lines
    s += (f'\t\t(instances\n\t\t\t(project "{PROJ}"\n\t\t\t\t(path "/{ROOT}"\n'
          f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')
    parts.append(s)
    return pin_pos


def wire(*pts):
    for a, b in zip(pts, pts[1:]):
        wires.append(f'\t(wire\n\t\t(pts\n\t\t\t(xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})\n\t\t)\n'
                     f'\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{u()}")\n\t)')


def label(name, x, y, angle, just):
    labels.append(f'\t(label "{name}"\n\t\t(at {x} {y} {angle})\n\t\t(effects\n\t\t\t(font\n'
                  f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{u()}")\n\t)')


def junction(x, y):
    junctions.append(f'\t(junction\n\t\t(at {x} {y})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "{u()}")\n\t)')


def text(s, x, y, size=1.27, bold=False):
    s = s.replace('"', "'").replace('\n', '\\n')
    b = '\n\t\t\t\t(bold yes)' if bold else ''
    texts.append(f'\t(text "{s}"\n\t\t(exclude_from_sim no)\n\t\t(at {x} {y} 0)\n\t\t(effects\n\t\t\t(font\n'
                 f'\t\t\t\t(size {size} {size}){b}\n\t\t\t)\n\t\t\t(justify left top)\n\t\t)\n\t\t(uuid "{u()}")\n\t)')


def stub(pt, dx, dy, name):
    """fio curto de 5.08mm saindo do pino + label de rede."""
    end = (round(pt[0] + dx, 3), round(pt[1] + dy, 3))
    wire(pt, end)
    if dx > 0:
        label(name, end[0], end[1], 0, 'left bottom')
    elif dx < 0:
        label(name, end[0], end[1], 180, 'right bottom')
    elif dy < 0:
        label(name, end[0], end[1], 90, 'left bottom')
    else:
        label(name, end[0], end[1], 270, 'right bottom')


# ------------------------------------------------------------ componentes
E = place('RF_Module:ESP32-S3-WROOM-1', 'U1', 'ESP32-S3-CAM (cabeca)', 81.28, 101.6)
N = place('MCU_Module:Arduino_Nano_v3.x', 'A1', 'Arduino Nano V3 (chassi)', 228.6, 101.6)
Q = place('Transistor_BJT:Q_NPN_CBE', 'Q1', 'BC337 (NPN, TO-92)', 170.18, 99.06)
R1 = place('Device:R', 'R1', '1k', 152.4, 99.06, 90)
R2 = place('Device:R', 'R2', '10k', 190.5, 81.28, 0)

# ESP32-S3: GPIO43 = TXD0 (pino 37)
stub(E['37'], 5.08, 0, 'ESP_TX_3V3')
stub(E['1'], 0, 5.08, 'GND')

# Estagio inversor: ESP TX -> R1 (1k) -> base (pino 2); emissor (pino 3) -> GND
stub(R1['1'], -5.08, 0, 'ESP_TX_3V3')
wire(R1['2'], Q['2'])
stub(Q['3'], 0, 5.08, 'GND')

# Coletor (pino 1) -> Nano D2 (pino 5) + pull-up R2 10k em +5V do Nano
d2 = N['5']
col = Q['1']
wire(col, (col[0], d2[1]), d2)
junction(190.5, d2[1])
wire((190.5, d2[1]), R2['2'])
stub(R2['1'], 0, -5.08, '+5V')

# Nano: +5V (pino 27) e GND (pino 4)
stub(N['27'], 0, -5.08, '+5V')
stub(N['4'], 0, 5.08, 'GND')

# ---------------------------------------------------------------- anotacoes
text('ROVER 4WD - SERIAL ESP32-S3-CAM (TX) -> ARDUINO NANO (RX D2)', 25.4, 20.32, 2.5, True)
text('Fios do chicote: +5V | GND | ESP_TX_3V3', 25.4, 27.94)
text('ESP GPIO43 (TX) -> R1 1k -> base Q1 (BC337). Emissor no GND.\n'
     'Coletor -> Nano D2 (RX) e pull-up R2 10k no +5V do Nano.\n'
     'O transistor sobe o nivel para 5V, mas INVERTE o sinal: no Nano use SoftwareSerial com logica invertida\n'
     '(SoftwareSerial(rx, tx, true)). GND do ESP e do Nano ligados juntos.', 25.4, 160.02)
text('BC337 TO-92 (face plana para voce): 1 = Coletor | 2 = Base | 3 = Emissor', 25.4, 180.34)

# ------------------------------------------------------------------ saída
lib_syms = '\n'.join(lib_block(k, v) for k, v in LIBS.items())
sch = f'''(kicad_sch
\t(version 20251024)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{ROOT}")
\t(paper "A4")
\t(lib_symbols
{lib_syms}
\t)
{chr(10).join(parts)}
{chr(10).join(wires)}
{chr(10).join(junctions)}
{chr(10).join(labels)}
{chr(10).join(texts)}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
'''
open(OUT, 'w').write(sch)
print('OK ->', OUT)
