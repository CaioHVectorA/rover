# Diagnóstico serial de bancada — 10/11/2026

## Montagem informada e resultado

O usuário confirmou **somente os dois cabos USB no PC**, sem jumpers entre ESP e
Nano. O Nano está fora da placa com BC337. Nessa montagem, o PC pode acessar cada
placa, mas não existe um enlace UART entre elas. Não há ponte USB automática no
firmware atual ou no servidor relay.

| Placa | Porta observada | Evidência |
|---|---|---|
| Nano CH340, VID:PID `1A86:7523` | COM26 | Bootloader respondeu a 57600 baud; assinatura ATmega328P `0x1e950f`; flash lida sem gravação |
| ESP32-S3 USB nativo, VID:PID `303A:1001` | COM29 | Logs USB a 115200 baud com `[AUTO] Enviando <L,0>` / `<L,1>` a cada dois segundos |

As portas podem mudar após reconexão.

## Firmware realmente identificado

- **Nano:** os 8818 bytes presentes no HEX recompilado de `rover_d0_nano`
  coincidiram integralmente com a leitura da flash. Fonte:
  [rover_d0/nano/main.cpp](../../src/firmware/testes_bancada/rover_d0/nano/main.cpp).
  Recebe quadros ASCII pelo D0 a **9600 baud**, controla D13, servos e motores,
  e não transmite respostas pelo D1. Monitor serial vazio é esperado.
- **ESP:** os logs recebidos correspondem ao
  [teste_inversao/esp32/main.cpp](../../src/firmware/testes_bancada/teste_inversao/esp32/main.cpp),
  que alterna comandos de LED automaticamente e aceita `i`, `1`, `0`, `2` pela
  USB. Esse teste não inicializa Wi-Fi, painel ou câmera. A identificação veio
  dos logs característicos; a flash do ESP não foi comparada.
- O teste do ESP inicia com inversão `true`, mas aceita alternância em execução.
  **A polaridade atual não foi consultada nem alterada nesta sessão.**
- O teste de inversão consegue comandar o LED do firmware Nano identificado,
  desde que o caminho físico e a polaridade estejam corretos; não é necessário
  trocar o Nano apenas por o ESP estar em um teste isolado.

## D0/RX e USB: onde existe conflito

O UART físico do Nano é o mesmo usado pelo conversor CH340: D0 recebe dados e
D1 transmite. Ao conectar também a saída do circuito do ESP em D0, há duas
fontes ligadas à mesma entrada. Enviar pela USB enquanto o ESP/circuito está
ligado pode causar disputa elétrica e dados corrompidos.

Fechar o monitor serial não isola eletricamente o CH340. A influência do nível
de repouso depende da implementação e dos resistores da placa Nano real, que
não foram inspecionados nesta sessão. Não afirmar que todo cabo USB conectado
necessariamente impede a comunicação, nem que leitura pelo monitor garante
ausência de conflito.

Para isolar o teste do enlace já validado, alimentar o Nano pela montagem
correta de 5V, com **USB do Nano desconectado**, e manter a USB nativa do ESP
para logs. Para gravar ou testar o Nano pela USB, desconectar a entrada externa
do D0. Não é preciso mudar para SoftwareSerial para fazer esse diagnóstico.

Referência oficial: [Arduino — interferência nos pinos 0/1 durante upload](https://support.arduino.cc/hc/en-us/articles/4401874331410--Error-avrdude-when-uploading).

## Pinagem e polaridade: variantes que não podem ser misturadas

| Caminho físico de ida | Receptor Nano | Inversão no TX ESP necessária |
|---|---|---|
| IO43 → BC337 → D0 | `Serial`, lógica normal | `true` |
| IO43 → D0 sem inversor | `Serial`, lógica normal | `false` |
| IO43 → BC337 → D2 | `SoftwareSerial(..., true)` | `false` |

A tabela descreve compatibilidade lógica. Não valida níveis elétricos,
montagem ou ausência de disputa com o CH340. O retorno D1 → IO44, quando usado,
precisa do divisor de tensão; não ligar TX de 5V diretamente ao ESP.

O caminho confirmado no histórico é **IO43 → BC337 → D0**, com UART física,
inversão no ESP e somente ida. Esquemas antigos da perfurada ainda indicam D2;
não devem ser usados como confirmação da posição atual do fio soldado.

## Inconsistências encontradas na codebase

1. **POC 1:** comentários e página do ESP indicam D2, mas o TX é invertido para
   BC337 → D0. O Nano também escuta D2 com SoftwareSerial invertida. Esse caminho
   D2 não combina com a dupla inversão usada no ESP. O Nano POC 1 interpreta
   caracteres `0`, `1`, `2`, sem validar o quadro completo: serve como teste
   mínimo de LED, não como validação integral do protocolo compartilhado.
2. **POCs genéricos:** `EnlaceNano` inicia `txInvertido = true`, enquanto o Nano
   padrão usa D2 com SoftwareSerial invertida e as variantes `LINK_HW` são
   descritas como fio direto no D0. Essas montagens exigem TX normal; o padrão
   combina com o BC337 → D0 adotado depois. Selecionar o ambiente, sozinho, não
   resolve essa diferença física.
3. **Inversão também afeta o retorno:** no core Arduino-ESP32 instalado,
   `Serial2.begin(..., true)` inverte **RX e TX**, não apenas TX. O retorno normal
   do Nano através de divisor será interpretado com polaridade errada no modo
   bidirecional se a inversão do RX não for configurada separadamente. Isso não
   explica falha de retorno no `rover_d0`: esse perfil deliberadamente não o usa.
   Ver [esp_enlace.h](../../src/firmware/comum/esp_enlace.h) e
   [documentação oficial da Espressif](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/serial.html#begin).
4. **Diagnóstico RX/TX:** os LEDs do conversor USB não comprovam recepção de
   comandos externos pelo ATmega. O teste de inversão ainda imprime previsões
   sobre esses LEDs e tensões sem medi-las. O D13 é a indicação visual do
   comando; bytes aceitos pela porta do PC não comprovam essa execução.
5. **App e legado:** `gateway_app` usa JSON no WebSocket e quadros antigos de
   servo `<pan,tilt>`; `rover_d0` usa `<S,pan10,tilt10,vel10>` e `<M,esq,dir>`.
   O serviço mobile oferece seleção de protocolo. Para o integrado D0, usar
   `poc_ascii`; o teste de inversão atualmente no ESP não oferece WebSocket.
   O ping JSON do app não recebe pong no servidor ASCII comum; o valor aleatório
   retornado por `sendPingFrame()` também não comprova RTT físico.
6. **Documentação e evolução:** o histórico mais recente tem projeto KiCad para
   chassi com segundo ESP32, mas o firmware identificado no Nano continua sendo
   o par D0. Projeto de PCB e firmware carregado precisam ser distinguidos.

## Verificações executadas

- Inventário USB e abertura das duas portas; leitura passiva de quatro segundos.
- Leitura da flash do Nano com `avrdude -n -D`, sem apagar ou gravar; backup em
  `%TEMP%/rover_serial_diagnostico_20261110/nano_flash.bin`.
- `pio run -e rover_d0_nano`: compilação aprovada; 8818 bytes de flash e
  364 bytes de RAM. Comparação de todos os bytes do HEX com a flash: zero diferenças.
- `node tools/verificar_joysticks_rover.cjs`: verificações existentes do painel
  aprovadas. Isso não testa o fio UART físico.
- Enviados três quadros `<L,2>` pela COM26 a 9600 baud, aguardando o boot e
  espaçando os envios. O usuário não conseguiu observar o D13; **recepção em
  execução e piscadas permanecem sem confirmação visual**. Nenhum retorno era
  esperado pelo firmware identificado.
- Nenhum firmware regravado; nenhum comando de motor ou servo enviado; nenhuma
  operação Git executada. Leitura pelo bootloader reinicializa o Nano; ele estava
  isolado dos periféricos, conforme a montagem informada.

## Próxima microetapa

Confirmar visualmente o D13 recebendo `<L,2>` pela USB do Nano isolado. Depois,
revalidar somente IO43 → BC337 → D0, GND comum e TX invertido, com USB do Nano
fora do teste. Só então retomar painel, servos e motores. Não há evidência nesta
sessão para concluir defeito do transistor, do UART ou da alimentação da montagem.
