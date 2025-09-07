#!/usr/bin/env python3
"""
Demo script for AI Query Service functionality.
Tests natural language query processing without requiring API keys.
"""

import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import Mock

from models.receipt import Receipt, ReceiptItem
from services.ai_query import QueryParser, ResponseFormatter, SQLQueryGenerator


def create_sample_data():
    """Create sample receipt data for testing."""
    items1 = [
        ReceiptItem("Pizza", 1, Decimal("12.99"), Decimal("12.99"), id=1, receipt_id=1),
        ReceiptItem("Soda", 2, Decimal("1.50"), Decimal("3.00"), id=2, receipt_id=1),
    ]

    items2 = [
        ReceiptItem(
            "Hamburger", 1, Decimal("8.99"), Decimal("8.99"), id=3, receipt_id=2
        ),
        ReceiptItem("Fries", 1, Decimal("3.50"), Decimal("3.50"), id=4, receipt_id=2),
    ]

    receipt1 = Receipt(
        id=1,
        store_name="Pizza Palace",
        receipt_date=date.today() - timedelta(days=1),
        total_amount=Decimal("15.99"),
        upload_timestamp=datetime.now(),
        raw_text="",
        image_path="",
        items=items1,
    )

    receipt2 = Receipt(
        id=2,
        store_name="Burger King",
        receipt_date=date.today() - timedelta(days=3),
        total_amount=Decimal("12.49"),
        upload_timestamp=datetime.now(),
        raw_text="",
        image_path="",
        items=items2,
    )

    return [receipt1, receipt2]


def create_mock_db_service(receipts):
    """Create a mock database service with sample data."""
    mock_db = Mock()

    def get_receipts_by_date_range(start_date, end_date):
        return [r for r in receipts if start_date <= r.receipt_date <= end_date]

    def get_total_spending_by_date(target_date):
        total = sum(r.total_amount for r in receipts if r.receipt_date == target_date)
        return total

    def get_stores_with_item(item_name, days_back=None):
        stores = set()
        cutoff_date = (
            date.today() - timedelta(days=days_back) if days_back else date.min
        )

        for receipt in receipts:
            if receipt.receipt_date >= cutoff_date:
                for item in receipt.items:
                    if item_name.lower() in item.item_name.lower():
                        stores.add(receipt.store_name)

        return list(stores)

    mock_db.get_receipts_by_date_range = get_receipts_by_date_range
    mock_db.get_total_spending_by_date = get_total_spending_by_date
    mock_db.get_stores_with_item = get_stores_with_item

    return mock_db


def create_mock_openrouter_client():
    """Create a mock OpenRouter client for testing."""
    mock_client = Mock()

    def chat_completion(messages, max_tokens=1000, temperature=0.1):
        return {
            "choices": [
                {
                    "message": {
                        "content": "Here's a formatted response based on your query results."
                    }
                }
            ]
        }

    mock_client.chat_completion = chat_completion
    return mock_client


def test_query_parsing():
    """Test natural language query parsing."""
    print("=== Testing Query Parsing ===")

    parser = QueryParser()

    test_queries = [
        "What food did I buy yesterday?",
        "Give me total expenses for food on 20 June",
        "Where did I buy hamburger from last 7 days?",
        "Show me all items I bought this week",
        "How much did I spend last 30 days?",
    ]

    for query in test_queries:
        result = parser.parse_query(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result['intent']}")
        print(f"Parameters: {result['parameters']}")
        print(f"Confidence: {result['confidence']}")


def test_sql_generation():
    """Test SQL query generation and execution."""
    print("\n=== Testing SQL Generation ===")

    receipts = create_sample_data()
    mock_db = create_mock_db_service(receipts)

    sql_generator = SQLQueryGenerator(mock_db)
    parser = QueryParser()

    test_queries = [
        "What food did I buy yesterday?",
        "How much did I spend yesterday?",
        "Where did I buy hamburger from last 7 days?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        parsed = parser.parse_query(query)
        results = sql_generator.generate_query_results(parsed)
        print(f"Results count: {len(results)}")
        if results:
            print(f"Sample result: {results[0]}")


def test_response_formatting():
    """Test response formatting."""
    print("\n=== Testing Response Formatting ===")

    receipts = create_sample_data()
    mock_db = create_mock_db_service(receipts)
    mock_client = create_mock_openrouter_client()

    sql_generator = SQLQueryGenerator(mock_db)
    formatter = ResponseFormatter(mock_client)
    parser = QueryParser()

    test_queries = [
        "What food did I buy yesterday?",
        "How much did I spend yesterday?",
        "Where did I buy hamburger from last 7 days?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        parsed = parser.parse_query(query)
        results = sql_generator.generate_query_results(parsed)
        formatted = formatter.format_response(query, results, parsed)
        print(f"Response: {formatted}")


def test_end_to_end():
    """Test complete end-to-end query processing."""
    print("\n=== Testing End-to-End Processing ===")

    receipts = create_sample_data()
    mock_db = create_mock_db_service(receipts)
    mock_client = create_mock_openrouter_client()

    parser = QueryParser()
    sql_generator = SQLQueryGenerator(mock_db)
    formatter = ResponseFormatter(mock_client)

    test_queries = [
        "What food did I buy yesterday?",
        "Give me total expenses for food yesterday",
        "Where did I buy pizza from last 7 days?",
    ]

    for query in test_queries:
        print(f"\n--- Processing: {query} ---")

        parsed = parser.parse_query(query)
        print(f"Parsed intent: {parsed['intent']}")

        results = sql_generator.generate_query_results(parsed)
        print(f"Found {len(results)} results")

        formatted = formatter.format_response(query, results, parsed)
        print(f"Response: {formatted}")


def main():
    """Run all demo tests."""
    print("Food Receipt Analyzer - AI Query Service Demo")
    print("=" * 50)

    try:
        test_query_parsing()
        test_sql_generation()
        test_response_formatting()
        test_end_to_end()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nThe AI Query Service is ready to process natural language queries.")
        print("To use with real data, ensure you have:")
        print("1. OPENROUTER_API_KEY set in your .env file")
        print("2. Receipt data in your database")
        print("3. The Streamlit app running")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
