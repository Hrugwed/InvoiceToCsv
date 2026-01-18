"""
CSV schema parser that uses OpenAI to understand semantic meaning of columns.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from openai_client import OpenAIClient
from utils import validate_csv_template


class SchemaParser:
    """Parse CSV template and infer semantic schema using OpenAI."""
    
    def __init__(self, openai_client: OpenAIClient):
        """Initialize schema parser with OpenAI client."""
        self.client = openai_client
    
    def parse_template(self, csv_path: Path) -> Dict[str, Any]:
        """
        Parse CSV template and return semantic schema.
        
        Args:
            csv_path: Path to CSV template file
            
        Returns:
            Dictionary containing schema information
        """
        validate_csv_template(csv_path)
        
        # Read CSV headers
        try:
            df = pd.read_csv(csv_path, nrows=0)  # Read only headers
            headers = df.columns.tolist()
        except Exception as e:
            raise ValueError(f"Failed to read CSV template: {str(e)}")
        
        if not headers:
            raise ValueError("CSV template has no headers")
        
        # Generate schema using OpenAI
        schema = self._infer_schema(headers)
        
        return {
            "headers": headers,
            "schema": schema,
            "column_count": len(headers),
        }
    
    def _infer_schema(self, headers: List[str]) -> List[Dict[str, Any]]:
        """
        Use OpenAI to infer semantic meaning and data types for each column.
        
        Args:
            headers: List of CSV column headers
            
        Returns:
            List of schema dictionaries for each column
        """
        system_prompt = """You are a data schema expert. Your task is to analyze CSV column headers and infer their semantic meaning, data type, and expected format.

For each column header, provide:
1. Semantic meaning (what the column represents)
2. Data type (string, number, date, currency, etc.)
3. Expected format (if applicable, e.g., date format, currency format)
4. Common aliases or alternative names for this field

Return your analysis as a JSON object with this exact structure:
{
  "columns": [
    {
      "header": "original_header_name",
      "semantic_meaning": "clear description of what this field represents",
      "data_type": "string|number|date|currency|email|phone|etc",
      "expected_format": "format description or null",
      "aliases": ["alternative_name1", "alternative_name2"]
    }
  ]
}"""

        user_prompt = f"""Analyze these CSV column headers and provide semantic schema information:

{', '.join(headers)}

Return the JSON schema analysis as specified."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        response = self.client.chat_completion(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        
        result = self.client.parse_json_response(response)
        
        # Validate and normalize schema
        if "columns" not in result:
            raise ValueError("Invalid schema response: missing 'columns' key")
        
        schema = result["columns"]
        
        # Ensure all headers are covered
        header_set = set(headers)
        schema_headers = {col["header"] for col in schema if "header" in col}
        
        if header_set != schema_headers:
            missing = header_set - schema_headers
            raise ValueError(f"Schema missing headers: {missing}")
        
        return schema
