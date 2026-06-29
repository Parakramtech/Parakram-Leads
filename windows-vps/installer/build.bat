@echo off
REM Parakram VPS Installer Builder
REM Builds the Windows installer EXE using PyInstaller

echo Building Parakram VPS Installer...
echo ================================

cd /d "%~dp0installer"

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
del /f /q *.spec 2>nul

REM Install build dependencies
echo Installing build dependencies...
python -m pip install pyinstaller customtkinter Pillow httpx >nul

REM Build the executable
echo Building EXE...
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name ParakramVPS-Setup ^
    --add-data "ui;ui" ^
    --add-data "core;core" ^
    --add-data "theme.py;." ^
    --hidden-import customtkinter ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import httpx ^
    --collect-all customtkinter ^
    app.py

if errorlevel 1 (
    echo.
    echo Build FAILED!
    exit /b 1
) else (
    echo.
    echo Build SUCCESSFUL!
    echo Output: dist\ParakramVPS-Setup.exe
    echo.
    echo To create a signed installer, you can use:
    echo   signtool sign /fd SHA256 /a dist\ParakramVPS-Setup.exe
)