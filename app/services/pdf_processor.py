import pdfplumber
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import re
import base64
from io import BytesIO
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class PDFProcessor:
    """Advanced PDF processor using pdfplumber for comprehensive data extraction"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_complete_pdf_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text, tables, images, and metadata from PDF
        Returns comprehensive data structure for LangGraph processing
        """
        try:
            extracted_data = {
                "text": "",
                "tables": [],
                "images": [],
                "metadata": {},
                "pages": [],
                "structure": {
                    "has_tables": False,
                    "has_images": False,
                    "page_count": 0,
                    "text_density": 0.0
                }
            }
            
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                extracted_data["metadata"] = {
                    "pages": len(pdf.pages),
                    "title": pdf.metadata.get('Title', ''),
                    "author": pdf.metadata.get('Author', ''),
                    "creator": pdf.metadata.get('Creator', ''),
                    "producer": pdf.metadata.get('Producer', ''),
                    "creation_date": str(pdf.metadata.get('CreationDate', '')),
                    "modification_date": str(pdf.metadata.get('ModDate', ''))
                }
                
                extracted_data["structure"]["page_count"] = len(pdf.pages)
                total_text_length = 0
                
                # Process each page
                for page_num, page in enumerate(pdf.pages):
                    page_data = self._process_page(page, page_num + 1)
                    extracted_data["pages"].append(page_data)
                    
                    # Accumulate text
                    if page_data["text"]:
                        extracted_data["text"] += f"\n--- Page {page_num + 1} ---\n{page_data['text']}"
                        total_text_length += len(page_data["text"])
                    
                    # Accumulate tables
                    if page_data["tables"]:
                        extracted_data["tables"].extend(page_data["tables"])
                        extracted_data["structure"]["has_tables"] = True
                    
                    # Accumulate images
                    if page_data["images"]:
                        extracted_data["images"].extend(page_data["images"])
                        extracted_data["structure"]["has_images"] = True
                
                # Calculate text density
                if extracted_data["structure"]["page_count"] > 0:
                    extracted_data["structure"]["text_density"] = total_text_length / extracted_data["structure"]["page_count"]
                
                # Clean and process text
                extracted_data["text"] = self.clean_text(extracted_data["text"])
                
                return extracted_data
                
        except Exception as e:
            logger.error(f"Error extracting PDF data from {file_path}: {e}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _process_page(self, page, page_num: int) -> Dict[str, Any]:
        """Process individual page for text, tables, and images"""
        page_data = {
            "page_number": page_num,
            "text": "",
            "tables": [],
            "images": [],
            "bbox": page.bbox if hasattr(page, 'bbox') else None
        }
        
        try:
            # Extract text
            page_text = page.extract_text()
            if page_text:
                page_data["text"] = page_text
            
            # Extract tables with better structure
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if table and len(table) > 0:
                    # Clean table data
                    cleaned_table = self._clean_table(table)
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
                            except Exception as e:
                                logger.warning(f"Could not convert table to DataFrame: {e}")
                        
                        page_data["tables"].append(table_data)
            
            # Extract images info
            if hasattr(page, 'images'):
                for img_idx, image in enumerate(page.images):
                    image_data = {
                        "page": page_num,
                        "image_index": img_idx,
                        "bbox": image.get('bbox', []),
                        "width": image.get('width', 0),
                        "height": image.get('height', 0),
                        "object_type": image.get('object_type', 'image')
                    }
                    page_data["images"].append(image_data)
            
        except Exception as e:
            logger.warning(f"Error processing page {page_num}: {e}")
        
        return page_data
    
    def _clean_table(self, table: List[List]) -> List[List]:
        """Clean table data by removing empty rows and normalizing cells"""
        if not table:
            return []
        
        cleaned_table = []
        for row in table:
            if row and any(cell and str(cell).strip() for cell in row):
                # Clean each cell
                cleaned_row = []
                for cell in row:
                    if cell is None:
                        cleaned_row.append("")
                    else:
                        # Clean cell content
                        cleaned_cell = str(cell).strip()
                        cleaned_cell = re.sub(r'\s+', ' ', cleaned_cell)
                        cleaned_row.append(cleaned_cell)
                cleaned_table.append(cleaned_row)
        
        return cleaned_table
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text for better processing"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page break markers
        text = re.sub(r'--- Page \d+ ---', '\n', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between words
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Add space between numbers and letters
        
        # Remove excessive newlines but preserve paragraph structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Clean up bullet points and special characters
        text = re.sub(r'[•·▪▫◦‣⁃]', '•', text)  # Normalize bullet points
        
        return text.strip()
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common resume sections from text
        Returns dictionary with section names as keys
        """
        sections = {}
        
        # Common section patterns
        section_patterns = {
            'summary': r'(?:summary|profile|objective|about|overview)[\s:]*\n(.*?)(?=\n\s*(?:experience|education|skills|work|employment|projects|certifications?)|\Z)',
            'experience': r'(?:experience|work|employment|professional)[\s:]*\n(.*?)(?=\n\s*(?:education|skills|projects|certifications?|awards|achievements)|\Z)',
            'education': r'(?:education|academic|qualifications?)[\s:]*\n(.*?)(?=\n\s*(?:experience|skills|projects|certifications?|awards|achievements)|\Z)',
            'skills': r'(?:skills|technical|competencies|technologies)[\s:]*\n(.*?)(?=\n\s*(?:experience|education|projects|certifications?|awards|achievements)|\Z)',
            'certifications': r'(?:certifications?|licenses?|credentials?)[\s:]*\n(.*?)(?=\n\s*(?:experience|education|skills|projects|awards|achievements)|\Z)',
            'projects': r'(?:projects?|portfolio)[\s:]*\n(.*?)(?=\n\s*(?:experience|education|skills|certifications?|awards|achievements)|\Z)',
            'achievements': r'(?:achievements?|awards?|honors?|accomplishments?)[\s:]*\n(.*?)(?=\n\s*(?:experience|education|skills|projects|certifications?)|\Z)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
        
        return sections
    
    def validate_pdf(self, file_path: str) -> Tuple[bool, str]:
        """Validate PDF file and return status with message"""
        try:
            if not Path(file_path).exists():
                return False, "File does not exist"
            
            if not file_path.lower().endswith('.pdf'):
                return False, "File is not a PDF"
            
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF has no pages"
                
                # Check if we can extract any text
                first_page_text = pdf.pages[0].extract_text()
                if not first_page_text or len(first_page_text.strip()) < 10:
                    return False, "PDF appears to be image-only or has no extractable text"
            
            return True, "PDF is valid and processable"
            
        except Exception as e:
            return False, f"Error validating PDF: {str(e)}"
