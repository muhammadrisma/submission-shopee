"""
Unit tests for database operations.
Tests database connection, schema creation, and CRUD operations.
"""

import unittest
import tempfile
import os
from datetime import date, datetime
from decimal import Decimal

from models.receipt import Receipt, ReceiptItem
from database.connection import DatabaseManager
from database.service import DatabaseService


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization creates tables."""
        self.db_manager.initialize_database()
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('receipts', tables)
            self.assertIn('receipt_items', tables)
    
    def test_database_connection(self):
        """Test database connection works."""
        self.assertTrue(self.db_manager.test_connection())
    
    def test_get_database_info(self):
        """Test getting database information."""
        self.db_manager.initialize_database()
        info = self.db_manager.get_database_info()
        
        self.assertIn('database_path', info)
        self.assertIn('tables', info)
        self.assertIn('table_counts', info)
        self.assertEqual(info['table_counts']['receipts'], 0)
        self.assertEqual(info['table_counts']['receipt_items'], 0)
    
    def test_drop_tables(self):
        """Test dropping tables."""
        self.db_manager.initialize_database()
        self.db_manager.drop_tables()
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertNotIn('receipts', tables)
            self.assertNotIn('receipt_items', tables)


class TestDatabaseService(unittest.TestCase):
    """Test cases for DatabaseService CRUD operations."""
    
    def setUp(self):
        """Set up test database and service."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.initialize_database()
        
        self.db_service = DatabaseService()
        self.db_service.db_manager = self.db_manager
        
        # Create sample data
        self.sample_items = [
            ReceiptItem("Apple", 2, Decimal("1.50"), Decimal("3.00")),
            ReceiptItem("Banana", 3, Decimal("0.75"), Decimal("2.25"))
        ]
        
        self.sample_receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
            items=self.sample_items,
            raw_text="Test receipt text",
            image_path="/test/path.jpg"
        )
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_save_receipt(self):
        """Test saving a receipt with items."""
        receipt_id = self.db_service.save_receipt(self.sample_receipt)
        
        self.assertIsNotNone(receipt_id)
        self.assertEqual(self.sample_receipt.id, receipt_id)
        
        # Verify items have receipt_id set
        for item in self.sample_receipt.items:
            self.assertEqual(item.receipt_id, receipt_id)
            self.assertIsNotNone(item.id)
    
    def test_save_duplicate_receipt(self):
        """Test saving duplicate receipt raises error."""
        self.db_service.save_receipt(self.sample_receipt)
        
        # Try to save the same receipt again
        duplicate_receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25")
        )
        
        with self.assertRaises(ValueError) as context:
            self.db_service.save_receipt(duplicate_receipt)
        self.assertIn("Receipt already exists", str(context.exception))
    
    def test_get_receipt_by_id(self):
        """Test retrieving receipt by ID."""
        receipt_id = self.db_service.save_receipt(self.sample_receipt)
        
        retrieved_receipt = self.db_service.get_receipt_by_id(receipt_id)
        
        self.assertIsNotNone(retrieved_receipt)
        self.assertEqual(retrieved_receipt.id, receipt_id)
        self.assertEqual(retrieved_receipt.store_name, "Test Store")
        self.assertEqual(retrieved_receipt.receipt_date, date(2024, 1, 15))
        self.assertEqual(retrieved_receipt.total_amount, Decimal("5.25"))
        self.assertEqual(len(retrieved_receipt.items), 2)
        
        # Check items
        apple_item = next(item for item in retrieved_receipt.items if item.item_name == "Apple")
        self.assertEqual(apple_item.quantity, 2)
        self.assertEqual(apple_item.unit_price, Decimal("1.50"))
        self.assertEqual(apple_item.total_price, Decimal("3.00"))
    
    def test_get_nonexistent_receipt(self):
        """Test retrieving non-existent receipt returns None."""
        result = self.db_service.get_receipt_by_id(999)
        self.assertIsNone(result)
    
    def test_get_receipts_by_date_range(self):
        """Test retrieving receipts by date range."""
        # Save multiple receipts with different dates
        receipt1 = Receipt("Store A", date(2024, 1, 10), Decimal("10.00"))
        receipt2 = Receipt("Store B", date(2024, 1, 15), Decimal("15.00"))
        receipt3 = Receipt("Store C", date(2024, 1, 20), Decimal("20.00"))
        
        self.db_service.save_receipt(receipt1)
        self.db_service.save_receipt(receipt2)
        self.db_service.save_receipt(receipt3)
        
        # Get receipts in range
        receipts = self.db_service.get_receipts_by_date_range(
            date(2024, 1, 12), date(2024, 1, 18)
        )
        
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0].store_name, "Store B")
    
    def test_get_receipts_by_store(self):
        """Test retrieving receipts by store name."""
        receipt1 = Receipt("Target", date(2024, 1, 10), Decimal("10.00"))
        receipt2 = Receipt("Walmart", date(2024, 1, 15), Decimal("15.00"))
        receipt3 = Receipt("Target Express", date(2024, 1, 20), Decimal("20.00"))
        
        self.db_service.save_receipt(receipt1)
        self.db_service.save_receipt(receipt2)
        self.db_service.save_receipt(receipt3)
        
        # Search for "Target" (should match both Target stores)
        receipts = self.db_service.get_receipts_by_store("Target")
        
        self.assertEqual(len(receipts), 2)
        store_names = [r.store_name for r in receipts]
        self.assertIn("Target", store_names)
        self.assertIn("Target Express", store_names)
    
    def test_search_items_by_name(self):
        """Test searching items by name."""
        # Create receipts with different items
        receipt1 = Receipt("Store A", date(2024, 1, 10), Decimal("5.00"), [
            ReceiptItem("Red Apple", 1, Decimal("2.00"), Decimal("2.00")),
            ReceiptItem("Banana", 2, Decimal("1.50"), Decimal("3.00"))
        ])
        
        receipt2 = Receipt("Store B", date(2024, 1, 15), Decimal("4.00"), [
            ReceiptItem("Green Apple", 2, Decimal("2.00"), Decimal("4.00"))
        ])
        
        self.db_service.save_receipt(receipt1)
        self.db_service.save_receipt(receipt2)
        
        # Search for "Apple"
        results = self.db_service.search_items_by_name("Apple")
        
        self.assertEqual(len(results), 2)
        item_names = [r['item_name'] for r in results]
        self.assertIn("Red Apple", item_names)
        self.assertIn("Green Apple", item_names)
    
    def test_search_items_with_time_limit(self):
        """Test searching items with time limit."""
        # Create receipt from 10 days ago
        old_receipt = Receipt("Store A", date(2024, 1, 1), Decimal("5.00"), [
            ReceiptItem("Apple", 1, Decimal("2.00"), Decimal("2.00"))
        ])
        
        self.db_service.save_receipt(old_receipt)
        
        # Search for items in last 7 days (should find nothing)
        results = self.db_service.search_items_by_name("Apple", days_back=7)
        self.assertEqual(len(results), 0)
    
    def test_get_total_spending_by_date(self):
        """Test getting total spending for a specific date."""
        receipt1 = Receipt("Store A", date(2024, 1, 15), Decimal("10.00"))
        receipt2 = Receipt("Store B", date(2024, 1, 15), Decimal("15.00"))
        receipt3 = Receipt("Store C", date(2024, 1, 16), Decimal("20.00"))
        
        self.db_service.save_receipt(receipt1)
        self.db_service.save_receipt(receipt2)
        self.db_service.save_receipt(receipt3)
        
        total = self.db_service.get_total_spending_by_date(date(2024, 1, 15))
        self.assertEqual(total, Decimal("25.00"))
        
        total_empty = self.db_service.get_total_spending_by_date(date(2024, 1, 17))
        self.assertEqual(total_empty, Decimal("0.00"))
    
    def test_get_stores_with_item(self):
        """Test getting stores that sold a specific item."""
        receipt1 = Receipt("Store A", date(2024, 1, 10), Decimal("5.00"), [
            ReceiptItem("Apple", 1, Decimal("2.00"), Decimal("2.00"))
        ])
        
        receipt2 = Receipt("Store B", date(2024, 1, 15), Decimal("4.00"), [
            ReceiptItem("Apple", 2, Decimal("2.00"), Decimal("4.00"))
        ])
        
        receipt3 = Receipt("Store C", date(2024, 1, 20), Decimal("3.00"), [
            ReceiptItem("Banana", 1, Decimal("3.00"), Decimal("3.00"))
        ])
        
        self.db_service.save_receipt(receipt1)
        self.db_service.save_receipt(receipt2)
        self.db_service.save_receipt(receipt3)
        
        stores = self.db_service.get_stores_with_item("Apple")
        
        self.assertEqual(len(stores), 2)
        self.assertIn("Store A", stores)
        self.assertIn("Store B", stores)
        self.assertNotIn("Store C", stores)
    
    def test_update_receipt(self):
        """Test updating an existing receipt."""
        receipt_id = self.db_service.save_receipt(self.sample_receipt)
        
        # Update the receipt
        self.sample_receipt.store_name = "Updated Store"
        self.sample_receipt.total_amount = Decimal("10.00")
        self.sample_receipt.items = [
            ReceiptItem("Orange", 1, Decimal("10.00"), Decimal("10.00"))
        ]
        
        success = self.db_service.update_receipt(self.sample_receipt)
        self.assertTrue(success)
        
        # Verify update
        updated_receipt = self.db_service.get_receipt_by_id(receipt_id)
        self.assertEqual(updated_receipt.store_name, "Updated Store")
        self.assertEqual(updated_receipt.total_amount, Decimal("10.00"))
        self.assertEqual(len(updated_receipt.items), 1)
        self.assertEqual(updated_receipt.items[0].item_name, "Orange")
    
    def test_update_nonexistent_receipt(self):
        """Test updating non-existent receipt returns False."""
        receipt = Receipt("Store", date(2024, 1, 15), Decimal("5.00"))
        receipt.id = 999  # Non-existent ID
        
        success = self.db_service.update_receipt(receipt)
        self.assertFalse(success)
    
    def test_delete_receipt(self):
        """Test deleting a receipt."""
        receipt_id = self.db_service.save_receipt(self.sample_receipt)
        
        success = self.db_service.delete_receipt(receipt_id)
        self.assertTrue(success)
        
        # Verify deletion
        deleted_receipt = self.db_service.get_receipt_by_id(receipt_id)
        self.assertIsNone(deleted_receipt)
    
    def test_delete_nonexistent_receipt(self):
        """Test deleting non-existent receipt returns False."""
        success = self.db_service.delete_receipt(999)
        self.assertFalse(success)
    
    def test_get_all_receipts(self):
        """Test getting all receipts."""
        receipt1 = Receipt("Store A", date(2024, 1, 10), Decimal("10.00"))
        receipt2 = Receipt("Store B", date(2024, 1, 15), Decimal("15.00"))
        
        self.db_service.save_receipt(receipt1)
        self.db_service.save_receipt(receipt2)
        
        all_receipts = self.db_service.get_all_receipts()
        self.assertEqual(len(all_receipts), 2)
        
        # Test with limit
        limited_receipts = self.db_service.get_all_receipts(limit=1)
        self.assertEqual(len(limited_receipts), 1)
    
    def test_get_database_stats(self):
        """Test getting database statistics."""
        receipt1 = Receipt("Store A", date(2024, 1, 10), Decimal("10.00"), [
            ReceiptItem("Apple", 1, Decimal("10.00"), Decimal("10.00"))
        ])
        receipt2 = Receipt("Store B", date(2024, 1, 15), Decimal("15.00"), [
            ReceiptItem("Banana", 2, Decimal("7.50"), Decimal("15.00"))
        ])
        
        self.db_service.save_receipt(receipt1)
        self.db_service.save_receipt(receipt2)
        
        stats = self.db_service.get_database_stats()
        
        self.assertEqual(stats['receipt_count'], 2)
        self.assertEqual(stats['item_count'], 2)
        self.assertEqual(stats['total_spending'], 25.0)
        self.assertEqual(stats['date_range']['earliest'], '2024-01-10')
        self.assertEqual(stats['date_range']['latest'], '2024-01-15')


if __name__ == '__main__':
    unittest.main()