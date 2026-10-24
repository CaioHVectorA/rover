# 🚀 Guia de Execução dos POCs Passo a Passo

Este guia detalha os procedimentos práticos de bancada para cada um dos 6 POCs do Rover, com conexões elétricas, operação das páginas web e comandos seriais de diagnóstico.

---

## 🛠️ Arquitetura Compartilhada de Software

Todos os POCs utilizam os módulos unificados localizados em [`src/firmware/comum/`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/):

* [`rover_protocolo.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/rover_protocolo.h): Parser ASCII determinístico de quadros curtos delimitados por `<` e `>` (`<S,pan,tilt>`, `<M,esq,dir>`, `<P,seq>`, `<X>`, etc.).
* [`esp_camera_frio.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/esp_camera_frio.h): Gerenciador térmico ativo do sensor OV5640 com registrador `0x3008`, clock adaptativo e servidor MJPEG isolado no Core 0.
* [`esp_painel.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/esp_painel.h): Interface Web única servida na porta 80 com Design System de Engenharia (Cockpit), WebSocket na porta 81 e vídeo na porta 82.
* [`nano_servos.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/nano_servos.h): Módulo de controle suave de servos SG90 em microssegundos (544–2400 µs) a 50 Hz com perfil trapezoidal e compensação de folga.
* [`nano_motores.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/nano_motores.h): Controle da ponte H TB6612FNG com rampa não-bloqueante em ponto fixo, tempo morto na reversão e watchdog.
* [`nano_diag.h`](file:///c:/Users/caihe/Documents/develop/rover/src/firmware/comum/nano_diag.h): Captura do registrador `MCUSR` no boot (identifica desligamento por Brown-Out) e leitura de bateria 2S em A0.

---

## 📡 POC 1: Teste de Enlace Serial RX/TX com Servidor Web

### Objetivo
Validar a integridade bidirecional do chicote serial entre o ESP32-S3 e o Arduino Nano antes de conectar atuadores de alta potência.

### Hardware Necessário
* ESP32-S3-CAM + Arduino Nano V3.
* Chicote: `5V` comum, `GND` comum, `ESP IO43 TX -> Nano D2 RX (via transistor BC337)` e `Nano D1 TX -> ESP IO44 RX (via divisor 1k/2k)`.

### Gravação
```powershell
pio run -e poc1_esp32 -t upload --upload-port COM24
pio run -e poc1_nano  -t upload --upload-port COM18
```

### Como Testar
1. Conecte o computador/celular ao Wi-Fi `Rover-POC1` (senha: `12345678`) ou acesse o IP da rede local informado na porta serial (ex: `http://192.168.7.25/` ou `http://rover.local/`).
2. A tela exibe métricas em tempo real:
   * **Pings Enviados / Acks Recebidos:** Taxa de sucesso deve ser 100%.
   * **RTT Médio (Ida e Volta):** Tempo típico de 12 a 25 ms em 9600 baud.
   * **Heartbeat do Nano:** Mostra se o canal de telemetria (Nano -> ESP) está vivo com idade `< 2500 ms`.
   * **Causa do Último Reset do Nano:** Mostra se houve `Power-on`, `BROWN-OUT` ou `Reset externo`.
3. Clique em **"100 pings @ 10 Hz"** para realizar estresse contínuo sem perda de pacotes.

---

## 🎯 POC 2: Pan/Tilt Controlado (Sem Vídeo)

### Objetivo
Sintonizar os micro servos SG90 nos eixos Pan (D9) e Tilt (D10) do suporte robótico, validando a ausência do efeito "rebolado" em velocidades lentas.

### Gravação
```powershell
pio run -e poc2_esp32 -t upload --upload-port COM24
pio run -e poc2_nano  -t upload --upload-port COM18
```
*(Nota: Para quem usa o pino D0 do Nano direto sem BC337, use o ambiente `poc2_nano_hw`).*

### Como Testar
1. Acesse o painel web em `http://<IP>/`.
2. Controle manual suave: Mova os sliders de **Pan** e **Tilt** (0° a 180°). O movimento é contínuo e silencioso.
3. **Teste de Varredura ("Anti-Rebolado"):**
   * Selecione o eixo (Pan ou Tilt), defina a faixa (ex: 45° a 135°) e a velocidade baixa (5°/s ou 10°/s).
   * Clique em **"Iniciar varredura"**.
   * Observe o movimento contínuo da cruzeta plástica: o movimento não engasga nem balança para os lados.
4. **Sintonia em Tempo Real:**
   * Ajuste o **Piso de Aproximação** (evita stick-slip no ponto final).
   * Ajuste a **Antifolga (Backlash)** se houver folga perceptível nas engrenagens ao mudar de direção.

---

## ❄️ POC 3: Transmissão de Vídeo Fria (ESP32 Isolado)

### Objetivo
Operar a câmera OV5640 no ESP32-S3-CAM com as técnicas máximas de redução de temperatura em software, sem necessidade de componentes mecânicos extras.

### Gravação
```powershell
pio run -e poc3_esp32 -t upload --upload-port COM24
```

### Como Testar
1. Acesse `http://<IP>/`.
2. O vídeo MJPEG é servido na porta 82 (`http://<IP>:82/stream`) em uma Task dedicada no Core 0.
3. **Validação do Standby Térmico (Soft Power-Down):**
   * Clique em **"Parar vídeo (esfria)"**.
   * O sensor entra imediatamente em `MODO_DORMINDO` via registrador `0x3008 = 0x42`.
   * O consumo cai e a câmera esfria rapidamente na bancada.
   * Ao clicar em **"Iniciar vídeo"**, a imagem retorna em ~40 ms sem travar o ESP32.
4. **Presets Rápidos de Temperatura:**
   * **Frio:** QVGA (320x240), qualidade 26, XCLK 8 MHz, teto 12 FPS (câmera fria para observação prolongada).
   * **Equilibrado:** VGA (640x480), qualidade 20, XCLK 12 MHz, teto 15 FPS (ótima nitidez com temperatura controlada).
   * **Qualidade / Máximo:** SVGA/HD para testes específicos de resolução.

---

## 🎬 POC 4: Pan/Tilt + Transmissão (Desempenho da Imagem)

### Objetivo
Validar a operação simultânea da cabeça robótica: vídeo contínuo em alta taxa de quadros e rotação suave dos dois eixos sem congelamentos ou atrasos no WebSocket.

### Gravação
```powershell
pio run -e poc4_esp32 -t upload --upload-port COM24
# No Nano, utilize o firmware poc2_nano já gravado!
```

### Como Testar
1. Acesse `http://<IP>/`.
2. A tela consolida o visor de vídeo com os controles dos servos na mesma interface.
3. Enquanto você assiste ao vídeo a 20 FPS, mova os servos ou execute uma varredura.
4. **Modo Eco Automático:** Fique 8 segundos sem enviar comandos nos servos. O robô detecta a inatividade e reduz automaticamente a taxa de quadros para 5 FPS (`MODO_ECO`), poupando energia e calor enquanto está parado observando. Ao mover qualquer slider, a taxa salta instantaneamente de volta para 20 FPS.

---

## ⚙️ POC 5: Teste Automático de Motores 4WD (Bancada com Rodas no Ar)

### Objetivo
Testar as conexões da ponte H TB6612FNG, conferir a polaridade dos 4 motores JGA16-050 e medir a queda de tensão (*sag*) na bateria sem risco de colisões.

### Gravação
```powershell
pio run -e poc5_nano -t upload --upload-port COM18
pio device monitor -e poc5_nano --port COM18
```

### Como Testar
1. **ATENÇÃO:** Coloque o robô sobre um suporte para que as 4 rodas fiquem suspensas no ar.
2. Ao ligar, o código não aciona os motores por segurança.
3. No Serial Monitor a 115200 baud, digite:
   * `p` -> **Teste de Polaridade:** Aciona o lado esquerdo por 1,5s e depois o lado direito por 1,5s. Ambos devem girar para frente. Se algum lado girar para trás, digite `e` ou `d` para inverter por software!
   * `v` -> **Teste de Vai-e-Volta:** Executa rampa suave de aceleração (0 a 100% em 900ms), cruzeiro, rampa de frenagem, tempo morto de 200ms e aceleração em ré. Testa também a reversão brusca com frenagem eletrônica controlada.
   * `c` -> **Teste de Giros e Curvas:** Realiza giro sobre o próprio eixo e curva suave diferencial.
   * `g` -> **Sequência Completa:** Executa todas as rotinas em sequência.
   * `s` -> **Parada de Emergência Imediata.**
   * `+` / `-` -> Aumenta ou diminui o PWM máximo do teste em degraus de 20.
4. Observe a leitura de `Vbat` e `mínimo (sag)` impressa no terminal: confira se o mínimo se mantém com folga acima de 6,5V para garantir que a bateria suportará o chassi no chão.

---

## 🕹️ POC 6: Motores Controlados (Joystick Virtual / Teclado)

### Objetivo
Pilotar a tração 4WD em tempo real a partir de qualquer celular ou PC com proteção de segurança e rampa suave de aceleração.

### Gravação
```powershell
pio run -e poc6_esp32 -t upload --upload-port COM24
pio run -e poc6_nano  -t upload --upload-port COM18
```

### Como Testar
1. Conecte ao Wi-Fi `Rover-POC6` e acesse `http://<IP>/`.
2. Controle touch: Mova o **Joystick Virtual analógico** ou use o **D-pad** com botões direcionais.
3. Controle via teclado (em PCs/notebooks):
   * `W` ou `Seta Cima`: Frente
   * `S` ou `Seta Baixo`: Ré
   * `A` ou `Seta Esquerda`: Giro à Esquerda
   * `D` ou `Seta Direita`: Giro à Direita
   * `Barra de Espaço`: Parada Imediata de Emergência
4. **Failsafe de Segurança (Watchdog):**
   * Se você fechar a aba do navegador ou afastar o celular perdendo a conexão Wi-Fi, o Arduino Nano desacelera os motores e desliga a ponte H automaticamente após 600 ms sem pacotes.
