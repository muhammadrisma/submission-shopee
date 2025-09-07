#!/usr/bin/env python3
"""
Debug script to test total extraction.
"""

from services.computer_vision import ReceiptParser
import re

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

def debug_total_extraction():
    """Debug the total extraction process."""
    parser = ReceiptParser()
    
    print("💰 Debugging Total Extraction")
    print("=" * 50)
    
    # Test each total pattern
    for i, pattern in enumerate(parser.total_patterns):
        print(f"Pattern {i+1}: {pattern}")
        
        matches = re.findall(pattern, sample_text)
        if matches:
            print(f"  ✅ Found matches: {matches}")
        else:
            print(f"  ❌ No matches")
        print()
    
    # Test the actual total extraction
    print("🧾 Actual Total Extraction:")
    print("=" * 50)
    
    total = parser._extract_total(sample_text)
    print(f"Extracted total: ${total:.2f}")
    
    # Test specific lines
    print("\n🎯 Testing Specific Lines:")
    print("=" * 50)
    
    test_lines = [
        "Subtotal: $20.96",
        "Tax: $1.15", 
        "Total (Balance Due): $22.11"
    ]
    
    for line in test_lines:
        print(f"\nTesting: '{line}'")
        for i, pattern in enumerate(parser.total_patterns):
            match = re.search(pattern, line)
            if match:
                print(f"  ✅ Pattern {i+1}: ${match.group(1)}")

if __name__ == "__main__":
    debug_total_extraction()