#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a planilha oficial de pinagem e arquitetura de comunicação do Rover ESP32 + Arduino Nano.
Arquivo gerado: tabela_pinagem_esp32_nano.xlsx
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# Remove sheet padrão
wb.remove(wb.active)

# Cores da Paleta de Design (Engenharia Moderna)
C_NAVY_DARK = "0F172A"      # Slate 900
C_NAVY_HEADER = "1E293B"    # Slate 800
C_BLUE_SECTION = "1E40AF"   # Blue 800
C_BLUE_LIGHT = "EFF6FF"     # Blue 50
C_BORDER = "CBD5E1"         # Slate 300
C_ZEBRA = "F8FAFC"          # Slate 50
C_WHITE = "FFFFFF"

# Cores de Status
FILL_OCUPADO = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")     # Red 100
FONT_OCUPADO = Font(name="Calibri", size=10, bold=True, color="991B1B")                     # Red 800

FILL_DISPONIVEL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")  # Green 100
FONT_DISPONIVEL = Font(name="Calibri", size=10, bold=True, color="166534")                  # Green 800

FILL_RESTRITO = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")    # Yellow 100
FONT_RESTRITO = Font(name="Calibri", size=10, bold=True, color="854D0E")                    # Yellow 800

FILL_ENERGIA = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")     # Blue 100
FONT_ENERGIA = Font(name="Calibri", size=10, bold=True, color="1E40AF")                     # Blue 800

border_thin = Border(
    left=Side(style='thin', color=C_BORDER),
    right=Side(style='thin', color=C_BORDER),
    top=Side(style='thin', color=C_BORDER),
    bottom=Side(style='thin', color=C_BORDER)
)

def format_cell(cell, font=None, fill=None, align=None, border=border_thin):
    if font: cell.font = font
    if fill: cell.fill = fill
    if align: cell.alignment = align
    if border: cell.border = border

def apply_header_style(ws, row_idx, headers, fill_color=C_NAVY_HEADER):
    header_fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_thin
    ws.row_dimensions[row_idx].height = 28

def create_title_banner(ws, title, subtitle, max_col=7):
    # Linha 1: Título Principal
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_col)
    title_cell = ws.cell(row=1, column=1, value=title)
    title_cell.font = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color=C_NAVY_DARK, end_color=C_NAVY_DARK, fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    # Linha 2: Subtítulo
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max_col)
    sub_cell = ws.cell(row=2, column=1, value=subtitle)
    sub_cell.font = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
    sub_cell.fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # Linha 3 vazia
    ws.row_dimensions[3].height = 10

def auto_fit_columns(ws, min_widths=None):
    if min_widths is None:
        min_widths = {}
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # Não medir linhas de título mescladas
            if cell.row in [1, 2]:
                continue
            if cell.value:
                lines = str(cell.value).split('\n')
                for l in lines:
                    if len(l) > max_len:
                        max_len = len(l)
        calc_width = max(max_len + 4, min_widths.get(col_letter, 12))
        ws.column_dimensions[col_letter].width = min(calc_width, 50)


# ==============================================================================
# ABA 1: ESP32 (Câmera & RX-TX)
# ==============================================================================
ws1 = wb.create_sheet(title="ESP32_Câmera_e_UART")
ws1.views.sheetView[0].showGridLines = True

create_title_banner(
    ws1,
    "MAPA DE PINOS - ESP32-CAM / ESP32-S3 (CÂMERA DVP & SERIAL RX/TX)",
    "Cabeça Móvel Pan/Tilt | Câmera consome 16 pinos DVP | UART0 (GPIO 1 TX) comanda o Arduino Nano via chicote",
    max_col=7
)

headers_esp = [
    "Pino (GPIO)",
    "Função Interna / Hardware",
    "Status na Placa",
    "Uso no Rover 4WD",
    "Nível Lógico",
    "Descrição Técnica & Barramento",
    "Cuidados de Boot & Strapping Pins"
]
apply_header_style(ws1, 4, headers_esp)

dados_esp = [
    ("GPIO 0", "XCLK Câmera (20 MHz)", "OCUPADO", "Não Conectar", "3.3V", "Clock mestre do sensor OV2640/OV5640.", "Pino de BOOT (Strapping). Deve estar em nível HIGH para inicialização normal do chip."),
    ("GPIO 1", "U0TXD (UART0 TX)", "DISPONÍVEL", "SIM -> Ligado no RX do Nano", "3.3V", "Transmissão Serial de Comandos. Envia pacotes de velocidade e ângulos ao Nano.", "Livre para transmissão. Conecta diretamente no pino D0 (RX) do Arduino Nano."),
    ("GPIO 2", "HS2_DATA0 / LED Onboard", "RESTRITO", "Não Conectar", "3.3V", "Linha de dados MicroSD e LED onboard da placa.", "Pino de Strapping. Se puxado para HIGH no boot, pode impedir gravação de firmware."),
    ("GPIO 3", "U0RXD (UART0 RX)", "DISPONÍVEL", "SIM (Opcional) <- Nano TX", "3.3V", "Recepção Serial de Telemetria do Nano (nível da bateria, sensores).", "ATENÇÃO: NUNCA conectar 5V direto! Usar divisor resistivo (1k/2k) vindo do TX do Nano."),
    ("GPIO 4", "Flash LED / HS2_DATA1", "OCUPADO", "Não Conectar", "3.3V", "Acionamento do transistor do LED Flash de alta potência.", "Pode acender de forma indesejada no boot. Mantido isolado para evitar aquecimento."),
    ("GPIO 5", "VSYNC Câmera", "OCUPADO", "Não Conectar", "3.3V", "Sincronismo Vertical de Quadro (DVP) da câmera.", "Uso exclusivo do driver de captura de vídeo do ESP32."),
    ("GPIO 12", "HS2_DATA2", "OCUPADO", "Não Conectar", "3.3V", "Barramento MicroSD Data 2.", "Strapping Pin (tensão do regulador Flash). Manter desconectado."),
    ("GPIO 13", "HS2_DATA3", "OCUPADO", "Não Conectar", "3.3V", "Barramento MicroSD Data 3.", "Uso exclusivo do leitor de cartão SD."),
    ("GPIO 14", "HS2_CLK", "OCUPADO", "Não Conectar", "3.3V", "Clock do Barramento MicroSD.", "Uso exclusivo do leitor de cartão SD."),
    ("GPIO 15", "HS2_CMD", "OCUPADO", "Não Conectar", "3.3V", "Comando do Barramento MicroSD.", "Pino de Strapping de depuração JTAG. Manter desconectado."),
    ("GPIO 16", "U2RXD / CS", "DISPONÍVEL", "Livre / Reserva", "3.3V", "Pino de I/O de uso geral exposto no header lateral da placa.", "Totalmente livre. Pode ser utilizado para botão ou sensor adicional na cabeça móvel."),
    ("GPIO 18", "Y3 / D1 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D1 do barramento paralelo DVP da câmera.", "Uso exclusivo do barramento paralelo de vídeo."),
    ("GPIO 19", "Y4 / D2 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D2 do barramento paralelo DVP da câmera.", "Uso exclusivo do barramento paralelo de vídeo."),
    ("GPIO 21", "Y5 / D3 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D3 do barramento paralelo DVP da câmera.", "Uso exclusivo do barramento paralelo de vídeo."),
    ("GPIO 22", "PCLK Câmera", "OCUPADO", "Não Conectar", "3.3V", "Pixel Clock (sincronismo de cada byte de pixel).", "Uso exclusivo do barramento paralelo de vídeo."),
    ("GPIO 23", "HREF Câmera", "OCUPADO", "Não Conectar", "3.3V", "Horizontal Reference (sincronismo de linha de vídeo).", "Uso exclusivo do barramento paralelo de vídeo."),
    ("GPIO 25", "Y2 / D0 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D0 do barramento paralelo DVP da câmera.", "Uso exclusivo do barramento paralelo de vídeo."),
    ("GPIO 26", "SIOD / SDA Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados do barramento SCCB / I2C de controle da câmera.", "Configura ganho, exposição, resolução e modo de cor do sensor."),
    ("GPIO 27", "SIOC / SCL Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Clock do barramento SCCB / I2C de controle da câmera.", "Clock de configuração dos registradores do sensor de imagem."),
    ("GPIO 32", "PWDN Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Power Down (habilitação de energia) da câmera.", "Controlado pelo firmware para ligar/desligar o sensor OV2640/OV5640."),
    ("GPIO 34", "Y8 / D6 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D6 do barramento paralelo DVP (somente entrada).", "Sem resistores de pull-up/pull-down internos configuráveis."),
    ("GPIO 35", "Y9 / D7 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D7 do barramento paralelo DVP (somente entrada).", "Sem resistores de pull-up/pull-down internos configuráveis."),
    ("GPIO 36", "Y6 / D4 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D4 do barramento paralelo DVP (somente entrada).", "Sem resistores de pull-up/pull-down internos configuráveis."),
    ("GPIO 39", "Y7 / D5 Câmera", "OCUPADO", "Não Conectar", "3.3V", "Linha de Dados D5 do barramento paralelo DVP (somente entrada).", "Sem resistores de pull-up/pull-down internos configuráveis."),
    ("5V (VCC)", "Alimentação Principal", "ENERGIA", "SIM -> Do Step-Down 5A", "5.0V", "Entrada de energia para o regulador linear interno AMS1117 (3.3V).", "Vem direto da saída do regulador Mini 560 (5V / até 5A). Suporta picos de Wi-Fi."),
    ("3V3 (Saída)", "Alimentação Auxiliar", "ENERGIA", "Não Conectar", "3.3V", "Saída regulada de 3.3V da placa (corrente máxima ~50mA).", "NUNCA alimentar servos, motores ou fitas de LED neste pino! Queima o regulador."),
    ("GND", "Referência de Terra", "ENERGIA", "SIM -> Terra Comum", "0V", "GND de referência comum de todo o sistema.", "Conectar com o GND do Arduino Nano, Step-Down, Bateria e TB6612FNG.")
]

font_body = Font(name="Calibri", size=10, color="000000")
fill_zebra = PatternFill(start_color=C_ZEBRA, end_color=C_ZEBRA, fill_type="solid")
fill_white = PatternFill(start_color=C_WHITE, end_color=C_WHITE, fill_type="solid")

for row_idx, row_data in enumerate(dados_esp, 5):
    status = row_data[2]
    # Escolha de cor por status
    if status == "OCUPADO":
        s_fill, s_font = FILL_OCUPADO, FONT_OCUPADO
    elif status == "DISPONÍVEL":
        s_fill, s_font = FILL_DISPONIVEL, FONT_DISPONIVEL
    elif status == "RESTRITO":
        s_fill, s_font = FILL_RESTRITO, FONT_RESTRITO
    else:
        s_fill, s_font = FILL_ENERGIA, FONT_ENERGIA
        
    bg_fill = fill_zebra if row_idx % 2 == 0 else fill_white
    ws1.row_dimensions[row_idx].height = 24
    
    for col_idx, val in enumerate(row_data, 1):
        cell = ws1.cell(row=row_idx, column=col_idx, value=val)
        cell.border = border_thin
        
        if col_idx == 3: # Coluna Status com Badge
            cell.fill = s_fill
            cell.font = s_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx in [1, 5]:
            cell.fill = bg_fill
            cell.font = Font(name="Calibri", size=10, bold=(col_idx==1))
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.fill = bg_fill
            cell.font = font_body
            cell.alignment = Alignment(horizontal="left", vertical="center")

# Congela painéis no cabeçalho
ws1.freeze_panes = "A5"
auto_fit_columns(ws1, min_widths={'A': 14, 'B': 26, 'C': 16, 'D': 30, 'E': 14, 'F': 42, 'G': 45})


# ==============================================================================
# ABA 2: Arduino Nano (Controle & Periféricos)
# ==============================================================================
ws2 = wb.create_sheet(title="Arduino_Nano_Controle")
ws2.views.sheetView[0].showGridLines = True

create_title_banner(
    ws2,
    "MAPA DE PINOS - ARDUINO NANO V3 (CO-PROCESSADOR DE TRAÇÃO E PERIFÉRICOS)",
    "Fixo no chassi (5V nativo) | Controla TB6612FNG (Motores JGA-050), 2 Servos SG90, 8 LEDs WS2812B, Buzzer e lê Bateria 7.4V",
    max_col=7
)

headers_nano = [
    "Pino Nano",
    "Tipo de I/O",
    "Nível Lógico",
    "Conexão no Rover (Módulo / Periférico)",
    "Função Detalhada no Robô",
    "Valores / Faixa Operacional",
    "Observações Técnicas de Projeto"
]
apply_header_style(ws2, 4, headers_nano, fill_color="1E3A8A")

dados_nano = [
    ("D0 (RX)", "Digital / UART RX", "5V TTL (3.3V comp.)", "ESP32 GPIO 1 (TX)", "Recepção de Comandos de Movimento e Câmera", "115200 bps", "Compatibilidade direta: Nível HIGH 3.3V do ESP32 é interpretado perfeitamente como HIGH pelo ATmega328P (Vih >= 3.0V)."),
    ("D1 (TX)", "Digital / UART TX", "5V TTL", "ESP32 GPIO 3 (RX) via Divisor", "Envio de Telemetria ao ESP32 (Bateria, Status)", "115200 bps", "CUIDADO: EXIGE DIVISOR DE TENSÃO (1k + 2k) para abaixar de 5V para 3.3V antes de entrar no ESP32!"),
    ("D2", "Digital / INT0", "5V TTL", "Livre / Reserva", "Interrupção Externa / Sensor de Toque", "HIGH / LOW", "Reserva para sensor de colisão (fim de curso), botão de calibração ou encoder de roda futuro."),
    ("D3 (PWM)", "Digital / PWM (Timer 2)", "5V TTL", "TB6612FNG -> Pino PWMA", "Velocidade dos Motores Esquerdos (JGA-050)", "PWM 0 a 255 (0% a 100%)", "Comanda os dois motores do lado esquerdo (dianteiro + traseiro ligados em paralelo no canal A)."),
    ("D4", "Digital Output", "5V TTL", "TB6612FNG -> Pino AIN1", "Sentido de Rotação Motor Esquerdo", "HIGH / LOW", "Tabela Verdade: AIN1=1, AIN2=0 (Frente) | AIN1=0, AIN2=1 (Ré) | AIN1=0, AIN2=0 (Parar suave)."),
    ("D5 (PWM)", "Digital / PWM (Timer 0)", "5V TTL", "TB6612FNG -> Pino AIN2", "Sentido de Rotação Motor Esquerdo", "HIGH / LOW", "Utilizado em conjunto com AIN1 para definição do sentido de rotação."),
    ("D6 (PWM)", "Digital / PWM (Timer 0)", "5V TTL", "TB6612FNG -> Pino PWMB", "Velocidade dos Motores Direitos (JGA-050)", "PWM 0 a 255 (0% a 100%)", "Comanda os dois motores do lado direito (dianteiro + traseiro ligados em paralelo no canal B)."),
    ("D7", "Digital Output", "5V TTL", "TB6612FNG -> Pino BIN1", "Sentido de Rotação Motor Direito", "HIGH / LOW", "Tabela Verdade: BIN1=1, BIN2=0 (Frente) | BIN1=0, BIN2=1 (Ré) | BIN1=0, BIN2=0 (Parar suave)."),
    ("D8", "Digital Output", "5V TTL", "TB6612FNG -> Pino BIN2", "Sentido de Rotação Motor Direito", "HIGH / LOW", "Utilizado em conjunto com BIN1 para definição do sentido de rotação."),
    ("D9 (PWM)", "Digital / PWM (Timer 1)", "5V TTL", "Sinal (Amarelo) Servo SG90 Pan", "Movimento Horizontal da Câmera (Pan)", "0° a 180° (Centro: 90°)", "Biblioteca Servo.h utiliza Timer 1 (16 bits), proporcionando resolução angular suave sem jitter."),
    ("D10 (PWM)", "Digital / PWM (Timer 1)", "5V TTL", "Sinal (Amarelo) Servo SG90 Tilt", "Movimento Vertical da Câmera (Tilt)", "50° a 130° (Centro: 90°)", "Ângulo limitado por software para evitar que a câmera colida fisicamente contra a estrutura do chassi."),
    ("D11 (PWM)", "Digital Output", "5V TTL", "Fita 8 LEDs WS2812B -> Pino DIN", "Controle de Cor Individual dos 8 LEDs RGB", "Protocolo 800 kHz (NeoPixel)", "Farol tático dianteiro, setas de conversão, luz de freio e sinalizador de status da bateria."),
    ("D12", "Digital Output", "5V TTL", "Buzzer Passivo 5V -> Pino de Sinal", "Sons de Alerta, Buzina e Bip de Boot", "Frequência em Hz via tone()", "Bip curto ao conectar Wi-Fi; alarme sonoro intermitente caso a bateria caia abaixo de 6.6V."),
    ("D13", "Digital Output", "5V TTL", "LED Onboard do Arduino Nano", "Heartbeat / Indicador de Vida do Sistema", "Pisca a cada 500ms", "Confirma visualmente que o loop principal do microcontrolador está rodando sem travamento."),
    ("A0", "Analógico Input", "0 a 5V", "Divisor Resistivo da Bateria Li-Ion", "Leitura do Nível de Carga da Bateria 7.4V", "ADC 10-bit (0 a 1023)", "Divisor de Tensão: R1 = 10 kΩ, R2 = 4.7 kΩ. Bateria 8.4V cheia gera 2.68V no pino A0 (totalmente seguro)."),
    ("A1", "Analógico / Digital", "0 a 5V", "Livre / Reserva", "Entrada Analógica ou Digital Futura", "ADC / I/O Geral", "Pode ser utilizado para sensor ultrassônico HC-SR04 (Pino Trigger)."),
    ("A2", "Analógico / Digital", "0 a 5V", "Livre / Reserva", "Entrada Analógica ou Digital Futura", "ADC / I/O Geral", "Pode ser utilizado para sensor ultrassônico HC-SR04 (Pino Echo)."),
    ("A3", "Analógico / Digital", "0 a 5V", "Livre / Reserva", "Entrada Analógica ou Digital Futura", "ADC / I/O Geral", "Reserva para sensor de linha infravermelho ou sensor de luminosidade LDR."),
    ("A4 (SDA)", "Analógico / I2C SDA", "5V TTL", "Livre / Barramento I2C", "Expansão de Sensores I2C", "I2C Data", "Permite adicionar facilmente IMU (acelerômetro/giroscópio MPU6050) ou display OLED 0.96 pol."),
    ("A5 (SCL)", "Analógico / I2C SCL", "5V TTL", "Livre / Barramento I2C", "Expansão de Sensores I2C", "I2C Clock", "Clock do barramento I2C para comunicação com periféricos inteligentes."),
    ("A6", "Analógico Input", "0 a 5V", "Livre / Reserva (Somente Analógico)", "Entrada de Sensor Analógico Auxiliar", "ADC 10-bit", "Pino exclusivo para leitura analógica do chip ATmega328P (não funciona como saída digital)."),
    ("A7", "Analógico Input", "0 a 5V", "Livre / Reserva (Somente Analógico)", "Entrada de Sensor Analógico Auxiliar", "ADC 10-bit", "Pino exclusivo para leitura analógica do chip ATmega328P (não funciona como saída digital)."),
    ("5V (Pino)", "Alimentação Lógica", "5.0V Regulado", "Saída Step-Down Mini 560 (5A)", "Alimentação do ATmega328P e Lógica", "5.0V Fixos", "Alimenta o Nano direto pelo pino 5V, evitando perdas e aquecimento do regulador linear onboard."),
    ("VIN", "Entrada Alta Tensão", "NÃO CONECTAR", "Desconectado", "-", "NÃO USAR! Alimentação direta em 5V via Step-Down é muito mais estável e eficiente."),
    ("GND", "Referência de Terra", "0V", "Barramento Central de Terra", "GND Comum de Potência e Lógica", "0V", "Unido ao GND da bateria, Step-Down, ESP32 e driver de motores.")
]

for row_idx, row_data in enumerate(dados_nano, 5):
    bg_fill = fill_zebra if row_idx % 2 == 0 else fill_white
    ws2.row_dimensions[row_idx].height = 24
    pino = row_data[0]
    
    # Destacar pinos em uso vs livres
    if "Livre" in row_data[3]:
        badge_fill, badge_font = FILL_DISPONIVEL, FONT_DISPONIVEL
    elif "ESP32" in row_data[3]:
        badge_fill, badge_font = FILL_ENERGIA, FONT_ENERGIA
    elif "NÃO" in row_data[3]:
        badge_fill, badge_font = FILL_RESTRITO, FONT_RESTRITO
    else:
        badge_fill, badge_font = FILL_DISPONIVEL, FONT_DISPONIVEL

    for col_idx, val in enumerate(row_data, 1):
        cell = ws2.cell(row=row_idx, column=col_idx, value=val)
        cell.border = border_thin
        
        if col_idx == 1:
            cell.fill = bg_fill
            cell.font = Font(name="Calibri", size=10, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx in [2, 3]:
            cell.fill = bg_fill
            cell.font = font_body
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx == 4:
            cell.fill = badge_fill
            cell.font = badge_font
            cell.alignment = Alignment(horizontal="left", vertical="center")
        else:
            cell.fill = bg_fill
            cell.font = font_body
            cell.alignment = Alignment(horizontal="left", vertical="center")

ws2.freeze_panes = "A5"
auto_fit_columns(ws2, min_widths={'A': 14, 'B': 24, 'C': 16, 'D': 34, 'E': 36, 'F': 24, 'G': 45})


# ==============================================================================
# ABA 3: Arquitetura Serial & Chicote de Interligação
# ==============================================================================
ws3 = wb.create_sheet(title="Interligação_RX_TX_e_Chicote")
ws3.views.sheetView[0].showGridLines = True

create_title_banner(
    ws3,
    "ARQUITETURA DE INTERLIGAÇÃO SERIAL (CHICOTE DE 4 FIOS & POTÊNCIA)",
    "Divisão Funcional: Cabeça Móvel (ESP32) vs Chassi Fixo (Nano + TB6612FNG + Servos + Sensores)",
    max_col=6
)

# SEÇÃO 1: Chicote de 4 Fios
ws3.merge_cells("A4:F4")
sec1_cell = ws3.cell(row=4, column=1, value="1. CHICOTE MÓVEL FLEXÍVEL (CABEÇA PAN/TILT <---> CHASSI)")
sec1_cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
sec1_cell.fill = PatternFill(start_color=C_BLUE_SECTION, end_color=C_BLUE_SECTION, fill_type="solid")
sec1_cell.alignment = Alignment(horizontal="left", vertical="center")
ws3.row_dimensions[4].height = 24

headers_s1 = ["Fio #", "Cor Sugerida", "Origem (Chassi)", "Destino (Cabeça ESP32)", "Nível de Sinal", "Função & Detalhes de Engenharia"]
apply_header_style(ws3, 5, headers_s1, fill_color="334155")

dados_s1 = [
    ("Fio 1", "Vermelho (26-28 AWG)", "Saída 5V do Step-Down Mini 560", "Pino 5V do ESP32", "5.0V DC (Potência)", "Alimenta o ESP32 através do regulador interno AMS1117 (3.3V). Corrente suporta picos de Wi-Fi (~300mA)."),
    ("Fio 2", "Preto (26-28 AWG)", "Barramento Central GND", "Pino GND do ESP32", "0V (Referência)", "Terra comum para fechamento do circuito de potência e referência do sinal de comunicação serial."),
    ("Fio 3", "Azul / Amarelo", "ESP32 GPIO 1 (U0TXD)", "Arduino Nano Pino D0 (RX)", "3.3V -> 5V TTL", "Comunicação Serial (ESP32 -> Nano). Transmite pacotes de direção, velocidade PWM e ângulos dos servos."),
    ("Fio 4", "Verde / Branco", "Arduino Nano Pino D1 (TX)", "ESP32 GPIO 3 (U0RXD)", "5V -> Divisor -> 3.3V", "Telemetria (Nano -> ESP32). Opcional. EXIGE DIVISOR DE TENSÃO (R1=1k, R2=2k) para proteção do ESP32.")
]

for row_idx, row_data in enumerate(dados_s1, 6):
    bg_fill = fill_zebra if row_idx % 2 == 0 else fill_white
    ws3.row_dimensions[row_idx].height = 24
    for col_idx, val in enumerate(row_data, 1):
        cell = ws3.cell(row=row_idx, column=col_idx, value=val)
        cell.border = border_thin
        cell.fill = bg_fill
        cell.font = Font(name="Calibri", size=10, bold=(col_idx==1))
        cell.alignment = Alignment(horizontal=("center" if col_idx in [1, 2, 5] else "left"), vertical="center")

# SEÇÃO 2: TB6612FNG
r_start = 11
ws3.merge_cells(f"A{r_start}:F{r_start}")
sec2_cell = ws3.cell(row=r_start, column=1, value="2. LIGAÇÃO DO DRIVER DUPLO MOSFET TB6612FNG NO CHASSI")
sec2_cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
sec2_cell.fill = PatternFill(start_color=C_BLUE_SECTION, end_color=C_BLUE_SECTION, fill_type="solid")
sec2_cell.alignment = Alignment(horizontal="left", vertical="center")
ws3.row_dimensions[r_start].height = 24

headers_s2 = ["Pino Driver", "Tipo", "Conectar Em", "Tensão / Nível", "Função de Controle", "Comportamento Operacional"]
apply_header_style(ws3, r_start+1, headers_s2, fill_color="334155")

dados_s2 = [
    ("VM", "Alimentação", "Positivo da Bateria 2S (+7.4V)", "6.0V a 8.4V", "Alimentação de Potência dos Motores", "Ligado após a Chave Geral Liga/Desliga KCD1. Fornece corrente pura aos 4 motores JGA-050."),
    ("VCC", "Alimentação", "Saída 5.0V do Step-Down", "5.0V DC", "Alimentação Lógica do Driver TB6612", "Alimenta os circuitos lógicos internos do chip MOSFET."),
    ("GND", "Referência", "GND Comum do Chassi", "0V", "Terra Comum Potência e Lógica", "Conectar aos pinos GND de alimentação e de sinal."),
    ("STBY", "Controle", "Pino 5V (ou Pino Digital do Nano)", "5.0V (HIGH)", "Habilitação (Standby) da Ponte H", "Quando em nível HIGH, o driver opera normalmente. Em LOW, desativa saídas para economizar energia."),
    ("PWMA", "Entrada PWM", "Arduino Nano Pino D3", "PWM (0-255)", "Velocidade Motor Esquerdo", "Ajusta velocidade via ciclo de trabalho (duty cycle) dos 2 motores esquerdos."),
    ("AIN1 / AIN2", "Entrada Digital", "Arduino Nano Pinos D4 e D5", "5V TTL (HIGH/LOW)", "Sentido Motor Esquerdo", "AIN1=1, AIN2=0: Frente | AIN1=0, AIN2=1: Ré | AIN1=0, AIN2=0: Ponto Morto | AIN1=1, AIN2=1: Freio."),
    ("PWMB", "Entrada PWM", "Arduino Nano Pino D6", "PWM (0-255)", "Velocidade Motor Direito", "Ajusta velocidade via ciclo de trabalho (duty cycle) dos 2 motores direitos."),
    ("BIN1 / BIN2", "Entrada Digital", "Arduino Nano Pinos D7 e D8", "5V TTL (HIGH/LOW)", "Sentido Motor Direito", "BIN1=1, BIN2=0: Frente | BIN1=0, BIN2=1: Ré | BIN1=0, BIN2=0: Ponto Morto | BIN1=1, BIN2=1: Freio."),
    ("AO1 / AO2", "Saída Potência", "2x Motores JGA-050 Esquerdos", "0V a 7.4V", "Saída Canal A (Motores Esquerdos)", "Ligar motor dianteiro e traseiro do lado esquerdo em paralelo."),
    ("BO1 / BO2", "Saída Potência", "2x Motores JGA-050 Direitos", "0V a 7.4V", "Saída Canal B (Motores Direitos)", "Ligar motor dianteiro e traseiro do lado direito em paralelo.")
]

for idx, row_data in enumerate(dados_s2, r_start+2):
    bg_fill = fill_zebra if idx % 2 == 0 else fill_white
    ws3.row_dimensions[idx].height = 24
    for col_idx, val in enumerate(row_data, 1):
        cell = ws3.cell(row=idx, column=col_idx, value=val)
        cell.border = border_thin
        cell.fill = bg_fill
        cell.font = Font(name="Calibri", size=10, bold=(col_idx==1))
        cell.alignment = Alignment(horizontal=("center" if col_idx in [1, 2, 4] else "left"), vertical="center")

# SEÇÃO 3: Divisor de Tensão do Monitor de Bateria
r_s3 = r_start + len(dados_s2) + 3
ws3.merge_cells(f"A{r_s3}:F{r_s3}")
sec3_cell = ws3.cell(row=r_s3, column=1, value="3. MONITOR DE TENSÃO DA BATERIA LI-ION 2S (DIVISOR RESISTIVO NO PINO A0 DO NANO)")
sec3_cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
sec3_cell.fill = PatternFill(start_color=C_BLUE_SECTION, end_color=C_BLUE_SECTION, fill_type="solid")
sec3_cell.alignment = Alignment(horizontal="left", vertical="center")
ws3.row_dimensions[r_s3].height = 24

headers_s3 = ["Parâmetro / Componente", "Valor", "Conexão Elétrica", "Tensão na Bateria", "Tensão no Pino A0", "Status / Ação do Firmware"]
apply_header_style(ws3, r_s3+1, headers_s3, fill_color="334155")

dados_s3 = [
    ("Resistor R1 (Superior)", "10 kΩ (1%)", "Entre Positivo da Bateria (+7.4V) e Pino A0", "-", "-", "Abaixa a impedância e protege a porta analógica."),
    ("Resistor R2 (Inferior)", "4.7 kΩ (1%)", "Entre Pino A0 do Nano e GND Comum", "-", "-", "Fórmula: V_A0 = V_bat * (R2 / (R1 + R2)) = V_bat * 0.3197."),
    ("Bateria 100% Carregada", "Pico Máximo", "Saída da Carga Completa (2S)", "8.40V", "2.68V (ADC ~549)", "Tensão perfeitamente segura para o ADC de 5.0V do Nano. LEDs em Verde."),
    ("Bateria Nominal", "Operação Normal", "Tensão Média de Trabalho", "7.40V", "2.36V (ADC ~484)", "Operação estável dos motores e reguladores. LEDs em Azul/Branco."),
    ("Bateria Limite de Alerta", "Alerta Amarelo", "Descarga moderada (~3.3V/célula)", "6.60V", "2.11V (ADC ~432)", "Acende LEDs frontais em Amarelo para indicar recarga próxima."),
    ("Bateria Corte Crítico", "CORTE CRÍTICO", "Bateria no limite mínimo (~3.0V/célula)", "6.00V", "1.91V (ADC ~392)", "PARADA IMEDIATA dos motores. Alarme sonoro contínuo no buzzer para proteger as células.")
]

for idx, row_data in enumerate(dados_s3, r_s3+2):
    bg_fill = fill_zebra if idx % 2 == 0 else fill_white
    ws3.row_dimensions[idx].height = 24
    for col_idx, val in enumerate(row_data, 1):
        cell = ws3.cell(row=idx, column=col_idx, value=val)
        cell.border = border_thin
        cell.fill = bg_fill
        cell.font = Font(name="Calibri", size=10, bold=(col_idx==1))
        cell.alignment = Alignment(horizontal=("center" if col_idx in [1, 2, 4, 5] else "left"), vertical="center")

auto_fit_columns(ws3, min_widths={'A': 16, 'B': 24, 'C': 32, 'D': 24, 'E': 22, 'F': 48})

# Salva arquivo
caminho_xlsx = "/home/usuario/Documentos/rover/tabela_pinagem_esp32_nano.xlsx"
wb.save(caminho_xlsx)
print(f"Planilha salva com sucesso em: {caminho_xlsx}")
