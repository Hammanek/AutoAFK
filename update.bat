@echo off
REM AutoAFK Updater Launcher

REM Try compiled updater first (in _internal folder)
if exist "_internal\updater.exe" (
    _internal\updater.exe
    exit /b %ERRORLEVEL%
)

REM Fallback to Python version (in _internal folder)
if exist "_internal\updater.py" (
    echo [INFO] Using Python updater (updater.exe not found)
    
    REM Check Python
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found!
        echo [INFO] Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    REM Install requests if needed
    python -c "import requests" 2>nul
    if errorlevel 1 (
        echo [INFO] Installing requests...
        python -m pip install requests --quiet
    )
    
    python _internal\updater.py
    exit /b %ERRORLEVEL%
)

echo [ERROR] Updater not found in _internal folder!
pause
exit /b 1
