#pragma once
// ====================================================================================
// PAINEL WEB UNICO (servido pelo ESP32 em http://<ip>/ ou http://rover.local/)
// Mostra so os paineis que o firmware declara em /api/info (caps: cam, servo, motor).
// ====================================================================================
#include <Arduino.h>

static const char PAINEL_HTML[] PROGMEM = R"HTML(<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Rover POC</title>
<style>
:root{--bg:#07080b;--p:#10131a;--b:#232833;--t:#d7dde8;--s:#7d8798;--a:#5fd38d;--w:#e6b450;--e:#ef6b6b;--i:#6aa7ff}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{background:var(--bg);color:var(--t);font:13px ui-monospace,Consolas,Menlo,monospace;padding:10px;max-width:780px;margin:auto}
header{display:flex;gap:8px;align-items:center;justify-content:space-between;padding:6px 0 10px;flex-wrap:wrap}
header b{font-size:15px;letter-spacing:.5px}
.pill{border:1px solid var(--b);padding:2px 8px;border-radius:3px;color:var(--s)}
.ok{color:var(--a);border-color:#2b5a40}.bad{color:var(--e);border-color:#6a2d2d}.warn{color:var(--w);border-color:#6a5624}
section{background:var(--p);border:1px solid var(--b);border-radius:4px;padding:10px;margin-bottom:10px}
section>h2{font-size:11px;letter-spacing:1.5px;color:var(--s);text-transform:uppercase;margin-bottom:8px;font-weight:600}
.row{display:flex;gap:8px;align-items:center;margin:5px 0;flex-wrap:wrap}
.row label{flex:0 0 150px;color:var(--s)}
.row input[type=range]{flex:1;min-width:120px}
.row output{flex:0 0 72px;text-align:right;color:var(--a)}
button,select,input[type=number]{background:#1a1f29;color:var(--t);border:1px solid #2d3441;border-radius:3px;padding:8px 12px;font:inherit}
button:active{background:#262d3a}
button.pri{background:#1f3a2b;border-color:#2b5a40;color:var(--a)}
button.stop{background:#4a1d1d;border-color:#8a3a3a;color:#ffd0d0;font-weight:700;padding:14px 18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:6px}
.kv{border:1px solid var(--b);padding:6px 8px;border-radius:3px}.kv span{display:block;color:var(--s);font-size:10px;letter-spacing:1px;text-transform:uppercase}.kv b{font-size:16px}
#vidbox{background:#000;border:1px solid var(--b);min-height:120px;display:flex;justify-content:center}
#vid{max-width:100%;max-height:60vh}
#joy{width:220px;height:220px;border:1px solid #2d3441;border-radius:50%;position:relative;touch-action:none;background:radial-gradient(#171c25,#0c0f14);margin:6px auto}
#knob{width:64px;height:64px;border-radius:50%;background:#2c3646;border:1px solid #4a566a;position:absolute;left:78px;top:78px;pointer-events:none}
.dpad{display:grid;grid-template-columns:repeat(3,64px);gap:6px;justify-content:center}.dpad button{height:54px;font-size:20px;padding:0}
small{color:var(--s)}
</style></head><body>
<header><b id="poc">ROVER POC</b><span><span class="pill" id="net">-</span> <span class="pill" id="wsp">WS</span> <span class="pill" id="lnk">NANO</span></span></header>

<section id="pCam" hidden>
 <h2>Video &mdash; camera</h2>
 <div id="vidbox"><img id="vid" alt=""></div>
 <div class="row"><button class="pri" onclick="video(1)">Iniciar video</button><button onclick="video(0)">Parar video (esfria)</button><button onclick="snap()">Foto</button>
  <span class="pill" id="cmodo">-</span></div>
 <div class="grid" id="cstats"></div>
 <div class="row" style="margin-top:8px"><small>Presets:</small>
  <button onclick="preset('frio')">Frio</button><button onclick="preset('equilibrado')">Equilibrado</button><button onclick="preset('qualidade')">Qualidade</button><button onclick="preset('maximo')">Maximo</button></div>
 <div id="cform"></div>
 <div class="row"><button class="pri" onclick="aplicarCam(0)">Aplicar</button><button onclick="aplicarCam(1)">Aplicar e salvar (flash)</button></div>
 <small>Termico = temperatura do chip ESP32-S3 (o OV5640 nao tem leitura propria). So 1 espectador de video por vez.</small>
</section>

<section id="pServo" hidden>
 <h2>Pan / Tilt</h2>
 <div class="row"><label>Pan (graus)</label><input type="range" id="pan" min="0" max="180" step="0.5" value="90"><output id="panO">90</output></div>
 <div class="row"><label>Tilt (graus)</label><input type="range" id="tilt" min="0" max="180" step="0.5" value="90"><output id="tiltO">90</output></div>
 <div class="row"><label>Velocidade do movimento</label><input type="range" id="vel" min="0" max="300" step="5" value="0"><output id="velO">padrao</output></div>
 <div class="row"><button class="pri" onclick="mover(90,90,0)">Centro 90/90</button><button onclick="mover(90,+$('tilt').value,0)">Pan 90</button><button onclick="mover(+$('pan').value,90,0)">Tilt 90</button></div>
 <h2 style="margin-top:12px">Teste do "rebolado" (varredura em velocidade constante)</h2>
 <div class="row"><label>Eixo</label><select id="swE"><option value="pan">Pan</option><option value="tilt">Tilt</option></select>
  <label style="flex:0 0 auto">de</label><input type="number" id="swA" value="45" style="width:70px"><label style="flex:0 0 auto">ate</label><input type="number" id="swB" value="135" style="width:70px"></div>
 <div class="row"><label>Velocidade (graus/s)</label><select id="swV"><option>5</option><option>10</option><option selected>20</option><option>45</option><option>90</option></select>
  <label style="flex:0 0 auto">ida-e-volta x</label><input type="number" id="swN" value="3" style="width:60px"></div>
 <div class="row"><button class="pri" onclick="varredura()">Iniciar varredura</button><button onclick="sweepOn=false">Parar</button><span id="swS" class="pill">-</span></div>
 <h2 style="margin-top:12px">Ajuste fino (tempo real no Nano)</h2>
 <div id="tuneServo"></div>
 <div class="row"><button class="pri" onclick="aplicarServo()">Aplicar ajustes</button><small>Piso de aproximacao alto = menos stick-slip. Antifolga &gt; 0 faz o servo chegar sempre pelo mesmo lado.</small></div>
</section>

<section id="pMotor" hidden>
 <h2>Motores 4WD</h2>
 <div class="row"><label>Limite de velocidade</label><input type="range" id="lim" min="10" max="100" value="45"><output id="limO">45%</output></div>
 <div id="joy"><div id="knob"></div></div>
 <div class="dpad">
  <span></span><button data-v="1,0">&#9650;</button><span></span>
  <button data-v="0,-1">&#9664;</button><button data-v="0,0">&#9632;</button><button data-v="0,1">&#9654;</button>
  <span></span><button data-v="-1,0">&#9660;</button><span></span>
 </div>
 <div class="row" style="justify-content:center;margin-top:10px"><button class="stop" id="btnStop">PARADA IMEDIATA</button></div>
 <small>Segure para andar; soltou = rampa ate parar. Teclado: WASD / setas, espaco = parada. Sem comando por 600 ms o Nano desacelera sozinho (watchdog).</small>
 <h2 style="margin-top:12px">Rampa e protecoes</h2>
 <div id="tuneMot"></div>
 <div class="row"><button class="pri" onclick="aplicarMotor()">Aplicar</button></div>
 <div class="grid" id="mstats"></div>
</section>

<section id="pSys"><h2>Sistema</h2><div class="grid" id="sys"></div></section>

<script>
const $=id=>document.getElementById(id), sleep=ms=>new Promise(r=>setTimeout(r,ms));
let caps=[],ws=null,sweepOn=false,info={};
const j=async u=>{try{const r=await fetch(u);return await r.json()}catch(e){return null}};
function conectarWS(){
  ws=new WebSocket('ws://'+location.hostname+':81/');
  ws.onopen=()=>{$('wsp').className='pill ok'};
  ws.onclose=()=>{$('wsp').className='pill bad';setTimeout(conectarWS,1000)};
}
function tx(f){ if(ws&&ws.readyState===1) ws.send(f); else fetch('/api/cmd?f='+encodeURIComponent(f)).catch(()=>{}); }
function fld(id,label,min,max,step,val,fmt){return `<div class="row"><label>${label}</label><input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${val}"><output id="${id}O">${fmt?fmt(val):val}</output></div>`}
function bind(id,fmt){const e=$(id);e.oninput=()=>{$(id+'O').textContent=fmt?fmt(e.value):e.value};}

/* ---------------- servo ---------------- */
const TUNE_SERVO=[['t1','Vel. padrao (graus/s)',5,400,5,145,1],['t2','Piso de aproximacao (graus/s)',0,60,1,15,2],['t3','Aceleracao (graus/s2)',50,3000,50,870,3],
  ['t4','Banda morta (us)',0,10,1,2,4],['t5','Antifolga (us, 0=off)',0,100,2,0,5],['t6','Soltar parado (s, 0=nunca)',0,30,1,0,6]];
let lastS=0,pend=null;
function enviarServo(){
  const v=Math.round(+$('vel').value*10);
  tx(`<S,${Math.round($('pan').value*10)},${Math.round($('tilt').value*10)},${v}>`);
}
function agendar(){const n=Date.now();if(n-lastS>40){lastS=n;enviarServo()}else{clearTimeout(pend);pend=setTimeout(()=>{lastS=Date.now();enviarServo()},45)}}
function mover(p,t,v){$('pan').value=p;$('tilt').value=t;$('panO').textContent=p;$('tiltO').textContent=t;const old=$('vel').value;tx(`<S,${Math.round(p*10)},${Math.round(t*10)},${Math.round(v*10)}>`)}
async function varredura(){
  sweepOn=true;const e=$('swE').value,a=+$('swA').value,b=+$('swB').value,v=+$('swV').value,n=+$('swN').value;
  let pan=+$('pan').value,tilt=+$('tilt').value;
  const go=async(ang,vel)=>{const cur=e==='pan'?pan:tilt;if(e==='pan')pan=ang;else tilt=ang;$(e).value=ang;$(e+'O').textContent=ang;
    tx(`<S,${Math.round(pan*10)},${Math.round(tilt*10)},${Math.round(vel*10)}>`);
    const ms=Math.abs(ang-cur)/vel*1000+500;const t0=Date.now();while(Date.now()-t0<ms){if(!sweepOn)return false;await sleep(50)}return true};
  $('swS').textContent='indo ao inicio';if(!await go(a,60)){$('swS').textContent='parado';return}
  for(let i=1;i<=n;i++){
    $('swS').textContent=`ciclo ${i}/${n} ida @${v}`;if(!await go(b,v)){$('swS').textContent='parado';return}
    $('swS').textContent=`ciclo ${i}/${n} volta @${v}`;if(!await go(a,v)){$('swS').textContent='parado';return}
  }
  sweepOn=false;$('swS').textContent='concluido';
}
async function aplicarServo(){for(const [id,,,,,,cid] of TUNE_SERVO){tx(`<C,${cid},${Math.round(+$(id).value)}>`);await sleep(45)}}

/* ---------------- motores ---------------- */
const TUNE_MOT=[['m1','Rampa 0-100% (ms)',100,3000,50,800,10],['m2','PWM minimo (partida)',0,120,5,60,11],['m3','PWM maximo',50,255,5,255,12],['m4','Tempo morto na reversao (ms)',0,600,10,150,13],['m5','Watchdog (ms)',200,3000,100,600,14]];
let vec=[0,0],mtimer=null,keys={};
function enviarMotor(){const lim=+$('lim').value/100*255;let x=vec[1],y=vec[0];let l=y+x,r=y-x;const m=Math.max(1,Math.abs(l),Math.abs(r));l/=m;r/=m;
  const k=Math.hypot(x,y);const esc=Math.min(1,k);tx(`<M,${Math.round(l*esc*lim)},${Math.round(r*esc*lim)}>`)}
function setVec(y,x){vec=[y,x];if(y||x){if(!mtimer){enviarMotor();mtimer=setInterval(enviarMotor,100)}}else{if(mtimer){clearInterval(mtimer);mtimer=null}tx('<M,0,0>')}}
function iniciarMotor(){
  const joy=$('joy'),kn=$('knob');
  const mv=e=>{const r=joy.getBoundingClientRect(),R=r.width/2;let dx=(e.clientX-r.left-R)/R,dy=(e.clientY-r.top-R)/R;const d=Math.hypot(dx,dy);if(d>1){dx/=d;dy/=d}
    kn.style.left=(78+dx*78)+'px';kn.style.top=(78+dy*78)+'px';setVec(-dy,dx)};
  joy.onpointerdown=e=>{joy.setPointerCapture(e.pointerId);mv(e);joy.onpointermove=mv};
  const fim=()=>{joy.onpointermove=null;kn.style.left='78px';kn.style.top='78px';setVec(0,0)};
  joy.onpointerup=fim;joy.onpointercancel=fim;
  document.querySelectorAll('.dpad button').forEach(b=>{const [y,x]=b.dataset.v.split(',').map(Number);
    b.onpointerdown=e=>{b.setPointerCapture(e.pointerId);setVec(y,x)};b.onpointerup=()=>setVec(0,0);b.onpointercancel=()=>setVec(0,0)});
  $('btnStop').onclick=()=>{setVec(0,0);tx('<X>')};
  addEventListener('keydown',e=>{if(e.repeat)return;const k=e.key.toLowerCase();if(k===' '){tx('<X>');return}keys[k]=1;kb()});
  addEventListener('keyup',e=>{delete keys[e.key.toLowerCase()];kb()});
  addEventListener('blur',()=>{keys={};kb()});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){setVec(0,0);tx('<X>')}});
}
function kb(){const y=(keys.w||keys.arrowup?1:0)-(keys.s||keys.arrowdown?1:0),x=(keys.d||keys.arrowright?1:0)-(keys.a||keys.arrowleft?1:0);if(y||x||vec[0]||vec[1])setVec(y,x)}
async function aplicarMotor(){for(const [id,,,,,,cid] of TUNE_MOT){tx(`<C,${cid},${Math.round(+$(id).value)}>`);await sleep(45)}}

/* ---------------- camera ---------------- */
const BLANK='data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';
const CAMF=[['res','Resolucao','sel'],['q','Qualidade JPEG (maior = mais leve)',8,45,1],['xclk','XCLK ativo (MHz)',6,20,1],['xclk_eco','XCLK eco (MHz)',6,20,1],['xclk_t','XCLK termico (MHz)',6,20,1],
 ['fps','Teto FPS ativo',1,30,1],['fps_eco','Teto FPS eco',1,30,1],['fps_t','Teto FPS termico',1,30,1],['sleep_s','Soneca sem espectador (s, 0=off)',0,60,1],['eco_s','Eco sem comandos (s, 0=off)',0,120,1],
 ['t_alerta','Temp. alerta chip (C)',45,95,1],['t_corte','Temp. corte chip (C)',50,100,1],['bright','Brilho',-2,2,1],['gov','Governador termico (0/1)',0,1,1],['hmirror','Espelhar H (0/1)',0,1,1],['vflip','Inverter V (0/1)',0,1,1]];
const RES=['qqvga','hqvga','qvga','cif','vga','svga','hd'],RESD=['160x120','240x176','320x240','400x296','640x480','800x600','1280x720'];
function montarCam(){let h='';for(const f of CAMF){if(f[2]==='sel')h+=`<div class="row"><label>${f[1]}</label><select id="c_res">${RES.map((r,i)=>`<option value="${r}">${r.toUpperCase()} ${RESD[i]}</option>`).join('')}</select></div>`;
  else h+=fld('c_'+f[0],f[1],f[2],f[3],f[4],f[2]);}
  $('cform').innerHTML=h;for(const f of CAMF)if(f[2]!=='sel')bind('c_'+f[0]);}
function preencherCam(c){if(!c)return;for(const f of CAMF){const e=$('c_'+f[0]);if(!e)continue;e.value=c[f[0]];if(f[2]!=='sel')$('c_'+f[0]+'O').textContent=c[f[0]]}}
async function cfgCam(){preencherCam(await j('/api/cam/cfg'))}
async function aplicarCam(save){const p=CAMF.map(f=>f[0]+'='+encodeURIComponent($('c_'+f[0]).value)).join('&');preencherCam(await j('/api/cam/set?'+p+(save?'&save=1':'')))}
async function preset(n){preencherCam(await j('/api/cam/preset?n='+n))}
function video(on){$('vid').src=on?('http://'+location.hostname+':82/stream?t='+Date.now()):BLANK}
function snap(){window.open('http://'+location.hostname+':82/capture?t='+Date.now())}

/* ---------------- telemetria ---------------- */
const kv=(k,v,c)=>`<div class="kv"><span>${k}</span><b class="${c||''}">${v}</b></div>`;
const RST=f=>f<0?'-':(f&4?'BROWN-OUT':f&8?'watchdog':f&1?'power-on':f&2?'externo':'?');
async function stats(){
  const s=await j('/api/stats');if(!s){$('net').className='pill bad';$('net').textContent='sem resposta';return}
  $('net').className='pill ok';$('net').textContent=`${info.ip||''} ${s.sys.rssi}dBm`;
  const l=s.link;if(l){const ok=l.hb_age>=0&&l.hb_age<2500;$('lnk').className='pill '+(ok?'ok':'bad');$('lnk').textContent=ok?'NANO ok':'NANO sem resposta'}
  let h=kv('Chip',s.sys.temp.toFixed(1)+' C',s.sys.temp>=68?'warn':'')+kv('CPU',s.sys.cpu+' MHz')+kv('Heap livre',(s.sys.heap/1024).toFixed(0)+' kB')+kv('PSRAM livre',(s.sys.psram/1048576).toFixed(1)+' MB')+kv('Ligado',s.sys.up+' s');
  if(l)h+=kv('Quadros TX/RX',l.tx+' / '+l.rx)+kv('Erros RX',l.err)+kv('Ultimo reset Nano',RST(l.reset),l.reset&4?'bad':'');
  $('sys').innerHTML=h;
  if(s.cam){const c=s.cam;$('cmodo').textContent=c.modo+(c.forcado?' (superaquecido)':'');$('cmodo').className='pill '+(c.modo==='ATIVO'?'ok':c.modo==='TERMICO'||c.forcado?'bad':'warn');
    $('cstats').innerHTML=kv('FPS entregue',c.fps.toFixed(1),c.fps<c.teto_fps*0.7&&c.clientes?'warn':'')+kv('Teto FPS',c.teto_fps)+kv('Debito',c.kbps.toFixed(0)+' kbit/s')+kv('kB / quadro',c.kb_frame.toFixed(1))+kv('Captura',c.cap_ms.toFixed(1)+' ms')+kv('XCLK',c.xclk+' MHz')+kv('Resolucao',c.res_px)+kv('Espectadores',c.clientes)+kv('Soneca',c.dormindo?'sim (frio)':'nao')}
  if(l&&caps.includes('motor'))$('mstats').innerHTML=kv('Bateria',(l.vbat/1000).toFixed(2)+' V',l.vbat&&l.vbat<6600?'warn':'')+kv('Minimo (queda)',(l.vmin/1000).toFixed(2)+' V',l.vmin&&l.vmin<6000?'bad':'')+kv('Saida esq / dir',l.mot_e+' / '+l.mot_d);
}
async function init(){
  info=await j('/api/info')||{};caps=info.caps||[];$('poc').textContent=(info.poc||'ROVER POC').toUpperCase();
  if(caps.includes('cam')){$('pCam').hidden=false;montarCam();cfgCam();video(1)}
  if(caps.includes('servo')){$('pServo').hidden=false;
    $('tuneServo').innerHTML=TUNE_SERVO.map(t=>fld(t[0],t[1],t[2],t[3],t[4],t[5])).join('');TUNE_SERVO.forEach(t=>bind(t[0]));
    for(const id of ['pan','tilt']){$(id).oninput=()=>{$(id+'O').textContent=$(id).value;agendar()}}
    $('vel').oninput=()=>{$('velO').textContent=$('vel').value==0?'padrao':$('vel').value+'/s'}}
  if(caps.includes('motor')){$('pMotor').hidden=false;
    $('tuneMot').innerHTML=TUNE_MOT.map(t=>fld(t[0],t[1],t[2],t[3],t[4],t[5])).join('');TUNE_MOT.forEach(t=>bind(t[0]));
    $('lim').oninput=()=>{$('limO').textContent=$('lim').value+'%'};iniciarMotor()}
  if(caps.includes('servo')||caps.includes('motor'))conectarWS();
  stats();setInterval(stats,1000);
}
init();
</script></body></html>)HTML";
