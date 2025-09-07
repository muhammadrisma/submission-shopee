"""
Unit tests for Computer Vision Service

Tests OCR accuracy and parsing logic with sample receipts.
"""

import os
import tempfile
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from services.computer_vision import (
    ComputerVisionService,
    ImagePreprocessor,
    OCRService,
    ReceiptParser,
)


class TestImagePreprocessor:
    """Test cases for ImagePreprocessor class."""

    def test_preprocess_image_invalid_path(self):
        """Test preprocessing with invalid image path."""
        with pytest.raises(Exception) as exc_info:
            ImagePreprocessor.preprocess_image("nonexistent.jpg")
        assert "Image file not found" in str(exc_info.value)

    @patch("os.access")
    @patch("os.path.exists")
    @patch("cv2.imread")
    @patch("cv2.cvtColor")
    @patch("services.computer_vision.ImagePreprocessor._reduce_noise")
    @patch("services.computer_vision.ImagePreprocessor._enhance_contrast")
    @patch("services.computer_vision.ImagePreprocessor._morphological_cleanup")
    def test_preprocess_image_success(
        self,
        mock_cleanup,
        mock_enhance,
        mock_reduce,
        mock_cvt,
        mock_imread,
        mock_exists,
        mock_access,
    ):
        """Test successful image preprocessing."""
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_gray = np.zeros((100, 100), dtype=np.uint8)
        mock_processed = np.ones((100, 100), dtype=np.uint8) * 255

        mock_imread.return_value = mock_image
        mock_cvt.return_value = mock_gray
        mock_reduce.return_value = mock_gray
        mock_enhance.return_value = mock_processed
        mock_cleanup.return_value = mock_processed

        result = ImagePreprocessor.preprocess_image("test.jpg")

        assert result is not None
        assert result.shape == (100, 100)
        mock_imread.assert_called_once_with("test.jpg")
        mock_cvt.assert_called_once()
        mock_reduce.assert_called_once()
        mock_enhance.assert_called_once()
        mock_cleanup.assert_called_once()

    def test_reduce_noise(self):
        """Test noise reduction functionality."""
        test_image = np.random.randint(0, 255, (50, 50), dtype=np.uint8)

        result = ImagePreprocessor._reduce_noise(test_image)

        assert result.shape == test_image.shape
        assert result.dtype == np.uint8

    def test_enhance_contrast(self):
        """Test contrast enhancement functionality."""
        test_image = np.full((50, 50), 128, dtype=np.uint8)

        result = ImagePreprocessor._enhance_contrast(test_image)

        assert result.shape == test_image.shape
        assert result.dtype == np.uint8

    def test_morphological_cleanup(self):
        """Test morphological cleanup functionality."""
        test_image = np.random.choice([0, 255], (50, 50)).astype(np.uint8)

        result = ImagePreprocessor._morphological_cleanup(test_image)

        assert result.shape == test_image.shape
        assert result.dtype == np.uint8


class TestOCRService:
    """Test cases for OCRService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ocr_service = OCRService()

    @patch("pytesseract.image_to_string")
    def test_extract_text_success(self, mock_tesseract):
        """Test successful text extraction."""
        mock_tesseract.return_value = "  WALMART  \n  Item 1  $5.99  \n  Total: $5.99  "

        test_image = np.zeros((100, 100), dtype=np.uint8)
        ocr_service = OCRService()

        result = ocr_service.extract_text(test_image)

        assert "WALMART" in result
        assert "Item 1" in result
        assert "$5.99" in result
        mock_tesseract.assert_called_once()

    @patch("pytesseract.image_to_string")
    def test_extract_text_with_artifacts(self, mock_tesseract):
        """Test text extraction with OCR artifacts."""
        mock_tesseract.return_value = "WAL|MART\n\\Item 1   $5.99\n\n\nTotal: $5.99"

        test_image = np.zeros((100, 100), dtype=np.uint8)
        ocr_service = OCRService()

        result = ocr_service.extract_text(test_image)

        assert "|" not in result
        assert "\\" not in result
        assert "WALMART" in result or "WAL MART" in result

    def test_clean_text(self):
        """Test text cleaning functionality."""
        ocr_service = OCRService()
        dirty_text = "  WAL|MART  \n\n\n  Item\\1   $5.99  \n  "

        result = ocr_service._clean_text(dirty_text)

        assert result.startswith("WAL")
        assert result.endswith("$5.99")
        assert "|" not in result
        assert "\\" not in result


class TestReceiptParser:
    """Test cases for ReceiptParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ReceiptParser()

    def test_extract_store_name_walmart(self):
        """Test store name extraction for Walmart."""
        text = "WALMART SUPERCENTER\nStore #1234\nItem 1 $5.99"

        result = self.parser._extract_store_name(text)

        assert result == "Walmart"

    def test_extract_store_name_generic(self):
        """Test store name extraction for generic store."""
        text = "FRESH MARKET\n123 Main St\nItem 1 $5.99"

        result = self.parser._extract_store_name(text)

        assert "Fresh Market" in result

    def test_extract_store_name_fallback(self):
        """Test store name extraction fallback."""
        text = "UNKNOWN STORE NAME\nAddress Line\nItem 1 $5.99"

        result = self.parser._extract_store_name(text)

        assert result == "Unknown Store Name"

    def test_extract_date_various_formats(self):
        """Test date extraction with various formats."""
        test_cases = [
            ("Receipt Date: 12/25/2023", date(2023, 12, 25)),
            ("Date: 2023-12-25", date(2023, 12, 25)),
            ("Dec 25, 2023", None),
            ("12-25-23", date(2023, 12, 25)),
        ]

        for text, expected in test_cases:
            result = self.parser._extract_date(text)
            if expected:
                assert result == expected
            else:
                assert result == date.today()

    def test_extract_items_simple(self):
        """Test item extraction with simple format."""
        text = """WALMART
        CHICKENBURRITO $2.99
        LARGEDRINK $3.49
        DOMESTICBEER $2.50
        Total: $8.98"""

        result = self.parser._extract_items(text)

        assert len(result) >= 2

        for item in result:
            assert "item_name" in item
            assert "quantity" in item
            assert "unit_price" in item
            assert "total_price" in item
            assert item["quantity"] >= 1
            assert item["total_price"] > 0

    def test_extract_items_with_quantity(self):
        """Test item extraction with quantity."""
        text = """STORE
        2 CHICKENBURRITO $4.98
        1 LARGEDRINK $1.50
        Total: $6.48"""

        result = self.parser._extract_items(text)

        assert len(result) >= 1

        for item in result:
            assert "item_name" in item
            assert "quantity" in item
            assert "unit_price" in item
            assert "total_price" in item
            assert item["quantity"] >= 1
            assert item["total_price"] > 0

    def test_extract_total_various_formats(self):
        """Test total extraction with various formats."""
        test_cases = [
            ("Total: $15.99", 15.99),
            ("TOTAL 15.99", 15.99),
            ("Amount: $15.99", 15.99),
            ("Balance: 15.99", 15.99),
        ]

        for text, expected in test_cases:
            result = self.parser._extract_total(text)
            assert result == expected

    def test_parse_receipt_complete(self):
        """Test complete receipt parsing."""
        sample_receipt = """WALMART SUPERCENTER
        Store
        123 Main Street
        Date: 12/25/2023
        
        CHICKENBURRITO $2.99
        LARGEDRINK $3.49
        DOMESTICBEER $2.50
        
        Subtotal: 8.98
        Tax: 0.72
        Total: $9.70"""

        result = self.parser.parse_receipt(sample_receipt)

        assert result["store_name"] == "Walmart"
        assert result["receipt_date"] == date(2023, 12, 25)
        assert 8.0 <= result["total_amount"] <= 10.0
        assert len(result["items"]) >= 1
        assert result["raw_text"] == sample_receipt


class TestComputerVisionService:
    """Test cases for ComputerVisionService integration."""

    @patch("services.computer_vision.ImagePreprocessor.preprocess_image")
    @patch("services.computer_vision.OCRService.extract_text")
    @patch("services.computer_vision.ReceiptParser.parse_receipt")
    @patch("os.path.exists")
    def test_process_receipt_success(
        self, mock_exists, mock_parse, mock_ocr, mock_preprocess
    ):
        """Test successful end-to-end receipt processing."""
        mock_exists.return_value = True
        mock_preprocess.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_ocr.return_value = "WALMART\nItem 1 $5.99\nTotal: $5.99"
        mock_parse.return_value = {
            "store_name": "Walmart",
            "receipt_date": date(2023, 12, 25),
            "items": [
                {
                    "item_name": "Item 1",
                    "quantity": 1,
                    "unit_price": 5.99,
                    "total_price": 5.99,
                }
            ],
            "total_amount": 5.99,
            "raw_text": "WALMART\nItem 1 $5.99\nTotal: $5.99",
        }

        service = ComputerVisionService()
        result = service.process_receipt("test_receipt.jpg")

        assert result["store_name"] == "Walmart"
        assert result["total_amount"] == 5.99
        assert len(result["items"]) == 1
        assert result["image_path"] == "test_receipt.jpg"
        assert "processing_timestamp" in result

        mock_preprocess.assert_called_once_with("test_receipt.jpg")
        mock_ocr.assert_called_once()
        mock_parse.assert_called_once()

    @patch("services.computer_vision.ImagePreprocessor.preprocess_image")
    @patch("os.path.exists")
    def test_process_receipt_preprocessing_error(self, mock_exists, mock_preprocess):
        """Test receipt processing with preprocessing error."""
        mock_exists.return_value = False

        service = ComputerVisionService()

        with pytest.raises(Exception) as exc_info:
            service.process_receipt("nonexistent.jpg")

        assert "Image file not found" in str(exc_info.value)


class TestIntegrationWithSampleData:
    """Integration tests using sample receipt data."""

    def test_parser_with_realistic_receipt_text(self):
        """Test parser with realistic OCR output."""
        realistic_ocr_text = """WAL*MART SUPERCENTER
        Store
        123 MAIN ST ANYTOWN ST 12345
        ST
        
        CHICKENBURRITO $3.48
        LARGEDRINK $2.18
        DOMESTICBEER $1.98
        KIDSMEAL-MAKEOWN $2.78
        
        SUBTOTAL                10.42
        TAX                      0.83
        TOTAL                   11.25
        
        CASH                    15.00
        CHANGE                   3.75
        
        12/25/2023 14:32:15"""

        parser = ReceiptParser()
        result = parser.parse_receipt(realistic_ocr_text)

        assert result["store_name"] is not None
        assert result["receipt_date"] is not None
        assert result["total_amount"] is not None
        assert isinstance(result["items"], list)

        assert len(result["items"]) >= 1

        assert 10.0 <= result["total_amount"] <= 12.0


if __name__ == "__main__":
    pytest.main([__file__])
