"""
Invoice data extractor using OpenAI Vision and text models.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from openai_client import OpenAIClient
from utils import get_file_type, encode_image, read_text_file, read_pdf_file


class InvoiceExtractor:
    """Extract structured data from invoice documents using OpenAI."""
    
    def __init__(self, openai_client: OpenAIClient):
        """Initialize invoice extractor with OpenAI client."""
        self.client = openai_client
    
    def extract(self, file_path: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract invoice data from a document file.
        
        Args:
            file_path: Path to invoice file (PDF, image, or text)
            
        Returns:
            Tuple of (extracted_data, api_usage)
        """
        file_type = get_file_type(file_path)
        
        if file_type == "image":
            return self._extract_from_image(file_path)
        elif file_type == "pdf":
            return self._extract_from_pdf(file_path)
        elif file_type == "text":
            return self._extract_from_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _extract_from_image(self, image_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract data from image invoice using Vision API."""
        prompt = """Analyze this invoice image and extract all relevant invoice data.

Extract the following information (if available):
- Invoice number
- Invoice date
- Due date
- Vendor/supplier name
- Vendor address
- Customer/buyer name
- Customer address
- Line items (description, quantity, unit price, total)
- Subtotal
- Tax/VAT amount
- Total amount
- Payment terms
- Currency
- Any other relevant invoice fields

Return the extracted data as a JSON object with this structure:
{
  "invoice_number": "value or null",
  "invoice_date": "value or null",
  "due_date": "value or null",
  "vendor_name": "value or null",
  "vendor_address": "value or null",
  "customer_name": "value or null",
  "customer_address": "value or null",
  "line_items": [
    {
      "description": "value",
      "quantity": "value or null",
      "unit_price": "value or null",
      "total": "value or null"
    }
  ],
  "subtotal": "value or null",
  "tax_amount": "value or null",
  "total_amount": "value or null",
  "currency": "value or null",
  "payment_terms": "value or null",
  "additional_fields": {
    "field_name": "value"
  }
}

Be thorough and extract all visible information. Use null for missing fields."""

        response = self.client.vision_completion(
            image_path=image_path,
            prompt=prompt,
            max_tokens=4096,
        )
        
        extracted_data = self.client.parse_json_response(response)
        api_usage = response.get("usage", {})
        
        return extracted_data, api_usage
    
    def _extract_from_pdf(self, pdf_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract data from PDF invoice."""
        # First, try to extract text from PDF
        try:
            text_content = read_pdf_file(pdf_path)
        except Exception as e:
            print(f"   ⚠️  Text extraction failed: {str(e)}")
            text_content = ""
        
        # Check if we got meaningful text (more than just whitespace)
        if text_content and len(text_content.strip()) > 50:
            # Use text model to extract structured data
            return self._extract_from_text_content(text_content)
        else:
            # PDF is likely image-based (scanned), use Vision API
            print("   📸 PDF appears to be image-based, using Vision API...")
            return self._extract_from_pdf_images(pdf_path)
    
    def _extract_from_pdf_images(self, pdf_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract data from image-based PDF by converting to images."""
        try:
            import fitz  # PyMuPDF
            import tempfile
            from PIL import Image
            
            # Open PDF
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                raise ValueError("PDF has no pages")
            
            # Convert first page to image (usually invoice is on first page)
            page = doc[0]
            zoom = 2.0  # Higher resolution for better OCR
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Save as temporary PNG
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_image_path = Path(tmp_file.name)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(temp_image_path, 'PNG')
            
            doc.close()
            
            try:
                # Use Vision API to extract data (same prompt as image extraction)
                prompt = """Analyze this invoice image and extract all relevant invoice data.

Extract the following information (if available):
- Invoice number
- Invoice date
- Due date
- Vendor/supplier name
- Vendor address
- Customer/buyer name
- Customer address
- GSTIN
- Line items (description, quantity, unit price, total)
- Subtotal
- Tax/VAT amount (IGST, CGST, SGST)
- Total amount
- Payment terms
- Currency
- Round off amount
- Any other relevant invoice fields

Return the extracted data as a JSON object with this structure:
{
  "invoice_number": "value or null",
  "invoice_date": "value or null",
  "due_date": "value or null",
  "vendor_name": "value or null",
  "vendor_address": "value or null",
  "customer_name": "value or null",
  "customer_address": "value or null",
  "gstin": "value or null",
  "line_items": [
    {
      "description": "value",
      "quantity": "value or null",
      "unit_price": "value or null",
      "total": "value or null"
    }
  ],
  "subtotal": "value or null",
  "tax_amount": "value or null",
  "igst": "value or null",
  "cgst": "value or null",
  "sgst": "value or null",
  "total_amount": "value or null",
  "currency": "value or null",
  "payment_terms": "value or null",
  "round_off": "value or null",
  "additional_fields": {
    "field_name": "value"
  }
}

Be thorough and extract all visible information. Use null for missing fields."""

                response = self.client.vision_completion(
                    image_path=temp_image_path,
                    prompt=prompt,
                    max_tokens=4096,
                )
                
                extracted_data = self.client.parse_json_response(response)
                api_usage = response.get("usage", {})
                
                return extracted_data, api_usage
            finally:
                # Clean up temporary image file
                if temp_image_path.exists():
                    temp_image_path.unlink()
                    
        except ImportError:
            raise ValueError(
                "PDF appears to be image-based but PyMuPDF is not installed. "
                "Install it with: pip install pymupdf pillow"
            )
        except Exception as e:
            raise ValueError(f"Failed to process PDF as image: {str(e)}")
    
    def _extract_from_text(self, text_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract data from text invoice file."""
        text_content = read_text_file(text_path)
        
        if not text_content or not text_content.strip():
            raise ValueError("Text file appears to be empty")
        
        return self._extract_from_text_content(text_content)
    
    def _extract_from_text_content(self, text_content: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract structured data from text content using GPT."""
        system_prompt = """You are an expert invoice data extractor. Your task is to analyze invoice text and extract all relevant structured data.

Extract comprehensive invoice information including:
- Invoice number, dates, vendor/customer information
- Line items with quantities and prices
- Financial totals (subtotal, tax, total)
- Payment terms and currency
- Any other relevant fields

Return structured JSON with all extracted information."""
        
        user_prompt = f"""Extract all invoice data from this text:

{text_content}

Return the extracted data as a JSON object with this structure:
{{
  "invoice_number": "value or null",
  "invoice_date": "value or null",
  "due_date": "value or null",
  "vendor_name": "value or null",
  "vendor_address": "value or null",
  "customer_name": "value or null",
  "customer_address": "value or null",
  "line_items": [
    {{
      "description": "value",
      "quantity": "value or null",
      "unit_price": "value or null",
      "total": "value or null"
    }}
  ],
  "subtotal": "value or null",
  "tax_amount": "value or null",
  "total_amount": "value or null",
  "currency": "value or null",
  "payment_terms": "value or null",
  "additional_fields": {{
    "field_name": "value"
  }}
}}

Extract all available information. Use null for missing fields."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        response = self.client.chat_completion(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        
        extracted_data = self.client.parse_json_response(response)
        api_usage = response.get("usage", {})
        
        return extracted_data, api_usage
