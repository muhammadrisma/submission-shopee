"""
Comprehensive error handling utilities for the Food Receipt Analyzer.
Provides centralized error handling, validation, and recovery mechanisms.
"""

import logging
import time
import traceback
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import requests


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification."""

    VALIDATION = "validation"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    OCR = "ocr"
    AI_SERVICE = "ai_service"
    CONFIGURATION = "configuration"
    USER_INPUT = "user_input"


class ApplicationError(Exception):
    """Base application error with enhanced metadata."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.user_message = user_message or message
        self.recovery_suggestions = recovery_suggestions or []
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()


class ValidationError(ApplicationError):
    """Error for validation failures."""

    def __init__(self, message: str, field: str = None, **kwargs):
        # Extract severity if provided, otherwise use default
        severity = kwargs.pop("severity", ErrorSeverity.LOW)

        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=severity,
            **kwargs,
        )
        self.field = field


class NetworkError(ApplicationError):
    """Error for network-related failures."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs,
        )


class FileSystemError(ApplicationError):
    """Error for file system operations."""

    def __init__(self, message: str, file_path: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            **kwargs,
        )
        self.file_path = file_path


class DatabaseError(ApplicationError):
    """Error for database operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs,
        )


class OCRError(ApplicationError):
    """Error for OCR processing."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.OCR,
            severity=ErrorSeverity.MEDIUM,
            **kwargs,
        )


class AIServiceError(ApplicationError):
    """Error for AI service operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AI_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            **kwargs,
        )


class ConfigurationError(ApplicationError):
    """Error for configuration issues."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs,
        )


class ErrorHandler:
    """Centralized error handler with logging and recovery mechanisms."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_counts = {}
        self.last_errors = []
        self.max_error_history = 100

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        log_level: int = logging.ERROR,
    ) -> Dict[str, Any]:
        """
        Handle an error with logging and metadata collection.

        Args:
            error: The exception that occurred
            context: Additional context information
            log_level: Logging level for the error

        Returns:
            Dictionary with error information and recovery suggestions
        """
        # Convert to ApplicationError if needed
        if not isinstance(error, ApplicationError):
            app_error = self._convert_to_application_error(error)
        else:
            app_error = error

        # Add context
        if context:
            app_error.context.update(context)

        # Log the error
        self._log_error(app_error, log_level)

        # Track error statistics
        self._track_error(app_error)

        # Generate response
        return self._generate_error_response(app_error)

    def _convert_to_application_error(self, error: Exception) -> ApplicationError:
        """Convert a generic exception to ApplicationError."""
        error_message = str(error)
        error_type = type(error).__name__

        # Classify error based on type and message
        if isinstance(error, (FileNotFoundError, PermissionError, OSError)):
            return FileSystemError(
                message=f"{error_type}: {error_message}",
                user_message="File system error occurred",
                recovery_suggestions=[
                    "Check if the file exists and is accessible",
                    "Verify file permissions",
                    "Ensure sufficient disk space",
                ],
            )

        elif isinstance(error, (requests.RequestException, ConnectionError)):
            return NetworkError(
                message=f"{error_type}: {error_message}",
                user_message="Network connection error",
                recovery_suggestions=[
                    "Check your internet connection",
                    "Verify API endpoints are accessible",
                    "Try again in a few moments",
                ],
            )

        elif "tesseract" in error_message.lower():
            return OCRError(
                message=f"OCR Error: {error_message}",
                user_message="Text extraction failed",
                recovery_suggestions=[
                    "Ensure Tesseract OCR is installed",
                    "Check image quality and format",
                    "Try with a different image",
                ],
            )

        elif "database" in error_message.lower() or "sqlite" in error_message.lower():
            return DatabaseError(
                message=f"Database Error: {error_message}",
                user_message="Database operation failed",
                recovery_suggestions=[
                    "Check database connection",
                    "Verify database file permissions",
                    "Try restarting the application",
                ],
            )

        else:
            return ApplicationError(
                message=f"{error_type}: {error_message}",
                category=ErrorCategory.USER_INPUT,
                user_message="An unexpected error occurred",
                recovery_suggestions=[
                    "Try the operation again",
                    "Check your input data",
                    "Contact support if the problem persists",
                ],
            )

    def _log_error(self, error: ApplicationError, log_level: int):
        """Log error with appropriate level and context."""
        log_message = f"[{error.category.value.upper()}] {error.message}"

        if error.context:
            log_message += f" | Context: {error.context}"

        self.logger.log(log_level, log_message)

        # Log stack trace for high severity errors
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(f"Stack trace: {traceback.format_exc()}")

    def _track_error(self, error: ApplicationError):
        """Track error statistics for monitoring."""
        error_key = f"{error.category.value}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Keep error history
        self.last_errors.append(
            {
                "timestamp": error.timestamp,
                "category": error.category.value,
                "severity": error.severity.value,
                "message": error.message,
                "error_code": error.error_code,
            }
        )

        # Limit history size
        if len(self.last_errors) > self.max_error_history:
            self.last_errors = self.last_errors[-self.max_error_history :]

    def _generate_error_response(self, error: ApplicationError) -> Dict[str, Any]:
        """Generate a structured error response."""
        return {
            "success": False,
            "error": {
                "message": error.user_message,
                "category": error.category.value,
                "severity": error.severity.value,
                "error_code": error.error_code,
                "recovery_suggestions": error.recovery_suggestions,
                "timestamp": error.timestamp.isoformat(),
                "context": error.context,
            },
            "technical_details": {
                "exception_type": type(error).__name__,
                "original_message": error.message,
            },
        }

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "error_counts": self.error_counts,
            "recent_errors": self.last_errors[-10:],  # Last 10 errors
            "total_errors": sum(self.error_counts.values()),
        }


class RetryMechanism:
    """Retry mechanism for external API calls and unreliable operations."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.logger = logging.getLogger(__name__)

    def retry(
        self, func: Callable, *args, retry_on: tuple = (Exception,), **kwargs
    ) -> Any:
        """
        Retry a function with exponential backoff.

        Args:
            func: Function to retry
            *args: Function arguments
            retry_on: Tuple of exceptions to retry on
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)

            except retry_on as e:
                last_exception = e

                if attempt == self.max_retries:
                    self.logger.error(
                        f"All {self.max_retries} retry attempts failed for {func.__name__}"
                    )
                    raise e

                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                time.sleep(delay)

        # This should never be reached, but just in case
        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff with jitter."""
        delay = min(self.base_delay * (self.exponential_base**attempt), self.max_delay)

        if self.jitter:
            import random

            delay *= 0.5 + random.random() * 0.5  # Add 0-50% jitter

        return delay


def with_error_handling(
    category: ErrorCategory = ErrorCategory.USER_INPUT,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    recovery_suggestions: Optional[List[str]] = None,
):
    """
    Decorator for automatic error handling.

    Args:
        category: Error category
        severity: Error severity
        recovery_suggestions: List of recovery suggestions
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ApplicationError:
                # Re-raise ApplicationErrors as-is
                raise
            except Exception as e:
                # Convert to ApplicationError
                raise ApplicationError(
                    message=f"Error in {func.__name__}: {str(e)}",
                    category=category,
                    severity=severity,
                    recovery_suggestions=recovery_suggestions
                    or [
                        f"Check the input parameters for {func.__name__}",
                        "Try the operation again",
                        "Contact support if the problem persists",
                    ],
                    context={"function": func.__name__, "args": str(args)[:100]},
                )

        return wrapper

    return decorator


def with_retry(
    max_retries: int = 3, retry_on: tuple = (Exception,), base_delay: float = 1.0
):
    """
    Decorator for automatic retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        retry_on: Tuple of exceptions to retry on
        base_delay: Base delay between retries
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_mechanism = RetryMechanism(
                max_retries=max_retries, base_delay=base_delay
            )
            return retry_mechanism.retry(func, *args, retry_on=retry_on, **kwargs)

        return wrapper

    return decorator


# Global error handler instance
error_handler = ErrorHandler()
