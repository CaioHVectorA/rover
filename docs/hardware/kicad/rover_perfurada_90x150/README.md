# Montagem proposta — perfurada 90 × 150 mm

Projeto principal sem buzzer, LEDs ou barras de pinos adicionais. Nano, Mini 560, TB6612 e inversor BC337 na perfurada; ESP na cabeça móvel; motores e servos externos.

## Arquivos atuais

- `rover_conexoes.kicad_sch`, `.pdf`, `.png`: esquema elétrico com inversor.
- `rover_perfurada_90x150.kicad_pcb`: mapa físico, ilhas e fios em camadas técnicas. Fios não são trilhas de PCB; não usar para fabricação.
- `montagem_superior.png`: projeção dos fios no lado dos componentes.
- `montagem_inferior.png`: lado de solda espelhado horizontalmente. Virar a placa como uma página, mantendo o topo para cima; os números de coluna refletem a mesma posição física.
- `ligacoes_furo_a_furo.csv`: origem/destino de cada fio, coluna e linha.

## Inversor restaurado

ESP IO43 TX → R1 1k → base B do BC337. Emissor E → GND. Coletor C → D2 Nano e R2 10k → +5V. Chicote continua com três fios: +5V, GND e TX ESP. Sem retorno Nano → ESP. Os pads C/B/E estão identificados; conferir fabricante/orientação do BC337 antes de dobrar os terminais ao passo 2,54 mm.

Proposta de firmware: `SoftwareSerial entrada(2, A1, true)` a 38400 baud. A1 é TX reservado sem fio; não pode ser usado como GPIO por outro circuito. Essa reserva libera D3 para PWMA. STBY muda para D12, deixando D2 exclusivamente como RX invertido. Firmware atual não foi alterado: `SoftwareSerial(2, 3)` sem inversão NÃO corresponde a esse circuito. É uma alteração explicitamente solicitada para o esquema; difere da arquitetura antiga D0 direta.

## Como ler o mapa físico

Grade de 34 × 58 furos, passo assumido 2,54 mm; tamanho confirmado pelo usuário: 90 × 150 mm, ilhas isoladas. Coordenadas de Nano seguem formato padrão de 30 terminais, USB para cima; conferir clone real. R1: (23,35)–(26,35). R2: (21,35)–(21,38). BC337: C=(23,39), B=(24,39), E=(25,39). Solda direta, sem soquetes/barras acrescentados.

TB6612 e Mini possuem ILHAS AUXILIARES para soldar fios identificados pelo nome. Não representam a ordem dos terminais físicos dos módulos; são pontos de ligação escolhidos na perfurada. É necessário ligar o terminal nominal do módulo à ilha correspondente por fio curto. Esses fios locais dependem da placa real e não têm comprimentos ou trajetos físicos definidos. Identificação 'TB6612FNG' informa o chip, mas não identifica a versão do breakout. Mini confirmado por link RoboCore, dimensões 29 × 18 mm; o corpo no mapa usa essa medida, sem inventar distâncias entre pads.

Trajetos são fios ISOLADOS, soldados somente nas pontas identificadas. Não remover isolamento em cruzamentos ou ao passar sobre outras ilhas. Repetição de uma rede e pontos de derivação não significa ponte nua por toda a placa. Fios de potência não foram dimensionados em bitola/corrente. Fixar módulos mecanicamente sem usar somente os fios como sustentação.

## Validação e referências

Conectividade conferida na netlist do KiCad 10.0.7 e no mapa de pontas dos 36 fios. Arquivo da perfurada reaberto pelo parser local, 1972 ilhas. Sem teste elétrico, térmico ou de bancada. Correntes dos motores paralelos, desacoplamento, alimentação e serial invertida precisam de validação antes da montagem final.

[Mini 560 — RoboCore](https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v), [SoftwareSerial — Arduino](https://docs.arduino.cc/learn/built-in-libraries/software-serial), [BC337 — onsemi](https://www.onsemi.com/pdf/datasheet/bc337-fsc-d.pdf).
