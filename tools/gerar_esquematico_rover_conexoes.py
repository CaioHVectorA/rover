#!/usr/bin/env python3
"""Esquema funcional de conexões: terminais nomeados, sem assumir headers físicos."""
from pathlib import Path
import uuid,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/hardware/kicad/rover_perfurada_90x150'
OUT.mkdir(parents=True,exist_ok=True)
uid=lambda:str(uuid.uuid4())
root=uid(); libs=[];parts=[];wires=[];labels=[];texts=[];junctions=[];audit=[]
def q(s):return json.dumps(s,ensure_ascii=False)
def font(size=1.5):return f'(font (size {size} {size}))'
def note(s,x,y,size=1.5):texts.append(f'(text {q(s)} (at {x} {y} 0) (effects {font(size)} (justify left top)) (uuid "{uid()}"))')
def block(ref,title,x,y,w,h,pins):
    name='Rover:'+ref
    pinlib=[];pp={}
    for terminal,side,off in pins:
        px=-5 if side=='L' else w+5;py=-off;ang=0 if side=='L' else 180
        pinlib.append(f'(pin passive line (at {px} {py} {ang}) (length 5) (name {q(terminal)} (effects {font(1.15)})) (number {q(terminal)} (effects {font(.8)})))')
        pp[terminal]=(x+px,y+off)
    libs.append(f'''(symbol {q(name)} (pin_numbers hide) (pin_names (offset 1)) (in_bom yes) (on_board yes)
(property "Reference" "{ref}" (at 0 3 0) (effects {font()}))
(property "Value" {q(title)} (at {w/2} {-h/2} 0) (effects {font()}))
(symbol "{ref}_0_1" (rectangle (start 0 0) (end {w} {-h}) (stroke (width .3) (type default)) (fill (type background))))
(symbol "{ref}_1_1" {' '.join(pinlib)}))''')
    parts.append(f'''(symbol (lib_id {q(name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")
(property "Reference" {q(ref)} (at {x+w/2} {y-3} 0) (effects {font()}))
(property "Value" {q(title)} (at {x+w/2} {y+h/2} 0) (effects {font(1.4)} (hide yes)))
(instances (project "rover_conexoes" (path "/{root}" (reference {q(ref)}) (unit 1)))))''')
    note(title,x+3,y+2,1.4)
    return pp

def wire(*points):
 for a,b in zip(points,points[1:]):
    if a==b:continue
    wires.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
def lab(net,pt):labels.append(f'(label {q(net)} (at {pt[0]} {pt[1]} 0) (effects {font(1.25)} (justify left bottom)) (uuid "{uid()}"))')
def stub(p,net,side='L',length=10):
 e=(p[0]+(-length if side=='L' else length),p[1]);wire(p,e);lab(net,e);return e

def tie(a,b,net,*middle):
 wire(a,*middle,b);audit.append([net,a,b])
def dot(p):junctions.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))')

note('ROVER — FIOS E CONEXÕES / PERFURADA 90 × 150 mm',15,10,2.6)
note('PROPOSTA ELÉTRICA • terminais por nome • fios diretos aos módulos • não validada em bancada',15,18,1.5)
# Alimentação
B=block('BT1','BATERIA 2S',20,35,28,22,[('+','R',7),('-','R',17)])
SW=block('SW1','CHAVE',70,35,22,15,[('IN','L',7),('OUT','R',7)])
REG=block('U1','MINI 560',120,35,32,32,[('IN+','L',7),('IN-','L',22),('OUT+ 5V','R',7),('OUT-','R',22)])
tie(B['+'],SW['IN'],'BAT+');tie(SW['OUT'],REG['IN+'],'VBAT');lab('VBAT',SW['OUT'])
tie(B['-'],REG['IN-'],'GND',(58,52),(58,57));lab('GND',(58,57))
stub(REG['OUT+ 5V'],'+5V','R',15);stub(REG['OUT-'],'GND','R',15)
note('VBAT = bateria após a chave (até 8,4 V).\n+5V vem da saída do Mini 560. Todos os GND são comuns.\nNano no pino 5V; servos/ESP alimentados pelo Mini 560.',200,35,1.5)
# Principal
E=block('U2','ESP32-S3-CAM\nFORA DA PLACA',25,92,45,58,[('5V','R',12),('GND','R',22),('IO43 / TX','R',32)])
N=block('A1','ARDUINO\nNANO V3',155,87,40,120,[('5V','L',17),('GND','L',27),('D2 / RX INV','L',67)]+[(f'D{i}','R',25+(i-3)*10) for i in range(3,11)]+[('D12 / STBY','R',15)])
tie(E['5V'],N['5V'],'+5V');lab('+5V',(100,104))
tie(E['GND'],N['GND'],'GND');lab('GND',(100,114))
R1=block('R1','1k',85,119,16,12,[('1','L',5),('2','R',5)])
Q=block('Q1','BC337',110,134,22,40,[('B / 2','L',20),('C / 1','R',10),('E / 3','R',30)])
R2=block('R2','10k',110,74,20,17,[('1','R',5),('2','R',12)])
tie(E['IO43 / TX'],R1['1'],'ESP_TX');lab('ESP_TX',(76,124))
tie(R1['2'],Q['B / 2'],'BASE',(106,154))
tie(Q['C / 1'],N['D2 / RX INV'],'RX_INV',(143,144),(143,154))
tie(R2['2'],Q['C / 1'],'RX_INV',(143,R2['2'][1]),(143,144));dot((143,144))
stub(R2['1'],'+5V','R',5);stub(Q['E / 3'],'GND','R',6)
note('CHICOTE DE 3 FIOS\nVermelho: 5V\nPreto: GND\nAmarelo: IO43 → R1 → BC337\nSem retorno Nano → ESP.',25,155,1.6)
D=block('U3','MÓDULO\nTB6612FNG',255,87,40,92,[(p,'L',15+i*10) for i,p in enumerate(['STBY','PWMA','AIN1','AIN2','PWMB','BIN1','BIN2'])]+[('VM','R',8),('VCC','R',18),('GND','R',28),('AO1','R',43),('AO2','R',53),('BO1','R',68),('BO2','R',78)])
for i,p in enumerate(['STBY','PWMA','AIN1','AIN2','PWMB','BIN1','BIN2']):
 tie(N['D12 / STBY'] if i==0 else N[f'D{i+2}'],D[p],p)
for pin,net in [('VM','VBAT'),('VCC','+5V'),('GND','GND')]:stub(D[pin],net,'R',8)
motors={}
for index,y,side in [(1,95,'E'),(2,135,'E'),(3,175,'D'),(4,215,'D')]:
 motors[index]=block('M'+str(index),f'JGA-050\n{side}{1 if index%2 else 2}',360,y,34,26,[('1','L',8),('2','L',18)])
for pin,ids,terminal,x in [('AO1',[1,2],'1',320),('AO2',[1,2],'2',325),('BO1',[3,4],'1',330),('BO2',[3,4],'2',335)]:
 origin=D[pin]; branch=(x,origin[1]);a=motors[ids[0]][terminal];b=motors[ids[1]][terminal]
 tie(origin,a,pin,branch,(x,a[1]));tie(branch,b,pin,(x,b[1]));dot(branch)
 lab(pin,(305,origin[1]))
note('E1 e E2 em paralelo no canal A.\nD1 e D2 em paralelo no canal B.\nConferir sentido de giro de cada motor.',335,253,1.25)
# Servos com fios diretos, sem conectores adicionais
P=block('S1','SERVO PAN',255,191,40,32,[('SINAL','L',7),('5V','R',7),('GND','R',22)])
T=block('S2','SERVO TILT',255,236,40,32,[('SINAL','L',7),('5V','R',7),('GND','R',22)])
tie(N['D9'],P['SINAL'],'PAN',(220,172),(220,198))
tie(N['D10'],T['SINAL'],'TILT',(230,182),(230,243))
for c in [P,T]:
 stub(c['5V'],'+5V','R',10);stub(c['GND'],'GND','R',10)
note('RX em D2 com inversão: SoftwareSerial entrada(2, A1, true), 38400 baud.\nA1 reservado como TX não conectado; libera D3 para PWMA. STBY passa para D12. Firmware ainda não alterado.',200,68,1.2)
note('Montagem sem barras de pinos. Mesmo nome = mesmo fio/rede, mesmo quando os trechos não se tocam. Caixa = módulo/terminal funcional; NÃO é footprint.',15,288,1.2)
note('PRINCIPAL: alimentação, comunicação, tração e Pan/Tilt. Fios soldados diretamente; periféricos auxiliares omitidos.',15,276,1.5)
body=f'''(kicad_sch (version 20251024) (generator "eeschema") (generator_version "10.0") (uuid "{root}") (paper "A3")
(lib_symbols {' '.join(libs)})
{' '.join(parts+wires+labels+junctions+texts)}
(sheet_instances (path "/" (page "1"))) (embedded_fonts no))'''
(OUT/'rover_conexoes.kicad_sch').write_text(body)
(OUT/'conexoes_auditoria.json').write_text(json.dumps(audit,indent=2))
print(OUT/'rover_conexoes.kicad_sch')
