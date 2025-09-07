#!/usr/bin/env python3
"""
Debug script to test AI query processing step by step.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add Tesseract to PATH
tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"

from datetime import date, timedelta

from database.service import db_service
from services.ai_query import get_ai_query_service


def debug_query_processing():
    """Debug the AI query processing step by step."""
    print("🔍 AI Query Processing Debug")
    print("=" * 50)

    ai_service = get_ai_query_service()
    if not ai_service:
        print("❌ AI service not available")
        return

    query = "what food did I buy"
    print(f"Query: '{query}'")

    # Step 1: Parse the query
    print("\n1️⃣ Query Parsing:")
    parsed_query = ai_service.query_parser.parse_query(query)
    print(f"   Intent: {parsed_query['intent']}")
    print(f"   Parameters: {parsed_query['parameters']}")
    print(f"   Confidence: {parsed_query['confidence']}")

    # Step 2: Generate database results
    print("\n2️⃣ Database Query:")
    results = ai_service.sql_generator.generate_query_results(parsed_query)
    print(f"   Results count: {len(results)}")

    if results:
        for i, result in enumerate(results[:3]):  # Show first 3
            print(f"   Result {i+1}: {result}")
    else:
        print("   No results found")

        # Debug: Let's try to get items directly
        print("\n🔧 Direct Database Check:")

        # Try different approaches
        print("   Trying get_all_receipts():")
        receipts = db_service.get_all_receipts()
        total_items = 0
        for receipt in receipts:
            total_items += len(receipt.items)
            if receipt.items:
                print(f"     Receipt {receipt.id}: {len(receipt.items)} items")
                for item in receipt.items[:2]:  # Show first 2 items
                    print(f"       - {item.item_name}")

        print(f"   Total items across all receipts: {total_items}")

        # Try date range queries
        print("\n   Trying date range queries:")
        today = date.today()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        last_year = today - timedelta(days=365)

        for period, start_date in [
            ("last week", last_week),
            ("last month", last_month),
            ("last year", last_year),
        ]:
            receipts_in_period = db_service.get_receipts_by_date_range(
                start_date, today
            )
            items_in_period = sum(len(r.items) for r in receipts_in_period)
            print(
                f"     {period}: {len(receipts_in_period)} receipts, {items_in_period} items"
            )


def test_specific_queries():
    """Test specific query formats."""
    print("\n🎯 Testing Specific Query Formats")
    print("=" * 50)

    ai_service = get_ai_query_service()

    test_queries = [
        "show me all items from last year",
        "what did I buy in 2018",
        "list items from December 2018",
        "show me food from last 365 days",
        "what food did I buy from Burrito Bar",
    ]

    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            result = ai_service.process_query(query)
            parsed = result["parsed_query"]
            print(f"   Intent: {parsed['intent']}")
            print(f"   Parameters: {parsed['parameters']}")
            print(f"   Results: {len(result['results'])}")

            if result["results"]:
                print(f"   Sample result: {result['results'][0]}")

        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """Run AI query debugging."""
    debug_query_processing()
    test_specific_queries()


if __name__ == "__main__":
    main()
