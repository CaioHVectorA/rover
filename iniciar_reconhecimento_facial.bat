@echo off
chcp 65001 > nul
title ROVER BIOMETRIC AI - RECONHECIMENTO FACIAL E LABELING

echo ======================================================================
echo       ROVER BIOMETRIC AI - DETECCAO, RECONHECIMENTO E LABELS
echo ======================================================================
echo.
echo Modelos Ativos:
echo   - Deteccao: YuNet ONNX (60+ FPS, 5 marcos anatomicos)
echo   - Reconhecimento: SFace ONNX (Embeddings 128-D)
echo.
echo Comandos Disponiveis neste Launcher:
echo   [1] Iniciar Stream UDP do Rover (ESP32-S3)
echo   [2] Listar Rostos Cadastrados no Banco
echo   [3] Cadastrar Rosto a partir de um Arquivo de Foto (.jpg/.png)
echo   [4] Testar Reconhecimento em um Arquivo de Foto (.jpg/.png)
echo   [5] Sair
echo.
set /p OPT="Escolha uma opcao [1-5]: "

if "%OPT%"=="1" (
    cls
    echo Iniciando conexao UDP com o Rover na porta 5005...
    python tools\reconhecimento_facial.py --udp
    pause
    exit /b
)

if "%OPT%"=="2" (
    cls
    python tools\reconhecimento_facial.py --listar
    pause
    exit /b
)

if "%OPT%"=="3" (
    cls
    set /p NOME="Digite o Nome da Pessoa (ex: Caihe): "
    set /p FOTO="Arraste o arquivo da foto aqui ou digite o caminho: "
    python tools\reconhecimento_facial.py --cadastrar "%NOME%" --foto %FOTO%
    pause
    exit /b
)

if "%OPT%"=="4" (
    cls
    set /p FOTO="Arraste o arquivo da foto aqui ou digite o caminho: "
    python tools\reconhecimento_facial.py --reconhecer %FOTO%
    pause
    exit /b
)

exit /b
