"""
Integration tests for error handling scenarios in the Food Receipt Analyzer.
Tests various error conditions and recovery mechanisms.
"""

import io
import os
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from PIL import Image

from services.ai_query import AIQueryService, OpenRouterClient
from services.computer_vision import ComputerVisionService
from ui.upload_interface import ReceiptUploadInterface
from utils.error_handling import (
    AIServiceError,
    ApplicationError,
    ConfigurationError,
    ErrorCategory,
    ErrorHandler,
    ErrorSeverity,
    FileSystemError,
    NetworkError,
    OCRError,
    RetryMechanism,
    ValidationError,
)
from utils.validation import (
    DataValidator,
    FileValidator,
    ReceiptValidator,
    TextValidator,
)


class TestErrorHandler:
    """Test the centralized error handler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.error_handler = ErrorHandler()

    def test_handle_generic_exception(self):
        """Test handling of generic exceptions."""
        error = ValueError("Test error")
        result = self.error_handler.handle_error(error)

        assert not result["success"]
        assert "error" in result
        assert result["error"]["category"] == "user_input"
        assert "recovery_suggestions" in result["error"]

    def test_handle_application_error(self):
        """Test handling of ApplicationError instances."""
        error = ValidationError(
            message="Test validation error",
            field="test_field",
            recovery_suggestions=["Fix the input"],
        )
        result = self.error_handler.handle_error(error)

        assert not result["success"]
        assert result["error"]["category"] == "validation"
        assert "Fix the input" in result["error"]["recovery_suggestions"]

    def test_error_statistics_tracking(self):
        """Test error statistics tracking."""
        self.error_handler.handle_error(ValueError("Error 1"))
        self.error_handler.handle_error(ValidationError("Error 2", "field"))
        self.error_handler.handle_error(ValueError("Error 3"))

        stats = self.error_handler.get_error_statistics()

        assert stats["total_errors"] == 3
        assert len(stats["recent_errors"]) == 3
        assert stats["total_errors"] > 0
        assert len(stats["error_counts"]) > 0


class TestRetryMechanism:
    """Test the retry mechanism."""

    def setup_method(self):
        """Set up test fixtures."""
        self.retry_mechanism = RetryMechanism(max_retries=3, base_delay=0.1)

    def test_successful_retry(self):
        """Test successful operation after retries."""
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.exceptions.RequestException("Temporary failure")
            return "success"

        result = self.retry_mechanism.retry(failing_function)

        assert result == "success"
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""

        def always_failing_function():
            raise requests.exceptions.RequestException("Permanent failure")

        with pytest.raises(requests.exceptions.RequestException):
            self.retry_mechanism.retry(always_failing_function)

    def test_no_retry_on_different_exception(self):
        """Test that retries don't happen for non-specified exceptions."""
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Different error")

        with pytest.raises(ValueError):
            self.retry_mechanism.retry(
                failing_function, retry_on=(requests.exceptions.RequestException,)
            )

        assert call_count == 1


class TestFileValidator:
    """Test file validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = FileValidator(max_size_mb=1, allowed_extensions=["jpg", "png"])

    def test_valid_image_file(self):
        """Test validation of a valid image file."""
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        img_bytes.name = "test.jpg"
        img_bytes.size = len(img_bytes.getvalue())

        result = self.validator.validate_file(img_bytes, "test.jpg")

        assert result["valid"]
        assert result["filename"] == "test.jpg"
        assert result["extension"] == "jpg"

    def test_file_too_large(self):
        """Test validation failure for oversized files."""
        mock_file = Mock()
        mock_file.size = 2 * 1024 * 1024
        mock_file.name = "large.jpg"

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_file(mock_file, "large.jpg")

        assert "size" in str(exc_info.value).lower()
        assert "recovery_suggestions" in exc_info.value.__dict__

    def test_invalid_extension(self):
        """Test validation failure for invalid file extensions."""
        mock_file = Mock()
        mock_file.size = 1000
        mock_file.name = "test.txt"

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_file(mock_file, "test.txt")

        assert "extension" in str(exc_info.value).lower()

    def test_empty_file(self):
        """Test validation failure for empty files."""
        mock_file = Mock()
        mock_file.size = 0
        mock_file.name = "empty.jpg"

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_file(mock_file, "empty.jpg")

        assert "empty" in str(exc_info.value).lower()


class TestTextValidator:
    """Test text validation functionality."""

    def test_valid_query(self):
        """Test validation of valid queries."""
        query = "What did I buy yesterday?"
        result = TextValidator.validate_query(query)

        assert result == query

    def test_empty_query(self):
        """Test validation failure for empty queries."""
        with pytest.raises(ValidationError) as exc_info:
            TextValidator.validate_query("")

        assert "empty" in str(exc_info.value).lower()

    def test_query_too_short(self):
        """Test validation failure for very short queries."""
        with pytest.raises(ValidationError) as exc_info:
            TextValidator.validate_query("hi")

        assert "short" in str(exc_info.value).lower()

    def test_query_too_long(self):
        """Test validation failure for very long queries."""
        long_query = "a" * 501

        with pytest.raises(ValidationError) as exc_info:
            TextValidator.validate_query(long_query)

        assert "long" in str(exc_info.value).lower()

    def test_suspicious_content(self):
        """Test validation failure for suspicious content."""
        malicious_query = "What did I buy <script>alert('xss')</script>?"

        with pytest.raises(ValidationError) as exc_info:
            TextValidator.validate_query(malicious_query)

        assert "suspicious" in str(exc_info.value).lower()


class TestDataValidator:
    """Test data validation functionality."""

    def test_valid_price(self):
        """Test validation of valid prices."""
        from decimal import Decimal

        assert DataValidator.validate_price("12.34") == Decimal("12.34")
        assert DataValidator.validate_price("$15.99") == Decimal("15.99")
        assert DataValidator.validate_price(10.5) == Decimal("10.50")

    def test_negative_price(self):
        """Test validation failure for negative prices."""
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_price("-5.00")

        assert "negative" in str(exc_info.value).lower()

    def test_invalid_price_format(self):
        """Test validation failure for invalid price formats."""
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_price("not_a_price")

        assert "format" in str(exc_info.value).lower()

    def test_valid_quantity(self):
        """Test validation of valid quantities."""
        assert DataValidator.validate_quantity("5") == 5
        assert DataValidator.validate_quantity(3) == 3

    def test_zero_quantity(self):
        """Test validation failure for zero quantity."""
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_quantity(0)

        assert "positive" in str(exc_info.value).lower()


class TestComputerVisionErrorHandling:
    """Test error handling in computer vision service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cv_service = ComputerVisionService()

    def test_missing_image_file(self):
        """Test handling of missing image files."""
        with pytest.raises(FileSystemError) as exc_info:
            self.cv_service.process_receipt("/nonexistent/path.jpg")

        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.recovery_suggestions

    @patch("cv2.imread")
    def test_corrupted_image_file(self, mock_imread):
        """Test handling of corrupted image files."""
        mock_imread.return_value = None

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"fake image data")
            temp_path = temp_file.name

        try:
            with pytest.raises(OCRError) as exc_info:
                self.cv_service.process_receipt(temp_path)

            assert "corrupted" in str(exc_info.value.user_message).lower()
        finally:
            os.unlink(temp_path)

    @patch("pytesseract.get_tesseract_version")
    def test_tesseract_not_found(self, mock_version):
        """Test handling when Tesseract is not installed."""
        from pytesseract import TesseractNotFoundError

        mock_version.side_effect = TesseractNotFoundError()

        img = Image.new("RGB", (100, 100), color="white")
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            img.save(temp_file.name, "JPEG")
            temp_path = temp_file.name

        try:
            with pytest.raises(OCRError) as exc_info:
                self.cv_service.process_receipt(temp_path)

            assert "ocr" in str(exc_info.value.user_message).lower()
            assert "install" in str(exc_info.value.recovery_suggestions[0]).lower()
        finally:
            os.unlink(temp_path)


class TestAIServiceErrorHandling:
    """Test error handling in AI service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = OpenRouterClient("test_key")

    @patch("requests.post")
    def test_network_timeout(self, mock_post):
        """Test handling of network timeouts."""
        mock_post.side_effect = requests.exceptions.Timeout()

        with pytest.raises(NetworkError) as exc_info:
            self.client.chat_completion([{"role": "user", "content": "test"}])

        assert "timed out" in str(exc_info.value.user_message).lower()

    @patch("requests.post")
    def test_api_authentication_error(self, mock_post):
        """Test handling of API authentication errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        with pytest.raises(AIServiceError) as exc_info:
            self.client.chat_completion([{"role": "user", "content": "test"}])

        assert "authentication" in str(exc_info.value.user_message).lower()

    @patch("requests.post")
    def test_rate_limit_error(self, mock_post):
        """Test handling of rate limit errors."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        with pytest.raises(AIServiceError) as exc_info:
            self.client.chat_completion([{"role": "user", "content": "test"}])

        assert "requests" in str(exc_info.value.user_message).lower()

    def test_missing_api_key(self):
        """Test handling of missing API key."""
        client = OpenRouterClient("")

        with pytest.raises(ConfigurationError) as exc_info:
            client.chat_completion([{"role": "user", "content": "test"}])

        assert "not configured" in str(exc_info.value.user_message).lower()


class TestUploadInterfaceErrorHandling:
    """Test error handling in upload interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.upload_interface = ReceiptUploadInterface()

    def test_file_validation_error(self):
        """Test handling of file validation errors."""
        mock_file = Mock()
        mock_file.size = 20 * 1024 * 1024
        mock_file.name = "large.jpg"

        result = self.upload_interface._validate_uploaded_file(mock_file)

        assert not result["valid"]
        assert "error" in result
        assert "recovery_suggestions" in result

    @patch("services.computer_vision.ComputerVisionService.process_receipt")
    def test_ocr_processing_error(self, mock_process):
        """Test handling of OCR processing errors."""
        mock_process.side_effect = OCRError(
            message="OCR failed",
            user_message="Could not extract text",
            recovery_suggestions=["Try a clearer image"],
        )

        assert mock_process.side_effect.user_message == "Could not extract text"
        assert "Try a clearer image" in mock_process.side_effect.recovery_suggestions


class TestReceiptValidator:
    """Test receipt data validation."""

    def test_valid_receipt_data(self):
        """Test validation of valid receipt data."""
        receipt_data = {
            "store_name": "Test Store",
            "receipt_date": "2024-01-15",
            "total_amount": "22.00",
            "items": [
                {
                    "item_name": "Test Item",
                    "quantity": 2,
                    "unit_price": "10.00",
                    "total_price": "20.00",
                }
            ],
        }

        result = ReceiptValidator.validate_receipt_data(receipt_data)

        assert result["store_name"] == "Test Store"
        assert len(result["items"]) == 1

    def test_price_inconsistency(self):
        """Test detection of price inconsistencies."""
        item_data = {
            "item_name": "Test Item",
            "quantity": 2,
            "unit_price": "10.00",
            "total_price": "25.00",
        }

        with pytest.raises(ValidationError) as exc_info:
            ReceiptValidator.validate_receipt_item(item_data)

        assert "inconsistency" in str(exc_info.value).lower()

    def test_total_mismatch_warning(self):
        """Test handling of total amount mismatches."""
        from decimal import Decimal

        items = [{"total_price": Decimal("10.00")}, {"total_price": Decimal("15.00")}]

        with pytest.raises(ValidationError) as exc_info:
            ReceiptValidator.validate_total_consistency(50.00, items)

        assert exc_info.value.severity == ErrorSeverity.LOW


if __name__ == "__main__":
    pytest.main([__file__])
