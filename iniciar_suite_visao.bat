@echo off
title ROVER - Suite Autonoma de Visao Computacional (UDP + IA)
echo ==============================================================
echo Conectando ao ESP32-S3 via Descoberta UDP (Porta 5005)
echo Modos: [1] Rosto  [2] Gestos  [3] Garrafa  [0] Streaming Puro
echo ==============================================================
python tools\rover_vision_suite.py %*
pause
