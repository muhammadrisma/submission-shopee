# Error Handling and Validation Guide

This document describes the comprehensive error handling and validation system implemented in the Food Receipt Analyzer.

## Overview

The application implements a multi-layered error handling approach:

1. **Input Validation** - Validates all user inputs and file uploads
2. **Retry Mechanisms** - Handles transient failures with exponential backoff
3. **User-Friendly Messages** - Provides clear error messages and recovery suggestions
4. **Centralized Error Handling** - Consistent error processing across the application
5. **Error Monitoring** - Tracks error statistics for debugging and monitoring

## Error Categories

### 1. Validation Errors
- **File Upload Validation**: Size, format, and content validation
- **Text Input Validation**: Query sanitization and format checking
- **Data Validation**: Price, quantity, and date validation
- **Receipt Data Validation**: Consistency checks and business logic validation

### 2. System Errors
- **File System Errors**: File access, permissions, and storage issues
- **OCR Errors**: Tesseract installation, image processing failures
- **Database Errors**: Connection issues, data integrity problems
- **Network Errors**: API connectivity, timeout, and rate limiting

### 3. Configuration Errors
- **Missing API Keys**: OpenRouter API configuration
- **Invalid Settings**: Environment variable validation
- **Dependency Issues**: Missing or misconfigured dependencies

## Error Handling Components

### ErrorHandler Class

The centralized error handler provides:

```python
from utils.error_handling import error_handler

# Handle any exception
result = error_handler.handle_error(exception, context={'user_id': 123})

# Get error statistics
stats = error_handler.get_error_statistics()
```

### Validation Utilities

#### File Validation
```python
from utils.validation import file_validator

try:
    result = file_validator.validate_file(uploaded_file, filename)
    print(f"File is valid: {result}")
except ValidationError as e:
    print(f"Validation failed: {e.user_message}")
    print(f"Recovery suggestions: {e.recovery_suggestions}")
```

#### Text Validation
```python
from utils.validation import TextValidator

try:
    clean_query = TextValidator.validate_query(user_input)
except ValidationError as e:
    print(f"Invalid input: {e.user_message}")
```

#### Data Validation
```python
from utils.validation import DataValidator

try:
    price = DataValidator.validate_price("$12.34")
    quantity = DataValidator.validate_quantity("5")
    date = DataValidator.validate_date("2024-01-15")
except ValidationError as e:
    print(f"Data validation error: {e.user_message}")
```

### Retry Mechanism

Automatic retry with exponential backoff:

```python
from utils.error_handling import with_retry
import requests

@with_retry(max_retries=3, retry_on=(requests.RequestException,))
def api_call():
    response = requests.get("https://api.example.com/data")
    return response.json()
```

### Error Decorators

Automatic error handling for functions:

```python
from utils.error_handling import with_error_handling, ErrorCategory

@with_error_handling(
    category=ErrorCategory.OCR,
    recovery_suggestions=["Check image quality", "Try different image"]
)
def process_image(image_path):
    # Function implementation
    pass
```

## Error Types and Recovery

### File Upload Errors

| Error | Cause | Recovery Suggestions |
|-------|-------|---------------------|
| File too large | File exceeds size limit | Compress image, use smaller file |
| Invalid format | Unsupported file type | Use JPG, PNG, or PDF format |
| Corrupted file | File cannot be read | Re-upload file, check file integrity |
| Empty file | File has no content | Select a different file |

### OCR Processing Errors

| Error | Cause | Recovery Suggestions |
|-------|-------|---------------------|
| Tesseract not found | OCR software not installed | Install Tesseract OCR, check PATH |
| Image too small | Image resolution too low | Use higher resolution image |
| No text extracted | Image has no readable text | Check image quality, try different image |
| Processing timeout | Image too complex | Try simpler image, check system resources |

### AI Service Errors

| Error | Cause | Recovery Suggestions |
|-------|-------|---------------------|
| API key missing | Configuration not set | Set OPENROUTER_API_KEY in .env |
| Authentication failed | Invalid API key | Check API key validity and credits |
| Rate limit exceeded | Too many requests | Wait before retrying, check usage limits |
| Network timeout | Connection issues | Check internet connection, try again |

### Database Errors

| Error | Cause | Recovery Suggestions |
|-------|-------|---------------------|
| Connection failed | Database not accessible | Check database file permissions |
| Data integrity error | Invalid data format | Validate input data, check constraints |
| Storage full | Insufficient disk space | Free up disk space, check storage |

## User Interface Error Handling

### Upload Interface

The upload interface provides comprehensive error feedback:

```python
# Validation with user-friendly messages
validation_result = upload_interface._validate_uploaded_file(file)

if not validation_result["valid"]:
    st.error(f"❌ {validation_result['error']}")
    
    # Show recovery suggestions
    if validation_result.get('recovery_suggestions'):
        with st.expander("💡 How to Fix This"):
            for suggestion in validation_result['recovery_suggestions']:
                st.write(f"• {suggestion}")
```

### Query Interface

Query processing with error handling:

```python
try:
    result = ai_service.process_query(user_query)
    if result['success']:
        st.write(result['formatted_response'])
    else:
        st.error(result['formatted_response'])
except Exception as e:
    error_response = error_handler.handle_error(e)
    st.error(error_response['error']['message'])
```

## Error Monitoring and Debugging

### Error Statistics

Track error patterns and frequency:

```python
stats = error_handler.get_error_statistics()
print(f"Total errors: {stats['total_errors']}")
print(f"Error types: {stats['error_counts']}")
print(f"Recent errors: {stats['recent_errors']}")
```

### Logging Configuration

Errors are automatically logged with appropriate levels:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Debug Mode

Enable detailed error information:

```python
# In Streamlit interface
if st.checkbox("Show technical details"):
    with st.expander("🔧 Technical Details"):
        st.write(f"Error Category: {error_info['category']}")
        st.write(f"Severity: {error_info['severity']}")
        st.json(error_response['technical_details'])
```

## Testing Error Scenarios

### Running Error Tests

```bash
# Run all error handling tests
python run_error_tests.py

# Run specific test categories
python -m pytest tests/test_error_handling.py::TestFileValidator -v
python -m pytest tests/test_error_handling.py::TestRetryMechanism -v
```

### Manual Testing Scenarios

1. **File Upload Errors**
   - Upload oversized file (>10MB)
   - Upload invalid format (.txt, .doc)
   - Upload corrupted image file
   - Upload empty file

2. **OCR Processing Errors**
   - Process image without Tesseract installed
   - Process very small image (<50px)
   - Process image with no text
   - Process corrupted image file

3. **AI Service Errors**
   - Query without API key configured
   - Query with invalid API key
   - Query during network outage
   - Query with malicious content

4. **Database Errors**
   - Save receipt with invalid data
   - Query database when file is locked
   - Exceed storage limits

## Best Practices

### 1. Error Message Design
- Use clear, non-technical language
- Provide specific recovery suggestions
- Include relevant context information
- Avoid exposing sensitive details

### 2. Error Handling Strategy
- Fail fast for validation errors
- Retry transient failures automatically
- Provide fallback options when possible
- Log errors for debugging

### 3. User Experience
- Show progress indicators during processing
- Provide immediate feedback for user actions
- Offer alternative approaches when errors occur
- Maintain application state during errors

### 4. Monitoring and Maintenance
- Track error patterns and frequencies
- Monitor system health metrics
- Update error messages based on user feedback
- Regularly test error scenarios

## Configuration

### Environment Variables

```bash
# .env file
OPENROUTER_API_KEY=your_api_key_here
TESSERACT_CMD=/usr/local/bin/tesseract  # Optional: explicit path
MAX_FILE_SIZE_MB=10
DATABASE_PATH=data/receipts.db
```

### Error Handling Settings

```python
# config.py
class Config:
    # Error handling configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    ERROR_LOG_LEVEL = "INFO"
    SHOW_TECHNICAL_DETAILS = False
```

## Troubleshooting Common Issues

### 1. Tesseract OCR Not Found
```bash
# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH or set TESSERACT_CMD in .env

# macOS
brew install tesseract

# Linux
sudo apt install tesseract-ocr
```

### 2. OpenRouter API Issues
```bash
# Check API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://openrouter.ai/api/v1/models

# Verify credits and usage
# Visit: https://openrouter.ai/activity
```

### 3. Database Permission Issues
```bash
# Check file permissions
ls -la data/receipts.db

# Fix permissions
chmod 664 data/receipts.db
```

### 4. Memory Issues with Large Images
```python
# Resize images before processing
from PIL import Image

def resize_image(image_path, max_size=2048):
    with Image.open(image_path) as img:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img.save(image_path, optimize=True, quality=85)
```

## Support and Debugging

### Getting Help

1. Check error messages and recovery suggestions
2. Review logs for technical details
3. Test with minimal examples
4. Check system dependencies and configuration
5. Consult documentation and troubleshooting guides

### Reporting Issues

When reporting errors, include:
- Error message and category
- Steps to reproduce
- System information (OS, Python version)
- Configuration details (sanitized)
- Log excerpts (without sensitive data)

This comprehensive error handling system ensures robust operation and provides users with clear guidance when issues occur.