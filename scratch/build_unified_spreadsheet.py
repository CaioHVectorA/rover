# -*- coding: utf-8 -*-
"""
Gerador da planilha unificada LISTA_DE_COMPRAS_ROVER.xlsx
  - 2 abas: Rover ESP32-S3 / Rover Raspberry Pi 3
  - Coluna "Opcional" com cor diferenciada
  - Preços já com desconto PIX (-5%) para itens da RoboCore
  - Subtotais: Essenciais | Opcionais | Total Geral
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = openpyxl.Workbook()
ws_esp = wb.active
ws_esp.title = 'Rover ESP32-S3'
ws_pi = wb.create_sheet(title='Rover Raspberry Pi 3')

# Colunas:
# A=Item  B=Produto  C=Loja  D=Qtd  E=Preço Unit.à vista(R$)  F=Subtotal(R$)  G=Opcional  H=Link
HEADERS = ['Item', 'Produto', 'Loja', 'Qtd', 'Preço Unit. à vista (R$)', 'Subtotal à vista (R$)', 'Opcional', 'Link Direto']

# Itens: (num, nome, loja, qtd, preco_cheio, opcional, url)
# Preços da RoboCore já são multiplicados por 0.95 (PIX) no campo E (via fórmula)
# Preços do Mercado Livre não têm desconto PIX

# 'opcional' = True → marcado como "Sim" na coluna G
# RoboCore = desconto 5% PIX aplicado
# ML = sem desconto (sem PIX)

esp_items = [
    # (num, nome,                                          loja,          qtd, preco_cheio,  opcional,  url)
    ( 1, 'Micro Servo 9g SG90 (TowerPro)',                'RoboCore',     2,   13.67,        False, 'https://www.robocore.net/atuador/micro-servo-9g-sg90-towerpro'),
    ( 2, 'Micro Motor DC 6V 100RPM Redução Metal',        'RoboCore',     4,   29.90,        False, 'https://www.robocore.net/motor-caixas-de-reducao/micro-motor-com-caixa-de-reducao-6v-100rpm'),
    ( 3, 'StickyMAX - Roda S20 Macia 22mm',               'RoboCore',     4,   39.90,        False, 'https://www.robocore.net/roda/roda-stickymax-s20-22mm'),
    ( 4, 'Suporte para Micro Motores (Par Branco)',        'RoboCore',     2,    9.90,        False, 'https://www.robocore.net/item-mecanico/suporte-para-micro-motores'),
    ( 5, 'Módulo Driver Ponte H - L298N (Driver 1)',       'RoboCore',     1,   14.90,        False, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    ( 6, 'Módulo Driver Ponte H - L298N (Driver 2)',       'RoboCore',     1,   14.90,        False, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    ( 7, 'Conversor DC/DC Step Down Mini 560 5V (5A)',     'RoboCore',     1,    7.50,        False, 'https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v'),
    ( 8, 'Pack Bateria Li-Ion 7,4V 2500mAh com BMS',      'RoboCore',     1,   69.90,        False, 'https://www.robocore.net/baterias-fontes/pack-bateria-li-ion-7_4v-2500mah-com-bms'),
    ( 9, 'Cabo JST-RCY 2 pinos Fêmea',                    'RoboCore',     1,    1.90,        False, 'https://www.robocore.net/cabo/cabo-jst-rcy-2-pinos-femea'),
    (10, 'Módulo Buzzer 5V Passivo',                       'RoboCore',     1,    4.90,        True,  'https://www.robocore.net/atuador/modulo-buzzer-5v-passivo'),
    (11, 'Módulo WS2812 LED RGB (Barra 8 LEDs)',           'RoboCore',     1,    9.90,        True,  'https://www.robocore.net/led/modulo-ws2812-led-enderecavel-8-leds'),
    (12, 'Chave Gangorra KCD1-101 2T',                     'RoboCore',     1,    1.50,        False, 'https://www.robocore.net/botao-chave/chave-gangorra-kcd1-101-2t'),
    (13, 'Jumpers Fêmea-Fêmea x40 Unidades',               'RoboCore',     1,    6.90,        False, 'https://www.robocore.net/cabo/jumpers-femea-femea-x40-unidades'),
    (14, 'Jumpers Macho-Macho x40 Cabos',                  'RoboCore',     1,    7.90,        False, 'https://www.robocore.net/cabo/jumpers-macho-macho-x40-cabos'),
    (15, 'Placa Nano V3 + Cabo USB',                       'RoboCore',     1,   28.90,        False, 'https://www.robocore.net/placa-arduino/placa-nano-v3-com-cabo-usb-para-arduino'),
    (16, 'Placa ESP32-S3 CAM N16R8 + Câmera OV5640 5MP',  'Mercado Livre', 1,  119.00,       False, 'https://www.mercadolivre.com.br/p/MLB2061307865?matt_tool=38524122&pdp_filters=item_id:MLB5139266661'),
    (17, 'Cartão MicroSD 32GB Sandisk Ultra A1',           'Mercado Livre', 1,   49.90,       False, 'https://www.mercadolivre.com.br/cartao-de-memoria-micro-sd-sandisk-ultra-32gb-120mbs-c10-a1/p/MLB20654826'),
    (18, 'Módulo Giroscópio MPU-6050 GY-521 (VR)',         'Mercado Livre', 1,   19.90,       True,  'https://www.mercadolivre.com.br/modulo-acelerometro-giroscopio-mpu6050-gy521/up/MLBU4448831937'),
]

pi_items = [
    ( 1, 'Micro Servo 9g SG90 (TowerPro)',                 'RoboCore',     2,   13.67,       False, 'https://www.robocore.net/atuador/micro-servo-9g-sg90-towerpro'),
    ( 2, 'Câmera para Raspberry Pi Rev 1.3 (5MP)',         'RoboCore',     1,   49.90,       False, 'https://www.robocore.net/acessorios-raspberry-pi/camera-para-raspberry-pi-rev-1-3'),
    ( 3, 'Suporte Pan/Tilt para Câmera Raspberry Pi',      'RoboCore',     1,    6.90,       False, 'https://www.robocore.net/item-mecanico/suporte-pan-tilt-para-camera-raspberry-pi'),
    ( 4, 'Micro Motor DC 6V 100RPM Redução Metal',         'RoboCore',     4,   29.90,       False, 'https://www.robocore.net/motor-caixas-de-reducao/micro-motor-com-caixa-de-reducao-6v-100rpm'),
    ( 5, 'StickyMAX - Roda S20 Macia 22mm',                'RoboCore',     4,   39.90,       False, 'https://www.robocore.net/roda/roda-stickymax-s20-22mm'),
    ( 6, 'Suporte para Micro Motores (Par Branco)',         'RoboCore',     2,    9.90,       False, 'https://www.robocore.net/item-mecanico/suporte-para-micro-motores'),
    ( 7, 'Módulo Driver Ponte H - L298N (Driver 1)',        'RoboCore',     1,   14.90,       False, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    ( 8, 'Módulo Driver Ponte H - L298N (Driver 2)',        'RoboCore',     1,   14.90,       False, 'https://www.robocore.net/driver-motor/driver-motor-ponte-h-l298n'),
    ( 9, 'Conversor DC/DC Step Down Mini 560 5V (5A)',      'RoboCore',     1,    7.50,       False, 'https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v'),
    (10, 'Pack Bateria Li-Ion 7,4V 2500mAh com BMS',       'RoboCore',     1,   69.90,       False, 'https://www.robocore.net/baterias-fontes/pack-bateria-li-ion-7_4v-2500mah-com-bms'),
    (11, 'Cabo JST-RCY 2 pinos Fêmea',                     'RoboCore',     1,    1.90,       False, 'https://www.robocore.net/cabo/cabo-jst-rcy-2-pinos-femea'),
    (12, 'Módulo Buzzer 5V Passivo',                        'RoboCore',     1,    4.90,       True,  'https://www.robocore.net/atuador/modulo-buzzer-5v-passivo'),
    (13, 'Módulo WS2812 LED RGB (Barra 8 LEDs)',            'RoboCore',     1,    9.90,       True,  'https://www.robocore.net/led/modulo-ws2812-led-enderecavel-8-leds'),
    (14, 'Chave Gangorra KCD1-101 2T',                      'RoboCore',     1,    1.50,       False, 'https://www.robocore.net/botao-chave/chave-gangorra-kcd1-101-2t'),
    (15, 'Jumpers Fêmea-Fêmea x40 Unidades',                'RoboCore',     1,    6.90,       False, 'https://www.robocore.net/cabo/jumpers-femea-femea-x40-unidades'),
    (16, 'Jumpers Macho-Macho x40 Cabos',                   'RoboCore',     1,    7.90,       False, 'https://www.robocore.net/cabo/jumpers-macho-macho-x40-cabos'),
    (17, 'Placa Nano V3 + Cabo USB',                        'RoboCore',     1,   28.90,       False, 'https://www.robocore.net/placa-arduino/placa-nano-v3-com-cabo-usb-para-arduino'),
    (18, 'Raspberry Pi 3 Model B (se não possuir)',         'Mercado Livre', 1,  389.00,      False, 'https://www.mercadolivre.com.br/raspberry-pi3-pi-3-model-b-quadcore-12ghz/p/MLB42963336'),
    (19, 'Cartão MicroSD 64GB Sandisk Ultra A1 Classe 10', 'Mercado Livre', 1,   69.90,      False, 'https://www.mercadolivre.com.br/memoria-microsd-profissional-sandisk-ultra-64gb-120-mbs-a1/p/MLB23033439'),
    (20, 'Módulo Giroscópio MPU-6050 GY-521 (VR)',         'Mercado Livre', 1,   19.90,      True,  'https://www.mercadolivre.com.br/modulo-acelerometro-giroscopio-mpu6050-gy521/up/MLBU4448831937'),
]


def style_sheet(ws, items):
    font_family = 'Calibri'

    # --- Estilos ---
    header_fill  = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
    header_font  = Font(name=font_family, size=11, bold=True, color='FFFFFF')
    data_font    = Font(name=font_family, size=10)
    italic_font  = Font(name=font_family, size=10, italic=True, color='6B7280')
    link_font    = Font(name=font_family, size=10, color='0563C1', underline='single')
    bold_font    = Font(name=font_family, size=10, bold=True)
    total_font   = Font(name=font_family, size=11, bold=True, color='1F4E79')

    thin_border = Border(
        left  =Side(style='thin', color='D9D9D9'),
        right =Side(style='thin', color='D9D9D9'),
        top   =Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9'),
    )
    total_border = Border(
        left  =Side(style='thin',   color='D9D9D9'),
        right =Side(style='thin',   color='D9D9D9'),
        top   =Side(style='thin',   color='1F4E79'),
        bottom=Side(style='double', color='1F4E79'),
    )

    subtotal_fill  = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')
    optional_fill  = PatternFill(start_color='FFF9E6', end_color='FFF9E6', fill_type='solid')  # amarelo suave
    total_ess_fill = PatternFill(start_color='E2F0D9', end_color='E2F0D9', fill_type='solid')  # verde suave
    total_all_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')  # azul suave

    MONEY_FMT = '"R$" #,##0.00'

    # ─────────────────────────────────────────────
    # CABEÇALHO (linha 1)
    # ─────────────────────────────────────────────
    ws.append(HEADERS)
    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(HEADERS) + 1):
        cell = ws.cell(1, col_idx)
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = thin_border

    # ─────────────────────────────────────────────
    # DADOS (linhas 2 … N)
    # ─────────────────────────────────────────────
    row_map = {}   # num_item → row_idx  (para formulas de subtotal)
    item_rows = []

    for item in items:
        num, name, store, qty, preco_cheio, opcional, url = item
        row_idx = ws.max_row + 1
        item_rows.append(row_idx)
        row_map[num] = row_idx

        # Preço à vista: RoboCore = -5% PIX; ML = preço cheio
        if store == 'RoboCore':
            # Preço unitário à vista já com PIX
            pix_unit = round(preco_cheio * 0.95, 2)
        else:
            pix_unit = preco_cheio

        opcional_label = 'Sim' if opcional else ''
        subtotal_formula = f'=D{row_idx}*E{row_idx}'

        ws.append([num, name, store, qty, pix_unit, subtotal_formula, opcional_label, 'Abrir Produto'])
        ws.row_dimensions[row_idx].height = 20

        c_num   = ws.cell(row_idx, 1)
        c_name  = ws.cell(row_idx, 2)
        c_store = ws.cell(row_idx, 3)
        c_qty   = ws.cell(row_idx, 4)
        c_price = ws.cell(row_idx, 5)
        c_sub   = ws.cell(row_idx, 6)
        c_opt   = ws.cell(row_idx, 7)
        c_link  = ws.cell(row_idx, 8)

        row_fill = optional_fill if opcional else None

        for c in [c_num, c_name, c_store, c_qty, c_price, c_sub, c_opt, c_link]:
            c.font   = data_font
            c.border = thin_border
            c.alignment = Alignment(vertical='center')
            if row_fill:
                c.fill = row_fill

        c_num.alignment   = Alignment(horizontal='center', vertical='center')
        c_store.alignment = Alignment(horizontal='center', vertical='center')
        c_qty.alignment   = Alignment(horizontal='center', vertical='center')
        c_opt.alignment   = Alignment(horizontal='center', vertical='center')

        c_price.number_format = MONEY_FMT
        c_price.alignment     = Alignment(horizontal='right', vertical='center')

        c_sub.number_format = MONEY_FMT
        c_sub.alignment     = Alignment(horizontal='right', vertical='center')

        if opcional:
            c_opt.font = Font(name=font_family, size=10, bold=True, color='B8860B')
        else:
            c_opt.font = italic_font

        c_link.hyperlink  = url
        c_link.font       = link_font
        c_link.alignment  = Alignment(horizontal='center', vertical='center')

    # ─────────────────────────────────────────────
    # TOTAIS
    # ─────────────────────────────────────────────
    # Identifica linhas por tipo (opcional vs essencial, loja)
    ess_rows = [r for it, r in zip(items, item_rows) if not it[5]]   # não opcional
    opt_rows = [r for it, r in zip(items, item_rows) if it[5]]       # opcional
    all_rows = item_rows

    def sum_formula(rows):
        """Gera =F2+F5+... para uma lista de linhas específicas."""
        return '=' + '+'.join(f'F{r}' for r in rows)

    def blank_row(ws, thin_border, font=None, fill=None, num_cols=8):
        """Linha em branco apenas com borda."""
        r = ws.max_row + 1
        ws.append([None] * num_cols)
        ws.row_dimensions[r].height = 8
        for c in range(1, num_cols + 1):
            ws.cell(r, c).border = thin_border
        return r

    def total_row(ws, label, formula, fill, font, thin_border, total_border, MONEY_FMT, is_last=False, num_cols=8):
        r = ws.max_row + 1
        ws.append([None, label, None, None, None, formula, None, None])
        ws.row_dimensions[r].height = 24
        border_to_use = total_border if is_last else thin_border
        for c in range(1, num_cols + 1):
            cell = ws.cell(r, c)
            cell.fill      = fill
            cell.font      = font
            cell.border    = border_to_use
            cell.alignment = Alignment(vertical='center')
        ws.cell(r, 6).number_format = MONEY_FMT
        ws.cell(r, 6).alignment     = Alignment(horizontal='right', vertical='center')
        return r

    blank_row(ws, thin_border)

    # Subtotal Essenciais
    total_row(
        ws, '✅  Total Essencial (sem opcionais) – à vista no PIX',
        sum_formula(ess_rows), total_ess_fill,
        Font(name=font_family, size=11, bold=True, color='375623'),
        thin_border, total_border, MONEY_FMT, is_last=False,
    )

    # Subtotal Opcionais
    total_row(
        ws, '⭐  Itens Opcionais (Buzzer, LEDs, Giroscópio)',
        sum_formula(opt_rows), optional_fill,
        Font(name=font_family, size=10, bold=True, color='B8860B'),
        thin_border, total_border, MONEY_FMT, is_last=False,
    )

    # Total Geral (com opcionais)
    total_row(
        ws, '💰  TOTAL GERAL (com opcionais) – à vista no PIX',
        sum_formula(all_rows), total_all_fill,
        Font(name=font_family, size=12, bold=True, color='1F4E79'),
        thin_border, total_border, MONEY_FMT, is_last=True,
    )

    # ─────────────────────────────────────────────
    # LARGURAS DE COLUNA
    # ─────────────────────────────────────────────
    widths = {'A': 7, 'B': 56, 'C': 16, 'D': 7, 'E': 24, 'F': 24, 'G': 12, 'H': 16}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    ws.views.sheetView[0].showGridLines = True


style_sheet(ws_esp, esp_items)
style_sheet(ws_pi, pi_items)

out_file = 'LISTA_DE_COMPRAS_ROVER.xlsx'
wb.save(out_file)
print(f'Planilha gerada: {out_file}  |  Abas: {wb.sheetnames}')
