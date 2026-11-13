# Montagem 3D da placa de chassi V2

Abra o projeto no KiCad 10 e use **Alt+3** no Editor de PCB. Os modelos da biblioteca padrão usam `${KICAD10_3DMODEL_DIR}` e os sólidos de referência do rover usam `${KIPRJMOD}/modelos_3d`. A placa mede 85 × 65 mm e os quatro furos M3 têm distância entre centros de 77 × 57 mm.

| Posição | O que aparece e o que conferir |
| --- | --- |
| U1 | DevKit de 30 pinos sobre duas barras fêmea. Portadora de referência com passo de 2,54 mm, 25,4 mm entre filas, rádio WROOM e Micro-USB. Conferir versão da bancada, altura do encaixe e acesso ao USB. |
| U2 | Duas barras fêmea de oito pinos e portadora simplificada com 12,7 mm entre filas. Conferir a distância e a ordem dos pinos do TB6612FNG adquirido. |
| U3 | Mini 560 no canto superior direito. O bloco de 29 × 18 × 5,4 mm aparece sobre apoio isolante previsto de 6 mm. As quatro ilhas U3 ficam sob o volume do conversor, no mesmo canto, para soldar fios curtos. A disposição na placa principal não é um gabarito de encaixe do módulo. Conferir o suporte, a saída dos fios do OLED e a folga da tampa na bancada. |
| U4 | Ilhas para solda direta dos fios que levam 5 V, GND, DIN, BCLK e WS ao MAX98357A externo. Os contatos 3 e 4 ficam livres. Ligar o alto-falante ao borne do módulo. |
| U5 | Opção de microfone interno. Barra fêmea 1×6 e portadora simplificada segundo o footprint atual. Conferir o breakout INMP441 real e alinhar sua abertura acústica com o chassi. |
| J2, J9 | Ilhas para soldar os fios da câmera e do OLED externo. Em J2 (4 vias), 1 = GND, 2 = +5V, 3 = CAM-TX (GPIO16 / RX2) e 4 = CAM-RX (GPIO23 / D23), roteados em face única com jumpers isolados `JP5` e `JP6` pelo lado superior. Em J9, 1 = GND, 2 = 3V3, 3 = SCL, 4 = SDA. |
| J1, J3–J7, SW1 | J4 e J5 têm barras macho para os servos. J1, J3, J6, J7 e SW1 têm ilhas para solda direta dos fios. Servos, motores, bateria, LEDs e chave de painel ficam nos chicotes. Confirmar o conector físico e a corrente nominal dos contatos de potência antes da fabricação. |
| U6, R3–R5 | U6 é o barramento do DS18B20 remoto: 1 GND, 2 DQ, 3 3V3. O pull-up R5 fica na placa. R3–R5 são resistores axiais de passo 7,62 mm. |
| C1–C4 | Filtragem e desacoplamento THT: `C1` eletrolítico 470 µF / 16 V (`+5V ↔ GND`) e `C2` eletrolítico 470 µF / 25 V (`VCC_BAT ↔ GND`) em passo 3,5 mm / Ø 8 mm (conferir marca `+` no pino esquerdo); `C3` cerâmico 100 nF (`VBAT-SENSE ↔ GND`) e `C4` cerâmico 100 nF (`+3V3 ↔ GND`) em passo 2,54 mm. |

As portadoras simplificadas usam substrato de 1,6 mm e assentamento nominal a 9 mm da PCB. São hipóteses de visualização para conferir com paquímetro. O modelo não determina a altura do conjunto real, o raio de dobra dos cabos ou a posição do furo acústico.

A geometria de referência do DevKit utiliza as posições relativas de EN, WROOM e USB de uma placa pública de 30 pinos. Os encapsulamentos do rádio e do Micro-USB vêm da biblioteca do KiCad. [Projeto de referência](https://github.com/BrijModi/ESP32-Dev-Kit-Clone)

O envelope dimensional do Mini 560 usa as medidas publicadas pelo fornecedor. A posição dos furos do módulo continua pendente de medição na bancada. [Mini 560 de 5 V da RoboCore](https://www.robocore.net/regulador-de-tensao/conversor-dc-dc-step-down-mini-560-5v)


