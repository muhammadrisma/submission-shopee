"""
Input validation utilities for the Food Receipt Analyzer.
Provides comprehensive validation for file uploads, user inputs, and data integrity.
"""

import mimetypes
import os
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image

try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from utils.error_handling import ErrorSeverity, ValidationError


class FileValidator:
    """Validator for uploaded files."""

    def __init__(
        self,
        max_size_mb: int = 10,
        allowed_extensions: List[str] = None,
        allowed_mime_types: List[str] = None,
    ):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allowed_extensions = allowed_extensions or ["jpg", "jpeg", "png", "pdf"]
        self.allowed_mime_types = allowed_mime_types or [
            "image/jpeg",
            "image/png",
            "image/jpg",
            "application/pdf",
        ]

    def validate_file(self, file_obj, filename: str = None) -> Dict[str, Any]:
        """
        Comprehensive file validation.

        Args:
            file_obj: File object to validate
            filename: Optional filename

        Returns:
            Validation result dictionary

        Raises:
            ValidationError: If validation fails
        """
        filename = filename or getattr(file_obj, "name", "unknown")

        self._validate_file_size(file_obj, filename)

        self._validate_file_extension(filename)

        self._validate_mime_type(file_obj, filename)

        if self._is_image_file(filename):
            self._validate_image_content(file_obj, filename)

        return {
            "valid": True,
            "filename": filename,
            "size_bytes": self._get_file_size(file_obj),
            "extension": self._get_file_extension(filename),
            "mime_type": self._get_mime_type(file_obj),
        }

    def _validate_file_size(self, file_obj, filename: str):
        """Validate file size."""
        size = self._get_file_size(file_obj)

        if size == 0:
            raise ValidationError(
                message=f"File '{filename}' is empty",
                field="file_size",
                user_message="The uploaded file is empty",
                recovery_suggestions=[
                    "Select a different file",
                    "Check that the file is not corrupted",
                ],
            )

        if size > self.max_size_bytes:
            size_mb = size / 1024 / 1024
            max_mb = self.max_size_bytes / 1024 / 1024
            raise ValidationError(
                message=f"File '{filename}' size ({size_mb:.1f}MB) exceeds maximum ({max_mb}MB)",
                field="file_size",
                user_message=f"File size ({size_mb:.1f}MB) is too large",
                recovery_suggestions=[
                    f"Use a file smaller than {max_mb}MB",
                    "Compress the image before uploading",
                    "Try a different image format",
                ],
            )

    def _validate_file_extension(self, filename: str):
        """Validate file extension."""
        extension = self._get_file_extension(filename)

        if not extension:
            raise ValidationError(
                message=f"File '{filename}' has no extension",
                field="file_extension",
                user_message="File must have a valid extension",
                recovery_suggestions=[
                    f"Use files with extensions: {', '.join(self.allowed_extensions)}",
                    "Rename the file with proper extension",
                ],
            )

        if extension not in self.allowed_extensions:
            raise ValidationError(
                message=f"File extension '{extension}' not allowed",
                field="file_extension",
                user_message=f"File type '{extension}' is not supported",
                recovery_suggestions=[
                    f"Use supported file types: {', '.join(self.allowed_extensions)}",
                    "Convert the file to a supported format",
                ],
            )

    def _validate_mime_type(self, file_obj, filename: str):
        """Validate MIME type."""
        mime_type = self._get_mime_type(file_obj)

        if mime_type not in self.allowed_mime_types:
            raise ValidationError(
                message=f"MIME type '{mime_type}' not allowed for file '{filename}'",
                field="mime_type",
                user_message="File type is not supported",
                recovery_suggestions=[
                    "Use a supported image format (JPEG, PNG)",
                    "Check that the file is not corrupted",
                    "Try converting to a different format",
                ],
            )

    def _validate_image_content(self, file_obj, filename: str):
        """Validate image content and integrity."""
        try:
            file_obj.seek(0)

            with Image.open(file_obj) as img:
                img.verify()

                file_obj.seek(0)
                with Image.open(file_obj) as img:
                    width, height = img.size

                    if width < 50 or height < 50:
                        raise ValidationError(
                            message=f"Image '{filename}' is too small ({width}x{height})",
                            field="image_dimensions",
                            user_message="Image is too small for processing",
                            recovery_suggestions=[
                                "Use an image at least 50x50 pixels",
                                "Try a higher resolution image",
                            ],
                        )

                    if width > 10000 or height > 10000:
                        raise ValidationError(
                            message=f"Image '{filename}' is too large ({width}x{height})",
                            field="image_dimensions",
                            user_message="Image resolution is too high",
                            recovery_suggestions=[
                                "Resize the image to a smaller resolution",
                                "Use an image under 10000x10000 pixels",
                            ],
                        )

            file_obj.seek(0)

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                message=f"Invalid image file '{filename}': {str(e)}",
                field="image_content",
                user_message="Image file is corrupted or invalid",
                recovery_suggestions=[
                    "Try a different image file",
                    "Check that the file is not corrupted",
                    "Convert to a standard image format",
                ],
            )

    def _get_file_size(self, file_obj) -> int:
        """Get file size in bytes."""
        if hasattr(file_obj, "size"):
            return file_obj.size

        current_pos = file_obj.tell()
        file_obj.seek(0, 2)
        size = file_obj.tell()
        file_obj.seek(current_pos)
        return size

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase."""
        return os.path.splitext(filename)[1][1:].lower()

    def _get_mime_type(self, file_obj) -> str:
        """Get MIME type of file."""
        try:
            file_obj.seek(0)

            header = file_obj.read(2048)
            file_obj.seek(0)

            if MAGIC_AVAILABLE:
                try:
                    mime_type = magic.from_buffer(header, mime=True)
                    return mime_type
                except Exception:
                    pass

            if hasattr(file_obj, "name"):
                mime_type, _ = mimetypes.guess_type(file_obj.name)
                if mime_type:
                    return mime_type

            if header.startswith(b"\xff\xd8\xff"):
                return "image/jpeg"
            elif header.startswith(b"\x89PNG\r\n\x1a\n"):
                return "image/png"
            elif header.startswith(b"%PDF"):
                return "application/pdf"
            elif header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
                return "image/gif"
            elif header.startswith(b"BM"):
                return "image/bmp"

            return "application/octet-stream"

        except Exception:
            return "application/octet-stream"

    def _is_image_file(self, filename: str) -> bool:
        """Check if file is an image based on extension."""
        extension = self._get_file_extension(filename)
        return extension in ["jpg", "jpeg", "png", "gif", "bmp", "tiff"]


class TextValidator:
    """Validator for text inputs."""

    @staticmethod
    def validate_query(query: str) -> str:
        """
        Validate natural language query input.

        Args:
            query: Query string to validate

        Returns:
            Cleaned query string

        Raises:
            ValidationError: If validation fails
        """
        if not query or not query.strip():
            raise ValidationError(
                message="Query cannot be empty",
                field="query",
                user_message="Please enter a question",
                recovery_suggestions=[
                    "Type a question about your receipts",
                    "Try example queries like 'What did I buy yesterday?'",
                ],
            )

        query = query.strip()

        if len(query) < 3:
            raise ValidationError(
                message="Query too short",
                field="query",
                user_message="Question is too short",
                recovery_suggestions=[
                    "Enter at least 3 characters",
                    "Be more specific in your question",
                ],
            )

        if len(query) > 500:
            raise ValidationError(
                message="Query too long",
                field="query",
                user_message="Question is too long",
                recovery_suggestions=[
                    "Keep questions under 500 characters",
                    "Break down complex questions into simpler ones",
                ],
            )

        suspicious_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"eval\s*\(",
            r"exec\s*\(",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValidationError(
                    message="Query contains suspicious content",
                    field="query",
                    user_message="Invalid characters in question",
                    recovery_suggestions=[
                        "Remove special characters and scripts",
                        "Use plain text questions only",
                    ],
                )

        return query

    @staticmethod
    def validate_store_name(store_name: str) -> str:
        """Validate store name."""
        if not store_name or not store_name.strip():
            raise ValidationError(
                message="Store name cannot be empty",
                field="store_name",
                user_message="Store name is required",
            )

        store_name = store_name.strip()

        if len(store_name) > 100:
            raise ValidationError(
                message="Store name too long",
                field="store_name",
                user_message="Store name must be under 100 characters",
            )

        return store_name

    @staticmethod
    def validate_item_name(item_name: str) -> str:
        """Validate item name."""
        if not item_name or not item_name.strip():
            raise ValidationError(
                message="Item name cannot be empty",
                field="item_name",
                user_message="Item name is required",
            )

        item_name = item_name.strip()

        if len(item_name) > 200:
            raise ValidationError(
                message="Item name too long",
                field="item_name",
                user_message="Item name must be under 200 characters",
            )

        return item_name


class DataValidator:
    """Validator for data integrity and business logic."""

    @staticmethod
    def validate_price(price: Union[str, float, Decimal]) -> Decimal:
        """
        Validate and convert price to Decimal.

        Args:
            price: Price value to validate

        Returns:
            Validated Decimal price

        Raises:
            ValidationError: If validation fails
        """
        try:
            if isinstance(price, str):
                price_str = re.sub(r"[$,\s]", "", price.strip())
                price_decimal = Decimal(price_str)
            else:
                price_decimal = Decimal(str(price))

            if price_decimal < 0:
                raise ValidationError(
                    message="Price cannot be negative",
                    field="price",
                    user_message="Price must be positive",
                    recovery_suggestions=[
                        "Enter a positive price value",
                        "Check for data entry errors",
                    ],
                )

            if price_decimal > Decimal("10000"):
                raise ValidationError(
                    message=f"Price too high: ${price_decimal}",
                    field="price",
                    user_message="Price seems unusually high",
                    recovery_suggestions=[
                        "Check for decimal point errors",
                        "Verify the price is correct",
                    ],
                )

            return price_decimal.quantize(Decimal("0.01"))

        except (InvalidOperation, ValueError) as e:
            raise ValidationError(
                message=f"Invalid price format: {price}",
                field="price",
                user_message="Invalid price format",
                recovery_suggestions=[
                    "Use format like '12.34' or '$12.34'",
                    "Check for typos in the price",
                ],
            )

    @staticmethod
    def validate_quantity(quantity: Union[str, int]) -> int:
        """
        Validate quantity value.

        Args:
            quantity: Quantity to validate

        Returns:
            Validated integer quantity

        Raises:
            ValidationError: If validation fails
        """
        try:
            if isinstance(quantity, str):
                quantity_int = int(quantity.strip())
            else:
                quantity_int = int(quantity)

            if quantity_int <= 0:
                raise ValidationError(
                    message="Quantity must be positive",
                    field="quantity",
                    user_message="Quantity must be at least 1",
                    recovery_suggestions=[
                        "Enter a positive number",
                        "Use whole numbers only",
                    ],
                )

            if quantity_int > 1000:
                raise ValidationError(
                    message=f"Quantity too high: {quantity_int}",
                    field="quantity",
                    user_message="Quantity seems unusually high",
                    recovery_suggestions=[
                        "Check for data entry errors",
                        "Verify the quantity is correct",
                    ],
                )

            return quantity_int

        except (ValueError, TypeError) as e:
            raise ValidationError(
                message=f"Invalid quantity format: {quantity}",
                field="quantity",
                user_message="Invalid quantity format",
                recovery_suggestions=[
                    "Use whole numbers only",
                    "Check for typos in the quantity",
                ],
            )

    @staticmethod
    def validate_date(date_value: Union[str, date, datetime]) -> date:
        """
        Validate and convert date.

        Args:
            date_value: Date to validate

        Returns:
            Validated date object

        Raises:
            ValidationError: If validation fails
        """
        if isinstance(date_value, date):
            result_date = date_value
        elif isinstance(date_value, datetime):
            result_date = date_value.date()
        elif isinstance(date_value, str):
            try:
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        parsed = datetime.strptime(date_value.strip(), fmt)
                        result_date = parsed.date()
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError("No matching date format found")
            except ValueError:
                raise ValidationError(
                    message=f"Invalid date format: {date_value}",
                    field="date",
                    user_message="Invalid date format",
                    recovery_suggestions=[
                        "Use format YYYY-MM-DD (e.g., 2024-01-15)",
                        "Use format MM/DD/YYYY (e.g., 01/15/2024)",
                        "Check for typos in the date",
                    ],
                )
        else:
            raise ValidationError(
                message=f"Invalid date type: {type(date_value)}",
                field="date",
                user_message="Invalid date value",
            )

        today = date.today()
        min_date = date(2000, 1, 1)
        max_date = date(today.year + 1, 12, 31)

        if result_date < min_date:
            raise ValidationError(
                message=f"Date too old: {result_date}",
                field="date",
                user_message="Date is too far in the past",
                recovery_suggestions=[
                    f"Use dates after {min_date}",
                    "Check the year in the date",
                ],
                severity=ErrorSeverity.LOW,
            )

        if result_date > max_date:
            raise ValidationError(
                message=f"Date too far in future: {result_date}",
                field="date",
                user_message="Date is too far in the future",
                recovery_suggestions=[
                    f"Use dates before {max_date}",
                    "Check the year in the date",
                ],
                severity=ErrorSeverity.LOW,
            )

        return result_date


class ReceiptValidator:
    """Validator for receipt data integrity."""

    @staticmethod
    def validate_receipt_data(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete receipt data.

        Args:
            receipt_data: Receipt data dictionary

        Returns:
            Validated receipt data

        Raises:
            ValidationError: If validation fails
        """
        validated_data = {}

        if "store_name" in receipt_data:
            validated_data["store_name"] = TextValidator.validate_store_name(
                receipt_data["store_name"]
            )

        if "receipt_date" in receipt_data:
            validated_data["receipt_date"] = DataValidator.validate_date(
                receipt_data["receipt_date"]
            )

        if "total_amount" in receipt_data:
            validated_data["total_amount"] = DataValidator.validate_price(
                receipt_data["total_amount"]
            )

        if "items" in receipt_data:
            validated_items = []
            for i, item in enumerate(receipt_data["items"]):
                try:
                    validated_item = ReceiptValidator.validate_receipt_item(item)
                    validated_items.append(validated_item)
                except ValidationError as e:
                    e.context = e.context or {}
                    e.context["item_index"] = i
                    raise e

            validated_data["items"] = validated_items

            if "total_amount" in validated_data:
                ReceiptValidator.validate_total_consistency(
                    validated_data["total_amount"], validated_items
                )

        return validated_data

    @staticmethod
    def validate_receipt_item(item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual receipt item."""
        validated_item = {}

        if "item_name" in item_data:
            validated_item["item_name"] = TextValidator.validate_item_name(
                item_data["item_name"]
            )

        if "quantity" in item_data:
            validated_item["quantity"] = DataValidator.validate_quantity(
                item_data["quantity"]
            )

        if "unit_price" in item_data:
            validated_item["unit_price"] = DataValidator.validate_price(
                item_data["unit_price"]
            )

        if "total_price" in item_data:
            validated_item["total_price"] = DataValidator.validate_price(
                item_data["total_price"]
            )

        if all(
            key in validated_item for key in ["quantity", "unit_price", "total_price"]
        ):
            expected_total = validated_item["quantity"] * validated_item["unit_price"]
            actual_total = validated_item["total_price"]

            if abs(expected_total - actual_total) > Decimal("0.02"):
                raise ValidationError(
                    message=f"Price inconsistency: {validated_item['quantity']} × ${validated_item['unit_price']} ≠ ${actual_total}",
                    field="item_price_consistency",
                    user_message="Item price calculation doesn't match",
                    recovery_suggestions=[
                        "Check quantity and unit price",
                        "Verify total price calculation",
                    ],
                )

        return validated_item

    @staticmethod
    def validate_total_consistency(total_amount: Decimal, items: List[Dict[str, Any]]):
        """Validate that receipt total matches sum of items."""
        items_total = sum(item.get("total_price", Decimal("0")) for item in items)

        total_amount = Decimal(str(total_amount))
        items_total = Decimal(str(items_total))

        difference = abs(total_amount - items_total)
        max_difference = max(total_amount * Decimal("0.15"), Decimal("5.00"))

        if difference > max_difference:
            raise ValidationError(
                message=f"Total mismatch: Receipt total ${total_amount} vs items total ${items_total}",
                field="total_consistency",
                user_message="Receipt total doesn't match items sum",
                recovery_suggestions=[
                    "Check if tax or discounts are included",
                    "Verify individual item prices",
                    "This might be normal for receipts with tax",
                ],
                severity=ErrorSeverity.LOW,
            )


file_validator = FileValidator()
text_validator = TextValidator()
data_validator = DataValidator()
receipt_validator = ReceiptValidator()
