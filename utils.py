"""
Utility functions for file handling and validation.
"""
import base64
from pathlib import Path
from typing import List, Optional
from config import (
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_PDF_EXTENSIONS,
    SUPPORTED_TEXT_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
)


def encode_image(image_path: Path) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def read_text_file(file_path: Path) -> str:
    """Read text file content."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_pdf_file(file_path: Path) -> str:
    """Read PDF file and extract text content."""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        text_content = []
        for page in reader.pages:
            text_content.append(page.extract_text())
        return "\n".join(text_content)
    except Exception as e:
        raise ValueError(f"Failed to read PDF file {file_path}: {str(e)}")


def get_file_type(file_path: Path) -> str:
    """Determine file type based on extension."""
    ext = file_path.suffix.lower()
    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    elif ext in SUPPORTED_PDF_EXTENSIONS:
        return "pdf"
    elif ext in SUPPORTED_TEXT_EXTENSIONS:
        return "text"
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def find_invoice_files(directory: Path) -> List[Path]:
    """Find all supported invoice files in a directory."""
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    invoice_files = []
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix in SUPPORTED_EXTENSIONS:
            invoice_files.append(file_path)
    
    if not invoice_files:
        raise ValueError(f"No supported invoice files found in {directory}")
    
    return sorted(invoice_files)


def validate_csv_template(csv_path: Path) -> bool:
    """Validate that CSV template file exists and is readable."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV template not found: {csv_path}")
    
    if not csv_path.is_file():
        raise ValueError(f"Path is not a file: {csv_path}")
    
    if csv_path.suffix.lower() != ".csv":
        raise ValueError(f"File is not a CSV: {csv_path}")
    
    return True


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
