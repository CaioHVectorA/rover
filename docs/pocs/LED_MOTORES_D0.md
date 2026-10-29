# LED D13 e motores por ESP IO43 → BC337 → Nano D0

Par minimo preparado para a montagem atual. Combina o envio serial do POC 1
que acendeu o LED com os pinos e PWM bruto 120 do teste direto de motores
confirmado pelo usuario em 27/10/2026. A combinacao ainda precisa de teste fisico.

## Ligacao e funcionamento

- ESP **IO43 TX → BC337 → Nano D0/RX**, GND comum, **9600 baud**.
- O ESP inicia a UART com `Serial2.begin(9600, SERIAL_8N1, 44, 43, true)`,
  como no POC 1 que funcionou. A inversao no ESP compensa a inversao do BC337.
- O Nano usa somente a UART fisica `Serial` para receber no D0.
- O retorno D1 → ESP IO44 nao e necessario. O Nano nao envia respostas.
- Nao ha SoftwareSerial, camera ou servos neste par.
- Ao ligar/resetar o novo firmware, os motores ficam parados e o D13 apagado.
- Cada comando de motor produz PWM bruto **120/255** durante **1 segundo**.
  O proprio Nano desliga PWM e STBY ao terminar; a pagina nao precisa enviar a parada.
- Antes de cada novo pulso, as saidas ficam desligadas por 150 ms.

| TB6612 | Pino do Nano |
|---|---|
| PWMA | D3 |
| AIN1 / AIN2 | D4 / D5 |
| PWMB | D6 |
| BIN1 / BIN2 | D7 / D8 |
| STBY | D12 |
| LED onboard | D13 |

O sentido chamado "frente" usa IN1=HIGH e IN2=LOW nos dois canais,
exatamente como o teste direto que funcionou. A orientacao fisica depende
da ligacao dos motores e deve ser observada com as rodas suspensas.

## Arquivos e ambientes

- ESP: `src/firmware/testes_bancada/led_motores_d0/esp32/main.cpp`
  — ambiente `led_motores_d0_esp32`.
- Nano: `src/firmware/testes_bancada/led_motores_d0/nano/main.cpp`
  — ambiente `led_motores_d0_nano`.
- Constantes e validacao comuns: `src/firmware/testes_bancada/led_motores_d0/protocolo.h`.

Compilar os dois, sem gravar:

```powershell
pio run -e led_motores_d0_nano -e led_motores_d0_esp32
```

## Gravar quando quiser

Confira as portas com `pio device list`. As ultimas portas identificadas foram
COM7 para o Nano (CH340) e COM5 para o ESP (CH343); podem mudar.
Grave primeiro o Nano e depois o ESP:

```powershell
pio run -e led_motores_d0_nano -t upload --upload-port COM7
pio run -e led_motores_d0_esp32 -t upload --upload-port COM5
```

O D0 tambem e usado pelo conversor USB-serial do Nano. Se houver conflito na
gravacao, interrompa envios do ESP; pode ser necessario isolar o sinal do D0
durante o upload. Nao altere fiacao com a montagem energizada.

O ESP usa o arquivo local ignorado `src/firmware/comum/credenciais.h`,
configurado atualmente para `PET_PC 2902`. O IP e atribuido pelo roteador;
192.168.137.149 foi o ultimo observado no firmware integrado, nao e fixo. Sem conexao com a rede em 8 s,
o ESP abre `Rover-LED-Motores`, senha `12345678`, normalmente em 192.168.4.1.

## Testar

1. Com as rodas suspensas, abra o IP do ESP e atualize a pagina.
2. Confirme o titulo **LED D13 e motores**. `/api/info` deve identificar
   `led_motores_d0`, D0, 9600 baud e `retorno: false`.
3. Clique em **Ligar LED**, depois **Desligar LED** e **Piscar 5 vezes**.
   O indicador e o D13 fisico. Nao use o LED RX USB como prova de recepcao.
4. Clique em **Frente · 1 segundo**. O Nano aplica o mesmo PWM do teste direto
   e para automaticamente. Depois pode testar **Re · 1 segundo** e **PARAR MOTORES**.

A mensagem da pagina confirma somente que o ESP enviou o quadro. Nao existe
confirmacao de recepcao do Nano, heartbeat ou status "Nano online" neste enlace.

Quadros: `<L,1>` liga, `<L,0>` desliga, `<L,2>` pisca 5 vezes,
`<M,120,120>` frente, `<M,-120,-120>` re, `<X>` parada imediata.
O Nano rejeita PWM fora de -120..120 e comandos com quantidade incorreta de argumentos.

## Estado real da bancada

Compilacao de `led_motores_d0_esp32` e `led_motores_d0_nano` concluida com sucesso
em 27/10/2026. O Nano compilou sem dependencias externas. Tambem foram conferidos
os pinos contra `nano_motor_direto`, a inversao de TX contra o POC 1 e a sintaxe
JavaScript do painel com `node --check`. Isso nao substitui o teste fisico do par.

Apos a preparacao, o usuario autorizou a gravacao: em 27/10/2026, os dois
firmwares foram gravados com verificacao da flash (Nano COM7; ESP USB nativo COM8).
A API em 192.168.7.8 confirmou `firmware: led_motores_d0`, `nano_rx: D0`,
`tx_invertido: true` e `retorno: false`. O Nano agora fica parado no boot;
o teste automatico anterior foi substituido. Nesta gravacao nao foram enviados
comandos de motor ou LED. A recepcao fisica e o movimento ainda aguardam
confirmacao do usuario.
Posteriormente, o usuario confirmou que este par funcionou (LED e motores).
As placas foram entao atualizadas para o [Rover D0 integrado](ROVER_D0_INTEGRADO.md),
com pan/tilt, joysticks e video; o par minimo permanece disponivel para regressao.
A medicao anterior de 5 V em VIN e 4,1 V no pino 5V do Nano continua registrada
como pendencia de alimentacao; nao houve confirmacao posterior de correcao.
