@echo off
setlocal
cd /d d:\app\mes
echo Starting MES Dashboard MVC Server in Virtual Environment...

if not exist venv (
    echo Error: Virtual environment 'venv' not found.
    pause
    exit /b
)

echo Activating environment...
call .\venv\Scripts\activate.bat

echo Running server...
python run.py

pause
endlocal
