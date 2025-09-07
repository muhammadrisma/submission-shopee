# Environment Variables Configuration Guide

## Overview

The Food Receipt Analyzer uses environment variables for configuration management. This document provides comprehensive documentation for all available environment variables.

## Configuration Files

### `.env` File
The primary configuration file located in the project root. Copy from `.env.example`:

```bash
cp .env.example .env
```

### Environment Variable Precedence
1. System environment variables (highest priority)
2. `.env` file variables
3. Default values in `config.py` (lowest priority)

## Required Variables

### OpenRouter API Configuration

#### `OPENROUTER_API_KEY`
- **Required**: Yes (for AI query functionality)
- **Type**: String
- **Description**: API key for OpenRouter service used for natural language processing
- **Example**: `OPENROUTER_API_KEY=sk-or-v1-abc123def456...`
- **How to get**: 
  1. Sign up at https://openrouter.ai/
  2. Navigate to API Keys section
  3. Create a new API key
  4. Copy the key to your `.env` file

#### `OPENROUTER_BASE_URL`
- **Required**: No
- **Type**: String
- **Default**: `https://openrouter.ai/api/v1`
- **Description**: Base URL for OpenRouter API
- **Example**: `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1`

#### `OPENROUTER_MODEL`
- **Required**: No
- **Type**: String
- **Default**: `deepseek/deepseek-chat-v3.1:free`
- **Description**: AI model to use for query processing
- **Example**: `OPENROUTER_MODEL=deepseek/deepseek-chat-v3.1:free`
- **Available Models**:
  - `deepseek/deepseek-chat-v3.1:free` (Free tier)
  - `openai/gpt-3.5-turbo` (Paid)
  - `anthropic/claude-3-haiku` (Paid)

## Optional Variables

### Database Configuration

#### `DATABASE_PATH`
- **Required**: No
- **Type**: String
- **Default**: `data/receipts.db`
- **Description**: Path to SQLite database file
- **Example**: `DATABASE_PATH=data/receipts.db`
- **Notes**: 
  - Directory will be created automatically
  - Use absolute path for custom locations
  - Ensure write permissions

### Streamlit Configuration

#### `STREAMLIT_PORT`
- **Required**: No
- **Type**: Integer
- **Default**: `8501`
- **Description**: Port number for Streamlit web server
- **Example**: `STREAMLIT_PORT=8501`
- **Valid Range**: 1024-65535
- **Notes**: Ensure port is not in use by other applications

#### `STREAMLIT_HOST`
- **Required**: No
- **Type**: String
- **Default**: `0.0.0.0`
- **Description**: Host address for Streamlit server
- **Example**: `STREAMLIT_HOST=localhost`
- **Options**:
  - `0.0.0.0` - Accept connections from any IP
  - `localhost` - Local connections only
  - `127.0.0.1` - Local connections only

### File Upload Configuration

#### `MAX_FILE_SIZE_MB`
- **Required**: No
- **Type**: Integer
- **Default**: `10`
- **Description**: Maximum file size for uploads in megabytes
- **Example**: `MAX_FILE_SIZE_MB=10`
- **Valid Range**: 1-100
- **Notes**: Larger files require more processing time and memory

#### `UPLOAD_FOLDER`
- **Required**: No
- **Type**: String
- **Default**: `uploads`
- **Description**: Directory for temporary file uploads
- **Example**: `UPLOAD_FOLDER=uploads`
- **Notes**: 
  - Directory will be created automatically
  - Files are cleaned up after processing

#### `ALLOWED_EXTENSIONS`
- **Required**: No
- **Type**: String (comma-separated)
- **Default**: `jpg,jpeg,png,pdf`
- **Description**: Allowed file extensions for uploads
- **Example**: `ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf`

### OCR Configuration

#### `TESSERACT_CMD`
- **Required**: No (if Tesseract is in PATH)
- **Type**: String
- **Description**: Full path to Tesseract executable
- **Platform Examples**:
  - Windows: `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`
  - macOS: `TESSERACT_CMD=/usr/local/bin/tesseract`
  - Linux: `TESSERACT_CMD=/usr/bin/tesseract`
- **Notes**: Only required if Tesseract is not in system PATH

#### `TESSERACT_CONFIG`
- **Required**: No
- **Type**: String
- **Default**: `--oem 3 --psm 6`
- **Description**: Tesseract OCR configuration parameters
- **Example**: `TESSERACT_CONFIG=--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`
- **Common Options**:
  - `--oem 3` - Use default OCR Engine Mode
  - `--psm 6` - Assume uniform block of text
  - `--psm 8` - Single word mode
  - `--psm 13` - Raw line mode

### Logging Configuration

#### `LOG_LEVEL`
- **Required**: No
- **Type**: String
- **Default**: `INFO`
- **Description**: Logging level for application
- **Example**: `LOG_LEVEL=DEBUG`
- **Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

#### `LOG_FILE`
- **Required**: No
- **Type**: String
- **Default**: None (console only)
- **Description**: Path to log file
- **Example**: `LOG_FILE=logs/app.log`
- **Notes**: Directory will be created automatically

### Performance Configuration

#### `MAX_WORKERS`
- **Required**: No
- **Type**: Integer
- **Default**: `4`
- **Description**: Maximum number of worker threads for processing
- **Example**: `MAX_WORKERS=4`
- **Notes**: Adjust based on system resources

#### `PROCESSING_TIMEOUT`
- **Required**: No
- **Type**: Integer
- **Default**: `30`
- **Description**: Timeout for OCR processing in seconds
- **Example**: `PROCESSING_TIMEOUT=30`

#### `CACHE_SIZE`
- **Required**: No
- **Type**: Integer
- **Default**: `100`
- **Description**: Maximum number of cached results
- **Example**: `CACHE_SIZE=100`

### Development Configuration

#### `DEBUG`
- **Required**: No
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable debug mode
- **Example**: `DEBUG=True`
- **Notes**: Shows detailed error messages and stack traces

#### `DEVELOPMENT_MODE`
- **Required**: No
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable development features
- **Example**: `DEVELOPMENT_MODE=True`
- **Features**:
  - Auto-reload on code changes
  - Detailed logging
  - Test data generation

## Platform-Specific Configuration

### Windows Configuration

```env
# Windows-specific settings
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
DATABASE_PATH=C:\Users\YourName\Documents\receipts.db
UPLOAD_FOLDER=C:\temp\uploads
```

### macOS Configuration

```env
# macOS-specific settings
TESSERACT_CMD=/usr/local/bin/tesseract
DATABASE_PATH=/Users/yourname/Documents/receipts.db
UPLOAD_FOLDER=/tmp/uploads
```

### Linux Configuration

```env
# Linux-specific settings
TESSERACT_CMD=/usr/bin/tesseract
DATABASE_PATH=/home/yourname/data/receipts.db
UPLOAD_FOLDER=/tmp/uploads
```

## Docker Configuration

### Docker Environment Variables

When running in Docker, use these additional variables:

#### `DOCKER_ENV`
- **Required**: No
- **Type**: Boolean
- **Default**: `False`
- **Description**: Indicates running in Docker container
- **Example**: `DOCKER_ENV=True`

#### `CONTAINER_PORT`
- **Required**: No
- **Type**: Integer
- **Default**: `8501`
- **Description**: Internal container port
- **Example**: `CONTAINER_PORT=8501`

### Docker Compose Example

```yaml
# docker-compose.yml
version: '3.8'
services:
  receipt-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DATABASE_PATH=/app/data/receipts.db
      - UPLOAD_FOLDER=/app/uploads
      - STREAMLIT_PORT=8501
      - DOCKER_ENV=True
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
```

## Configuration Validation

### Validation Script

Run the configuration validation script:

```bash
python scripts/check_installation.py
```

### Manual Validation

Check configuration in Python:

```python
from config import config

# Check required variables
print(f"API Key configured: {bool(config.OPENROUTER_API_KEY)}")
print(f"Database path: {config.DATABASE_PATH}")
print(f"Tesseract path: {config.TESSERACT_CMD}")

# Test database connection
from database.service import DatabaseService
db_service = DatabaseService()
print(f"Database accessible: {db_service.test_connection()}")

# Test OCR
from services.computer_vision import ComputerVisionService
cv_service = ComputerVisionService()
print(f"OCR available: {cv_service.test_ocr()}")
```

## Security Considerations

### API Key Security

1. **Never commit API keys to version control**
2. **Use environment variables or secure vaults**
3. **Rotate API keys regularly**
4. **Monitor API usage for anomalies**

### File Path Security

1. **Use absolute paths when possible**
2. **Validate file paths to prevent directory traversal**
3. **Set appropriate file permissions**
4. **Clean up temporary files**

### Database Security

1. **Set appropriate database file permissions**
2. **Use database encryption for sensitive data**
3. **Regular database backups**
4. **Monitor database access**

## Troubleshooting

### Common Configuration Issues

#### API Key Not Working
```bash
# Test API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://openrouter.ai/api/v1/models
```

#### Tesseract Not Found
```bash
# Check Tesseract installation
tesseract --version

# Find Tesseract location
which tesseract  # Linux/macOS
where tesseract  # Windows
```

#### Database Permission Issues
```bash
# Check database file permissions
ls -la data/receipts.db

# Fix permissions
chmod 664 data/receipts.db
```

#### Port Already in Use
```bash
# Find process using port
netstat -tulpn | grep 8501  # Linux
lsof -i :8501              # macOS
netstat -ano | findstr 8501 # Windows
```

### Configuration Testing

Test individual components:

```python
# Test configuration loading
from config import config
print("Configuration loaded successfully")

# Test API connection
from services.ai_query import AIQueryService
ai_service = AIQueryService()
result = ai_service.test_connection()
print(f"API connection: {result}")

# Test database
from database.service import DatabaseService
db_service = DatabaseService()
result = db_service.test_connection()
print(f"Database connection: {result}")

# Test OCR
from services.computer_vision import ComputerVisionService
cv_service = ComputerVisionService()
result = cv_service.test_ocr()
print(f"OCR available: {result}")
```

## Best Practices

### Environment Management

1. **Use separate `.env` files for different environments**
   - `.env.development`
   - `.env.staging`
   - `.env.production`

2. **Document all environment variables**
3. **Use meaningful default values**
4. **Validate configuration on startup**
5. **Provide clear error messages for missing configuration**

### Configuration Organization

```env
# Group related variables
# ======================

# API Configuration
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=deepseek/deepseek-chat-v3.1:free

# Database Configuration
DATABASE_PATH=data/receipts.db

# Server Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0

# File Processing
MAX_FILE_SIZE_MB=10
UPLOAD_FOLDER=uploads

# OCR Configuration
TESSERACT_CMD=/usr/local/bin/tesseract
```

This comprehensive guide covers all environment variables and configuration options for the Food Receipt Analyzer application.