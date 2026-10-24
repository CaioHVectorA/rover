import openpyxl

wb = openpyxl.load_workbook(r'docs\hardware\compras_rover_reorganizado_atualizado.xlsx')
ws = wb['UsinaInfo']

# Check rows 19 to 25
print("Before fix:")
for r in range(19, 25):
    print(f"R{r}:", ws.cell(r, 3).value, ws.cell(r, 6).value)

# Delete one empty row 19
ws.delete_rows(19, 1)

# Now row 19 is empty separator, row 20 is "Total dos itens cotados"
ws.cell(20, 6, '=SUM(F8:F18)')
ws.cell(20, 7, '=SUM(G8:G18)')
ws.cell(21, 6, '=SUMIF(I8:I18,"Alta",F8:F18)')
ws.cell(21, 7, '=SUMIF(I8:I18,"Alta",G8:G18)')
ws.cell(22, 6, '=SUMIF(I8:I18,"Média",F8:F18)')
ws.cell(22, 7, '=SUMIF(I8:I18,"Média",G8:G18)')
ws.cell(23, 6, '=SUMIF(I8:I18,"Baixa",F8:F18)')
ws.cell(23, 7, '=SUMIF(I8:I18,"Baixa",G8:G18)')

# Update Resumo Geral
ws_rg = wb['Resumo Geral']
ws_rg.cell(6, 2, "='UsinaInfo'!F20+'Mercado Livre'!F14+'Curto Circuito'!F10")
ws_rg.cell(6, 4, "='UsinaInfo'!G20+'Mercado Livre'!G14+'Curto Circuito'!G10")
ws_rg.cell(11, 5, "='UsinaInfo'!F20")
ws_rg.cell(11, 6, "='UsinaInfo'!G20")

wb.save(r'docs\hardware\compras_rover_reorganizado_atualizado.xlsx')
print("After fix:")
for r in range(19, 25):
    print(f"R{r}:", ws.cell(r, 3).value, ws.cell(r, 6).value)
