// Executa o JavaScript real do painel com relogio e eventos simulados.
// Nao acessa placas nem envia comandos a rede.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, '../src/firmware/comum/esp_painel.h'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

class Target {
  constructor() { this.listeners = {}; this.style = {}; this.value = '120'; this.parentElement = {style:{}}; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  dispatchEvent(event) { for (const fn of this.listeners[event.type] || []) fn(event); }
  setPointerCapture() {}
  getBoundingClientRect() { return {left:0, top:0, width:120, height:120}; }
}
function ambiente() {
  let now = 0, id = 0;
  const timers = new Map(), nodes = new Map(), enviados = [], http = [];
  const window = new Target(), document = new Target();
  document.hidden = false;
  document.getElementById = name => {
    if (!nodes.has(name)) nodes.set(name, new Target());
    return nodes.get(name);
  };
  const timer = (fn, ms, repeat) => { const key = ++id; timers.set(key, {fn, at:now+ms, ms, repeat}); return key; };
  const context = vm.createContext({window, document, location:{hostname:'rover.test'},
    Event:class {constructor(type) {this.type=type;}},
    WebSocket:class {constructor() {this.readyState=1;} send(s) {enviados.push(s);}},
    fetch:uri => {http.push(uri); return Promise.resolve({json:async()=>uri==='/api/info'
      ? {controle:{retorno:false,pwm_max:120,pan_min:30,pan_max:150,tilt_min:40,tilt_max:140,vel_servo:150}}
      : {link:{retorno:false,hb_age:-1,led:0},cam:{}}});},
    setInterval:(fn,ms)=>timer(fn,ms,true), setTimeout:(fn,ms)=>timer(fn,ms,false),
    clearInterval:key=>timers.delete(key), clearTimeout:key=>timers.delete(key), console
  });
  const run = code => vm.runInContext(code, context);
  run(script);
  run('conectarWS();');
  function advance(ms) {
    const end = now + ms;
    for (let count=0; count<10000; ++count) {
      const next = [...timers.entries()].filter(([,t])=>t.at<=end).sort((a,b)=>a[1].at-b[1].at)[0];
      if (!next) {now=end; return;}
      const [key,t] = next; now=t.at;
      if (t.repeat) t.at+=t.ms; else timers.delete(key);
      t.fn();
    }
    throw new Error('Timer sem limite');
  }
  return {run, advance, enviados, http, nodes, document, window};
}
function movimentos(a) { return a.enviados.filter(s=>s.startsWith('<M,') && s!=='<M,0,0>'); }

{
  const a=ambiente();
  a.run('drive(1,0)'); a.advance(350);
  assert.equal(movimentos(a)[0], '<M,120,120>');
  assert.ok(movimentos(a).length>=4, 'Heartbeat deve renovar comando com dedo parado');
  a.run('parada()'); const total=movimentos(a).length; a.advance(1000);
  assert.equal(movimentos(a).length,total, 'Parada nao pode deixar heartbeat ativo');
  assert.equal(a.enviados.at(-1),'<X>');
}
{
  const a=ambiente();
  a.run('testeMotor(150,150,1000)'); a.advance(250);
  assert.ok(movimentos(a).every(s=>s==='<M,120,120>'), 'Teste deve respeitar PWM do slider');
  a.run('parada()'); const total=movimentos(a).length; a.advance(2000);
  assert.equal(movimentos(a).length,total, 'Emergencia deve cancelar teste programado');
}
{
  const a=ambiente(); a.run('testeMotor(150,150,1000)'); a.advance(1000);
  const total=movimentos(a).length; a.advance(1000);
  assert.equal(movimentos(a).length,total, 'Pulso deve terminar no tempo solicitado');
  assert.equal(a.enviados.at(-1),'<M,0,0>');
}
{
  const a=ambiente(); a.run('drive(1,0); ws.readyState=3; ws.onclose()');
  const total=movimentos(a).length; a.advance(1000);
  assert.equal(movimentos(a).length,total, 'Desconexao deve cancelar movimento');
  a.run("tx('<M,100,100>'); tx('<S,900,900>')");
  assert.ok(!a.http.some(uri=>uri.includes('M%2C100') || uri.includes('S%2C900')), 'Movimento nao pode usar fallback HTTP');
}
{
  const a=ambiente(); a.run('initJoysticks()');
  const drive=a.document.getElementById('joyDriveBase');
  const pt=a.document.getElementById('joyPTBase');
  drive.dispatchEvent({type:'pointerdown',pointerId:1,clientX:60,clientY:22});
  pt.dispatchEvent({type:'pointerdown',pointerId:2,clientX:98,clientY:60});
  pt.dispatchEvent({type:'pointerup',pointerId:2});
  const antes=movimentos(a).length; a.advance(200);
  assert.ok(movimentos(a).length>antes, 'Soltar pan/tilt nao deve interromper joystick de tracao');
  a.run('parada()'); const total=movimentos(a).length;
  drive.dispatchEvent({type:'pointermove',pointerId:1,clientX:60,clientY:22});
  a.advance(500);
  assert.equal(movimentos(a).length,total, 'Emergencia exige um novo toque para voltar a mover');
}
{
  const a=ambiente(); a.run('initJoysticks()');
  const drive=a.document.getElementById('joyDriveBase');
  drive.dispatchEvent({type:'pointerdown',pointerId:1,clientX:60,clientY:22});
  drive.dispatchEvent({type:'lostpointercapture',pointerId:1});
  const total=movimentos(a).length; a.advance(500);
  assert.equal(movimentos(a).length,total, 'Perda de captura do toque deve parar');
}
{
  const a=ambiente(); a.run('initJoysticks()');
  const drive=a.document.getElementById('joyDriveBase');
  const pt=a.document.getElementById('joyPTBase');
  drive.dispatchEvent({type:'pointerdown',pointerId:1,clientX:60,clientY:22});
  pt.dispatchEvent({type:'pointerdown',pointerId:2,clientX:98,clientY:60});
  const totalS=a.enviados.filter(s=>s.startsWith('<S,')).length;
  drive.dispatchEvent({type:'pointerup',pointerId:1});
  assert.equal(a.enviados.at(-1),'<M,0,0>', 'Soltar tracao deve parar apenas motores');
  a.advance(120);
  assert.ok(a.enviados.filter(s=>s.startsWith('<S,')).length>totalS, 'Pan/tilt deve continuar com o dedo mantido');
}
(async () => {
  const a=ambiente(); await a.window.onload();
  assert.equal(a.document.getElementById('viewJoy').style.display, 'grid');
  assert.equal(a.document.getElementById('rngPwmJoy').max, 120);
  assert.equal(a.document.getElementById('rngTilt').min, 40);
  assert.equal(a.document.getElementById('rngTilt').max, 140);
  assert.equal(a.document.getElementById('btnPing').hidden, true);
  assert.equal(a.document.getElementById('stNano').textContent, 'ENVIO → NANO');
  assert.match(a.document.getElementById('vid').src, /:82\/stream/);
  assert.equal(movimentos(a).length, 0, 'Abrir a pagina nao deve movimentar motores');
  await a.run('atualizarStats()');
  assert.equal(a.document.getElementById('stLed').textContent, 'CONFIRA D13');
  console.log('OK: heartbeat, limite PWM, parada, pulso, desconexao, multitouch, captura, perfil de ida e video.');
})().catch(e => {console.error(e); process.exitCode=1;});
