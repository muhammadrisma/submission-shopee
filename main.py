"""
Main entry point for the Food Receipt Analyzer application.
"""

import streamlit as st
from config import config

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Food Receipt Analyzer",
        page_icon="🧾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧾 Food Receipt Analyzer")
    st.markdown("Upload your food receipts and query your purchase history with natural language!")
    
    # Validate configuration
    if not config.validate_config():
        st.warning("⚠️ Configuration incomplete. Please check your environment variables.")
    
    # Placeholder for main application logic
    st.info("Application structure is set up. Ready for implementation of core features.")


if __name__ == "__main__":
    main()