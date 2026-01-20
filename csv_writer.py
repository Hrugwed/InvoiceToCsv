"""
CSV writer for generating final output file.
"""
import pandas as pd
import time
import os
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
        
        # Write to CSV with retry logic for locked files
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to write with retries (in case file is open in Excel)
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # If file exists and might be locked, try to remove it first
                if attempt > 0 and self.output_path.exists():
                    try:
                        os.remove(self.output_path)
                    except PermissionError:
                        # File is locked, wait and try again
                        if attempt < max_retries - 1:
                            print(f"   ⚠️  File is locked (may be open in Excel). Retrying in {retry_delay} second(s)...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                
                df.to_csv(self.output_path, index=False, encoding="utf-8")
                break
                
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Permission denied. Retrying in {retry_delay} second(s)...")
                    print(f"   💡 Please close the file if it's open in Excel or another program.")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # Last attempt failed, try with timestamp backup
                    timestamp = int(time.time())
                    backup_path = self.output_path.parent / f"final_output_{timestamp}.csv"
                    print(f"   ⚠️  Could not write to {self.output_path.name}")
                    print(f"   💾 Writing to backup file: {backup_path.name}")
                    df.to_csv(backup_path, index=False, encoding="utf-8")
                    return backup_path
        
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
        
        # Write to CSV with retry logic for locked files
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to write with retries (in case file is open in Excel)
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # If file exists and might be locked, try to remove it first
                if attempt > 0 and self.output_path.exists():
                    try:
                        os.remove(self.output_path)
                    except PermissionError:
                        # File is locked, wait and try again
                        if attempt < max_retries - 1:
                            print(f"   ⚠️  File is locked (may be open in Excel). Retrying in {retry_delay} second(s)...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                
                df.to_csv(self.output_path, index=False, encoding="utf-8")
                break
                
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Permission denied. Retrying in {retry_delay} second(s)...")
                    print(f"   💡 Please close the file if it's open in Excel or another program.")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # Last attempt failed, try with timestamp backup
                    timestamp = int(time.time())
                    backup_path = self.output_path.parent / f"final_output_{timestamp}.csv"
                    print(f"   ⚠️  Could not write to {self.output_path.name}")
                    print(f"   💾 Writing to backup file: {backup_path.name}")
                    df.to_csv(backup_path, index=False, encoding="utf-8")
                    return backup_path
        
        return self.output_path
