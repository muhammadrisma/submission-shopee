"""
Custom Vector Database Implementation with Cosine Similarity
Built from scratch without high-level libraries for semantic search of food items.
"""

import json
import math
import pickle
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from database.connection import db_manager


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""

    item_id: int
    item_name: str
    similarity_score: float
    metadata: Dict[str, Any]


class TextVectorizer:
    """Custom text vectorizer using TF-IDF approach."""

    def __init__(self):
        """Initialize the vectorizer."""
        self.vocabulary = {}  # word -> index mapping
        self.idf_scores = {}  # word -> IDF score
        self.is_fitted = False

    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocess text into tokens."""
        # Convert to lowercase and remove special characters
        text = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())

        # Split into words and filter out short words
        words = [word.strip() for word in text.split() if len(word.strip()) > 1]

        # Handle compound food names
        processed_words = []
        for word in words:
            # Split hyphenated words: "kids-meal" -> ["kids", "meal"]
            if "-" in word:
                processed_words.extend(word.split("-"))
            else:
                processed_words.append(word)

        return [w for w in processed_words if w]

    def fit(self, documents: List[str]):
        """Fit the vectorizer on a collection of documents."""
        # Preprocess all documents
        processed_docs = [self._preprocess_text(doc) for doc in documents]

        # Build vocabulary
        all_words = set()
        for doc in processed_docs:
            all_words.update(doc)

        self.vocabulary = {word: idx for idx, word in enumerate(sorted(all_words))}

        # Calculate IDF scores
        doc_count = len(processed_docs)
        word_doc_counts = defaultdict(int)

        for doc in processed_docs:
            unique_words = set(doc)
            for word in unique_words:
                word_doc_counts[word] += 1

        # IDF = log(total_docs / docs_containing_word)
        self.idf_scores = {}
        for word in self.vocabulary:
            doc_freq = word_doc_counts[word]
            self.idf_scores[word] = math.log(
                doc_count / (doc_freq + 1)
            )  # +1 for smoothing

        self.is_fitted = True

    def transform(self, text: str) -> List[float]:
        """Transform text into TF-IDF vector."""
        if not self.is_fitted:
            raise ValueError("Vectorizer must be fitted before transform")

        words = self._preprocess_text(text)
        word_counts = Counter(words)

        # Calculate TF-IDF vector
        vector = [0.0] * len(self.vocabulary)
        total_words = len(words)

        for word, count in word_counts.items():
            if word in self.vocabulary:
                tf = count / total_words  # Term frequency
                idf = self.idf_scores[word]  # Inverse document frequency
                tfidf = tf * idf

                word_idx = self.vocabulary[word]
                vector[word_idx] = tfidf

        return vector

    def fit_transform(self, documents: List[str]) -> List[List[float]]:
        """Fit the vectorizer and transform documents."""
        self.fit(documents)
        return [self.transform(doc) for doc in documents]


class VectorMath:
    """Custom vector mathematics operations."""

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        Returns value between -1 and 1, where 1 means identical vectors.
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))

        # Handle zero vectors
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)

        # Clamp to [-1, 1] to handle floating point errors
        return max(-1.0, min(1.0, similarity))

    @staticmethod
    def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")

        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    @staticmethod
    def normalize_vector(vector: List[float]) -> List[float]:
        """Normalize vector to unit length."""
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude == 0:
            return vector
        return [x / magnitude for x in vector]


class CustomVectorDB:
    """Custom vector database implementation using SQLite."""

    def __init__(self):
        """Initialize the vector database."""
        self.vectorizer = TextVectorizer()
        self.db_manager = db_manager
        self._ensure_vector_tables()

    def _ensure_vector_tables(self):
        """Create vector storage tables if they don't exist."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Table for storing item vectors
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS item_vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    vector_data BLOB NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES receipt_items (id)
                )
            """
            )

            # Table for storing vectorizer state
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vectorizer_state (
                    id INTEGER PRIMARY KEY,
                    vocabulary TEXT NOT NULL,
                    idf_scores TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    def _serialize_vector(self, vector: List[float]) -> bytes:
        """Serialize vector to bytes for storage."""
        return pickle.dumps(vector)

    def _deserialize_vector(self, data: bytes) -> List[float]:
        """Deserialize vector from bytes."""
        return pickle.loads(data)

    def _save_vectorizer_state(self):
        """Save vectorizer state to database."""
        if not self.vectorizer.is_fitted:
            return

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            vocabulary_json = json.dumps(self.vectorizer.vocabulary)
            idf_scores_json = json.dumps(self.vectorizer.idf_scores)

            cursor.execute(
                """
                INSERT OR REPLACE INTO vectorizer_state (id, vocabulary, idf_scores)
                VALUES (1, ?, ?)
            """,
                (vocabulary_json, idf_scores_json),
            )

            conn.commit()

    def _load_vectorizer_state(self) -> bool:
        """Load vectorizer state from database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT vocabulary, idf_scores FROM vectorizer_state WHERE id = 1"
            )
            row = cursor.fetchone()

            if row:
                self.vectorizer.vocabulary = json.loads(row[0])
                self.vectorizer.idf_scores = json.loads(row[1])
                self.vectorizer.is_fitted = True
                return True

            return False

    def build_index(self, force_rebuild: bool = False):
        """Build or rebuild the vector index from all receipt items."""
        from database.service import db_service

        # Load existing vectorizer state if available
        if not force_rebuild and self._load_vectorizer_state():
            print("📚 Loaded existing vectorizer state")
        else:
            print("🔨 Building new vector index...")

            # Get all receipt items
            receipts = db_service.get_all_receipts()
            all_items = []
            item_texts = []

            for receipt in receipts:
                for item in receipt.items:
                    all_items.append(
                        {
                            "id": item.id,
                            "name": item.item_name,
                            "store": receipt.store_name,
                            "date": receipt.receipt_date,
                            "price": float(item.total_price),
                        }
                    )
                    # Create rich text representation for better vectorization
                    item_text = f"{item.item_name} {receipt.store_name}"
                    item_texts.append(item_text)

            if not item_texts:
                print("⚠️ No items found to vectorize")
                return

            # Fit vectorizer on all item texts
            self.vectorizer.fit(item_texts)
            self._save_vectorizer_state()

            print(f"📊 Vectorizer vocabulary size: {len(self.vectorizer.vocabulary)}")

        # Clear existing vectors
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM item_vectors")
            conn.commit()

        # Generate and store vectors for all items
        from database.service import db_service

        receipts = db_service.get_all_receipts()

        vectors_added = 0
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            for receipt in receipts:
                for item in receipt.items:
                    if item.id is None:
                        continue

                    # Create text representation
                    item_text = f"{item.item_name} {receipt.store_name}"

                    # Generate vector
                    vector = self.vectorizer.transform(item_text)
                    vector_data = self._serialize_vector(vector)

                    # Store metadata
                    metadata = {
                        "store_name": receipt.store_name,
                        "receipt_date": receipt.receipt_date.isoformat(),
                        "price": float(item.total_price),
                        "quantity": item.quantity,
                    }
                    metadata_json = json.dumps(metadata)

                    # Insert vector
                    cursor.execute(
                        """
                        INSERT INTO item_vectors (item_id, item_name, vector_data, metadata)
                        VALUES (?, ?, ?, ?)
                    """,
                        (item.id, item.item_name, vector_data, metadata_json),
                    )

                    vectors_added += 1

            conn.commit()

        print(f"✅ Added {vectors_added} vectors to the database")

    def search_similar(
        self, query: str, top_k: int = 10, min_similarity: float = 0.1
    ) -> List[VectorSearchResult]:
        """
        Search for items similar to the query using cosine similarity.

        Args:
            query: Search query text
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of VectorSearchResult objects sorted by similarity
        """
        if not self.vectorizer.is_fitted:
            if not self._load_vectorizer_state():
                print("⚠️ Vector index not built. Run build_index() first.")
                return []

        # Generate query vector
        query_vector = self.vectorizer.transform(query)

        # Get all stored vectors
        results = []
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT item_id, item_name, vector_data, metadata FROM item_vectors"
            )

            for row in cursor.fetchall():
                item_id, item_name, vector_data, metadata_json = row

                # Deserialize vector
                item_vector = self._deserialize_vector(vector_data)

                # Calculate similarity
                similarity = VectorMath.cosine_similarity(query_vector, item_vector)

                if similarity >= min_similarity:
                    metadata = json.loads(metadata_json) if metadata_json else {}

                    result = VectorSearchResult(
                        item_id=item_id,
                        item_name=item_name,
                        similarity_score=similarity,
                        metadata=metadata,
                    )
                    results.append(result)

        # Sort by similarity (descending) and return top_k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    def find_similar_items(
        self, item_name: str, top_k: int = 5
    ) -> List[VectorSearchResult]:
        """Find items similar to a given item name."""
        return self.search_similar(item_name, top_k=top_k, min_similarity=0.2)

    def semantic_search(self, query: str, top_k: int = 10) -> List[VectorSearchResult]:
        """Perform semantic search across all items."""
        return self.search_similar(query, top_k=top_k, min_similarity=0.1)

    def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM item_vectors")
            vector_count = cursor.fetchone()[0]

            vocabulary_size = (
                len(self.vectorizer.vocabulary) if self.vectorizer.is_fitted else 0
            )

            return {
                "vector_count": vector_count,
                "vocabulary_size": vocabulary_size,
                "is_fitted": self.vectorizer.is_fitted,
            }


# Global vector database instance
vector_db = CustomVectorDB()
