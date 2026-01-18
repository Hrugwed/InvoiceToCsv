"""
CSV writer for generating final output file.
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from config import OUTPUT_FILE


class CSVWriter:
    """Write mapped invoice data to CSV file."""
    
    def __init__(self, output_path: Path = None):
        """
        Initialize CSV writer.
        
        Args:
            output_path: Path to output CSV file (defaults to config.OUTPUT_FILE)
        """
        self.output_path = output_path or OUTPUT_FILE
    
    def write(
        self,
        headers: List[str],
        rows: List[Dict[str, Any]],
        confidence_scores: List[Dict[str, float]] = None,
    ) -> Path:
        """
        Write mapped data to CSV file.
        
        Args:
            headers: List of CSV column headers
            rows: List of row dictionaries
            confidence_scores: Optional list of confidence score dictionaries
            
        Returns:
            Path to written CSV file
        """
        if not rows:
            raise ValueError("No rows to write")
        
        # Ensure all rows have all headers
        normalized_rows = []
        for row in rows:
            normalized_row = {}
            for header in headers:
                normalized_row[header] = row.get(header, None)
            normalized_rows.append(normalized_row)
        
        # Create DataFrame
        df = pd.DataFrame(normalized_rows, columns=headers)
        
        # Write to CSV
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_path, index=False, encoding="utf-8")
        
        return self.output_path
    
    def write_with_confidence(
        self,
        headers: List[str],
        rows: List[Dict[str, Any]],
        confidence_scores: List[Dict[str, float]],
    ) -> Path:
        """
        Write CSV with confidence scores as additional columns.
        
        Args:
            headers: List of CSV column headers
            rows: List of row dictionaries
            confidence_scores: List of confidence score dictionaries
            
        Returns:
            Path to written CSV file
        """
        if len(rows) != len(confidence_scores):
            raise ValueError("Rows and confidence scores must have same length")
        
        # Create extended headers with confidence columns
        extended_headers = []
        for header in headers:
            extended_headers.append(header)
            extended_headers.append(f"{header}_confidence")
        
        # Create extended rows
        extended_rows = []
        for row, scores in zip(rows, confidence_scores):
            extended_row = {}
            for header in headers:
                extended_row[header] = row.get(header, None)
                extended_row[f"{header}_confidence"] = scores.get(header, 0.0)
            extended_rows.append(extended_row)
        
        # Create DataFrame
        df = pd.DataFrame(extended_rows, columns=extended_headers)
        
        # Write to CSV
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_path, index=False, encoding="utf-8")
        
        return self.output_path
