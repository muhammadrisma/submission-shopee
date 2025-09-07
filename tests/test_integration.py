#!/usr/bin/env python3
"""
Integration test script to verify all components work together.
"""

import os
import sys
from datetime import date
from decimal import Decimal


def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")

    try:
        from config import config

        print("✅ Config imported")

        from database.connection import db_manager
        from database.service import db_service

        print("✅ Database services imported")

        from models.receipt import Receipt, ReceiptItem

        print("✅ Models imported")

        from services.computer_vision import ComputerVisionService

        print("✅ Computer vision service imported")

        from services.ai_query import get_ai_query_service

        print("✅ AI query service imported")

        from ui.query_interface import query_interface
        from ui.upload_interface import upload_interface

        print("✅ UI components imported")

        from app import FoodReceiptAnalyzerApp

        print("✅ Main app imported")

        assert True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        assert False, f"Import error: {e}"


def test_database():
    """Test database initialization and basic operations."""
    print("\n🔍 Testing database...")

    try:
        from database.connection import db_manager
        from database.service import db_service
        from models.receipt import Receipt, ReceiptItem

        db_manager.initialize_database()
        print("✅ Database initialized")

        stats = db_service.get_database_stats()
        print(f"✅ Database stats: {stats['receipt_count']} receipts")

        assert True

    except Exception as e:
        print(f"❌ Database error: {e}")
        assert False, f"Database error: {e}"


def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")

    try:
        from config import config

        print(f"✅ Database path: {config.DATABASE_PATH}")
        print(f"✅ Upload folder: {config.UPLOAD_FOLDER}")
        print(f"✅ Max file size: {config.MAX_FILE_SIZE_MB}MB")

        if config.OPENROUTER_API_KEY:
            print("✅ OpenRouter API key configured")
        else:
            print("⚠️ OpenRouter API key not configured")

        assert True

    except Exception as e:
        print(f"❌ Config error: {e}")
        assert False, f"Config error: {e}"


def test_services():
    """Test service initialization."""
    print("\n🔍 Testing services...")

    try:
        from services.computer_vision import ComputerVisionService

        cv_service = ComputerVisionService()
        print("✅ Computer vision service initialized")

        from services.ai_query import get_ai_query_service

        ai_service = get_ai_query_service()
        if ai_service:
            print("✅ AI query service initialized")
        else:
            print("⚠️ AI query service not available (no API key)")

        assert True

    except Exception as e:
        print(f"❌ Service error: {e}")
        assert False, f"Service error: {e}"


def test_ui_components():
    """Test UI component initialization."""
    print("\n🔍 Testing UI components...")

    try:
        from ui.upload_interface import upload_interface

        print("✅ Upload interface initialized")

        from ui.query_interface import query_interface

        print("✅ Query interface initialized")

        assert True

    except Exception as e:
        print(f"❌ UI component error: {e}")
        assert False, f"UI component error: {e}"


def main():
    """Run all integration tests."""
    print("🧾 Food Receipt Analyzer - Integration Test")
    print("=" * 50)

    tests = [
        test_imports,
        test_config,
        test_database,
        test_services,
        test_ui_components,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n🚀 Ready to run the application:")
        print("   python run_app.py")
        print("   or")
        print("   streamlit run app.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
