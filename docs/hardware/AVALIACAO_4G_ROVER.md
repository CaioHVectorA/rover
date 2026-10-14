# Avaliação de conexão 4G para o rover

Consulta: 13/10/2026. Nenhum teste físico ou compra finalizada. Esta avaliação distingue anúncio, documentação de fabricante, relatos de compradores e inferências de integração.

## Conclusão de compra

O hotspot Athenix Full de R$144,95 tem arquitetura de conexão plausível para o ESP32-S3 via Wi-Fi, mas documentação insuficiente para recomendá-lo como conexão principal de vídeo remoto contínuo. Full confirma logística, não estabilidade elétrica, radiofrequência ou térmica. O usuário esperava módulo integrado; hotspot USB é outra forma de montagem e não deve ser substituído silenciosamente na compra.

O A7608SA-H continua candidato de módulo mais coerente com expansão de vídeo, por documentação e interfaces, mas não está validado com a S3-CAM. Modelo/firmware USB, alimentação e GPIO da placa precisam de confirmação antes da seleção definitiva. A oferta na Curto Circuito é loja direta com NF; anúncio ML do mesmo produto não confirmou Full. Não foi encontrado nesta pesquisa módulo Cat-1/Cat-4 de desenvolvimento com Full confirmado e todos os requisitos técnicos verificados.

## Produtos investigados

| Produto | Oferta consultada | Evidência | Resultado |
|---|---|---|---|
| Athenix hotspot USB | R$144,95, RAXON, Full confirmado | Wi-Fi b/g/n, microSIM, comprimento93,7mm e massa30g declarados. Bandas LTE, largura/altura, corrente máxima, temperatura e modelo eletrônico ausentes | Candidato de experimento econômico, sem confirmação para vídeo contínuo |
| A7608SA-H + antena LTE | Curto R$403,20 Pix/R$448 cartão, em estoque | Placa anunciada5–16V/UART3,3V. SIMCom confirma Cat4, PPP e USB. Dimensões da placa montada ausentes | Candidato de expansão integrada, exige validação local |
| A7670SA + antena | Curto R$337,50 Pix/R$375 cartão, esgotado | Cat1; descrição resumida da loja confunde NB-IoT/Cat-M, mas descrição detalhada e documentação da família confirmam Cat1 | Sem estoque; economia deR$65,70 frente ao Cat4, menos margem de rede |
| SIM7000G T-PCIE | ML R$332,50, HITEMPSOLUCOES, Full confirmado | Fabricante informa Cat-M300kbps down/375kbps up. Módulo MiniPCIe exige infraestrutura de integração | Descartado para câmera contínua; possível telemetria separada |
| LilyGO T-A7670X | Documentação oficial, Full de variante útil não confirmado | Placa inteira111×34×19mm, inclui outro ESP32 e modem. VarianteSA/G incluiB7/B28, E tem bandas diferentes | Não confundir medida do chip com placa inteira; não fechado para compra |
| TP-Link M7000 EUv1 | Documentação oficial, oferta Full não fechada | 94×56,7×19,8mm,5V/1A, Wi-Fi2,4GHz; temperatura ambiente0–35°C e bandasEUv1 semB28 | Mais documentado, mas volumoso, restrição térmica e variante regional precisam avaliação |

Fontes de oferta:
- [Athenix Full](https://www.mercadolivre.com.br/modem-4g-usb-lte-notebook-wifi-compartilhamento-cor-branco-athenix/p/MLB45000536?pdp_filters=item_id%3AMLB4208432419%7Cshipping%3Afulfillment)
- [A7608SA-H Curto](https://curtocircuito.com.br/modulo-a7608sa-h-4g-lte-antena-fcp.html)
- [A7670SA Curto](https://curtocircuito.com.br/modulo-a7670sa-4g-lte-antena-fcp.html)
- [SIM7000G Full](https://www.mercadolivre.com.br/modulo-lte-4g-modem-simcom-sim7000g-t-pcie/p/MLB2088472124?pdp_filters=item_id%3AMLB6844845926%7Cshipping%3Afulfillment)

## Avaliações do Athenix

No próprio catálogoMLB45000536 foram lidas 56avaliações agregadas, média4,6/5, e comentários de compradores. Há relatos de uso com notebook e máquina de pagamento, mas sem duração de ensaio, taxa de upload, temperatura, vídeo contínuo ou RTT remoto. Um comprador relatou chipClaro não funcionando mesmo atribuindo5estrelas; não há evidência que identifique se a causa foi APN, plano, bandas ou defeito. A avaliação1estrela contém somente “Não presta”, sem diagnóstico. O resumo gerado por IA do site não foi usado como evidência técnica. A mistura de opiniões de outros países e eventual agregação de variantes limita transferência ao lote vendido.

Não foi localizado datasheet identificável do hardware exato Athenix que forneça bandasLTE, corrente de pico, faixa de temperatura ou firmware. Anúncios com mesma marca não provam que a placa interna seja idêntica. Não assumir B28 ou funcionamento em qualquer operadora a partir de “desbloqueado”.

## Compatibilidade com o rover

### Forma de ligação

Hotspot pronto: SIM→LTE→Wi-Fi local→S3. USB é alimentação; não pressupor ligaçãoUSB aoESP. O modem pode ficar no chassi fixo, enquanto a cabeçaS3-CAM continua móvel, sem fios extras de dados pelo pan/tilt. O protocolo remoto ainda precisa implementação.

Módulo direto: SIM→LTE→USB/PPP ou UART/PPP→S3. O Nano continua comandando TB6612/servos. A integração pode ampliar o chicote móvel; não decidir montagem de alta velocidade, flexão e roteamento sem layout. Alternativamente, um gateway fixo dedicado pode fornecer Wi-Fi ao S3, mas isso é outra arquitetura, não validada nem adicionada às compras.

A [Espressif USBPPP](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_host/usb_ppp.html) documenta módulos testados e necessidade de verificar firmware/descritoresPPP. A7608 não aparece explicitamente na tabela consultada; a existência deUSB no chip não garante compatibilidade direta. O [S3 USBHost](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/usb_host.html) é FullSpeed12Mbit/s, não uma ligação de150Mbit/s. A câmera e USB nativoGPIO19/20 precisam de conferência na placa real. O projeto não contém configuração de câmera completa que permita provar GPIO livres nesta leitura.

UART115200, 8N1, transporta no máximo11520bytes/s antes do overheadPPP/IP, cerca92kbps úteis brutos. Não escolher placa por “50Mbps LTE” mantendo essa serial para vídeo. É possível aumentarbaudrate, mas vazão sustentada, buffers, RTS/CTS e carga doESP precisam de medição. [esp_modem](https://docs.espressif.com/projects/esp-protocols/esp_modem/docs/latest/README.html) registra limitações deUART/buffers eCMUX. Cat4 fornece margem celular maior; não elimina gargalo de interface.

### Vídeo e dados

Exemplos calculados, não medições daOV5640:
- JPEG20kB ×10FPS ≈1,6Mbit/s depayload.
- JPEG50kB ×15FPS ≈6Mbit/s depayload.

Somar overhead e variação de cena. A resolução não determina sozinha tamanhoJPEG ou vazão. Um enlaceCat1 com teto nominal5Mbps deupload pode servir ao primeiro exemplo em condições favoráveis, mas não ao segundo mesmo antes dosoverheads. Não inferir FPS real de anúncio150Mbps.

Cada1Mbit/s sustentado consome aproximadamente0,45GB/h, antes deoverhead. Plano e eventualrelay de vídeo entram no custo operacional. RTT/jitter e cobertura na rota importam tanto quantoMbps; modem não promete pilotagem responsiva.

### Alimentação e calor

Nunca alimentar modem peloGPIO ou saída3V3 doESP/Nano. Para placas5V usar ramal de potência com retorno bem roteado e desacoplamento conforme documentação. Mini560 anunciado5A precisa suportar carga simultânea de câmera, modem, servos e acessórios sem queda; a capacidade real no case não foi medida. Núcleo A7608 avulso tem alimentação3,4–4,2V; placa reguladaCurto anuncia5–16V. Não intercambiar essas especificações.

Modem deve ser previsto no chassi fixo, com caminho de ventilação, sem compartilhar o volume quente atrás da câmera. A antena precisa de posição afastada de motores/driver, grandes massas metálicas e dissipadores; distância precisa depende da antena e layout. PlásticoABS comum permite projetar passagem deRF, mas isso não valida cobertura nem imunidade ao ruído na montagem.

As docs trazem bateria69×37×19mm, motoresJGA e mecanismosSG90, mas não dimensões finais internas dochassi. Não localizado CADSTEP/STL/FCStd/F3D no repositório. Não é possível declarar encaixe do modem aprovado. Medidas do núcleo30×30×2,5mmA7608 não são medidas da placa comprada, que incluiSIM, regulador e conectores.

## Validação necessária para fechar a solução

1. Obter da ofertaexata modelo/firmware, bandasLTE, medidas da placa completa e requisitos elétricos. Confirmar interfaceUSBFullSpeed+PPP se for ligada diretamente aoS3.
2. Medir vídeo atual viahotspot do celular: JPEGbytes/frame, FPS, bitrate, atraso e comandos. Isso define a demanda antes de escolherCat1/Cat4.
3. Na bancada, comparar candidato com celular usando mesmoSIM/local. Rodar câmera e movimentos de servo por pelo menos1–2h; registrar resets, queda5V, temperatura e reconexões. A duração é proposta de teste, não garantia de vida útil.
4. Repetir com sinalfraco e perda de conexão. Implementar parada automática dos motores por expiração de comandos e reconexão sem retomar movimento antigo.
5. Testar novamente na carcaça com antena definitiva. Só então classificar como adequado ao case e pilotagem remota.

Fontes técnicas:
- [SIMCom A7608SA-H](https://www.simcom.com/product/A7608SA-H.html)
- [SIMCom SIM7000G](https://www.simcom.com/product/SIM7000G.html)
- [LilyGO variantesT-A7670X](https://wiki.lilygo.cc/products/t-sim-series/t-a7670/)
- [TP-Link M7000EUv1 datasheet](https://static.tp-link.com/2019/201909/20190916/M7000%28EU%29%201.0_Datasheet.pdf)
