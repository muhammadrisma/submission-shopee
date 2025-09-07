#!/usr/bin/env python3
"""
Script to run error handling integration tests.
Tests various error scenarios and validates recovery mechanisms.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_pytest_tests():
    """Run pytest tests for error handling."""
    print("🧪 Running error handling tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_error_handling.py",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True, cwd=project_root)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def test_file_validation():
    """Test file validation with various scenarios."""
    print("\n📁 Testing file validation scenarios...")
    
    from utils.validation import file_validator
    from utils.error_handling import ValidationError
    import io
    from PIL import Image
    
    # Test 1: Valid image
    try:
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        img_bytes.name = 'test.jpg'
        img_bytes.size = len(img_bytes.getvalue())
        
        result = file_validator.validate_file(img_bytes, 'test.jpg')
        print("✅ Valid image test passed")
    except Exception as e:
        print(f"❌ Valid image test failed: {e}")
    
    # Test 2: File too large
    try:
        large_file = io.BytesIO(b"x" * (15 * 1024 * 1024))  # 15MB
        large_file.name = 'large.jpg'
        large_file.size = 15 * 1024 * 1024
        
        file_validator.validate_file(large_file, 'large.jpg')
        print("❌ Large file test should have failed")
    except ValidationError as e:
        print("✅ Large file validation correctly failed")
        print(f"   Recovery suggestions: {e.recovery_suggestions}")
    except Exception as e:
        print(f"❌ Large file test failed unexpectedly: {e}")
    
    # Test 3: Invalid extension
    try:
        text_file = io.BytesIO(b"Hello world")
        text_file.name = 'test.txt'
        text_file.size = 11
        
        file_validator.validate_file(text_file, 'test.txt')
        print("❌ Invalid extension test should have failed")
    except ValidationError as e:
        print("✅ Invalid extension validation correctly failed")
        print(f"   Recovery suggestions: {e.recovery_suggestions}")
    except Exception as e:
        print(f"❌ Invalid extension test failed unexpectedly: {e}")

def test_text_validation():
    """Test text validation scenarios."""
    print("\n📝 Testing text validation scenarios...")
    
    from utils.validation import TextValidator
    from utils.error_handling import ValidationError
    
    # Test 1: Valid query
    try:
        result = TextValidator.validate_query("What did I buy yesterday?")
        print("✅ Valid query test passed")
    except Exception as e:
        print(f"❌ Valid query test failed: {e}")
    
    # Test 2: Empty query
    try:
        TextValidator.validate_query("")
        print("❌ Empty query test should have failed")
    except ValidationError as e:
        print("✅ Empty query validation correctly failed")
        print(f"   Recovery suggestions: {e.recovery_suggestions}")
    except Exception as e:
        print(f"❌ Empty query test failed unexpectedly: {e}")
    
    # Test 3: Malicious content
    try:
        TextValidator.validate_query("What did I buy <script>alert('xss')</script>?")
        print("❌ Malicious content test should have failed")
    except ValidationError as e:
        print("✅ Malicious content validation correctly failed")
        print(f"   Recovery suggestions: {e.recovery_suggestions}")
    except Exception as e:
        print(f"❌ Malicious content test failed unexpectedly: {e}")

def test_retry_mechanism():
    """Test retry mechanism."""
    print("\n🔄 Testing retry mechanism...")
    
    from utils.error_handling import RetryMechanism
    import requests
    
    retry_mechanism = RetryMechanism(max_retries=3, base_delay=0.1)
    
    # Test 1: Successful retry
    try:
        call_count = 0
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.exceptions.RequestException("Temporary failure")
            return "success"
        
        result = retry_mechanism.retry(failing_function)
        if result == "success" and call_count == 3:
            print("✅ Successful retry test passed")
        else:
            print(f"❌ Successful retry test failed: result={result}, calls={call_count}")
    except Exception as e:
        print(f"❌ Successful retry test failed: {e}")
    
    # Test 2: Max retries exceeded
    try:
        def always_failing_function():
            raise requests.exceptions.RequestException("Permanent failure")
        
        retry_mechanism.retry(always_failing_function)
        print("❌ Max retries test should have failed")
    except requests.exceptions.RequestException:
        print("✅ Max retries exceeded test passed")
    except Exception as e:
        print(f"❌ Max retries test failed unexpectedly: {e}")

def test_error_handler():
    """Test centralized error handler."""
    print("\n🛠️ Testing error handler...")
    
    from utils.error_handling import ErrorHandler, ValidationError
    
    handler = ErrorHandler()
    
    # Test 1: Handle generic exception
    try:
        error = ValueError("Test error")
        result = handler.handle_error(error)
        
        if not result['success'] and 'error' in result:
            print("✅ Generic exception handling test passed")
        else:
            print(f"❌ Generic exception handling test failed: {result}")
    except Exception as e:
        print(f"❌ Generic exception handling test failed: {e}")
    
    # Test 2: Handle application error
    try:
        error = ValidationError(
            message="Test validation error",
            field="test_field",
            recovery_suggestions=["Fix the input"]
        )
        result = handler.handle_error(error)
        
        if (not result['success'] and 
            result['error']['category'] == 'validation' and
            "Fix the input" in result['error']['recovery_suggestions']):
            print("✅ Application error handling test passed")
        else:
            print(f"❌ Application error handling test failed: {result}")
    except Exception as e:
        print(f"❌ Application error handling test failed: {e}")

def test_ocr_error_scenarios():
    """Test OCR-related error scenarios."""
    print("\n🔍 Testing OCR error scenarios...")
    
    from services.computer_vision import ComputerVisionService
    from utils.error_handling import FileSystemError, OCRError
    
    cv_service = ComputerVisionService()
    
    # Test 1: Missing file
    try:
        cv_service.process_receipt("/nonexistent/path.jpg")
        print("❌ Missing file test should have failed")
    except FileSystemError as e:
        print("✅ Missing file error correctly handled")
        print(f"   Recovery suggestions: {e.recovery_suggestions}")
    except Exception as e:
        print(f"❌ Missing file test failed unexpectedly: {e}")

def main():
    """Run all error handling tests."""
    print("🚀 Starting comprehensive error handling tests...\n")
    
    # Run pytest tests
    pytest_success = run_pytest_tests()
    
    # Run manual integration tests
    test_file_validation()
    test_text_validation()
    test_retry_mechanism()
    test_error_handler()
    test_ocr_error_scenarios()
    
    print("\n" + "="*50)
    if pytest_success:
        print("✅ All pytest tests passed!")
    else:
        print("❌ Some pytest tests failed!")
    
    print("🎯 Manual integration tests completed!")
    print("📋 Check the output above for detailed results.")
    print("\n💡 To run individual test categories:")
    print("   python -m pytest tests/test_error_handling.py::TestFileValidator -v")
    print("   python -m pytest tests/test_error_handling.py::TestRetryMechanism -v")

if __name__ == "__main__":
    main()