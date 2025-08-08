import os
import logging
import re
import base64
from typing import Dict, Any, List
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pdfminer.layout import LAParams
from io import BytesIO
from PIL import Image
from source.interface.resume import ResumeLoader

class SmartPDFUniversalLoader(ResumeLoader):
    """Universal PDF loader to handle text, tables, and images."""

    def __init__(self, tesseract_cmd: str = None):
        self.logger = logging.getLogger(__name__)
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.laparams = LAParams(
            line_overlap=0.5,
            char_margin=2.0,
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=None,
            detect_vertical=True,
            all_texts=True
        )

    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        self.logger.info(f"Loading PDF from: {file_path}")
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()

        extracted_text = ""
        extracted_tables = []
        extracted_images = []
        extraction_method = ""
        extraction_details = {}

        try:
            with pdfplumber.open(file_path, laparams=self.laparams) as pdf:
                pages_text = []
                for i, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5, layout=True) or ""
                    pages_text.append(text)

                    # Extract tables
                    try:
                        tables = page.extract_tables({
                            "vertical_strategy": "lines",
                            "horizontal_strategy": "lines",
                            "intersection_tolerance": 5,
                            "snap_tolerance": 3
                        })
                        extracted_tables.extend(tables)
                    except Exception as e:
                        self.logger.warning(f"Table extraction failed on page {i}: {e}")

                    # Extract images
                    for img in page.images:
                        try:
                            cropped = page.within_bbox((img['x0'], img['top'], img['x1'], img['bottom'])).to_image()
                            pil_img = cropped.original
                            buffered = BytesIO()
                            pil_img.save(buffered, format="PNG")
                            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                            extracted_images.append(img_base64)
                        except Exception as e:
                            self.logger.warning(f"Image extraction failed on page {i}: {e}")

                extracted_text = "\n".join(pages_text).strip()
                if extracted_text:
                    extraction_method = "pdfplumber"
                    extraction_details["pdfplumber"] = {
                        "success": True,
                        "pages": len(pdf.pages),
                        "char_count": len(extracted_text),
                        "tables_found": len(extracted_tables),
                        "images_found": len(extracted_images),
                        "laparams": vars(self.laparams)
                    }

        except Exception as e:
            self.logger.error(f"pdfplumber failed: {e}")
            extraction_details["pdfplumber"] = {"success": False, "error": str(e)}

        # Fallback to OCR if no text extracted
        if not extracted_text:
            try:
                self.logger.info("Using OCR fallback...")
                images = convert_from_path(file_path, dpi=300)
                ocr_text = "\n".join([pytesseract.image_to_string(img) for img in images]).strip()
                if ocr_text:
                    extracted_text = ocr_text
                    extraction_method = "ocr"
                    extraction_details["ocr"] = {
                        "success": True,
                        "images": len(images),
                        "char_count": len(ocr_text),
                        "dpi": 300
                    }
                    # Also capture OCR page images as base64
                    for img in images:
                        buffered = BytesIO()
                        img.save(buffered, format="PNG")
                        extracted_images.append(base64.b64encode(buffered.getvalue()).decode('utf-8'))
            except Exception as e:
                self.logger.error(f"OCR failed: {e}")
                extraction_details["ocr"] = {"success": False, "error": str(e)}

        if not extracted_text:
            raise ValueError("No content extracted from PDF via either method.")

        processed_text = self._process_text(extracted_text)

        return {
            "content": processed_text,
            "tables": extracted_tables,
            "images": extracted_images,
            "metadata": {
                "file_name": file_name,
                "file_size": file_size,
                "file_extension": file_extension,
                "extraction_method": extraction_method,
                "extraction_details": extraction_details
            }
        }

    def _process_text(self, text: str) -> str:
        """Enhance text readability by adding structure."""
        text = re.sub(r'\s+', ' ', text)
        headers = [
            "EDUCATION", "EXPERIENCE", "SKILLS", "PROJECTS", "CERTIFICATIONS",
            "LANGUAGES", "SUMMARY", "OBJECTIVE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE",
            "TECHNICAL SKILLS", "PERSONAL PROJECTS"
        ]
        for header in headers:
            text = re.sub(f"({header})", r"\n\n\1", text, flags=re.IGNORECASE)
        return text
