"""
Main Streamlit application for the Food Receipt Analyzer.
Integrates all services and provides the complete user interface.
"""

import streamlit as st
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Configure Streamlit page
st.set_page_config(
    page_title="Food Receipt Analyzer",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import application components
from config import config
from ui.upload_interface import upload_interface
from ui.query_interface import query_interface
from database.service import db_service
from database.connection import db_manager


class FoodReceiptAnalyzerApp:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        """Initialize the application."""
        self.setup_session_state()
        self.setup_database()
    
    def setup_session_state(self):
        """Initialize session state variables."""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'upload'
        
        if 'last_processed_receipt' not in st.session_state:
            st.session_state.last_processed_receipt = None
        
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = False
        
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
    
    def setup_database(self):
        """Initialize database connection and schema."""
        try:
            # Initialize database schema
            db_manager.initialize_database()
            
            if not st.session_state.app_initialized:
                st.session_state.app_initialized = True
                
        except Exception as e:
            st.error(f"❌ Database initialization failed: {str(e)}")
            st.write("Please check your database configuration and try again.")
            
            with st.expander("🔧 Troubleshooting"):
                st.write("**Common solutions:**")
                st.write("1. Check if the data directory exists and is writable")
                st.write("2. Verify DATABASE_PATH in your configuration")
                st.write("3. Ensure you have sufficient disk space")
                st.write(f"**Current database path:** {config.DATABASE_PATH}")
            
            st.stop()
    
    def render_sidebar(self):
        """Render the application sidebar with navigation and stats."""
        with st.sidebar:
            st.title("🧾 Food Receipt Analyzer")
            st.write("Digitize, analyze, and query your food receipts with AI.")
            
            # Navigation
            st.subheader("📍 Navigation")
            
            pages = {
                'upload': '📤 Upload Receipt',
                'query': '🤖 Ask Questions',
                'dashboard': '📊 Dashboard',
                'settings': '⚙️ Settings'
            }
            
            for page_key, page_name in pages.items():
                if st.button(page_name, use_container_width=True, 
                           type="primary" if st.session_state.current_page == page_key else "secondary"):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            st.divider()
            
            # Database statistics
            self.render_sidebar_stats()
            
            st.divider()
            
            # Configuration status
            self.render_config_status()
    
    def render_sidebar_stats(self):
        """Render database statistics in the sidebar."""
        st.subheader("📈 Statistics")
        
        try:
            stats = db_service.get_database_stats()
            
            st.metric("Total Receipts", stats['receipt_count'])
            st.metric("Total Items", stats['item_count'])
            st.metric("Total Spending", f"${stats['total_spending']:.2f}")
            
            if stats['date_range']['earliest'] and stats['date_range']['latest']:
                st.write(f"**Date Range:**")
                st.write(f"From: {stats['date_range']['earliest']}")
                st.write(f"To: {stats['date_range']['latest']}")
            
        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")
    
    def render_config_status(self):
        """Render configuration status in the sidebar."""
        st.subheader("🔧 Configuration")
        
        # Check OpenRouter API key
        if config.OPENROUTER_API_KEY:
            st.success("✅ AI Queries Enabled")
        else:
            st.warning("⚠️ AI Queries Disabled")
            st.caption("Set OPENROUTER_API_KEY in .env")
        
        # Check database
        try:
            db_service.get_database_stats()
            st.success("✅ Database Connected")
        except Exception as e:
            st.error("❌ Database Error")
            st.caption(f"Error: {str(e)[:50]}...")
        
        # Check upload folder
        try:
            upload_path = config.get_upload_path()
            if os.path.exists(upload_path) and os.access(upload_path, os.W_OK):
                st.success("✅ Upload Folder Ready")
            else:
                st.warning("⚠️ Upload Folder Issues")
                st.caption("Check folder permissions")
        except Exception as e:
            st.error("❌ Upload Folder Error")
            st.caption(f"Error: {str(e)[:30]}...")
    
    def render_main_content(self):
        """Render the main content area based on current page."""
        page = st.session_state.current_page
        
        if page == 'upload':
            self.render_upload_page()
        elif page == 'query':
            self.render_query_page()
        elif page == 'dashboard':
            self.render_dashboard_page()
        elif page == 'settings':
            self.render_settings_page()
        else:
            st.error("Unknown page selected")
    
    def render_upload_page(self):
        """Render the receipt upload page."""
        st.title("📤 Upload Receipt")
        
        # Upload interface
        result = upload_interface.render_upload_section()
        
        # Display results if processing was successful
        if result:
            st.session_state.last_processed_receipt = result
            upload_interface.render_extracted_data_display(result)
            
            # Success actions
            st.subheader("🎉 What's Next?")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🤖 Ask Questions About This Receipt", use_container_width=True):
                    st.session_state.current_page = 'query'
                    st.rerun()
            
            with col2:
                if st.button("📊 View Dashboard", use_container_width=True):
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
        
        # Recent receipts section
        self.render_recent_receipts()
    
    def render_query_page(self):
        """Render the natural language query page."""
        st.title("🤖 Ask Questions")
        
        # Query interface
        query_interface.render_query_section()
        
        # Query statistics
        query_interface.render_query_stats()
    
    def render_dashboard_page(self):
        """Render the dashboard page with analytics and insights."""
        st.title("📊 Dashboard")
        
        try:
            stats = db_service.get_database_stats()
            
            if stats['receipt_count'] == 0:
                st.info("📝 No receipts uploaded yet. Upload your first receipt to see analytics!")
                if st.button("📤 Upload Receipt", use_container_width=True):
                    st.session_state.current_page = 'upload'
                    st.rerun()
                return
            
            # Overview metrics
            st.subheader("📈 Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Receipts", stats['receipt_count'])
            
            with col2:
                st.metric("Total Items", stats['item_count'])
            
            with col3:
                st.metric("Total Spending", f"${stats['total_spending']:.2f}")
            
            with col4:
                if stats['receipt_count'] > 0:
                    avg_per_receipt = stats['total_spending'] / stats['receipt_count']
                    st.metric("Avg per Receipt", f"${avg_per_receipt:.2f}")
                else:
                    st.metric("Avg per Receipt", "$0.00")
            
            # Recent activity
            st.subheader("🕒 Recent Activity")
            recent_receipts = db_service.get_all_receipts(limit=5)
            
            if recent_receipts:
                for receipt in recent_receipts:
                    with st.expander(
                        f"🧾 {receipt.store_name} - {receipt.receipt_date} - ${receipt.total_amount:.2f}"
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Store:** {receipt.store_name}")
                            st.write(f"**Date:** {receipt.receipt_date}")
                            st.write(f"**Items:** {len(receipt.items)}")
                            
                            if receipt.items:
                                st.write("**Top Items:**")
                                for item in receipt.items[:3]:
                                    st.write(f"• {item.item_name} - ${item.total_price:.2f}")
                        
                        with col2:
                            st.metric("Total", f"${receipt.total_amount:.2f}")
                            if receipt.upload_timestamp:
                                st.write(f"Uploaded: {receipt.upload_timestamp.strftime('%H:%M')}")
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Upload New Receipt", use_container_width=True):
                    st.session_state.current_page = 'upload'
                    st.rerun()
            
            with col2:
                if st.button("🤖 Ask Questions", use_container_width=True):
                    st.session_state.current_page = 'query'
                    st.rerun()
            
            with col3:
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.rerun()
            
        except Exception as e:
            st.error(f"Error loading dashboard: {str(e)}")
    
    def render_settings_page(self):
        """Render the settings and configuration page."""
        st.title("⚙️ Settings")
        
        # Configuration section
        st.subheader("🔧 Configuration")
        
        # API Configuration
        with st.expander("🤖 AI Query Configuration"):
            st.write("**OpenRouter API Configuration**")
            
            if config.OPENROUTER_API_KEY:
                st.success("✅ API Key is configured")
                st.write(f"**Model:** {config.OPENROUTER_MODEL}")
                st.write(f"**Base URL:** {config.OPENROUTER_BASE_URL}")
            else:
                st.error("❌ API Key not configured")
                st.write("To enable AI queries, add your OpenRouter API key to the .env file:")
                st.code("OPENROUTER_API_KEY=your_api_key_here")
        
        # Database Configuration
        with st.expander("💾 Database Configuration"):
            st.write(f"**Database Path:** {config.DATABASE_PATH}")
            
            try:
                stats = db_service.get_database_stats()
                st.success("✅ Database connection successful")
                st.write(f"**Records:** {stats['receipt_count']} receipts, {stats['item_count']} items")
            except Exception as e:
                st.error(f"❌ Database error: {str(e)}")
        
        # Vector Search Configuration
        with st.expander("🔍 Vector Search Configuration"):
            self._check_vector_search_status()
        
        # File Upload Configuration
        with st.expander("📁 File Upload Configuration"):
            st.write(f"**Upload Folder:** {config.UPLOAD_FOLDER}")
            st.write(f"**Max File Size:** {config.MAX_FILE_SIZE_MB} MB")
            st.write(f"**Allowed Extensions:** {', '.join(config.ALLOWED_EXTENSIONS)}")
            
            if os.path.exists(config.get_upload_path()):
                st.success("✅ Upload folder exists")
            else:
                st.error("❌ Upload folder missing")
        
        # OCR Configuration
        with st.expander("🔍 OCR Configuration (Tesseract)"):
            self._check_tesseract_status()
        
        # System Information
        with st.expander("💻 System Information"):
            self._display_system_info()
        
        # Data Management
        st.subheader("🗂️ Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Database Stats", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear Query History", use_container_width=True):
                if 'query_history' in st.session_state:
                    st.session_state.query_history = []
                    st.success("Query history cleared!")
        
        # Danger Zone
        with st.expander("⚠️ Danger Zone", expanded=False):
            st.warning("These actions cannot be undone!")
            
            if st.button("🗑️ Clear All Data", type="secondary"):
                st.error("This feature is not implemented for safety reasons.")
                st.write("To clear all data, delete the database file manually.")
    
    def render_recent_receipts(self):
        """Render recent receipts section on upload page."""
        st.subheader("📋 Recent Receipts")
        
        try:
            recent_receipts = db_service.get_all_receipts(limit=3)
            
            if not recent_receipts:
                st.info("No receipts uploaded yet.")
                return
            
            for receipt in recent_receipts:
                with st.expander(
                    f"🧾 {receipt.store_name} - {receipt.receipt_date} - ${receipt.total_amount:.2f}"
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Store:** {receipt.store_name}")
                        st.write(f"**Date:** {receipt.receipt_date}")
                        st.write(f"**Items:** {len(receipt.items)}")
                        
                        if receipt.items:
                            items_preview = ", ".join([item.item_name for item in receipt.items[:3]])
                            if len(receipt.items) > 3:
                                items_preview += f" and {len(receipt.items) - 3} more..."
                            st.write(f"**Items:** {items_preview}")
                    
                    with col2:
                        st.metric("Total", f"${receipt.total_amount:.2f}")
        
        except Exception as e:
            st.error(f"Error loading recent receipts: {str(e)}")
    
    def _check_tesseract_status(self):
        """Check and display Tesseract OCR status."""
        try:
            import pytesseract
            
            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            st.success(f"✅ Tesseract OCR installed (v{version})")
            
            # Show Tesseract path
            try:
                tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
                st.write(f"**Path:** {tesseract_cmd}")
            except:
                st.write("**Path:** Using system PATH")
            
        except Exception as e:
            st.error("❌ Tesseract OCR not available")
            st.write(f"**Error:** {str(e)}")
            
            st.write("**To fix this:**")
            st.write("1. Install Tesseract OCR on your system")
            st.write("2. Add it to your system PATH")
            st.write("3. Or set TESSERACT_CMD in your .env file")
            
            if st.button("📖 View Installation Guide"):
                st.info("Check the INSTALLATION.md file for detailed installation instructions.")
    
    def _check_vector_search_status(self):
        """Check and display vector search status."""
        try:
            from services.vector_db import vector_db
            
            stats = vector_db.get_stats()
            
            if stats['vector_count'] > 0:
                st.success(f"✅ Vector search ready ({stats['vector_count']} vectors)")
                st.write(f"**Vocabulary size:** {stats['vocabulary_size']} words")
                
                if st.button("🔄 Rebuild Vector Index"):
                    with st.spinner("Rebuilding vector index..."):
                        vector_db.build_index(force_rebuild=True)
                        st.success("Vector index rebuilt!")
                        st.rerun()
            else:
                st.warning("⚠️ Vector index not built")
                if st.button("🔨 Build Vector Index"):
                    with st.spinner("Building vector index..."):
                        vector_db.build_index()
                        st.success("Vector index built!")
                        st.rerun()
            
            st.write("**Semantic search queries:**")
            st.write("• 'find chicken food'")
            st.write("• 'search for apple'") 
            st.write("• 'similar to burrito'")
            
        except Exception as e:
            st.error(f"❌ Vector search error: {str(e)}")
    
    def _display_system_info(self):
        """Display system information for troubleshooting."""
        import sys
        import platform
        
        st.write(f"**Python Version:** {sys.version}")
        st.write(f"**Platform:** {platform.system()} {platform.release()}")
        st.write(f"**Architecture:** {platform.machine()}")
        
        # Check key dependencies
        dependencies = {
            'streamlit': 'Streamlit',
            'opencv-python': 'OpenCV',
            'pytesseract': 'PyTesseract',
            'requests': 'Requests',
            'PIL': 'Pillow'
        }
        
        st.write("**Dependencies:**")
        for module, name in dependencies.items():
            try:
                if module == 'opencv-python':
                    import cv2
                    version = cv2.__version__
                elif module == 'PIL':
                    from PIL import Image
                    version = Image.__version__
                else:
                    mod = __import__(module)
                    version = getattr(mod, '__version__', 'Unknown')
                
                st.write(f"• {name}: ✅ v{version}")
            except ImportError:
                st.write(f"• {name}: ❌ Not installed")
    
    def render_error_boundary(self, error: Exception):
        """Render error boundary for unhandled exceptions."""
        st.error("🚨 Application Error")
        st.write("An unexpected error occurred:")
        st.exception(error)
        
        if st.button("🔄 Reload Application"):
            st.rerun()
    
    def run(self):
        """Run the main application."""
        try:
            # Render sidebar
            self.render_sidebar()
            
            # Render main content
            self.render_main_content()
            
            # Footer
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.caption("🧾 Food Receipt Analyzer - Powered by AI and Computer Vision")
                st.caption(f"Session ID: {st.session_state.get('session_id', 'unknown')[:8]}...")
            
        except Exception as e:
            self.render_error_boundary(e)


def main():
    """Main application entry point."""
    app = FoodReceiptAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()