# 🛒 Lista de Compras - Robô Móvel ESP32-S3 CAM

Lista consolidada de componentes para o robô com tração 4WD, visão em tempo real Pan/Tilt, iluminação e saída sonora.

> 📚 **Documentos Relacionados:**
> * 🗺️ [**`ROADMAP.md`**](file:///home/usuario/Documentos/rover/ROADMAP.md): Canvas do MVP e cronograma de fases de montagem e software.
> * 🧠 [**`MEMORIA_DO_PROJETO.md`**](file:///home/usuario/Documentos/rover/MEMORIA_DO_PROJETO.md): Diário de decisões e histórico das conversas.
> * 🏠 [**`README.md`**](file:///home/usuario/Documentos/rover/README.md): Visão geral do projeto.

---

## 1. Mercado Livre (Cérebro & Visão)

Placa principal adquirida individualmente no Mercado Livre:

| Componente | Produto | Qtd | Link |
|---|---|:---:|---|
| **Cérebro + Câmera 5MP** | Placa ESP32-S3 CAM (N16R8 - 16MB Flash / 8MB PSRAM) + Câmera OV5640 5MP com USB-C | 1 | [Abrir no Mercado Livre](https://www.mercadolivre.com.br/p/MLB2061307865?matt_tool=38524122&pdp_filters=item_id:MLB5139266661) |

---

## 2. Pedido Principal: RoboCore (`robocore.net`)

Todos os itens mecânicos, motores, servos, alimentação e periféricos reunidos em um único pedido na **RoboCore**:

| Subsistema | Componente Sugerido na Loja | Qtd | Fase no Roadmap | Finalidade no Robô |
|---|---|:---:|:---:|---|
| **Mecânica Pan/Tilt** | Micro Servo 9g SG90 (com cruzetas e parafusos) | 2 | **Fases 1, 2 e 3 (MVP)** | Movimento horizontal (Pan) e vertical (Tilt) |
| **Mecânica Pan/Tilt** | Suporte Pan-Tilt 2 Eixos para Micro Servo 9g | 1 | **Fase 2 (MVP)** | Estrutura articulada onde a placa/câmera é fixada |
| **Tração** | Micromotor DC com Caixa de Redução metálica (~100 a 200 RPM, eixo D de 3mm) | 4 | **Fases 1, 2 e 3 (MVP)** | Tração independente nas 4 rodas (Skid-steer) |
| **Tração** | Rodas de Borracha de Alta Aderência (ex: linha StickyMAX para eixo 3mm) | 4 | **Fase 2 (MVP)** | Rodas emborrachadas de silicone/borracha de alto atrito |
| **Tração** | Suportes em "L" para fixação de Micromotores | 4 | **Fase 2 (MVP)** | Fixação dos micromotores ao chassi |
| **Ponte H** | Módulo Driver de Motor DC / Ponte H (L9110 / MX1616 ou L298N) | 1 | **Fases 1, 2 e 3 (MVP)** | Controle de velocidade (PWM) e direção dos 4 motores |
| **Regulação** | Módulo Regulador Step-Down DC-DC (LM2596 ou XL4015 ajustável) | 1 | **Fases 1, 2 e 3 (MVP)** | Converte 7.4V das baterias em 5.0V estáveis para o ESP32 e Servos |
| **Alimentação** | Suporte para 2 Baterias 18650 com rabicho | 1 | **Fases 1, 2 e 3 (MVP)** | Conexão das células em série (7.4V nominal) |
| **Alimentação** | Baterias 18650 Li-Ion Recarregáveis | 2 | **Fases 1, 2 e 3 (MVP)** | Células de alimentação do sistema |
| **Som** | Buzzer Passivo ou Ativo 5V | 1 | *Fase 4 (Pós-MVP)* | Saída sonora para bips de inicialização, alarme e status |
| **Iluminação** | Módulo / Barra de LED RGB Endereçável WS2812B (Neopixel) | 1 | *Fase 4 (Pós-MVP)* | Efeitos coloridos usando apenas 1 pino GPIO do ESP32 |
| **Acessórios** | Chave Gangorra Liga/Desliga + Cartela de Fios Jumpers (M-F e F-F) | 1 | **Fases 1, 2 e 3 (MVP)** | Chave geral e cabeamento flexível |

---

## 💡 Observações Importantes de Montagem
1. **Pan & Tilt:** Como a câmera é integrada ao ESP32-S3 CAM, a placa inteira (~16g) é montada na base superior do suporte Pan/Tilt com os fios descendo em chicote flexível com alívio de tensão.
2. **Alimentação:** A alimentação de 5V dos servos **deve vir da saída do Step-Down**, nunca direto do pino 5V da placa ESP32 (para evitar *brownout* e reinicializações).
