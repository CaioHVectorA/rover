#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera ilustração física intuitiva dos pinos do ESP32 e do Arduino Nano (visão superior de bancada).
Arquivos salvos em imagens_importantes/
- mapa_fisico_pinos_esp32.png
- mapa_fisico_pinos_nano.png
"""

from PIL import Image, ImageDraw, ImageFont

font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
font_sec = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 16)
font_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 14)
font_pin = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 13)
font_desc = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 11)
font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", 11)

def draw_esp32_physical():
    w, h = 1200, 850
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([(0, 0), (w, 60)], fill=(15, 23, 42))
    d.text((30, 16), "MAPA FÍSICO DE PINOS - ESP32 (DISPOSIÇÃO REAL DOS HEADERS NA PLACA)", fill=(255, 255, 255), font=font_title)
    d.rectangle([(0, 60), (w, 85)], fill=(30, 41, 59))
    d.text((30, 64), "Visão superior de bancada | Todos os 16 pinos físicos mapeados de forma direta e sem restrições de software", fill=(226, 232, 240), font=font_desc)

    # Centro: Desenho da Placa ESP32
    bx, by = 420, 120
    bw, bh = 360, 680

    # PCB Board
    d.rectangle([(bx, by), (bx + bw, by + bh)], fill=(30, 41, 59), outline=(15, 23, 42), width=3)

    # Antena PCB no topo
    d.rectangle([(bx + 30, by + 15), (bx + bw - 30, by + 75)], fill=(202, 138, 4), outline=(161, 98, 7), width=2)
    d.text((bx + 105, by + 35), "ANTENA WI-FI / BT", fill=(255, 255, 255), font=font_bold)

    # Conector FPC da Câmera (central)
    d.rectangle([(bx + 80, by + 100), (bx + bw - 80, by + 220)], fill=(241, 245, 249), outline=(100, 116, 139), width=2)
    # Lente / Módulo
    d.ellipse([(bx + bw//2 - 40, by + 120), (bx + bw//2 + 40, by + 200)], fill=(15, 23, 42), outline=(220, 38, 38), width=3)
    d.ellipse([(bx + bw//2 - 20, by + 140), (bx + bw//2 + 20, by + 180)], fill=(30, 41, 59))
    d.text((bx + 115, by + 103), "SOQUETE CÂMERA", fill=(100, 116, 139), font=font_desc)

    # Slot MicroSD (abaixo da câmera)
    d.rectangle([(bx + 70, by + 250), (bx + bw - 70, by + 410)], fill=(203, 213, 225), outline=(71, 85, 105), width=2)
    d.text((bx + 110, by + 320), "SLOT MICRO-SD", fill=(51, 65, 85), font=font_bold)

    # Blindagem Metálica / Chip ESP32
    d.rectangle([(bx + 60, by + 440), (bx + bw - 60, by + 610)], fill=(148, 163, 184), outline=(71, 85, 105), width=2)
    d.text((bx + 90, by + 500), "MÓDULO ESP32\n(CPU Dual-Core + RAM)", fill=(15, 23, 42), font=font_bold)

    # Botão Reset
    d.rectangle([(bx + 40, by + 630), (bx + 100, by + 660)], fill=(220, 38, 38))
    d.text((bx + 45, by + 638), "RESET", fill=(255, 255, 255), font=font_desc)

    # Flash LED
    d.rectangle([(bx + bw - 100, by + 630), (bx + bw - 40, by + 660)], fill=(254, 240, 138), outline=(202, 138, 4), width=1)
    d.text((bx + bw - 95, by + 638), "FLASH", fill=(133, 77, 14), font=font_desc)

    # =========================================================================
    # HEADERS FÍSICOS (PINOS NA PLACA)
    # =========================================================================
    # Header Esquerdo (8 pinos)
    pins_left = [
        ("P1", "5V", "Entrada Alimentação 5.0V", (220, 38, 38), (254, 242, 242)),
        ("P2", "GND", "Terra / Referência Comum", (15, 23, 42), (241, 245, 249)),
        ("P3", "IO12", "GPIO 12 (Digital / Touch)", (37, 99, 235), (239, 246, 255)),
        ("P4", "IO13", "GPIO 13 (Digital / Touch)", (37, 99, 235), (239, 246, 255)),
        ("P5", "IO15", "GPIO 15 (Digital / Touch)", (37, 99, 235), (239, 246, 255)),
        ("P6", "IO14", "GPIO 14 (Digital / Touch)", (37, 99, 235), (239, 246, 255)),
        ("P7", "IO2", "GPIO 2 (Digital / LED onboard)", (37, 99, 235), (239, 246, 255)),
        ("P8", "IO4", "GPIO 4 (Digital / LED Flash)", (37, 99, 235), (239, 246, 255))
    ]

    # Header Direito (8 pinos)
    pins_right = [
        ("P9", "3V3", "Saída 3.3V (Não ligar motor/servo)", (217, 119, 6), (254, 249, 195)),
        ("P10", "GND", "Terra / Referência Comum", (15, 23, 42), (241, 245, 249)),
        ("P11", "IO16", "GPIO 16 (Livre / PSRAM / I/O)", (37, 99, 235), (239, 246, 255)),
        ("P12", "IO0", "GPIO 0 (Pino de Boot / Gravação)", (180, 83, 9), (254, 243, 199)),
        ("P13", "U0R", "GPIO 3 (UART0 RX - Recepção Serial)", (22, 101, 52), (240, 253, 244)),
        ("P14", "U0T", "GPIO 1 (UART0 TX - Transmissão Serial)", (22, 101, 52), (240, 253, 244)),
        ("P15", "GND", "Terra / Referência Comum", (15, 23, 42), (241, 245, 249)),
        ("P16", "VCC", "5V ou 3.3V (Alimentação Auxiliar)", (220, 38, 38), (254, 242, 242))
    ]

    start_y = by + 70
    step_y = 65

    # Desenho Pinos da Esquerda
    for i, (num, name, desc, border_col, bg_col) in enumerate(pins_left):
        py = start_y + (i * step_y)
        # Terminal metálico no PCB
        d.rectangle([(bx - 12, py + 12), (bx + 12, py + 36)], fill=(203, 213, 225), outline=(15, 23, 42), width=1)
        d.ellipse([(bx - 6, py + 18), (bx + 6, py + 30)], fill=(255, 255, 255), outline=(15, 23, 42))

        # Linha conectora
        d.line([(bx - 12, py + 24), (bx - 50, py + 24)], fill=(100, 116, 139), width=2)

        # Caixa do Pino
        d.rectangle([(40, py), (bx - 50, py + 48)], fill=bg_col, outline=border_col, width=2)
        # Tag do Pino
        d.rectangle([(40, py), (85, py + 48)], fill=border_col)
        d.text((48, py + 14), num, fill=(255, 255, 255), font=font_bold)
        # Nome do Pino (Silk)
        d.text((95, py + 6), name, fill=border_col, font=font_sec)
        # Descrição
        d.text((95, py + 28), desc, fill=(71, 85, 105), font=font_small)

    # Desenho Pinos da Direita
    for i, (num, name, desc, border_col, bg_col) in enumerate(pins_right):
        py = start_y + (i * step_y)
        rx = bx + bw
        # Terminal metálico no PCB
        d.rectangle([(rx - 12, py + 12), (rx + 12, py + 36)], fill=(203, 213, 225), outline=(15, 23, 42), width=1)
        d.ellipse([(rx - 6, py + 18), (rx + 6, py + 30)], fill=(255, 255, 255), outline=(15, 23, 42))

        # Linha conectora
        d.line([(rx + 12, py + 24), (rx + 50, py + 24)], fill=(100, 116, 139), width=2)

        # Caixa do Pino
        d.rectangle([(rx + 50, py), (w - 40, py + 48)], fill=bg_col, outline=border_col, width=2)
        # Tag do Pino
        d.rectangle([(w - 85, py), (w - 40, py + 48)], fill=border_col)
        d.text((w - 77, py + 14), num, fill=(255, 255, 255), font=font_bold)
        # Nome do Pino (Silk)
        d.text((rx + 60, py + 6), name, fill=border_col, font=font_sec)
        # Descrição
        d.text((rx + 60, py + 28), desc, fill=(71, 85, 105), font=font_small)

    # Rodapé de Legenda
    d.rectangle([(40, 770), (w - 40, 825)], fill=(248, 250, 252), outline=(203, 213, 225), width=1)
    legenda = (
        "LEGENDA:  [Vermelho] = Alimentação (5V / VCC)  |  [Preto] = Terra (GND)  |  "
        "[Azul] = GPIOs Digitais  |  [Verde] = Comunicação Serial (TX / RX)  |  [Amarelo] = 3.3V / Boot"
    )
    d.text((60, 790), legenda, fill=(15, 23, 42), font=font_bold)

    path = "/home/usuario/Documentos/rover/imagens_importantes/mapa_fisico_pinos_esp32.png"
    img.save(path)
    print(f"Salvo: {path}")

def draw_nano_physical():
    w, h = 1200, 950
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([(0, 0), (w, 60)], fill=(15, 23, 42))
    d.text((30, 16), "MAPA FÍSICO DE PINOS - ARDUINO NANO V3 (DISPOSIÇÃO REAL DOS HEADERS)", fill=(255, 255, 255), font=font_title)
    d.rectangle([(0, 60), (w, 85)], fill=(30, 41, 59))
    d.text((30, 64), "Visão superior de bancada | 30 pinos físicos (15 à esquerda e 15 à direita) para controle total do chassi", fill=(226, 232, 240), font=font_desc)

    # Placa Arduino Nano central
    bx, by = 430, 110
    bw, bh = 340, 800

    # PCB Azul clássico do Arduino Nano
    d.rectangle([(bx, by), (bx + bw, by + bh)], fill=(30, 64, 175), outline=(15, 23, 42), width=3)

    # Conector USB Mini no topo
    d.rectangle([(bx + 90, by + 10), (bx + bw - 90, by + 70)], fill=(203, 213, 225), outline=(100, 116, 139), width=2)
    d.text((bx + 115, by + 32), "CONECTOR USB", fill=(15, 23, 42), font=font_bold)

    # Chip ATmega328P central (girado 45 deg ou quadrado)
    d.rectangle([(bx + 85, by + 320), (bx + bw - 85, by + 500)], fill=(15, 23, 42), outline=(148, 163, 184), width=2)
    d.text((bx + 115, by + 390), "ATmega328P\n(Microcontrolador)", fill=(255, 255, 255), font=font_bold)

    # Botão de Reset
    d.rectangle([(bx + 130, by + 150), (bx + bw - 130, by + 190)], fill=(220, 38, 38))
    d.text((bx + 140, by + 162), "RESET", fill=(255, 255, 255), font=font_desc)

    # Cristais e LEDs onboard
    d.rectangle([(bx + 120, by + 230), (bx + bw - 120, by + 260)], fill=(241, 245, 249))
    d.text((bx + 135, by + 238), "16 MHz Cristal", fill=(15, 23, 42), font=font_desc)

    # 15 Pinos Esquerda
    pins_left_nano = [
        ("D1", "TX1", "Pino D1 / UART TX (5V)", (22, 101, 52), (240, 253, 244)),
        ("D0", "RX0", "Pino D0 / UART RX (5V)", (22, 101, 52), (240, 253, 244)),
        ("RST", "RESET", "Linha de Reset do chip", (185, 28, 28), (254, 242, 242)),
        ("GND", "GND", "Terra Comum", (15, 23, 42), (241, 245, 249)),
        ("D2", "D2", "Digital / Interrupção INT0", (37, 99, 235), (239, 246, 255)),
        ("D3", "D3 (PWM)", "Digital / PWM Timer 2 (PWMA)", (147, 51, 234), (245, 243, 255)),
        ("D4", "D4", "Digital Output (AIN1)", (37, 99, 235), (239, 246, 255)),
        ("D5", "D5 (PWM)", "Digital / PWM Timer 0 (AIN2)", (147, 51, 234), (245, 243, 255)),
        ("D6", "D6 (PWM)", "Digital / PWM Timer 0 (PWMB)", (147, 51, 234), (245, 243, 255)),
        ("D7", "D7", "Digital Output (BIN1)", (37, 99, 235), (239, 246, 255)),
        ("D8", "D8", "Digital Output (BIN2)", (37, 99, 235), (239, 246, 255)),
        ("D9", "D9 (PWM)", "Digital / PWM Timer 1 (Servo Pan)", (217, 119, 6), (254, 249, 195)),
        ("D10", "D10 (PWM)", "Digital / PWM Timer 1 (Servo Tilt)", (217, 119, 6), (254, 249, 195)),
        ("D11", "D11 (MOSI)", "Digital / PWM (DIN LEDs WS2812B)", (147, 51, 234), (245, 243, 255)),
        ("D12", "D12 (MISO)", "Digital Output (Buzzer 5V)", (37, 99, 235), (239, 246, 255))
    ]

    # 15 Pinos Direita
    pins_right_nano = [
        ("VIN", "VIN", "Entrada 7-12V (NÃO USAR)", (100, 116, 139), (241, 245, 249)),
        ("GND", "GND", "Terra Comum", (15, 23, 42), (241, 245, 249)),
        ("RST", "RESET", "Linha de Reset do chip", (185, 28, 28), (254, 242, 242)),
        ("5V", "+5V", "Entrada 5.0V (Do Step-Down)", (220, 38, 38), (254, 242, 242)),
        ("A7", "A7", "Analógico (Somente ADC)", (217, 119, 6), (254, 249, 195)),
        ("A6", "A6", "Analógico (Somente ADC)", (217, 119, 6), (254, 249, 195)),
        ("A5", "A5 (SCL)", "Analógico / I2C Clock", (217, 119, 6), (254, 249, 195)),
        ("A4", "A4 (SDA)", "Analógico / I2C Dados", (217, 119, 6), (254, 249, 195)),
        ("A3", "A3", "Analógico / Digital Livre", (217, 119, 6), (254, 249, 195)),
        ("A2", "A2", "Analógico / Digital Livre", (217, 119, 6), (254, 249, 195)),
        ("A1", "A1", "Analógico / Digital Livre", (217, 119, 6), (254, 249, 195)),
        ("A0", "A0", "Analógico (Divisor Bateria 7.4V)", (220, 38, 38), (254, 242, 242)),
        ("REF", "AREF", "Referência Analógica Externa", (100, 116, 139), (241, 245, 249)),
        ("3V3", "3V3", "Saída 3.3V do chip FTDI", (217, 119, 6), (254, 249, 195)),
        ("D13", "D13 (SCK)", "Digital / LED Onboard Heartbeat", (37, 99, 235), (239, 246, 255))
    ]

    start_y = by + 30
    step_y = 50

    # Lado Esquerdo
    for i, (num, name, desc, border_col, bg_col) in enumerate(pins_left_nano):
        py = start_y + (i * step_y)
        # Terminal no PCB
        d.rectangle([(bx - 10, py + 8), (bx + 10, py + 28)], fill=(203, 213, 225), outline=(15, 23, 42), width=1)
        d.ellipse([(bx - 5, py + 13), (bx + 5, py + 23)], fill=(255, 255, 255), outline=(15, 23, 42))

        d.line([(bx - 10, py + 18), (bx - 45, py + 18)], fill=(100, 116, 139), width=2)
        d.rectangle([(30, py), (bx - 45, py + 36)], fill=bg_col, outline=border_col, width=2)
        d.rectangle([(30, py), (80, py + 36)], fill=border_col)
        d.text((38, py + 10), num, fill=(255, 255, 255), font=font_desc)
        d.text((90, py + 3), name, fill=border_col, font=font_bold)
        d.text((90, py + 20), desc, fill=(71, 85, 105), font=font_small)

    # Lado Direito
    for i, (num, name, desc, border_col, bg_col) in enumerate(pins_right_nano):
        py = start_y + (i * step_y)
        rx = bx + bw
        d.rectangle([(rx - 10, py + 8), (rx + 10, py + 28)], fill=(203, 213, 225), outline=(15, 23, 42), width=1)
        d.ellipse([(rx - 5, py + 13), (rx + 5, py + 23)], fill=(255, 255, 255), outline=(15, 23, 42))

        d.line([(rx + 10, py + 18), (rx + 45, py + 18)], fill=(100, 116, 139), width=2)
        d.rectangle([(rx + 45, py), (w - 30, py + 36)], fill=bg_col, outline=border_col, width=2)
        d.rectangle([(w - 80, py), (w - 30, py + 36)], fill=border_col)
        d.text((w - 72, py + 10), num, fill=(255, 255, 255), font=font_desc)
        d.text((rx + 55, py + 3), name, fill=border_col, font=font_bold)
        d.text((rx + 55, py + 20), desc, fill=(71, 85, 105), font=font_small)

    path = "/home/usuario/Documentos/rover/imagens_importantes/mapa_fisico_pinos_nano.png"
    img.save(path)
    print(f"Salvo: {path}")

draw_esp32_physical()
draw_nano_physical()
