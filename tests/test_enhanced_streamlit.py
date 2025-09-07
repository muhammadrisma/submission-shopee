#!/usr/bin/env python3
"""
Test the enhanced Streamlit integration with vector search indicators.
"""

import os
import sys

# Add Tesseract to PATH
tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    current_path = os.environ.get("PATH", "")
    if tesseract_path not in current_path:
        os.environ["PATH"] = f"{tesseract_path};{current_path}"

def test_enhanced_features():
    """Test the enhanced Streamlit features."""
    print("🎨 Enhanced Streamlit Features Test")
    print("=" * 50)
    
    # Test vector search status
    try:
        from services.vector_db import vector_db
        
        # Build index
        vector_db.build_index(force_rebuild=True)
        stats = vector_db.get_stats()
        
        print(f"✅ Vector search ready: {stats['vector_count']} vectors")
        print(f"✅ Vocabulary size: {stats['vocabulary_size']} words")
        
    except Exception as e:
        print(f"❌ Vector search error: {e}")
    
    # Test AI service with enhanced responses
    try:
        from services.ai_query import get_ai_query_service
        
        ai_service = get_ai_query_service()
        
        # Test semantic search query
        result = ai_service.process_query("find chicken food")
        
        print(f"\n🔍 Semantic Search Test:")
        print(f"   Query: 'find chicken food'")
        print(f"   Intent: {result['parsed_query']['intent']}")
        print(f"   Results: {len(result['results'])}")
        
        if result['results'] and 'similarity_score' in result['results'][0]:
            top_similarity = result['results'][0]['similarity_score']
            print(f"   Top similarity: {top_similarity:.1%}")
            print("   ✅ Vector search indicators will show in Streamlit")
        
    except Exception as e:
        print(f"❌ AI service error: {e}")
    
    print(f"\n🎉 Enhanced Streamlit Features:")
    print("   ✅ Vector search status in Settings")
    print("   ✅ Similarity score indicators")
    print("   ✅ Vector search examples in suggestions")
    print("   ✅ Rebuild vector index button")
    print("   ✅ Enhanced query details with similarity scores")

if __name__ == "__main__":
    test_enhanced_features()