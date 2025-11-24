@echo off
rem Lanceur générique pour exécuter le bot depuis Windows.
rem Copie ce fichier en lanceur.bat et ajuste si besoin les chemins ci-dessous.

set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"

pushd "%PROJECT_DIR%"
"%PYTHON%" main.py
popd

pause
