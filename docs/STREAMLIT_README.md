# Food Receipt Analyzer - Streamlit Web Interface

## Overview

The Food Receipt Analyzer now includes a complete Streamlit web interface that provides:

- 📤 **Receipt Upload Interface** - Upload and process receipt images
- 🤖 **Natural Language Queries** - Ask questions about your receipts in plain English
- 📊 **Dashboard** - View analytics and insights about your spending
- ⚙️ **Settings** - Configure the application

## Features Implemented

### 1. Receipt Upload Interface (`ui/upload_interface.py`)
- ✅ File upload widget with validation for image formats and size
- ✅ Upload progress indicators and error handling
- ✅ Receipt preview and extracted data display components
- ✅ Integration with computer vision service
- ✅ Database storage of processed receipts

### 2. Natural Language Query Interface (`ui/query_interface.py`)
- ✅ Chat-style input interface for user queries
- ✅ Query history and results display
- ✅ Loading indicators for AI processing
- ✅ Integration with AI query service
- ✅ Query suggestions and examples

### 3. Main Streamlit Application (`app.py`)
- ✅ Complete integration of all services
- ✅ Session state management for user data
- ✅ Comprehensive error handling and user feedback
- ✅ Multi-page navigation (Upload, Query, Dashboard, Settings)
- ✅ Sidebar with statistics and configuration status

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

## Application Structure

```
📁 ui/
├── upload_interface.py    # Receipt upload and processing UI
├── query_interface.py     # Natural language query UI
└── __init__.py

📄 app.py                  # Main Streamlit application
📄 main.py                 # Entry point
📄 run_app.py             # Application runner script
📄 test_integration.py    # Integration tests
```

## Pages and Features

### 📤 Upload Page
- Upload receipt images (JPG, PNG, PDF)
- Real-time image preview
- Processing progress indicators
- Extracted data display with validation warnings
- Recent receipts overview

### 🤖 Query Page
- Natural language query input
- Example query suggestions
- Query history with re-run capability
- AI-powered response formatting
- Query statistics and analytics

### 📊 Dashboard
- Overview metrics (total receipts, items, spending)
- Recent activity timeline
- Quick action buttons
- Spending analytics

### ⚙️ Settings
- Configuration status checks
- API key management
- Database information
- Data management tools

## Key Components

### Session State Management
- Current page navigation
- Query history persistence
- Last processed receipt data
- Application initialization state

### Error Handling
- Graceful error boundaries
- User-friendly error messages
- Configuration validation
- Service availability checks

### Integration Points
- Computer Vision Service integration
- Database Service integration
- AI Query Service integration
- Configuration management

## Configuration

The application uses the existing configuration system:

```python
# Required for AI queries
OPENROUTER_API_KEY=your_api_key_here

# Optional customizations
STREAMLIT_PORT=8501
MAX_FILE_SIZE_MB=10
UPLOAD_FOLDER=uploads
DATABASE_PATH=data/receipts.db
```

## Testing

Run the integration test to verify all components work together:

```bash
python test_integration.py
```

## Requirements Met

This implementation satisfies all requirements from the specification:

- **Requirement 1.1-1.5**: Web interface with file upload and validation ✅
- **Requirement 2.4-2.5**: Integration with computer vision service ✅
- **Requirement 3.4-3.5**: Database integration and error handling ✅
- **Requirement 4.1-4.6**: Natural language query interface ✅

## Next Steps

The Streamlit web interface is now complete and ready for use. Users can:

1. Upload receipt images and see extracted data
2. Ask natural language questions about their receipts
3. View analytics and insights on the dashboard
4. Manage application settings and configuration

The interface provides a complete end-to-end experience for the Food Receipt Analyzer application.