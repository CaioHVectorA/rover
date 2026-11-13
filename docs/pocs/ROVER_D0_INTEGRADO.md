# Rover integrado D0: joysticks, motores, pan/tilt, LED e video

Par de firmware que amplia o teste `led_motores_d0` confirmado pelo usuario.
Mantem ESP IO43 TX -> BC337 -> Nano D0 RX, GND comum, UART fisica a 9600 baud
e enlace de ida. Nao requer fio de retorno D1 -> IO44 e nao usa SoftwareSerial.

## Firmware

- `src/firmware/testes_bancada/rover_d0/esp32/main.cpp`: ambiente `rover_d0_esp32`.
- `src/firmware/testes_bancada/rover_d0/nano/main.cpp`: ambiente `rover_d0_nano`.
- Painel e servidor reutilizam `esp_painel.h`, `esp_app.h` e `esp_camera_frio.h`.

```powershell
pio run -e rover_d0_nano -e rover_d0_esp32
pio device list
pio run -e rover_d0_nano -t upload --upload-port COM7
pio run -e rover_d0_esp32 -t upload --upload-port COM8
```

COM7/COM8 foram as portas desta gravacao; confira antes de repetir.
O ESP usa as credenciais locais ja configuradas para `PET_PC 2902`.
Ultimo IP observado apos a troca de rede: **192.168.137.149** (DHCP; pode mudar).
Pagina e API na porta 80, comandos WebSocket na 81, MJPEG na 82.

## Pinos e limites

| Funcao | Nano |
|---|---|
| PWMA / AIN1 / AIN2 | D3 / D4 / D5 |
| PWMB / BIN1 / BIN2 | D6 / D7 / D8 |
| STBY | D12 |
| LED onboard | D13 |
| Pan / Tilt | D9 / D10 |
| Serial RX do ESP | D0 |

- PWM bruto dos motores limitado a **120/255**, preservando o teste direto.
  Sem o remapeamento de PWM minimo da antiga classe de motores.
- Antes de arrancar ou inverter o sentido: 150 ms com as saidas desligadas.
  Pacotes recebidos durante essa espera atualizam o alvo sem reiniciar a espera.
- Sem novo comando de motor por **600 ms**, o Nano zera PWM e desabilita STBY.
  Comandos de servo/LED nao renovam esse prazo.
- Pan em **30 a 150 graus**; Tilt em **40 a 140 graus**. Estes sao limites
  conservadores do firmware, nao uma calibracao mecanica validada nesta sessao.
- Servos centralizam em **90 graus** no boot. PWM de servo por Timer1 no D9/D10;
  PWM dos motores continua em D3/D6, sem usar Timer1.
- Motores iniciam parados. LED D13 suporta ligar, desligar e piscar cinco vezes.

## Interface e teste

1. Atualize a pagina do IP do ESP para carregar a UI nova. `/api/info` deve
   identificar `rover_d0`, capacidades `cam`, `servo`, `motor`, e `retorno: false`.
2. O modo inicial tem dois joysticks: tracao a esquerda e pan/tilt a direita.
   Tambem existe o modo D-pad. O video e carregado automaticamente.
3. Confirme primeiro o D13 fisico; a interface exibe "CONFIRA D13" porque
   nao ha confirmacao de recepcao do Nano. "ENVIO -> NANO" nao e telemetria.
4. Com as rodas suspensas, teste os controles. Soltar a tracao para somente
   os motores; o pan/tilt continua caso o outro dedo permaneca no joystick.
5. PARADA IMEDIATA cancela os controles e comandos pendentes e exige novo toque
   para voltar a mover. Fechar/ocultar a pagina ou perder o WebSocket cancela
   os envios; o prazo de 600 ms no Nano cobre a perda do comando de parada.

Comandos de movimento usam somente WebSocket para evitar requisicoes HTTP
atrasadas provocando movimento apos soltar o controle. LED e parada ainda
podem usar o fallback HTTP. Os botoes de teste curto renovam o comando
a cada 100 ms e param ao fim do intervalo ou ao cancelar o teste.

## Evidencia desta entrega — 27/10/2026

- Usuario confirmou que LED e motores funcionaram juntos no par anterior
  `led_motores_d0`; essa confirmacao motivou a integracao.
- `rover_d0_nano` e `rover_d0_esp32` compilados e gravados com verificacao de flash
  (Nano COM7; ESP COM8). Nano compilou sem dependencias externas.
- Testes do JavaScript real em `tools/verificar_joysticks_rover.cjs`: heartbeat,
  limite de PWM, parada, cancelamento de teste temporizado, desconexao,
  independencia dos dois joysticks, multitouch, perda de captura, perfil de ida,
  limites de servo e carregamento do endereco de video.
- API ao vivo confirmou `rover_d0`, PWM maximo 120, limites de servos e enlace
  de ida. Camera reportou OV5640 ativa, QVGA 320x240, 13 fps e um cliente,
  com contador de quadros aumentando. Nao foi necessario abrir outro stream.
- A recompilacao do ambiente anterior `testes_bancada_esp32` tambem passou,
  conferindo a compatibilidade das alteracoes nos modulos compartilhados.
  A pinagem de motores foi comparada ao sketch direto confirmado pelo usuario.
- Nao foram enviados comandos de motor, servo ou LED pelo agente durante
  a verificacao desta entrega. Movimento mecanico conjunto aguarda observacao
  do usuario; dados de envio do ESP nao comprovam recepcao no Nano.
- A leitura anterior de 4,1 V no pino 5V do Nano permanece no historico;
  nao houve confirmacao explicita de correcao da alimentacao nesta sessao.

## Atualização local do painel — 10/11/2026

Visual sem emojis, paleta preservada e temperatura interna do chip ESP sobre o
vídeo, atualizada pela API de estatísticas. Sem conexão, indica `ESP -- °C`.
Gestos: mão aberta = frente; mão fechada = ré; V à esquerda/direita do vídeo = giros; V no centro = parar; três dedos sem movimento; apontar ou
polegar = parar/rearmar. Perder a mão por 700 ms interrompe o movimento; teto contínuo
permanece 4,5 s, com rearme por gesto de parada. Botão PARADA IMEDIATA mantido.
Compilação e testes locais aprovados. Upload desta atualização concluído na COM29 em 10/11/2026, com flash verificada.

## Preparar modelos (nova versão local)

1. Na primeira preparação, use internet no dispositivo que abrirá o painel.
2. Abra o vídeo, enquadre rosto e mão, expanda Visão Computacional e clique em
   **PREPARAR MODELOS**. O botão seleciona Leve e desliga comandos gestuais.
3. Espere o estado PRONTO. Se pedir rosto/mão ou vídeo, corrija enquadramento e
   repita. Ative Rosto + Gestos para ensaiar; habilite comandos somente depois.

Bibliotecas e arquivos dos modelos são guardados em IndexedDB. Testado com os
modelos reais carregando após recarga sem rede externa. Use o mesmo navegador,
dispositivo e endereço do painel; apagar dados ou mudar IP/hostname perde acesso
a esse cache. Mantenha a aba aberta para preservar também os modelos inicializados.
Cache reduz downloads; não elimina o custo de inferência nem garante FPS.
Nenhum download manual é necessário no fluxo implementado. Sem armazenamento
local disponível, a carga depende de internet.

Atualização gravada no ESP pela COM29 em 10/11/2026, com hash da flash verificado. Nano preservado. Último endereço conhecido: http://192.168.137.233/; o acesso HTTP após este upload não foi confirmado pelo PC.

## Estudo de caso: Jitter no Pan/Tilt e Motion Blur (branch `exp/estudo-jitter-pantilt`)

Preparado exclusivamente no firmware do ESP32 (`rover_d0_esp32` + módulos `comum/`), mantendo 100% de compatibilidade com o `rover_d0_nano` atual (sem regravar o Nano):

- **Gerador determinístico no ESP32 (`esp_estudo_pt.h`):** reproduz no `loop()` do ESP (sem variação de Wi-Fi/navegador) 4 ensaios: `Pulso 1x` (`<S>` único por trecho), `Radar Extremos`, `Radar Bug 90ms (420°/s)` e `Radar Passos Casados` (horizonte à frente + velocidade casada). Rotas `/api/estudo/start` e `/api/estudo/stop`.
- **Telemetria do fluxo `<S>` e Câmera (`esp_enlace.h`, `esp_camera_frio.h`, `esp_app.h`):** `/api/stats` expõe `pt_tx` (`n`, `dt`, `dp`, `v`), estado de `estudo` e `cam.ae_level` (`-2..2`) + preset `cv_rapida` (`QVGA`, `XCLK 16MHz`, `fps=24`, `ae_level=-1`).
- **Painel de bancada (`esp_painel.h`):** card retrátil **Estudo Jitter Pan/Tilt** (acessível também pelo botão `Jitter` em paisagem), controle ao vivo de `C2`/`C3`/`C4` (`velMin`, `acc`, `deadUs` já aceitos pelo Nano), joystick Pan/Tilt com velocidade proporcional à deflexão e 3 estratégias de Auto-Tracking para comparação A/B (`Suave` com velocidade casada, `Sacada Anti-Blur` move+pausa para visão nítida, e `Original` 420°/s).
- **Status de verificação:** suíte JS (`tools/verificar_joysticks_rover.cjs`) e checagem de sintaxe/estado em C++ executadas no ambiente virtual; compilação PlatformIO (`pio run -e rover_d0_esp32`) e ensaios físicos em bancada pendentes de execução local no robô.

