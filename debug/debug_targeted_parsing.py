#!/usr/bin/env python3
"""
Debug script with targeted parsing for the specific receipt format.
"""

import os
import re
from decimal import Decimal

# Add Tesseract to PATH
tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"


def targeted_item_extraction(text):
    """Extract items using a targeted approach for this specific receipt format."""

    # The actual text we're working with
    print("Raw text:")
    print(repr(text))
    print()

    # Look for the specific pattern in this receipt
    # The items appear to be: CHICKENBURRITO $8.79 KIDSMEAL-MAKEOWN $4.99 LARGEDRINK $2.19 DOMESTICBEER $4.99

    # More targeted patterns
    patterns = [
        # Look for the exact sequence we see in the OCR
        r"CHICKENBURRITO\s+\$(\d+\.\d{2})",
        r"KIDSMEAL-MAKEOWN\s+\$(\d+\.\d{2})",
        r"LARGEDRINK\s+\$(\d+\.\d{2})",
        r"DOMESTICBEER\s+\$(\d+\.\d{2})",
    ]

    item_names = [
        "Chicken Burrito",
        "Kids Meal - Make Own",
        "Large Drink",
        "Domestic Beer",
    ]

    items = []

    for i, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if match:
            price = float(match.group(1))
            items.append(
                {
                    "item_name": item_names[i],
                    "quantity": 1,
                    "unit_price": price,
                    "total_price": price,
                }
            )
            print(f"✅ Found: {item_names[i]} - ${price:.2f}")
        else:
            print(f"❌ Not found: {item_names[i]}")

    return items


def test_targeted_parsing():
    """Test the targeted parsing approach."""

    # Sample text from the actual OCR
    sample_text = "ear ron AUTHENTICMEXICANJOINT 908KIRKWOODAVE WESTHOLLYWOOD,CA HOST:MAURA 12/14/2018 ORDER:391 11:43AM CHICKENBURRITO $8.79 KIDSMEAL-MAKEOWN $4.99 LARGEDRINK $2.19 DOMESTICBEER $4.99 SUBTOTAL: $20.96 TAX: $1.15 VISA4932XXXXXKXXXX AUTHORIZE... BALANCEDUE $22.11 LIKEUSONFACEB800KTOGET SPECIALOFFERSBYEMAIL"

    print("🎯 Targeted Item Extraction")
    print("=" * 50)

    items = targeted_item_extraction(sample_text)

    print(f"\n📦 Found {len(items)} items:")
    total = 0
    for item in items:
        print(f"  • {item['item_name']} - ${item['total_price']:.2f}")
        total += item["total_price"]

    print(f"\n💰 Items total: ${total:.2f}")

    # Test total extraction
    total_pattern = r"BALANCEDUE\s+\$(\d+\.\d{2})"
    total_match = re.search(total_pattern, sample_text)
    if total_match:
        receipt_total = float(total_match.group(1))
        print(f"💰 Receipt total: ${receipt_total:.2f}")
        print(f"✅ Totals match: {abs(total - receipt_total) < 0.01}")


if __name__ == "__main__":
    test_targeted_parsing()
