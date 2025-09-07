#!/usr/bin/env python3
"""
Test vector database integration in Streamlit interface.
"""

import os
import sys

tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"

from services.ai_query import get_ai_query_service
from services.vector_db import vector_db


def test_streamlit_integration():
    """Test that vector search works through the AI query system."""
    print("🔍 Testing Streamlit Vector Integration")
    print("=" * 50)

    vector_db.build_index(force_rebuild=True)

    ai_service = get_ai_query_service()

    streamlit_queries = [
        "find chicken food",
        "search for apple",
        "similar to burrito",
        "mexican food",
        "dairy products",
        "what food did I buy",
    ]

    print("Testing queries as they would work in Streamlit:")

    for query in streamlit_queries:
        print(f"\n💬 User types: '{query}'")

        result = ai_service.process_query(query)

        print(f"🎯 Intent detected: {result['parsed_query']['intent']}")
        print(f"📊 Results found: {len(result['results'])}")
        print(f"🤖 Response: {result['formatted_response'][:100]}...")

        if result["parsed_query"]["intent"] == "semantic_search":
            print("   ✅ Using VECTOR SEARCH")
            if result["results"]:
                top_result = result["results"][0]
                if "similarity_score" in top_result:
                    print(f"   🎯 Top similarity: {top_result['similarity_score']:.1%}")
        else:
            print("   📋 Using traditional SQL search")


if __name__ == "__main__":
    test_streamlit_integration()
