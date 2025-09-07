#!/usr/bin/env python3
"""
Demo script for the custom vector database implementation.
Shows vector similarity search capabilities.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"

from services.vector_db import TextVectorizer, VectorMath, vector_db


def demo_vector_math():
    """Demonstrate basic vector operations."""
    print("🧮 Vector Math Demo")
    print("=" * 50)

    vec1 = [1.0, 2.0, 3.0]
    vec2 = [2.0, 4.0, 6.0]
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [-1.0, -2.0, -3.0]

    print(f"Vector 1: {vec1}")
    print(f"Vector 2: {vec2} (same direction)")
    print(f"Vector 3: {vec3} (orthogonal)")
    print(f"Vector 4: {vec4} (opposite direction)")
    print()

    sim_12 = VectorMath.cosine_similarity(vec1, vec2)
    sim_13 = VectorMath.cosine_similarity(vec1, vec3)
    sim_14 = VectorMath.cosine_similarity(vec1, vec4)

    print("Cosine Similarities:")
    print(f"  vec1 ↔ vec2 (same direction): {sim_12:.3f}")
    print(f"  vec1 ↔ vec3 (orthogonal): {sim_13:.3f}")
    print(f"  vec1 ↔ vec4 (opposite): {sim_14:.3f}")
    print()

    dist_12 = VectorMath.euclidean_distance(vec1, vec2)
    dist_13 = VectorMath.euclidean_distance(vec1, vec3)

    print("Euclidean Distances:")
    print(f"  vec1 ↔ vec2: {dist_12:.3f}")
    print(f"  vec1 ↔ vec3: {dist_13:.3f}")


def demo_text_vectorizer():
    """Demonstrate text vectorization."""
    print("\n📝 Text Vectorizer Demo")
    print("=" * 50)

    food_items = [
        "Chicken Burrito",
        "Kids Meal - Make Own",
        "Large Drink",
        "Domestic Beer",
        "Green Apple",
        "Red Apple",
        "Orange Juice",
        "Whole Milk",
        "Bread",
        "Banana",
    ]

    print("Sample food items:")
    for i, item in enumerate(food_items, 1):
        print(f"  {i}. {item}")
    print()

    vectorizer = TextVectorizer()
    vectors = vectorizer.fit_transform(food_items)

    print(f"Vocabulary size: {len(vectorizer.vocabulary)}")
    print(f"Sample vocabulary: {list(vectorizer.vocabulary.keys())[:10]}")
    print()

    print("Similarity Tests:")

    chicken_vec = vectorizer.transform("Chicken Burrito")
    kids_meal_vec = vectorizer.transform("Kids Meal")
    apple_green_vec = vectorizer.transform("Green Apple")
    apple_red_vec = vectorizer.transform("Red Apple")

    sim_chicken_kids = VectorMath.cosine_similarity(chicken_vec, kids_meal_vec)
    sim_apples = VectorMath.cosine_similarity(apple_green_vec, apple_red_vec)
    sim_chicken_apple = VectorMath.cosine_similarity(chicken_vec, apple_green_vec)

    print(f"  Chicken Burrito ↔ Kids Meal: {sim_chicken_kids:.3f}")
    print(f"  Green Apple ↔ Red Apple: {sim_apples:.3f}")
    print(f"  Chicken Burrito ↔ Green Apple: {sim_chicken_apple:.3f}")
    print()

    print("Query Matching:")
    query_vec = vectorizer.transform("apple fruit")

    for i, item in enumerate(food_items):
        item_vec = vectors[i]
        similarity = VectorMath.cosine_similarity(query_vec, item_vec)
        print(f"  '{item}': {similarity:.3f}")


def demo_vector_database():
    """Demonstrate the full vector database functionality."""
    print("\n🗄️ Vector Database Demo")
    print("=" * 50)

    print("Building vector index...")
    vector_db.build_index(force_rebuild=True)

    stats = vector_db.get_stats()
    print(f"\nDatabase Stats:")
    print(f"  Vectors stored: {stats['vector_count']}")
    print(f"  Vocabulary size: {stats['vocabulary_size']}")
    print(f"  Index fitted: {stats['is_fitted']}")
    print()

    test_queries = [
        "chicken food",
        "apple fruit",
        "drink beverage",
        "mexican food",
        "kids meal",
        "dairy milk",
    ]

    for query in test_queries:
        print(f"🔍 Search: '{query}'")
        results = vector_db.semantic_search(query, top_k=3)

        if results:
            for i, result in enumerate(results, 1):
                print(
                    f"  {i}. {result.item_name} (similarity: {result.similarity_score:.3f})"
                )
                print(f"     Store: {result.metadata.get('store_name', 'Unknown')}")
                print(f"     Price: ${result.metadata.get('price', 0):.2f}")
        else:
            print("  No results found")
        print()

    print("🔗 Finding Similar Items:")
    similar_results = vector_db.find_similar_items("Chicken Burrito", top_k=3)

    print("Items similar to 'Chicken Burrito':")
    for i, result in enumerate(similar_results, 1):
        print(f"  {i}. {result.item_name} (similarity: {result.similarity_score:.3f})")


def main():
    """Run all vector database demos."""
    demo_vector_math()
    demo_text_vectorizer()
    demo_vector_database()


if __name__ == "__main__":
    main()
