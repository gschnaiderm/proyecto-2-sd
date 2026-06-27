@echo off
:: Desactivar eco para que la consola se vea limpia
title Cliente de Busqueda HTTP

:: Verificar si existe el entorno virtual en la raiz del proyecto (carpeta padre) o local
if exist "..\.venv" (
    set "VENV_PATH=..\.venv"
) else if exist ".venv" (
    set "VENV_PATH=.venv"
) else (
    echo [ERROR] No se encontro la carpeta del entorno virtual venv ni en la raiz del proyecto ni en esta carpeta.
    echo Por favor, asegurate de que el entorno virtual este creado.
    pause
    exit /b 1
)

echo Iniciando cliente de busqueda HTTP...
:: Ejecutamos python directamente desde el entorno virtual pasando la ruta del script.
:: Como se realizo un refactor plano, el cliente esta directamente en la raiz de este microservicio: "client.py"
"%VENV_PATH%\Scripts\python.exe" "client.py"

pause
