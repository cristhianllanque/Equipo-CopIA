@echo off
title CopIA - Lanzador de Servidores Centrales
color 0A

echo ===================================================
echo     Iniciando el Cerebro Central de CopIA Edge     
echo ===================================================
echo.

echo [1/4] Abriendo panel de XAMPP (Recuerda darle a "Start" en MySQL)...
if exist "C:\xampp\xampp-control.exe" (
    start "" "C:\xampp\xampp-control.exe"
) else (
    echo XAMPP no se encontro en C:\xampp, abrelo manualmente.
)
timeout /t 3 >nul

echo [2/4] Iniciando Backend de Python (Base de Datos)...
start "CopIA - Backend API" cmd /k "cd /d %~dp0 && python api_main.py"
timeout /t 3 >nul

echo [3/4] Iniciando Frontend de la Pagina Web...
start "CopIA - Pagina Web" cmd /k "cd /d %~dp0Frontend && npm run dev"
timeout /t 3 >nul

echo [4/4] Iniciando Ngrok (El Tunel de Internet)...
start "CopIA - Ngrok" cmd /k "ngrok http 8000"

echo.
echo ===================================================
echo   ¡TODO LISTO PARA TU PRESENTACIÓN!
echo ===================================================
echo.
echo Ve a la ventana negra de Ngrok y copia el enlace nuevo.
echo.
pause
