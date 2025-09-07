@echo off
echo 🧾 Starting Food Receipt Analyzer...

REM Add Tesseract to PATH
set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"

REM Check if Tesseract is available
tesseract --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Tesseract OCR found
) else (
    echo ⚠️  Tesseract OCR not found - receipt processing may not work
    echo    Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
)

REM Run the Python application
python run_app.py

pause