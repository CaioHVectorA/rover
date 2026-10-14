#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a planilha oficial com o mapeamento completo e limpo para AMBAS as placas adquiridas:
1. "ESP32_S3_CAM_N16R8" (Placa moderna do Mercado Livre com USB-C, 24 pinos nos headers)
2. "ESP32_CAM_RoboCore" (Placa clássica AI-Thinker de 16 pinos)
3. "Arduino_Nano_Chassi" (Co-processador fixo no chassi assumindo motores, servos e periféricos)

Sem cabeçalhos decorativos (inicia direto na linha 1 com os nomes das colunas).
Pinos livres 100% em branco para edição.
Cores apenas nos pinos ocupados pela câmera, memória, energia e serial.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
wb.remove(wb.active)  # Remove padrão

# Cores suaves
FILL_CAM = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid")      # Laranja suave (Câmera)
FONT_CAM = Font(name="Calibri", size=10, bold=True, color="9A3412")

FILL_SD = PatternFill(start_color="E0E7FF", end_color="E0E7FF", fill_type="solid")       # Azul/Índigo (MicroSD)
FONT_SD = Font(name="Calibri", size=10, bold=True, color="3730A3")

FILL_SERIAL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")   # Verde suave (Serial)
FONT_SERIAL = Font(name="Calibri", size=10, bold=True, color="166534")

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
    ws.row_dimensions[row_idx].height = 24

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
# ABA 1: ESP32-S3-CAM N16R8 (Mercado Livre - USB-C)
# ==============================================================================
ws_s3 = wb.create_sheet(title="ESP32_S3_CAM_N16R8")
ws_s3.views.sheetView[0].showGridLines = True
style_header(ws_s3, 1, headers_tab)

# 24 pinos típicos nos headers da placa ESP32-S3-CAM
pinos_s3 = [
    ("J1-01 (Esq)", "3V3", "-", "Livre / Sem Fio", "Saída 3.3V", "OCUPADO (Energia)", "Alimentação de sensores 3.3V", FILL_PWR, FONT_PWR),
    ("J1-02 (Esq)", "GND", "-", "Fio Externo (Chicote)", "GND Comum (Chicote)", "OCUPADO (Terra)", "FIO 2: Terra de referência comum", FILL_SERIAL, FONT_SERIAL),
    ("J1-03 (Esq)", "IO1", "GPIO 1", "Livre / Sem Fio", "", "", "Livre (ADC1_CH0 / Touch 1)", None, None),
    ("J1-04 (Esq)", "IO2", "GPIO 2", "Livre / Sem Fio", "", "", "Livre (ADC1_CH1 / Touch 2)", None, None),
    ("J1-05 (Esq)", "IO3", "GPIO 3", "Livre / Sem Fio", "", "", "Livre (ADC1_CH2 / Touch 3)", None, None),
    ("J1-06 (Esq)", "IO41", "GPIO 41", "Livre / Sem Fio", "", "", "Livre (I/O Digital de uso geral)", None, None),
    ("J1-07 (Esq)", "IO42", "GPIO 42", "Livre / Sem Fio", "", "", "Livre (I/O Digital de uso geral)", None, None),
    ("J1-08 (Esq)", "TX (U0T)", "GPIO 43", "Fio Externo (Chicote)", "Comandos -> Nano RX (D0)", "OCUPADO (Serial)", "FIO 3: Envia comandos seriais de direção e servos", FILL_SERIAL, FONT_SERIAL),
    ("J1-09 (Esq)", "RX (U0R)", "GPIO 44", "Livre / Sem Fio", "", "", "Livre (Pode ser Fio 4 se quiser telemetria)", None, None),
    ("J1-10 (Esq)", "IO19", "GPIO 19", "Trilha Interna USB", "USB D- (Nativo)", "OCUPADO (USB-C)", "Linha de dados do conector USB-C nativo", FILL_PWR, FONT_PWR),
    ("J1-11 (Esq)", "IO20", "GPIO 20", "Trilha Interna USB", "USB D+ (Nativo)", "OCUPADO (USB-C)", "Linha de dados do conector USB-C nativo", FILL_PWR, FONT_PWR),
    ("J1-12 (Esq)", "IO21", "GPIO 21", "Livre / Sem Fio", "", "", "Livre (I/O Digital)", None, None),
    ("J2-01 (Dir)", "5V", "-", "Fio Externo (Chicote)", "Alimentação 5.0V (Chicote)", "OCUPADO (Energia)", "FIO 1: Recebe 5.0V regulados do Step-Down Mini 560", FILL_SERIAL, FONT_SERIAL),
    ("J2-02 (Dir)", "GND", "-", "Livre / Sem Fio", "GND Auxiliar", "OCUPADO (Terra)", "Terra de referência", FILL_PWR, FONT_PWR),
    ("J2-03 (Dir)", "IO0", "GPIO 0", "Trilha Interna Botão", "Botão BOOT / Gravação", "OCUPADO (Boot)", "Botão de boot soldado na placa", FILL_CAM, FONT_CAM),
    ("J2-04 (Dir)", "IO4", "GPIO 4", "Trilha Interna PCB", "Câmera (SIOD / SDA)", "OCUPADO (Câmera)", "Zero fios externos. Controle I2C da câmera OV5640", FILL_CAM, FONT_CAM),
    ("J2-05 (Dir)", "IO5", "GPIO 5", "Trilha Interna PCB", "Câmera (SIOC / SCL)", "OCUPADO (Câmera)", "Zero fios externos. Clock I2C da câmera OV5640", FILL_CAM, FONT_CAM),
    ("J2-06 (Dir)", "IO6", "GPIO 6", "Trilha Interna PCB", "Câmera (VSYNC)", "OCUPADO (Câmera)", "Zero fios externos. Sincronismo vertical da imagem", FILL_CAM, FONT_CAM),
    ("J2-07 (Dir)", "IO7", "GPIO 7", "Trilha Interna PCB", "Câmera (HREF)", "OCUPADO (Câmera)", "Zero fios externos. Referência horizontal de linha", FILL_CAM, FONT_CAM),
    ("J2-08 (Dir)", "IO8", "GPIO 8", "Trilha Interna PCB", "Câmera (D2)", "OCUPADO (Câmera)", "Zero fios externos. Dado de vídeo DVP da câmera", FILL_CAM, FONT_CAM),
    ("J2-09 (Dir)", "IO9", "GPIO 9", "Trilha Interna PCB", "Câmera (D1)", "OCUPADO (Câmera)", "Zero fios externos. Dado de vídeo DVP da câmera", FILL_CAM, FONT_CAM),
    ("J2-10 (Dir)", "IO10", "GPIO 10", "Trilha Interna PCB", "Câmera (D3)", "OCUPADO (Câmera)", "Zero fios externos. Dado de vídeo DVP da câmera", FILL_CAM, FONT_CAM),
    ("J2-11 (Dir)", "IO11", "GPIO 11", "Trilha Interna PCB", "Câmera (D0)", "OCUPADO (Câmera)", "Zero fios externos. Dado de vídeo DVP da câmera", FILL_CAM, FONT_CAM),
    ("J2-12 (Dir)", "GND", "-", "Livre / Sem Fio", "GND Auxiliar", "OCUPADO (Terra)", "Terra de referência", FILL_PWR, FONT_PWR)
]

for idx, p in enumerate(pinos_s3, 2):
    ws_s3.row_dimensions[idx].height = 20
    p_num, p_silk, p_gpio, p_tipo_lig, p_uso, p_st, p_obs, fill_s, font_s = p

    ws_s3.cell(row=idx, column=1, value=p_num).alignment = Alignment(horizontal="center", vertical="center")
    ws_s3.cell(row=idx, column=2, value=p_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws_s3.cell(row=idx, column=3, value=p_gpio).alignment = Alignment(horizontal="center", vertical="center")

    c_lig = ws_s3.cell(row=idx, column=4, value=p_tipo_lig)
    c_lig.alignment = Alignment(horizontal="center", vertical="center")

    c_uso = ws_s3.cell(row=idx, column=5, value=p_uso)
    c_uso.alignment = Alignment(horizontal="left", vertical="center")

    c_st = ws_s3.cell(row=idx, column=6, value=p_st)
    c_st.alignment = Alignment(horizontal="center", vertical="center")

    c_obs = ws_s3.cell(row=idx, column=7, value=p_obs)
    c_obs.alignment = Alignment(horizontal="left", vertical="center")

    for c in range(1, 8):
        cell_obj = ws_s3.cell(row=idx, column=c)
        cell_obj.border = border_thin
        cell_obj.font = Font(name="Calibri", size=10, bold=(c==2))

    if fill_s and font_s:
        c_lig.fill = fill_s
        c_lig.font = font_s
        c_uso.fill = fill_s
        c_uso.font = font_s
        c_st.fill = fill_s
        c_st.font = font_s

auto_width(ws_s3)


# ==============================================================================
# ABA 2: ESP32-CAM RoboCore (AI-Thinker Clássico - 16 pinos)
# ==============================================================================
ws_c = wb.create_sheet(title="ESP32_CAM_RoboCore")
ws_c.views.sheetView[0].showGridLines = True
style_header(ws_c, 1, headers_tab)

pinos_c = [
    ("P01 (Header Esq)", "5V", "-", "Fio Externo (Chicote)", "Alimentação 5.0V (Chicote)", "OCUPADO (Energia)", "FIO 1: Recebe 5.0V do Step-Down pelo chicote", FILL_SERIAL, FONT_SERIAL),
    ("P02 (Header Esq)", "GND", "-", "Fio Externo (Chicote)", "GND Comum (Chicote)", "OCUPADO (Terra)", "FIO 2: Terra comum com o chassi pelo chicote", FILL_SERIAL, FONT_SERIAL),
    ("P03 (Header Esq)", "IO12", "GPIO 12", "Trilha Interna PCB", "MicroSD (Data 2)", "OCUPADO (MicroSD)", "Zero fios externos. Trilha interna para o slot SD", FILL_SD, FONT_SD),
    ("P04 (Header Esq)", "IO13", "GPIO 13", "Trilha Interna PCB", "MicroSD (Data 3)", "OCUPADO (MicroSD)", "Zero fios externos. Trilha interna para o slot SD", FILL_SD, FONT_SD),
    ("P05 (Header Esq)", "IO15", "GPIO 15", "Trilha Interna PCB", "MicroSD (CMD)", "OCUPADO (MicroSD)", "Zero fios externos. Trilha interna para o slot SD", FILL_SD, FONT_SD),
    ("P06 (Header Esq)", "IO14", "GPIO 14", "Trilha Interna PCB", "MicroSD (CLK)", "OCUPADO (MicroSD)", "Zero fios externos. Clock do cartão SD", FILL_SD, FONT_SD),
    ("P07 (Header Esq)", "IO2", "GPIO 2", "Trilha Interna PCB", "LED Onboard", "OCUPADO (LED / Boot)", "Zero fios externos. Ligado ao LED onboard da placa", FILL_SD, FONT_SD),
    ("P08 (Header Esq)", "IO4", "GPIO 4", "Trilha Interna PCB", "Flash LED", "OCUPADO (Flash)", "Zero fios externos. Trilha interna para o transistor do Flash", FILL_SD, FONT_SD),
    ("P09 (Header Dir)", "3V3", "-", "Livre / Sem Fio", "Saída 3.3V", "OCUPADO (Energia)", "Saída regulada pequena (~50mA)", FILL_PWR, FONT_PWR),
    ("P10 (Header Dir)", "GND", "-", "Livre / Sem Fio", "GND Comum", "OCUPADO (Terra)", "Terra de referência", FILL_PWR, FONT_PWR),
    ("P11 (Header Dir)", "IO16", "GPIO 16", "Livre / Sem Fio", "", "", "Disponível para uso (zero conexões)", None, None),
    ("P12 (Header Dir)", "IO0", "GPIO 0", "Trilha Interna PCB", "Câmera (XCLK) / Boot", "OCUPADO (Câmera)", "Zero fios externos. Clock 20MHz vai direto para a câmera", FILL_CAM, FONT_CAM),
    ("P13 (Header Dir)", "U0R", "GPIO 3", "Livre / Sem Fio", "", "", "Disponível para uso (Porta Serial RX)", None, None),
    ("P14 (Header Dir)", "U0T", "GPIO 1", "Fio Externo (Chicote)", "Comandos -> Nano RX (D0)", "OCUPADO (Serial)", "FIO 3: Envia comandos de movimento e servos ao Nano", FILL_SERIAL, FONT_SERIAL),
    ("P15 (Header Dir)", "GND", "-", "Livre / Sem Fio", "GND Comum", "OCUPADO (Terra)", "Terra de referência", FILL_PWR, FONT_PWR),
    ("P16 (Header Dir)", "VCC", "-", "Livre / Sem Fio", "VCC Auxiliar", "OCUPADO (Energia)", "Alimentação auxiliar", FILL_PWR, FONT_PWR)
]

for idx, p in enumerate(pinos_c, 2):
    ws_c.row_dimensions[idx].height = 20
    p_num, p_silk, p_gpio, p_tipo_lig, p_uso, p_st, p_obs, fill_s, font_s = p

    ws_c.cell(row=idx, column=1, value=p_num).alignment = Alignment(horizontal="center", vertical="center")
    ws_c.cell(row=idx, column=2, value=p_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws_c.cell(row=idx, column=3, value=p_gpio).alignment = Alignment(horizontal="center", vertical="center")

    c_lig = ws_c.cell(row=idx, column=4, value=p_tipo_lig)
    c_lig.alignment = Alignment(horizontal="center", vertical="center")

    c_uso = ws_c.cell(row=idx, column=5, value=p_uso)
    c_uso.alignment = Alignment(horizontal="left", vertical="center")

    c_st = ws_c.cell(row=idx, column=6, value=p_st)
    c_st.alignment = Alignment(horizontal="center", vertical="center")

    c_obs = ws_c.cell(row=idx, column=7, value=p_obs)
    c_obs.alignment = Alignment(horizontal="left", vertical="center")

    for c in range(1, 8):
        cell_obj = ws_c.cell(row=idx, column=c)
        cell_obj.border = border_thin
        cell_obj.font = Font(name="Calibri", size=10, bold=(c==2))

    if fill_s and font_s:
        c_lig.fill = fill_s
        c_lig.font = font_s
        c_uso.fill = fill_s
        c_uso.font = font_s
        c_st.fill = fill_s
        c_st.font = font_s

auto_width(ws_c)


# ==============================================================================
# ABA 3: Arduino Nano (Chassi)
# ==============================================================================
ws_nano = wb.create_sheet(title="Arduino_Nano_Chassi")
ws_nano.views.sheetView[0].showGridLines = True

headers_nano = [
    "Pino Nano",
    "Silk no Nano",
    "Porta ATmega",
    "Tipo de Ligação Física",
    "Uso",
    "Status",
    "Observações"
]
style_header(ws_nano, 1, headers_nano)

pinos_nano = [
    ("D0", "RX0", "PD0", "Fio Externo (Chicote)", "Comandos <- ESP32 TX", "OCUPADO (Serial)", "Recebe comandos de movimento direto (3.3V TTL)", FILL_SERIAL, FONT_SERIAL),
    ("D1", "TX1", "PD1", "Livre / Sem Fio", "", "", "Livre (Descartado no chicote de 3 fios)", None, None),
    ("D2", "D2", "PD2", "Livre / Sem Fio", "", "", "Livre / Interrupção externa INT0", None, None),
    ("D3", "D3", "PD3", "Fio Externo (Chassi)", "PWMA (TB6612)", "OCUPADO (Motor)", "Velocidade dos 2 motores esquerdos (0-255)", FILL_CAM, FONT_CAM),
    ("D4", "D4", "PD4", "Fio Externo (Chassi)", "AIN1 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor esquerdo", FILL_CAM, FONT_CAM),
    ("D5", "D5", "PD5", "Fio Externo (Chassi)", "AIN2 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor esquerdo", FILL_CAM, FONT_CAM),
    ("D6", "D6", "PD6", "Fio Externo (Chassi)", "PWMB (TB6612)", "OCUPADO (Motor)", "Velocidade dos 2 motores direitos (0-255)", FILL_CAM, FONT_CAM),
    ("D7", "D7", "PD7", "Fio Externo (Chassi)", "BIN1 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor direito", FILL_CAM, FONT_CAM),
    ("D8", "D8", "PB0", "Fio Externo (Chassi)", "BIN2 (TB6612)", "OCUPADO (Motor)", "Sentido de rotação motor direito", FILL_CAM, FONT_CAM),
    ("D9", "D9", "PB1", "Fio Externo (Chassi)", "Servo Pan (SG90)", "OCUPADO (Servo)", "Giro horizontal da câmera (0° a 180°)", FILL_CAM, FONT_CAM),
    ("D10", "D10", "PB2", "Fio Externo (Chassi)", "Servo Tilt (SG90)", "OCUPADO (Servo)", "Inclinação vertical da câmera", FILL_CAM, FONT_CAM),
    ("D11", "D11", "PB3", "Fio Externo (Chassi)", "Barra 8 LEDs WS2812B", "OCUPADO (LEDs)", "Sinal de dados DIN para cores dos LEDs", FILL_SD, FONT_SD),
    ("D12", "D12", "PB4", "Fio Externo (Chassi)", "Buzzer Passivo 5V", "OCUPADO (Áudio)", "Sons, bips e alertas sonoros via tone()", FILL_SD, FONT_SD),
    ("D13", "D13", "PB5", "Trilha Interna PCB", "LED Onboard Heartbeat", "OCUPADO (Status)", "Zero fios externos. Pisca indicando funcionamento", FILL_PWR, FONT_PWR),
    ("A0", "A0", "PC0", "Fio Externo (Chassi)", "Leitura Bateria Li-Ion", "OCUPADO (Bateria)", "Divisor resistivo 10k/4.7k (8.4V max = 2.68V)", FILL_CAM, FONT_CAM),
    ("A1", "A1", "PC1", "Livre / Sem Fio", "", "", "Livre para sensor", None, None),
    ("A2", "A2", "PC2", "Livre / Sem Fio", "", "", "Livre para sensor", None, None),
    ("A3", "A3", "PC3", "Livre / Sem Fio", "", "", "Livre para sensor", None, None),
    ("A4", "A4", "PC4", "Livre / Sem Fio", "", "", "Livre / Barramento I2C SDA", None, None),
    ("A5", "A5", "PC5", "Livre / Sem Fio", "", "", "Livre / Barramento I2C Clock", None, None),
    ("A6", "A6", "ADC6", "Livre / Sem Fio", "", "", "Livre para leitura analógica", None, None),
    ("A7", "A7", "ADC7", "Livre / Sem Fio", "", "", "Livre para leitura analógica", None, None),
    ("5V", "5V", "-", "Fio Externo (Chassi)", "Entrada 5.0V (Step-Down)", "OCUPADO (Energia)", "Alimenta o Nano direto pelo barramento 5V", FILL_PWR, FONT_PWR),
    ("GND", "GND", "-", "Fio Externo (Chassi)", "GND Comum", "OCUPADO (Terra)", "Referência de terra comum", FILL_PWR, FONT_PWR)
]

for idx_n, pn in enumerate(pinos_nano, 2):
    ws_nano.row_dimensions[idx_n].height = 20
    n_num, n_silk, n_port, n_tipo_lig, n_uso, n_st, n_obs, fill_sn, font_sn = pn

    ws_nano.cell(row=idx_n, column=1, value=n_num).alignment = Alignment(horizontal="center", vertical="center")
    ws_nano.cell(row=idx_n, column=2, value=n_silk).alignment = Alignment(horizontal="center", vertical="center")
    ws_nano.cell(row=idx_n, column=3, value=n_port).alignment = Alignment(horizontal="center", vertical="center")

    cn_lig = ws_nano.cell(row=idx_n, column=4, value=n_tipo_lig)
    cn_lig.alignment = Alignment(horizontal="center", vertical="center")

    cn_uso = ws_nano.cell(row=idx_n, column=5, value=n_uso)
    cn_uso.alignment = Alignment(horizontal="left", vertical="center")

    cn_st = ws_nano.cell(row=idx_n, column=6, value=n_st)
    cn_st.alignment = Alignment(horizontal="center", vertical="center")

    cn_obs = ws_nano.cell(row=idx_n, column=7, value=n_obs)
    cn_obs.alignment = Alignment(horizontal="left", vertical="center")

    for c in range(1, 8):
        cell_obj = ws_nano.cell(row=idx_n, column=c)
        cell_obj.border = border_thin
        cell_obj.font = Font(name="Calibri", size=10, bold=(c==2))

    if fill_sn and font_sn:
        cn_lig.fill = fill_sn
        cn_lig.font = font_sn
        cn_uso.fill = fill_sn
        cn_uso.font = font_sn
        cn_st.fill = fill_sn
        cn_st.font = font_sn

auto_width(ws_nano)

caminho = "/home/usuario/Documentos/rover/tabela_pinagem_esp32_nano.xlsx"
wb.save(caminho)
print(f"Planilha salva com sucesso com as 3 abas oficiais em: {caminho}")
