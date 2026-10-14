#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera ilustrações técnicas de engenharia de alta fidelidade para a pasta imagens_importantes/
1. desenho_tecnico_motor_jga16_050.png
2. desenho_tecnico_micro_servo_sg90.png
3. esquema_eletrico_chicote_esp32_nano.png
"""

from PIL import Image, ImageDraw, ImageFont
import os

font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
font_sec = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 16)
font_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 13)
font_regular = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", 12)
font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 11)

# ==============================================================================
# 1. DESENHO TÉCNICO DO MOTOR JGA16-050 E VÃO LIVRE COM RODA 22MM
# ==============================================================================
def draw_jga050():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([(0, 0), (w, 60)], fill=(15, 23, 42))
    d.text((30, 16), "DESENHO TÉCNICO DE ENGENHARIA - MOTOR JGA16-050 (16mm) & VÃO LIVRE", fill=(255, 255, 255), font=font_title)
    d.rectangle([(0, 60), (w, 85)], fill=(30, 41, 59))
    d.text((30, 64), "Cotas milimétricas nominais para modelagem CAD 3D do chassi e cálculo do vão livre de 3,0 mm ao solo", fill=(226, 232, 240), font=font_small)

    # Painel 1: Vista Lateral do Motor (Dimensões do corpo e eixo)
    d.rectangle([(30, 110), (680, 430)], outline=(203, 213, 225), width=2, fill=(248, 250, 252))
    d.text((50, 125), "1. VISTA LATERAL DO MOTOR CILÍNDRICO (16 mm)", fill=(30, 58, 138), font=font_sec)

    # Desenho Motor Lateral
    # Corpo Traseiro (DC Motor 050): 16mm diâmetro x 22mm comprimento
    # Caixa Redução Dianteira: 16mm diâmetro x 12.5mm comprimento
    # Flange frontal: diâmetro 6mm x 1.5mm
    # Eixo D 3mm: comprimento 10mm
    mx, my = 120, 260
    # Corpo DC
    d.rectangle([(mx, my - 60), (mx + 200, my + 60)], fill=(148, 163, 184), outline=(51, 65, 85), width=2)
    d.text((mx + 45, my - 10), "Corpo Motor DC 050", fill=(15, 23, 42), font=font_bold)
    # Caixa de Redução
    d.rectangle([(mx + 200, my - 60), (mx + 320, my + 60)], fill=(203, 213, 225), outline=(51, 65, 85), width=2)
    d.text((mx + 210, my - 10), "Caixa Redução\nMetálica 16mm", fill=(15, 23, 42), font=font_bold)
    # Flange frontal
    d.rectangle([(mx + 320, my - 25), (mx + 335, my + 25)], fill=(100, 116, 139), outline=(51, 65, 85), width=2)
    # Eixo metálico com corte em D
    d.rectangle([(mx + 335, my - 14), (mx + 435, my + 14)], fill=(241, 245, 249), outline=(51, 65, 85), width=2)
    d.line([(mx + 335, my - 10), (mx + 435, my - 10)], fill=(148, 163, 184), width=1)
    d.text((mx + 350, my + 20), "Eixo D: Ø3,0 mm", fill=(185, 28, 28), font=font_bold)

    # Cotas Laterais
    # Cota Diâmetro 16mm
    d.line([(mx - 30, my - 60), (mx - 30, my + 60)], fill=(30, 41, 59), width=2)
    d.line([(mx - 40, my - 60), (mx - 20, my - 60)], fill=(30, 41, 59), width=2)
    d.line([(mx - 40, my + 60), (mx - 20, my + 60)], fill=(30, 41, 59), width=2)
    d.text((mx - 95, my - 10), "Ø 16,0 mm", fill=(30, 41, 59), font=font_bold)

    # Cota Comprimento do Corpo (~34.5 mm)
    d.line([(mx, my + 80), (mx + 320, my + 80)], fill=(30, 41, 59), width=2)
    d.line([(mx, my + 70), (mx, my + 90)], fill=(30, 41, 59), width=2)
    d.line([(mx + 320, my + 70), (mx + 320, my + 90)], fill=(30, 41, 59), width=2)
    d.text((mx + 110, my + 88), "Comprimento Corpo: ~34,5 mm", fill=(30, 41, 59), font=font_bold)

    # Cota Eixo (10.0 mm)
    d.line([(mx + 335, my + 60), (mx + 435, my + 60)], fill=(185, 28, 28), width=2)
    d.line([(mx + 335, my + 50), (mx + 335, my + 70)], fill=(185, 28, 28), width=2)
    d.line([(mx + 435, my + 50), (mx + 435, my + 70)], fill=(185, 28, 28), width=2)
    d.text((mx + 350, my + 68), "10,0 mm", fill=(185, 28, 28), font=font_bold)

    # Painel 2: Vista Frontal (Furação M2 e Chanfro D)
    d.rectangle([(710, 110), (1170, 430)], outline=(203, 213, 225), width=2, fill=(248, 250, 252))
    d.text((730, 125), "2. VISTA FRONTAL (FIXAÇÃO M2 & EIXO D)", fill=(30, 58, 138), font=font_sec)

    fx, fy = 940, 270
    # Círculo externo carcaça 16mm (raio 75px)
    d.ellipse([(fx - 75, fy - 75), (fx + 75, fy + 75)], fill=(203, 213, 225), outline=(51, 65, 85), width=2)
    # Furos M2 (espaçados em 10mm -> 50px de raio de furação)
    d.ellipse([(fx - 45 - 8, fy - 8), (fx - 45 + 8, fy + 8)], fill=(15, 23, 42))
    d.ellipse([(fx + 45 - 8, fy - 8), (fx + 45 + 8, fy + 8)], fill=(15, 23, 42))
    d.text((fx - 55, fy - 35), "M2", fill=(185, 28, 28), font=font_bold)
    d.text((fx + 35, fy - 35), "M2", fill=(185, 28, 28), font=font_bold)
    # Cota entre furos 10mm
    d.line([(fx - 45, fy + 25), (fx + 45, fy + 25)], fill=(30, 41, 59), width=2)
    d.line([(fx - 45, fy + 20), (fx - 45, fy + 30)], fill=(30, 41, 59), width=2)
    d.line([(fx + 45, fy + 20), (fx + 45, fy + 30)], fill=(30, 41, 59), width=2)
    d.text((fx - 35, fy + 32), "Entre-furos: 10,0 mm", fill=(30, 41, 59), font=font_small)

    # Eixo D central
    d.ellipse([(fx - 18, fy - 18), (fx + 18, fy + 18)], fill=(241, 245, 249), outline=(185, 28, 28), width=2)
    # Chanfro D
    d.rectangle([(fx + 10, fy - 18), (fx + 22, fy + 18)], fill=(203, 213, 225))
    d.line([(fx + 10, fy - 15), (fx + 10, fy + 15)], fill=(185, 28, 28), width=2)
    d.text((fx - 40, fy - 95), "Perfil Chanfrado em D (3,0 mm)", fill=(185, 28, 28), font=font_small)

    # Painel 3: Comparação Geométrica e Cálculo do Vão Livre (Ground Clearance)
    d.rectangle([(30, 450), (1170, 720)], outline=(30, 58, 138), width=2, fill=(239, 246, 255))
    d.text((50, 465), "3. ANÁLISE GEOMÉTRICA DO VÃO LIVRE COM RODA STICKYMAX DE 22 mm", fill=(30, 58, 138), font=font_sec)

    # Desenho da Roda de 22mm e do Motor
    cx, cy = 200, 585
    # Solo
    d.line([(50, cy + 90), (1150, cy + 90)], fill=(100, 116, 139), width=4)
    d.text((60, cy + 95), "LINHA DO SOLO / PISO", fill=(100, 116, 139), font=font_bold)

    # Roda 22mm (Raio = 11mm -> 90px de escala)
    r_roda = 90
    d.ellipse([(cx - r_roda, cy - r_roda), (cx + r_roda, cy + r_roda)], fill=(254, 242, 242), outline=(220, 38, 38), width=3)
    d.text((cx - 75, cy - 70), "Roda StickyMAX S20", fill=(220, 38, 38), font=font_bold)
    d.text((cx - 50, cy - 50), "Diâmetro = 22,0 mm", fill=(220, 38, 38), font=font_bold)
    d.text((cx - 40, cy - 35), "Raio = 11,0 mm", fill=(220, 38, 38), font=font_small)

    # Motor 16mm concêntrico ao mesmo eixo
    r_motor = int(90 * (8.0 / 11.0)) # 65px
    d.ellipse([(cx - r_motor, cy - r_motor), (cx + r_motor, cy + r_motor)], fill=(226, 232, 240), outline=(15, 23, 42), width=2)
    d.text((cx - 50, cy - 10), "Motor JGA16-050", fill=(15, 23, 42), font=font_bold)
    d.text((cx - 45, cy + 8), "Diâmetro = 16,0 mm", fill=(15, 23, 42), font=font_small)
    d.text((cx - 35, cy + 24), "Raio = 8,0 mm", fill=(15, 23, 42), font=font_small)

    # Ponto do Eixo Central
    d.ellipse([(cx - 5, cy - 5), (cx + 5, cy + 5)], fill=(185, 28, 28))

    # Cota do Vão Livre
    d.line([(cx + 120, cy + r_motor), (cx + 120, cy + r_roda)], fill=(22, 101, 52), width=3)
    d.line([(cx + 110, cy + r_motor), (cx + 130, cy + r_motor)], fill=(22, 101, 52), width=2)
    d.line([(cx + 110, cy + r_roda), (cx + 130, cy + r_roda)], fill=(22, 101, 52), width=2)
    d.line([(cx, cy + r_motor), (cx + 120, cy + r_motor)], fill=(148, 163, 184), width=1)

    d.text((cx + 135, cy + r_motor + 2), "VÃO LIVRE = 3,0 mm!", fill=(22, 101, 52), font=font_title)
    d.text((cx + 135, cy + r_motor + 30), "(Raio da Roda: 11,0 mm) - (Raio do Motor: 8,0 mm) = 3,0 mm exatos", fill=(22, 101, 52), font=font_bold)

    # Caixa de Decisão de Projeto 3D
    d.rectangle([(620, 520), (1140, 680)], fill=(255, 255, 255), outline=(22, 101, 52), width=2)
    d.text((640, 535), "DIRETRIZ OBRIGATÓRIA PARA A MODELAGEM 3D:", fill=(22, 101, 52), font=font_bold)
    desc_txt = (
        "• Como o vão livre sob o motor é de apenas 3,0 mm, a parede plástica\n"
        "  do chassi NÃO PODE passar por baixo do motor (roubaria o vão livre).\n"
        "• O motor deve ser montado abraçado por cima e pelas laterais (berço invertido).\n"
        "• Montagem da Roda Invertida (Orientador): Roda montada voltada para fora\n"
        "  do chassi; motor e caixa de redução ficam 100% alojados internamente.\n"
        "• Se desejar andar em pisos com desníveis no futuro, a troca para rodas\n"
        "  de 32 mm eleva o vão livre para 8,0 mm automaticamente."
    )
    d.text((640, 560), desc_txt, fill=(15, 23, 42), font=font_small)

    caminho = "/home/usuario/Documentos/rover/imagens_importantes/desenho_tecnico_motor_jga16_050.png"
    img.save(caminho)
    print(f"Salvo: {caminho}")


# ==============================================================================
# 2. DESENHO TÉCNICO DO MICRO SERVO SG90 (PAN & TILT)
# ==============================================================================
def draw_sg90():
    w, h = 1000, 600
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([(0, 0), (w, 60)], fill=(15, 23, 42))
    d.text((30, 16), "DESENHO TÉCNICO DE ENGENHARIA - MICRO SERVO SG90 9g", fill=(255, 255, 255), font=font_title)
    d.rectangle([(0, 60), (w, 85)], fill=(30, 41, 59))
    d.text((30, 64), "Dimensões nominais de encaixe para suporte Pan & Tilt impresso em 3D", fill=(226, 232, 240), font=font_small)

    # Painel Principal
    d.rectangle([(30, 105), (970, 570)], outline=(203, 213, 225), width=2, fill=(248, 250, 252))

    # Desenho Servo SG90 Vista Lateral
    sx, sy = 180, 260
    # Corpo principal: 22.8 mm x 28.5 mm (escala: 1mm = 10px)
    bw = 228
    bh = 285
    flange_h = 40  # altura da aba

    # Aba / Flange de fixação (32.5 mm de largura total -> 325px)
    d.rectangle([(sx - 48, sy + 70), (sx + bw + 48, sy + 70 + flange_h)], fill=(59, 130, 246), outline=(30, 58, 138), width=2)
    # Furos de fixação na aba (distância entre centros = 28.0 mm -> 280px)
    d.ellipse([(sx - 26 - 6, sy + 85), (sx - 26 + 6, sy + 97)], fill=(255, 255, 255), outline=(15, 23, 42))
    d.ellipse([(sx + bw + 26 - 6, sy + 85), (sx + bw + 26 + 6, sy + 97)], fill=(255, 255, 255), outline=(15, 23, 42))

    # Corpo inferior (abaixo da aba: ~18.5 mm)
    d.rectangle([(sx, sy + 110), (sx + bw, sy + bh)], fill=(96, 165, 250), outline=(30, 58, 138), width=2)
    d.text((sx + 60, sy + 180), "Corpo Inferior SG90\n(Motor DC + Engrenagens)", fill=(15, 23, 42), font=font_bold)

    # Corpo superior (acima da aba: ~10 mm)
    d.rectangle([(sx, sy), (sx + bw, sy + 70)], fill=(96, 165, 250), outline=(30, 58, 138), width=2)

    # Eixo estriado de saída (spline): Ø4.8 mm x 4.0 mm altura
    d.rectangle([(sx + 35, sy - 40), (sx + 83, sy)], fill=(255, 255, 255), outline=(185, 28, 28), width=2)
    d.text((sx + 20, sy - 60), "Eixo Estriado: Ø4,8 mm", fill=(185, 28, 28), font=font_bold)

    # Cotas
    # Cota Comprimento do Corpo (22.8 mm)
    d.line([(sx, sy + bh + 30), (sx + bw, sy + bh + 30)], fill=(30, 41, 59), width=2)
    d.line([(sx, sy + bh + 20), (sx, sy + bh + 40)], fill=(30, 41, 59), width=2)
    d.line([(sx + bw, sy + bh + 20), (sx + bw, sy + bh + 40)], fill=(30, 41, 59), width=2)
    d.text((sx + 70, sy + bh + 35), "Corpo: 22,8 mm", fill=(30, 41, 59), font=font_bold)

    # Cota Distância Entre Furos da Flange (28.0 mm)
    d.line([(sx - 26, sy + 40), (sx + bw + 26, sy + 40)], fill=(185, 28, 28), width=2)
    d.line([(sx - 26, sy + 30), (sx - 26, sy + 50)], fill=(185, 28, 28), width=2)
    d.line([(sx + bw + 26, sy + 30), (sx + bw + 26, sy + 50)], fill=(185, 28, 28), width=2)
    d.text((sx + 50, sy + 18), "Entre-furos de Fixação: 28,0 mm", fill=(185, 28, 28), font=font_bold)

    # Cota Comprimento Total com Flanges (32.5 mm)
    d.line([(sx - 48, sy + bh + 70), (sx + bw + 48, sy + bh + 70)], fill=(30, 41, 59), width=2)
    d.line([(sx - 48, sy + bh + 60), (sx - 48, sy + bh + 80)], fill=(30, 41, 59), width=2)
    d.line([(sx + bw + 48, sy + bh + 60), (sx + bw + 48, sy + bh + 80)], fill=(30, 41, 59), width=2)
    d.text((sx + 45, sy + bh + 75), "Comprimento Total (Flanges): 32,5 mm", fill=(30, 41, 59), font=font_bold)

    # Cota Altura Total (28.5 mm)
    d.line([(sx - 75, sy), (sx - 75, sy + bh)], fill=(30, 41, 59), width=2)
    d.line([(sx - 85, sy), (sx - 65, sy)], fill=(30, 41, 59), width=2)
    d.line([(sx - 85, sy + bh), (sx - 65, sy + bh)], fill=(30, 41, 59), width=2)
    d.text((sx - 165, sy + 130), "Altura:\n28,5 mm", fill=(30, 41, 59), font=font_bold)

    # Tabela Lateral de Especificações
    tx = 580
    d.rectangle([(tx, 130), (940, 540)], fill=(255, 255, 255), outline=(59, 130, 246), width=2)
    d.text((tx + 20, 145), "ESPECIFICAÇÕES TÉCNICAS (SG90):", fill=(30, 58, 138), font=font_sec)

    specs = [
        ("Peso:", "9 gramas (ultraleve)"),
        ("Dimensões do Corpo:", "22.8 mm x 12.2 mm x 28.5 mm"),
        ("Largura da Caixa (Perfil):", "12.2 mm (profundidade de encaixe)"),
        ("Comprimento com Flange:", "32.5 mm"),
        ("Furação de Montagem:", "2 furos com centro a centro de 28.0 mm"),
        ("Torque de Operação:", "1.6 kgf·cm (@ 4.8V) - Excelente para a câmera!"),
        ("Velocidade:", "0.12 s / 60 graus"),
        ("Tensão de Operação:", "4.8V a 5.0V (direto do Step-Down Mini 560)"),
        ("Pinagem dos Cabos:", ""),
        ("  • Marrom:", "GND (Terra Comum)"),
        ("  • Vermelho:", "VCC (+5.0V do Step-Down)"),
        ("  • Amarelo / Laranja:", "Sinal PWM (Arduino Nano D9 e D10)")
    ]

    ty = 180
    for label, val in specs:
        d.text((tx + 20, ty), label, fill=(15, 23, 42), font=font_bold)
        d.text((tx + 180, ty), val, fill=(30, 41, 59), font=font_small)
        ty += 28

    caminho = "/home/usuario/Documentos/rover/imagens_importantes/desenho_tecnico_micro_servo_sg90.png"
    img.save(caminho)
    print(f"Salvo: {caminho}")


# ==============================================================================
# 3. DIAGRAMA ESQUEMÁTICO DO CHICOTE SERIAL ESP32 <-> NANO & ELETRÔNICA
# ==============================================================================
def draw_electric_schematic():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([(0, 0), (w, 60)], fill=(15, 23, 42))
    d.text((30, 16), "ESQUEMA ELÉTRICO - CHICOTE SERIAL (4 FIOS) & ARQUITETURA DE CONTROLE", fill=(255, 255, 255), font=font_title)
    d.rectangle([(0, 60), (w, 85)], fill=(30, 41, 59))
    d.text((30, 64), "Separação funcional: Cabeça Móvel Pan/Tilt (ESP32) vs Chassi Fixo (Arduino Nano + TB6612FNG + Energia)", fill=(226, 232, 240), font=font_small)

    # Bloco 1: Cabeça Móvel (ESP32-CAM)
    bx1, by1 = 40, 110
    bw1, bh1 = 340, 650
    d.rectangle([(bx1, by1), (bx1 + bw1, by1 + bh1)], fill=(241, 245, 249), outline=(30, 58, 138), width=3)
    d.rectangle([(bx1, by1), (bx1 + bw1, by1 + 45)], fill=(30, 58, 138))
    d.text((bx1 + 15, by1 + 12), "CABEÇA MÓVEL (PAN / TILT)", fill=(255, 255, 255), font=font_sec)

    d.rectangle([(bx1 + 20, by1 + 65), (bx1 + bw1 - 20, by1 + 140)], fill=(255, 255, 255), outline=(148, 163, 184), width=1)
    d.text((bx1 + 35, by1 + 75), "MÓDULO ESP32 (OV2640/OV5640)", fill=(15, 23, 42), font=font_bold)
    d.text((bx1 + 35, by1 + 95), "• Streaming de Vídeo Wi-Fi em tempo real\n• WebServer de Controle (Joypad Virtual)\n• Processamento de Visão", fill=(71, 85, 105), font=font_small)

    # Pinos expostos do ESP32
    d.rectangle([(bx1 + 20, by1 + 160), (bx1 + bw1 - 20, by1 + 480)], fill=(255, 255, 255), outline=(148, 163, 184), width=1)
    d.text((bx1 + 35, by1 + 175), "CONEXÕES DO ESP32:", fill=(30, 58, 138), font=font_bold)

    esp_pins = [
        ("Pino 5V:", "Entrada de Alimentação (do Step-Down)", (220, 38, 38)),
        ("Pino GND:", "Terra de Referência Comum", (15, 23, 42)),
        ("GPIO 1 (TX):", "Saída Serial Comandos -> RX Nano", (37, 99, 235)),
        ("GPIO 3 (RX):", "Entrada Serial Telemetria (via Divisor)", (22, 101, 52)),
        ("16x GPIOs:", "Ocupados pela Câmera Paralela DVP", (148, 163, 184)),
        ("6x GPIOs:", "Ocupados pelo Leitor MicroSD / Flash", (148, 163, 184))
    ]
    py = by1 + 210
    for p, desc, cor in esp_pins:
        d.text((bx1 + 35, py), p, fill=cor, font=font_bold)
        d.text((bx1 + 35, py + 18), desc, fill=(71, 85, 105), font=font_small)
        py += 44

    # Bloco Central: Chicote de 4 Fios
    cx1, cx2 = bx1 + bw1, 520
    d.rectangle([(cx1 + 10, by1 + 180), (cx2 - 10, by1 + 450)], fill=(254, 249, 195), outline=(202, 138, 4), width=2)
    d.text((cx1 + 20, by1 + 195), "CHICOTE 4 FIOS", fill=(133, 77, 14), font=font_bold)
    d.text((cx1 + 18, by1 + 215), "Articulação Móvel", fill=(133, 77, 14), font=font_small)

    # 4 Fios
    wires = [
        (by1 + 250, "FIO 1: 5.0V (Alimentação)", (220, 38, 38)),
        (by1 + 295, "FIO 2: GND (Terra Comum)", (15, 23, 42)),
        (by1 + 340, "FIO 3: TX -> RX (Comandos)", (37, 99, 235)),
        (by1 + 385, "FIO 4: RX <- TX (Telemetria)", (22, 101, 52))
    ]
    for wy, wtext, wcor in wires:
        d.line([(bx1 + bw1 - 10, wy), (cx2 + 10, wy)], fill=wcor, width=4)
        d.text((cx1 + 15, wy - 16), wtext, fill=wcor, font=font_small)

    # Bloco 2: Chassi Fixo (Arduino Nano + Periféricos)
    bx2, by2 = 530, 110
    bw2, bh2 = 630, 650
    d.rectangle([(bx2, by2), (bx2 + bw2, by2 + bh2)], fill=(248, 250, 252), outline=(22, 101, 52), width=3)
    d.rectangle([(bx2, by2), (bx2 + bw2, by2 + 45)], fill=(22, 101, 52))
    d.text((bx2 + 15, by2 + 12), "CHASSI FIXO (ARDUINO NANO + ATUADORES & ENERGIA)", fill=(255, 255, 255), font=font_sec)

    # Sub-bloco Arduino Nano
    nx, ny = bx2 + 20, by2 + 65
    nw, nh = 270, 400
    d.rectangle([(nx, ny), (nx + nw, ny + nh)], fill=(255, 255, 255), outline=(59, 130, 246), width=2)
    d.text((nx + 15, ny + 12), "ARDUINO NANO V3 (5V)", fill=(30, 58, 138), font=font_bold)

    nano_conns = [
        ("D0 (RX):", "Recebe Comandos do ESP32 TX", (37, 99, 235)),
        ("D1 (TX):", "Telemetria -> Divisor -> ESP32 RX", (22, 101, 52)),
        ("D3, D5, D6:", "PWM Motores (TB6612FNG)", (185, 28, 28)),
        ("D4, D7, D8:", "Direção Motores (TB6612FNG)", (185, 28, 28)),
        ("D9 (PWM):", "Sinal Servo Pan (Giro Horiz.)", (217, 119, 6)),
        ("D10 (PWM):", "Sinal Servo Tilt (Inclin. Vert.)", (217, 119, 6)),
        ("D11 (PWM):", "DIN Fita 8 LEDs WS2812B", (147, 51, 234)),
        ("D12:", "Sinal Buzzer Passivo 5V", (71, 85, 105)),
        ("A0 (ADC):", "Lê Divisor Bateria (10k / 4.7k)", (220, 38, 38)),
        ("5V / GND:", "Barramento 5V Step-Down & GND", (15, 23, 42))
    ]
    py2 = ny + 40
    for p, cdesc, col in nano_conns:
        d.text((nx + 15, py2), p, fill=col, font=font_bold)
        d.text((nx + 15, py2 + 15), cdesc, fill=(71, 85, 105), font=font_small)
        py2 += 34

    # Sub-bloco Atuadores da Direita
    ax, ay = nx + nw + 20, by2 + 65
    aw, ah = 300, 550
    d.rectangle([(ax, ay), (ax + aw, ay + ah)], fill=(255, 255, 255), outline=(148, 163, 184), width=1)
    d.text((ax + 15, ay + 12), "MÓDULOS CONECTADOS AO NANO:", fill=(15, 23, 42), font=font_bold)

    # 1. Driver TB6612FNG
    d.rectangle([(ax + 10, ay + 40), (ax + aw - 10, ay + 150)], fill=(241, 245, 249), outline=(185, 28, 28), width=1)
    d.text((ax + 20, ay + 48), "Driver Duplo TB6612FNG", fill=(185, 28, 28), font=font_bold)
    d.text((ax + 20, ay + 68), "• VM: Direto na Bateria 2S (7.4V a 8.4V)\n• VCC: 5.0V do Step-Down Mini 560\n• Saída A: 2x Motores JGA-050 Esquerdos\n• Saída B: 2x Motores JGA-050 Direitos", fill=(51, 65, 85), font=font_small)

    # 2. Servos Pan / Tilt
    d.rectangle([(ax + 10, ay + 160), (ax + aw - 10, ay + 250)], fill=(254, 243, 199), outline=(217, 119, 6), width=1)
    d.text((ax + 20, ay + 168), "2x Micro Servos SG90 (Pan & Tilt)", fill=(180, 83, 9), font=font_bold)
    d.text((ax + 20, ay + 188), "• VCC Servos: Ligados no 5V Step-Down (5A)\n• NUNCA alimentar servos no pino 5V do Nano!\n• Sinais nos pinos D9 e D10", fill=(51, 65, 85), font=font_small)

    # 3. LEDs e Buzzer
    d.rectangle([(ax + 10, ay + 260), (ax + aw - 10, ay + 350)], fill=(243, 232, 255), outline=(147, 51, 234), width=1)
    d.text((ax + 20, ay + 268), "Iluminação & Áudio", fill=(126, 34, 206), font=font_bold)
    d.text((ax + 20, ay + 288), "• Barra 8 LEDs WS2812B (Pino D11)\n• Buzzer Passivo 5V (Pino D12)\n• Farol dianteiro, setas e alerta sonoro", fill=(51, 65, 85), font=font_small)

    # 4. Step-Down & Bateria
    d.rectangle([(ax + 10, ay + 360), (ax + aw - 10, ay + 530)], fill=(254, 242, 242), outline=(220, 38, 38), width=2)
    d.text((ax + 20, ay + 368), "ALIMENTAÇÃO CENTRAL (2S 7.4V)", fill=(220, 38, 38), font=font_bold)
    d.text((ax + 20, ay + 388), (
        "• Bateria Li-Ion 2S 7.4V 2500mAh c/ BMS\n"
        "• Chave Geral Liga/Desliga KCD1 no polo (+)\n"
        "• Regulador Step-Down Mini 560 (5V / 5A):\n"
        "   - Alimenta ESP32, Nano e 2 Servos\n"
        "• Divisor Resistivo Bateria -> Nano A0:\n"
        "   - R1 = 10k, R2 = 4.7k (8.4V vira 2.68V)"
    ), fill=(51, 65, 85), font=font_small)

    caminho = "/home/usuario/Documentos/rover/imagens_importantes/esquema_eletrico_chicote_esp32_nano.png"
    img.save(caminho)
    print(f"Salvo: {caminho}")

draw_jga050()
draw_sg90()
draw_electric_schematic()
