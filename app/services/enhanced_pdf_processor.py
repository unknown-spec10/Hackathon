"""
Enhanced PDF Processor with OCR capabilities
Follows the comprehensive pipeline: PDFPlumber + PyMuPDF + Tesseract OCR
"""

import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import re
import base64
from io import BytesIO
import logging
from pathlib import Path
import cv2
import numpy as np
import tempfile
import os

logger = logging.getLogger(__name__)


class EnhancedPDFProcessor:
    """
    Comprehensive PDF processor using multiple libraries for maximum extraction
    Pipeline: PDFPlumber (text/tables) + PyMuPDF (images) + Tesseract (OCR)
    """
    
    def __init__(self, tesseract_path: str = None):
        self.supported_formats = ['.pdf']
        
        # Configure Tesseract path if provided
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # OCR configuration for better accuracy
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%^&*()_+-=[]{}|;:\'\"<>/\\ '
    
    def extract_complete_resume_data(self, file_path: str) -> Dict[str, Any]:
        """
        Complete pipeline for resume data extraction
        Returns comprehensive data structure with text, tables, and OCR results
        """
        try:
            extracted_data = {
                "text": "",
                "tables": [],
                "images": [],
                "ocr_text": "",
                "image_analysis": [],
                "metadata": {},
                "pages": [],
                "structure": {
                    "has_tables": False,
                    "has_images": False,
                    "has_ocr_content": False,
                    "page_count": 0,
                    "text_density": 0.0,
                    "image_count": 0
                },
                "extraction_sources": {
                    "pdfplumber_text": "",
                    "pdfplumber_tables": [],
                    "pymupdf_images": [],
                    "ocr_results": []
                }
            }
            
            # Step 1: Extract text and tables using PDFPlumber
            logger.info("Step 1: Extracting text and tables with PDFPlumber")
            plumber_data = self._extract_with_pdfplumber(file_path)
            extracted_data.update(plumber_data)
            
            # Step 2: Extract images using PyMuPDF
            logger.info("Step 2: Extracting images with PyMuPDF")
            image_data = self._extract_images_with_pymupdf(file_path)
            extracted_data["images"].extend(image_data["images"])
            extracted_data["image_analysis"] = image_data["analysis"]
            
            # Step 3: Process images with OCR
            logger.info("Step 3: Processing images with OCR")
            ocr_results = self._process_images_with_ocr(image_data["images"])
            extracted_data["ocr_text"] = ocr_results["combined_text"]
            extracted_data["extraction_sources"]["ocr_results"] = ocr_results["individual_results"]
            
            # Step 4: Integrate and analyze all data
            logger.info("Step 4: Integrating and analyzing combined data")
            integrated_data = self._integrate_all_sources(extracted_data)
            extracted_data.update(integrated_data)
            
            # Update structure information
            extracted_data["structure"]["has_ocr_content"] = bool(extracted_data["ocr_text"].strip())
            extracted_data["structure"]["image_count"] = len(extracted_data["images"])
            
            logger.info(f"Extraction complete. Found {extracted_data['structure']['page_count']} pages, "
                       f"{len(extracted_data['tables'])} tables, {len(extracted_data['images'])} images")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in complete extraction pipeline: {e}")
            raise Exception(f"Failed to process PDF with enhanced pipeline: {str(e)}")
    
    def _extract_with_pdfplumber(self, file_path: str) -> Dict[str, Any]:
        """Step 1: Extract text and tables using PDFPlumber"""
        data = {
            "text": "",
            "tables": [],
            "metadata": {},
            "pages": [],
            "structure": {
                "has_tables": False,
                "page_count": 0,
                "text_density": 0.0
            }
        }
        
        with pdfplumber.open(file_path) as pdf:
            # Extract metadata
            data["metadata"] = {
                "pages": len(pdf.pages),
                "title": pdf.metadata.get('Title', ''),
                "author": pdf.metadata.get('Author', ''),
                "creator": pdf.metadata.get('Creator', ''),
                "producer": pdf.metadata.get('Producer', ''),
                "creation_date": str(pdf.metadata.get('CreationDate', '')),
                "modification_date": str(pdf.metadata.get('ModDate', ''))
            }
            
            data["structure"]["page_count"] = len(pdf.pages)
            total_text_length = 0
            
            # Process each page
            for page_num, page in enumerate(pdf.pages):
                page_data = self._process_page_with_pdfplumber(page, page_num + 1)
                data["pages"].append(page_data)
                
                # Accumulate text
                if page_data["text"]:
                    data["text"] += f"\n--- Page {page_num + 1} ---\n{page_data['text']}"
                    total_text_length += len(page_data["text"])
                
                # Accumulate tables
                if page_data["tables"]:
                    data["tables"].extend(page_data["tables"])
                    data["structure"]["has_tables"] = True
            
            # Calculate text density
            if data["structure"]["page_count"] > 0:
                data["structure"]["text_density"] = total_text_length / data["structure"]["page_count"]
            
            # Clean text
            data["text"] = self._clean_extracted_text(data["text"])
            data["extraction_sources"] = {
                "pdfplumber_text": data["text"],
                "pdfplumber_tables": data["tables"]
            }
        
        return data
    
    def _process_page_with_pdfplumber(self, page, page_num: int) -> Dict[str, Any]:
        """Process individual page with PDFPlumber"""
        page_data = {
            "page_number": page_num,
            "text": "",
            "tables": [],
            "bbox": page.bbox if hasattr(page, 'bbox') else None
        }
        
        try:
            # Extract text
            page_text = page.extract_text()
            if page_text:
                page_data["text"] = page_text
            
            # Extract tables with enhanced processing
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if table and len(table) > 0:
                    cleaned_table = self._clean_table_data(table)
                    if cleaned_table:
                        table_data = {
                            "page": page_num,
                            "table_index": table_idx,
                            "raw_data": cleaned_table,
                            "headers": cleaned_table[0] if cleaned_table else [],
                            "rows": cleaned_table[1:] if len(cleaned_table) > 1 else [],
                            "row_count": len(cleaned_table) - 1 if len(cleaned_table) > 1 else 0,
                            "column_count": len(cleaned_table[0]) if cleaned_table and cleaned_table[0] else 0
                        }
                        
                        # Convert to DataFrame for easier processing
                        if table_data["headers"] and table_data["rows"]:
                            try:
                                df = pd.DataFrame(table_data["rows"], columns=table_data["headers"])
                                table_data["dataframe_dict"] = df.to_dict('records')
                                table_data["table_text"] = self._table_to_text(cleaned_table)
                            except Exception as e:
                                logger.warning(f"Could not convert table to DataFrame: {e}")
                        
                        page_data["tables"].append(table_data)
        
        except Exception as e:
            logger.warning(f"Error processing page {page_num} with PDFPlumber: {e}")
        
        return page_data
    
    def _extract_images_with_pymupdf(self, file_path: str) -> Dict[str, Any]:
        """Step 2: Extract images using PyMuPDF"""
        images_data = {
            "images": [],
            "analysis": []
        }
        
        try:
            pdf_document = fitz.open(file_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Extract image
                        xref = img[0]
                        pix = fitz.Pixmap(pdf_document, xref)
                        
                        # Convert to PIL Image
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("ppm")
                            img_pil = Image.open(BytesIO(img_data))
                        else:  # CMYK: convert to RGB first
                            pix1 = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix1.tobytes("ppm")
                            img_pil = Image.open(BytesIO(img_data))
                            pix1 = None
                        
                        pix = None
                        
                        # Analyze image properties
                        image_info = {
                            "page": page_num + 1,
                            "image_index": img_index,
                            "width": img_pil.width,
                            "height": img_pil.height,
                            "format": img_pil.format,
                            "mode": img_pil.mode,
                            "size_bytes": len(img_data),
                            "pil_image": img_pil,
                            "bbox": img[1:5] if len(img) > 4 else None,
                            "analysis": self._analyze_image_content(img_pil)
                        }
                        
                        images_data["images"].append(image_info)
                        images_data["analysis"].append({
                            "page": page_num + 1,
                            "index": img_index,
                            "type": image_info["analysis"]["type"],
                            "likely_content": image_info["analysis"]["content_type"]
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error extracting image {img_index} from page {page_num + 1}: {e}")
            
            pdf_document.close()
            
        except Exception as e:
            logger.error(f"Error extracting images with PyMuPDF: {e}")
        
        return images_data
    
    def _process_images_with_ocr(self, images: List[Dict]) -> Dict[str, Any]:
        """Step 3: Process images with OCR"""
        ocr_results = {
            "combined_text": "",
            "individual_results": []
        }
        
        for image_info in images:
            try:
                pil_image = image_info["pil_image"]
                
                # Preprocess image for better OCR
                processed_image = self._preprocess_image_for_ocr(pil_image)
                
                # Perform OCR
                ocr_text = pytesseract.image_to_string(processed_image, config=self.ocr_config)
                
                if ocr_text.strip():
                    # Analyze what type of content this might be
                    content_analysis = self._analyze_ocr_content(ocr_text, image_info["analysis"])
                    
                    result = {
                        "page": image_info["page"],
                        "image_index": image_info["image_index"],
                        "raw_text": ocr_text,
                        "cleaned_text": self._clean_ocr_text(ocr_text),
                        "content_type": content_analysis["type"],
                        "confidence": content_analysis["confidence"],
                        "extracted_elements": content_analysis["elements"]
                    }
                    
                    ocr_results["individual_results"].append(result)
                    ocr_results["combined_text"] += f"\n--- OCR from Page {image_info['page']} Image {image_info['image_index']} ---\n{result['cleaned_text']}"
                
            except Exception as e:
                logger.warning(f"Error performing OCR on image from page {image_info['page']}: {e}")
        
        return ocr_results
    
    def _integrate_all_sources(self, extracted_data: Dict) -> Dict[str, Any]:
        """Step 4: Integrate all extraction sources"""
        integrated = {
            "combined_text": "",
            "structured_data": {
                "personal_info": {},
                "skills": [],
                "experience": [],
                "education": [],
                "certifications": []
            },
            "data_sources": {
                "primary_text": bool(extracted_data["text"].strip()),
                "tables": bool(extracted_data["tables"]),
                "ocr": bool(extracted_data["ocr_text"].strip()),
                "images": bool(extracted_data["images"])
            }
        }
        
        # Combine all text sources
        text_parts = []
        
        if extracted_data["text"]:
            text_parts.append("=== MAIN DOCUMENT TEXT ===")
            text_parts.append(extracted_data["text"])
        
        # Add table text
        if extracted_data["tables"]:
            text_parts.append("\n=== TABLE CONTENT ===")
            for table in extracted_data["tables"]:
                if table.get("table_text"):
                    text_parts.append(f"Table from Page {table['page']}:")
                    text_parts.append(table["table_text"])
        
        # Add OCR text
        if extracted_data["ocr_text"]:
            text_parts.append("\n=== OCR EXTRACTED TEXT ===")
            text_parts.append(extracted_data["ocr_text"])
        
        integrated["combined_text"] = "\n".join(text_parts)
        
        # Extract structured data from combined sources
        integrated["structured_data"] = self._extract_structured_data(integrated["combined_text"], extracted_data)
        
        return integrated
    
    # Helper methods
    def _clean_table_data(self, table: List[List]) -> List[List]:
        """Clean table data"""
        if not table:
            return []
        
        cleaned_table = []
        for row in table:
            if row and any(cell and str(cell).strip() for cell in row):
                cleaned_row = []
                for cell in row:
                    if cell is None:
                        cleaned_row.append("")
                    else:
                        cleaned_cell = str(cell).strip()
                        cleaned_cell = re.sub(r'\s+', ' ', cleaned_cell)
                        cleaned_row.append(cleaned_cell)
                cleaned_table.append(cleaned_row)
        
        return cleaned_table
    
    def _table_to_text(self, table: List[List]) -> str:
        """Convert table to readable text"""
        if not table:
            return ""
        
        text_parts = []
        for row in table:
            if row:
                row_text = " | ".join(str(cell) for cell in row if cell)
                text_parts.append(row_text)
        
        return "\n".join(text_parts)
    
    def _analyze_image_content(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze image to determine content type"""
        analysis = {
            "type": "unknown",
            "content_type": "general",
            "has_text": False,
            "dominant_colors": [],
            "aspect_ratio": image.width / image.height if image.height > 0 else 1.0
        }
        
        # Simple heuristics for content type
        if analysis["aspect_ratio"] > 2.0:
            analysis["content_type"] = "banner_or_header"
        elif analysis["aspect_ratio"] < 0.5:
            analysis["content_type"] = "sidebar_or_icon"
        elif 0.8 <= analysis["aspect_ratio"] <= 1.2:
            analysis["content_type"] = "logo_or_photo"
        else:
            analysis["content_type"] = "diagram_or_chart"
        
        # Check if image might contain text (very basic check)
        # Convert to grayscale and check for text-like patterns
        try:
            gray = image.convert('L')
            img_array = np.array(gray)
            
            # Simple edge detection to find text-like patterns
            edges = cv2.Canny(img_array, 50, 150)
            edge_ratio = np.sum(edges > 0) / edges.size
            
            if edge_ratio > 0.05:  # If more than 5% edges, likely contains text
                analysis["has_text"] = True
        except:
            pass
        
        return analysis
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Apply noise reduction
            img_array = cv2.medianBlur(img_array, 3)
            
            # Apply thresholding
            _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL Image
            return Image.fromarray(img_array)
            
        except Exception as e:
            logger.warning(f"Error preprocessing image for OCR: {e}")
            return image
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean OCR extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        text = re.sub(r'[|]{2,}', '', text)  # Multiple pipes
        text = re.sub(r'[_]{3,}', '', text)  # Multiple underscores
        text = re.sub(r'[.]{3,}', '...', text)  # Multiple dots
        
        # Fix common OCR mistakes
        text = text.replace('|', 'I')  # Common mistake
        text = text.replace('0', 'O')  # In names/words
        
        return text.strip()
    
    def _analyze_ocr_content(self, text: str, image_analysis: Dict) -> Dict[str, Any]:
        """Analyze OCR text to determine content type"""
        analysis = {
            "type": "general",
            "confidence": 0.5,
            "elements": []
        }
        
        text_lower = text.lower()
        
        # Check for personal information
        if re.search(r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b', text_lower):
            analysis["elements"].append("email")
            analysis["confidence"] += 0.2
        
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            analysis["elements"].append("phone")
            analysis["confidence"] += 0.2
        
        # Check for skills/technologies
        tech_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'sql', 'aws', 'docker']
        if any(keyword in text_lower for keyword in tech_keywords):
            analysis["elements"].append("skills")
            analysis["confidence"] += 0.3
        
        # Check for education keywords
        edu_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd']
        if any(keyword in text_lower for keyword in edu_keywords):
            analysis["elements"].append("education")
            analysis["confidence"] += 0.3
        
        # Determine overall type
        if "skills" in analysis["elements"]:
            analysis["type"] = "skills_section"
        elif "education" in analysis["elements"]:
            analysis["type"] = "education_section"
        elif "email" in analysis["elements"] or "phone" in analysis["elements"]:
            analysis["type"] = "contact_info"
        
        return analysis
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page break markers
        text = re.sub(r'--- Page \d+ ---', '\n', text)
        
        # Fix common extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
        
        # Clean up bullet points
        text = re.sub(r'[•·▪▫◦‣⁃]', '•', text)
        
        return text.strip()
    
    def _extract_structured_data(self, combined_text: str, extracted_data: Dict) -> Dict[str, Any]:
        """Extract structured data from combined sources"""
        structured = {
            "personal_info": {},
            "skills": [],
            "experience": [],
            "education": [],
            "certifications": []
        }
        
        # This is a basic implementation - the main parsing will be done by LangGraph
        # But we can do some preliminary extraction here
        
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', combined_text)
        if emails:
            structured["personal_info"]["email"] = emails[0]
        
        # Extract phone numbers
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', combined_text)
        if phones:
            structured["personal_info"]["phone"] = phones[0]
        
        return structured
    
    def validate_pdf(self, file_path: str) -> Tuple[bool, str]:
        """Validate PDF file"""
        try:
            if not Path(file_path).exists():
                return False, "File does not exist"
            
            if not file_path.lower().endswith('.pdf'):
                return False, "File is not a PDF"
            
            # Test with both libraries
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF has no pages"
            
            # Test PyMuPDF
            pdf_doc = fitz.open(file_path)
            pdf_doc.close()
            
            return True, "PDF is valid and processable"
            
        except Exception as e:
            return False, f"Error validating PDF: {str(e)}"


# Factory function
def create_enhanced_pdf_processor(tesseract_path: str = None) -> EnhancedPDFProcessor:
    """Create an enhanced PDF processor instance"""
    return EnhancedPDFProcessor(tesseract_path=tesseract_path)
