#!/usr/bin/env python3
"""
Installation diagnostic script for Food Receipt Analyzer.
Checks all dependencies and system requirements.
"""

import sys
import os
import platform
from typing import List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"

def check_dependencies() -> List[Tuple[bool, str]]:
    """Check if all required Python dependencies are installed."""
    dependencies = [
        ('streamlit', 'Streamlit'),
        ('cv2', 'OpenCV'),
        ('pytesseract', 'PyTesseract'),
        ('requests', 'Requests'),
        ('PIL', 'Pillow'),
        ('dotenv', 'Python-dotenv')
    ]
    
    results = []
    for module, name in dependencies:
        try:
            if module == 'cv2':
                import cv2
                version = cv2.__version__
            elif module == 'PIL':
                from PIL import Image
                version = Image.__version__
            elif module == 'dotenv':
                from dotenv import load_dotenv
                import dotenv
                version = getattr(dotenv, '__version__', 'Unknown')
            else:
                mod = __import__(module)
                version = getattr(mod, '__version__', 'Unknown')
            
            results.append((True, f"✅ {name} v{version}"))
        except ImportError:
            results.append((False, f"❌ {name} - Not installed"))
    
    return results

def check_tesseract() -> Tuple[bool, str]:
    """Check if Tesseract OCR is installed and accessible."""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        path = pytesseract.pytesseract.tesseract_cmd
        return True, f"✅ Tesseract OCR v{version} at {path}"
    except Exception as e:
        return False, f"❌ Tesseract OCR - {str(e)}"

def check_config_file() -> Tuple[bool, str]:
    """Check if configuration file exists."""
    if os.path.exists('.env'):
        return True, "✅ .env configuration file found"
    elif os.path.exists('.env.example'):
        return False, "⚠️ .env file missing (found .env.example)"
    else:
        return False, "❌ No configuration files found"

def check_directories() -> List[Tuple[bool, str]]:
    """Check if required directories exist."""
    directories = [
        ('data', 'Database directory'),
        ('uploads', 'Upload directory'),
        ('ui', 'UI components directory'),
        ('services', 'Services directory'),
        ('database', 'Database modules directory'),
        ('models', 'Data models directory')
    ]
    
    results = []
    for dir_path, description in directories:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            results.append((True, f"✅ {description} ({dir_path})"))
        else:
            results.append((False, f"❌ {description} missing ({dir_path})"))
    
    return results

def check_permissions() -> List[Tuple[bool, str]]:
    """Check file system permissions."""
    results = []
    
    # Check if we can create the data directory
    try:
        os.makedirs('data', exist_ok=True)
        results.append((True, "✅ Can create data directory"))
    except Exception as e:
        results.append((False, f"❌ Cannot create data directory: {e}"))
    
    # Check if we can create the uploads directory
    try:
        os.makedirs('uploads', exist_ok=True)
        results.append((True, "✅ Can create uploads directory"))
    except Exception as e:
        results.append((False, f"❌ Cannot create uploads directory: {e}"))
    
    return results

def main():
    """Run all diagnostic checks."""
    print("🧾 Food Receipt Analyzer - Installation Diagnostic")
    print("=" * 60)
    
    # System information
    print(f"\n💻 System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python: {sys.executable}")
    
    # Check Python version
    print(f"\n🐍 Python Version:")
    python_ok, python_msg = check_python_version()
    print(f"   {python_msg}")
    
    # Check dependencies
    print(f"\n📦 Python Dependencies:")
    dep_results = check_dependencies()
    all_deps_ok = True
    for dep_ok, dep_msg in dep_results:
        print(f"   {dep_msg}")
        if not dep_ok:
            all_deps_ok = False
    
    # Check Tesseract
    print(f"\n🔍 OCR Engine:")
    tesseract_ok, tesseract_msg = check_tesseract()
    print(f"   {tesseract_msg}")
    
    # Check configuration
    print(f"\n⚙️ Configuration:")
    config_ok, config_msg = check_config_file()
    print(f"   {config_msg}")
    
    # Check directories
    print(f"\n📁 Project Structure:")
    dir_results = check_directories()
    all_dirs_ok = True
    for dir_ok, dir_msg in dir_results:
        print(f"   {dir_msg}")
        if not dir_ok:
            all_dirs_ok = False
    
    # Check permissions
    print(f"\n🔐 Permissions:")
    perm_results = check_permissions()
    all_perms_ok = True
    for perm_ok, perm_msg in perm_results:
        print(f"   {perm_msg}")
        if not perm_ok:
            all_perms_ok = False
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 Summary:")
    
    issues = []
    if not python_ok:
        issues.append("Python version")
    if not all_deps_ok:
        issues.append("Python dependencies")
    if not tesseract_ok:
        issues.append("Tesseract OCR")
    if not config_ok:
        issues.append("Configuration file")
    if not all_dirs_ok:
        issues.append("Project directories")
    if not all_perms_ok:
        issues.append("File permissions")
    
    if not issues:
        print("🎉 All checks passed! Your installation looks good.")
        print("\n🚀 You can now run the application:")
        print("   python run_app.py")
        print("   or")
        print("   streamlit run app.py")
        return 0
    else:
        print(f"⚠️ Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"   • {issue}")
        
        print(f"\n🔧 Next Steps:")
        if "Python dependencies" in issues:
            print("   1. Install missing dependencies: pip install -r requirements.txt")
        if "Tesseract OCR" in issues:
            print("   2. Install Tesseract OCR (see INSTALLATION.md)")
        if "Configuration file" in issues:
            print("   3. Copy .env.example to .env and configure")
        
        print("   4. Check INSTALLATION.md for detailed instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())