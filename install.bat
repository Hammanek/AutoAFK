@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo                    AutoAFK - Installation
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8-3.12 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo       Python %PYTHON_VERSION% detected
echo.

echo [2/4] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
) else (
    echo       pip upgraded
)
echo.

echo [3/4] Installing dependencies...
echo       This may take a few minutes...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Try running manually: 
    echo   python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo       Dependencies installed
echo.

echo [4/4] Setting up configuration...
if not exist settings.ini (
    if exist settings.ini.example (
        copy settings.ini.example settings.ini >nul
        echo       Created settings.ini from example
        echo.
        echo [IMPORTANT] Edit settings.ini and configure your device!
    ) else (
        echo [WARNING] settings.ini.example not found!
    )
) else (
    echo       settings.ini already exists
)
echo.

echo ================================================================================
echo                         Installation Complete!
echo ================================================================================
echo.
echo Next steps:
echo   1. Connect your emulator/device
echo   2. Run "adb devices" to find your device name
echo   3. Edit settings.ini and set device_name
echo   4. Run start.bat to launch AutoAFK
echo.
echo For compiled version users:
echo   - No installation needed, just run AutoAFK.exe
echo   - Configure settings.ini and you're ready!
echo.
pause
