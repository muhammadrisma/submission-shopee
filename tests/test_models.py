"""
Unit tests for data models (Receipt and ReceiptItem).
Tests validation, data integrity, and model functionality.
"""

import unittest
from datetime import date, datetime
from decimal import Decimal

from models.receipt import Receipt, ReceiptItem


class TestReceiptItem(unittest.TestCase):
    """Test cases for ReceiptItem model."""

    def test_valid_receipt_item_creation(self):
        """Test creating a valid receipt item."""
        item = ReceiptItem(
            item_name="Apple",
            quantity=2,
            unit_price=Decimal("1.50"),
            total_price=Decimal("3.00"),
        )

        self.assertEqual(item.item_name, "Apple")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal("1.50"))
        self.assertEqual(item.total_price, Decimal("3.00"))
        self.assertIsNone(item.id)
        self.assertIsNone(item.receipt_id)

    def test_receipt_item_validation_empty_name(self):
        """Test validation fails for empty item name."""
        with self.assertRaises(ValueError) as context:
            ReceiptItem(
                item_name="",
                quantity=1,
                unit_price=Decimal("1.00"),
                total_price=Decimal("1.00"),
            )
        self.assertIn("Item name cannot be empty", str(context.exception))

    def test_receipt_item_validation_zero_quantity(self):
        """Test validation fails for zero quantity."""
        with self.assertRaises(ValueError) as context:
            ReceiptItem(
                item_name="Apple",
                quantity=0,
                unit_price=Decimal("1.00"),
                total_price=Decimal("1.00"),
            )
        self.assertIn("Quantity must be greater than 0", str(context.exception))

    def test_receipt_item_validation_negative_prices(self):
        """Test validation fails for negative prices."""
        with self.assertRaises(ValueError):
            ReceiptItem(
                item_name="Apple",
                quantity=1,
                unit_price=Decimal("-1.00"),
                total_price=Decimal("1.00"),
            )

        with self.assertRaises(ValueError):
            ReceiptItem(
                item_name="Apple",
                quantity=1,
                unit_price=Decimal("1.00"),
                total_price=Decimal("-1.00"),
            )

    def test_receipt_item_price_conversion(self):
        """Test automatic conversion of prices to Decimal."""
        item = ReceiptItem(
            item_name="Apple",
            quantity=1,
            unit_price=1.50,
            total_price="1.50",
        )

        self.assertIsInstance(item.unit_price, Decimal)
        self.assertIsInstance(item.total_price, Decimal)
        self.assertEqual(item.unit_price, Decimal("1.50"))
        self.assertEqual(item.total_price, Decimal("1.50"))

    def test_receipt_item_name_trimming(self):
        """Test item name is trimmed of whitespace."""
        item = ReceiptItem(
            item_name="  Apple  ",
            quantity=1,
            unit_price=Decimal("1.00"),
            total_price=Decimal("1.00"),
        )

        self.assertEqual(item.item_name, "Apple")

    def test_receipt_item_to_dict(self):
        """Test converting receipt item to dictionary."""
        item = ReceiptItem(
            id=1,
            receipt_id=10,
            item_name="Apple",
            quantity=2,
            unit_price=Decimal("1.50"),
            total_price=Decimal("3.00"),
        )

        expected = {
            "id": 1,
            "receipt_id": 10,
            "item_name": "Apple",
            "quantity": 2,
            "unit_price": 1.50,
            "total_price": 3.00,
        }

        self.assertEqual(item.to_dict(), expected)


class TestReceipt(unittest.TestCase):
    """Test cases for Receipt model."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_items = [
            ReceiptItem("Apple", 2, Decimal("1.50"), Decimal("3.00")),
            ReceiptItem("Banana", 3, Decimal("0.75"), Decimal("2.25")),
        ]

    def test_valid_receipt_creation(self):
        """Test creating a valid receipt."""
        receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
            items=self.sample_items,
        )

        self.assertEqual(receipt.store_name, "Test Store")
        self.assertEqual(receipt.receipt_date, date(2024, 1, 15))
        self.assertEqual(receipt.total_amount, Decimal("5.25"))
        self.assertEqual(len(receipt.items), 2)
        self.assertIsNotNone(receipt.upload_timestamp)
        self.assertIsNone(receipt.id)

    def test_receipt_validation_empty_store_name(self):
        """Test validation fails for empty store name."""
        with self.assertRaises(ValueError) as context:
            Receipt(
                store_name="",
                receipt_date=date(2024, 1, 15),
                total_amount=Decimal("5.25"),
            )
        self.assertIn("Store name cannot be empty", str(context.exception))

    def test_receipt_validation_invalid_date(self):
        """Test validation fails for invalid date."""
        with self.assertRaises(ValueError) as context:
            Receipt(
                store_name="Test Store",
                receipt_date="2024-01-15",
                total_amount=Decimal("5.25"),
            )
        self.assertIn(
            "Receipt date must be a valid date object", str(context.exception)
        )

    def test_receipt_validation_negative_total(self):
        """Test validation fails for negative total amount."""
        with self.assertRaises(ValueError) as context:
            Receipt(
                store_name="Test Store",
                receipt_date=date(2024, 1, 15),
                total_amount=Decimal("-5.25"),
            )
        self.assertIn("Total amount cannot be negative", str(context.exception))

    def test_receipt_store_name_trimming(self):
        """Test store name is trimmed of whitespace."""
        receipt = Receipt(
            store_name="  Test Store  ",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
        )

        self.assertEqual(receipt.store_name, "Test Store")

    def test_receipt_total_amount_conversion(self):
        """Test automatic conversion of total amount to Decimal."""
        receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=5.25,
        )

        self.assertIsInstance(receipt.total_amount, Decimal)
        self.assertEqual(receipt.total_amount, Decimal("5.25"))

    def test_receipt_add_item(self):
        """Test adding items to receipt."""
        receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
        )

        item = ReceiptItem("Apple", 1, Decimal("1.00"), Decimal("1.00"))
        receipt.add_item(item)

        self.assertEqual(len(receipt.items), 1)
        self.assertEqual(receipt.items[0], item)

    def test_receipt_add_invalid_item(self):
        """Test adding invalid item to receipt fails."""
        receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
        )

        with self.assertRaises(ValueError):
            receipt.add_item("not an item")

    def test_receipt_calculate_items_total(self):
        """Test calculating total from items."""
        receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
            items=self.sample_items,
        )

        calculated_total = receipt.calculate_items_total()
        self.assertEqual(calculated_total, Decimal("5.25"))

    def test_receipt_validate_total_consistency(self):
        """Test validation of total consistency with items."""
        receipt = Receipt(
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
            items=self.sample_items,
        )

        self.assertTrue(receipt.validate_total_consistency())

        receipt.total_amount = Decimal("10.00")
        self.assertFalse(receipt.validate_total_consistency())

        receipt.total_amount = Decimal("5.27")
        self.assertTrue(receipt.validate_total_consistency())

    def test_receipt_to_dict(self):
        """Test converting receipt to dictionary."""
        upload_time = datetime(2024, 1, 15, 10, 30, 0)
        receipt = Receipt(
            id=1,
            store_name="Test Store",
            receipt_date=date(2024, 1, 15),
            total_amount=Decimal("5.25"),
            upload_timestamp=upload_time,
            raw_text="Raw receipt text",
            image_path="/path/to/image.jpg",
            items=self.sample_items,
        )

        result = receipt.to_dict()

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["store_name"], "Test Store")
        self.assertEqual(result["receipt_date"], "2024-01-15")
        self.assertEqual(result["total_amount"], 5.25)
        self.assertEqual(result["upload_timestamp"], "2024-01-15T10:30:00")
        self.assertEqual(result["raw_text"], "Raw receipt text")
        self.assertEqual(result["image_path"], "/path/to/image.jpg")
        self.assertEqual(len(result["items"]), 2)

    def test_receipt_from_dict(self):
        """Test creating receipt from dictionary."""
        data = {
            "id": 1,
            "store_name": "Test Store",
            "receipt_date": "2024-01-15",
            "total_amount": 5.25,
            "upload_timestamp": "2024-01-15T10:30:00",
            "raw_text": "Raw receipt text",
            "image_path": "/path/to/image.jpg",
            "items": [
                {
                    "id": 1,
                    "receipt_id": 1,
                    "item_name": "Apple",
                    "quantity": 2,
                    "unit_price": 1.50,
                    "total_price": 3.00,
                }
            ],
        }

        receipt = Receipt.from_dict(data)

        self.assertEqual(receipt.id, 1)
        self.assertEqual(receipt.store_name, "Test Store")
        self.assertEqual(receipt.receipt_date, date(2024, 1, 15))
        self.assertEqual(receipt.total_amount, Decimal("5.25"))
        self.assertEqual(receipt.upload_timestamp, datetime(2024, 1, 15, 10, 30, 0))
        self.assertEqual(receipt.raw_text, "Raw receipt text")
        self.assertEqual(receipt.image_path, "/path/to/image.jpg")
        self.assertEqual(len(receipt.items), 1)
        self.assertEqual(receipt.items[0].item_name, "Apple")


if __name__ == "__main__":
    unittest.main()
