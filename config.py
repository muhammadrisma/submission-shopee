"""
Configuration management for the Food Receipt Analyzer application.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing application settings."""
    
    # Database configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/receipts.db")
    
    # OpenRouter API configuration
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
    
    # Streamlit configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # File upload configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: list = ["jpg", "jpeg", "png", "pdf"]
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    
    # OCR configuration
    TESSERACT_CMD: Optional[str] = os.getenv("TESSERACT_CMD")  # Path to tesseract executable
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENROUTER_API_KEY:
            print("Warning: OPENROUTER_API_KEY not set. AI query functionality will be limited.")
            return False
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the full database URL/path."""
        return cls.DATABASE_PATH
    
    @classmethod
    def get_upload_path(cls) -> str:
        """Get the upload folder path."""
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        return cls.UPLOAD_FOLDER


# Create a global config instance
config = Config()