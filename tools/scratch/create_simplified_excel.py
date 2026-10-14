#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a planilha simplificada e interativa de pinagem: tabela_pinagem_esp32_nano.xlsx
Foco: Layout físico visual (visão de bancada), simples, direto e 100% editável pelo usuário.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
wb.remove(wb.active)  # remove sheet padrão

# Cores Modernas e Limpas
C_NAVY = "1E293B"      # Slate 800
C_HEADER = "334155"    # Slate 700
C_CHIP_BG = "0F172A"   # Slate 900
C_CHIP_TEXT = "F8FAFC"
C_BORDER = "CBD5E1"    # Slate 300
C_ZEBRA = "F8FAFC"
C_WHITE = "FFFFFF"

# Cores de Pinos
FILL_PWR = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")     # Vermelho claro (5V/VCC)
FONT_PWR = Font(name="Calibri", size=10, bold=True, color="991B1B")

FILL_GND = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")     # Cinza claro (GND)
FONT_GND = Font(name="Calibri", size=10, bold=True, color="0F172A")

FILL_GPIO = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")    # Azul claro (GPIO)
FONT_GPIO = Font(name="Calibri", size=10, bold=True, color="1E40AF")

FILL_UART = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")    # Verde claro (UART)
FONT_UART = Font(name="Calibri", size=10, bold=True, color="166534")

FILL_PWM = PatternFill(start_color="F3E8FF", end_color="F3E8FF", fill_type="solid")     # Roxo claro (PWM)
FONT_PWM = Font(name="Calibri", size=10, bold=True, color="6B21A8")

FILL_ADC = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")     # Amarelo claro (ADC)
FONT_ADC = Font(name="Calibri", size=10, bold=True, color="854D0E")

# Estilo para células editáveis do usuário (fundo branco com borda suave)
FILL_USER_EDIT = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
FONT_USER_EDIT = Font(name="Calibri", size=10, bold=True, color="0F172A")

border_thin = Border(
    left=Side(style='thin', color=C_BORDER),
    right=Side(style='thin', color=C_BORDER),
    top=Side(style='thin', color=C_BORDER),
    bottom=Side(style='thin', color=C_BORDER)
)

border_chip = Border(
    left=Side(style='medium', color="0F172A"),
    right=Side(style='medium', color="0F172A"),
    top=Side(style='medium', color="0F172A"),
    bottom=Side(style='medium', color="0F172A")
)

def style_header(ws, row, headers, fill_color=C_HEADER):
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=h)
        cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_thin
    ws.row_dimensions[row].height = 26

def auto_width(ws, padding=4):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_l = 0
        for cell in col:
            if cell.row in [1, 2]: continue
            if cell.value:
                for line in str(cell.value).split('\n'):
                    max_l = max(max_l, len(line))
        ws.column_dimensions[col_letter].width = max(max_l + padding, 12)


# ==============================================================================
# ABA 1: ESP32 - MAPA FÍSICO E TABELA EDITÁVEL
# ==============================================================================
ws1 = wb.create_sheet(title="ESP32_Mapa_Fisico")
ws1.views.sheetView[0].showGridLines = True

# Título
ws1.merge_cells("A1:G1")
t1 = ws1.cell(row=1, column=1, value="ESP32 - MAPA FÍSICO DE PINOS (VISÃO DE BANCADA)")
t1.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
t1.fill = PatternFill(start_color=C_NAVY, end_color=C_NAVY, fill_type="solid")
t1.alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[1].height = 32

ws1.merge_cells("A2:G2")
sub1 = ws1.cell(row=2, column=1, value="Disposição física idêntica à placa real. Edite a coluna 'Minha Conexão' livremente.")
sub1.font = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
sub1.fill = PatternFill(start_color=C_HEADER, end_color=C_HEADER, fill_type="solid")
sub1.alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[2].height = 20

# -------------------------------------------------------------
# 1. ILUSTRAÇÃO FÍSICA (VISÃO SUPERIOR)
# -------------------------------------------------------------
ws1.merge_cells("A4:G4")
sec1 = ws1.cell(row=4, column=1, value="1. DISPOSIÇÃO FÍSICA DOS PINOS NA PLACA (VISÃO SUPERIOR)")
sec1.font = Font(name="Calibri", size=11, bold=True, color="1E40AF")
sec1.alignment = Alignment(horizontal="left", vertical="center")
ws1.row_dimensions[4].height = 22

# Cabeçalhos da Ilustração Física
headers_vis_esp = [
    "Pino #", "Silk (Esq)", "Minha Conexão (Esq)",
    "CORPO DA PLACA ESP32",
    "Minha Conexão (Dir)", "Silk (Dir)", "Pino #"
]
style_header(ws1, 5, headers_vis_esp, fill_color="475569")

# 8 Pinos na Esquerda e 8 Pinos na Direita
pinos_esq_esp = [
    ("P01", "5V", "Entrada 5.0V (Step-Down 5A)", FILL_PWR, FONT_PWR),
    ("P02", "GND", "GND Comum do Robô", FILL_GND, FONT_GND),
    ("P03", "IO12", "", FILL_GPIO, FONT_GPIO),
    ("P04", "IO13", "", FILL_GPIO, FONT_GPIO),
    ("P05", "IO15", "", FILL_GPIO, FONT_GPIO),
    ("P06", "IO14", "", FILL_GPIO, FONT_GPIO),
    ("P07", "IO2", "", FILL_GPIO, FONT_GPIO),
    ("P08", "IO4", "", FILL_GPIO, FONT_GPIO)
]

pinos_dir_esp = [
    ("P09", "3V3", "", FILL_PWR, FONT_PWR),
    ("P10", "GND", "GND Comum", FILL_GND, FONT_GND),
    ("P11", "IO16", "", FILL_GPIO, FONT_GPIO),
    ("P12", "IO0", "Boot / Livre", FILL_ADC, FONT_ADC),
    ("P13", "U0R", "RX0 <- TX Nano (com divisor)", FILL_UART, FONT_UART),
    ("P14", "U0T", "TX0 -> RX Nano (Comandos)", FILL_UART, FONT_UART),
    ("P15", "GND", "GND Comum", FILL_GND, FONT_GND),
    ("P16", "VCC", "", FILL_PWR, FONT_PWR)
]

corpo_esp_labels = [
    "▲ ANTENA WI-FI / BLUETOOTH ▲",
    "╔═════════════════════════╗",
    "║       CHIP ESP32        ║",
    "║    (Dual-Core + RAM)    ║",
    "║                         ║",
    "║      SOQUETE CÂMERA     ║",
    "╚═════════════════════════╝",
    "▼      BOTÃO RESET        ▼"
]

for idx in range(8):
    r = 6 + idx
    ws1.row_dimensions[r].height = 24
    pe_num, pe_silk, pe_conn, pe_fill, pe_font = pinos_esq_esp[idx]
    pd_num, pd_silk, pd_conn, pd_fill, pd_font = pinos_dir_esp[idx]

    # Lado Esquerdo
    c1 = ws1.cell(row=r, column=1, value=pe_num)
    c1.alignment = Alignment(horizontal="center", vertical="center")
    c1.border = border_thin
    c1.fill = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid")
    c1.font = Font(name="Calibri", size=10, bold=True)

    c2 = ws1.cell(row=r, column=2, value=pe_silk)
    c2.alignment = Alignment(horizontal="center", vertical="center")
    c2.border = border_thin
    c2.fill = pe_fill
    c2.font = pe_font

    c3 = ws1.cell(row=r, column=3, value=pe_conn)
    c3.alignment = Alignment(horizontal="left", vertical="center")
    c3.border = border_thin
    c3.fill = FILL_USER_EDIT
    c3.font = FONT_USER_EDIT

    # Centro: Corpo ESP32
    c4 = ws1.cell(row=r, column=4, value=corpo_esp_labels[idx])
    c4.alignment = Alignment(horizontal="center", vertical="center")
    c4.border = border_chip
    c4.fill = PatternFill(start_color=C_CHIP_BG, end_color=C_CHIP_BG, fill_type="solid")
    c4.font = Font(name="Calibri", size=10, bold=True, color=C_CHIP_TEXT)

    # Lado Direito
    c5 = ws1.cell(row=r, column=5, value=pd_conn)
    c5.alignment = Alignment(horizontal="left", vertical="center")
    c5.border = border_thin
    c5.fill = FILL_USER_EDIT
    c5.font = FONT_USER_EDIT

    c6 = ws1.cell(row=r, column=6, value=pd_silk)
    c6.alignment = Alignment(horizontal="center", vertical="center")
    c6.border = border_thin
    c6.fill = pd_fill
    c6.font = pd_font

    c7 = ws1.cell(row=r, column=7, value=pd_num)
    c7.alignment = Alignment(horizontal="center", vertical="center")
    c7.border = border_thin
    c7.fill = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid")
    c7.font = Font(name="Calibri", size=10, bold=True)

# -------------------------------------------------------------
# 2. TABELA COMPLETA E EDITÁVEL DE TODOS OS PINOS
# -------------------------------------------------------------
r_tab_esp = 16
ws1.merge_cells(f"A{r_tab_esp}:G{r_tab_esp}")
sec2 = ws1.cell(row=r_tab_esp, column=1, value="2. TABELA COMPLETA DE TODOS OS PINOS (EDITÁVEL)")
sec2.font = Font(name="Calibri", size=11, bold=True, color="1E40AF")
sec2.alignment = Alignment(horizontal="left", vertical="center")
ws1.row_dimensions[r_tab_esp].height = 24

headers_flat_esp = [
    "Pino #", "Posição", "Nome no Silk", "Tipo de Pino",
    "Nível Lógico", "Minha Conexão (Editar Aqui)", "Minhas Anotações"
]
style_header(ws1, r_tab_esp + 1, headers_flat_esp, fill_color=C_HEADER)

tabela_completa_esp = [
    ("P01", "Header Esquerdo", "5V", "Alimentação", "5.0V", "Entrada 5.0V (Step-Down 5A)", "Alimenta o regulador interno 3.3V do ESP32"),
    ("P02", "Header Esquerdo", "GND", "Terra", "0V", "GND Comum do Robô", "Conectar ao terra comum de todo o sistema"),
    ("P03", "Header Esquerdo", "IO12", "GPIO Digital", "3.3V", "", "Pino digital de I/O"),
    ("P04", "Header Esquerdo", "IO13", "GPIO Digital", "3.3V", "", "Pino digital de I/O"),
    ("P05", "Header Esquerdo", "IO15", "GPIO Digital", "3.3V", "", "Pino digital de I/O"),
    ("P06", "Header Esquerdo", "IO14", "GPIO Digital", "3.3V", "", "Pino digital de I/O"),
    ("P07", "Header Esquerdo", "IO2", "GPIO Digital", "3.3V", "", "Pino ligado também ao LED onboard pequeno"),
    ("P08", "Header Esquerdo", "IO4", "GPIO Digital", "3.3V", "", "Pino de I/O (aciona LED Flash de fábrica)"),
    ("P09", "Header Direito", "3V3", "Saída Auxiliar", "3.3V", "", "Saída de 3.3V (apenas sinais, não ligar motores)"),
    ("P10", "Header Direito", "GND", "Terra", "0V", "GND Comum", "Terra de referência"),
    ("P11", "Header Direito", "IO16", "GPIO Digital", "3.3V", "", "Pino de I/O livre"),
    ("P12", "Header Direito", "IO0", "GPIO / Boot", "3.3V", "Boot / Livre", "Ligue a GND apenas durante gravação de código"),
    ("P13", "Header Direito", "U0R", "Serial UART0 RX", "3.3V", "RX0 <- TX Nano", "Recepção Serial. Usar divisor se o Nano enviar 5V"),
    ("P14", "Header Direito", "U0T", "Serial UART0 TX", "3.3V", "TX0 -> RX Nano", "Transmissão Serial de comandos para o Nano (D0)"),
    ("P15", "Header Direito", "GND", "Terra", "0V", "GND Comum", "Terra de referência"),
    ("P16", "Header Direito", "VCC", "Alimentação", "5V / 3.3V", "", "Pino de alimentação auxiliar da placa")
]

for idx, row_d in enumerate(tabela_completa_esp, r_tab_esp + 2):
    ws1.row_dimensions[idx].height = 22
    bg = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=C_WHITE, end_color=C_WHITE, fill_type="solid")
    
    for c_idx, val in enumerate(row_d, 1):
        cell = ws1.cell(row=idx, column=c_idx, value=val)
        cell.border = border_thin
        if c_idx == 6: # Campo de edição do usuário
            cell.fill = FILL_USER_EDIT
            cell.font = FONT_USER_EDIT
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_idx in [1, 2, 3, 4, 5]:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10, bold=(c_idx==3))
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")

auto_width(ws1)


# ==============================================================================
# ABA 2: ARDUINO NANO - MAPA FÍSICO E TABELA EDITÁVEL
# ==============================================================================
ws2 = wb.create_sheet(title="Nano_Mapa_Fisico")
ws2.views.sheetView[0].showGridLines = True

# Título
ws2.merge_cells("A1:G1")
t2 = ws2.cell(row=1, column=1, value="ARDUINO NANO V3 - MAPA FÍSICO DE PINOS (VISÃO DE BANCADA)")
t2.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
t2.fill = PatternFill(start_color=C_NAVY, end_color=C_NAVY, fill_type="solid")
t2.alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 32

ws2.merge_cells("A2:G2")
sub2 = ws2.cell(row=2, column=1, value="30 pinos físicos (15 à esquerda e 15 à direita). Co-processador fixo no chassi do robô.")
sub2.font = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
sub2.fill = PatternFill(start_color=C_HEADER, end_color=C_HEADER, fill_type="solid")
sub2.alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[2].height = 20

# 1. ILUSTRAÇÃO FÍSICA DO NANO
ws2.merge_cells("A4:G4")
sec_n1 = ws2.cell(row=4, column=1, value="1. DISPOSIÇÃO FÍSICA DOS PINOS NA PLACA NANO (VISÃO SUPERIOR)")
sec_n1.font = Font(name="Calibri", size=11, bold=True, color="1E40AF")
sec_n1.alignment = Alignment(horizontal="left", vertical="center")
ws2.row_dimensions[4].height = 22

headers_vis_nano = [
    "Pino #", "Silk (Esq)", "Minha Conexão (Esq)",
    "CORPO DO ARDUINO NANO",
    "Minha Conexão (Dir)", "Silk (Dir)", "Pino #"
]
style_header(ws2, 5, headers_vis_nano, fill_color="475569")

pinos_esq_nano = [
    ("N01", "TX1", "Telemetria -> ESP32 RX (via divisor)", FILL_UART, FONT_UART),
    ("N02", "RX0", "Comandos <- ESP32 TX", FILL_UART, FONT_UART),
    ("N03", "RST", "", FILL_PWR, FONT_PWR),
    ("N04", "GND", "GND Comum do Robô", FILL_GND, FONT_GND),
    ("N05", "D2", "Livre / Sensor", FILL_GPIO, FONT_GPIO),
    ("N06", "D3", "TB6612 -> PWMA (Velocidade Esq)", FILL_PWM, FONT_PWM),
    ("N07", "D4", "TB6612 -> AIN1 (Direção Esq)", FILL_GPIO, FONT_GPIO),
    ("N08", "D5", "TB6612 -> AIN2 (Direção Esq)", FILL_PWM, FONT_PWM),
    ("N09", "D6", "TB6612 -> PWMB (Velocidade Dir)", FILL_PWM, FONT_PWM),
    ("N10", "D7", "TB6612 -> BIN1 (Direção Dir)", FILL_GPIO, FONT_GPIO),
    ("N11", "D8", "TB6612 -> BIN2 (Direção Dir)", FILL_GPIO, FONT_GPIO),
    ("N12", "D9", "Servo Pan (Giro Câmera)", FILL_PWM, FONT_PWM),
    ("N13", "D10", "Servo Tilt (Inclinação Câmera)", FILL_PWM, FONT_PWM),
    ("N14", "D11", "Fita 8 LEDs WS2812B (DIN)", FILL_PWM, FONT_PWM),
    ("N15", "D12", "Buzzer Passivo 5V", FILL_GPIO, FONT_GPIO)
]

pinos_dir_nano = [
    ("N30", "VIN", "Desconectado (NÃO USAR)", FILL_GND, FONT_GND),
    ("N29", "GND", "GND Comum", FILL_GND, FONT_GND),
    ("N28", "RST", "", FILL_PWR, FONT_PWR),
    ("N27", "5V", "Entrada 5.0V (Do Step-Down)", FILL_PWR, FONT_PWR),
    ("N26", "A7", "Livre / Analógico", FILL_ADC, FONT_ADC),
    ("N25", "A6", "Livre / Analógico", FILL_ADC, FONT_ADC),
    ("N24", "A5", "Livre / I2C SCL", FILL_ADC, FONT_ADC),
    ("N23", "A4", "Livre / I2C SDA", FILL_ADC, FONT_ADC),
    ("N22", "A3", "Livre / Analógico", FILL_ADC, FONT_ADC),
    ("N21", "A2", "Livre / Analógico", FILL_ADC, FONT_ADC),
    ("N20", "A1", "Livre / Analógico", FILL_ADC, FONT_ADC),
    ("N19", "A0", "Leitura Bateria 7.4V (Divisor)", FILL_PWR, FONT_PWR),
    ("N18", "REF", "", FILL_GND, FONT_GND),
    ("N17", "3V3", "", FILL_PWR, FONT_PWR),
    ("N16", "D13", "LED Onboard (Heartbeat)", FILL_GPIO, FONT_GPIO)
]

corpo_nano_labels = [
    "▲ CONECTOR MINI-USB ▲",
    "║                       ║",
    "║     BOTÃO RESET       ║",
    "║                       ║",
    "║     CRISTAL 16MHz     ║",
    "║                       ║",
    "║      ATmega328P       ║",
    "║   (Microcontrolador)  ║",
    "║                       ║",
    "║       LEDs PWR/RX/TX  ║",
    "║                       ║",
    "║                       ║",
    "║                       ║",
    "║                       ║",
    "▼   FIM DA PLACA NANO   ▼"
]

for idx in range(15):
    r = 6 + idx
    ws2.row_dimensions[r].height = 22
    pe_num, pe_silk, pe_conn, pe_fill, pe_font = pinos_esq_nano[idx]
    pd_num, pd_silk, pd_conn, pd_fill, pd_font = pinos_dir_nano[idx]

    # Esquerda
    c1 = ws2.cell(row=r, column=1, value=pe_num)
    c1.alignment = Alignment(horizontal="center", vertical="center")
    c1.border = border_thin
    c1.fill = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid")
    c1.font = Font(name="Calibri", size=9, bold=True)

    c2 = ws2.cell(row=r, column=2, value=pe_silk)
    c2.alignment = Alignment(horizontal="center", vertical="center")
    c2.border = border_thin
    c2.fill = pe_fill
    c2.font = pe_font

    c3 = ws2.cell(row=r, column=3, value=pe_conn)
    c3.alignment = Alignment(horizontal="left", vertical="center")
    c3.border = border_thin
    c3.fill = FILL_USER_EDIT
    c3.font = FONT_USER_EDIT

    # Centro: Placa Nano
    c4 = ws2.cell(row=r, column=4, value=corpo_nano_labels[idx])
    c4.alignment = Alignment(horizontal="center", vertical="center")
    c4.border = border_chip
    c4.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    c4.font = Font(name="Calibri", size=9, bold=True, color="FFFFFF")

    # Direita
    c5 = ws2.cell(row=r, column=5, value=pd_conn)
    c5.alignment = Alignment(horizontal="left", vertical="center")
    c5.border = border_thin
    c5.fill = FILL_USER_EDIT
    c5.font = FONT_USER_EDIT

    c6 = ws2.cell(row=r, column=6, value=pd_silk)
    c6.alignment = Alignment(horizontal="center", vertical="center")
    c6.border = border_thin
    c6.fill = pd_fill
    c6.font = pd_font

    c7 = ws2.cell(row=r, column=7, value=pd_num)
    c7.alignment = Alignment(horizontal="center", vertical="center")
    c7.border = border_thin
    c7.fill = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid")
    c7.font = Font(name="Calibri", size=9, bold=True)

# 2. TABELA COMPLETA EDITÁVEL NANO
r_tab_nano = 23
ws2.merge_cells(f"A{r_tab_nano}:G{r_tab_nano}")
sec_n2 = ws2.cell(row=r_tab_nano, column=1, value="2. TABELA COMPLETA DE TODOS OS PINOS DO NANO (EDITÁVEL)")
sec_n2.font = Font(name="Calibri", size=11, bold=True, color="1E40AF")
sec_n2.alignment = Alignment(horizontal="left", vertical="center")
ws2.row_dimensions[r_tab_nano].height = 24

headers_flat_nano = [
    "Pino #", "Posição", "Nome no Silk", "Tipo / Recurso",
    "Nível Lógico", "Minha Conexão (Editar Aqui)", "Minhas Anotações"
]
style_header(ws2, r_tab_nano + 1, headers_flat_nano, fill_color=C_HEADER)

tabela_nano_flat = [
    ("N01", "Esquerda", "TX1", "Serial UART TX", "5V", "Telemetria -> ESP32 RX", "Usar divisor 1k/2k para rebaixar 5V para 3.3V"),
    ("N02", "Esquerda", "RX0", "Serial UART RX", "5V", "Comandos <- ESP32 TX", "Recebe 3.3V direto do ESP32 (compatível)"),
    ("N03", "Esquerda", "RST", "Reset", "5V", "", "Reinicia o microcontrolador ATmega328P"),
    ("N04", "Esquerda", "GND", "Terra", "0V", "GND Comum do Robô", "Terra de referência"),
    ("N05", "Esquerda", "D2", "Digital / INT0", "5V", "Livre / Sensor", "Interrupção externa para encoder ou fim de curso"),
    ("N06", "Esquerda", "D3", "Digital / PWM", "5V", "TB6612 -> PWMA", "Velocidade Motores Esquerdos (0 a 255)"),
    ("N07", "Esquerda", "D4", "Digital Output", "5V", "TB6612 -> AIN1", "Sentido Motores Esquerdos"),
    ("N08", "Esquerda", "D5", "Digital / PWM", "5V", "TB6612 -> AIN2", "Sentido Motores Esquerdos"),
    ("N09", "Esquerda", "D6", "Digital / PWM", "5V", "TB6612 -> PWMB", "Velocidade Motores Direitos (0 a 255)"),
    ("N10", "Esquerda", "D7", "Digital Output", "5V", "TB6612 -> BIN1", "Sentido Motores Direitos"),
    ("N11", "Esquerda", "D8", "Digital Output", "5V", "TB6612 -> BIN2", "Sentido Motores Direitos"),
    ("N12", "Esquerda", "D9", "Digital / PWM", "5V", "Servo Pan (Giro)", "Giro horizontal da câmera (0° a 180°)"),
    ("N13", "Esquerda", "D10", "Digital / PWM", "5V", "Servo Tilt (Inclinação)", "Inclinação vertical da câmera (50° a 130°)"),
    ("N14", "Esquerda", "D11", "Digital / SPI MOSI", "5V", "Fita 8 LEDs WS2812B", "Sinal DIN para controle de cor dos LEDs"),
    ("N15", "Esquerda", "D12", "Digital / SPI MISO", "5V", "Buzzer Passivo 5V", "Sinais sonoros via função tone()"),
    ("N16", "Direita", "D13", "Digital / LED", "5V", "LED Onboard (Heartbeat)", "Pisca a cada 500ms indicando funcionamento"),
    ("N17", "Direita", "3V3", "Saída 3.3V", "3.3V", "", "Saída regulada pequena do chip serial"),
    ("N18", "Direita", "REF", "Referência ADC", "5V", "", "Tensão de referência para conversor analógico"),
    ("N19", "Direita", "A0", "Analógico Input", "0-5V", "Leitura Bateria 7.4V", "Divisor R1=10k, R2=4.7k (8.4V max = 2.68V)"),
    ("N20", "Direita", "A1", "Analógico / Digital", "0-5V", "Livre / Analógico", "Sensor de distância ou linha"),
    ("N21", "Direita", "A2", "Analógico / Digital", "0-5V", "Livre / Analógico", "Sensor de distância ou linha"),
    ("N22", "Direita", "A3", "Analógico / Digital", "0-5V", "Livre / Analógico", "Sensor auxiliar"),
    ("N23", "Direita", "A4", "Analógico / I2C SDA", "5V", "Livre / I2C SDA", "Dados para acelerômetro MPU6050 ou Display OLED"),
    ("N24", "Direita", "A5", "Analógico / I2C SCL", "5V", "Livre / I2C SCL", "Clock para acelerômetro MPU6050 ou Display OLED"),
    ("N25", "Direita", "A6", "Analógico Puro", "0-5V", "Livre / Analógico", "Somente leitura analógica"),
    ("N26", "Direita", "A7", "Analógico Puro", "0-5V", "Livre / Analógico", "Somente leitura analógica"),
    ("N27", "Direita", "5V", "Alimentação 5.0V", "5.0V", "Entrada 5.0V Step-Down", "Alimenta o Nano direto pelo barramento 5V"),
    ("N28", "Direita", "RST", "Reset", "5V", "", "Linha de reset"),
    ("N29", "Direita", "GND", "Terra", "0V", "GND Comum", "Terra de referência comum"),
    ("N30", "Direita", "VIN", "Entrada Alta Tensão", "7-12V", "Desconectado (NÃO USAR)", "Evita aquecimento do regulador linear onboard")
]

for idx, row_d in enumerate(tabela_nano_flat, r_tab_nano + 2):
    ws2.row_dimensions[idx].height = 22
    bg = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=C_WHITE, end_color=C_WHITE, fill_type="solid")

    for c_idx, val in enumerate(row_d, 1):
        cell = ws2.cell(row=idx, column=c_idx, value=val)
        cell.border = border_thin
        if c_idx == 6:
            cell.fill = FILL_USER_EDIT
            cell.font = FONT_USER_EDIT
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_idx in [1, 2, 3, 4, 5]:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10, bold=(c_idx==3))
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")

auto_width(ws2)


# ==============================================================================
# ABA 3: RESUMO DE CONEXÕES DO ROVER (SIMPLES E DIRETO)
# ==============================================================================
ws3 = wb.create_sheet(title="Minhas_Conexoes_Rover")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("A1:F1")
t3 = ws3.cell(row=1, column=1, value="RESUMO DAS CONEXÕES DO ROVER (GUIA RÁPIDO DE MONTAGEM)")
t3.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
t3.fill = PatternFill(start_color=C_NAVY, end_color=C_NAVY, fill_type="solid")
t3.alignment = Alignment(horizontal="center", vertical="center")
ws3.row_dimensions[1].height = 32

headers_conexoes = [
    "Periférico / Módulo", "Pino no Módulo", "Ligar Em (Placa / Pino)",
    "Nível de Tensão", "Status / Teste", "Observações Rápidas"
]
style_header(ws3, 3, headers_conexoes, fill_color=C_HEADER)

dados_conexoes = [
    # Chicote Serial
    ("Chicote Móvel 4 Fios", "Fio Vermelho (5V)", "Saída Step-Down -> ESP32 5V", "5.0V", "Planejado", "Alimenta placa da câmera"),
    ("Chicote Móvel 4 Fios", "Fio Preto (GND)", "GND Central -> ESP32 GND", "0V", "Planejado", "Terra de referência comum"),
    ("Chicote Móvel 4 Fios", "Fio Azul (TX -> RX)", "ESP32 GPIO 1 (TX) -> Nano D0 (RX)", "3.3V", "Planejado", "Comandos de movimento e servos"),
    ("Chicote Móvel 4 Fios", "Fio Verde (RX <- TX)", "Nano D1 (TX) -> Divisor -> ESP32 GPIO 3 (RX)", "5V -> 3.3V", "Planejado", "Telemetria opcional (usar divisor 1k/2k)"),
    # Ponte H
    ("Driver TB6612FNG", "VM (Potência Motores)", "Positivo Bateria Li-Ion 7.4V", "7.4V a 8.4V", "Planejado", "Ligado após a Chave Geral KCD1"),
    ("Driver TB6612FNG", "VCC (Lógica)", "Saída 5.0V Step-Down", "5.0V", "Planejado", "Alimentação do chip lógico"),
    ("Driver TB6612FNG", "GND", "GND Central do Robô", "0V", "Planejado", "Terra comum"),
    ("Driver TB6612FNG", "STBY (Standby)", "Pino 5.0V (Ativo)", "5.0V", "Planejado", "Mantém ponte H sempre ativada"),
    ("Driver TB6612FNG", "PWMA (Velocidade Esq)", "Arduino Nano Pino D3", "PWM (0-255)", "Planejado", "2 motores esquerdos em paralelo"),
    ("Driver TB6612FNG", "AIN1 / AIN2 (Sentido Esq)", "Arduino Nano Pinos D4 e D5", "5V Digital", "Planejado", "Controle de direção esquerda"),
    ("Driver TB6612FNG", "PWMB (Velocidade Dir)", "Arduino Nano Pino D6", "PWM (0-255)", "Planejado", "2 motores direitos em paralelo"),
    ("Driver TB6612FNG", "BIN1 / BIN2 (Sentido Dir)", "Arduino Nano Pinos D7 e D8", "5V Digital", "Planejado", "Controle de direção direita"),
    # Servos Pan / Tilt
    ("Micro Servo SG90 Pan", "Sinal (Amarelo)", "Arduino Nano Pino D9", "PWM 5V", "Planejado", "Giro horizontal (0° a 180°, centro 90°)"),
    ("Micro Servo SG90 Pan", "VCC (Vermelho) / GND (Marrom)", "Saída 5.0V Step-Down / GND", "5.0V", "Planejado", "NUNCA alimentar pelo pino 5V do Nano!"),
    ("Micro Servo SG90 Tilt", "Sinal (Amarelo)", "Arduino Nano Pino D10", "PWM 5V", "Planejado", "Inclinação vertical (50° a 130°, centro 90°)"),
    ("Micro Servo SG90 Tilt", "VCC (Vermelho) / GND (Marrom)", "Saída 5.0V Step-Down / GND", "5.0V", "Planejado", "NUNCA alimentar pelo pino 5V do Nano!"),
    # Sinalização e Áudio
    ("Barra 8 LEDs WS2812B", "DIN (Dados)", "Arduino Nano Pino D11", "5V Digital", "Planejado", "Farol dianteiro, lanternas e alertas"),
    ("Barra 8 LEDs WS2812B", "5V / GND", "Saída 5.0V Step-Down / GND", "5.0V", "Planejado", "Alimentação direta"),
    ("Buzzer Passivo 5V", "Sinal / GND", "Arduino Nano Pino D12 / GND", "5V Digital", "Planejado", "Bips e alertas sonoros via tone()"),
    # Bateria
    ("Leitura de Bateria", "Divisor Resistivo", "Bateria (+) -> 10k -> Nano A0 -> 4.7k -> GND", "Max 2.68V", "Planejado", "Bateria 8.4V cheia gera 2.68V no pino A0")
]

for idx, row_d in enumerate(dados_conexoes, 4):
    ws3.row_dimensions[idx].height = 22
    bg = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=C_WHITE, end_color=C_WHITE, fill_type="solid")
    
    for c_idx, val in enumerate(row_d, 1):
        cell = ws3.cell(row=idx, column=c_idx, value=val)
        cell.border = border_thin
        if c_idx == 5:
            cell.fill = FILL_USER_EDIT
            cell.font = FONT_USER_EDIT
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c_idx in [1, 2, 4]:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10, bold=(c_idx==1))
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")

auto_width(ws3)

# Salva arquivo
caminho = "/home/usuario/Documentos/rover/tabela_pinagem_esp32_nano.xlsx"
wb.save(caminho)
print(f"Planilha simplificada salva com sucesso em: {caminho}")
