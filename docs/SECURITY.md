# Security Guidelines

This document outlines the security measures implemented in the Food Receipt Analyzer application.

## Security Fixes Applied

### 1. SQL Injection Prevention
- **Issue**: String-based SQL query construction in `database/connection.py`
- **Fix**: Added table name validation and used bracket notation for table names
- **Location**: `get_database_info()` method

### 2. Shell Injection Prevention
- **Issue**: Using `subprocess.run()` with `shell=True` in CI scripts
- **Fix**: Split commands into lists to avoid shell interpretation
- **Location**: `scripts/local_ci_test.py`

### 3. Network Security
- **Issue**: Server binding to all interfaces (`0.0.0.0`)
- **Fix**: Default to localhost (`127.0.0.1`) with environment variable override
- **Location**: `run_app.py`
- **Environment Variable**: `STREAMLIT_SERVER_ADDRESS`

### 4. Safe Data Serialization
- **Issue**: Using `pickle` for vector serialization (unsafe deserialization)
- **Fix**: Replaced with `struct` module for safe binary serialization
- **Location**: `services/vector_db.py`

## Security Best Practices

### Environment Variables
- Store sensitive data like API keys in environment variables
- Never commit `.env` files to version control
- Use `.env.example` as a template

### Network Configuration
- By default, the application binds to localhost only
- To allow external access, set `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- Ensure proper firewall configuration when exposing to external networks

### Database Security
- SQLite database files should have appropriate file permissions
- Regular backups should be encrypted
- Consider using connection pooling for production deployments

### Input Validation
- All user inputs are validated before processing
- File uploads are restricted to supported image formats
- OCR text extraction is sandboxed

### Dependencies
- Regular security scans using `bandit` and `safety`
- Keep dependencies updated
- Monitor for security advisories

## Running Security Scans

```bash
# Install security tools
pip install -r requirements-dev.txt

# Run security scan
bandit -r . -ll -f json -o bandit-report.json

# Check for vulnerable dependencies
safety check

# Run all security checks
python scripts/local_ci_test.py
```

## Reporting Security Issues

If you discover a security vulnerability, please:

1. Do not create a public GitHub issue
2. Contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Security Checklist for Deployment

- [ ] Environment variables configured securely
- [ ] Database files have proper permissions
- [ ] Network access is properly restricted
- [ ] All dependencies are up to date
- [ ] Security scans pass without high/medium severity issues
- [ ] Logs don't contain sensitive information
- [ ] File upload directory has size limits
- [ ] Regular security updates are scheduled