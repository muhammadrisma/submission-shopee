#!/usr/bin/env python3
"""
Debug script to see what text is actually extracted from the real receipt image.
"""

import os
import sys

tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"
        print(f"📍 Added Tesseract to PATH: {tesseract_path}")

from services.computer_vision import ComputerVisionService


def debug_real_receipt():
    """Debug the actual receipt processing."""
    receipt_path = "receipt_example/burrito_receipt.jpg"

    if not os.path.exists(receipt_path):
        print(f"❌ Receipt file not found: {receipt_path}")
        print("Please make sure the file exists.")
        return

    print("🔍 Processing Real Receipt Image")
    print("=" * 50)
    print(f"File: {receipt_path}")

    try:
        cv_service = ComputerVisionService()
        result = cv_service.process_receipt(receipt_path)

        print("\n📝 Raw Extracted Text:")
        print("-" * 30)
        print(repr(result["raw_text"]))
        print("-" * 30)
        print(result["raw_text"])

        print(f"\n🏪 Store: {result['store_name']}")
        print(f"📅 Date: {result['receipt_date']}")
        print(f"💰 Total: ${result['total_amount']:.2f}")
        print(f"📦 Items: {len(result['items'])}")

        if result["items"]:
            for i, item in enumerate(result["items"], 1):
                print(f"  {i}. {item['item_name']} - ${item['total_price']:.2f}")
        else:
            print("  No items extracted")

        print(f"\n🔍 Line-by-Line Analysis:")
        print("-" * 30)
        lines = result["raw_text"].split("\n")
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                print(f"Line {i:2d}: '{line}'")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    debug_real_receipt()
