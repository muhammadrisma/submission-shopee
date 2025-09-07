#!/usr/bin/env python3
"""
Test the complete flow: receipt processing + AI queries.
"""

import os
import sys

# Add Tesseract to PATH
tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"

from services.ai_query import get_ai_query_service

def test_user_queries():
    """Test queries that a user would typically ask."""
    print("🤖 Testing User Queries")
    print("=" * 50)
    
    ai_service = get_ai_query_service()
    if not ai_service:
        print("❌ AI service not available")
        return
    
    user_queries = [
        "what food i already buy",
        "what food did I buy",
        "show me all my food purchases",
        "what did I buy from Burrito Bar",
        "what did I buy in 2018",
        "show me items from December 2018",
        "how much did I spend on food",
        "what stores did I shop at"
    ]
    
    for query in user_queries:
        print(f"\n💬 User: '{query}'")
        try:
            result = ai_service.process_query(query)
            print(f"🤖 Bot: {result['formatted_response']}")
            print(f"   📊 Found {len(result['results'])} results")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Test the complete flow."""
    test_user_queries()

if __name__ == "__main__":
    main()