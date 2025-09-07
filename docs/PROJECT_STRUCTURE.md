# Project Structure Guide

This document explains the organization and structure of the Food Receipt Analyzer project, following Python best practices for maintainable and scalable applications.

## 📁 Directory Structure

### Core Application
```
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Configuration management and environment variables
├── requirements.txt            # Python package dependencies
├── .env.example               # Environment variables template
└── Makefile                   # Build automation and development commands
```

### Source Code Organization

#### `/database/` - Data Layer
```
database/
├── __init__.py                # Package initialization
├── connection.py              # Database connection management and schema
└── service.py                 # Database service layer with CRUD operations
```
- **Purpose**: Handles all database operations and data persistence
- **Key Components**: SQLite connection management, database schema, service layer
- **Dependencies**: sqlite3, models

#### `/models/` - Data Models
```
models/
├── __init__.py                # Package initialization
└── receipt.py                 # Receipt and ReceiptItem data models
```
- **Purpose**: Defines data structures and business entities
- **Key Components**: Receipt model, ReceiptItem model, validation methods
- **Dependencies**: dataclasses, decimal, datetime

#### `/services/` - Business Logic
```
services/
├── __init__.py                # Package initialization
├── computer_vision.py         # OCR and image processing service
├── ai_query.py               # Natural language query processing
└── vector_db.py              # Vector similarity search service
```
- **Purpose**: Contains core business logic and external service integrations
- **Key Components**: Image processing, OCR, AI queries, vector search
- **Dependencies**: OpenCV, Tesseract, OpenRouter API, numpy

#### `/ui/` - User Interface
```
ui/
├── __init__.py                # Package initialization
├── upload_interface.py        # Receipt upload and processing UI
└── query_interface.py         # Natural language query interface
```
- **Purpose**: Streamlit UI components and user interaction logic
- **Key Components**: File upload handling, query interface, error display
- **Dependencies**: streamlit, services, utils

#### `/utils/` - Utilities
```
utils/
├── __init__.py                # Package initialization
├── error_handling.py          # Comprehensive error handling system
└── validation.py              # Input validation utilities
```
- **Purpose**: Common utilities and helper functions
- **Key Components**: Error handling, validation, retry mechanisms
- **Dependencies**: typing, enum, functools

### Testing and Quality Assurance

#### `/tests/` - Test Suite
```
tests/
├── __init__.py                # Package initialization
├── test_error_handling.py     # Error handling and validation tests
├── test_computer_vision.py    # Computer vision service tests
├── test_ai_query.py          # AI query processing tests
├── test_database.py          # Database operations tests
├── test_models.py            # Data model tests
├── test_integration.py       # Integration tests
├── test_complete_flow.py     # End-to-end workflow tests
├── test_enhanced_streamlit.py # Enhanced UI tests
├── test_streamlit_vector_integration.py # Vector search UI tests
└── test_vector_ai_integration.py # AI integration tests
```
- **Purpose**: Comprehensive test coverage for all components
- **Test Types**: Unit tests, integration tests, end-to-end tests
- **Framework**: pytest with fixtures and mocking

### Development and Debugging

#### `/demos/` - Demonstration Scripts
```
demos/
├── __init__.py                # Package initialization
├── demo_computer_vision.py    # Computer vision functionality demo
├── demo_ai_query.py          # AI query processing demo
├── demo_database.py          # Database operations demo
├── demo_vector_db.py         # Vector search demo
└── demo_complete_system.py   # Full system integration demo
```
- **Purpose**: Standalone scripts demonstrating specific functionality
- **Usage**: Learning, testing, and showcasing features
- **Target Audience**: Developers, users, stakeholders

#### `/debug/` - Debug Utilities
```
debug/
├── __init__.py                # Package initialization
├── debug_ai_query.py         # AI query debugging tools
├── debug_database.py         # Database debugging and inspection
├── debug_parsing.py          # Receipt parsing debugging
├── debug_real_receipt.py     # Real receipt processing debugging
├── debug_targeted_parsing.py # Targeted parsing debugging
└── debug_total.py            # Total calculation debugging
```
- **Purpose**: Debugging tools for development and troubleshooting
- **Usage**: Issue diagnosis, performance analysis, data inspection
- **Target Audience**: Developers, maintainers

#### `/scripts/` - Utility Scripts
```
scripts/
├── __init__.py                # Package initialization
├── run_error_tests.py         # Error handling test runner
├── check_installation.py      # Installation verification
├── csv_parser_clean.py        # CSV parsing utilities
└── simple_chunking.py         # Text chunking utilities
```
- **Purpose**: Standalone utility scripts for maintenance and operations
- **Usage**: Installation checks, test execution, data processing
- **Target Audience**: Developers, system administrators

### Documentation and Configuration

#### `/docs/` - Documentation
```
docs/
├── ERROR_HANDLING.md          # Error handling system documentation
├── PROJECT_STRUCTURE.md       # This document
└── INSTALLATION.md            # Installation and setup guide
```
- **Purpose**: Project documentation and guides
- **Content**: Architecture, setup, usage, troubleshooting
- **Target Audience**: Developers, users, contributors

#### `/.kiro/` - IDE Specifications
```
.kiro/
└── specs/food-receipt-analyzer/
    ├── requirements.md         # Project requirements specification
    ├── design.md              # System design document
    └── tasks.md               # Implementation task list
```
- **Purpose**: Kiro IDE project specifications and planning
- **Content**: Requirements, design decisions, task tracking
- **Target Audience**: Development team, project managers

### Data and Runtime

#### `/data/` - Data Storage
```
data/
└── receipts.db               # SQLite database file
```
- **Purpose**: Persistent data storage
- **Content**: Receipt data, items, metadata
- **Backup**: Should be included in backup strategies

#### `/uploads/` - Temporary Storage
```
uploads/                      # Temporary file upload storage
```
- **Purpose**: Temporary storage for uploaded files
- **Lifecycle**: Files are processed and cleaned up
- **Security**: Input validation and sanitization

## 🏗️ Architecture Principles

### Separation of Concerns
- **Data Layer**: Database operations isolated in `/database/`
- **Business Logic**: Core functionality in `/services/`
- **Presentation Layer**: UI components in `/ui/`
- **Utilities**: Common functionality in `/utils/`

### Dependency Management
- **Top-Down Dependencies**: Higher layers depend on lower layers
- **Interface Segregation**: Clear interfaces between components
- **Dependency Injection**: Configuration and services injected where needed

### Error Handling Strategy
- **Centralized Error Handling**: Common error handling in `/utils/error_handling.py`
- **Layered Error Handling**: Each layer handles appropriate errors
- **User-Friendly Messages**: Technical errors translated to user messages

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Full workflow testing
- **Test Organization**: Tests mirror source code structure

## 📦 Package Dependencies

### Core Dependencies
```python
# Web Framework
streamlit>=1.28.0

# Computer Vision
opencv-python>=4.8.0
pytesseract>=0.3.10
Pillow>=10.0.0

# AI and ML
requests>=2.31.0
numpy>=1.24.0

# Data Processing
python-dotenv>=1.0.0
```

### Development Dependencies
```python
# Testing
pytest>=7.4.0
pytest-mock>=3.11.0

# Code Quality
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

## 🔧 Development Workflow

### Setting Up Development Environment
1. **Clone Repository**: `git clone <repo-url>`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Configure Environment**: Copy `.env.example` to `.env`
4. **Run Tests**: `python -m pytest tests/`
5. **Start Application**: `streamlit run app.py`

### Adding New Features
1. **Create Feature Branch**: `git checkout -b feature/new-feature`
2. **Write Tests**: Add tests in appropriate `/tests/` files
3. **Implement Feature**: Add code in appropriate packages
4. **Update Documentation**: Update relevant documentation
5. **Run Full Test Suite**: Ensure all tests pass
6. **Create Pull Request**: Submit for review

### Debugging Workflow
1. **Identify Issue**: Use application logs and error messages
2. **Use Debug Scripts**: Run appropriate scripts from `/debug/`
3. **Write Reproduction Test**: Add test case in `/tests/`
4. **Fix Issue**: Implement fix in appropriate package
5. **Verify Fix**: Run tests and debug scripts

## 📋 Best Practices

### Code Organization
- **Single Responsibility**: Each module has a clear, single purpose
- **DRY Principle**: Common functionality extracted to utilities
- **Clear Naming**: Descriptive names for modules, classes, and functions
- **Documentation**: Comprehensive docstrings and comments

### Error Handling
- **Fail Fast**: Validate inputs early and clearly
- **Graceful Degradation**: Provide fallbacks where possible
- **User-Friendly Messages**: Translate technical errors to user language
- **Comprehensive Logging**: Log errors with context for debugging

### Testing
- **Test Coverage**: Aim for high test coverage across all components
- **Test Isolation**: Tests should be independent and repeatable
- **Mock External Dependencies**: Use mocks for external services
- **Test Data**: Use fixtures and factories for test data

### Security
- **Input Validation**: Validate all user inputs
- **File Upload Security**: Validate file types and content
- **Environment Variables**: Use environment variables for sensitive data
- **Error Information**: Don't expose sensitive information in errors

This structure provides a solid foundation for maintaining and scaling the Food Receipt Analyzer application while following Python best practices and ensuring code quality.