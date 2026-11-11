# 🚀 POC: Streaming de Vídeo UDP de Alta Performance & Benchmark

Este POC valida a transmissão de vídeo do sensor **OV5640 no ESP32-S3-CAM** diretamente via datagramas **UDP (Zero-Buffer)** para um servidor/computador em rede local (LAN), medindo **FPS real, latência (RTT), throughput (Mbps) e perda de pacotes** em tempo real.

---

## 🎯 Por que UDP em vez de HTTP/MJPEG?

| Característica | HTTP / MJPEG Clássico | UDP Puro (Este POC) |
| :--- | :--- | :--- |
| **Protocolo de Rede** | TCP (com confirmação e retransmissão) | UDP (sem confirmação / fire-and-forget) |
| **Comportamento em Oscilações** | Enfileira quadros velhos (**Buffer Lag de 300–800 ms**) | Descarta quadros incompletos (**Zero-Buffer / Tempo Real**) |
| **Latência Típica em LAN** | 150 a 300 ms | **30 a 60 ms** |
| **Taxa de Quadros (VGA 640×480)**| 8 a 12 FPS | **18 a 25 FPS** |
| **Sobrecarga na CPU do ESP32** | Alta (LwIP gerencia estado de conexões TCP) | Mínima (apenas cospe os blocos de bytes por DMA) |

---

## 🛠️ Arquitetura do Protocolo UDP (Fragmentação Inteligente)

Como cada foto JPEG varia entre 10 KB (QVGA) e 45 KB (SVGA), e o limite seguro por pacote Wi-Fi sem fragmentação IP é de **1400 bytes**, o ESP32 quebra cada frame em fatias com um cabeçalho binário compacto de **16 bytes**:

```text
[ Cabeçalho 16B ] + [ Fatia JPEG até 1400B ]
 ├─ Magic: 0x52565231 ('RVR1')
 ├─ frame_id: uint16
 ├─ chunk_id: uint16
 ├─ total_chunks: uint16
 ├─ payload_size: uint16
 └─ timestamp_us: uint32 (micros no ESP32)
```

O receptor em Python remonta os pedaços. Se um pacote for perdido no ar, ele **descarta o frame danificado imediatamente e pega o próximo**, garantindo que a tela nunca congele e a latência nunca se acumule.

---

## 💻 Como Executar o Teste Prático

### 1. Gravar o Firmware no ESP32-S3-CAM
Conecte o cabo USB no ESP32-S3 e execute no terminal:
```powershell
pio run -e poc_udp_camera -t upload --upload-port COM29
```
*(Substitua `COM29` pela porta correta do seu ESP32)*.

### 2. Executar o Servidor de Benchmark no PC
Abra outro terminal na pasta raiz do projeto e execute:
```powershell
python tools/benchmark_udp_camera.py
```
*(O script envia um broadcast na rede local e descobre o ESP32 automaticamente).*

Caso queira apontar direto para o IP do robô:
```powershell
python tools/benchmark_udp_camera.py --ip 192.168.137.233
```

---

## 🎮 Controles Interativos em Tempo Real (Janela OpenCV)

Com a janela de vídeo aberta, você pode testar o limite do hardware pressionando as teclas:

* **`1`**: Muda para **QVGA (320×240)** $\rightarrow$ Máxima velocidade e fluidez.
* **`2`**: Muda para **CIF (400×296)** $\rightarrow$ Resolução intermediária balanceada.
* **`3`**: Muda para **VGA (640×480)** $\rightarrow$ Ponto ideal de nitidez para visão computacional.
* **`4`**: Muda para **SVGA (800×600)** $\rightarrow$ Máxima resolução do teste.
* **`+` / `-`**: Ajusta o nível de compressão JPEG dinamicamente.
* **`Q` ou `ESC`**: Encerra o benchmark.

O HUD no topo do vídeo exibe em verde: **FPS decodificado**, **Bitrate (Mbps)**, **Resolução real**, **Tamanho médio do quadro**, **Taxa de descarte (%)** e **RTT (Latência de ida e volta em ms)**.
