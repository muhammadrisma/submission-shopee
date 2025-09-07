"""
Database connection utilities and schema management for the Food Receipt Analyzer.
Handles SQLite database initialization, connection management, and schema creation.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional
from config import config


class DatabaseManager:
    """Manages database connections and schema operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager with optional custom path."""
        self.db_path = db_path or config.get_database_url()
        self._ensure_database_directory()
    
    def _ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def initialize_database(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            self._create_tables(conn)
            conn.commit()
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create all required database tables."""
        
        # Create receipts table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT NOT NULL,
                receipt_date DATE NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                raw_text TEXT,
                image_path TEXT,
                UNIQUE(store_name, receipt_date, total_amount)
            )
        """)
        
        # Create receipt_items table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS receipt_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit_price DECIMAL(10,2) NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (receipt_id) REFERENCES receipts (id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better query performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_receipts_date 
            ON receipts(receipt_date)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_receipts_store 
            ON receipts(store_name)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_receipt_id 
            ON receipt_items(receipt_id)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_name 
            ON receipt_items(item_name)
        """)
    
    def drop_tables(self):
        """Drop all tables (useful for testing)."""
        with self.get_connection() as conn:
            conn.execute("DROP TABLE IF EXISTS receipt_items")
            conn.execute("DROP TABLE IF EXISTS receipts")
            conn.commit()
    
    def get_database_info(self) -> dict:
        """Get information about the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get counts for each table
            table_counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                table_counts[table] = cursor.fetchone()[0]
            
            return {
                'database_path': self.db_path,
                'tables': tables,
                'table_counts': table_counts
            }
    
    def test_connection(self) -> bool:
        """Test if database connection is working."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False


# Global database manager instance
db_manager = DatabaseManager()


def initialize_database():
    """Initialize the database with required schema."""
    db_manager.initialize_database()


def get_database_connection():
    """Get a database connection context manager."""
    return db_manager.get_connection()