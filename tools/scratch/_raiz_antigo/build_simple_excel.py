import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Styles
font_title = Font(name='Segoe UI', size=14, bold=True, color='1E293B')
font_subtitle = Font(name='Segoe UI', size=10, italic=True, color='64748B')
font_sec_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
font_tbl_header = Font(name='Segoe UI', size=10, bold=True, color='334155')
font_data = Font(name='Segoe UI', size=10, color='1E293B')
font_bold = Font(name='Segoe UI', size=10, bold=True, color='1E293B')
font_link = Font(name='Segoe UI', size=9, color='0284C7', underline='single')
font_total = Font(name='Segoe UI', size=11, bold=True, color='0F172A')

fill_tbl_header = PatternFill(start_color='F1F5F9', end_color='F1F5F9', fill_type='solid')
fill_usina = PatternFill(start_color='0D9488', end_color='0D9488', fill_type='solid') # Teal
fill_ml = PatternFill(start_color='0284C7', end_color='0284C7', fill_type='solid') # Sky
fill_curto = PatternFill(start_color='7C3AED', end_color='7C3AED', fill_type='solid') # Purple
fill_total_sec = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
fill_grand_total = PatternFill(start_color='ECFDF5', end_color='ECFDF5', fill_type='solid')

border_thin = Border(
    left=Side(style='thin', color='E2E8F0'),
    right=Side(style='thin', color='E2E8F0'),
    top=Side(style='thin', color='E2E8F0'),
    bottom=Side(style='thin', color='E2E8F0')
)
border_total = Border(
    top=Side(style='thin', color='94A3B8'),
    bottom=Side(style='double', color='0F172A')
)

ws = wb.create_sheet(title='Lista de Compras')
ws.views.sheetView[0].showGridLines = True

# Title
ws.cell(1, 1, 'ROVER ESP32-S3 — PLANEJAMENTO DE COMPRAS (2º LOTE)').font = font_title
ws.cell(2, 1, 'Planilha simplificada para visualização rápida no celular e computador.').font = font_subtitle

# Cards at Top
# Card 1: Total Pix
ws.merge_cells('A4:B4')
ws.cell(4, 1, 'TOTAL À VISTA (PIX)').font = Font(name='Segoe UI', size=9, bold=True, color='047857')
ws.cell(4, 1).alignment = Alignment(horizontal='center')
ws.merge_cells('A5:B5')
ws.cell(5, 1, '=E33').font = Font(name='Segoe UI', size=16, bold=True, color='059669')
ws.cell(5, 1).alignment = Alignment(horizontal='center')
ws.cell(5, 1).number_format = '"R$ "#,##0.00'

# Card 2: Total Cartão
ws.merge_cells('C4:D4')
ws.cell(4, 3, 'TOTAL CARTÃO').font = Font(name='Segoe UI', size=9, bold=True, color='1E293B')
ws.cell(4, 3).alignment = Alignment(horizontal='center')
ws.merge_cells('C5:D5')
ws.cell(5, 3, '=D33').font = Font(name='Segoe UI', size=16, bold=True, color='1E293B')
ws.cell(5, 3).alignment = Alignment(horizontal='center')
ws.cell(5, 3).number_format = '"R$ "#,##0.00'

# Card 3: Economia
ws.merge_cells('E4:F4')
ws.cell(4, 5, 'ECONOMIA NO PIX').font = Font(name='Segoe UI', size=9, bold=True, color='0369A1')
ws.cell(4, 5).alignment = Alignment(horizontal='center')
ws.merge_cells('E5:F5')
ws.cell(5, 5, '=C5-A5').font = Font(name='Segoe UI', size=16, bold=True, color='0284C7')
ws.cell(5, 5).alignment = Alignment(horizontal='center')
ws.cell(5, 5).number_format = '"R$ "#,##0.00'

for r in range(4, 6):
    for c in range(1, 7):
        cell = ws.cell(r, c)
        cell.border = border_thin
        cell.fill = fill_grand_total if c in [1, 2] else (fill_total_sec if c in [3, 4] else PatternFill(start_color='F0F9FF', end_color='F0F9FF', fill_type='solid'))

# ==========================================
# SEÇÃO 1: USINAINFO
# ==========================================
row = 7
ws.merge_cells(f'A{row}:F{row}')
ws.cell(row, 1, '1. USINAINFO — SENSORES, TELAS, BOTÕES & REFRIGERAÇÃO (5% OFF NO PIX)').font = font_sec_header
ws.cell(row, 1).fill = fill_usina
ws.cell(row, 1).alignment = Alignment(vertical='center', indent=1)
ws.row_dimensions[row].height = 24

row += 1
headers = ['Produto / Componente', 'Qtd', 'Preço Unit.', 'Subtotal Cartão', 'À Vista (Pix)', 'Link de Compra']
for col_idx, h in enumerate(headers, 1):
    c = ws.cell(row, col_idx, h)
    c.font = font_tbl_header
    c.fill = fill_tbl_header
    c.border = border_thin
    c.alignment = Alignment(horizontal='center' if col_idx in [2, 3, 4, 5] else 'left', vertical='center')

usina_items = [
    ('Display TFT LCD 3,5" SPI Touch + Slot SD (ILI9488)', 1, 119.60, 'https://www.usinainfo.com.br/display-arduino/tft-lcd-35-spi-touch-screen-com-slot-sd-8570.html'),
    ('Display TFT 1,3” ST7789 SPI 240×240 (Econômico)', 1, 34.70, 'https://www.usinainfo.com.br/display-arduino/display-tft-lcd-13-spi-rgb-240x240-st7789-5607.html'),
    ('Display OLED 0,96” I²C 128×64 (SSD1306)', 1, 24.30, 'https://www.usinainfo.com.br/display-arduino/display-oled-096-i2c-128x64-branco-5366.html'),
    ('Push Button Chave Táctil 6×6×5mm (2x Kits c/ 5 = 10 botões)', 2, 2.46, 'https://www.usinainfo.com.br/push-buttons/push-button-chave-tactil-6x6x5-kit-com-5-unidades-2989.html'),
    ('Kit 10 Capas para Push Button 6×6mm (Pretas/Brancas)', 1, 8.86, 'https://www.usinainfo.com.br/push-buttons/capa-para-push-button-6x6mm-preta-kit-com-10-unidades-5861.html'),
    ('Conversor de Nível Lógico 3,3V / 5V Bidirecional (CNL35)', 1, 7.50, 'https://www.usinainfo.com.br/conversores-de-sinal/conversor-de-nivel-logico-33-5v-bidirecional-cnl35-3741.html'),
    ('Kit Antena Wi-Fi 2,4GHz 3dBi + Cabo Pigtail U.FL (IPEX)', 1, 11.80, 'https://www.usinainfo.com.br/antenas-wireless/antena-omni-wi-fi-24ghz-3dbi-com-pigtail-u-fl-ipex1-5259.html'),
    ('Mini Ventoinha 5V (25×25×10mm)', 1, 16.97, 'https://www.usinainfo.com.br/coolers-para-pc/mini-cooler-5v-25x25mm-para-esc-e-projetos-4408.html'),
    ('2x Sensores de Temperatura DS18B20', 2, 15.34, 'https://www.usinainfo.com.br/sensores-de-temperatura/sensor-de-temperatura-ds18b20-avulso-2741.html'),
    ('Kit 3 Mini Dissipadores Autoadesivos', 1, 3.60, 'https://www.usinainfo.com.br/dissipadores-de-calor/kit-com-3-dissipadores-de-aluminio-para-raspberry-pi-3-e-outros-4428.html'),
    ('Sensor de Tensão DC 0–25V (Divisor 5:1)', 1, 4.95, 'https://www.usinainfo.com.br/sensor-de-tensao/sensor-de-tensao-dc-0-25v-3425.html'),
    ('2x Joysticks Analógicos KY-023 (Controle Futuro)', 2, 5.95, 'https://www.usinainfo.com.br/joystick-e-controles-ir/joystick-ky023-3-eixos-2305.html')
]

usina_start = row + 1
for item, qtd, preco, link in usina_items:
    row += 1
    ws.cell(row, 1, item).font = font_data
    ws.cell(row, 2, qtd).font = font_data
    ws.cell(row, 2).alignment = Alignment(horizontal='center')
    
    ws.cell(row, 3, preco).font = font_data
    ws.cell(row, 3).number_format = '"R$ "#,##0.00'
    ws.cell(row, 3).alignment = Alignment(horizontal='right')
    
    ws.cell(row, 4, f'=B{row}*C{row}').font = font_data
    ws.cell(row, 4).number_format = '"R$ "#,##0.00'
    ws.cell(row, 4).alignment = Alignment(horizontal='right')
    
    ws.cell(row, 5, f'=ROUND(D{row}*0.95,2)').font = font_data
    ws.cell(row, 5).number_format = '"R$ "#,##0.00'
    ws.cell(row, 5).alignment = Alignment(horizontal='right')
    
    cl = ws.cell(row, 6, 'Abrir Loja ↗')
    cl.hyperlink = link
    cl.font = font_link
    cl.alignment = Alignment(horizontal='center')
    
    for c in range(1, 7):
        ws.cell(row, c).border = border_thin
usina_end = row

# Subtotal UsinaInfo
row += 1
ws.cell(row, 1, 'Subtotal UsinaInfo (12 itens):').font = font_bold
ws.cell(row, 4, f'=SUM(D{usina_start}:D{usina_end})').font = font_bold
ws.cell(row, 4).number_format = '"R$ "#,##0.00'
ws.cell(row, 5, f'=SUM(E{usina_start}:E{usina_end})').font = font_bold
ws.cell(row, 5).number_format = '"R$ "#,##0.00'
for c in range(1, 7):
    cell = ws.cell(row, c)
    cell.fill = fill_total_sec
    cell.border = border_thin
row_usina_subtotal = row

# ==========================================
# SEÇÃO 2: MERCADO LIVRE
# ==========================================
row += 2
ws.merge_cells(f'A{row}:F{row}')
ws.cell(row, 1, '2. MERCADO LIVRE — ÁUDIO I2S, FARÓIS, MICROSD & RÁDIO (FRETE FULL)').font = font_sec_header
ws.cell(row, 1).fill = fill_ml
ws.cell(row, 1).alignment = Alignment(vertical='center', indent=1)
ws.row_dimensions[row].height = 24

row += 1
for col_idx, h in enumerate(headers, 1):
    c = ws.cell(row, col_idx, h)
    c.font = font_tbl_header
    c.fill = fill_tbl_header
    c.border = border_thin
    c.alignment = Alignment(horizontal='center' if col_idx in [2, 3, 4, 5] else 'left', vertical='center')

ml_items = [
    ('Módulo Áudio I2S MAX98357A + Mini Alto-falante 3W', 1, 25.00, 'https://lista.mercadolivre.com.br/modulo-max98357a'),
    ('Cartão MicroSD SanDisk Ultra 32GB Classe 10 A1', 1, 44.90, 'https://www.mercadolivre.com.br/cartao-de-memoria-micro-sd-sandisk-ultra-32gb-120mbs-c10-a1/p/MLB20654826?pdp_filters=shipping:fulfillment'),
    ('Kit 10x LEDs 3W Branco Frio Estrela (Faróis)', 1, 29.90, 'https://lista.mercadolivre.com.br/led-3w-estrela_OrderId_PRICE*ASC_Fulfillment_YES'),
    ('Receptor FlySky FS-iA6B 6CH 2.4GHz', 1, 79.90, 'https://lista.mercadolivre.com.br/fs-ia6b_OrderId_PRICE*ASC_Fulfillment_YES')
]

ml_start = row + 1
for item, qtd, preco, link in ml_items:
    row += 1
    ws.cell(row, 1, item).font = font_data
    ws.cell(row, 2, qtd).font = font_data
    ws.cell(row, 2).alignment = Alignment(horizontal='center')
    
    ws.cell(row, 3, preco).font = font_data
    ws.cell(row, 3).number_format = '"R$ "#,##0.00'
    ws.cell(row, 3).alignment = Alignment(horizontal='right')
    
    ws.cell(row, 4, f'=B{row}*C{row}').font = font_data
    ws.cell(row, 4).number_format = '"R$ "#,##0.00'
    ws.cell(row, 4).alignment = Alignment(horizontal='right')
    
    ws.cell(row, 5, f'=D{row}').font = font_data # ML sem desc pix adicional
    ws.cell(row, 5).number_format = '"R$ "#,##0.00'
    ws.cell(row, 5).alignment = Alignment(horizontal='right')
    
    cl = ws.cell(row, 6, 'Abrir ML ↗')
    cl.hyperlink = link
    cl.font = font_link
    cl.alignment = Alignment(horizontal='center')
    
    for c in range(1, 7):
        ws.cell(row, c).border = border_thin
ml_end = row

# Subtotal ML
row += 1
ws.cell(row, 1, 'Subtotal Mercado Livre (4 itens):').font = font_bold
ws.cell(row, 4, f'=SUM(D{ml_start}:D{ml_end})').font = font_bold
ws.cell(row, 4).number_format = '"R$ "#,##0.00'
ws.cell(row, 5, f'=SUM(E{ml_start}:E{ml_end})').font = font_bold
ws.cell(row, 5).number_format = '"R$ "#,##0.00'
for c in range(1, 7):
    cell = ws.cell(row, c)
    cell.fill = fill_total_sec
    cell.border = border_thin
row_ml_subtotal = row

# ==========================================
# SEÇÃO 3: CURTO CIRCUITO (4G)
# ==========================================
row += 2
ws.merge_cells(f'A{row}:F{row}')
ws.cell(row, 1, '3. CURTO CIRCUITO — EXPANSÃO 4G LTE (10% OFF NO PIX)').font = font_sec_header
ws.cell(row, 1).fill = fill_curto
ws.cell(row, 1).alignment = Alignment(vertical='center', indent=1)
ws.row_dimensions[row].height = 24

row += 1
for col_idx, h in enumerate(headers, 1):
    c = ws.cell(row, col_idx, h)
    c.font = font_tbl_header
    c.fill = fill_tbl_header
    c.border = border_thin
    c.alignment = Alignment(horizontal='center' if col_idx in [2, 3, 4, 5] else 'left', vertical='center')

curto_items = [
    ('Módulo 4G LTE Cat-4 A7608SA-H + Antena FCP (Teleoperação)', 1, 448.00, 'https://curtocircuito.com.br/modulo-a7608sa-h-4g-lte-antena-fcp.html')
]

curto_start = row + 1
for item, qtd, preco, link in curto_items:
    row += 1
    ws.cell(row, 1, item).font = font_data
    ws.cell(row, 2, qtd).font = font_data
    ws.cell(row, 2).alignment = Alignment(horizontal='center')
    
    ws.cell(row, 3, preco).font = font_data
    ws.cell(row, 3).number_format = '"R$ "#,##0.00'
    ws.cell(row, 3).alignment = Alignment(horizontal='right')
    
    ws.cell(row, 4, f'=B{row}*C{row}').font = font_data
    ws.cell(row, 4).number_format = '"R$ "#,##0.00'
    ws.cell(row, 4).alignment = Alignment(horizontal='right')
    
    ws.cell(row, 5, f'=ROUND(D{row}*0.90,2)').font = font_data
    ws.cell(row, 5).number_format = '"R$ "#,##0.00'
    ws.cell(row, 5).alignment = Alignment(horizontal='right')
    
    cl = ws.cell(row, 6, 'Abrir Loja ↗')
    cl.hyperlink = link
    cl.font = font_link
    cl.alignment = Alignment(horizontal='center')
    
    for c in range(1, 7):
        ws.cell(row, c).border = border_thin
curto_end = row

# Subtotal Curto Circuito
row += 1
ws.cell(row, 1, 'Subtotal Curto Circuito (1 item):').font = font_bold
ws.cell(row, 4, f'=SUM(D{curto_start}:D{curto_end})').font = font_bold
ws.cell(row, 4).number_format = '"R$ "#,##0.00'
ws.cell(row, 5, f'=SUM(E{curto_start}:E{curto_end})').font = font_bold
ws.cell(row, 5).number_format = '"R$ "#,##0.00'
for c in range(1, 7):
    cell = ws.cell(row, c)
    cell.fill = fill_total_sec
    cell.border = border_thin
row_curto_subtotal = row

# ==========================================
# TOTAL GERAL CONSOLIDADO
# ==========================================
row += 2
ws.cell(row, 1, 'TOTAL GERAL CONSOLIDADO:').font = font_total
ws.cell(row, 4, f'=D{row_usina_subtotal}+D{row_ml_subtotal}+D{row_curto_subtotal}').font = font_total
ws.cell(row, 4).number_format = '"R$ "#,##0.00'
ws.cell(row, 4).alignment = Alignment(horizontal='right')
ws.cell(row, 5, f'=E{row_usina_subtotal}+E{row_ml_subtotal}+E{row_curto_subtotal}').font = font_total
ws.cell(row, 5).number_format = '"R$ "#,##0.00'
ws.cell(row, 5).alignment = Alignment(horizontal='right')

for c in range(1, 7):
    cell = ws.cell(row, c)
    cell.fill = fill_grand_total
    cell.border = border_total

# Column widths
ws.column_dimensions['A'].width = 52
ws.column_dimensions['B'].width = 8
ws.column_dimensions['C'].width = 15
ws.column_dimensions['D'].width = 17
ws.column_dimensions['E'].width = 17
ws.column_dimensions['F'].width = 16

# Save file
wb_path = r'docs\hardware\compras_rover_reorganizado_atualizado.xlsx'
wb.save(wb_path)
print("Simplified spreadsheet created successfully at:", wb_path)
