@echo off
REM AutoAFK Updater Launcher

REM Check for self-updates and other staged files first
for /r "_internal" %%f in (*.new) do (
    set "target=%%~dpnf"
    echo [INFO] Applying update to %%~nxf...
    del "!target!" >nul 2>&1
    move "%%f" "!target!" >nul 2>&1
)

if exist "AutoAFKUpdater.py.new" (
    echo [INFO] Applying updater update...
    del "AutoAFKUpdater.py" >nul 2>&1
    move "AutoAFKUpdater.py.new" "AutoAFKUpdater.py" >nul 2>&1
)

REM Try compiled updater first (in _internal folder)
if exist "_internal\AutoAFKUpdater.exe" (
    _internal\AutoAFKUpdater.exe %*
    exit /b %ERRORLEVEL%
)

REM Fallback to Python version
if exist "_internal\AutoAFKUpdater.py" (
    echo [INFO] Using Python updater
    
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
    
    python _internal\AutoAFKUpdater.py %*
    exit /b %ERRORLEVEL%
)

if exist "AutoAFKUpdater.py" (
    echo [INFO] Using Python updater
    python AutoAFKUpdater.py %*
    exit /b %ERRORLEVEL%
)



echo [ERROR] Updater not found in _internal folder!
pause
exit /b 1
