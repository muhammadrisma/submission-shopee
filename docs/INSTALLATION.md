# Installation Guide - Food Receipt Analyzer

## Prerequisites

### 1. Python Dependencies
Install Python packages:
```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR Installation

Tesseract OCR is required for text extraction from receipt images.

#### Windows
1. **Download Tesseract installer:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Install Tesseract:**
   - Run the installer as Administrator
   - Install to default location: `C:\Program Files\Tesseract-OCR\`
   - Make sure to check "Add to PATH" during installation

3. **Verify Installation:**
   ```cmd
   tesseract --version
   ```

4. **If PATH not set automatically:**
   - Add `C:\Program Files\Tesseract-OCR\` to your system PATH
   - Or set in your `.env` file:
   ```
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

#### macOS
```bash
# Using Homebrew
brew install tesseract

# Using MacPorts
sudo port install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install tesseract
# or
sudo dnf install tesseract
```

### 3. Verify Tesseract Installation

Run this command to verify Tesseract is properly installed:
```bash
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"
```

## Configuration

### 1. Environment Variables
Create a `.env` file in the project root:
```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Required for AI queries
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional - Tesseract path (if not in PATH)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Optional - Database and upload settings
DATABASE_PATH=data/receipts.db
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=10
STREAMLIT_PORT=8501
```

### 2. OpenRouter API Key
1. Sign up at https://openrouter.ai/
2. Get your API key from the dashboard
3. Add it to your `.env` file

## Running the Application

### Option 1: Using the run script
```bash
python run_app.py
```

### Option 2: Direct Streamlit command
```bash
streamlit run app.py
```

### Option 3: Using main.py
```bash
python main.py
```

## Testing the Installation

Run the integration test to verify everything works:
```bash
python test_integration.py
```

## Troubleshooting

### Tesseract Issues

**Error: "tesseract is not installed or it's not in your PATH"**

Solutions:
1. **Check if Tesseract is installed:**
   ```bash
   tesseract --version
   ```

2. **Find Tesseract location:**
   - Windows: Usually `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - macOS: Usually `/usr/local/bin/tesseract` or `/opt/homebrew/bin/tesseract`
   - Linux: Usually `/usr/bin/tesseract`

3. **Set explicit path in .env:**
   ```env
   TESSERACT_CMD=/path/to/tesseract
   ```

4. **Windows specific:**
   - Make sure you installed the 64-bit version if you have 64-bit Python
   - Try running Command Prompt as Administrator
   - Check Windows PATH environment variable

**Error: "Failed to load image"**

Solutions:
1. Check image file format (supported: JPG, PNG, PDF)
2. Verify image file is not corrupted
3. Check file permissions

### Database Issues

**Error: "Database initialization failed"**

Solutions:
1. Check if `data/` directory exists and is writable
2. Verify DATABASE_PATH in configuration
3. Ensure sufficient disk space

### API Issues

**Error: "OpenRouter API request failed"**

Solutions:
1. Verify your API key is correct
2. Check internet connection
3. Verify API key has sufficient credits

## System Requirements

- **Python:** 3.8 or higher
- **RAM:** 2GB minimum, 4GB recommended
- **Disk Space:** 500MB for application + space for uploaded receipts
- **OS:** Windows 10+, macOS 10.14+, or Linux

## Optional Enhancements

### GPU Acceleration (Advanced)
For faster image processing, you can install OpenCV with GPU support:
```bash
pip uninstall opencv-python
pip install opencv-contrib-python
```

### Additional Language Support
Tesseract supports multiple languages. Install additional language packs:
```bash
# Windows: Download language packs from GitHub
# Linux: 
sudo apt install tesseract-ocr-eng tesseract-ocr-spa tesseract-ocr-fra
```

## Getting Help

If you encounter issues:
1. Check this installation guide
2. Run the integration test: `python test_integration.py`
3. Check the application logs in the Streamlit interface
4. Verify all prerequisites are installed correctly