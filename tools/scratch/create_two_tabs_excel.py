#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a planilha simplificada em exatamente 2 abas com tabelas simples e diretas:
1. "Sem_Nano" (Tentativa de ligar tudo direto no ESP32 - mostrando pinos e conflitos)
2. "Com_Nano" (Arquitetura oficial com Arduino Nano - mostrando o ESP32 livre e chicote)
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
wb.remove(wb.active)  # Remove aba padrão

# Paleta Limpa e Funcional
C_NAVY = "1E293B"       # Slate 800 (Cabeçalho Principal)
C_HEADER = "334155"     # Slate 700
C_BORDER = "CBD5E1"     # Slate 300
C_ZEBRA = "F8FAFC"      # Slate 50
C_WHITE = "FFFFFF"

# Cores de Status
FILL_OK = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")     # Verde claro
FONT_OK = Font(name="Calibri", size=10, bold=True, color="166534")

FILL_WARN = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")   # Amarelo claro
FONT_WARN = Font(name="Calibri", size=10, bold=True, color="854D0E")

FILL_ERR = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")    # Vermelho claro
FONT_ERR = Font(name="Calibri", size=10, bold=True, color="991B1B")

FILL_PWR = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")    # Cinza energia
FONT_PWR = Font(name="Calibri", size=10, bold=True, color="334155")

border_thin = Border(
    left=Side(style='thin', color=C_BORDER),
    right=Side(style='thin', color=C_BORDER),
    top=Side(style='thin', color=C_BORDER),
    bottom=Side(style='thin', color=C_BORDER)
)

def apply_title(ws, title, subtitle):
    ws.merge_cells("A1:G1")
    t = ws.cell(row=1, column=1, value=title)
    t.font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    t.fill = PatternFill(start_color=C_NAVY, end_color=C_NAVY, fill_type="solid")
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:G2")
    s = ws.cell(row=2, column=1, value=subtitle)
    s.font = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
    s.fill = PatternFill(start_color=C_HEADER, end_color=C_HEADER, fill_type="solid")
    s.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 8

def apply_headers(ws, row, headers):
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=h)
        cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color=C_HEADER, end_color=C_HEADER, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_thin
    ws.row_dimensions[row].height = 24

def auto_width(ws):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            if cell.row in [1, 2]: continue
            if cell.value:
                for line in str(cell.value).split('\n'):
                    max_len = max(max_len, len(line))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)


# ==============================================================================
# ABA 1: SEM NANO (Tudo no ESP32)
# ==============================================================================
ws1 = wb.create_sheet(title="Sem_Nano")
ws1.views.sheetView[0].showGridLines = True

apply_title(
    ws1,
    "CENÁRIO 1: ESP32 SEM ARDUINO NANO (TENTATIVA DE CONTROLAR TUDO NA MESMA PLACA)",
    "Todos os 16 pinos expostos do ESP32. Mostra a falta de pinos livres e conflitos com a câmera/cartão."
)

headers_sem = [
    "Pino Físico",
    "Silk na Placa",
    "GPIO Nativo",
    "Tipo de Pino",
    "Tentativa de Ligação (Sem Nano)",
    "Status / Viabilidade",
    "Observações & Conflitos"
]
apply_headers(ws1, 4, headers_sem)

# Dados de todos os 16 pinos físicos expostos no ESP32-CAM
dados_sem_nano = [
    ("P01 (Header Esq)", "5V", "-", "Alimentação 5V", "Entrada 5V da Bateria / Step-Down", "ENERGIA", "Alimenta o regulador interno AMS1117 (3.3V) da placa"),
    ("P02 (Header Esq)", "GND", "-", "Terra", "GND Comum do Robô", "ENERGIA", "Referência de terra comum de potência e sinal"),
    ("P03 (Header Esq)", "IO12", "GPIO 12", "Digital I/O", "Motor Esq (PWMA TB6612)", "CONFLITO GRAVE", "Usado internamente pelo leitor MicroSD. Pino de boot de tensão (VDet)"),
    ("P04 (Header Esq)", "IO13", "GPIO 13", "Digital I/O", "Motor Esq (AIN1 TB6612)", "CONFLITO", "Usado internamente pelo leitor MicroSD (Data 3)"),
    ("P05 (Header Esq)", "IO15", "GPIO 15", "Digital I/O", "Motor Esq (AIN2 TB6612)", "CONFLITO", "Usado pelo leitor MicroSD (CMD) e pino de strapping JTAG"),
    ("P06 (Header Esq)", "IO14", "GPIO 14", "Digital I/O", "Motor Dir (PWMB TB6612)", "CONFLITO", "Usado pelo leitor MicroSD (Clock)"),
    ("P07 (Header Esq)", "IO2", "GPIO 2", "Digital I/O", "Motor Dir (BIN1 TB6612)", "CONFLITO GRAVE", "Conectado ao LED onboard. Pino de boot (se HIGH no boot impede gravação)"),
    ("P08 (Header Esq)", "IO4", "GPIO 4", "Digital I/O", "Motor Dir (BIN2 TB6612)", "CONFLITO", "Ligado ao transistor do LED Flash de alta potência (acende sozinho)"),
    ("P09 (Header Dir)", "3V3", "-", "Saída 3.3V", "NÃO CONECTAR", "ENERGIA", "Saída máxima fraca (~50mA). Não aguenta servos nem motores"),
    ("P10 (Header Dir)", "GND", "-", "Terra", "GND Comum", "ENERGIA", "Terra de referência"),
    ("P11 (Header Dir)", "IO16", "GPIO 16", "Digital I/O", "Servo Pan (SG90)", "DISPONÍVEL", "Único pino de I/O totalmente livre exposto no header"),
    ("P12 (Header Dir)", "IO0", "GPIO 0", "Digital / Boot", "Servo Tilt (SG90)", "RESTRITO", "Usado pelo clock mestre da câmera (20MHz) e pino de gravação de boot"),
    ("P13 (Header Dir)", "U0R", "GPIO 3", "Serial UART RX", "Fita 8 LEDs WS2812B (DIN)", "DISPONÍVEL COM CUIDADO", "Pino de recepção serial. Se usado para LED perde a porta serial/USB"),
    ("P14 (Header Dir)", "U0T", "GPIO 1", "Serial UART TX", "Buzzer Passivo 5V", "DISPONÍVEL COM CUIDADO", "Pino de transmissão serial. Apita a cada log/inicialização do ESP32"),
    ("P15 (Header Dir)", "GND", "-", "Terra", "GND Comum", "ENERGIA", "Terra de referência"),
    ("P16 (Header Dir)", "VCC", "-", "Alimentação", "Não Conectar", "ENERGIA", "Pino auxiliar de alimentação")
]

for idx, r_data in enumerate(dados_sem_nano, 5):
    ws1.row_dimensions[idx].height = 22
    status = r_data[5]
    if status == "DISPONÍVEL":
        fill_st, font_st = FILL_OK, FONT_OK
    elif "CONFLITO" in status:
        fill_st, font_st = FILL_ERR, FONT_ERR
    elif status == "RESTRITO" or "CUIDADO" in status:
        fill_st, font_st = FILL_WARN, FONT_WARN
    else:
        fill_st, font_st = FILL_PWR, FONT_PWR

    bg = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=C_WHITE, end_color=C_WHITE, fill_type="solid")

    for c_idx, val in enumerate(r_data, 1):
        cell = ws1.cell(row=idx, column=c_idx, value=val)
        cell.border = border_thin
        if c_idx == 6:
            cell.fill = fill_st
            cell.font = font_st
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c_idx in [1, 2, 3, 4]:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10, bold=(c_idx==2))
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")

# Linha resumo/diagnóstico
r_diag = len(dados_sem_nano) + 6
ws1.merge_cells(f"A{r_diag}:G{r_diag}")
diag = ws1.cell(row=r_diag, column=1, value="DIAGNÓSTICO: O ESP32 sozinho precisa de 11 pinos de controle (6 motores + 2 servos + LEDs + Buzzer + Bateria), mas só possui 3 pinos livres sem conflito com a câmera.")
diag.font = Font(name="Calibri", size=10, bold=True, color="991B1B")
diag.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
diag.alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[r_diag].height = 24

auto_width(ws1)


# ==============================================================================
# ABA 2: COM NANO (ESP32 + Arduino Nano via RX/TX)
# ==============================================================================
ws2 = wb.create_sheet(title="Com_Nano")
ws2.views.sheetView[0].showGridLines = True

apply_title(
    ws2,
    "CENÁRIO 2: ESP32 COM ARDUINO NANO (ARQUITETURA OFICIAL DIVIDIDA VIA SERIAL RX/TX)",
    "ESP32 na cabeça móvel (só vídeo e Wi-Fi) | Arduino Nano no chassi fixo (comanda motores, servos e periféricos)"
)

headers_com = [
    "Pino Físico",
    "Silk na Placa",
    "GPIO Nativo",
    "Tipo de Pino",
    "Ligação no Robô (Com Nano)",
    "Status no ESP32",
    "Observações Rápidas"
]
apply_headers(ws2, 4, headers_com)

dados_com_nano = [
    ("P01 (Header Esq)", "5V", "-", "Alimentação 5V", "FIO 1 DO CHICOTE: Entrada 5.0V (Step-Down 5A)", "EM USO", "Alimenta o ESP32 vindo do chassi pelo chicote móvel"),
    ("P02 (Header Esq)", "GND", "-", "Terra", "FIO 2 DO CHICOTE: GND Comum", "EM USO", "Terra comum de referência de energia e sinal"),
    ("P03 (Header Esq)", "IO12", "GPIO 12", "Digital I/O", "LIVRE (Reservado Câmera / MicroSD)", "LIVRE", "Sem fios pendurados, zero risco de falha de boot"),
    ("P04 (Header Esq)", "IO13", "GPIO 13", "Digital I/O", "LIVRE (Reservado Câmera / MicroSD)", "LIVRE", "Sem fios pendurados"),
    ("P05 (Header Esq)", "IO15", "GPIO 15", "Digital I/O", "LIVRE (Reservado Câmera / MicroSD)", "LIVRE", "Sem fios pendurados"),
    ("P06 (Header Esq)", "IO14", "GPIO 14", "Digital I/O", "LIVRE (Reservado Câmera / MicroSD)", "LIVRE", "Sem fios pendurados"),
    ("P07 (Header Esq)", "IO2", "GPIO 2", "Digital I/O", "LIVRE (LED onboard)", "LIVRE", "Sem fios pendurados"),
    ("P08 (Header Esq)", "IO4", "GPIO 4", "Digital I/O", "LIVRE (Flash LED)", "LIVRE", "Sem fios pendurados"),
    ("P09 (Header Dir)", "3V3", "-", "Saída 3.3V", "NÃO CONECTAR", "LIVRE", "Deixar desconectado"),
    ("P10 (Header Dir)", "GND", "-", "Terra", "LIVRE (GND Interno)", "LIVRE", "Disponível se precisar de terra auxiliar"),
    ("P11 (Header Dir)", "IO16", "GPIO 16", "Digital I/O", "LIVRE / RESERVA", "LIVRE", "Pino totalmente livre para sensor ou expansão futura"),
    ("P12 (Header Dir)", "IO0", "GPIO 0", "Digital / Boot", "LIVRE (Reservado Câmera / Boot)", "LIVRE", "Usado apenas para gravação de firmware"),
    ("P13 (Header Dir)", "U0R", "GPIO 3", "Serial UART RX", "FIO 4 DO CHICOTE: RX0 <- TX Nano", "EM USO (OPCIONAL)", "Recebe telemetria do Nano (bateria/sensores via divisor 1k/2k)"),
    ("P14 (Header Dir)", "U0T", "GPIO 1", "Serial UART TX", "FIO 3 DO CHICOTE: TX0 -> RX Nano", "EM USO", "Transmite comandos de velocidade e servos ao Nano (direto 3.3V)"),
    ("P15 (Header Dir)", "GND", "-", "Terra", "LIVRE", "LIVRE", "Deixar desconectado"),
    ("P16 (Header Dir)", "VCC", "-", "Alimentação", "LIVRE", "LIVRE", "Deixar desconectado")
]

for idx, r_data in enumerate(dados_com_nano, 5):
    ws2.row_dimensions[idx].height = 22
    status = r_data[5]
    if status == "EM USO":
        fill_st, font_st = FILL_OK, FONT_OK
    elif "OPCIONAL" in status:
        fill_st, font_st = FILL_WARN, FONT_WARN
    else:
        fill_st, font_st = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid"), Font(name="Calibri", size=10, color="64748B")

    bg = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=C_WHITE, end_color=C_WHITE, fill_type="solid")

    for c_idx, val in enumerate(r_data, 1):
        cell = ws2.cell(row=idx, column=c_idx, value=val)
        cell.border = border_thin
        if c_idx == 6:
            cell.fill = fill_st
            cell.font = font_st
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c_idx in [1, 2, 3, 4]:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10, bold=(c_idx==2))
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")

# Subtabela: Onde ficaram os periféricos no Arduino Nano
r_nano_sec = len(dados_com_nano) + 7
ws2.merge_cells(f"A{r_nano_sec}:G{r_nano_sec}")
sec_n = ws2.cell(row=r_nano_sec, column=1, value="DISTRIBUIÇÃO DOS COMPONENTES NO ARDUINO NANO (CHASSI FIXO)")
sec_n.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
sec_n.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
sec_n.alignment = Alignment(horizontal="left", vertical="center")
ws2.row_dimensions[r_nano_sec].height = 24

headers_nano_sub = [
    "Componente no Chassi",
    "Pino no Componente",
    "Pino no Arduino Nano",
    "Tipo de Sinal",
    "Função no Robô",
    "Status",
    "Vantagem em Relação ao ESP32 Sozinho"
]
apply_headers(ws2, r_nano_sec + 1, headers_nano_sub)

dados_nano_alocacao = [
    ("Comunicação Serial", "TX do ESP32", "Pino D0 (RX)", "Serial 115200 bps", "Recebe comandos de movimento e servos", "OK", "3.3V do ESP32 é 100% compatível com a entrada TTL do Nano"),
    ("Comunicação Serial", "RX do ESP32", "Pino D1 (TX)", "Serial 115200 bps", "Envia nível de bateria e status de volta", "OK", "Basta divisor 1k/2k para rebaixar 5V para 3.3V"),
    ("Ponte H TB6612FNG", "PWMA (Velocidade Esq)", "Pino D3 (PWM)", "PWM Timer 2 (0-255)", "Velocidade dos 2 motores esquerdos", "OK", "PWM nativo do Nano sem disputa com o timer da câmera"),
    ("Ponte H TB6612FNG", "AIN1 / AIN2 (Sentido Esq)", "Pinos D4 e D5", "Digital Output", "Sentido de rotação esquerdo", "OK", "Pinos 5V nativos sem risco de boot"),
    ("Ponte H TB6612FNG", "PWMB (Velocidade Dir)", "Pino D6 (PWM)", "PWM Timer 0 (0-255)", "Velocidade dos 2 motores direitos", "OK", "PWM nativo sem disputa"),
    ("Ponte H TB6612FNG", "BIN1 / BIN2 (Sentido Dir)", "Pinos D7 e D8", "Digital Output", "Sentido de rotação direito", "OK", "Pinos 5V nativos"),
    ("Micro Servo SG90 Pan", "Sinal Amarelo", "Pino D9 (PWM)", "PWM Timer 1 (16-bit)", "Giro horizontal da câmera (0° a 180°)", "OK", "Timer 1 garante giro estável sem tremedeira (jitter)"),
    ("Micro Servo SG90 Tilt", "Sinal Amarelo", "Pino D10 (PWM)", "PWM Timer 1 (16-bit)", "Inclinação vertical da câmera", "OK", "Timer 1 garante giro estável"),
    ("Barra 8 LEDs WS2812B", "DIN (Dados)", "Pino D11 (MOSI)", "Digital 800 kHz", "Farol dianteiro, setas e alertas", "OK", "Biblioteca NeoPixel roda sem travar o Wi-Fi"),
    ("Buzzer Passivo 5V", "Sinal", "Pino D12", "Frequência via tone()", "Buzina, bips e alarme de bateria", "OK", "Não afeta o clock da CPU"),
    ("Monitor de Bateria", "Divisor 10k / 4.7k", "Pino A0 (Analógico)", "ADC 10-bit (0 a 5V)", "Lê tensão real da bateria 7.4V", "OK", "Leitura analógica limpa (8.4V vira 2.68V no ADC)"),
    ("Pinos Livres no Nano", "Sensores Extras", "Pinos D2, A1 a A7", "Digital / Analógico", "Livres para ultrassom, linha ou I2C", "LIVRE", "8 pinos sobrando para melhorias futuras")
]

for idx, r_data in enumerate(dados_nano_alocacao, r_nano_sec + 2):
    ws2.row_dimensions[idx].height = 22
    bg = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=C_WHITE, end_color=C_WHITE, fill_type="solid")
    
    for c_idx, val in enumerate(r_data, 1):
        cell = ws2.cell(row=idx, column=c_idx, value=val)
        cell.border = border_thin
        if c_idx == 6:
            cell.fill = FILL_OK
            cell.font = FONT_OK
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c_idx in [1, 2, 3, 4]:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10, bold=(c_idx==1))
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.fill = bg
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")

auto_width(ws2)

# Salva arquivo
caminho = "/home/usuario/Documentos/rover/tabela_pinagem_esp32_nano.xlsx"
wb.save(caminho)
print(f"Planilha salva com sucesso com exatamente 2 abas em: {caminho}")
