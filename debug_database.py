#!/usr/bin/env python3
"""
Debug script to check what's in the database and test queries.
"""

import os
import sys

# Add Tesseract to PATH
tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"

from database.service import db_service
from services.ai_query import get_ai_query_service

def check_database_contents():
    """Check what's currently in the database."""
    print("🗄️ Database Contents")
    print("=" * 50)
    
    try:
        # Get database stats
        stats = db_service.get_database_stats()
        print(f"📊 Database Statistics:")
        print(f"   Receipts: {stats['receipt_count']}")
        print(f"   Items: {stats['item_count']}")
        print(f"   Total Spending: ${stats['total_spending']:.2f}")
        
        if stats['date_range']['earliest']:
            print(f"   Date Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        # Get all receipts
        receipts = db_service.get_all_receipts()
        print(f"\n📋 All Receipts ({len(receipts)}):")
        
        for i, receipt in enumerate(receipts, 1):
            print(f"\n{i}. Receipt ID: {receipt.id}")
            print(f"   Store: {receipt.store_name}")
            print(f"   Date: {receipt.receipt_date}")
            print(f"   Total: ${receipt.total_amount:.2f}")
            print(f"   Items: {len(receipt.items)}")
            
            for j, item in enumerate(receipt.items, 1):
                print(f"     {j}. {item.item_name} - ${item.total_price:.2f}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def test_ai_queries():
    """Test AI query functionality."""
    print("\n🤖 AI Query Testing")
    print("=" * 50)
    
    ai_service = get_ai_query_service()
    if not ai_service:
        print("❌ AI service not available")
        return
    
    test_queries = [
        "what food i already buy",
        "what food did I buy",
        "show me all items",
        "list all food items",
        "what did I purchase"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        try:
            result = ai_service.process_query(query)
            print(f"   Success: {result['success']}")
            print(f"   Intent: {result.get('parsed_query', {}).get('intent', 'unknown')}")
            print(f"   Results: {len(result.get('results', []))}")
            print(f"   Response: {result['formatted_response'][:100]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def add_test_receipt():
    """Add a test receipt to the database."""
    print("\n➕ Adding Test Receipt")
    print("=" * 50)
    
    try:
        from services.computer_vision import ComputerVisionService
        from models.receipt import Receipt, ReceiptItem
        from datetime import date
        from decimal import Decimal
        
        # Process the actual receipt
        receipt_path = "receipt_example/burrito_receipt.jpg"
        if os.path.exists(receipt_path):
            print(f"Processing: {receipt_path}")
            cv_service = ComputerVisionService()
            result = cv_service.process_receipt(receipt_path)
            
            # Create receipt object
            items = []
            for item_data in result['items']:
                item = ReceiptItem(
                    item_name=item_data['item_name'],
                    quantity=item_data['quantity'],
                    unit_price=Decimal(str(item_data['unit_price'])),
                    total_price=Decimal(str(item_data['total_price']))
                )
                items.append(item)
            
            receipt = Receipt(
                store_name=result['store_name'],
                receipt_date=result['receipt_date'],
                total_amount=Decimal(str(result['total_amount'])),
                raw_text=result['raw_text'],
                image_path=receipt_path,
                items=items
            )
            
            # Save to database
            receipt_id = db_service.save_receipt(receipt)
            print(f"✅ Saved receipt with ID: {receipt_id}")
            print(f"   Store: {receipt.store_name}")
            print(f"   Items: {len(receipt.items)}")
            
        else:
            print(f"❌ Receipt file not found: {receipt_path}")
            
    except Exception as e:
        print(f"❌ Error adding test receipt: {e}")

def main():
    """Run all database debugging."""
    check_database_contents()
    
    # If database is empty, add a test receipt
    stats = db_service.get_database_stats()
    if stats['receipt_count'] == 0:
        add_test_receipt()
        print("\n" + "="*50)
        check_database_contents()
    
    test_ai_queries()

if __name__ == "__main__":
    main()