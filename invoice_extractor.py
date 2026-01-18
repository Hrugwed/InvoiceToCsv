"""
Invoice data extractor using OpenAI Vision and text models.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from openai_client import OpenAIClient
from utils import get_file_type, encode_image, read_text_file, read_pdf_file


class InvoiceExtractor:
    """Extract structured data from invoice documents using OpenAI."""
    
    def __init__(self, openai_client: OpenAIClient):
        """Initialize invoice extractor with OpenAI client."""
        self.client = openai_client
    
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract invoice data from a document file.
        
        Args:
            file_path: Path to invoice file (PDF, image, or text)
            
        Returns:
            Dictionary containing extracted invoice data
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
    
    def _extract_from_image(self, image_path: Path) -> Dict[str, Any]:
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
        
        return self.client.parse_json_response(response)
    
    def _extract_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract data from PDF invoice."""
        # First, try to extract text from PDF
        try:
            text_content = read_pdf_file(pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")
        
        if not text_content or not text_content.strip():
            raise ValueError("PDF appears to be empty or unreadable")
        
        # Use text model to extract structured data
        return self._extract_from_text_content(text_content)
    
    def _extract_from_text(self, text_path: Path) -> Dict[str, Any]:
        """Extract data from text invoice file."""
        text_content = read_text_file(text_path)
        
        if not text_content or not text_content.strip():
            raise ValueError("Text file appears to be empty")
        
        return self._extract_from_text_content(text_content)
    
    def _extract_from_text_content(self, text_content: str) -> Dict[str, Any]:
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
        
        return self.client.parse_json_response(response)
