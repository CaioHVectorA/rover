@echo off
title ROVER TREKKING - Autonomous Mission Control (YOLOv8 + Radar + Gemini)
echo ==============================================================
echo Conectando ao ESP32-S3 via Descoberta UDP (Porta 5005)
echo Missao: Radar Pan/Tilt, Deteccao de Cones/Garrafas e Desvio
echo ==============================================================
python tools\rover_trekking.py %*
pause
