#!/usr/bin/env python3
"""
Demonstration script for the Food Receipt Analyzer database functionality.
Shows how to use the data models and database service.
"""

from datetime import date, datetime
from decimal import Decimal

from models.receipt import Receipt, ReceiptItem
from database.connection import initialize_database
from database.service import db_service


def main():
    """Demonstrate database functionality."""
    print("=== Food Receipt Analyzer Database Demo ===\n")
    
    # Initialize database
    print("1. Initializing database...")
    initialize_database()
    print("   ✓ Database initialized with schema\n")
    
    # Create sample receipt items
    print("2. Creating sample receipt items...")
    items = [
        ReceiptItem("Red Apple", 3, Decimal("1.25"), Decimal("3.75")),
        ReceiptItem("Banana", 6, Decimal("0.50"), Decimal("3.00")),
        ReceiptItem("Whole Milk", 1, Decimal("3.99"), Decimal("3.99")),
        ReceiptItem("Bread", 1, Decimal("2.49"), Decimal("2.49"))
    ]
    
    for item in items:
        print(f"   - {item.item_name}: {item.quantity} x ${item.unit_price} = ${item.total_price}")
    print()
    
    # Create sample receipt
    print("3. Creating sample receipt...")
    receipt = Receipt(
        store_name="Fresh Market",
        receipt_date=date(2024, 1, 15),
        total_amount=Decimal("13.23"),
        items=items,
        raw_text="Fresh Market Receipt - Thank you for shopping!",
        image_path="/uploads/receipt_001.jpg"
    )
    
    print(f"   Store: {receipt.store_name}")
    print(f"   Date: {receipt.receipt_date}")
    print(f"   Total: ${receipt.total_amount}")
    print(f"   Items: {len(receipt.items)}")
    print(f"   Total consistency: {receipt.validate_total_consistency()}\n")
    
    # Save receipt to database
    print("4. Saving receipt to database...")
    receipt_id = db_service.save_receipt(receipt)
    print(f"   ✓ Receipt saved with ID: {receipt_id}\n")
    
    # Retrieve receipt from database
    print("5. Retrieving receipt from database...")
    retrieved_receipt = db_service.get_receipt_by_id(receipt_id)
    print(f"   ✓ Retrieved receipt: {retrieved_receipt.store_name}")
    print(f"   Items retrieved: {len(retrieved_receipt.items)}")
    print(f"   First item: {retrieved_receipt.items[0].item_name}\n")
    
    # Search for items
    print("6. Searching for items...")
    apple_results = db_service.search_items_by_name("Apple")
    print(f"   Found {len(apple_results)} items matching 'Apple':")
    for result in apple_results:
        print(f"   - {result['item_name']} at {result['store_name']} on {result['receipt_date']}")
    print()
    
    # Get total spending
    print("7. Getting total spending for date...")
    total_spending = db_service.get_total_spending_by_date(date(2024, 1, 15))
    print(f"   Total spending on 2024-01-15: ${total_spending}\n")
    
    # Get stores that sell specific items
    print("8. Finding stores that sell milk...")
    milk_stores = db_service.get_stores_with_item("Milk")
    print(f"   Stores selling milk: {milk_stores}\n")
    
    # Get database statistics
    print("9. Database statistics...")
    stats = db_service.get_database_stats()
    print(f"   Total receipts: {stats['receipt_count']}")
    print(f"   Total items: {stats['item_count']}")
    print(f"   Total spending: ${stats['total_spending']}")
    print(f"   Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}\n")
    
    # Create another receipt for demonstration
    print("10. Adding another receipt...")
    receipt2 = Receipt(
        store_name="Corner Store",
        receipt_date=date(2024, 1, 16),
        total_amount=Decimal("8.50"),
        items=[
            ReceiptItem("Green Apple", 2, Decimal("1.50"), Decimal("3.00")),
            ReceiptItem("Orange Juice", 1, Decimal("5.50"), Decimal("5.50"))
        ]
    )
    
    receipt2_id = db_service.save_receipt(receipt2)
    print(f"   ✓ Second receipt saved with ID: {receipt2_id}\n")
    
    # Search across multiple receipts
    print("11. Searching across all receipts...")
    all_apples = db_service.search_items_by_name("Apple")
    print(f"   Found {len(all_apples)} apple items across all receipts:")
    for result in all_apples:
        print(f"   - {result['item_name']} at {result['store_name']} (${result['total_price']})")
    print()
    
    # Get receipts by date range
    print("12. Getting receipts by date range...")
    receipts_in_range = db_service.get_receipts_by_date_range(
        date(2024, 1, 14), date(2024, 1, 17)
    )
    print(f"   Found {len(receipts_in_range)} receipts in date range:")
    for r in receipts_in_range:
        print(f"   - {r.store_name} on {r.receipt_date}: ${r.total_amount}")
    print()
    
    print("=== Demo completed successfully! ===")


if __name__ == "__main__":
    main()