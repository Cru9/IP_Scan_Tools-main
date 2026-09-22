@echo off
title IP_Scan_Tools - Propiedad de Ezequiel Diaz

REM Auto-elevacion a Permisos de Administrador para Scapy y Escaneo de Red
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo  Solicitando Permisos de Administrador para Escaneo de Red Completo...
    echo ================================================================================
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
cls
echo ================================================================================
echo                IP_Scan_Tools v2.0 - Propiedad de Ezequiel Diaz
echo ================================================================================
echo.

REM [1/4] Crear entorno virtual venv si no existe
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creando entorno virtual de Python venv aislado...
    python -m venv venv
    if errorlevel 1 (
        echo [!] Error al crear el entorno virtual. Verifique su instalacion de Python.
        pause
        exit /b
    )
    echo [OK] Entorno virtual venv creado exitosamente.
) else (
    echo [1/4] Entorno virtual venv detectado.
)

REM [2/4] Activar el entorno virtual
call venv\Scripts\activate.bat

REM [3/4] Comprobar e instalar librerias de Python dentro del venv solo si faltan
python -c "import customtkinter, PIL, requests, scapy, speedtest, plyer" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [2/4] Instalando dependencias en el entorno virtual venv...
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [!] Reintentando instalacion de dependencias...
        python -m pip install customtkinter pillow requests scapy plyer speedtest-cli python-whois
    )
) else (
    echo [2/4] Dependencias verificadas correctamente [OK].
)

echo.
echo [3/4] Verificando permisos de Administrador... [OK]
echo.
echo [4/4] Iniciando la suite de monitoreo de red, Wi-Fi, seguridad y velocidad...
echo.

python gui_app.py
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo [ERROR] No se pudo iniciar IP_Scan_Tools.
    echo ================================================================================
    pause
)
