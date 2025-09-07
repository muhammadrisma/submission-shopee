#!/usr/bin/env python3
"""
Test the integration of vector database with AI query system.
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
from services.vector_db import vector_db


def test_vector_ai_integration():
    """Test the complete vector + AI integration."""
    print("🤖🔍 Vector AI Integration Test")
    print("=" * 60)

    # Initialize AI service
    ai_service = get_ai_query_service()
    if not ai_service:
        print("❌ AI service not available")
        return

    # Build vector index
    print("Building vector index...")
    vector_db.build_index(force_rebuild=True)

    # Test various query types
    test_queries = [
        # Traditional queries
        "what food did I buy",
        "what did I buy in 2018",
        # Semantic search queries
        "find chicken food",
        "search for apple fruit",
        "look for drinks",
        "similar to burrito",
        "mexican food",
        "dairy products",
        "beverages",
        "meat items",
        # Mixed queries
        "find items like apple",
        "search for food similar to chicken",
        "show me drinks I bought",
    ]

    for query in test_queries:
        print(f"\n💬 Query: '{query}'")
        try:
            result = ai_service.process_query(query)

            print(f"🎯 Intent: {result['parsed_query']['intent']}")
            print(f"📊 Results: {len(result['results'])}")
            print(f"🤖 Response: {result['formatted_response'][:150]}...")

            # Show similarity scores for semantic searches
            if (
                result["parsed_query"]["intent"] == "semantic_search"
                and result["results"]
            ):
                print("   Similarity scores:")
                for i, res in enumerate(result["results"][:3]):
                    if "similarity_score" in res:
                        print(
                            f"     {i+1}. {res['item_name']}: {res['similarity_score']:.3f}"
                        )

        except Exception as e:
            print(f"❌ Error: {e}")


def test_semantic_search_accuracy():
    """Test the accuracy of semantic search."""
    print("\n🎯 Semantic Search Accuracy Test")
    print("=" * 60)

    # Test cases with expected results
    test_cases = [
        {
            "query": "chicken",
            "expected_items": ["Chicken Burrito"],
            "description": "Should find chicken-based items",
        },
        {
            "query": "apple",
            "expected_items": ["Green Apple", "Red Apple"],
            "description": "Should find apple varieties",
        },
        {
            "query": "drink",
            "expected_items": ["Large Drink", "Orange Juice"],
            "description": "Should find beverages",
        },
        {
            "query": "mexican",
            "expected_items": ["Chicken Burrito"],
            "description": "Should find Mexican food items",
        },
    ]

    for test_case in test_cases:
        print(f"\n🔍 Testing: '{test_case['query']}'")
        print(f"   Expected: {test_case['expected_items']}")
        print(f"   Goal: {test_case['description']}")

        # Perform semantic search
        results = vector_db.semantic_search(test_case["query"], top_k=5)

        if results:
            print("   Found:")
            found_items = []
            for i, result in enumerate(results):
                print(
                    f"     {i+1}. {result.item_name} (similarity: {result.similarity_score:.3f})"
                )
                found_items.append(result.item_name)

            # Check accuracy
            expected_found = sum(
                1 for item in test_case["expected_items"] if item in found_items
            )
            accuracy = (
                expected_found / len(test_case["expected_items"])
                if test_case["expected_items"]
                else 0
            )
            print(
                f"   ✅ Accuracy: {accuracy:.1%} ({expected_found}/{len(test_case['expected_items'])} expected items found)"
            )
        else:
            print("   ❌ No results found")


def test_vector_database_performance():
    """Test vector database performance."""
    print("\n⚡ Vector Database Performance Test")
    print("=" * 60)

    import time

    # Test search performance
    queries = ["chicken", "apple", "drink", "food", "mexican"]

    total_time = 0
    total_queries = 0

    for query in queries:
        start_time = time.time()
        results = vector_db.semantic_search(query, top_k=10)
        end_time = time.time()

        query_time = end_time - start_time
        total_time += query_time
        total_queries += 1

        print(f"Query '{query}': {query_time:.4f}s ({len(results)} results)")

    avg_time = total_time / total_queries if total_queries > 0 else 0
    print(f"\nAverage query time: {avg_time:.4f}s")
    if avg_time > 0:
        print(f"Queries per second: {1/avg_time:.1f}")
    else:
        print("Queries per second: Very fast (< 0.0001s per query)")

    # Test index building performance
    print("\nIndex building performance:")
    start_time = time.time()
    vector_db.build_index(force_rebuild=True)
    build_time = time.time() - start_time

    stats = vector_db.get_stats()
    print(f"Index build time: {build_time:.4f}s")
    print(f"Vectors indexed: {stats['vector_count']}")
    print(f"Vectors per second: {stats['vector_count']/build_time:.1f}")


def main():
    """Run all vector AI integration tests."""
    test_vector_ai_integration()
    test_semantic_search_accuracy()
    test_vector_database_performance()


if __name__ == "__main__":
    main()
