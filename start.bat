@echo off
echo ========================================
echo   AutoAFK
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Run AutoAFK
echo Starting AutoAFK...
echo.
python main.py