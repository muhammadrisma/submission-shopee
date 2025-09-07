#!/usr/bin/env python3
"""
Complete system demonstration: Receipt processing + Vector DB + AI queries.
Shows the full pipeline from receipt upload to semantic search.
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
from database.service import db_service


def demo_complete_pipeline():
    """Demonstrate the complete food receipt analyzer pipeline."""
    print("🧾🤖 Complete Food Receipt Analyzer Demo")
    print("=" * 70)
    
    # 1. Show database contents
    print("1️⃣ Current Database Contents:")
    print("-" * 40)
    
    stats = db_service.get_database_stats()
    print(f"📊 Database: {stats['receipt_count']} receipts, {stats['item_count']} items")
    print(f"💰 Total spending: ${stats['total_spending']:.2f}")
    
    receipts = db_service.get_all_receipts(limit=3)
    for receipt in receipts:
        print(f"🧾 {receipt.store_name} ({receipt.receipt_date}): {len(receipt.items)} items, ${receipt.total_amount:.2f}")
    
    # 2. Build vector index
    print(f"\n2️⃣ Building Vector Search Index:")
    print("-" * 40)
    
    vector_db.build_index(force_rebuild=True)
    vector_stats = vector_db.get_stats()
    print(f"📚 Vector index: {vector_stats['vector_count']} vectors, {vector_stats['vocabulary_size']} vocabulary")
    
    # 3. Test AI query system
    print(f"\n3️⃣ AI Query System Demo:")
    print("-" * 40)
    
    ai_service = get_ai_query_service()
    
    # Traditional queries
    print("\n🔍 Traditional Queries:")
    traditional_queries = [
        "what food did I buy",
        "what did I buy in 2018",
        "how much did I spend on food"
    ]
    
    for query in traditional_queries:
        print(f"\n💬 '{query}'")
        result = ai_service.process_query(query)
        print(f"🤖 {result['formatted_response'][:100]}...")
    
    # Semantic search queries
    print(f"\n🔍 Semantic Search Queries:")
    semantic_queries = [
        "find chicken food",
        "search for apple fruit", 
        "look for mexican food",
        "similar to burrito",
        "dairy products"
    ]
    
    for query in semantic_queries:
        print(f"\n💬 '{query}'")
        result = ai_service.process_query(query)
        intent = result['parsed_query']['intent']
        results_count = len(result['results'])
        
        print(f"🎯 Intent: {intent} | Results: {results_count}")
        print(f"🤖 {result['formatted_response'][:120]}...")
        
        # Show similarity scores for semantic searches
        if intent == 'semantic_search' and result['results']:
            top_result = result['results'][0]
            if 'similarity_score' in top_result:
                print(f"   🎯 Top match: {top_result['item_name']} ({top_result['similarity_score']:.1%} similar)")
    
    # 4. Vector similarity demonstration
    print(f"\n4️⃣ Vector Similarity Demonstration:")
    print("-" * 40)
    
    similarity_tests = [
        ("chicken", "Should find chicken-based items"),
        ("apple", "Should find apple varieties"),
        ("drink", "Should find beverages"),
        ("mexican", "Should find Mexican cuisine")
    ]
    
    for search_term, description in similarity_tests:
        print(f"\n🔍 Searching for '{search_term}' - {description}")
        results = vector_db.semantic_search(search_term, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.item_name} ({result.similarity_score:.1%} similar)")
                print(f"     ${result.metadata.get('price', 0):.2f} from {result.metadata.get('store_name', 'Unknown')}")
        else:
            print("  No similar items found")
    
    # 5. System capabilities summary
    print(f"\n5️⃣ System Capabilities Summary:")
    print("-" * 40)
    
    capabilities = [
        "✅ Receipt image processing with OCR",
        "✅ Structured data extraction (items, prices, stores)",
        "✅ SQLite database storage",
        "✅ Custom vector database with TF-IDF",
        "✅ Cosine similarity search (implemented from scratch)",
        "✅ Natural language query understanding",
        "✅ Semantic search capabilities",
        "✅ AI-powered response generation",
        "✅ Streamlit web interface",
        "✅ Query history and analytics"
    ]
    
    for capability in capabilities:
        print(f"  {capability}")
    
    print(f"\n🎉 Complete Food Receipt Analyzer System Ready!")
    print("   - Upload receipts through Streamlit interface")
    print("   - Ask questions in natural language")
    print("   - Get semantic search results")
    print("   - View analytics and insights")


def demo_vector_math_concepts():
    """Demonstrate vector mathematics concepts."""
    print(f"\n📐 Vector Mathematics Concepts:")
    print("-" * 40)
    
    from services.vector_db import VectorMath, TextVectorizer
    
    # Show how text becomes vectors
    vectorizer = TextVectorizer()
    food_items = ["Chicken Burrito", "Apple Fruit", "Orange Juice"]
    vectors = vectorizer.fit_transform(food_items)
    
    print("Text → Vector conversion:")
    for i, (item, vector) in enumerate(zip(food_items, vectors)):
        non_zero = sum(1 for x in vector if x > 0)
        print(f"  '{item}' → {len(vector)}-dim vector ({non_zero} non-zero values)")
    
    print(f"\nVocabulary: {list(vectorizer.vocabulary.keys())}")
    
    # Show similarity calculations
    print(f"\nSimilarity calculations:")
    for i in range(len(food_items)):
        for j in range(i+1, len(food_items)):
            similarity = VectorMath.cosine_similarity(vectors[i], vectors[j])
            print(f"  '{food_items[i]}' ↔ '{food_items[j]}': {similarity:.3f}")


def main():
    """Run the complete system demonstration."""
    demo_complete_pipeline()
    demo_vector_math_concepts()


if __name__ == "__main__":
    main()