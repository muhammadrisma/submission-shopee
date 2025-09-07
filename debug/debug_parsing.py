#!/usr/bin/env python3
"""
Debug script to test receipt parsing with sample text.
"""

import re

from services.computer_vision import ReceiptParser

# Sample text from your receipt
sample_text = """🧾 Receipt Details
Store: Burrito Bar – Authentic Mexican Joint
Address: 900 Kirkwood Ave, West Hollywood, CA
Date: 12/14/2018
Time: 11:43 AM
Host: Maura
Order #: 391

🍽️ Items Purchased
Chicken Burrito — $8.79
Kids Meal (Make Own) — $4.99
Large Drink — $2.19
Domestic Beer — $4.99

💵 Totals
Subtotal: $20.96
Tax: $1.15
Total (Balance Due): $22.11

💳 Payment
Paid with VISA 4932 (masked number)"""


def debug_item_extraction():
    """Debug the item extraction process."""
    parser = ReceiptParser()

    print("🔍 Debugging Item Extraction")
    print("=" * 50)

    lines = sample_text.split("\n")
    print(f"Total lines: {len(lines)}")
    print()

    # Test each pattern
    for i, pattern in enumerate(parser.item_patterns):
        print(f"Pattern {i+1}: {pattern}")
        matches = []

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            match = re.search(pattern, line)
            if match:
                matches.append((line_num + 1, line, match.groups()))

        if matches:
            print(f"  ✅ Found {len(matches)} matches:")
            for line_num, line, groups in matches:
                print(f"    Line {line_num}: '{line}' -> {groups}")
        else:
            print(f"  ❌ No matches")
        print()

    # Test the actual parsing
    print("🧾 Full Parsing Result:")
    print("=" * 50)

    result = parser.parse_receipt(sample_text)

    print(f"Store: {result['store_name']}")
    print(f"Date: {result['receipt_date']}")
    print(f"Total: ${result['total_amount']:.2f}")
    print(f"Items found: {len(result['items'])}")

    for i, item in enumerate(result["items"], 1):
        print(f"  {i}. {item['item_name']} - ${item['total_price']:.2f}")


def test_individual_patterns():
    """Test individual patterns on specific lines."""
    print("\n🎯 Testing Individual Lines")
    print("=" * 50)

    test_lines = [
        "Chicken Burrito — $8.79",
        "Kids Meal (Make Own) — $4.99",
        "Large Drink — $2.19",
        "Domestic Beer — $4.99",
    ]

    patterns = [
        r"([A-Za-z][A-Za-z\s\(\)]+?)\s*[—–-]\s*\$(\d+\.\d{2})",
        r"([A-Za-z][A-Za-z\s\(\)]+?)\s+\$(\d+\.\d{2})",
        r"(\d+)\s+([A-Za-z][A-Za-z\s\(\)]+?)\s+\$(\d+\.\d{2})",
        r"([A-Za-z][A-Za-z\s\(\)]+?)\s+(\d+\.\d{2})",
        r"(\d+)\s+([A-Za-z][A-Za-z\s\(\)]+?)\s+(\d+\.\d{2})",
    ]

    for line in test_lines:
        print(f"\nTesting: '{line}'")
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, line)
            if match:
                print(f"  ✅ Pattern {i+1}: {match.groups()}")
            else:
                print(f"  ❌ Pattern {i+1}: No match")


if __name__ == "__main__":
    debug_item_extraction()
    test_individual_patterns()
