# API Documentation - Food Receipt Analyzer

## Overview

This document provides comprehensive API documentation for the internal services of the Food Receipt Analyzer application.

## Table of Contents

1. [Computer Vision Service](#computer-vision-service)
2. [AI Query Service](#ai-query-service)
3. [Database Service](#database-service)
4. [Vector Database Service](#vector-database-service)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)

## Computer Vision Service

### `ComputerVisionService`

Handles OCR text extraction and receipt parsing from images.

#### Methods

##### `extract_text_from_image(image_path: str) -> Dict[str, Any]`

Extracts raw text from receipt images using OCR.

**Parameters:**
- `image_path` (str): Path to the receipt image file

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `success` (bool): Whether extraction was successful
  - `text` (str): Extracted raw text
  - `confidence` (float): OCR confidence score (0-100)
  - `error` (str, optional): Error message if extraction failed

**Example:**
```python
from services.computer_vision import ComputerVisionService

cv_service = ComputerVisionService()
result = cv_service.extract_text_from_image("receipt.jpg")

if result['success']:
    print(f"Extracted text: {result['text']}")
    print(f"Confidence: {result['confidence']}%")
else:
    print(f"Error: {result['error']}")
```

##### `parse_receipt_data(text: str) -> Dict[str, Any]`

Parses structured data from raw receipt text.

**Parameters:**
- `text` (str): Raw text extracted from receipt

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `success` (bool): Whether parsing was successful
  - `store_name` (str): Extracted store name
  - `date` (str): Receipt date in YYYY-MM-DD format
  - `total` (float): Total amount
  - `items` (List[Dict]): List of items with name, quantity, price
  - `error` (str, optional): Error message if parsing failed

**Example:**
```python
parsed_data = cv_service.parse_receipt_data(raw_text)

if parsed_data['success']:
    print(f"Store: {parsed_data['store_name']}")
    print(f"Date: {parsed_data['date']}")
    print(f"Total: ${parsed_data['total']}")
    for item in parsed_data['items']:
        print(f"- {item['name']}: ${item['price']}")
```

##### `process_receipt_image(image_path: str) -> Dict[str, Any]`

Complete receipt processing pipeline (extract + parse).

**Parameters:**
- `image_path` (str): Path to the receipt image file

**Returns:**
- `Dict[str, Any]`: Combined result from extraction and parsing

**Example:**
```python
result = cv_service.process_receipt_image("receipt.jpg")

if result['success']:
    receipt_data = result['parsed_data']
    print(f"Processed receipt from {receipt_data['store_name']}")
```

## AI Query Service

### `AIQueryService`

Handles natural language query processing and response generation.

#### Methods

##### `process_query(query: str, user_context: Dict = None) -> Dict[str, Any]`

Processes natural language queries and generates responses.

**Parameters:**
- `query` (str): User's natural language query
- `user_context` (Dict, optional): Additional context for query processing

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `success` (bool): Whether query processing was successful
  - `intent` (str): Detected query intent (search, analytics, etc.)
  - `parameters` (Dict): Extracted query parameters
  - `sql_query` (str): Generated SQL query
  - `results` (List): Query results from database
  - `formatted_response` (str): Natural language response
  - `error` (str, optional): Error message if processing failed

**Example:**
```python
from services.ai_query import AIQueryService

ai_service = AIQueryService()
result = ai_service.process_query("What food did I buy yesterday?")

if result['success']:
    print(f"Intent: {result['intent']}")
    print(f"Response: {result['formatted_response']}")
```

##### `parse_query_intent(query: str) -> Dict[str, Any]`

Extracts intent and parameters from natural language query.

**Parameters:**
- `query` (str): User's natural language query

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `intent` (str): Query intent (item_search, spending_analysis, store_query)
  - `parameters` (Dict): Extracted parameters (dates, items, stores, etc.)
  - `confidence` (float): Intent classification confidence

**Example:**
```python
intent_result = ai_service.parse_query_intent("How much did I spend on groceries last week?")
print(f"Intent: {intent_result['intent']}")
print(f"Parameters: {intent_result['parameters']}")
```

##### `generate_sql_query(intent: str, parameters: Dict) -> str`

Generates SQL query based on intent and parameters.

**Parameters:**
- `intent` (str): Query intent
- `parameters` (Dict): Query parameters

**Returns:**
- `str`: Generated SQL query

**Example:**
```python
sql_query = ai_service.generate_sql_query(
    intent="spending_analysis",
    parameters={"date_range": "last_week", "category": "groceries"}
)
print(f"Generated SQL: {sql_query}")
```

## Database Service

### `DatabaseService`

Handles all database operations for receipts and items.

#### Methods

##### `save_receipt(receipt_data: Dict) -> Dict[str, Any]`

Saves receipt data to the database.

**Parameters:**
- `receipt_data` (Dict): Receipt data dictionary

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `success` (bool): Whether save was successful
  - `receipt_id` (int): ID of saved receipt
  - `error` (str, optional): Error message if save failed

**Example:**
```python
from database.service import DatabaseService

db_service = DatabaseService()
result = db_service.save_receipt({
    'store_name': 'Grocery Store',
    'date': '2024-01-15',
    'total': 25.99,
    'items': [
        {'name': 'Milk', 'price': 3.99, 'quantity': 1},
        {'name': 'Bread', 'price': 2.50, 'quantity': 2}
    ]
})

if result['success']:
    print(f"Receipt saved with ID: {result['receipt_id']}")
```

##### `get_receipts(filters: Dict = None) -> List[Dict]`

Retrieves receipts from database with optional filtering.

**Parameters:**
- `filters` (Dict, optional): Filter criteria

**Returns:**
- `List[Dict]`: List of receipt dictionaries

**Example:**
```python
# Get all receipts
all_receipts = db_service.get_receipts()

# Get receipts from specific store
store_receipts = db_service.get_receipts({
    'store_name': 'Grocery Store'
})

# Get receipts from date range
recent_receipts = db_service.get_receipts({
    'date_from': '2024-01-01',
    'date_to': '2024-01-31'
})
```

##### `search_items(query: str, filters: Dict = None) -> List[Dict]`

Searches for items across all receipts.

**Parameters:**
- `query` (str): Search query for item names
- `filters` (Dict, optional): Additional filters

**Returns:**
- `List[Dict]`: List of matching items

**Example:**
```python
# Search for specific items
milk_items = db_service.search_items("milk")

# Search with date filter
recent_milk = db_service.search_items("milk", {
    'date_from': '2024-01-01'
})
```

##### `get_spending_analytics(date_range: str, group_by: str = None) -> Dict`

Generates spending analytics for specified date range.

**Parameters:**
- `date_range` (str): Date range specification
- `group_by` (str, optional): Grouping criteria (store, category, date)

**Returns:**
- `Dict`: Analytics data with totals, averages, and breakdowns

**Example:**
```python
# Get weekly spending analytics
weekly_stats = db_service.get_spending_analytics("last_week")

# Get monthly spending by store
monthly_by_store = db_service.get_spending_analytics(
    "last_month", 
    group_by="store"
)
```

## Vector Database Service

### `VectorDBService`

Handles semantic similarity search for food items.

#### Methods

##### `add_items_to_index(items: List[Dict]) -> bool`

Adds items to the vector search index.

**Parameters:**
- `items` (List[Dict]): List of item dictionaries

**Returns:**
- `bool`: Success status

**Example:**
```python
from services.vector_db import VectorDBService

vector_service = VectorDBService()
success = vector_service.add_items_to_index([
    {'name': 'Organic Milk', 'category': 'dairy'},
    {'name': 'Whole Wheat Bread', 'category': 'bakery'}
])
```

##### `search_similar_items(query: str, limit: int = 10) -> List[Dict]`

Finds items similar to the query using semantic search.

**Parameters:**
- `query` (str): Search query
- `limit` (int): Maximum number of results

**Returns:**
- `List[Dict]`: List of similar items with similarity scores

**Example:**
```python
similar_items = vector_service.search_similar_items("dairy products", limit=5)
for item in similar_items:
    print(f"{item['name']} (similarity: {item['score']:.2f})")
```

## Data Models

### Receipt Model

```python
@dataclass
class Receipt:
    id: Optional[int] = None
    store_name: str = ""
    receipt_date: Optional[date] = None
    total_amount: Decimal = Decimal('0.00')
    upload_timestamp: Optional[datetime] = None
    raw_text: Optional[str] = None
    image_path: Optional[str] = None
    items: List['ReceiptItem'] = field(default_factory=list)
```

### ReceiptItem Model

```python
@dataclass
class ReceiptItem:
    id: Optional[int] = None
    receipt_id: Optional[int] = None
    item_name: str = ""
    quantity: int = 1
    unit_price: Decimal = Decimal('0.00')
    total_price: Decimal = Decimal('0.00')
```

## Error Handling

All services implement consistent error handling patterns:

### Error Response Format

```python
{
    "success": False,
    "error": "Human-readable error message",
    "error_code": "ERROR_CODE",
    "technical_details": {
        "exception_type": "ValueError",
        "stack_trace": "...",
        "context": {...}
    }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `OCR_ERROR`: OCR processing failed
- `PARSING_ERROR`: Receipt parsing failed
- `DATABASE_ERROR`: Database operation failed
- `API_ERROR`: External API call failed
- `FILE_ERROR`: File operation failed

### Error Handling Example

```python
try:
    result = cv_service.process_receipt_image("receipt.jpg")
    if not result['success']:
        print(f"Processing failed: {result['error']}")
        if 'technical_details' in result:
            print(f"Technical details: {result['technical_details']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

### Environment Variables

All services respect these environment variables:

```bash
# API Configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-chat-v3.1:free

# Database Configuration
DATABASE_PATH=data/receipts.db

# OCR Configuration
TESSERACT_CMD=/path/to/tesseract

# File Processing
MAX_FILE_SIZE_MB=10
UPLOAD_FOLDER=uploads
```

### Service Initialization

```python
# Initialize services with custom configuration
from config import config

cv_service = ComputerVisionService(
    tesseract_cmd=config.TESSERACT_CMD
)

ai_service = AIQueryService(
    api_key=config.OPENROUTER_API_KEY,
    model=config.OPENROUTER_MODEL
)

db_service = DatabaseService(
    database_path=config.DATABASE_PATH
)
```

## Testing

### Unit Testing

Each service includes comprehensive unit tests:

```bash
# Test individual services
python -m pytest tests/test_computer_vision.py -v
python -m pytest tests/test_ai_query.py -v
python -m pytest tests/test_database.py -v

# Test with coverage
python -m pytest tests/ --cov=services --cov-report=html
```

### Integration Testing

```bash
# Test service interactions
python -m pytest tests/test_integration.py -v

# Test complete workflow
python -m pytest tests/test_complete_flow.py -v
```

### API Testing Examples

```python
# Test computer vision service
def test_cv_service():
    cv_service = ComputerVisionService()
    result = cv_service.process_receipt_image("test_receipt.jpg")
    assert result['success'] == True
    assert 'store_name' in result['parsed_data']

# Test AI query service
def test_ai_service():
    ai_service = AIQueryService()
    result = ai_service.process_query("What did I buy yesterday?")
    assert result['success'] == True
    assert result['intent'] in ['item_search', 'spending_analysis']
```

This API documentation provides comprehensive guidance for developers working with the Food Receipt Analyzer's internal services.