#!/usr/bin/env python3
"""
Simple script to run the Food Receipt Analyzer Streamlit application.
"""

import os
import subprocess
import sys

from config import config


def main():
    """Run the Streamlit application."""
    print("🧾 Starting Food Receipt Analyzer...")

    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit is not installed. Please install requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    os.makedirs(config.get_upload_path(), exist_ok=True)

    env = os.environ.copy()
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        (
            config.TESSERACT_CMD.replace("tesseract.exe", "")
            if hasattr(config, "TESSERACT_CMD") and config.TESSERACT_CMD
            else None
        ),
    ]

    for tesseract_path in tesseract_paths:
        if tesseract_path and os.path.exists(tesseract_path):
            current_path = env.get("PATH", "")
            if tesseract_path not in current_path:
                env["PATH"] = f"{tesseract_path};{current_path}"
                print(f"📍 Added Tesseract to PATH: {tesseract_path}")
            break

    try:
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port",
            str(config.STREAMLIT_PORT),
            "--server.address",
            "0.0.0.0",
        ]

        print(f"🚀 Starting server on port {config.STREAMLIT_PORT}")
        print(f"📁 Upload folder: {config.get_upload_path()}")

        if config.OPENROUTER_API_KEY:
            print("✅ AI queries enabled")
        else:
            print("⚠️  AI queries disabled (no API key)")

        subprocess.run(cmd, env=env)

    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
