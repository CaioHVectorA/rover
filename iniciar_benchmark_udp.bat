@echo off
title ROVER - Benchmark de Video UDP de Alta Performance
echo ==============================================================
echo Conectando ao ESP32-S3-CAM no IP 192.168.7.20 (Porta UDP 5005)
echo ==============================================================
python tools\benchmark_udp_camera.py --ip 192.168.7.20
pause
