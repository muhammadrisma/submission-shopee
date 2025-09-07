# Troubleshooting Guide - Food Receipt Analyzer

## Overview

This guide provides solutions to common issues encountered when installing, configuring, and using the Food Receipt Analyzer application.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [OCR and Computer Vision Issues](#ocr-and-computer-vision-issues)
4. [AI Query Service Issues](#ai-query-service-issues)
5. [Database Problems](#database-problems)
6. [Web Interface Issues](#web-interface-issues)
7. [Performance Issues](#performance-issues)
8. [Docker and Deployment Issues](#docker-and-deployment-issues)
9. [Error Messages and Solutions](#error-messages-and-solutions)
10. [Getting Help](#getting-help)

## Installation Issues

### Python Dependencies

#### Issue: `pip install` fails with permission errors
**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**
```bash
# Option 1: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Option 2: Install for user only
pip install --user -r requirements.txt

# Option 3: Use sudo (Linux/macOS only, not recommended)
sudo pip install -r requirements.txt
```

#### Issue: Package conflicts or version incompatibilities
**Symptoms:**
```
ERROR: pip's dependency resolver does not currently consider all the packages that are installed
```

**Solutions:**
```bash
# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Or use pip-tools for dependency resolution
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

### Tesseract OCR Installation

#### Issue: Tesseract not found after installation
**Symptoms:**
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**Solutions:**

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to default location: C:\Program Files\Tesseract-OCR\

# Add to PATH or set in .env:
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Verify installation:
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

**macOS:**
```bash
# Install via Homebrew
brew install tesseract

# If not in PATH, find location:
which tesseract
# Add to .env if needed:
TESSERACT_CMD=/usr/local/bin/tesseract

# Verify installation:
tesseract --version
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr

# CentOS/RHEL
sudo yum install tesseract
# or
sudo dnf install tesseract

# Verify installation:
tesseract --version
```

#### Issue: Tesseract installed but Python can't find it
**Solutions:**
```python
# Test Tesseract availability
import pytesseract
from PIL import Image

# Set explicit path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Test with simple image
try:
    text = pytesseract.image_to_string(Image.new('RGB', (100, 100), 'white'))
    print("Tesseract working!")
except Exception as e:
    print(f"Tesseract error: {e}")
```

## Configuration Problems

### Environment Variables

#### Issue: API key not recognized
**Symptoms:**
```
Error: OpenRouter API key not configured
```

**Solutions:**
```bash
# Check .env file exists and has correct format
cat .env
# Should contain:
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Verify environment variable is loaded
python -c "from config import config; print(f'API Key: {config.OPENROUTER_API_KEY[:10]}...')"

# Test API key validity
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://openrouter.ai/api/v1/models
```

#### Issue: Configuration file not found
**Symptoms:**
```
FileNotFoundError: .env file not found
```

**Solutions:**
```bash
# Copy example file
cp .env.example .env

# Edit with your settings
nano .env  # Linux/macOS
notepad .env  # Windows

# Verify file exists
ls -la .env
```

### Database Configuration

#### Issue: Database file permissions
**Symptoms:**
```
sqlite3.OperationalError: unable to open database file
```

**Solutions:**
```bash
# Check file permissions
ls -la data/receipts.db

# Fix permissions
chmod 664 data/receipts.db
chown $USER:$USER data/receipts.db

# Create directory if missing
mkdir -p data
```

## OCR and Computer Vision Issues

### Image Processing Problems

#### Issue: Poor OCR accuracy
**Symptoms:**
- Incorrect text extraction
- Missing text from receipts
- Garbled characters

**Solutions:**
```python
# Improve image preprocessing
from services.computer_vision import ComputerVisionService

cv_service = ComputerVisionService()

# Try different OCR configurations
configs = [
    '--oem 3 --psm 6',  # Default
    '--oem 3 --psm 8',  # Single word
    '--oem 3 --psm 13', # Raw line
    '--oem 1 --psm 6',  # LSTM only
]

for config in configs:
    result = cv_service.extract_text_with_config(image_path, config)
    print(f"Config {config}: {result['confidence']}% confidence")
```

**Image Quality Tips:**
- Use high-resolution images (300+ DPI)
- Ensure good lighting and contrast
- Avoid blurry or skewed images
- Crop to receipt area only

#### Issue: Supported image formats
**Symptoms:**
```
PIL.UnidentifiedImageError: cannot identify image file
```

**Solutions:**
```python
# Check supported formats
from PIL import Image
print(f"Supported formats: {Image.registered_extensions()}")

# Convert unsupported formats
from PIL import Image

def convert_to_supported_format(input_path, output_path):
    with Image.open(input_path) as img:
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output_path, 'JPEG', quality=95)
```

### Receipt Parsing Issues

#### Issue: Store name not detected
**Solutions:**
```python
# Debug parsing with verbose output
from services.computer_vision import ComputerVisionService

cv_service = ComputerVisionService()
result = cv_service.parse_receipt_data(text, debug=True)

# Check parsing patterns
print(f"Store patterns found: {result['debug_info']['store_patterns']}")
print(f"Date patterns found: {result['debug_info']['date_patterns']}")
```

#### Issue: Incorrect price parsing
**Solutions:**
```python
# Test price parsing patterns
import re

price_patterns = [
    r'\$?(\d+\.\d{2})',
    r'(\d+,\d{3}\.\d{2})',
    r'(\d+\.\d{2})\s*\$',
]

text = "Total: $25.99"
for pattern in price_patterns:
    matches = re.findall(pattern, text)
    print(f"Pattern {pattern}: {matches}")
```

## AI Query Service Issues

### API Connection Problems

#### Issue: OpenRouter API connection fails
**Symptoms:**
```
requests.exceptions.ConnectionError: Failed to establish a new connection
```

**Solutions:**
```bash
# Test internet connectivity
ping openrouter.ai

# Test API endpoint
curl -v https://openrouter.ai/api/v1/models

# Check firewall/proxy settings
export https_proxy=http://your-proxy:port  # If behind proxy

# Test with Python
python -c "
import requests
response = requests.get('https://openrouter.ai/api/v1/models', 
                       headers={'Authorization': 'Bearer YOUR_KEY'})
print(f'Status: {response.status_code}')
print(f'Response: {response.text[:200]}')
"
```

#### Issue: API rate limiting
**Symptoms:**
```
HTTP 429: Too Many Requests
```

**Solutions:**
```python
# Implement retry with backoff
import time
import random

def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited, waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                raise e
```

### Query Processing Issues

#### Issue: Natural language queries not understood
**Solutions:**
```python
# Test query parsing
from services.ai_query import AIQueryService

ai_service = AIQueryService()

# Try different query formats
queries = [
    "What food did I buy yesterday?",
    "Show me purchases from yesterday",
    "List items bought on 2024-01-15",
    "Find food from yesterday's receipts"
]

for query in queries:
    result = ai_service.parse_query_intent(query)
    print(f"Query: {query}")
    print(f"Intent: {result['intent']}, Confidence: {result['confidence']}")
```

## Database Problems

### Connection Issues

#### Issue: Database locked
**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
```bash
# Check for other processes using database
lsof data/receipts.db  # Linux/macOS
handle data/receipts.db  # Windows (with handle.exe)

# Kill processes if safe to do so
# Or restart application

# Check database integrity
sqlite3 data/receipts.db "PRAGMA integrity_check;"
```

#### Issue: Database corruption
**Symptoms:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solutions:**
```bash
# Backup current database
cp data/receipts.db data/receipts.db.backup

# Try to repair
sqlite3 data/receipts.db ".recover" | sqlite3 data/receipts_recovered.db

# Or restore from backup
cp data/receipts.db.backup data/receipts.db

# Recreate database if necessary
python -c "
from database.service import DatabaseService
db = DatabaseService()
db.initialize_database()
"
```

### Data Issues

#### Issue: Duplicate receipts
**Solutions:**
```python
# Find duplicates
from database.service import DatabaseService

db_service = DatabaseService()
duplicates = db_service.find_duplicate_receipts()

for duplicate_group in duplicates:
    print(f"Duplicates found: {duplicate_group}")
    # Keep newest, remove others
    db_service.remove_duplicate_receipts(duplicate_group[1:])
```

## Web Interface Issues

### Streamlit Problems

#### Issue: Streamlit won't start
**Symptoms:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions:**
```bash
# Install Streamlit
pip install streamlit

# Verify installation
streamlit --version

# Test basic Streamlit app
echo "import streamlit as st; st.write('Hello')" > test.py
streamlit run test.py
```

#### Issue: Port already in use
**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
```bash
# Find process using port
netstat -tulpn | grep 8501  # Linux
lsof -i :8501              # macOS
netstat -ano | findstr 8501 # Windows

# Kill process or use different port
streamlit run app.py --server.port 8502

# Or set in .env
STREAMLIT_PORT=8502
```

### File Upload Issues

#### Issue: File upload fails
**Symptoms:**
- Upload button not responding
- Files not processing

**Solutions:**
```python
# Check file size limits
import os
file_size = os.path.getsize('receipt.jpg')
max_size = 10 * 1024 * 1024  # 10MB
print(f"File size: {file_size}, Max: {max_size}")

# Check file permissions
import stat
file_stat = os.stat('receipt.jpg')
print(f"File permissions: {stat.filemode(file_stat.st_mode)}")

# Test file reading
try:
    with open('receipt.jpg', 'rb') as f:
        data = f.read(100)  # Read first 100 bytes
    print("File readable")
except Exception as e:
    print(f"File read error: {e}")
```

## Performance Issues

### Slow Processing

#### Issue: OCR processing takes too long
**Solutions:**
```python
# Optimize image size before processing
from PIL import Image

def optimize_image(image_path, max_size=2048):
    with Image.open(image_path) as img:
        # Resize if too large
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to grayscale for faster OCR
        if img.mode != 'L':
            img = img.convert('L')
        
        # Save optimized version
        optimized_path = image_path.replace('.jpg', '_optimized.jpg')
        img.save(optimized_path, 'JPEG', quality=85, optimize=True)
        return optimized_path
```

#### Issue: Database queries slow
**Solutions:**
```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_receipts_date ON receipts(receipt_date);
CREATE INDEX IF NOT EXISTS idx_receipts_store ON receipts(store_name);
CREATE INDEX IF NOT EXISTS idx_items_name ON receipt_items(item_name);
CREATE INDEX IF NOT EXISTS idx_items_receipt ON receipt_items(receipt_id);

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM receipts WHERE receipt_date > '2024-01-01';
```

### Memory Issues

#### Issue: Out of memory errors
**Solutions:**
```python
# Process images in batches
def process_images_batch(image_paths, batch_size=5):
    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i+batch_size]
        for image_path in batch:
            # Process image
            result = process_image(image_path)
            yield result
        
        # Force garbage collection
        import gc
        gc.collect()

# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

## Docker and Deployment Issues

### Container Problems

#### Issue: Docker build fails
**Solutions:**
```bash
# Check Dockerfile syntax
docker build --no-cache -t receipt-analyzer .

# Build with verbose output
docker build --progress=plain -t receipt-analyzer .

# Check base image availability
docker pull python:3.11-slim
```

#### Issue: Container won't start
**Solutions:**
```bash
# Check container logs
docker logs container_name

# Run container interactively
docker run -it receipt-analyzer /bin/bash

# Check port mapping
docker run -p 8501:8501 receipt-analyzer

# Check environment variables
docker run -e OPENROUTER_API_KEY=your_key receipt-analyzer
```

### Volume and Persistence Issues

#### Issue: Data not persisting
**Solutions:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  receipt-analyzer:
    build: .
    volumes:
      - ./data:/app/data          # Database persistence
      - ./uploads:/app/uploads    # Upload persistence
    environment:
      - DATABASE_PATH=/app/data/receipts.db
```

## Error Messages and Solutions

### Common Error Messages

#### `ValidationError: Invalid file format`
**Solution:**
- Use supported formats: JPG, JPEG, PNG, PDF
- Check file is not corrupted
- Verify file extension matches content

#### `OCRError: Text extraction failed`
**Solution:**
- Check image quality and resolution
- Verify Tesseract installation
- Try different OCR configuration

#### `DatabaseError: Connection failed`
**Solution:**
- Check database file permissions
- Verify database path in configuration
- Ensure sufficient disk space

#### `APIError: Authentication failed`
**Solution:**
- Verify API key is correct
- Check API key has sufficient credits
- Test API key with curl command

### Debug Mode

Enable debug mode for detailed error information:

```python
# In .env file
DEBUG=True
LOG_LEVEL=DEBUG

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Getting Help

### Self-Diagnosis

1. **Run the installation checker:**
   ```bash
   python scripts/check_installation.py
   ```

2. **Run comprehensive tests:**
   ```bash
   python scripts/run_error_tests.py
   ```

3. **Check system requirements:**
   ```bash
   python -c "
   import sys
   print(f'Python version: {sys.version}')
   import platform
   print(f'OS: {platform.system()} {platform.release()}')
   "
   ```

### Collecting Debug Information

When reporting issues, include:

```bash
# System information
python --version
pip list | grep -E "(streamlit|opencv|pytesseract|pillow)"

# Configuration (sanitized)
python -c "
from config import config
print(f'Database path: {config.DATABASE_PATH}')
print(f'Upload folder: {config.get_upload_path()}')
print(f'API key configured: {bool(config.OPENROUTER_API_KEY)}')
print(f'Tesseract path: {config.TESSERACT_CMD}')
"

# Test results
python scripts/check_installation.py > debug_info.txt 2>&1
```

### Log Analysis

Check application logs for patterns:

```bash
# Search for errors
grep -i error logs/app.log

# Search for specific components
grep -i "tesseract\|ocr" logs/app.log
grep -i "database\|sqlite" logs/app.log
grep -i "api\|openrouter" logs/app.log
```

### Community Resources

- Check existing issues in the project repository
- Review documentation in the `docs/` folder
- Test with minimal examples from `demos/` folder
- Use debug scripts in `debug/` folder

This troubleshooting guide covers the most common issues. For specific problems not covered here, enable debug mode and collect detailed error information before seeking help.