#!/usr/bin/env python3
"""Mapa físico proposto com fios isolados e ilhas auxiliares, sem barras de pinos."""
from pathlib import Path
import json,csv
import pcbnew as k
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/hardware/kicad/rover_perfurada_90x150';OUT.mkdir(parents=True,exist_ok=True)
P=2.54;OX=(90-33*P)/2;OY=(150-57*P)/2
pt=lambda c,r:(OX+(c-1)*P,OY+(r-1)*P)
ends={};net_at={};connections=[]
def end(name,c,r,net):
 assert (c,r) not in [v[:2] for v in ends.values()],(name,c,r)
 ends[name]=(c,r,net);net_at[c,r]=net;return name
# Nano padrão: USB para cima, solda direta nos furos, sem soquete.
left=['D1','D0','RST-L','GND-L','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12']
right=['VIN','GND-R','RST-R','5V','A7','A6','A5','A4','A3','A2','A1','A0','AREF','3V3','D13']
mapnet={'D2':'RX_INV','D3':'PWMA','D4':'AIN1','D5':'AIN2','D6':'PWMB','D7':'BIN1','D8':'BIN2','D9':'PAN','D10':'TILT','D12':'STBY','5V':'+5V','GND-L':'GND','GND-R':'GND'}
for i,label in enumerate(left):end('N:'+label,9,34+i,mapnet.get(label,''))
for i,label in enumerate(right):end('N:'+label,15,34+i,mapnet.get(label,''))
# Ilhas auxiliares: ligar por fios curtos aos terminais NOMINAIS dos módulos.
for i,label in enumerate(['STBY','PWMA','AIN1','AIN2','PWMB','BIN1','BIN2']):end('TB:'+label,6,10+i,label)
for i,(label,net) in enumerate([('VM','VBAT'),('VCC','+5V'),('GND','GND'),('AO1','AO1'),('AO2','AO2'),('BO1','BO1'),('BO2','BO2')]):end('TB:'+label,18,10+i,net)
for label,c,r,net in [('IN+',22,10,'VBAT'),('IN-',22,14,'GND'),('OUT+',33,10,'+5V'),('OUT-',33,14,'GND')]:end('MINI:'+label,c,r,net)
for name,c,r,net in [('BAT+',22,3,'VBAT'),('BAT-',27,3,'GND'),('ESP:5V',32,40,'+5V'),('ESP:GND',32,42,'GND'),('ESP:TX',32,44,'ESP_TX'),('PAN:S',4,54,'PAN'),('PAN:5V',6,54,'+5V'),('PAN:GND',8,54,'GND'),('TILT:S',13,54,'TILT'),('TILT:5V',15,54,'+5V'),('TILT:GND',17,54,'GND'),('Q:C',23,39,'RX_INV'),('Q:B',24,39,'BASE'),('Q:E',25,39,'GND'),('R1:1',23,35,'ESP_TX'),('R1:2',26,35,'BASE'),('R2:1',21,35,'+5V'),('R2:2',21,38,'RX_INV')]:end(name,c,r,net)
for name,c,r,net in [('E1:1',3,4,'AO1'),('E1:2',5,4,'AO2'),('E2:1',8,4,'AO1'),('E2:2',10,4,'AO2'),('D1:1',13,4,'BO1'),('D1:2',15,4,'BO2'),('D2:1',18,4,'BO1'),('D2:2',20,4,'BO2')]:end(name,c,r,net)
def link(a,b,via=()):
 assert ends[a][2]==ends[b][2],(a,b)
 points=[pt(*ends[a][:2]),*via,pt(*ends[b][:2])]
 connections.append({'a':a,'b':b,'net':ends[a][2],'points':points})
link('BAT+','MINI:IN+');link('BAT-','MINI:IN-');link('MINI:IN+','TB:VM')
# Cada alimentação sai do regulador: fios isolados, sem depender do Nano para alimentar cargas.
for target in ['N:5V','TB:VCC','ESP:5V','PAN:5V','TILT:5V','R2:1']:
 a=pt(*ends['MINI:OUT+'][:2]);b=pt(*ends[target][:2]);link('MINI:OUT+',target,[(87,a[1]),(87,b[1]-1),(b[0],b[1]-1)])
for target in ['N:GND-R','TB:GND','ESP:GND','PAN:GND','TILT:GND','Q:E']:
 a=pt(*ends['MINI:OUT-'][:2]);b=pt(*ends[target][:2]);link('MINI:OUT-',target,[(89,a[1]),(89,b[1]+1),(b[0],b[1]+1)])
for i,label in enumerate(['STBY','PWMA','AIN1','AIN2','PWMB','BIN1','BIN2']):
 n='D12' if label=='STBY' else f'D{i+2}'
 a=pt(*ends['N:'+n][:2]);b=pt(*ends['TB:'+label][:2]);lane=3+i*1.3
 link('N:'+n,'TB:'+label,[(lane,a[1]),(lane,b[1])])
for net,targets in [('AO1',['E1:1','E2:1']),('AO2',['E1:2','E2:2']),('BO1',['D1:1','D2:1']),('BO2',['D1:2','D2:2'])]:
 for target in targets:link('TB:'+net,target)
link('N:D9','PAN:S');link('N:D10','TILT:S')
link('ESP:TX','R1:1');link('R1:2','Q:B');link('Q:C','N:D2');link('Q:C','R2:2')
# Resistores: ligação interna do componente, não fio/jumper.
component_edges=[('R1:1','R1:2'),('R2:1','R2:2')]
# KiCad: grade física de ilhas; fios em camada de desenho, NÃO trilhas de PCB.
b=k.BOARD();mm=k.FromMM;v=lambda x,y:k.wxPoint(mm(x),mm(y))
nets={n:k.NETINFO_ITEM(b,n) for n in {e[2] for e in ends.values()} if n}
for n in nets.values():b.Add(n)
f=k.FOOTPRINT(b);f.SetReference('PERFURADA');f.SetValue('ILHAS_2.54mm');f.Reference().SetVisible(False);f.Value().SetVisible(False);b.Add(f)
for c in range(1,35):
 for r in range(1,59):
  p=k.PAD(f);p.SetNumber(f'{c}-{r}');p.SetAttribute(k.PAD_ATTRIB_PTH);p.SetShape(k.PAD_SHAPE_CIRCLE);p.SetPosition(v(*pt(c,r)));p.SetSize(k.wxSize(mm(1.7),mm(1.7)));p.SetDrillSize(k.wxSize(mm(.9),mm(.9)));p.SetLayerSet(k.LSET.AllCuMask())
  if net_at.get((c,r)):p.SetNet(nets[net_at[c,r]])
  f.Add(p)
def line(a,z,layer=k.Dwgs_User,width=.2):
 s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*z));s.SetLayer(layer);s.SetWidth(mm(width));b.Add(s)
def rect(x,y,w,h,layer=k.Dwgs_User):
 corners=[(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]
 for a,z in zip(corners,corners[1:]):line(a,z,layer)
def text(t,x,y,size=1):
 s=k.PCB_TEXT(b);s.SetText(t);s.SetPosition(v(x,y));s.SetTextSize(k.wxSize(mm(size),mm(size)));s.SetTextThickness(mm(.15));s.SetLayer(k.Dwgs_User);b.Add(s)
rect(0,0,90,150,k.Edge_Cuts)
modules=[('TB6612',19,23,24,24),('MINI 560',57,24,29,18),('NANO',pt(9,34)[0]-1.27,pt(9,34)[1]-5,17.78,43.18)]
for label,x,y,w,h in modules:rect(x,y,w,h);text(label,x+w/2,y+h/2,1.3)
for name,(c,r,net) in ends.items():
 x,y=pt(c,r);text(name,x,y-1.2,.7)
for conn in connections:
 for a,z in zip(conn['points'],conn['points'][1:]):line(a,z,k.Cmts_User,.25)
for a,z in component_edges:line(pt(*ends[a][:2]),pt(*ends[z][:2]),k.Dwgs_User,.7)
text('MAPA PROPOSTO - FIOS ISOLADOS / SEM BARRAS DE PINOS',45,-5,1.2)
text('TB/MINI: ILHAS AUXILIARES, NAO POSICAO REAL DOS TERMINAIS',45,154,.9)
k.SaveBoard(str(OUT/'rover_perfurada_90x150.kicad_pcb'),b)
# Imagens: mesmas coordenadas, vista inferior refletida no eixo horizontal.
S=14;L=95;T=150;W=1450;H=2520
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';ft=lambda n:ImageFont.truetype(font,n)
colors={'+5V':'#c12d25','VBAT':'#96351d','GND':'#26282c','ESP_TX':'#c19c00','BASE':'#c19c00','RX_INV':'#7652b8','PAN':'#008091','TILT':'#008091','STBY':'#347da0','PWMA':'#347da0','AIN1':'#347da0','AIN2':'#347da0','PWMB':'#347da0','BIN1':'#347da0','BIN2':'#347da0','AO1':'#438249','AO2':'#438249','BO1':'#438249','BO2':'#438249'}
for bottom in [False,True]:
 im=Image.new('RGB',(W,H),'#f5f4ef');d=ImageDraw.Draw(im)
 xy=lambda x,y:(L+(90-x if bottom else x)*S,T+y*S)
 box=lambda x,y,w,h:[(min(xy(x,y)[0],xy(x+w,y)[0]),xy(x,y)[1]),(max(xy(x,y)[0],xy(x+w,y)[0]),xy(x,y+h)[1])]
 d.text((50,30),'PERFURADA 90 × 150 mm · '+('LADO DA SOLDA' if bottom else 'LADO DOS COMPONENTES'),fill='#172b35',font=ft(29))
 d.text((50,77),'INFERIOR ESPELHADA: vire a placa como uma página.' if bottom else 'Proposta de montagem com fios isolados e inversor BC337.',fill='#43545c',font=ft(21))
 d.rectangle(box(0,0,90,150),fill='#e7ddbc',outline='#716b55',width=3)
 for c in range(1,35):
  for r in range(1,59):
   x,y=xy(*pt(c,r));d.ellipse((x-3,y-3,x+3,y+3),fill='#a59975')
 for c in range(1,35,3):
  x,y=xy(pt(c,1)[0],-2);d.text((x,y),str(c),fill='#43545c',font=ft(16),anchor='mm')
 for r in range(1,59,3):
  x,y=xy(-2,pt(1,r)[1]);d.text((x,y),str(r),fill='#43545c',font=ft(16),anchor='mm')
 # Fundo suave mantém módulos legíveis; fios por baixo são mostrados em projeção no topo.
 for label,x,y,w,h in modules:
  d.rectangle(box(x,y,w,h),fill='#dde3df' if bottom else '#bed1da',outline='#43545c',width=2)
  tx,ty=xy(x+w/2,y+h/2);d.text((tx,ty),label,fill='#172b35',font=ft(21),anchor='mm')
 # Fios abaixo; cruzamento sem ilha NÃO é conexão. Halos separam cruzamentos.
 for conn in connections:
  path=[xy(*p) for p in conn['points']]
  d.line(path,fill='#f5f4ef',width=8);d.line(path,fill=colors[conn['net']],width=4)
 for a,z in component_edges:
  pa=xy(*pt(*ends[a][:2]));pb=xy(*pt(*ends[z][:2]));d.line([pa,pb],fill='#503c26',width=13)
  label='R1 1k' if a.startswith('R1') else 'R2 10k';cx=(pa[0]+pb[0])/2;cy=(pa[1]+pb[1])/2
  d.text((cx,cy-18),label,fill='#172b35',font=ft(18),anchor='mm')
 for name,(c,r,net) in ends.items():
  x,y=xy(*pt(c,r));color=colors.get(net,'#716b55');d.ellipse((x-7,y-7,x+7,y+7),fill='#f5f4ef',outline=color,width=3)
  # Nomes Nano e ilhas dos módulos dispostos no lado externo.
  if name.startswith('N:'):
   dx=(-14 if c==9 else 14)*(-1 if bottom else 1);anchor='rm' if dx<0 else 'lm';d.text((x+dx,y),name[2:],fill='#172b35',font=ft(15),anchor=anchor)
  elif name.startswith('TB:'):
   dx=(-12 if c==6 else 12)*(-1 if bottom else 1);d.text((x+dx,y),name[3:],fill='#172b35',font=ft(15),anchor='rm' if dx<0 else 'lm')
  elif name.startswith(('R1:','R2:')):pass
  else:
   d.text((x,y-13),name.replace('MINI:',''),fill='#172b35',font=ft(15),anchor='mb')
 # Legendas locais sem simular pinos dos módulos comerciais.
 for txt,x,y in [('ILHAS → TB6612',30,51),('MINI: ILHAS DE LIGAÇÃO',70,47),('BC337: C / B / E',65,105),('ESP FORA DA PLACA',70,124),('SAÍDA PARA SERVOS',28,145),('BATERIA APÓS CHAVE',63,3),('4 MOTORES EXTERNOS',29,3)]:
  d.text(xy(x,y),txt,fill='#172b35',font=ft(17),anchor='mm')
 d.text((50,2280),'Vermelho 5V · preto GND · amarelo TX/base · roxo RX invertido',fill='#172b35',font=ft(22))
 d.text((50,2320),'Azul: controle · verde: motores · cruzamentos sem ilha não se unem.',fill='#172b35',font=ft(22))
 d.text((50,2370),'TB/Mini: pontos propostos para soldar fios, não o pinout físico dos módulos.',fill='#43545c',font=ft(20))
 d.text((50,2410),'Passo 2,54 mm assumido. Conferir Nano, BC337 e fixação antes de soldar.',fill='#43545c',font=ft(20))
 d.text((50,2450),'Os trajetos representam fios ISOLADOS; não fazer pontes nuas nos cruzamentos.',fill='#43545c',font=ft(20))
 im.save(OUT/('montagem_inferior.png' if bottom else 'montagem_superior.png'))
with (OUT/'ligacoes_furo_a_furo.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Rede','Origem','Coluna','Linha','Destino','Coluna','Linha'])
 for c in connections:w.writerow([c['net'],c['a'],*ends[c['a']][:2],c['b'],*ends[c['b']][:2]])
(OUT/'montagem_dados.json').write_text(json.dumps({'terminais':ends,'fios':connections,'componentes':component_edges},indent=2))
print('Mapa físico:',len(connections),'fios;',len(ends),'terminais; topo e inferior espelhada.')
