#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza a planilha tabela_pinagem_esp32_nano.xlsx separando explicitamente:
- O que é TRILHA INTERNA DA PLACA (PCB / FPC Câmera / Slot SD / Flash) -> ZERO fios externos
- O que é FIO EXTERNO (Chicote de 4 fios / Conexões do Chassi)
- Pinos não usados continuam 100% em branco para o usuário
- Sem cabeçalhos decorativos (começa direto na linha 1)
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
wb.remove(wb.active)  # Remove padrão

# Cores de Destaque
FILL_INTERNO = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")  # Amarelo/Laranja claro (Trilha Interna)
FONT_INTERNO = Font(name="Calibri", size=10, bold=True, color="92400E")

FILL_EXTERNO = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")  # Verde claro (Fio Externo)
FONT_EXTERNO = Font(name="Calibri", size=10, bold=True, color="166534")

FILL_PWR = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")      # Cinza (Energia)
FONT_PWR = Font(name="Calibri", size=10, bold=True, color="334155")

C_HEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
C_HEADER_FONT = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

border_thin = Border(
    left=Side(style='thin', color="CBD5E1"),
    right=Side(style='thin', color="CBD5E1"),
    top=Side(style='thin', color="CBD5E1"),
    bottom=Side(style='thin', color="CBD5E1")
)

def style_header(ws, row_idx, headers):
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=h)
        cell.font = C_HEADER_FONT
        cell.fill = C_HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_thin
    ws.row_dimensions[row_idx].height = 26

def auto_width(ws):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            if cell.value:
                for line in str(cell.value).split('\n'):
                    max_len = max(max_len, len(line))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

headers_tab = [
    "Pino Físico",
    "Silk na Placa",
    "GPIO Nativo",
    "Tipo de Ligação Física",
    "Uso",
    "Status",
    "Observações"
]


# ==============================================================================
# ABA 1: Sem_Nano
# ==============================================================================
ws1 = wb.create_sheet(title="Sem_Nano")
ws1.views.sheetView[0].showGridLines = True
style_header(ws1, 1, headers_tab)

pinos_sem_nano = [
    ("P01 (Header Esq)", "5V", "-", "Fio Externo", "Alimentação 5.0V", "OCUPADO (Energia)", "Entrada de energia para o regulador 3.3V", FILL_PWR, FONT_PWR),
    ("P02 (Header Esq)", "GND", "-", "Fio Externo", "GND Comum", "OCUPADO (Terra)", "Referência de terra da placa", FILL_PWR, FONT_PWR),
    ("P03 (Header Esq)", "IO12", "GPIO 12", "Trilha Interna PCB", "MicroSD (Data 2)", "OCUPADO (MicroSD)", "Zero fios externos. Trilha de cobre vai direto pro slot SD", FILL_INTERNO, FONT_INTERNO),
    ("P04 (Header Esq)", "IO13", "GPIO 13", "Trilha Interna PCB", "MicroSD (Data 3)", "OCUPADO (MicroSD)", "Zero fios externos. Trilha vai para o slot MicroSD", FILL_INTERNO, FONT_INTERNO),
    ("P05 (Header Esq)", "IO15", "GPIO 15", "Trilha Interna PCB", "MicroSD (CMD)", "OCUPADO (MicroSD)", "Zero fios externos. Trilha vai para o slot MicroSD", FILL_INTERNO, FONT_INTERNO),
    ("P06 (Header Esq)", "IO14", "GPIO 14", "Trilha Interna PCB", "MicroSD (CLK)", "OCUPADO (MicroSD)", "Zero fios externos. Clock do leitor MicroSD", FILL_INTERNO, FONT_INTERNO),
    ("P07 (Header Esq)", "IO2", "GPIO 2", "Trilha Interna PCB", "LED Onboard", "OCUPADO (LED / Boot)", "Zero fios externos. Ligado ao LED onboard da placa", FILL_INTERNO, FONT_INTERNO),
    ("P08 (Header Esq)", "IO4", "GPIO 4", "Trilha Interna PCB", "Flash LED", "OCUPADO (Flash)", "Zero fios externos. Trilha vai para o transistor do Flash", FILL_INTERNO, FONT_INTERNO),
    ("P09 (Header Dir)", "3V3", "-", "Livre / Sem Fio", "Saída 3.3V", "OCUPADO (Energia)", "Não conectar fio (saída fraca de ~50mA)", FILL_PWR, FONT_PWR),
    ("P10 (Header Dir)", "GND", "-", "Livre / Sem Fio", "GND Comum", "OCUPADO (Terra)", "Não conectar fio", FILL_PWR, FONT_PWR),
    ("P11 (Header Dir)", "IO16", "GPIO 16", "Livre / Sem Fio", "", "", "Disponível para uso (zero conexões)", None, None),
    ("P12 (Header Dir)", "IO0", "GPIO 0", "Trilha Interna PCB", "Câmera (XCLK) / Boot", "OCUPADO (Câmera)", "Zero fios externos. Trilha 20MHz vai direto para a câmera", FILL_INTERNO, FONT_INTERNO),
    ("P13 (Header Dir)", "U0R", "GPIO 3", "Livre / Sem Fio", "", "", "Disponível para uso (Porta Serial RX)", None, None),
    ("P14 (Header Dir)", "U0T", "GPIO 1", "Livre / Sem Fio", "", "", "Disponível para uso (Porta Serial TX)", None, None),
    ("P15 (Header Dir)", "GND", "-", "Livre / Sem Fio", "GND Comum", "OCUPADO (Terra)", "Não conectar fio", FILL_PWR, FONT_PWR),
    ("P16 (Header Dir)", "VCC", "-", "Livre / Sem Fio", "VCC Auxiliar", "OCUPADO (Energia)", "Não conectar fio", FILL_PWR, FONT_PWR)
]

for idx, p in enumerate(pinos_sem_nano, 2):
    ws1.row_dimensions[idx].height = 20
    p_num, p_silk, p_gpio, p_tipo_lig, p_uso, p_st, p_obs, fill_s, font_s = p

    ws1.cell(row=idx, column=1, value=p_num).alignment = Alignment(horizontal="center", vertical="center")
    ws1.cell(row=idx, column=2, value=p_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws1.cell(row=idx, column=3, value=p_gpio).alignment = Alignment(horizontal="center", vertical="center")
    
    c_lig = ws1.cell(row=idx, column=4, value=p_tipo_lig)
    c_lig.alignment = Alignment(horizontal="center", vertical="center")

    c_uso = ws1.cell(row=idx, column=5, value=p_uso)
    c_uso.alignment = Alignment(horizontal="left", vertical="center")

    c_st = ws1.cell(row=idx, column=6, value=p_st)
    c_st.alignment = Alignment(horizontal="center", vertical="center")

    c_obs = ws1.cell(row=idx, column=7, value=p_obs)
    c_obs.alignment = Alignment(horizontal="left", vertical="center")

    for c in range(1, 8):
        cell_obj = ws1.cell(row=idx, column=c)
        cell_obj.border = border_thin
        cell_obj.font = Font(name="Calibri", size=10, bold=(c==2))

    if fill_s and font_s:
        c_lig.fill = fill_s
        c_lig.font = font_s
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
style_header(ws2, 1, headers_tab)

pinos_com_nano = [
    ("P01 (Header Esq)", "5V", "-", "Fio Externo (Chicote)", "Alimentação 5.0V (Chicote)", "OCUPADO (Energia)", "FIO 1: Recebe 5.0V do Step-Down pelo chicote", FILL_EXTERNO, FONT_EXTERNO),
    ("P02 (Header Esq)", "GND", "-", "Fio Externo (Chicote)", "GND Comum (Chicote)", "OCUPADO (Terra)", "FIO 2: Terra comum com o chassi pelo chicote", FILL_EXTERNO, FONT_EXTERNO),
    ("P03 (Header Esq)", "IO12", "GPIO 12", "Trilha Interna PCB", "MicroSD (Data 2)", "OCUPADO (MicroSD)", "Zero fios externos. Fica totalmente livre no conector", FILL_INTERNO, FONT_INTERNO),
    ("P04 (Header Esq)", "IO13", "GPIO 13", "Trilha Interna PCB", "MicroSD (Data 3)", "OCUPADO (MicroSD)", "Zero fios externos. Fica livre no conector", FILL_INTERNO, FONT_INTERNO),
    ("P05 (Header Esq)", "IO15", "GPIO 15", "Trilha Interna PCB", "MicroSD (CMD)", "OCUPADO (MicroSD)", "Zero fios externos. Fica livre no conector", FILL_INTERNO, FONT_INTERNO),
    ("P06 (Header Esq)", "IO14", "GPIO 14", "Trilha Interna PCB", "MicroSD (CLK)", "OCUPADO (MicroSD)", "Zero fios externos. Fica livre no conector", FILL_INTERNO, FONT_INTERNO),
    ("P07 (Header Esq)", "IO2", "GPIO 2", "Trilha Interna PCB", "LED Onboard", "OCUPADO (LED / Boot)", "Zero fios externos. Sem risco de puxar nível no boot", FILL_INTERNO, FONT_INTERNO),
    ("P08 (Header Esq)", "IO4", "GPIO 4", "Trilha Interna PCB", "Flash LED", "OCUPADO (Flash)", "Zero fios externos. Trilha interna para o LED Flash", FILL_INTERNO, FONT_INTERNO),
    ("P09 (Header Dir)", "3V3", "-", "Livre / Sem Fio", "Saída 3.3V", "OCUPADO (Energia)", "Deixar desconectado", FILL_PWR, FONT_PWR),
    ("P10 (Header Dir)", "GND", "-", "Livre / Sem Fio", "GND Comum", "OCUPADO (Terra)", "Deixar desconectado", FILL_PWR, FONT_PWR),
    ("P11 (Header Dir)", "IO16", "GPIO 16", "Livre / Sem Fio", "", "", "Totalmente livre para uso se desejar", None, None),
    ("P12 (Header Dir)", "IO0", "GPIO 0", "Trilha Interna PCB", "Câmera (XCLK) / Boot", "OCUPADO (Câmera)", "Zero fios externos. Usado para clock interno da câmera", FILL_INTERNO, FONT_INTERNO),
    ("P13 (Header Dir)", "U0R", "GPIO 3", "Fio Externo (Chicote)", "Telemetria <- Nano TX", "OCUPADO (Serial)", "FIO 4: Recebe telemetria do Nano (com divisor 1k/2k)", FILL_EXTERNO, FONT_EXTERNO),
    ("P14 (Header Dir)", "U0T", "GPIO 1", "Fio Externo (Chicote)", "Comandos -> Nano RX", "OCUPADO (Serial)", "FIO 3: Envia comandos de movimento e servos ao Nano", FILL_EXTERNO, FONT_EXTERNO),
    ("P15 (Header Dir)", "GND", "-", "Livre / Sem Fio", "GND Comum", "OCUPADO (Terra)", "Deixar desconectado", FILL_PWR, FONT_PWR),
    ("P16 (Header Dir)", "VCC", "-", "Livre / Sem Fio", "VCC Auxiliar", "OCUPADO (Energia)", "Deixar desconectado", FILL_PWR, FONT_PWR)
]

for idx, p in enumerate(pinos_com_nano, 2):
    ws2.row_dimensions[idx].height = 20
    p_num, p_silk, p_gpio, p_tipo_lig, p_uso, p_st, p_obs, fill_s, font_s = p

    ws2.cell(row=idx, column=1, value=p_num).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx, column=2, value=p_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx, column=3, value=p_gpio).alignment = Alignment(horizontal="center", vertical="center")

    c_lig = ws2.cell(row=idx, column=4, value=p_tipo_lig)
    c_lig.alignment = Alignment(horizontal="center", vertical="center")

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
        c_lig.fill = fill_s
        c_lig.font = font_s
        c_uso.fill = fill_s
        c_uso.font = font_s
        c_st.fill = fill_s
        c_st.font = font_s

# Tabela do Arduino Nano (Onde os fios externos do chassi se conectam)
r_nano_start = 20
headers_nano = [
    "Pino Nano",
    "Silk no Nano",
    "Porta ATmega",
    "Tipo de Ligação Física",
    "Uso",
    "Status",
    "Observações"
]
style_header(ws2, r_nano_start, headers_nano)

pinos_nano_lista = [
    ("D0", "RX0", "PD0", "Fio Externo (Chicote)", "Comandos <- ESP32 TX", "OCUPADO (Serial)", "Recebe comandos de movimento direto (3.3V TTL)", FILL_EXTERNO, FONT_EXTERNO),
    ("D1", "TX1", "PD1", "Fio Externo (Chicote)", "Telemetria -> ESP32 RX", "OCUPADO (Serial)", "Envia telemetria ao ESP32 (usar divisor 1k/2k)", FILL_EXTERNO, FONT_EXTERNO),
    ("D2", "D2", "PD2", "Livre / Sem Fio", "", "", "Livre / Interrupção externa INT0", None, None),
    ("D3", "D3", "PD3", "Fio Externo (Chassi)", "PWMA (TB6612)", "OCUPADO (Motor)", "Velocidade dos 2 motores esquerdos (0-255)", FILL_EXTERNO, FONT_EXTERNO),
    ("D4", "D4", "PD4", "Fio Externo (Chassi)", "AIN1 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor esquerdo", FILL_EXTERNO, FONT_EXTERNO),
    ("D5", "D5", "PD5", "Fio Externo (Chassi)", "AIN2 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor esquerdo", FILL_EXTERNO, FONT_EXTERNO),
    ("D6", "D6", "PD6", "Fio Externo (Chassi)", "PWMB (TB6612)", "OCUPADO (Motor)", "Velocidade dos 2 motores direitos (0-255)", FILL_EXTERNO, FONT_EXTERNO),
    ("D7", "D7", "PD7", "Fio Externo (Chassi)", "BIN1 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor direito", FILL_EXTERNO, FONT_EXTERNO),
    ("D8", "D8", "PB0", "Fio Externo (Chassi)", "BIN2 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor direito", FILL_EXTERNO, FONT_EXTERNO),
    ("D9", "D9", "PB1", "Fio Externo (Chassi)", "Servo Pan (SG90)", "OCUPADO (Servo)", "Giro horizontal da câmera (0° a 180°)", FILL_EXTERNO, FONT_EXTERNO),
    ("D10", "D10", "PB2", "Fio Externo (Chassi)", "Servo Tilt (SG90)", "OCUPADO (Servo)", "Inclinação vertical da câmera", FILL_EXTERNO, FONT_EXTERNO),
    ("D11", "D11", "PB3", "Fio Externo (Chassi)", "Barra 8 LEDs WS2812B", "OCUPADO (LEDs)", "Sinal de dados DIN para cores dos LEDs", FILL_EXTERNO, FONT_EXTERNO),
    ("D12", "D12", "PB4", "Fio Externo (Chassi)", "Buzzer Passivo 5V", "OCUPADO (Áudio)", "Sons, bips e alertas sonoros via tone()", FILL_EXTERNO, FONT_EXTERNO),
    ("D13", "D13", "PB5", "Trilha Interna PCB", "LED Onboard Heartbeat", "OCUPADO (Status)", "Zero fios externos. Pisca indicando funcionamento", FILL_INTERNO, FONT_INTERNO),
    ("A0", "A0", "PC0", "Fio Externo (Chassi)", "Leitura Bateria Li-Ion", "OCUPADO (Bateria)", "Divisor resistivo 10k/4.7k (8.4V max = 2.68V)", FILL_EXTERNO, FONT_EXTERNO),
    ("A1", "A1", "PC1", "Livre / Sem Fio", "", "", "Livre para sensor", None, None),
    ("A2", "A2", "PC2", "Livre / Sem Fio", "", "", "Livre para sensor", None, None),
    ("A3", "A3", "PC3", "Livre / Sem Fio", "", "", "Livre para sensor", None, None),
    ("A4", "A4", "PC4", "Livre / Sem Fio", "", "", "Livre / Barramento I2C Dados", None, None),
    ("A5", "A5", "PC5", "Livre / Sem Fio", "", "", "Livre / Barramento I2C Clock", None, None),
    ("A6", "A6", "ADC6", "Livre / Sem Fio", "", "", "Livre para leitura analógica", None, None),
    ("A7", "A7", "ADC7", "Livre / Sem Fio", "", "", "Livre para leitura analógica", None, None),
    ("5V", "5V", "-", "Fio Externo (Chassi)", "Entrada 5.0V (Step-Down)", "OCUPADO (Energia)", "Alimenta o Nano direto pelo barramento 5V", FILL_PWR, FONT_PWR),
    ("GND", "GND", "-", "Fio Externo (Chassi)", "GND Comum", "OCUPADO (Terra)", "Referência de terra comum", FILL_PWR, FONT_PWR)
]

for idx_n, pn in enumerate(pinos_nano_lista, r_nano_start + 1):
    ws2.row_dimensions[idx_n].height = 20
    n_num, n_silk, n_port, n_tipo_lig, n_uso, n_st, n_obs, fill_sn, font_sn = pn

    ws2.cell(row=idx_n, column=1, value=n_num).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx_n, column=2, value=n_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws2.cell(row=idx_n, column=3, value=n_port).alignment = Alignment(horizontal="center", vertical="center")

    cn_lig = ws2.cell(row=idx_n, column=4, value=n_tipo_lig)
    cn_lig.alignment = Alignment(horizontal="center", vertical="center")

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
        cn_lig.fill = fill_sn
        cn_lig.font = font_sn
        cn_uso.fill = fill_sn
        cn_uso.font = font_sn
        cn_st.fill = fill_sn
        cn_st.font = font_sn

auto_width(ws2)

caminho = "/home/usuario/Documentos/rover/tabela_pinagem_esp32_nano.xlsx"
wb.save(caminho)
print(f"Planilha atualizada com distinção física Trilha Interna vs Fio Externo em: {caminho}")
