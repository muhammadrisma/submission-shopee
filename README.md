# Food Receipt Analyzer

A comprehensive AI-powered system for digitizing, analyzing, and querying food receipts using computer vision and natural language processing.

## 📁 Project Structure

```
food-receipt-analyzer/
├── 📁 app.py                    # Main Streamlit application
├── 📁 config.py                 # Configuration management
├── 📁 requirements.txt          # Python dependencies
├── 📁 .env.example              # Environment variables template
├── 📁 Makefile                  # Build and development commands
│
├── 📁 database/                 # Database layer
│   ├── __init__.py
│   ├── connection.py            # Database connection management
│   └── service.py               # Database service layer
│
├── 📁 models/                   # Data models
│   ├── __init__.py
│   └── receipt.py               # Receipt and ReceiptItem models
│
├── 📁 services/                 # Business logic services
│   ├── __init__.py
│   ├── computer_vision.py       # OCR and image processing
│   ├── ai_query.py              # Natural language query processing
│   └── vector_db.py             # Vector similarity search
│
├── 📁 ui/                       # User interface components
│   ├── __init__.py
│   ├── upload_interface.py      # Receipt upload UI
│   └── query_interface.py       # Query interface UI
│
├── 📁 utils/                    # Utility modules
│   ├── __init__.py
│   ├── error_handling.py        # Comprehensive error handling
│   └── validation.py            # Input validation utilities
│
├── 📁 tests/                    # Test suite
│   ├── __init__.py
│   ├── test_error_handling.py   # Error handling tests
│   ├── test_computer_vision.py  # Computer vision tests
│   ├── test_ai_query.py         # AI query tests
│   ├── test_database.py         # Database tests
│   ├── test_models.py           # Model tests
│   ├── test_integration.py      # Integration tests
│   ├── test_complete_flow.py    # End-to-end tests
│   ├── test_enhanced_streamlit.py
│   ├── test_streamlit_vector_integration.py
│   └── test_vector_ai_integration.py
│
├── 📁 demos/                    # Demonstration scripts
│   ├── __init__.py
│   ├── demo_computer_vision.py  # Computer vision demo
│   ├── demo_ai_query.py         # AI query demo
│   ├── demo_database.py         # Database demo
│   ├── demo_vector_db.py        # Vector search demo
│   └── demo_complete_system.py  # Full system demo
│
├── 📁 debug/                    # Debug utilities
│   ├── __init__.py
│   ├── debug_ai_query.py        # AI query debugging
│   ├── debug_database.py        # Database debugging
│   ├── debug_parsing.py         # Receipt parsing debugging
│   ├── debug_real_receipt.py    # Real receipt debugging
│   ├── debug_targeted_parsing.py
│   └── debug_total.py
│
├── 📁 scripts/                  # Utility scripts
│   ├── __init__.py
│   ├── run_error_tests.py       # Error handling test runner
│   ├── check_installation.py    # Installation checker
│   ├── csv_parser_clean.py      # CSV parsing utilities
│   └── simple_chunking.py       # Text chunking utilities
│
├── 📁 docs/                     # Documentation
│   ├── ERROR_HANDLING.md        # Error handling guide
│   └── INSTALLATION.md          # Installation guide
│
├── 📁 data/                     # Data storage
│   └── receipts.db              # SQLite database
│
├── 📁 uploads/                  # Temporary file uploads
│
└── 📁 .kiro/                    # Kiro IDE specifications
    └── specs/food-receipt-analyzer/
        ├── requirements.md
        ├── design.md
        └── tasks.md
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd food-receipt-analyzer

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (required for text extraction)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt install tesseract-ocr
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# OPENROUTER_API_KEY=your_api_key_here  # For AI queries
# TESSERACT_CMD=/path/to/tesseract       # If not in PATH
```

### 3. Run the Application

```bash
# Start the Streamlit app
streamlit run app.py

# Or use the convenience script
python run_app.py
```

## 🧪 Testing

### Run All Tests
```bash
# Run the complete test suite
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_error_handling.py -v
python -m pytest tests/test_computer_vision.py -v
python -m pytest tests/test_ai_query.py -v
```

### Run Error Handling Tests
```bash
# Comprehensive error handling tests
python scripts/run_error_tests.py
```

### Check Installation
```bash
# Verify all dependencies are installed
python scripts/check_installation.py
```

## 🎯 Demos

### Computer Vision Demo
```bash
# Test OCR and receipt parsing
python demos/demo_computer_vision.py
```

### AI Query Demo
```bash
# Test natural language query processing
python demos/demo_ai_query.py
```

### Database Demo
```bash
# Test database operations
python demos/demo_database.py
```

### Vector Search Demo
```bash
# Test semantic similarity search
python demos/demo_vector_db.py
```

### Complete System Demo
```bash
# Test the full pipeline
python demos/demo_complete_system.py
```

## 🔧 Debug Tools

### Debug AI Queries
```bash
python debug/debug_ai_query.py
```

### Debug Database
```bash
python debug/debug_database.py
```

### Debug Receipt Parsing
```bash
python debug/debug_parsing.py
python debug/debug_real_receipt.py
```

## 📚 Features

### 🔍 Computer Vision
- **Image Preprocessing**: Noise reduction, contrast enhancement, morphological operations
- **OCR Text Extraction**: Tesseract integration with optimized configuration
- **Receipt Parsing**: Intelligent extraction of store names, dates, items, and totals
- **Error Handling**: Comprehensive validation and recovery mechanisms

### 🤖 AI-Powered Queries
- **Natural Language Processing**: Query intent recognition and parameter extraction
- **Semantic Search**: Vector-based similarity search for food items
- **Response Generation**: AI-powered natural language responses
- **Multiple Query Types**: Item searches, spending analysis, store queries

### 💾 Data Management
- **SQLite Database**: Efficient local storage with full-text search
- **Data Models**: Structured receipt and item representations
- **CRUD Operations**: Complete database service layer
- **Data Validation**: Comprehensive input validation and consistency checks

### 🎨 User Interface
- **Streamlit Web App**: Modern, responsive web interface
- **File Upload**: Drag-and-drop receipt image upload with validation
- **Query Interface**: Chat-style natural language query interface
- **Dashboard**: Analytics and insights visualization
- **Error Handling**: User-friendly error messages with recovery suggestions

### 🛡️ Error Handling & Validation
- **Comprehensive Validation**: File, text, and data validation
- **Retry Mechanisms**: Automatic retry with exponential backoff
- **Error Categories**: Structured error classification and handling
- **User-Friendly Messages**: Clear error messages with recovery suggestions
- **Monitoring**: Error statistics and debugging tools

## 🔧 Configuration

### Environment Variables
```bash
# Required for AI queries
OPENROUTER_API_KEY=your_api_key_here

# Optional configurations
DATABASE_PATH=data/receipts.db
MAX_FILE_SIZE_MB=10
TESSERACT_CMD=/path/to/tesseract
STREAMLIT_PORT=8501
```

### File Upload Limits
- **Maximum file size**: 10MB (configurable)
- **Supported formats**: JPG, JPEG, PNG, PDF
- **Image validation**: Size, format, and content validation

## 🤝 Development

### Code Structure
- **Modular Design**: Clear separation of concerns
- **Error Handling**: Comprehensive error handling throughout
- **Testing**: Extensive test coverage with integration tests
- **Documentation**: Detailed documentation and examples
- **Type Hints**: Full type annotation for better code quality

### Best Practices
- **PEP 8**: Python code style compliance
- **Error Handling**: Graceful error handling with user feedback
- **Logging**: Comprehensive logging for debugging
- **Validation**: Input validation at all entry points
- **Testing**: Test-driven development approach

## 📖 Documentation

- **[Error Handling Guide](docs/ERROR_HANDLING.md)**: Comprehensive error handling documentation
- **[Installation Guide](docs/INSTALLATION.md)**: Detailed installation instructions
- **API Documentation**: Inline code documentation with examples

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract not found**
   ```bash
   # Install Tesseract OCR
   # Windows: Download from GitHub releases
   # macOS: brew install tesseract
   # Linux: sudo apt install tesseract-ocr
   ```

2. **OpenRouter API errors**
   ```bash
   # Set your API key in .env
   OPENROUTER_API_KEY=your_key_here
   ```

3. **Database permission errors**
   ```bash
   # Check file permissions
   chmod 664 data/receipts.db
   ```

### Debug Tools
Use the debug scripts in the `debug/` folder to troubleshoot specific components.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Tesseract OCR**: Google's open-source OCR engine
- **OpenRouter**: AI model API gateway
- **Streamlit**: Python web app framework
- **OpenCV**: Computer vision library
- **SQLite**: Embedded database engine