@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo                    AutoAFK - Complete Build
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM Check PyInstaller
echo [1/9] Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo       Installing PyInstaller...
    python -m pip install pyinstaller --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller!
        pause
        exit /b 1
    )
    echo       PyInstaller installed
) else (
    echo       PyInstaller ready
)
echo.

echo [2/9] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist updater.exe del /q updater.exe
echo       Cleaned
echo.

echo [3/9] Building updater...
echo       Compiling updater.exe...
pyinstaller updater.spec --clean >nul 2>&1
if errorlevel 1 (
    echo       [WARNING] Updater build failed
    set UPDATER_BUILT=0
) else (
    copy dist\updater.exe . >nul 2>&1
    echo       ✓ updater.exe compiled
    set UPDATER_BUILT=1
)
echo.

echo [4/9] Cleaning for main build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo       Cleaned
echo.

echo [5/9] Building main executable...
echo       This may take 5-10 minutes...
echo.

pyinstaller AutoAFK.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Main build failed!
    pause
    exit /b 1
)

echo.
echo [6/9] Copying required files...
copy settings.ini.example dist\AutoAFK\settings.ini >nul
copy README.md dist\AutoAFK\ >nul
copy CHANGELOG.md dist\AutoAFK\ >nul
if exist LICENSE copy LICENSE dist\AutoAFK\ >nul

REM Copy updater to _internal folder
if !UPDATER_BUILT! == 1 (
    copy updater.exe dist\AutoAFK\_internal\ >nul
    echo       Copied updater.exe to _internal
) else (
    copy updater.py dist\AutoAFK\_internal\ >nul
    echo       Copied updater.py to _internal
)

REM Copy update.bat to main folder (launcher for updater)
copy update.bat dist\AutoAFK\ >nul
echo       Files copied
echo.

echo [7/9] Cleaning build artifacts...
if exist build rmdir /s /q build
if exist updater.exe del /q updater.exe
echo       Build folder cleaned
echo.

echo [8/9] Creating distribution package...
echo       Waiting for file handles to release...
timeout /t 2 /nobreak >nul
cd dist
if exist AutoAFK.zip del /q AutoAFK.zip
tar -a -c -f AutoAFK.zip AutoAFK
if errorlevel 1 (
    echo       [WARNING] tar compression failed, trying alternative PowerShell method...
    powershell -command "Compress-Archive -Path AutoAFK -DestinationPath AutoAFK.zip -Force -CompressionLevel Optimal"
)
cd ..
if exist dist\AutoAFK.zip (
    echo       Package created: dist\AutoAFK.zip
) else (
    echo       [WARNING] ZIP creation failed - distribute folder manually
)
echo.

echo [9/9] Calculating sizes...
if exist dist\AutoAFK.zip (
    for %%F in (dist\AutoAFK.zip) do set SIZE=%%~zF
    set /a SIZE_MB=!SIZE! / 1024 / 1024
    echo       ZIP size: !SIZE_MB! MB
) else (
    echo       ZIP not created - skipping size calculation
    set SIZE_MB=0
)
echo.

echo ================================================================================
echo                         Build Complete!
echo ================================================================================
echo.
echo Output files:
echo   - dist\AutoAFK\AutoAFK.exe  (Main executable)
echo   - dist\AutoAFK\_internal\   (Required libraries)

if !UPDATER_BUILT! == 1 (
    echo   - dist\AutoAFK\updater.exe  (Updater - no Python needed!)
) else (
    echo   - dist\AutoAFK\updater.py   (Updater - requires Python)
)

echo   - dist\AutoAFK.zip          (Distribution package - !SIZE_MB! MB)
echo.
echo The package includes:
echo   - All Python dependencies
echo   - Image recognition files
echo   - Configuration template
echo   - ADB tools (adb.exe, AdbWinApi.dll)

if !UPDATER_BUILT! == 1 (
    echo   - Updater (updater.exe - fully compiled!)
) else (
    echo   - Updater (updater.py - requires Python)
)

echo   - Documentation
echo.
echo To distribute:
echo   1. Share dist\AutoAFK.zip
echo   2. Users extract entire folder
echo   3. Users run AutoAFK.exe
echo   4. Users configure settings.ini
echo.

if !UPDATER_BUILT! == 1 (
    echo Note: Updater is fully compiled - users don't need Python!
) else (
    echo Note: Updater requires Python - users need Python 3.8+ for updates
)

echo.
pause
