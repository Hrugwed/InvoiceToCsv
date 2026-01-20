"""
Semantic mapper that maps extracted invoice data to CSV schema.
"""
from typing import Dict, List, Any, Tuple
from openai_client import OpenAIClient


class SemanticMapper:
    """Map extracted invoice data to CSV schema using semantic matching."""
    
    def __init__(self, openai_client: OpenAIClient):
        """Initialize mapper with OpenAI client."""
        self.client = openai_client
    
    def map_invoice_to_schema(
        self, invoice_data: Dict[str, Any], schema: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, Any]]:
        """
        Map extracted invoice data to CSV schema columns.
        
        Args:
            invoice_data: Extracted invoice data dictionary
            schema: CSV schema with semantic information
            
        Returns:
            Tuple of (mapped_data, confidence_scores, api_usage)
        """
        system_prompt = """You are a data mapping expert. Your task is to map extracted invoice data to CSV column headers based on semantic meaning, not exact string matching.

You will receive:
1. Extracted invoice data (JSON)
2. CSV schema with semantic meanings for each column

Your job is to:
- Match invoice fields to CSV columns by meaning
- Fill in values for all CSV columns
- Assign confidence scores (0.0 to 1.0) for each mapping
- Use null for missing values
- Aggregate line items if needed (e.g., sum quantities, concatenate descriptions)

Return a JSON object with this structure:
{
  "mapped_data": {
    "column_header_1": "mapped_value or null",
    "column_header_2": "mapped_value or null"
  },
  "confidence_scores": {
    "column_header_1": 0.95,
    "column_header_2": 0.80
  },
  "mapping_explanations": {
    "column_header_1": "brief explanation of mapping"
  }
}

Confidence scores:
- 1.0: Perfect match, exact field found
- 0.8-0.9: Strong semantic match
- 0.6-0.7: Reasonable match with some inference
- 0.4-0.5: Weak match, significant inference
- 0.0-0.3: No match found, null value"""
        
        # Prepare schema description
        schema_description = self._format_schema_description(schema)
        
        user_prompt = f"""Map this extracted invoice data to the CSV schema:

EXTRACTED INVOICE DATA:
{self._format_invoice_data(invoice_data)}

CSV SCHEMA:
{schema_description}

Perform semantic mapping and return the mapped data with confidence scores."""
        
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
        api_usage = response.get("usage", {})
        
        # Validate response structure
        if "mapped_data" not in result:
            raise ValueError("Mapping response missing 'mapped_data'")
        if "confidence_scores" not in result:
            raise ValueError("Mapping response missing 'confidence_scores'")
        
        mapped_data = result["mapped_data"]
        confidence_scores = result["confidence_scores"]
        
        # Ensure all schema columns are present
        schema_headers = {col["header"] for col in schema}
        mapped_headers = set(mapped_data.keys())
        
        # Add missing columns with null values and 0.0 confidence
        for header in schema_headers:
            if header not in mapped_data:
                mapped_data[header] = None
                confidence_scores[header] = 0.0
        
        # Normalize confidence scores to 0.0-1.0 range
        normalized_scores = {}
        for header, score in confidence_scores.items():
            try:
                score_float = float(score)
                normalized_scores[header] = max(0.0, min(1.0, score_float))
            except (ValueError, TypeError):
                normalized_scores[header] = 0.0
        
        return mapped_data, normalized_scores, api_usage
    
    def _format_schema_description(self, schema: List[Dict[str, Any]]) -> str:
        """Format schema for prompt."""
        lines = []
        for col in schema:
            header = col.get("header", "")
            meaning = col.get("semantic_meaning", "")
            data_type = col.get("data_type", "")
            aliases = col.get("aliases", [])
            
            line = f"- {header}"
            if meaning:
                line += f" (meaning: {meaning})"
            if data_type:
                line += f" [type: {data_type}]"
            if aliases:
                line += f" [aliases: {', '.join(aliases)}]"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _format_invoice_data(self, invoice_data: Dict[str, Any]) -> str:
        """Format invoice data as readable string."""
        import json
        return json.dumps(invoice_data, indent=2)
