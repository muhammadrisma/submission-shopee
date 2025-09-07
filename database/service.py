"""
Database service class with CRUD operations for receipts and items.
Provides high-level database operations for the Food Receipt Analyzer.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
import sqlite3

from models.receipt import Receipt, ReceiptItem
from database.connection import db_manager


class DatabaseService:
    """Service class for database operations on receipts and items."""
    
    def __init__(self):
        """Initialize the database service."""
        self.db_manager = db_manager
    
    def save_receipt(self, receipt: Receipt) -> int:
        """
        Save a receipt and its items to the database.
        Returns the receipt ID.
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Insert receipt
                cursor.execute("""
                    INSERT INTO receipts (store_name, receipt_date, total_amount, 
                                        upload_timestamp, raw_text, image_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    receipt.store_name,
                    receipt.receipt_date.isoformat(),
                    float(receipt.total_amount),
                    receipt.upload_timestamp.isoformat() if receipt.upload_timestamp else None,
                    receipt.raw_text,
                    receipt.image_path
                ))
                
                receipt_id = cursor.lastrowid
                receipt.id = receipt_id
                
                # Insert receipt items
                for item in receipt.items:
                    item.receipt_id = receipt_id
                    self._save_receipt_item(cursor, item)
                
                conn.commit()
                return receipt_id
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Receipt already exists or constraint violation: {e}")
            except Exception as e:
                conn.rollback()
                raise e
    
    def _save_receipt_item(self, cursor: sqlite3.Cursor, item: ReceiptItem) -> int:
        """Save a single receipt item."""
        cursor.execute("""
            INSERT INTO receipt_items (receipt_id, item_name, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?)
        """, (
            item.receipt_id,
            item.item_name,
            item.quantity,
            float(item.unit_price),
            float(item.total_price)
        ))
        
        item_id = cursor.lastrowid
        item.id = item_id
        return item_id
    
    def get_receipt_by_id(self, receipt_id: int) -> Optional[Receipt]:
        """Get a receipt by its ID, including all items."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get receipt
            cursor.execute("""
                SELECT id, store_name, receipt_date, total_amount, 
                       upload_timestamp, raw_text, image_path
                FROM receipts WHERE id = ?
            """, (receipt_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse receipt data
            receipt_data = dict(row)
            receipt_data['receipt_date'] = datetime.fromisoformat(receipt_data['receipt_date']).date()
            if receipt_data['upload_timestamp']:
                receipt_data['upload_timestamp'] = datetime.fromisoformat(receipt_data['upload_timestamp'])
            receipt_data['total_amount'] = Decimal(str(receipt_data['total_amount']))
            
            # Get receipt items
            cursor.execute("""
                SELECT id, receipt_id, item_name, quantity, unit_price, total_price
                FROM receipt_items WHERE receipt_id = ?
                ORDER BY id
            """, (receipt_id,))
            
            items = []
            for item_row in cursor.fetchall():
                item_data = dict(item_row)
                items.append(ReceiptItem(
                    id=item_data['id'],
                    receipt_id=item_data['receipt_id'],
                    item_name=item_data['item_name'],
                    quantity=item_data['quantity'],
                    unit_price=Decimal(str(item_data['unit_price'])),
                    total_price=Decimal(str(item_data['total_price']))
                ))
            
            # Create receipt directly instead of using from_dict
            return Receipt(
                id=receipt_data['id'],
                store_name=receipt_data['store_name'],
                receipt_date=receipt_data['receipt_date'],
                total_amount=receipt_data['total_amount'],
                upload_timestamp=receipt_data['upload_timestamp'],
                raw_text=receipt_data['raw_text'],
                image_path=receipt_data['image_path'],
                items=items
            )
    
    def get_receipts_by_date_range(self, start_date: date, end_date: date) -> List[Receipt]:
        """Get all receipts within a date range."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM receipts 
                WHERE receipt_date BETWEEN ? AND ?
                ORDER BY receipt_date DESC, id DESC
            """, (start_date.isoformat(), end_date.isoformat()))
            
            receipt_ids = [row[0] for row in cursor.fetchall()]
            return [self.get_receipt_by_id(rid) for rid in receipt_ids if self.get_receipt_by_id(rid)]
    
    def get_receipts_by_store(self, store_name: str) -> List[Receipt]:
        """Get all receipts from a specific store."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM receipts 
                WHERE store_name LIKE ?
                ORDER BY receipt_date DESC, id DESC
            """, (f"%{store_name}%",))
            
            receipt_ids = [row[0] for row in cursor.fetchall()]
            return [self.get_receipt_by_id(rid) for rid in receipt_ids if self.get_receipt_by_id(rid)]
    
    def search_items_by_name(self, item_name: str, days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for items by name, optionally within a time period.
        Returns list of items with receipt information.
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT ri.id, ri.item_name, ri.quantity, ri.unit_price, ri.total_price,
                       r.id as receipt_id, r.store_name, r.receipt_date, r.total_amount
                FROM receipt_items ri
                JOIN receipts r ON ri.receipt_id = r.id
                WHERE ri.item_name LIKE ?
            """
            params = [f"%{item_name}%"]
            
            if days_back:
                query += " AND r.receipt_date >= date('now', '-{} days')".format(days_back)
            
            query += " ORDER BY r.receipt_date DESC"
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                row_dict['receipt_date'] = datetime.fromisoformat(row_dict['receipt_date']).date()
                row_dict['unit_price'] = Decimal(str(row_dict['unit_price']))
                row_dict['total_price'] = Decimal(str(row_dict['total_price']))
                row_dict['total_amount'] = Decimal(str(row_dict['total_amount']))
                results.append(row_dict)
            
            return results
    
    def get_total_spending_by_date(self, target_date: date) -> Decimal:
        """Get total spending for a specific date."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as total
                FROM receipts 
                WHERE receipt_date = ?
            """, (target_date.isoformat(),))
            
            result = cursor.fetchone()
            return Decimal(str(result[0]))
    
    def get_stores_with_item(self, item_name: str, days_back: Optional[int] = None) -> List[str]:
        """Get list of stores that sold a specific item."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT DISTINCT r.store_name
                FROM receipt_items ri
                JOIN receipts r ON ri.receipt_id = r.id
                WHERE ri.item_name LIKE ?
            """
            params = [f"%{item_name}%"]
            
            if days_back:
                query += " AND r.receipt_date >= date('now', '-{} days')".format(days_back)
            
            query += " ORDER BY r.store_name"
            
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]
    
    def update_receipt(self, receipt: Receipt) -> bool:
        """Update an existing receipt."""
        if not receipt.id:
            raise ValueError("Receipt must have an ID to update")
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Update receipt
                cursor.execute("""
                    UPDATE receipts 
                    SET store_name = ?, receipt_date = ?, total_amount = ?,
                        raw_text = ?, image_path = ?
                    WHERE id = ?
                """, (
                    receipt.store_name,
                    receipt.receipt_date.isoformat(),
                    float(receipt.total_amount),
                    receipt.raw_text,
                    receipt.image_path,
                    receipt.id
                ))
                
                if cursor.rowcount == 0:
                    return False
                
                # Delete existing items and re-insert
                cursor.execute("DELETE FROM receipt_items WHERE receipt_id = ?", (receipt.id,))
                
                for item in receipt.items:
                    item.receipt_id = receipt.id
                    self._save_receipt_item(cursor, item)
                
                conn.commit()
                return True
                
            except Exception as e:
                conn.rollback()
                raise e
    
    def delete_receipt(self, receipt_id: int) -> bool:
        """Delete a receipt and all its items."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Delete receipt (items will be deleted by CASCADE)
                cursor.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
                
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
                
            except Exception as e:
                conn.rollback()
                raise e
    
    def get_all_receipts(self, limit: Optional[int] = None) -> List[Receipt]:
        """Get all receipts, optionally limited."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT id FROM receipts ORDER BY receipt_date DESC, id DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            receipt_ids = [row[0] for row in cursor.fetchall()]
            return [self.get_receipt_by_id(rid) for rid in receipt_ids if self.get_receipt_by_id(rid)]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count receipts
            cursor.execute("SELECT COUNT(*) FROM receipts")
            receipt_count = cursor.fetchone()[0]
            
            # Count items
            cursor.execute("SELECT COUNT(*) FROM receipt_items")
            item_count = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(receipt_date), MAX(receipt_date) FROM receipts")
            date_range = cursor.fetchone()
            
            # Get total spending
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM receipts")
            total_spending = cursor.fetchone()[0]
            
            return {
                'receipt_count': receipt_count,
                'item_count': item_count,
                'date_range': {
                    'earliest': date_range[0],
                    'latest': date_range[1]
                },
                'total_spending': float(total_spending)
            }


# Global database service instance
db_service = DatabaseService()