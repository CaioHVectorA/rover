// Executa o JavaScript real do painel com relogio e eventos simulados.
// Nao acessa placas nem envia comandos a rede.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, '../src/firmware/comum/esp_painel.h'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

class Target {
  constructor() {
    this.listeners = {}; this.style = {}; this.value = '120'; this.parentElement = {style:{}};
    this.classList = {
      add: c => { if (c === 'hidden') this.style.display = 'none'; },
      remove: c => { if (c === 'hidden') this.style.display = 'grid'; }
    };
  }
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
  const context = vm.createContext({performance:{now:()=>now}, window, document, location:{hostname:'rover.test'},
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

// Gestos reais do painel: direções, debounce, parada, perda de mão e trava.
{
  const a = ambiente();
  a.run("var direcoes=[]; drive=(f,t)=>direcoes.push([f,t]);");
  a.run("processarComandoGesto('aberta')");
  assert.equal(a.run('direcoes.length'), 0);
  a.run("processarComandoGesto('aberta')");
  assert.equal(a.run('direcoes.at(-1)[0]'), .85);
  a.run("processarComandoGesto('punho');processarComandoGesto('punho')");
  assert.equal(a.run('direcoes.at(-1)[0]'), -.85);
  a.advance(699);
  assert.equal(a.run('direcoes.at(-1)[0]'), -.85, 'Deve tolerar ausência menor que 700 ms');
  a.advance(1);
  assert.equal(a.run('direcoes.at(-1)[0]'), 0, 'Perda de mão deve parar');
  a.run("processarComandoGesto('aberta');processarComandoGesto('aberta')");
  for(let i=0;i<47;i++) { a.advance(100); a.run("processarComandoGesto('aberta')"); }
  assert.equal(a.run('gestoPausaSeguranca'), true);
  assert.equal(a.run('direcoes.at(-1)[0]'), 0);
  a.run("processarComandoGesto('punho');processarComandoGesto('punho')");
  assert.equal(a.run('direcoes.at(-1)[0]'), 0, 'Punho não pode liberar a trava');
  a.run("processarComandoGesto('apontar')");
  assert.equal(a.run('gestoPausaSeguranca'), false);
  a.run("processarComandoGesto('punho');processarComandoGesto('punho')");
  assert.equal(a.run('direcoes.at(-1)[0]'), -.85);
  a.run("processarComandoGesto('joia')");
  assert.equal(a.run('direcoes.at(-1)[0]'), 0);
  console.log('OK: aberta frente, punho ré, debounce, watchdog, teto, rearme e parada.');
}

// O mesmo V comanda os dois sentidos pela posição normalizada no vídeo.
{
  const a = ambiente();
  a.run("var direcoes=[]; drive=(f,t)=>direcoes.push([f,t]);");
  a.run("processarComandoGesto('paz', .2)");
  assert.equal(a.run('direcoes.length'), 0, 'Dois quadros exigidos no início');
  a.run("processarComandoGesto('paz', .2)");
  assert.equal(a.run('direcoes.at(-1)[1]'), -.75);
  a.run("processarComandoGesto('paz', .38)");
  assert.equal(a.run('direcoes.at(-1)[1]'), -.75, 'Histerese mantém lado perto da borda');
  a.run("processarComandoGesto('paz', .5)");
  assert.equal(a.run('direcoes.at(-1)[1]'), 0, 'Centro para no primeiro quadro');
  a.run("processarComandoGesto('paz', .62);processarComandoGesto('paz', .62)");
  assert.equal(a.run('direcoes.at(-1)[1]'), 0, 'Não iniciar giro dentro da margem');
  a.run("processarComandoGesto('paz', .8);processarComandoGesto('paz', .8)");
  assert.equal(a.run('direcoes.at(-1)[1]'), .75);
  a.advance(699);
  assert.equal(a.run('direcoes.at(-1)[1]'), .75);
  a.advance(1);
  assert.equal(a.run('direcoes.at(-1)[1]'), 0, 'Perda da mão por 700 ms para o giro');
  for (const x of ['null', 'NaN', 'Infinity', '-.1', '1.1']) {
    a.run("processarComandoGesto('paz', .2);processarComandoGesto('paz', .2)");
    a.run(`processarComandoGesto('paz', ${x})`);
    assert.equal(a.run('direcoes.at(-1)[1]'), 0, 'Coordenada inválida não pode girar');
  }
  a.run("processarComandoGesto('paz', .2);processarComandoGesto('paz', .2)");
  for(let i=0;i<47;i++) { a.advance(100); a.run("processarComandoGesto('paz', .2)"); }
  assert.equal(a.run('gestoPausaSeguranca'), true);
  a.run("processarComandoGesto('paz', .5);processarComandoGesto('paz', .8);processarComandoGesto('paz', .8)");
  assert.equal(a.run('direcoes.at(-1)[1]'), 0, 'Centro e lado oposto não rearmam a trava');
  a.run("processarComandoGesto('apontar');processarComandoGesto('paz', .8);processarComandoGesto('paz', .8)");
  assert.equal(a.run('direcoes.at(-1)[1]'), .75);
  a.run("processarComandoGesto('tres')");
  assert.equal(a.run('direcoes.at(-1)[1]'), 0, 'Três dedos não comandam mais giro');
  // O conversor precisa usar os offsets do zoom, não o centro do recorte.
  a.run("classificarGestoMao=()=>({id:'paz', label:'V', mira:[25,25]}); var pontos=Array.from({length:21},(_,i)=>[25,i]);");
  a.run("converterPredsMao([{landmarks:pontos}],100,100,.25,0,.5);converterPredsMao([{landmarks:pontos}],100,100,.25,0,.5)");
  assert.equal(a.run('direcoes.at(-1)[1]'), 0, 'Zoom: .25 + .25*.5 = .375, não aciona lado desde o centro');
  const result = a.run("converterPredsMao([{landmarks:pontos}],100,100,.25,0,.5)");
  assert.equal(result[0].maoX, .375);
  assert.equal(result[0].cx, .375);
  console.log('OK: V por posição, centro, histerese, zoom, coordenadas inválidas, 700 ms, trava e três dedos neutro.');
}

// Estudo Pan/Tilt: velocidade casada no joystick, estrategias suave/sacada/original, presets <C,2..4> e telemetria.
(async () => {
  const ultimoS = a => a.enviados.filter(s => s.startsWith('<S,')).at(-1);
  const velDeS = cmd => Number(cmd.replace(/[<>]/g, '').split(',')[3]);

  // 1. Joystick Pan/Tilt proporcional casa a velocidade (evita tiros de 420 deg/s para micro-deflexoes)
  {
    const a = ambiente();
    a.run('velServo = 150; curPTX = 0.2; curPTY = 0; joyPTTick();');
    const cmdFraco = ultimoS(a);
    assert.ok(cmdFraco, 'Joystick deve emitir <S>');
    assert.equal(velDeS(cmdFraco), 350, 'Deflexao 20% deve enviar vel casada ~35 deg/s (350)');
    a.run('curPTX = 1.0; curPTY = 0; joyPTTick();');
    assert.equal(velDeS(ultimoS(a)), 1730, 'Deflexao 100% deve enviar ~173 deg/s (1730)');
  }

  // 2. aplicarAutoTrack: original vs suave vs sacada
  {
    const a = ambiente();
    a.run('velServo = 150; pan = 90; tilt = 90; cvGanhoAuto = false;');
    a.run("mudarTrackModo('original');");
    a.advance(120);
    a.run('aplicarAutoTrack({cx: 0.85, cy: 0.5});');
    assert.equal(velDeS(ultimoS(a)), 4200, "Modo 'original' deve forcar minimo de 420 deg/s (4200)");

    a.run("mudarTrackModo('suave'); pan = 90; tilt = 90;");
    a.advance(120);
    a.run('aplicarAutoTrack({cx: 0.72, cy: 0.5});');
    const vSuave = velDeS(ultimoS(a));
    assert.ok(vSuave >= 500 && vSuave <= 2400, `Modo 'suave' deve enviar vel casada [500..2400], veio ${vSuave}`);
    a.run("mudarTrackModo('suave');");
    const totalAntesRuido = a.enviados.filter(s => s.startsWith('<S,')).length;
    a.advance(120);
    a.run('aplicarAutoTrack({cx: 0.525, cy: 0.48});');
    assert.equal(a.enviados.filter(s => s.startsWith('<S,')).length, totalAntesRuido, 'Ruido na deadzone nao deve emitir <S>');
    a.run('cvGanho = 3; cvGanhoAuto = false;');
    a.advance(120);
    a.run('aplicarAutoTrack({cx: 0.60, cy: 0.5});');
    a.advance(120);
    a.run('aplicarAutoTrack({cx: 0.60, cy: 0.5});');
    assert.equal(a.enviados.filter(s => s.startsWith('<S,')).length, totalAntesRuido, 'Micropasso menor que 0.45 deg nao deve emitir <S>');
    a.run('cvGanho = 22;');

    a.run("mudarTrackModo('sacada'); pan = 90; tilt = 90;");
    a.advance(120);
    a.run('aplicarAutoTrack({cx: 0.88, cy: 0.5});');
    const nPosSalto = a.enviados.filter(s => s.startsWith('<S,')).length;
    assert.equal(nPosSalto, totalAntesRuido + 1, "Modo 'sacada' deve emitir 1 salto inicial");
    assert.equal(a.run('cvSacadaLimparEma'), true, 'Sacada deve armar limpeza de EMA pos-acomodacao');
    a.advance(100);
    a.run('aplicarAutoTrack({cx: 0.99, cy: 0.99});');
    assert.equal(a.enviados.filter(s => s.startsWith('<S,')).length, nPosSalto, 'Quadros borrados durante pausa da sacada devem ser ignorados');
    a.advance(500);
    a.run('aplicarAutoTrack({cx: 0.50, cy: 0.50});');
    assert.equal(a.run('cvSacadaLimparEma'), false, 'Primeiro quadro nitido deve limpar EMA antiga');
    assert.equal(a.enviados.filter(s => s.startsWith('<S,')).length, nPosSalto, 'Alvo ja centrado pos-sacada permanece imovel e nitido');
  }

  // 3. Presets Nano <C,2..4> e ciclo do estudo + telemetria
  {
    const a = ambiente();
    a.run('aplicarNanoPreset(45, 1400, 4);');
    assert.ok(a.enviados.includes('<C,2,45>') && a.enviados.includes('<C,3,1400>') && a.enviados.includes('<C,4,4>'),
      'Preset Anti Stick-Slip deve enviar <C,2>, <C,3> e <C,4>');
  }
  {
    const a = ambiente();
    a.run(`var _httpLog = []; fetch = window.fetch = uri => {
      _httpLog.push(uri);
      if (uri.startsWith('/api/estudo/start')) return Promise.resolve({json: async () => ({ativo:1, modo:2, nome:'extremos', ciclos:3})});
      if (uri === '/api/stats') return Promise.resolve({json: async () => ({
        sys:{temp:42.5}, link:{retorno:true, hb_age:100, led:1},
        pt_tx:{n:42, dt:90, dp:5.4, v:64},
        estudo:{ativo:1, modo:4, nome:'passos_casados', ciclos:2},
        cam:{res:'qvga', xclk:16, fps:24.2, ae_level:-1}
      })});
      return Promise.resolve({json: async () => ({})});
    };`);
    await a.run('iniciarEstudo()');
    assert.ok(a.run('_httpLog').some(u => u.startsWith('/api/estudo/start?modo=')), 'iniciarEstudo deve chamar /api/estudo/start');
    assert.equal(a.run('estudoAtivo'), true);
    assert.equal(a.document.getElementById('stEstudo').textContent, 'EXTREMOS (3)');
    await a.run('atualizarStats()');
    assert.equal(a.document.getElementById('stEstudo').textContent, 'PASSOS_CASADOS (2)');
    assert.match(a.document.getElementById('lblTxPT').textContent, /#42.*dt:90ms.*d:5\.4°.*16MHz.*ae:-1/);
    a.run('parada()');
    assert.equal(a.run('estudoAtivo'), false);
    assert.ok(a.run('_httpLog').includes('/api/estudo/stop'), 'parada() deve interromper estudo ativo no ESP');
    assert.equal(a.enviados.at(-1), '<X>');
  }
  console.log('OK: estudo pan/tilt (joy proporcional, tracking suave/sacada/original, presets C2-C4 e telemetria).');
})().catch(e => { console.error(e); process.exitCode = 1; });
