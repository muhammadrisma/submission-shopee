"""
Receipt upload interface components for Streamlit.
Handles file upload, validation, progress indicators, and data display.
"""

import os
import shutil
import tempfile
from typing import Any, Dict, Optional

import streamlit as st
from PIL import Image

from config import config
from database.service import db_service
from models.receipt import Receipt, ReceiptItem
from services.computer_vision import ComputerVisionService
from utils.error_handling import (
    DatabaseError,
    ErrorCategory,
    ErrorSeverity,
    FileSystemError,
    OCRError,
    error_handler,
)
from utils.validation import file_validator


class ReceiptUploadInterface:
    """Handles receipt upload interface and processing."""

    def __init__(self):
        """Initialize the upload interface."""
        self.cv_service = ComputerVisionService()
        self.max_file_size = config.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.allowed_extensions = config.ALLOWED_EXTENSIONS

    def render_upload_section(self) -> Optional[Dict[str, Any]]:
        """
        Render the file upload section with validation.
        Returns processed receipt data if successful, None otherwise.
        """
        st.header("📄 Upload Receipt")
        st.write(
            "Upload a food receipt image to extract and analyze your purchase data."
        )

        # File upload widget
        uploaded_file = st.file_uploader(
            "Choose a receipt image",
            type=self.allowed_extensions,
            help=f"Supported formats: {', '.join(self.allowed_extensions).upper()}. Max size: {config.MAX_FILE_SIZE_MB}MB",
        )

        if uploaded_file is not None:
            # Validate file
            validation_result = self._validate_uploaded_file(uploaded_file)

            if not validation_result["valid"]:
                st.error(f"❌ {validation_result['error']}")

                # Show recovery suggestions if available
                if validation_result.get("recovery_suggestions"):
                    with st.expander("💡 How to Fix This"):
                        for suggestion in validation_result["recovery_suggestions"]:
                            st.write(f"• {suggestion}")

                return None

            # Display file info
            self._display_file_info(uploaded_file)

            # Show image preview
            self._display_image_preview(uploaded_file)

            # Process button
            if st.button("🔍 Process Receipt", type="primary"):
                return self._process_uploaded_receipt(uploaded_file)

        return None

    def _validate_uploaded_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Validate the uploaded file for size and format.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            Dictionary with validation result and error message if any
        """
        try:
            # Use comprehensive file validator
            validation_result = file_validator.validate_file(
                uploaded_file, uploaded_file.name
            )
            return {"valid": True, "error": None, "details": validation_result}

        except Exception as e:
            # Handle validation errors
            error_response = error_handler.handle_error(e)
            error_info = error_response["error"]

            return {
                "valid": False,
                "error": error_info["message"],
                "recovery_suggestions": error_info.get("recovery_suggestions", []),
            }

    def _display_file_info(self, uploaded_file):
        """Display information about the uploaded file."""
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("File Name", uploaded_file.name)

        with col2:
            file_size_mb = uploaded_file.size / 1024 / 1024
            st.metric("File Size", f"{file_size_mb:.1f} MB")

        with col3:
            file_type = uploaded_file.name.split(".")[-1].upper()
            st.metric("File Type", file_type)

    def _display_image_preview(self, uploaded_file):
        """Display a preview of the uploaded image."""
        try:
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)

            st.subheader("📷 Image Preview")

            # Resize image for preview if too large
            max_width = 600
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height))

            st.image(image, caption="Receipt Preview", use_column_width=True)

            uploaded_file.seek(0)  # Reset file pointer

        except Exception as e:
            st.warning(f"Could not display image preview: {str(e)}")

    def _process_uploaded_receipt(self, uploaded_file) -> Optional[Dict[str, Any]]:
        """
        Process the uploaded receipt through computer vision pipeline.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            Processed receipt data or None if processing failed
        """
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()

        temp_file_path = None

        try:
            # Step 1: Save uploaded file temporarily
            status_text.text("💾 Saving uploaded file...")
            progress_bar.progress(20)

            temp_file_path = self._save_temp_file(uploaded_file)

            # Step 2: Process with computer vision
            status_text.text("🔍 Extracting text from receipt...")
            progress_bar.progress(40)

            processed_data = self.cv_service.process_receipt(temp_file_path)

            # Step 3: Create receipt object
            status_text.text("📋 Parsing receipt data...")
            progress_bar.progress(60)

            receipt = self._create_receipt_from_data(processed_data, temp_file_path)

            # Step 4: Save to database
            status_text.text("💾 Saving to database...")
            progress_bar.progress(80)

            receipt_id = db_service.save_receipt(receipt)
            receipt.id = receipt_id

            # Step 5: Complete
            status_text.text("✅ Processing complete!")
            progress_bar.progress(100)

            # Clean up temp file
            self._cleanup_temp_file(temp_file_path)
            temp_file_path = None  # Mark as cleaned up

            # Display success message
            success_msg = (
                f"Receipt processed successfully! Extracted {len(receipt.items)} items."
            )
            if processed_data.get("processing_warnings"):
                success_msg += (
                    f" (with {len(processed_data['processing_warnings'])} warnings)"
                )

            st.success(success_msg)

            # Show warnings if any
            if processed_data.get("processing_warnings"):
                with st.expander("⚠️ Processing Warnings"):
                    for warning in processed_data["processing_warnings"]:
                        st.warning(warning)

            return {"receipt": receipt, "processed_data": processed_data}

        except Exception as e:
            # Handle errors with comprehensive error handling
            error_response = error_handler.handle_error(
                e,
                context={
                    "file_name": uploaded_file.name,
                    "file_size": uploaded_file.size,
                },
            )
            error_info = error_response["error"]

            # Display error with category-specific styling
            if error_info["category"] == "ocr":
                st.error(f"🔍 OCR Error: {error_info['message']}")
            elif error_info["category"] == "file_system":
                st.error(f"📁 File Error: {error_info['message']}")
            elif error_info["category"] == "database":
                st.error(f"💾 Database Error: {error_info['message']}")
            else:
                st.error(f"❌ Error: {error_info['message']}")

            # Show recovery suggestions
            if error_info.get("recovery_suggestions"):
                with st.expander("💡 How to Fix This"):
                    for suggestion in error_info["recovery_suggestions"]:
                        st.write(f"• {suggestion}")

            # Show technical details for debugging
            if st.checkbox("Show technical details", key="show_tech_details"):
                with st.expander("🔧 Technical Details"):
                    st.write(f"**Error Category:** {error_info['category']}")
                    st.write(f"**Severity:** {error_info['severity']}")
                    st.write(f"**Timestamp:** {error_info['timestamp']}")
                    if error_response.get("technical_details"):
                        st.json(error_response["technical_details"])

            status_text.text("❌ Processing failed")
            progress_bar.progress(0)

            return None

        finally:
            # Always clean up temp file
            if temp_file_path:
                self._cleanup_temp_file(temp_file_path)

    def _save_temp_file(self, uploaded_file) -> str:
        """Save uploaded file to temporary location for processing."""
        # Create temp file with proper extension
        file_extension = uploaded_file.name.split(".")[-1].lower()
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file_extension}", dir=config.get_upload_path()
        )

        # Copy uploaded file content to temp file
        uploaded_file.seek(0)
        shutil.copyfileobj(uploaded_file, temp_file)
        temp_file.close()

        return temp_file.name

    def _cleanup_temp_file(self, temp_file_path: str):
        """Clean up temporary file."""
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except Exception as e:
            st.warning(f"Could not clean up temporary file: {str(e)}")

    def _create_receipt_from_data(
        self, processed_data: Dict[str, Any], image_path: str
    ) -> Receipt:
        """Create Receipt object from processed computer vision data."""
        # Create receipt items
        items = []
        for item_data in processed_data.get("items", []):
            item = ReceiptItem(
                item_name=item_data["item_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
            )
            items.append(item)

        # Create receipt
        receipt = Receipt(
            store_name=processed_data.get("store_name", "Unknown Store"),
            receipt_date=processed_data.get("receipt_date"),
            total_amount=processed_data.get("total_amount", 0.0),
            raw_text=processed_data.get("raw_text"),
            image_path=image_path,
            items=items,
        )

        return receipt

    def render_extracted_data_display(self, result_data: Dict[str, Any]):
        """
        Display the extracted receipt data in a user-friendly format.

        Args:
            result_data: Dictionary containing receipt and processed data
        """
        if not result_data:
            return

        receipt = result_data["receipt"]

        st.header("📊 Extracted Receipt Data")

        # Receipt summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Store", receipt.store_name)

        with col2:
            st.metric("Date", receipt.receipt_date.strftime("%Y-%m-%d"))

        with col3:
            st.metric("Total Amount", f"${receipt.total_amount:.2f}")

        # Items table
        if receipt.items:
            st.subheader("🛒 Items")

            # Create items data for display
            items_data = []
            for item in receipt.items:
                items_data.append(
                    {
                        "Item": item.item_name,
                        "Quantity": item.quantity,
                        "Unit Price": f"${item.unit_price:.2f}",
                        "Total": f"${item.total_price:.2f}",
                    }
                )

            st.dataframe(items_data, use_container_width=True)

            # Items summary
            total_items = sum(item.quantity for item in receipt.items)
            st.info(
                f"📦 Total items: {total_items} | 🏷️ Unique products: {len(receipt.items)}"
            )
        else:
            st.warning("No items were extracted from the receipt.")

        # Raw text section (collapsible)
        with st.expander("📝 Raw Extracted Text"):
            if receipt.raw_text:
                st.text(receipt.raw_text)
            else:
                st.write("No raw text available.")

        # Data validation warnings
        self._display_validation_warnings(receipt)

    def _display_validation_warnings(self, receipt: Receipt):
        """Display any validation warnings about the extracted data."""
        warnings = []

        # Check total consistency
        if not receipt.validate_total_consistency():
            items_total = receipt.calculate_items_total()
            difference = abs(receipt.total_amount - items_total)
            warnings.append(
                f"⚠️ Total amount mismatch: Receipt total (${receipt.total_amount:.2f}) "
                f"vs items sum (${items_total:.2f}). Difference: ${difference:.2f}"
            )

        # Check for missing data
        if receipt.store_name == "Unknown Store":
            warnings.append("⚠️ Store name could not be determined from the receipt.")

        if not receipt.items:
            warnings.append("⚠️ No items were extracted from the receipt.")

        # Display warnings
        if warnings:
            st.warning("Data Quality Warnings:")
            for warning in warnings:
                st.write(warning)


# Global upload interface instance
upload_interface = ReceiptUploadInterface()
