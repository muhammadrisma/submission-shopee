"""
Data models for the Food Receipt Analyzer application.
Contains Receipt and ReceiptItem dataclasses with validation.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
import re


@dataclass
class ReceiptItem:
    """Represents an individual item from a receipt."""
    
    item_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    id: Optional[int] = None
    receipt_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate the receipt item data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate receipt item data."""
        if not self.item_name or not self.item_name.strip():
            raise ValueError("Item name cannot be empty")
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        # Clean item name
        self.item_name = self.item_name.strip()
        
        # Ensure prices are properly formatted Decimal objects
        if not isinstance(self.unit_price, Decimal):
            self.unit_price = Decimal(str(self.unit_price)).quantize(Decimal('0.01'))
        
        if not isinstance(self.total_price, Decimal):
            self.total_price = Decimal(str(self.total_price)).quantize(Decimal('0.01'))
        
        # Validate prices after conversion
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        
        if self.total_price < 0:
            raise ValueError("Total price cannot be negative")
    
    def to_dict(self) -> dict:
        """Convert receipt item to dictionary."""
        return {
            'id': self.id,
            'receipt_id': self.receipt_id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }


@dataclass
class Receipt:
    """Represents a complete receipt with metadata and items."""
    
    store_name: str
    receipt_date: date
    total_amount: Decimal
    items: List[ReceiptItem] = field(default_factory=list)
    id: Optional[int] = None
    upload_timestamp: Optional[datetime] = None
    raw_text: Optional[str] = None
    image_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate the receipt data after initialization."""
        self._validate()
        
        # Set upload timestamp if not provided
        if self.upload_timestamp is None:
            self.upload_timestamp = datetime.now()
    
    def _validate(self):
        """Validate receipt data."""
        if not self.store_name or not self.store_name.strip():
            raise ValueError("Store name cannot be empty")
        
        if not isinstance(self.receipt_date, date):
            raise ValueError("Receipt date must be a valid date object")
        
        if self.total_amount < 0:
            raise ValueError("Total amount cannot be negative")
        
        # Clean store name
        self.store_name = self.store_name.strip()
        
        # Ensure total_amount is properly formatted Decimal
        if not isinstance(self.total_amount, Decimal):
            self.total_amount = Decimal(str(self.total_amount)).quantize(Decimal('0.01'))
        
        # Validate items if present
        for item in self.items:
            if not isinstance(item, ReceiptItem):
                raise ValueError("All items must be ReceiptItem instances")
    
    def add_item(self, item: ReceiptItem):
        """Add an item to the receipt."""
        if not isinstance(item, ReceiptItem):
            raise ValueError("Item must be a ReceiptItem instance")
        
        self.items.append(item)
    
    def calculate_items_total(self) -> Decimal:
        """Calculate the total amount from all items."""
        return sum(item.total_price for item in self.items)
    
    def validate_total_consistency(self) -> bool:
        """Check if the receipt total matches the sum of item totals."""
        items_total = self.calculate_items_total()
        # Allow for small rounding differences
        difference = abs(self.total_amount - items_total)
        return difference <= Decimal('0.02')  # 2 cent tolerance
    
    def to_dict(self) -> dict:
        """Convert receipt to dictionary."""
        return {
            'id': self.id,
            'store_name': self.store_name,
            'receipt_date': self.receipt_date.isoformat() if self.receipt_date else None,
            'total_amount': float(self.total_amount),
            'upload_timestamp': self.upload_timestamp.isoformat() if self.upload_timestamp else None,
            'raw_text': self.raw_text,
            'image_path': self.image_path,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Receipt':
        """Create Receipt instance from dictionary."""
        # Parse date strings back to date objects
        receipt_date = None
        if data.get('receipt_date'):
            if isinstance(data['receipt_date'], str):
                receipt_date = datetime.fromisoformat(data['receipt_date']).date()
            else:
                receipt_date = data['receipt_date']
        
        upload_timestamp = None
        if data.get('upload_timestamp'):
            if isinstance(data['upload_timestamp'], str):
                upload_timestamp = datetime.fromisoformat(data['upload_timestamp'])
            else:
                upload_timestamp = data['upload_timestamp']
        
        # Create receipt items
        items = []
        for item_data in data.get('items', []):
            items.append(ReceiptItem(
                id=item_data.get('id'),
                receipt_id=item_data.get('receipt_id'),
                item_name=item_data['item_name'],
                quantity=item_data['quantity'],
                unit_price=Decimal(str(item_data['unit_price'])),
                total_price=Decimal(str(item_data['total_price']))
            ))
        
        return cls(
            id=data.get('id'),
            store_name=data['store_name'],
            receipt_date=receipt_date,
            total_amount=Decimal(str(data['total_amount'])),
            upload_timestamp=upload_timestamp,
            raw_text=data.get('raw_text'),
            image_path=data.get('image_path'),
            items=items
        )