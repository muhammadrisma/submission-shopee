#!/usr/bin/env python3
"""
Demo script for Computer Vision Service

This script demonstrates the computer vision service functionality
with sample receipt text (simulating OCR output).
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from datetime import date

from services.computer_vision import ComputerVisionService, ReceiptParser


def demo_receipt_parser():
    """Demonstrate receipt parsing with sample OCR text."""
    print("=== Computer Vision Service Demo ===\n")

    # Sample OCR text that might come from a real receipt
    sample_ocr_text = """WAL*MART SUPERCENTER
Store #2345 Manager JOHN DOE
123 MAIN ST ANYTOWN ST 12345
ST# 2345 OP# 00001234 TE# 12 TR# 5678

GREAT VALUE MILK 1GAL    3.48
BANANAS                  2.18 F
WHITE BREAD              1.98
EGGS LARGE 12CT          2.78

SUBTOTAL                10.42
TAX                      0.83
TOTAL                   11.25

CASH                    15.00
CHANGE                   3.75

12/25/2023 14:32:15"""

    print("Sample OCR Text:")
    print("-" * 50)
    print(sample_ocr_text)
    print("-" * 50)
    print()

    # Parse the receipt
    parser = ReceiptParser()
    result = parser.parse_receipt(sample_ocr_text)

    print("Parsed Receipt Data:")
    print("-" * 50)
    print(f"Store Name: {result['store_name']}")
    print(f"Date: {result['receipt_date']}")
    print(f"Total Amount: ${result['total_amount']:.2f}")
    print(f"Number of Items: {len(result['items'])}")
    print()

    print("Items:")
    for i, item in enumerate(result["items"], 1):
        print(f"  {i}. {item['item_name']}")
        print(f"     Quantity: {item['quantity']}")
        print(f"     Unit Price: ${item['unit_price']:.2f}")
        print(f"     Total Price: ${item['total_price']:.2f}")
        print()

    print("Raw JSON Output:")
    print("-" * 50)
    # Convert date to string for JSON serialization
    result_copy = result.copy()
    result_copy["receipt_date"] = result_copy["receipt_date"].isoformat()
    if "processing_timestamp" in result_copy:
        result_copy["processing_timestamp"] = result_copy[
            "processing_timestamp"
        ].isoformat()

    print(json.dumps(result_copy, indent=2))


def demo_different_receipt_formats():
    """Demonstrate parsing different receipt formats."""
    print("\n\n=== Testing Different Receipt Formats ===\n")

    test_receipts = [
        {
            "name": "Target Receipt",
            "text": """TARGET
Store T-1234
123 Shopping Blvd
City, ST 12345

Coca Cola 12pk       5.99
Chips Ahoy Cookies   3.49
Tide Detergent      12.99

Subtotal            22.47
Tax                  1.80
Total              $24.27

01/15/2024 16:45""",
        },
        {
            "name": "Grocery Store Receipt",
            "text": """FRESH MARKET
Local Grocery Store
456 Main Street

2 Apples             1.98
Whole Milk Gallon    4.29
Sourdough Bread      2.99
3 Bananas            2.47

Total: $11.73
Date: 02/20/2024""",
        },
    ]

    parser = ReceiptParser()

    for receipt in test_receipts:
        print(f"Testing: {receipt['name']}")
        print("-" * 30)

        result = parser.parse_receipt(receipt["text"])

        print(f"Store: {result['store_name']}")
        print(f"Date: {result['receipt_date']}")
        print(f"Total: ${result['total_amount']:.2f}")
        print(f"Items found: {len(result['items'])}")

        for item in result["items"]:
            print(f"  - {item['item_name']}: ${item['total_price']:.2f}")

        print()


if __name__ == "__main__":
    demo_receipt_parser()
    demo_different_receipt_formats()

    print("\n=== Demo Complete ===")
    print("The computer vision service is ready for integration!")
    print("Next steps:")
    print("1. Integrate with Streamlit UI for file uploads")
    print("2. Add real image processing with actual receipt photos")
    print("3. Connect to database service for data storage")
