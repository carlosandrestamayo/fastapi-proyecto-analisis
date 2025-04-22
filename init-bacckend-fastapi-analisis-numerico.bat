@echo off
cd /d C:\PythonProjects\fastapi-analisis

:: Abrir VSCode en el directorio actual
code .

:: Iniciar el servidor FastAPI
fastapi dev main.py

pause
