#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a planilha tabela_pinagem_esp32_nano.xlsx sem cabeçalhos decorativos:
- Apenas 2 abas: "Sem_Nano" e "Com_Nano"
- Linha 1 já inicia direto no cabeçalho das colunas (Pino, Silk, GPIO, Tipo, Uso, Status, Observações)
- Coluna "Uso" substituindo "tentativa de ligação"
- Pinos NÃO usados ficam 100% EM BRANCO (sem texto e sem cor) para o usuário editar
- APENAS os pinos ocupados pela câmera, MicroSD, Flash, Energia ou Comunicação são preenchidos e coloridos
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
wb.remove(wb.active)  # Remove aba padrão

# Estilos de Cores para Pinos Ocupados
# Câmera / Boot: Laranja suave
FILL_CAM = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid")
FONT_CAM = Font(name="Calibri", size=10, bold=True, color="9A3412")

# MicroSD: Azul/Índigo suave
FILL_SD = PatternFill(start_color="E0E7FF", end_color="E0E7FF", fill_type="solid")
FONT_SD = Font(name="Calibri", size=10, bold=True, color="3730A3")

# Flash LED: Amarelo suave
FILL_FLASH = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
FONT_FLASH = Font(name="Calibri", size=10, bold=True, color="854D0E")

# Energia / Terra: Cinza neutro
FILL_PWR = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
FONT_PWR = Font(name="Calibri", size=10, bold=True, color="334155")

# Comunicação Serial (RX/TX): Verde suave
FILL_SERIAL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
FONT_SERIAL = Font(name="Calibri", size=10, bold=True, color="166534")

# Cabeçalho da Tabela
C_HEADER_FILL = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
C_HEADER_FONT = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

# Borda suave
border_thin = Border(
    left=Side(style='thin', color="CBD5E1"),
    right=Side(style='thin', color="CBD5E1"),
    top=Side(style='thin', color="CBD5E1"),
    bottom=Side(style='thin', color="CBD5E1")
)

def style_header_row(ws, row_idx, headers):
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=h)
        cell.font = C_HEADER_FONT
        cell.fill = C_HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_thin
    ws.row_dimensions[row_idx].height = 24

def auto_width(ws):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_l = 0
        for cell in col:
            if cell.value:
                for line in str(cell.value).split('\n'):
                    max_l = max(max_l, len(line))
        ws.column_dimensions[col_letter].width = max(max_l + 3, 12)


# ==============================================================================
# ABA 1: Sem_Nano
# ==============================================================================
ws1 = wb.create_sheet(title="Sem_Nano")
ws1.views.sheetView[0].showGridLines = True

headers_tab = [
    "Pino Físico",
    "Silk na Placa",
    "GPIO",
    "Tipo",
    "Uso",
    "Status",
    "Observações"
]
style_header_row(ws1, 1, headers_tab)

# 16 Pinos que saem fisicamente nos headers do ESP32
# Se NÃO ocupado: uso="", status="", fill=None
pinos_sem_nano = [
    ("P01 (Header Esq)", "5V", "-", "Alimentação", "Alimentação 5.0V", "OCUPADO (Energia)", "Entrada de energia para o regulador 3.3V", FILL_PWR, FONT_PWR),
    ("P02 (Header Esq)", "GND", "-", "Terra", "GND Comum", "OCUPADO (Terra)", "Referência de terra da placa", FILL_PWR, FONT_PWR),
    ("P03 (Header Esq)", "IO12", "GPIO 12", "Digital I/O", "MicroSD (Data 2)", "OCUPADO (MicroSD)", "Usado internamente pelo leitor de cartão SD / Boot", FILL_SD, FONT_SD),
    ("P04 (Header Esq)", "IO13", "GPIO 13", "Digital I/O", "MicroSD (Data 3)", "OCUPADO (MicroSD)", "Usado internamente pelo leitor de cartão SD", FILL_SD, FONT_SD),
    ("P05 (Header Esq)", "IO15", "GPIO 15", "Digital I/O", "MicroSD (CMD)", "OCUPADO (MicroSD)", "Usado internamente pelo leitor de cartão SD", FILL_SD, FONT_SD),
    ("P06 (Header Esq)", "IO14", "GPIO 14", "Digital I/O", "MicroSD (CLK)", "OCUPADO (MicroSD)", "Clock do leitor de cartão SD", FILL_SD, FONT_SD),
    ("P07 (Header Esq)", "IO2", "GPIO 2", "Digital I/O", "LED Onboard", "OCUPADO (LED / Boot)", "Conectado ao LED onboard da placa / Boot", FILL_SD, FONT_SD),
    ("P08 (Header Esq)", "IO4", "GPIO 4", "Digital I/O", "Flash LED", "OCUPADO (Flash)", "Aciona o transistor do LED Flash de alta potência", FILL_FLASH, FONT_FLASH),
    ("P09 (Header Dir)", "3V3", "-", "Saída 3.3V", "Saída 3.3V", "OCUPADO (Energia)", "Saída regulada pequena (~50mA)", FILL_PWR, FONT_PWR),
    ("P10 (Header Dir)", "GND", "-", "Terra", "GND Comum", "OCUPADO (Terra)", "Referência de terra da placa", FILL_PWR, FONT_PWR),
    ("P11 (Header Dir)", "IO16", "GPIO 16", "Digital I/O", "", "", "Disponível para uso", None, None),
    ("P12 (Header Dir)", "IO0", "GPIO 0", "Digital / Boot", "Câmera (XCLK) / Boot", "OCUPADO (Câmera)", "Clock 20MHz do sensor de imagem e pino de boot", FILL_CAM, FONT_CAM),
    ("P13 (Header Dir)", "U0R", "GPIO 3", "Serial UART RX", "", "", "Disponível para uso (Porta Serial RX)", None, None),
    ("P14 (Header Dir)", "U0T", "GPIO 1", "Serial UART TX", "", "", "Disponível para uso (Porta Serial TX)", None, None),
    ("P15 (Header Dir)", "GND", "-", "Terra", "GND Comum", "OCUPADO (Terra)", "Referência de terra da placa", FILL_PWR, FONT_PWR),
    ("P16 (Header Dir)", "VCC", "-", "Alimentação", "VCC Auxiliar", "OCUPADO (Energia)", "Pino de alimentação auxiliar", FILL_PWR, FONT_PWR)
]

for idx, p in enumerate(pinos_sem_nano, 2):
    ws1.row_dimensions[idx].height = 20
    p_num, p_silk, p_gpio, p_tipo, p_uso, p_st, p_obs, fill_s, font_s = p

    ws1.cell(row=idx, column=1, value=p_num).alignment = Alignment(horizontal="center", vertical="center")
    ws1.cell(row=idx, column=2, value=p_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws1.cell(row=idx, column=3, value=p_gpio).alignment = Alignment(horizontal="center", vertical="center")
    ws1.cell(row=idx, column=4, value=p_tipo).alignment = Alignment(horizontal="center", vertical="center")

    c_uso = ws1.cell(row=idx, column=5, value=p_uso)
    c_uso.alignment = Alignment(horizontal="left", vertical="center")

    c_st = ws1.cell(row=idx, column=6, value=p_st)
    c_st.alignment = Alignment(horizontal="center", vertical="center")

    c_obs = ws1.cell(row=idx, column=7, value=p_obs)
    c_obs.alignment = Alignment(horizontal="left", vertical="center")

    # Borda em todas as células
    for c in range(1, 8):
        cell_obj = ws1.cell(row=idx, column=c)
        cell_obj.border = border_thin
        cell_obj.font = Font(name="Calibri", size=10, bold=(c==2))

    # Colore APENAS os ocupados
    if fill_s and font_s:
        c_uso.fill = fill_s
        c_uso.font = font_s
        c_st.fill = fill_s
        c_st.font = font_s

auto_width(ws1)


# ==============================================================================
# ABA 2: Com_Nano
# ==============================================================================
ws2 = wb.create_sheet(title="Com_Nano")
ws2.views.sheetView[0].showGridLines = True

style_header_row(ws2, 1, headers_tab)

# Cenário Com Nano: ESP32 cuidando da câmera e conversando com Nano via RX/TX
pinos_com_nano = [
    ("P01 (Header Esq)", "5V", "-", "Alimentação", "Alimentação 5.0V (Chicote)", "OCUPADO (Energia)", "Alimentação vinda do Step-Down pelo chicote", FILL_PWR, FONT_PWR),
    ("P02 (Header Esq)", "GND", "-", "Terra", "GND Comum (Chicote)", "OCUPADO (Terra)", "Referência de terra comum com o chassi", FILL_PWR, FONT_PWR),
    ("P03 (Header Esq)", "IO12", "GPIO 12", "Digital I/O", "MicroSD (Data 2)", "OCUPADO (MicroSD)", "Usado internamente pelo leitor de cartão SD / Boot", FILL_SD, FONT_SD),
    ("P04 (Header Esq)", "IO13", "GPIO 13", "Digital I/O", "MicroSD (Data 3)", "OCUPADO (MicroSD)", "Usado internamente pelo leitor de cartão SD", FILL_SD, FONT_SD),
    ("P05 (Header Esq)", "IO15", "GPIO 15", "Digital I/O", "MicroSD (CMD)", "OCUPADO (MicroSD)", "Usado internamente pelo leitor de cartão SD", FILL_SD, FONT_SD),
    ("P06 (Header Esq)", "IO14", "GPIO 14", "Digital I/O", "MicroSD (CLK)", "OCUPADO (MicroSD)", "Clock do leitor de cartão SD", FILL_SD, FONT_SD),
    ("P07 (Header Esq)", "IO2", "GPIO 2", "Digital I/O", "LED Onboard", "OCUPADO (LED / Boot)", "Conectado ao LED onboard da placa / Boot", FILL_SD, FONT_SD),
    ("P08 (Header Esq)", "IO4", "GPIO 4", "Digital I/O", "Flash LED", "OCUPADO (Flash)", "Aciona o transistor do LED Flash de alta potência", FILL_FLASH, FONT_FLASH),
    ("P09 (Header Dir)", "3V3", "-", "Saída 3.3V", "Saída 3.3V", "OCUPADO (Energia)", "Saída regulada pequena (~50mA)", FILL_PWR, FONT_PWR),
    ("P10 (Header Dir)", "GND", "-", "Terra", "GND Comum", "OCUPADO (Terra)", "Referência de terra da placa", FILL_PWR, FONT_PWR),
    ("P11 (Header Dir)", "IO16", "GPIO 16", "Digital I/O", "", "", "Totalmente livre para uso", None, None),
    ("P12 (Header Dir)", "IO0", "GPIO 0", "Digital / Boot", "Câmera (XCLK) / Boot", "OCUPADO (Câmera)", "Clock 20MHz do sensor de imagem e pino de boot", FILL_CAM, FONT_CAM),
    ("P13 (Header Dir)", "U0R", "GPIO 3", "Serial UART RX", "Telemetria <- Nano TX", "OCUPADO (Serial)", "Recebe dados do Nano (usar divisor de tensão 1k/2k)", FILL_SERIAL, FONT_SERIAL),
    ("P14 (Header Dir)", "U0T", "GPIO 1", "Serial UART TX", "Comandos -> Nano RX", "OCUPADO (Serial)", "Envia comandos de motores e servos direto ao Nano (3.3V)", FILL_SERIAL, FONT_SERIAL),
    ("P15 (Header Dir)", "GND", "-", "Terra", "GND Comum", "OCUPADO (Terra)", "Referência de terra da placa", FILL_PWR, FONT_PWR),
    ("P16 (Header Dir)", "VCC", "-", "Alimentação", "VCC Auxiliar", "OCUPADO (Energia)", "Pino de alimentação auxiliar", FILL_PWR, FONT_PWR)
]

for idx, p in enumerate(pinos_com_nano, 2):
    ws2.row_dimensions[idx].height = 20
    p_num, p_silk, p_gpio, p_tipo, p_uso, p_st, p_obs, fill_s, font_s = p

    ws2.cell(row=idx, column=1, value=p_num).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx, column=2, value=p_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx, column=3, value=p_gpio).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx, column=4, value=p_tipo).alignment = Alignment(horizontal="center", vertical="center")

    c_uso = ws2.cell(row=idx, column=5, value=p_uso)
    c_uso.alignment = Alignment(horizontal="left", vertical="center")

    c_st = ws2.cell(row=idx, column=6, value=p_st)
    c_st.alignment = Alignment(horizontal="center", vertical="center")

    c_obs = ws2.cell(row=idx, column=7, value=p_obs)
    c_obs.alignment = Alignment(horizontal="left", vertical="center")

    for c in range(1, 8):
        cell_obj = ws2.cell(row=idx, column=c)
        cell_obj.border = border_thin
        cell_obj.font = Font(name="Calibri", size=10, bold=(c==2))

    if fill_s and font_s:
        c_uso.fill = fill_s
        c_uso.font = font_s
        c_st.fill = fill_s
        c_st.font = font_s

# Tabela do Arduino Nano (Abaixo da tabela do ESP32 na mesma aba, sem banners decorativos)
r_nano_start = 20
headers_nano = [
    "Pino Nano",
    "Silk no Nano",
    "Porta ATmega",
    "Tipo",
    "Uso",
    "Status",
    "Observações"
]
style_header_row(ws2, r_nano_start, headers_nano)

pinos_nano_lista = [
    ("D0", "RX0", "PD0", "Serial UART RX", "Comandos <- ESP32 TX", "OCUPADO (Serial)", "Recebe comandos de movimento direto (3.3V TTL)", FILL_SERIAL, FONT_SERIAL),
    ("D1", "TX1", "PD1", "Serial UART TX", "Telemetria -> ESP32 RX", "OCUPADO (Serial)", "Envia telemetria ao ESP32 (usar divisor 1k/2k)", FILL_SERIAL, FONT_SERIAL),
    ("D2", "D2", "PD2", "Digital I/O", "", "", "Livre / Interrupção externa INT0", None, None),
    ("D3", "D3", "PD3", "Digital / PWM", "PWMA (TB6612)", "OCUPADO (Motor)", "Velocidade dos 2 motores esquerdos (0-255)", FILL_CAM, FONT_CAM),
    ("D4", "D4", "PD4", "Digital Output", "AIN1 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor esquerdo", FILL_CAM, FONT_CAM),
    ("D5", "D5", "PD5", "Digital / PWM", "AIN2 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor esquerdo", FILL_CAM, FONT_CAM),
    ("D6", "D6", "PD6", "Digital / PWM", "PWMB (TB6612)", "OCUPADO (Motor)", "Velocidade dos 2 motores direitos (0-255)", FILL_CAM, FONT_CAM),
    ("D7", "D7", "PD7", "Digital Output", "BIN1 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor direito", FILL_CAM, FONT_CAM),
    ("D8", "D8", "PB0", "Digital Output", "BIN2 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor direito", FILL_CAM, FONT_CAM),
    ("D9", "D9", "PB1", "Digital / PWM", "Servo Pan (SG90)", "OCUPADO (Servo)", "Giro horizontal da câmera (0° a 180°)", FILL_FLASH, FONT_FLASH),
    ("D10", "D10", "PB2", "Digital / PWM", "Servo Tilt (SG90)", "OCUPADO (Servo)", "Inclinação vertical da câmera", FILL_FLASH, FONT_FLASH),
    ("D11", "D11", "PB3", "Digital / PWM", "Barra 8 LEDs WS2812B", "OCUPADO (LEDs)", "Sinal de dados DIN para cores dos LEDs", FILL_SD, FONT_SD),
    ("D12", "D12", "PB4", "Digital Output", "Buzzer Passivo 5V", "OCUPADO (Áudio)", "Sons, bips e alertas sonoros via tone()", FILL_SD, FONT_SD),
    ("D13", "D13", "PB5", "Digital Output", "LED Onboard Heartbeat", "OCUPADO (Status)", "Pisca a cada 500ms indicando funcionamento", FILL_PWR, FONT_PWR),
    ("A0", "A0", "PC0", "Analógico Input", "Leitura Bateria Li-Ion", "OCUPADO (Bateria)", "Divisor resistivo 10k/4.7k (8.4V max = 2.68V)", FILL_CAM, FONT_CAM),
    ("A1", "A1", "PC1", "Analógico / Digital", "", "", "Livre para sensor", None, None),
    ("A2", "A2", "PC2", "Analógico / Digital", "", "", "Livre para sensor", None, None),
    ("A3", "A3", "PC3", "Analógico / Digital", "", "", "Livre para sensor", None, None),
    ("A4", "A4", "PC4", "Analógico / I2C SDA", "", "", "Livre / Barramento I2C Dados", None, None),
    ("A5", "A5", "PC5", "Analógico / I2C SCL", "", "", "Livre / Barramento I2C Clock", None, None),
    ("A6", "A6", "ADC6", "Analógico Puro", "", "", "Livre para leitura analógica", None, None),
    ("A7", "A7", "ADC7", "Analógico Puro", "", "", "Livre para leitura analógica", None, None),
    ("5V", "5V", "-", "Alimentação 5V", "Entrada 5.0V (Step-Down)", "OCUPADO (Energia)", "Alimenta o Nano direto pelo barramento 5V", FILL_PWR, FONT_PWR),
    ("GND", "GND", "-", "Terra", "GND Comum", "OCUPADO (Terra)", "Referência de terra comum", FILL_PWR, FONT_PWR)
]

for idx_n, pn in enumerate(pinos_nano_lista, r_nano_start + 1):
    ws2.row_dimensions[idx_n].height = 20
    n_num, n_silk, n_port, n_tipo, n_uso, n_st, n_obs, fill_sn, font_sn = pn

    ws2.cell(row=idx_n, column=1, value=n_num).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx_n, column=2, value=n_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx_n, column=3, value=n_port).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx_n, column=4, value=n_tipo).alignment = Alignment(horizontal="center", vertical="center")

    cn_uso = ws2.cell(row=idx_n, column=5, value=n_uso)
    cn_uso.alignment = Alignment(horizontal="left", vertical="center")

    cn_st = ws2.cell(row=idx_n, column=6, value=n_st)
    cn_st.alignment = Alignment(horizontal="center", vertical="center")

    cn_obs = ws2.cell(row=idx_n, column=7, value=n_obs)
    cn_obs.alignment = Alignment(horizontal="left", vertical="center")

    for c in range(1, 8):
        cell_obj = ws2.cell(row=idx_n, column=c)
        cell_obj.border = border_thin
        cell_obj.font = Font(name="Calibri", size=10, bold=(c==2))

    if fill_sn and font_sn:
        cn_uso.fill = fill_sn
        cn_uso.font = font_sn
        cn_st.fill = fill_sn
        cn_st.font = font_sn

auto_width(ws2)

# Salva arquivo
caminho = "/home/usuario/Documentos/rover/tabela_pinagem_esp32_nano.xlsx"
wb.save(caminho)
print(f"Planilha salva com sucesso em: {caminho}")
