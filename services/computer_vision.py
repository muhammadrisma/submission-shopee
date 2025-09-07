"""
Computer Vision Service for Receipt Processing

This module provides image preprocessing, OCR text extraction, and receipt parsing
functionality for the Food Receipt Analyzer application.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime, date
from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Handles image preprocessing for better OCR accuracy."""
    
    @staticmethod
    def preprocess_image(image_path: str) -> np.ndarray:
        """
        Preprocess receipt image for better OCR accuracy.
        
        Args:
            image_path: Path to the receipt image
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = ImagePreprocessor._reduce_noise(gray)
            
            # Enhance contrast
            enhanced = ImagePreprocessor._enhance_contrast(denoised)
            
            # Apply morphological operations to clean up text
            cleaned = ImagePreprocessor._morphological_cleanup(enhanced)
            
            logger.info(f"Successfully preprocessed image: {image_path}")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            raise
    
    @staticmethod
    def _reduce_noise(image: np.ndarray) -> np.ndarray:
        """Apply noise reduction techniques."""
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Apply bilateral filter for edge-preserving smoothing
        filtered = cv2.bilateralFilter(blurred, 9, 75, 75)
        
        return filtered
    
    @staticmethod
    def _enhance_contrast(image: np.ndarray) -> np.ndarray:
        """Enhance image contrast for better text recognition."""
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Apply threshold to create binary image
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    @staticmethod
    def _morphological_cleanup(image: np.ndarray) -> np.ndarray:
        """Apply morphological operations to clean up text."""
        # Create kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        
        # Apply opening to remove small noise
        opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        
        # Apply closing to fill small gaps
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        
        return closed


class OCRService:
    """Handles OCR text extraction from preprocessed images."""
    
    def __init__(self):
        """Initialize OCR service with optimal configuration."""
        # Configure Tesseract for receipt processing
        self.config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,/$-: '
    
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from preprocessed image using OCR.
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            Extracted text as string
        """
        try:
            # Convert numpy array to PIL Image for pytesseract
            pil_image = Image.fromarray(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(pil_image, config=self.config)
            
            # Clean up extracted text
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Successfully extracted text, length: {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean up extracted text by removing excessive whitespace and noise."""
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common OCR artifacts
        cleaned = re.sub(r'[|\\]', '', cleaned)
        
        return cleaned


class ReceiptParser:
    """Parses structured data from OCR-extracted text."""
    
    def __init__(self):
        """Initialize parser with regex patterns for receipt data extraction."""
        # Store name patterns (common receipt headers)
        self.store_patterns = [
            r'(?i)(walmart|target|kroger|safeway|whole foods|costco|trader joe|publix)',
            r'(?i)([A-Z][a-z]+\s+[A-Z][a-z]+)\s*(?:store|market|grocery)',
            r'^([A-Z\s]+)(?:\n|\r)',  # First line in caps
        ]
        
        # Date patterns
        self.date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}',
        ]
        
        # Item and price patterns
        self.item_patterns = [
            r'(\d+)\s+([A-Za-z][A-Za-z\s]+?)\s+(\d+\.\d{2})',  # Quantity, item, price
            r'([A-Za-z][A-Za-z\s]+?)\s+(\d+\.\d{2})',  # Item name followed by price
        ]
        
        # Total patterns (prioritize "Total" over "Subtotal")
        self.total_patterns = [
            r'(?i)(?<!sub)total[:\s]*\$?(\d+\.\d{2})',  # Total but not Subtotal
            r'(?i)amount[:\s]*\$?(\d+\.\d{2})',
            r'(?i)balance[:\s]*\$?(\d+\.\d{2})',
            r'(?i)total[:\s]*\$?(\d+\.\d{2})',  # Fallback to any total
        ]
    
    def parse_receipt(self, text: str) -> Dict:
        """
        Parse receipt text to extract structured data.
        
        Args:
            text: OCR-extracted text from receipt
            
        Returns:
            Dictionary containing parsed receipt data
        """
        try:
            parsed_data = {
                'store_name': self._extract_store_name(text),
                'receipt_date': self._extract_date(text),
                'items': self._extract_items(text),
                'total_amount': self._extract_total(text),
                'raw_text': text
            }
            
            logger.info(f"Successfully parsed receipt: {parsed_data['store_name']}, "
                       f"{len(parsed_data['items'])} items")
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing receipt text: {str(e)}")
            raise
    
    def _extract_store_name(self, text: str) -> Optional[str]:
        """Extract store name from receipt text."""
        lines = text.split('\n')
        
        # Try each store pattern
        for pattern in self.store_patterns:
            for line in lines[:5]:  # Check first 5 lines
                match = re.search(pattern, line.strip())
                if match:
                    store_name = match.group(1).strip()
                    return store_name.title()
        
        # Fallback: use first non-empty line if no pattern matches
        for line in lines[:3]:
            if line.strip() and len(line.strip()) > 3:
                return line.strip().title()
        
        return "Unknown Store"
    
    def _extract_date(self, text: str) -> Optional[date]:
        """Extract receipt date from text."""
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d', 
                               '%m/%d/%y', '%m-%d-%y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt).date()
                            return parsed_date
                        except ValueError:
                            continue
                except Exception:
                    continue
        
        # Fallback to today's date if no date found
        return date.today()
    
    def _extract_items(self, text: str) -> List[Dict]:
        """Extract items and prices from receipt text."""
        items = []
        lines = text.split('\n')
        
        # Words to exclude from items (receipt metadata)
        exclude_words = {
            'subtotal', 'tax', 'total', 'cash', 'change', 'balance', 
            'amount', 'tender', 'credit', 'debit', 'visa', 'mastercard',
            'store', 'manager', 'cashier', 'receipt', 'thank', 'you',
            'phone', 'address', 'street', 'city', 'state', 'zip'
        }
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Skip lines that look like receipt metadata
            line_lower = line.lower()
            if any(exclude_word in line_lower for exclude_word in exclude_words):
                continue
            
            # Skip lines with store numbers, dates, or transaction IDs
            if re.search(r'(st#|op#|te#|tr#|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', line_lower):
                continue
            
            # Try to match item patterns
            for pattern in self.item_patterns:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) == 2:
                        # Item name and price
                        item_name, price_str = match.groups()
                        quantity = 1
                    else:
                        # Quantity, item name, and price
                        quantity_str, item_name, price_str = match.groups()
                        try:
                            quantity = int(quantity_str)
                        except ValueError:
                            quantity = 1
                    
                    # Additional filtering for item names
                    item_name_clean = item_name.strip().lower()
                    if any(exclude_word in item_name_clean for exclude_word in exclude_words):
                        continue
                    
                    # Skip very short item names (likely parsing errors)
                    if len(item_name.strip()) < 3:
                        continue
                    
                    try:
                        price = Decimal(price_str)
                        unit_price = price / quantity if quantity > 0 else price
                        
                        item = {
                            'item_name': item_name.strip().title(),
                            'quantity': quantity,
                            'unit_price': float(unit_price),
                            'total_price': float(price)
                        }
                        items.append(item)
                        break
                    except (ValueError, TypeError):
                        continue
        
        return items
    
    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from receipt text."""
        for pattern in self.total_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    total = float(match.group(1))
                    return total
                except ValueError:
                    continue
        
        # Fallback: sum of all item prices if no total found
        items = self._extract_items(text)
        if items:
            return sum(item['total_price'] for item in items)
        
        return 0.0


class ComputerVisionService:
    """Main service class that orchestrates image processing, OCR, and parsing."""
    
    def __init__(self):
        """Initialize the computer vision service with all components."""
        self.preprocessor = ImagePreprocessor()
        self.ocr_service = OCRService()
        self.parser = ReceiptParser()
    
    def process_receipt(self, image_path: str) -> Dict:
        """
        Process a receipt image end-to-end.
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            Dictionary containing all extracted receipt data
        """
        try:
            logger.info(f"Starting receipt processing for: {image_path}")
            
            # Step 1: Preprocess image
            preprocessed_image = self.preprocessor.preprocess_image(image_path)
            
            # Step 2: Extract text using OCR
            extracted_text = self.ocr_service.extract_text(preprocessed_image)
            
            # Step 3: Parse structured data
            parsed_data = self.parser.parse_receipt(extracted_text)
            
            # Add processing metadata
            parsed_data['image_path'] = image_path
            parsed_data['processing_timestamp'] = datetime.now()
            
            logger.info(f"Successfully processed receipt: {image_path}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error processing receipt {image_path}: {str(e)}")
            raise