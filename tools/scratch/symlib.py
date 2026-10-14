import re,glob,sys
BASE=glob.glob('/home/usuario/.local/share/flatpak/runtime/org.kicad.KiCad.Library.Symbols/x86_64/stable/*/files/symbols')[0]
def extract(lib,name):
    t=open(f'{BASE}/{lib}.kicad_sym').read()
    m=re.search(r'\n\t\(symbol "%s"\n'%re.escape(name),t)
    i=m.start()+1; d=0
    for j in range(i,len(t)):
        if t[j]=='(':d+=1
        elif t[j]==')':
            d-=1
            if d==0: return t[i:j+1]
def pins(s):
    return re.findall(r'\(pin (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)\s*\(length ([\d.]+)\)(?:\s*\(hide yes\))?\s*\(name "([^"]*)".*?\(number "([^"]*)"',s,re.S)
if __name__=='__main__':
    for lib,n in [('RF_Module','ESP32-S3-WROOM-1'),('MCU_Module','Arduino_Nano_v3.x'),('MCU_Module','Arduino_Nano_v2.x'),('Transistor_BJT','BC547')]:
        s=extract(lib,n); print('==',n,len(s)); 
        if n.endswith('v3.x'): print(s[:600])
        for p in pins(s): 
            if n.startswith('ESP') and not any(k in p[6] for k in ('TXD','RXD','3V3','GND','EN')): continue
            print(p)
