import openpyxl

wb = openpyxl.load_workbook(r'docs\hardware\compras_rover_reorganizado.xlsx')
for sheetname in wb.sheetnames:
    ws = wb[sheetname]
    print(f"Sheet {sheetname}: data_validations={len(ws.data_validations.dataValidation)}")
    for dv in ws.data_validations.dataValidation:
        print(f"  DV: formula={dv.formula1}, sqref={dv.sqref}")
