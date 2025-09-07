# Quick Start Guide - Food Receipt Analyzer

## 🚀 Get Running in 5 Minutes

This guide will get you up and running with the Food Receipt Analyzer in just a few minutes.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection (for AI queries)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd food-receipt-analyzer

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Install Tesseract OCR

### Windows
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer and add to PATH
3. Verify: `tesseract --version`

### macOS
```bash
brew install tesseract
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (use your preferred editor)
nano .env  # Linux/macOS
notepad .env  # Windows
```

**Minimum required configuration:**
```env
# Get your free API key from https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Set Tesseract path if not in PATH
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Step 4: Run the Application

```bash
# Start the application
python run_app.py

# Or use Streamlit directly
streamlit run app.py
```

The application will start and be available at: http://localhost:8501

## Step 5: Test with Sample Receipt

1. **Upload a Receipt**:
   - Click "Browse files" or drag and drop a receipt image
   - Supported formats: JPG, PNG, PDF
   - Maximum size: 10MB

2. **Review Extracted Data**:
   - Check the extracted store name, date, and items
   - Verify prices and totals are correct
   - Edit any incorrect information

3. **Save to Database**:
   - Click "Save Receipt" to store the data
   - Receipt will be added to your database

4. **Query Your Data**:
   - Try natural language queries like:
     - "What food did I buy yesterday?"
     - "How much did I spend this week?"
     - "Where did I buy milk?"

## Quick Test Commands

### Verify Installation
```bash
# Check all dependencies
python scripts/check_installation.py

# Test individual components
python -c "import streamlit; print('Streamlit OK')"
python -c "import pytesseract; print('Tesseract OK')"
python -c "from config import config; print('Config OK')"
```

### Run Demos
```bash
# Test computer vision
python demos/demo_computer_vision.py

# Test AI queries
python demos/demo_ai_query.py

# Test database operations
python demos/demo_database.py
```

## Common Quick Fixes

### Tesseract Not Found
```bash
# Find Tesseract location
which tesseract  # macOS/Linux
where tesseract  # Windows

# Add to .env file
echo "TESSERACT_CMD=/path/to/tesseract" >> .env
```

### API Key Issues
```bash
# Test API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://openrouter.ai/api/v1/models

# Should return list of available models
```

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or set in .env
echo "STREAMLIT_PORT=8502" >> .env
```

## Docker Quick Start

If you prefer Docker:

```bash
# Build and run with Docker Compose
cp .env.example .env
# Edit .env with your API key
docker-compose up -d

# View logs
docker-compose logs -f

# Access at http://localhost:8501
```

## Sample Queries to Try

Once you have some receipts uploaded, try these queries:

### Basic Queries
- "What did I buy today?"
- "Show me yesterday's purchases"
- "List all my receipts"

### Spending Analysis
- "How much did I spend this week?"
- "What's my total spending this month?"
- "Show me my most expensive purchase"

### Item Searches
- "Where did I buy milk?"
- "When did I last buy bread?"
- "Show me all dairy products"

### Store Queries
- "What stores have I shopped at?"
- "How much did I spend at Walmart?"
- "Show me receipts from Target"

## Next Steps

### Explore Features
- Upload multiple receipts to build your database
- Try different types of natural language queries
- Explore the analytics and insights features

### Customize Configuration
- Adjust file size limits in `.env`
- Configure logging levels
- Set up custom upload folders

### Advanced Usage
- Check out the API documentation for programmatic access
- Explore the demo scripts for advanced features
- Review the troubleshooting guide for optimization tips

## Getting Help

If you encounter issues:

1. **Check the logs** in the Streamlit interface
2. **Run the installation checker**: `python scripts/check_installation.py`
3. **Review the troubleshooting guide**: `docs/TROUBLESHOOTING.md`
4. **Test individual components** using the demo scripts

## What's Next?

- **[Full Documentation](../README.md)**: Complete feature overview
- **[API Documentation](API_DOCUMENTATION.md)**: Internal service APIs
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Common issues and solutions
- **[Environment Variables](ENVIRONMENT_VARIABLES.md)**: Complete configuration guide

You're now ready to start digitizing and analyzing your food receipts! 🎉