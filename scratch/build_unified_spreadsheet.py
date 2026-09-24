# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = openpyxl.Workbook()

# Sheet 1: ESP32-S3
ws_esp = wb.active
ws_esp.title = 'Rover ESP32-S3'

# Sheet 2: Raspberry Pi 3
ws_pi = wb.create_sheet(title='Rover Raspberry Pi 3')

headers = ['Item', 'Produto', 'Loja', 'Qtd', 'Preço Unitário (R$)', 'Subtotal (R$)', 'Link Direto']

esp_items = [
    (1, 'Micro Servo 9g SG90 (TowerPro)', 'RoboCore', 2, 13.67, 'https://www.robocore.net/atuador/micro-servo-9g-sg90-towerpro'),
    (2, 'Micro Motor DC 6V 100RPM Redução Metal', 'RoboCore', 4, 29.90, 'https://www.robocore.net/motor-caixas-de-reducao/micro-motor-com-caixa-de-reducao-6v-100rpm'),
    (3, 'StickyMAX - Roda S20 Macia 22mm', 'RoboCore', 4, 39.90, 'https://www.robocore.net/roda/roda-stickymax-s20-22mm'),
    (4, 'Suporte para Micro Motores (Par Branco)', 'RoboCore', 2, 9.90, 'https://www.robocore.net/item-mecanico/suporte-para-micro-motores'),
    (5, 'Módulo Driver Ponte H - L298N (Driver 1: Motores Esq.)', 'RoboCore', 1, 14.90, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    (6, 'Módulo Driver Ponte H - L298N (Driver 2: Motores Dir.)', 'RoboCore', 1, 14.90, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    (7, 'Conversor DC/DC Step Down Mini 560 5V (5A síncrono)', 'RoboCore', 1, 7.50, 'https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v'),
    (8, 'Pack Bateria Li-Ion 7,4V 2500mAh com BMS', 'RoboCore', 1, 69.90, 'https://www.robocore.net/baterias-fontes/pack-bateria-li-ion-7_4v-2500mah-com-bms'),
    (9, 'Cabo JST-RCY 2 pinos Fêmea', 'RoboCore', 1, 1.90, 'https://www.robocore.net/cabo/cabo-jst-rcy-2-pinos-femea'),
    (10, 'Módulo Buzzer 5V Passivo', 'RoboCore', 1, 4.90, 'https://www.robocore.net/atuador/modulo-buzzer-5v-passivo'),
    (11, 'Módulo WS2812 LED RGB (Barra 8 LEDs)', 'RoboCore', 1, 9.90, 'https://www.robocore.net/led/modulo-ws2812-led-enderecavel-8-leds'),
    (12, 'Chave Gangorra KCD1-101 2T', 'RoboCore', 1, 1.50, 'https://www.robocore.net/botao-chave/chave-gangorra-kcd1-101-2t'),
    (13, 'Jumpers Fêmea-Fêmea x40 Unidades', 'RoboCore', 1, 6.90, 'https://www.robocore.net/cabo/jumpers-femea-femea-x40-unidades'),
    (14, 'Jumpers Macho-Macho x40 Cabos', 'RoboCore', 1, 7.90, 'https://www.robocore.net/cabo/jumpers-macho-macho-x40-cabos'),
    (15, 'Placa Nano V3 + Cabo USB', 'RoboCore', 1, 28.90, 'https://www.robocore.net/placa-arduino/placa-nano-v3-com-cabo-usb-para-arduino'),
    (16, 'Placa ESP32-S3 CAM N16R8 + Câmera OV5640 5MP', 'Mercado Livre', 1, 119.00, 'https://www.mercadolivre.com.br/p/MLB2061307865?matt_tool=38524122&pdp_filters=item_id:MLB5139266661'),
    (17, 'Cartão MicroSD 32GB Sandisk Ultra A1 (FAT32 p/ ESP32)', 'Mercado Livre', 1, 49.90, 'https://www.mercadolivre.com.br/cartao-de-memoria-micro-sd-sandisk-ultra-32gb-120mbs-c10-a1/p/MLB20654826'),
    (18, 'Módulo Giroscópio MPU-6050 GY-521 (VR Head Tracking)', 'Mercado Livre', 1, 19.90, 'https://www.mercadolivre.com.br/modulo-acelerometro-giroscopio-mpu6050-gy521/up/MLBU4448831937')
]

pi_items = [
    (1, 'Micro Servo 9g SG90 (TowerPro)', 'RoboCore', 2, 13.67, 'https://www.robocore.net/atuador/micro-servo-9g-sg90-towerpro'),
    (2, 'Câmera para Raspberry Pi Rev 1.3 (5MP)', 'RoboCore', 1, 49.90, 'https://www.robocore.net/acessorios-raspberry-pi/camera-para-raspberry-pi-rev-1-3'),
    (3, 'Suporte Pan/Tilt para Câmera Raspberry Pi', 'RoboCore', 1, 6.90, 'https://www.robocore.net/item-mecanico/suporte-pan-tilt-para-camera-raspberry-pi'),
    (4, 'Micro Motor DC 6V 100RPM Redução Metal', 'RoboCore', 4, 29.90, 'https://www.robocore.net/motor-caixas-de-reducao/micro-motor-com-caixa-de-reducao-6v-100rpm'),
    (5, 'StickyMAX - Roda S20 Macia 22mm', 'RoboCore', 4, 39.90, 'https://www.robocore.net/roda/roda-stickymax-s20-22mm'),
    (6, 'Suporte para Micro Motores (Par Branco)', 'RoboCore', 2, 9.90, 'https://www.robocore.net/item-mecanico/suporte-para-micro-motores'),
    (7, 'Módulo Driver Ponte H - L298N (Driver 1: Esquerda)', 'RoboCore', 1, 14.90, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    (8, 'Módulo Driver Ponte H - L298N (Driver 2: Direita)', 'RoboCore', 1, 14.90, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    (9, 'Conversor DC/DC Step Down Mini 560 5V (5A síncrono)', 'RoboCore', 1, 7.50, 'https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v'),
    (10, 'Pack Bateria Li-Ion 7,4V 2500mAh com BMS', 'RoboCore', 1, 69.90, 'https://www.robocore.net/baterias-fontes/pack-bateria-li-ion-7_4v-2500mah-com-bms'),
    (11, 'Cabo JST-RCY 2 pinos Fêmea', 'RoboCore', 1, 1.90, 'https://www.robocore.net/cabo/cabo-jst-rcy-2-pinos-femea'),
    (12, 'Módulo Buzzer 5V Passivo', 'RoboCore', 1, 4.90, 'https://www.robocore.net/atuador/modulo-buzzer-5v-passivo'),
    (13, 'Módulo WS2812 LED RGB (Barra 8 LEDs)', 'RoboCore', 1, 9.90, 'https://www.robocore.net/led/modulo-ws2812-led-enderecavel-8-leds'),
    (14, 'Chave Gangorra KCD1-101 2T', 'RoboCore', 1, 1.50, 'https://www.robocore.net/botao-chave/chave-gangorra-kcd1-101-2t'),
    (15, 'Jumpers Fêmea-Fêmea x40 Unidades', 'RoboCore', 1, 6.90, 'https://www.robocore.net/cabo/jumpers-femea-femea-x40-unidades'),
    (16, 'Jumpers Macho-Macho x40 Cabos', 'RoboCore', 1, 7.90, 'https://www.robocore.net/cabo/jumpers-macho-macho-x40-cabos'),
    (17, 'Placa Nano V3 + Cabo USB', 'RoboCore', 1, 28.90, 'https://www.robocore.net/placa-arduino/placa-nano-v3-com-cabo-usb-para-arduino'),
    (18, 'Raspberry Pi 3 Model B (se não possuir)', 'Mercado Livre', 1, 389.00, 'https://www.mercadolivre.com.br/raspberry-pi3-pi-3-model-b-quadcore-12ghz/p/MLB42963336'),
    (19, 'Cartão MicroSD 64GB Sandisk Ultra A1 Classe 10', 'Mercado Livre', 1, 69.90, 'https://www.mercadolivre.com.br/memoria-microsd-profissional-sandisk-ultra-64gb-120-mbs-a1/p/MLB23033439'),
    (20, 'Módulo Giroscópio MPU-6050 GY-521 (VR Head Tracking)', 'Mercado Livre', 1, 19.90, 'https://www.mercadolivre.com.br/modulo-acelerometro-giroscopio-mpu6050-gy521/up/MLBU4448831937')
]

def style_sheet(ws, items, rc_count, ml_count):
    font_family = 'Calibri'
    header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
    header_font = Font(name=font_family, size=11, bold=True, color='FFFFFF')
    
    data_font = Font(name=font_family, size=10)
    link_font = Font(name=font_family, size=10, color='0563C1', underline='single')
    bold_font = Font(name=font_family, size=10, bold=True)
    total_font = Font(name=font_family, size=11, bold=True, color='1F4E79')
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    total_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='1F4E79'),
        bottom=Side(style='double', color='1F4E79')
    )
    
    subtotal_fill = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')
    total_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    
    # Headers
    ws.append(headers)
    ws.row_dimensions[1].height = 26
    for col_idx in range(1, 8):
        cell = ws.cell(1, col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # Items
    for item in items:
        num, name, store, qty, unit_price, url = item
        row_idx = ws.max_row + 1
        formula = f'=D{row_idx}*E{row_idx}'
        ws.append([num, name, store, qty, unit_price, formula, 'Abrir Produto'])
        ws.row_dimensions[row_idx].height = 20
        
        c_num = ws.cell(row_idx, 1)
        c_name = ws.cell(row_idx, 2)
        c_store = ws.cell(row_idx, 3)
        c_qty = ws.cell(row_idx, 4)
        c_price = ws.cell(row_idx, 5)
        c_sub = ws.cell(row_idx, 6)
        c_link = ws.cell(row_idx, 7)
        
        for c in [c_num, c_name, c_store, c_qty, c_price, c_sub, c_link]:
            c.font = data_font
            c.border = thin_border
            c.alignment = Alignment(vertical='center')
            
        c_num.alignment = Alignment(horizontal='center', vertical='center')
        c_store.alignment = Alignment(horizontal='center', vertical='center')
        c_qty.alignment = Alignment(horizontal='center', vertical='center')
        
        c_price.number_format = '"R$" #,##0.00'
        c_price.alignment = Alignment(horizontal='right', vertical='center')
        
        c_sub.number_format = '"R$" #,##0.00'
        c_sub.alignment = Alignment(horizontal='right', vertical='center')
        
        c_link.hyperlink = url
        c_link.font = link_font
        c_link.alignment = Alignment(horizontal='center', vertical='center')

    # Totals
    rc_start = 2
    rc_end = 1 + rc_count
    ml_start = rc_end + 1
    ml_end = rc_end + ml_count
    
    r_rc_sub = ws.max_row + 1
    ws.append([None, f'Subtotal RoboCore (Itens 1 a {rc_count})', None, None, None, f'=SUM(F{rc_start}:F{rc_end})', None])
    
    r_rc_pix = ws.max_row + 1
    ws.append([None, 'RoboCore à vista no PIX (-5%)', None, None, None, f'=F{r_rc_sub}*0.95', None])
    
    r_ml_sub = ws.max_row + 1
    ws.append([None, f'Subtotal Mercado Livre (Itens {rc_count+1} a {rc_count+ml_count})', None, None, None, f'=SUM(F{ml_start}:F{ml_end})', None])
    
    r_total = ws.max_row + 1
    ws.append([None, 'TOTAL GERAL ESTIMADO (PIX RoboCore + ML)', None, None, None, f'=F{r_rc_pix}+F{r_ml_sub}', None])

    for r in [r_rc_sub, r_rc_pix, r_ml_sub]:
        ws.row_dimensions[r].height = 21
        for col_idx in range(1, 8):
            c = ws.cell(r, col_idx)
            c.fill = subtotal_fill
            c.border = thin_border
            c.font = bold_font
            c.alignment = Alignment(vertical='center')
        ws.cell(r, 6).number_format = '"R$" #,##0.00'
        ws.cell(r, 6).alignment = Alignment(horizontal='right', vertical='center')

    ws.row_dimensions[r_total].height = 24
    for col_idx in range(1, 8):
        c = ws.cell(r_total, col_idx)
        c.fill = total_fill
        c.border = total_border
        c.font = total_font
        c.alignment = Alignment(vertical='center')
    ws.cell(r_total, 6).number_format = '"R$" #,##0.00'
    ws.cell(r_total, 6).alignment = Alignment(horizontal='right', vertical='center')

    # Column widths
    widths = {'A': 7, 'B': 58, 'C': 16, 'D': 8, 'E': 22, 'F': 22, 'G': 16}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    ws.views.sheetView[0].showGridLines = True

style_sheet(ws_esp, esp_items, 15, 3)
style_sheet(ws_pi, pi_items, 17, 3)

out_file = 'LISTA_DE_COMPRAS_ROVER.xlsx'
wb.save(out_file)
print(f'Successfully created {out_file} with sheets: {wb.sheetnames}')
