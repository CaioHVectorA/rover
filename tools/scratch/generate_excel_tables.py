import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color Palette
HEADER_BG = "1E293B"      # Dark Slate
HEADER_FG = "FFFFFF"      # White

FILL_EXTERNAL = "DCFCE7"  # Soft Light Green (Fio Externo)
FONT_EXTERNAL = "166534"  # Dark Green text

FILL_INTERNAL = "F1F5F9"  # Soft Slate/Gray (Interno)
FONT_INTERNAL = "475569"  # Slate text

FILL_POWER = "FEF3C7"     # Soft Amber (Energia / GND)
FONT_POWER = "92400E"     # Dark Amber text

FILL_FREE = "FFFFFF"      # Pure White (Livre)
FONT_FREE = "000000"

BORDER_GRAY = "CBD5E1"
thin_side = Side(border_style="thin", color=BORDER_GRAY)
border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

headers = [
    "Pino Físico",
    "Silk na Placa",
    "GPIO Nativo",
    "Ligação",
    "Uso",
    "Suporta PWM?",
    "ADC (Analógico)",
    "Nível Lógico",
    "Boot / Strapping",
    "Observações"
]

def style_sheet(ws, data_rows):
    # Set headers in row 1
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(name="Calibri", size=11, bold=True, color=HEADER_FG)
        cell.fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_all
    ws.row_dimensions[1].height = 28

    # Populate rows
    for row_idx, row_data in enumerate(data_rows, 2):
        ws.row_dimensions[row_idx].height = 22
        ligacao = row_data[3]
        uso = row_data[4]

        # Determine styling based on type of connection
        if ligacao == "Fio Externo":
            if "Alimentação" in str(uso) or "GND" in str(uso) or "5V" in str(uso) or "3V3" in str(uso):
                row_fill = PatternFill(start_color=FILL_POWER, end_color=FILL_POWER, fill_type="solid")
                text_color = FONT_POWER
            else:
                row_fill = PatternFill(start_color=FILL_EXTERNAL, end_color=FILL_EXTERNAL, fill_type="solid")
                text_color = FONT_EXTERNAL
        elif ligacao == "Interno":
            row_fill = PatternFill(start_color=FILL_INTERNAL, end_color=FILL_INTERNAL, fill_type="solid")
            text_color = FONT_INTERNAL
        else:
            # Livre (em branco)
            row_fill = PatternFill(start_color=FILL_FREE, end_color=FILL_FREE, fill_type="solid")
            text_color = FONT_FREE

        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = border_all
            cell.font = Font(name="Calibri", size=10, color=text_color if ligacao else "000000", bold=(col_idx==1 or col_idx==2))
            
            # Alignments
            if col_idx in [1, 2, 3, 4, 6, 7, 8, 9]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

            # Apply fill
            if ligacao:
                cell.fill = row_fill
            else:
                cell.fill = PatternFill(fill_type=None)

    # Auto-fit columns with safety margins
    col_widths = {
        1: 15, # Pino Físico
        2: 15, # Silk na Placa
        3: 15, # GPIO Nativo
        4: 16, # Ligação
        5: 32, # Uso
        6: 18, # Suporta PWM?
        7: 24, # ADC (Analógico)
        8: 15, # Nível Lógico
        9: 22, # Boot / Strapping
        10: 30 # Observações (vazia para o usuário)
    }
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.freeze_panes = "A2"


# ==============================================================================
# 1. ABA: S3_CAM_Sem_Nano (ESP32-S3 controlando tudo sozinho)
# ==============================================================================
ws_s3_single = wb.create_sheet(title="S3_CAM_Sem_Nano")
s3_single_data = [
    # Header J1 (Esquerdo)
    ["J1-01 (Esq)", "3V3", "-", "Interno", "Saída Regulada 3.3V", "Não", "Não", "3.3V", "Normal", None],
    ["J1-02 (Esq)", "GND", "-", "Fio Externo", "GND Comum (Chassi e Sensores)", "Não", "Não", "0V (GND)", "Normal", None],
    ["J1-03 (Esq)", "IO1", "GPIO 1", "Fio Externo", "Leitura Bateria 2S (Divisor 100k/33k)", "Sim (LEDC/MCPWM)", "ADC1_CH0 (Lê c/ Wi-Fi)", "3.3V", "Touch 1", None],
    ["J1-04 (Esq)", "IO2", "GPIO 2", "Fio Externo", "LEDs WS2812B (Sinal DIN)", "Sim (LEDC/MCPWM)", "ADC1_CH1 (Lê c/ Wi-Fi)", "3.3V", "Touch 2", None],
    ["J1-05 (Esq)", "IO3", "GPIO 3", "Fio Externo", "Servo Tilt (PWM 50Hz)", "Sim (LEDC/MCPWM)", "ADC1_CH2 (Lê c/ Wi-Fi)", "3.3V", "JTAG / Touch 3", None],
    ["J1-06 (Esq)", "IO41", "GPIO 41", "Fio Externo", "Motor Esq AIN1 (TB6612 PWM)", "Sim (LEDC/MCPWM)", "Não", "3.3V", "Normal", None],
    ["J1-07 (Esq)", "IO42", "GPIO 42", "Fio Externo", "Motor Esq AIN2 (TB6612 PWM)", "Sim (LEDC/MCPWM)", "Não", "3.3V", "Normal", None],
    ["J1-08 (Esq)", "TX (U0T)", "GPIO 43", "Fio Externo", "Motor Dir BIN1 (TB6612 PWM)", "Sim (LEDC/MCPWM)", "Não", "3.3V", "U0TXD", None],
    ["J1-09 (Esq)", "RX (U0R)", "GPIO 44", "Fio Externo", "Motor Dir BIN2 (TB6612 PWM)", "Sim (LEDC/MCPWM)", "Não", "3.3V", "U0RXD", None],
    ["J1-10 (Esq)", "IO19", "GPIO 19", "Interno", "USB-C Nativo (D-)", "Sim (LEDC/MCPWM)", "ADC2_CH8", "3.3V", "USB D-", None],
    ["J1-11 (Esq)", "IO20", "GPIO 20", "Interno", "USB-C Nativo (D+)", "Sim (LEDC/MCPWM)", "ADC2_CH9", "3.3V", "USB D+", None],
    ["J1-12 (Esq)", "IO21", "GPIO 21", "Fio Externo", "Servo Pan (PWM 50Hz)", "Sim (LEDC/MCPWM)", "Não", "3.3V", "Normal", None],
    # Header J2 (Direito)
    ["J2-01 (Dir)", "5V", "-", "Fio Externo", "Alimentação 5.0V (Vem do Mini 560)", "Não", "Não", "5.0V", "Normal", None],
    ["J2-02 (Dir)", "GND", "-", "Interno", "GND Auxiliar Onboard", "Não", "Não", "0V (GND)", "Normal", None],
    ["J2-03 (Dir)", "IO0", "GPIO 0", "Interno", "Botão BOOT Onboard", "Sim (LEDC/MCPWM)", "Não", "3.3V", "Boot (Pull-up)", None],
    ["J2-04 (Dir)", "IO4", "GPIO 4", "Interno", "Câmera OV5640 (SIOD / SDA)", "Sim (LEDC/MCPWM)", "ADC1_CH3", "3.3V", "I2C Câmera", None],
    ["J2-05 (Dir)", "IO5", "GPIO 5", "Interno", "Câmera OV5640 (SIOC / SCL)", "Sim (LEDC/MCPWM)", "ADC1_CH4", "3.3V", "I2C Câmera", None],
    ["J2-06 (Dir)", "IO6", "GPIO 6", "Interno", "Câmera OV5640 (VSYNC)", "Sim (LEDC/MCPWM)", "ADC1_CH5", "3.3V", "Sinc Câmera", None],
    ["J2-07 (Dir)", "IO7", "GPIO 7", "Interno", "Câmera OV5640 (HREF)", "Sim (LEDC/MCPWM)", "ADC1_CH6", "3.3V", "Ref Câmera", None],
    ["J2-08 (Dir)", "IO8", "GPIO 8", "Interno", "Câmera OV5640 (D2)", "Sim (LEDC/MCPWM)", "ADC1_CH7", "3.3V", "Dados Câmera", None],
    ["J2-09 (Dir)", "IO9", "GPIO 9", "Interno", "Câmera OV5640 (D1)", "Sim (LEDC/MCPWM)", "ADC1_CH8", "3.3V", "Dados Câmera", None],
    ["J2-10 (Dir)", "IO10", "GPIO 10", "Interno", "Câmera OV5640 (D3)", "Sim (LEDC/MCPWM)", "ADC1_CH9", "3.3V", "Dados Câmera", None],
    ["J2-11 (Dir)", "IO11", "GPIO 11", "Interno", "Câmera OV5640 (D0)", "Sim (LEDC/MCPWM)", "ADC2_CH0", "3.3V", "Dados Câmera", None],
    ["J2-12 (Dir)", "GND", "-", "Interno", "GND Auxiliar Onboard", "Não", "Não", "0V (GND)", "Normal", None]
]
style_sheet(ws_s3_single, s3_single_data)


# ==============================================================================
# 2. ABA: S3_CAM_Com_Nano (Arquitetura Distribuída com Chicote Serial de 3 fios)
# ==============================================================================
ws_s3_nano = wb.create_sheet(title="S3_CAM_Com_Nano")
s3_nano_data = [
    # Header J1 (Esquerdo)
    ["J1-01 (Esq)", "3V3", "-", "Interno", "Saída Regulada 3.3V", "Não", "Não", "3.3V", "Normal", None],
    ["J1-02 (Esq)", "GND", "-", "Fio Externo", "GND Comum (Chicote Fio 2)", "Não", "Não", "0V (GND)", "Normal", None],
    ["J1-03 (Esq)", "IO1", "GPIO 1", None, None, "Sim (LEDC/MCPWM)", "ADC1_CH0 (Lê c/ Wi-Fi)", "3.3V", "Touch 1 (Livre)", None],
    ["J1-04 (Esq)", "IO2", "GPIO 2", None, None, "Sim (LEDC/MCPWM)", "ADC1_CH1 (Lê c/ Wi-Fi)", "3.3V", "Touch 2 (Livre)", None],
    ["J1-05 (Esq)", "IO3", "GPIO 3", None, None, "Sim (LEDC/MCPWM)", "ADC1_CH2 (Lê c/ Wi-Fi)", "3.3V", "Touch 3 (Livre)", None],
    ["J1-06 (Esq)", "IO41", "GPIO 41", None, None, "Sim (LEDC/MCPWM)", "Não", "3.3V", "Livre p/ Expansão", None],
    ["J1-07 (Esq)", "IO42", "GPIO 42", None, None, "Sim (LEDC/MCPWM)", "Não", "3.3V", "Livre p/ Expansão", None],
    ["J1-08 (Esq)", "TX (U0T)", "GPIO 43", "Fio Externo", "Comandos -> Nano RX (Chicote Fio 3)", "Sim (LEDC/MCPWM)", "Não", "3.3V", "U0TXD Serial", None],
    ["J1-09 (Esq)", "RX (U0R)", "GPIO 44", None, None, "Sim (LEDC/MCPWM)", "Não", "3.3V", "Livre (Simplex)", None],
    ["J1-10 (Esq)", "IO19", "GPIO 19", "Interno", "USB-C Nativo (D-)", "Sim (LEDC/MCPWM)", "ADC2_CH8", "3.3V", "USB D-", None],
    ["J1-11 (Esq)", "IO20", "GPIO 20", "Interno", "USB-C Nativo (D+)", "Sim (LEDC/MCPWM)", "ADC2_CH9", "3.3V", "USB D+", None],
    ["J1-12 (Esq)", "IO21", "GPIO 21", None, None, "Sim (LEDC/MCPWM)", "Não", "3.3V", "Livre p/ Expansão", None],
    # Header J2 (Direito)
    ["J2-01 (Dir)", "5V", "-", "Fio Externo", "Alimentação 5.0V (Chicote Fio 1)", "Não", "Não", "5.0V", "Normal", None],
    ["J2-02 (Dir)", "GND", "-", "Interno", "GND Auxiliar Onboard", "Não", "Não", "0V (GND)", "Normal", None],
    ["J2-03 (Dir)", "IO0", "GPIO 0", "Interno", "Botão BOOT Onboard", "Sim (LEDC/MCPWM)", "Não", "3.3V", "Boot (Pull-up)", None],
    ["J2-04 (Dir)", "IO4", "GPIO 4", "Interno", "Câmera OV5640 (SIOD / SDA)", "Sim (LEDC/MCPWM)", "ADC1_CH3", "3.3V", "I2C Câmera", None],
    ["J2-05 (Dir)", "IO5", "GPIO 5", "Interno", "Câmera OV5640 (SIOC / SCL)", "Sim (LEDC/MCPWM)", "ADC1_CH4", "3.3V", "I2C Câmera", None],
    ["J2-06 (Dir)", "IO6", "GPIO 6", "Interno", "Câmera OV5640 (VSYNC)", "Sim (LEDC/MCPWM)", "ADC1_CH5", "3.3V", "Sinc Câmera", None],
    ["J2-07 (Dir)", "IO7", "GPIO 7", "Interno", "Câmera OV5640 (HREF)", "Sim (LEDC/MCPWM)", "ADC1_CH6", "3.3V", "Ref Câmera", None],
    ["J2-08 (Dir)", "IO8", "GPIO 8", "Interno", "Câmera OV5640 (D2)", "Sim (LEDC/MCPWM)", "ADC1_CH7", "3.3V", "Dados Câmera", None],
    ["J2-09 (Dir)", "IO9", "GPIO 9", "Interno", "Câmera OV5640 (D1)", "Sim (LEDC/MCPWM)", "ADC1_CH8", "3.3V", "Dados Câmera", None],
    ["J2-10 (Dir)", "IO10", "GPIO 10", "Interno", "Câmera OV5640 (D3)", "Sim (LEDC/MCPWM)", "ADC1_CH9", "3.3V", "Dados Câmera", None],
    ["J2-11 (Dir)", "IO11", "GPIO 11", "Interno", "Câmera OV5640 (D0)", "Sim (LEDC/MCPWM)", "ADC2_CH0", "3.3V", "Dados Câmera", None],
    ["J2-12 (Dir)", "GND", "-", "Interno", "GND Auxiliar Onboard", "Não", "Não", "0V (GND)", "Normal", None]
]
style_sheet(ws_s3_nano, s3_nano_data)


# ==============================================================================
# 3. ABA: ESP32_CAM_RoboCore (16 pinos do clássico AI-Thinker)
# ==============================================================================
ws_classic = wb.create_sheet(title="ESP32_CAM_RoboCore")
classic_data = [
    ["P01 (Header Esq)", "5V", "-", "Fio Externo", "Alimentação 5.0V (Chicote Fio 1)", "Não", "Não", "5.0V", "Normal", None],
    ["P02 (Header Esq)", "GND", "-", "Fio Externo", "GND Comum (Chicote Fio 2)", "Não", "Não", "0V (GND)", "Normal", None],
    ["P03 (Header Esq)", "IO12", "GPIO 12", "Interno", "MicroSD (Data 2)", "Sim (LEDC)", "ADC2_CH5 (Incompatível c/ Wi-Fi)", "3.3V", "Boot Strapping (Pull-down)", None],
    ["P04 (Header Esq)", "IO13", "GPIO 13", "Interno", "MicroSD (Data 3)", "Sim (LEDC)", "ADC2_CH4 (Incompatível c/ Wi-Fi)", "3.3V", "Normal", None],
    ["P05 (Header Esq)", "IO15", "GPIO 15", "Interno", "MicroSD (CMD)", "Sim (LEDC)", "ADC2_CH3 (Incompatível c/ Wi-Fi)", "3.3V", "Gera pulso no boot", None],
    ["P06 (Header Esq)", "IO14", "GPIO 14", "Interno", "MicroSD (CLK)", "Sim (LEDC)", "ADC2_CH6 (Incompatível c/ Wi-Fi)", "3.3V", "Normal", None],
    ["P07 (Header Esq)", "IO2", "GPIO 2", "Interno", "LED Onboard (Azul)", "Sim (LEDC)", "ADC2_CH2 (Incompatível c/ Wi-Fi)", "3.3V", "Boot Strapping (Pull-down)", None],
    ["P08 (Header Esq)", "IO4", "GPIO 4", "Interno", "Flash LED Alta Potência", "Sim (LEDC)", "ADC2_CH0 (Incompatível c/ Wi-Fi)", "3.3V", "Trilha transistor Flash", None],
    ["P09 (Header Dir)", "3V3", "-", "Interno", "Saída Regulada 3.3V", "Não", "Não", "3.3V", "Normal (~50mA max)", None],
    ["P10 (Header Dir)", "GND", "-", "Interno", "GND Auxiliar Onboard", "Não", "Não", "0V (GND)", "Normal", None],
    ["P11 (Header Dir)", "IO16", "GPIO 16", None, None, "Sim (LEDC)", "Não", "3.3V", "100% Livre (Sem ADC)", None],
    ["P12 (Header Dir)", "IO0", "GPIO 0", "Interno", "Câmera (XCLK 20MHz) / Boot", "Sim (LEDC)", "ADC2_CH1", "3.3V", "Bootloader (Pull-up)", None],
    ["P13 (Header Dir)", "U0R", "GPIO 3", None, None, "Sim (LEDC)", "Não", "3.3V", "RX0 Serial (Livre no Simplex)", None],
    ["P14 (Header Dir)", "U0T", "GPIO 1", "Fio Externo", "Comandos -> Nano RX (Chicote Fio 3)", "Sim (LEDC)", "Não", "3.3V", "TX0 Serial", None],
    ["P15 (Header Dir)", "GND", "-", "Interno", "GND Auxiliar Onboard", "Não", "Não", "0V (GND)", "Normal", None],
    ["P16 (Header Dir)", "VCC", "-", "Interno", "VCC Auxiliar Onboard", "Não", "Não", "5.0V / 3.3V", "Normal", None]
]
style_sheet(ws_classic, classic_data)


# ==============================================================================
# 4. ABA: Arduino_Nano_Chassi (Controle total de potência e sensores)
# ==============================================================================
ws_nano = wb.create_sheet(title="Arduino_Nano_Chassi")
nano_data = [
    ["P01 (D0)", "RX0", "PD0", "Fio Externo", "Comandos <- ESP TX (Chicote Fio 3)", "Não", "Não", "5.0V", "Serial RX (3.3V TTL direto)", None],
    ["P02 (D1)", "TX1", "PD1", None, None, "Não", "Não", "5.0V", "Serial TX (Livre no Simplex)", None],
    ["P03 (D2)", "D2", "PD2", None, None, "Não", "Não", "5.0V", "Interrupção Externa INT0 (Livre)", None],
    ["P04 (D3)", "D3", "PD3", "Fio Externo", "Motor Esq PWMA (Velocidade)", "Sim (Timer 2 - 8-bit)", "Não", "5.0V", "PWM Hardware (490Hz)", None],
    ["P05 (D4)", "D4", "PD4", "Fio Externo", "Motor Esq AIN1 (Direção)", "Não", "Não", "5.0V", "Sentido Giro Esq", None],
    ["P06 (D5)", "D5", "PD5", "Fio Externo", "Motor Esq AIN2 (Direção)", "Sim (Timer 0 - 8-bit)", "Não", "5.0V", "Sentido Giro Esq", None],
    ["P07 (D6)", "D6", "PD6", "Fio Externo", "Motor Dir PWMB (Velocidade)", "Sim (Timer 0 - 8-bit)", "Não", "5.0V", "PWM Hardware (980Hz)", None],
    ["P08 (D7)", "D7", "PD7", "Fio Externo", "Motor Dir BIN1 (Direção)", "Não", "Não", "5.0V", "Sentido Giro Dir", None],
    ["P09 (D8)", "D8", "PB0", "Fio Externo", "Motor Dir BIN2 (Direção)", "Não", "Não", "5.0V", "Sentido Giro Dir", None],
    ["P10 (D9)", "D9", "PB1", "Fio Externo", "Servo Pan Horizontal (Sinal)", "Sim (Timer 1 - 16-bit)", "Não", "5.0V", "PWM Servo 50Hz Alta Precisão", None],
    ["P11 (D10)", "D10", "PB2", "Fio Externo", "Servo Tilt Vertical (Sinal)", "Sim (Timer 1 - 16-bit)", "Não", "5.0V", "PWM Servo 50Hz Alta Precisão", None],
    ["P12 (D11)", "D11", "PB3", "Fio Externo", "Barra 8 LEDs WS2812B (Sinal DIN)", "Sim (Timer 2 - 8-bit)", "Não", "5.0V", "Timing Crítico 800kHz (MOSI)", None],
    ["P13 (D12)", "D12", "PB4", "Fio Externo", "Buzzer Passivo (Sinal Beep)", "Não", "Não", "5.0V", "Frequência tone() (MISO)", None],
    ["P14 (D13)", "D13", "PB5", "Interno", "LED L Onboard (Amarelo)", "Não", "Não", "5.0V", "SPI SCK Onboard", None],
    ["P15 (A0)", "A0", "PC0", "Fio Externo", "Leitura Tensão Bateria 2S", "Não", "Sim (ADC0 10-bit 0-5V)", "5.0V", "Divisor Resistivo (100k/47k)", None],
    ["P16 (A1)", "A1", "PC1", None, None, "Não", "Sim (ADC1 10-bit 0-5V)", "5.0V", "Livre p/ Sensor Analógico", None],
    ["P17 (A2)", "A2", "PC2", None, None, "Não", "Sim (ADC2 10-bit 0-5V)", "5.0V", "Livre p/ Sensor Analógico", None],
    ["P18 (A3)", "A3", "PC3", None, None, "Não", "Sim (ADC3 10-bit 0-5V)", "5.0V", "Livre p/ Sensor Analógico", None],
    ["P19 (A4)", "A4", "PC4", None, None, "Não", "Sim (ADC4 10-bit 0-5V)", "5.0V", "I2C SDA (Livre p/ IMU MPU6050)", None],
    ["P20 (A5)", "A5", "PC5", None, None, "Não", "Sim (ADC5 10-bit 0-5V)", "5.0V", "I2C SCL (Livre p/ IMU MPU6050)", None],
    ["P21 (A6)", "A6", "-", None, None, "Não", "Sim (ADC6 10-bit 0-5V)", "5.0V", "Entrada Analógica Pura (Livre)", None],
    ["P22 (A7)", "A7", "-", None, None, "Não", "Sim (ADC7 10-bit 0-5V)", "5.0V", "Entrada Analógica Pura (Livre)", None],
    ["P23 (PWR)", "5V", "-", "Fio Externo", "Alimentação 5.0V (Vem do Step-Down)", "Não", "Não", "5.0V", "Entrada 5.0V Regulada", None],
    ["P24 (PWR)", "GND", "-", "Fio Externo", "GND Comum do Chassi", "Não", "Não", "0V (GND)", "Terra Comum", None]
]
style_sheet(ws_nano, nano_data)

wb.save("tabela_pinagem_esp32_nano.xlsx")
print("Workbook saved successfully!")
