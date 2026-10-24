# Compras para conexão e refrigeração — 2026-10-13

Atualização de prioridade: o usuário quer a máxima qualidade de imagem possível com performance estável. O ESP32-C3 dos carrinhos é apenas uma placa auxiliar econômica para testes de comunicação/ESP-NOW; não melhora o vídeo da S3-CAM e não é necessário para testar UDP no Wi-Fi atual. Para a prioridade de vídeo e refrigeração, considerá-lo opcional, sem alteração automática dos carrinhos já montados. Não foi encontrado thermal pad avulso nas três lojas consultadas; isso não comprova inexistência em lojas físicas ou exclusividade do Mercado Livre.

O usuário forneceu dois relatos de aquecimento: [ESP32S3 CAM using OV5640](https://www.reddit.com/r/esp32/comments/1pg818g/esp32s3_cam_using_ov5640/) e [Camera gets toasty](https://www.reddit.com/r/esp32/comments/1lqj78b/esp32s3_camera_gets_toasty_with_the/). São experiências individuais: incluem aquecimento, comparação com OV2640, uso de dissipadores e hipóteses de alimentação; não estabelecem a causa na placa do usuário. Confirmar tensões de alimentação do módulo e configuração antes de atribuir tudo à falta de dissipador. O objetivo de ensaio é escolher a maior resolução/qualidade JPEG que mantenha FPS, atraso e temperatura estáveis ao longo do tempo, sem prometer 1080p/30FPS com base no limite nominal do sensor.

Pesquisa no navegador em 13/10/2026. Três carrinhos foram montados na sessão do navegador: UsinaInfo, Eletrogate e RoboCore. Nenhum pedido foi finalizado. Os carrinhos dependem dos cookies dessa sessão; links abertos em outro navegador podem mostrar um carrinho vazio. Preços e estoque são os observados, sem frete; não foi informado CEP de entrega para cotação. As alternativas não contêm exatamente os mesmos itens.

## Opção recomendada: UsinaInfo

[Abrir carrinho](https://www.usinainfo.com.br/carrinho). [Política de nota fiscal: todas as vendas com NF-e](https://www.usinainfo.com.br/perguntas-frequentes).

| Produto | Quantidade | Preço unitário no cartão | Total da linha |
|---|---:|---:|---:|
| [W5500 SPI com RJ45](https://www.usinainfo.com.br/ethernet-e-wifi-arduino/modulo-ethernet-w5500-5469.html) | 1 | R$ 44,60 | R$ 44,60 |
| [ESP32-C3 Super Mini USB-C](https://www.usinainfo.com.br/esp32/esp32-c3-super-mini-com-wifi-e-bluetooth-com-usb-c-8967.html) | 1 | R$ 28,60 | R$ 28,60 |
| [DS18B20 em encapsulamento pequeno](https://www.usinainfo.com.br/sensor-de-temperatura/ds18b20-sensor-de-temperatura-digital-2806.html) | 2 | R$ 15,34 | R$ 30,68 |
| [Ventoinha 5V 25×25×10 mm](https://www.usinainfo.com.br/coolers-para-pc/mini-cooler-5v-25x25mm-para-esc-e-projetos-4408.html) | 1 | R$ 16,97 | R$ 16,97 |
| [Kit de três mini dissipadores](https://www.usinainfo.com.br/acessorios-raspberry-pi/kit-dissipador-de-calor-autoadesivo-raspberry-pi-3-pi-2-b-e-b-em-aluminio-3-unidades-4428.html) | 1 | R$ 3,60 | R$ 3,60 |

**Total verificado: R$ 124,45; boleto/depósito: R$ 118,23.** A loja anuncia desconto também no Pix nas páginas de produto, mas o resumo do carrinho identifica o total descontado como boleto/depósito.

O W5500 permite comparar TCP/UDP por Ethernet; não é necessário para UDP via Wi-Fi. É um módulo SPI, alimentado em 3,3V, com dimensões anunciadas de 59×28×16 mm. Verificar GPIOs e alimentação antes de integrá-lo à S3-CAM; pode ficar como instrumento de bancada.

O segundo ESP permite testes entre placas, controle dedicado e ESP-NOW. O C3 complementa a S3-CAM; não substitui a placa de câmera.

A ventoinha é anunciada com 7g e corrente de 30–60mA. O kit tem um dissipador de 14×14×5,5 mm e dois de 9×9×5 mm. São candidatos para ensaio, sem encaixe ou desempenho térmico validado no módulo da câmera. Alternativa encontrada: [ventoinha 5V 30×30 mm](https://www.usinainfo.com.br/coolers-para-pc/cooler-5v-30x30mm-para-raspberry-pi-4938.html), R$ 13,93 no Pix/boleto, não adicionada.

![Carrinho UsinaInfo](./compras_2026-10-13/usinainfo.jpg)

## Alternativa econômica parcial: Eletrogate

[Abrir carrinho](https://www.eletrogate.com/carrinho/index). A [página inicial](https://www.eletrogate.com/) anuncia Nota Fiscal Eletrônica.

| Produto | Quantidade | Preço unitário | Total da linha |
|---|---:|---:|---:|
| [ESP32-C3 Mini USB-C](https://www.eletrogate.com/esp32-c3-mini-tipo-c) | 1 | R$ 42,90 | R$ 42,90 |
| [Sensor anunciado como DS18B20, CI MY18E20 compatível](https://www.eletrogate.com/sensor-de-temperatura-digital-ds18b20) | 2 | R$ 4,90 | R$ 9,80 |
| [Kit de três mini dissipadores](https://www.eletrogate.com/dissipador-de-calor-autoadesivo-raspberry-pi-x3-unidades) | 1 | R$ 3,90 | R$ 3,90 |

**Total verificado: R$ 56,60; Pix: R$ 53,77.** Sensor anunciado explicitamente como compatível, não registrar como CI original Dallas/Analog Devices. Comparar leituras com uma referência antes de usar limites térmicos.

W5500 e ventoinhas pequenas 5V consultados estavam indisponíveis. Este carrinho não cobre Ethernet nem refrigeração ativa.

![Carrinho Eletrogate](./compras_2026-10-13/eletrogate.jpg)

## Alternativa parcial: RoboCore

[Abrir carrinho](https://www.robocore.net/carrinho). A [página inicial](https://www.robocore.net/) declara NF-e para todos os pedidos.

| Produto | Quantidade | Preço unitário | Total da linha |
|---|---:|---:|---:|
| [ESP32 Wi-Fi + Bluetooth](https://www.robocore.net/wifi/esp32-wifi-bluetooth) | 1 | R$ 42,90 | R$ 42,90 |
| [DS18B20 à prova d'água](https://www.robocore.net/sensor-ambiente/sensor-de-temperatura-ds18b20-a-prova-de-agua) | 2 | R$ 9,81 | R$ 19,62 |

**Total verificado: R$ 62,52; Pix: R$ 59,39.** As sondas têm ponta de 6×50 mm e cabo de cerca de 95 cm: úteis em testes de bancada, menos adequadas ao espaço e peso da cabeça do rover. Não cobre Ethernet nem refrigeração.

O W5500 encontrado é um [shield para Arduino](https://www.robocore.net/shields-arduino/arduino-shield-ethernet-w5500), R$ 149,00, em formato menos conveniente que o módulo SPI da UsinaInfo; não adicionado. Também existe [cooler oficial para Raspberry Pi 4 com dissipador](https://www.robocore.net/acessorios-raspberry-pi/cooler-para-case-oficial-raspberry-pi-4), R$ 41,90, com dissipador 18×18×10 mm e suporte específico de Raspberry; não adicionado por não haver encaixe validado na câmera.

![Carrinho RoboCore](./compras_2026-10-13/robocore.jpg)

## Thermal pad: referência adicional, sem quarto carrinho

[Thermal pad Infni 100×100×0,5 mm, anúncio MLB5677032060](https://www.mercadolivre.com.br/thermal-pad-infni-10x10cm-05mm-silicone-cinza-6wmk-para-dissipador-de-calor/p/MLB54977704?pdp_filters=item_id%3AMLB5677032060): R$ 37,90. A página exibiu estoque disponível, loja oficial Infni Tecnologia e **armazenado e enviado pelo Full**. Não foi adicionado ao carrinho, mantendo apenas três carrinhos preparados.

O material é anunciado como silicone, 6 W/m·K e **não adesivo**. Precisa de suporte que mantenha contato, sem transferir esforços ao cabo flat/lente. O [fluxo fiscal oficial do Mercado Livre](https://developers.mercadolivre.com.br/devcenter/api-fiscal-faturamento-de-venda) descreve emissão automática de NF-e no Full. Conferir se o vendedor e a modalidade Full continuam selecionados ao comprar.

0,5 mm é uma opção para experimentar, não espessura definida para montagem: a escolha depende da distância real entre superfície quente e dissipador. O pad sozinho não constitui refrigeração. Não empilhar a fita adesiva do kit e outro pad sem necessidade. A [Implastec](https://www.implastec.com.br/product/almofada-termica-ts-pad) oferece TS-PAD de 0,5 a 3 mm; um anúncio com NF consultado estava indisponível.

## Câmeras no mercado nacional

Não foram adicionadas câmeras aos carrinhos, pois o modelo exato da placa/conector atual e sua pinagem precisam ser conferidos. Ter o mesmo número de contatos no flat não comprova compatibilidade.

| Candidato encontrado | Preço Pix/boleto | Avaliação |
|---|---:|---|
| [OV2640-V3 avulsa](https://www.usinainfo.com.br/esp32/camera-ov2640-v3-2mp-para-esp32-cam-com-lente-14-interface-sccb-9108.html) | R$ 55,39 | Alternativa para comparação, 2MP; não é melhoria garantida sobre OV5640 nem garantia de menor temperatura. |
| [OV5640 avulsa, lente 66°, flat 24 pinos](https://www.usinainfo.com.br/outros-modulos-arduino/camera-ov5640-5mp-com-lente-66-e-interface-sccb-24-pinos-9281.html) | R$ 54,10 | Mesmo sensor, útil como reposição se compatível; não resolve o aquecimento por si só. |
| [ESP32-CAM completo com OV3660 e USB-C](https://www.usinainfo.com.br/esp32/esp32-cam-com-camera-ov3660-3mp-ch340-e-programador-usb-c-integrado-9101.html) | R$ 139,94 | Outra placa inteira com sensor 3MP; não é câmera avulsa para encaixar automaticamente na S3 atual. |

O [driver oficial esp32-camera](https://github.com/espressif/esp32-camera) suporta OV2640, OV3660 e OV5640, mas suporte de software não garante compatibilidade elétrica de um módulo avulso. O anúncio OV2640 tem inconsistências em resolução/FOV; conferir ficha do módulo, sem assumir todas as especificações do texto comercial. Não foi identificado um upgrade direto comprovado para a placa atual nesta pesquisa. Módulos CSI de Raspberry Pi não devem ser tratados como substitutos diretos de uma câmera DVP da S3.

## Temperatura relatada e ensaio sugerido

O usuário relata que a câmera atual, provavelmente OV5640, chega a aproximadamente 70°C em operação. Ainda não foram informados o instrumento, o ponto medido e as condições de operação. Não houve medição feita pelo agente.

A [ficha da OV5640 distribuída pela Waveshare](https://files.waveshare.com/upload/d/da/OV5640_DataSheet.pdf), seção 8.2, indica limite de operação de 70°C na junção e faixa de imagem estável de 0–50°C na junção. Temperatura externa e temperatura da junção não são equivalentes; 70°C externos não devem ser registrados como operação comprovadamente segura.

Ensaio proposto: medir temperatura ambiente e do conjunto com mesma resolução/FPS, comparar sem refrigeração, com dissipador e com dissipador + ventoinha. Registrar também estabilidade da imagem, consumo e tempo até estabilização. O DS18B20 instalado no conjunto mede temperatura local, não a junção do sensor de imagem. Identificar o ponto que realmente aquece antes de definir contato térmico atrás da câmera; não comprimir o flat ou apoiar metal sobre contatos expostos. Prever entrada e saída de ar na caixa, peso móvel e afastamento da antena.

Para LTE, não foi selecionada nesta pesquisa uma opção nacional de modem que reúna estoque, compatibilidade e preço suficientes para inclusão nos carrinhos. Não comprar SIM800L como substituto de modem 4G.

## Ampliação da seleção UsinaInfo (13/10/2026)

A planilha `outputs/01a136bb-0898-72e1-a621-24d29689bee0/compra_usinainfo_rover.xlsx` agora inclui prioridade, situação e finalidade. Total **parcial** cotado: R$234,50 cartão / R$222,79 Pix-boleto, sem frete. Nenhum carrinho foi modificado nesta atualização.

- Sensor de tensão [DC 0–25V](https://www.usinainfo.com.br/sensor-de-tensao/sensor-de-tensao-dc-0-25v-3425.html), código06731: R$4,95 cartão. É divisor resistivo 5:1; calibrar no Nano. A tensão não fornece percentual exato de carga sob movimento.
- [OLED I2C 0,96](https://www.usinainfo.com.br/display-arduino/display-oled-096-i2c-128x64-branco-5366.html), código08483: R$24,30 cartão, prioridade média. Verificar A4/A5 e RAM no firmware Nano.
- Controle futuro de prioridade baixa: [ESP32-S3 N8R2](https://www.usinainfo.com.br/esp32/esp32-s3-devkitc-1-n8r2-8mb-flash-com-wifi-e-bluetooth-com-usb-c-8679.html) R$62,80, [TFT ST7789 1,3](https://www.usinainfo.com.br/display-arduino/display-tft-lcd-13-spi-rgb-240x240-st7789-5607.html) R$34,70 e [dois joysticks](https://www.usinainfo.com.br/joystick-e-controles-ir/joystick-ky023-3-eixos-2305.html) R$5,95 cada. OLED de bateria é separado da tela colorida do controle. Vídeo requer firmware e validação de desempenho. O anúncio S3 contém especificações incorretas sobre Wi-Fi6/Zigbee; S3 é Wi-Fi b/g/n, conforme [Espressif](https://www.espressif.com/en/products/socs/esp32-s3/).
- Farol previsto: LED3W + driver de corrente constante DIM/PWM + dissipação própria. [LED3W](https://www.usinainfo.com.br/led-alto-brilho/led-smd-branco-frio-de-alto-brilho-3w-epistar-2788.html) está indisponível. Driver ainda a definir; [XL4015 CC/CV](https://www.usinainfo.com.br/regulador-de-tensao/regulador-de-tensao-e-corrente-ajustavel-xl4015-dc-step-down-saida-125-a-32vdc-02-a-3a-5880.html) pede ≥8V e não atende a bateria2S durante descarga. Conjunto não cotado completamente.
- Cartão microSD32GB Classe10/U1 previsto, alta prioridade, preço pendente; busca da Usina retornou leitores e acessórios. Confirmar slot da placa antes de adicionar leitor.
- Usuário já possui FlySky. Receptor específico ainda pendente do modelo; manter Nano/TB6612. [FlySky](https://shop.flysky-cn.com/pages/support) exige protocolo compatível entre transmissor e receptor. Implementar failsafe antes de pilotagem; nada testado nesta etapa.
- [W5500 ML Full](https://www.mercadolivre.com.br/modulo-ethernet-w5500/p/MLB42965922?pdp_filters=shipping%3Afulfillment), oferta MLB5834894252: R$57,00, Full verificado no produto. Fora dos totais UsinaInfo; nenhum quarto carrinho. Ethernet oferece ligação cabeada por SPI/RJ45 e [TCP/UDP](https://docs.wiznet.io/Product/Chip/Ethernet/W5500/Application); Wi-Fi da placa já permite UDP.

### Pesquisa 4G para compra antecipada — 13/10/2026

Orçamento do laboratório vai até dezembro; usuário deseja adquirir agora componentes de iterações futuras. Prioridade de compra não é a etapa de implementação. Pesquisa no Mercado Livre com filtro Full não confirmou SIM7600 adequado (resultados exibiam módulos não celulares). Não afirmar inexistência global de ofertas.

Melhor candidato nacional encontrado: Curto Circuito A7608SA-H Cat4 em placa, antena LTE inclusa, SKU18609, em estoque verificado no navegador, R$448 cartão / R$403,20 Pix-boleto, sem frete: https://curtocircuito.com.br/modulo-a7608sa-h-4g-lte-antena-fcp.html . Loja informa nota fiscal na página inicial e termos. Placa anunciada 5–16V e UART TTL3,3V; núcleo SIMCom isolado é 3,4–4,2V, não confundir alimentações. Fabricante suporta PPP/USB, B3/B7/B28 entre outras; compatibilidade USB/firmware e GPIO19/20 na S3-CAM não confirmada localmente. Candidato, não plug-and-play validado. Loja inverte uplink/downlink em uma lista; valores corretos SIMCom: até150Mbps down /50Mbps up celulares nominais, não taxa real do ESP. https://www.simcom.com/product/A7608SA-H.html .

Magalu/nocnocestadosunidos Waveshare SIM7600G-H HAT(B): R$838,19 Pix/R$882,30 cartão, importado, página informa NF, antenas LTE/GPS e cabo. https://www.magazineluiza.com.br/modulo-4g-hat-waveshare-sim7600g-h-lte-gnss-para-raspberry-pi/p/eaf5f2ka89/in/ardn/ . Modelo(B) possui hubUSB; não considerar compatível automaticamente com stack USB do S3. Não escolhido.

Albacore SIM7600G-H MiniPCIe R$537,92/3estoque segundo página indexada; é módulo de integração, exige carrier/adaptador/SIM/antenas e NF não verificada; excluído da recomendação fechada. Curto SIM7600SA Cat1 R$660 esgotado; não escolhido.

W5500 da seleção UsinaInfo é Ethernet SPI/RJ45, sem SIM nem rádio4G. Pode receber internet de roteador4G com portaLAN, mas não converte modemUSB/serial em Ethernet e não é necessário para modem direto. Permanece baixa prioridade experimental. Não alterada planilha nem carrinhos, nenhum pedido finalizado.

### 4G incluído na planilha — 13/10/2026

Usuário autorizou adicionar A7608SA-H na planilha. Adicionado bloco separado Curto Circuito, prioridade de compra alta / uso futuro, 1unidade R$448 cartão ou R$403,20 Pix-boleto, sem aplicar desconto UsinaInfo à outra loja. Totais UsinaInfo preservados. Total geral parcial cotado R$682,50 cartão /R$625,99 à vista, sem frete/plano e sem cinco itens ainda sem cotação. Arquivo existente atualizado, não houve pedido nem novo carrinho.

Oferta Mercado Livre encontrada por busca do modelo exato: https://www.mercadolivre.com.br/modulo-gsm-a7608sah-4g-lte-com-antena-fcp/up/MLBU2311204429 , itemMLB3669224895, loja oficial Curto Circuito, 4disponíveis e R$427,51 na consulta. Descrição informa NF. Seção de entrega não confirma Full; badgesFull observados pertencem a recomendações de outros produtos, não ao modem. Link registrado como alternativa na planilha, fora dos totais, não elegível sob critério Full atual. Não afirmar que não existe no ML. Compatibilidade USB/PPP com a S3-CAM ainda não validada.
