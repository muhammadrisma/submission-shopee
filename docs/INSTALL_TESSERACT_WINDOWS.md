# Installing Tesseract OCR on Windows

## Quick Installation Guide

### Step 1: Download Tesseract
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer:
   - For 64-bit Windows: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)
   - For 32-bit Windows: `tesseract-ocr-w32-setup-5.3.3.20231005.exe`

### Step 2: Install Tesseract
1. **Run the installer as Administrator** (right-click → "Run as administrator")
2. **Important:** During installation, make sure to check **"Add to PATH"**
3. Install to the default location: `C:\Program Files\Tesseract-OCR\`
4. Complete the installation

### Step 3: Verify Installation
Open Command Prompt and run:
```cmd
tesseract --version
```

You should see output like:
```
tesseract 5.3.3
 leptonica-1.83.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 2.1.4) : libpng 1.6.39 : libtiff 4.5.1 : zlib 1.2.13 : libwebp 1.3.2 : libopenjp2 2.5.0
```

### Step 4: Test with Python
Run this command to test Python integration:
```cmd
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"
```

## If Installation Doesn't Work

### Option 1: Manual PATH Setup
If Tesseract wasn't added to PATH automatically:

1. **Find Tesseract installation path:**
   - Default: `C:\Program Files\Tesseract-OCR\`
   - Look for `tesseract.exe` in this folder

2. **Add to Windows PATH:**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Under "System Variables", find and select "Path"
   - Click "Edit" → "New"
   - Add: `C:\Program Files\Tesseract-OCR\`
   - Click OK on all dialogs
   - **Restart Command Prompt/PowerShell**

### Option 2: Set Explicit Path in .env
If you can't modify system PATH, set the explicit path in your `.env` file:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Troubleshooting

### Error: "Access Denied" during installation
- Run the installer as Administrator
- Temporarily disable antivirus software

### Error: "tesseract is not recognized"
- Check if PATH was added correctly
- Restart your terminal/command prompt
- Try the explicit path method in .env

### Error: "Permission denied"
- Make sure the installation directory is writable
- Run Command Prompt as Administrator when testing

### Different Installation Path
If you installed to a different location, update the path accordingly:
```env
TESSERACT_CMD=D:\YourCustomPath\Tesseract-OCR\tesseract.exe
```

## After Installation

1. **Restart your terminal/command prompt**
2. **Run the diagnostic again:**
   ```cmd
   python check_installation.py
   ```
3. **Test the application:**
   ```cmd
   python run_app.py
   ```

## Quick Fix: If PATH Issues Persist

If you're still having PATH issues, you can use one of these methods:

### Method 1: Use the Windows Batch File
```cmd
run_app.bat
```
This automatically sets the PATH and runs the application.

### Method 2: Set PATH Manually Before Running
```cmd
set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
python run_app.py
```

### Method 3: Use PowerShell
```powershell
$env:PATH = "C:\Program Files\Tesseract-OCR;" + $env:PATH
python run_app.py
```

## Alternative: Portable Installation

If you can't install system-wide:

1. Download the portable version from the same GitHub page
2. Extract to a folder (e.g., `C:\tesseract\`)
3. Set in your `.env` file:
   ```env
   TESSERACT_CMD=C:\tesseract\tesseract.exe
   ```

## Verification Commands

After installation, these commands should work:

```cmd
# Check Tesseract version
tesseract --version

# Check Python integration
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# Run full diagnostic
python check_installation.py

# Test the application
python run_app.py
```

Once Tesseract is installed, your Food Receipt Analyzer will be able to extract text from receipt images!