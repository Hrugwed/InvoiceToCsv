"""
JSON data saver for OpenAI API responses and intermediate data.
Saving JSON locally does NOT cost any additional tokens - it's just file I/O.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import OUTPUT_DIR


class JSONSaver:
    """Save raw JSON data from OpenAI API responses."""
    
    def __init__(self, output_dir: Path = None):
        """Initialize JSON saver."""
        self.output_dir = output_dir or OUTPUT_DIR / "json_data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def save_extraction(
        self, 
        invoice_name: str, 
        raw_data: Dict[str, Any], 
        api_usage: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Save raw extraction JSON from OpenAI."""
        # Clean filename (remove extension, replace spaces)
        clean_name = Path(invoice_name).stem.replace(' ', '_')
        filename = f"extraction_{clean_name}_{self.session_id}.json"
        filepath = self.output_dir / filename
        
        data = {
            "invoice_file": invoice_name,
            "timestamp": datetime.now().isoformat(),
            "extraction_data": raw_data,
            "api_usage": api_usage or {}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def save_mapping(
        self, 
        invoice_name: str, 
        mapped_data: Dict[str, Any],
        confidence_scores: Dict[str, float], 
        api_usage: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Save mapping JSON with confidence scores."""
        clean_name = Path(invoice_name).stem.replace(' ', '_')
        filename = f"mapping_{clean_name}_{self.session_id}.json"
        filepath = self.output_dir / filename
        
        data = {
            "invoice_file": invoice_name,
            "timestamp": datetime.now().isoformat(),
            "mapped_data": mapped_data,
            "confidence_scores": confidence_scores,
            "api_usage": api_usage or {}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def save_schema(
        self, 
        schema_data: Dict[str, Any], 
        api_usage: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Save CSV schema analysis."""
        filename = f"schema_{self.session_id}.json"
        filepath = self.output_dir / filename
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "schema": schema_data,
            "api_usage": api_usage or {}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def save_summary(
        self, 
        all_invoices: List[str], 
        total_usage: Dict[str, Any],
        all_analyses: List[Dict[str, Any]]
    ) -> Path:
        """Save summary of all processing."""
        filename = f"summary_{self.session_id}.json"
        filepath = self.output_dir / filename
        
        # Calculate cost estimates (approximate)
        total_prompt_tokens = total_usage.get("total_prompt_tokens", 0)
        total_completion_tokens = total_usage.get("total_completion_tokens", 0)
        
        # GPT-4o-mini pricing: $0.15/1M input, $0.60/1M output
        # GPT-4o pricing: $2.50/1M input, $10/1M output
        cost_estimate_mini = (total_prompt_tokens / 1_000_000 * 0.15) + (total_completion_tokens / 1_000_000 * 0.60)
        cost_estimate_gpt4o = (total_prompt_tokens / 1_000_000 * 2.50) + (total_completion_tokens / 1_000_000 * 10.0)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "total_invoices": len(all_invoices),
            "invoices_processed": all_invoices,
            "total_api_usage": total_usage,
            "cost_estimates": {
                "gpt_4o_mini": round(cost_estimate_mini, 6),
                "gpt_4o": round(cost_estimate_gpt4o, 6),
                "note": "Actual costs depend on model used per call"
            },
            "confidence_summary": [
                {
                    "invoice": inv,
                    "average_confidence": analysis.get("average_confidence", 0),
                    "low_confidence_fields": len(analysis.get("low_confidence_fields", [])),
                    "medium_confidence_fields": len(analysis.get("medium_confidence_fields", []))
                }
                for inv, analysis in zip(all_invoices, all_analyses)
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
