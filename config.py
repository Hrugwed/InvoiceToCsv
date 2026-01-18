"""
Configuration module for invoice-to-CSV CLI application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please create a .env file with your OpenAI API key."
    )

# Model Configuration
DEFAULT_MODEL = "gpt-4o-mini"      # Cheapest model for most operations
VISION_MODEL = "gpt-4o"            # Required for images (mini doesn't support vision)
TEXT_MODEL = "gpt-4o-mini"         # Cheapest for text/PDF extraction

# Project Paths
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "final_output.csv"

# Supported file extensions
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"}
SUPPORTED_PDF_EXTENSIONS = {".pdf", ".PDF"}
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".TXT"}
SUPPORTED_EXTENSIONS = (
    SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_PDF_EXTENSIONS | SUPPORTED_TEXT_EXTENSIONS
)

# Confidence thresholds
LOW_CONFIDENCE_THRESHOLD = 0.7
MEDIUM_CONFIDENCE_THRESHOLD = 0.85

# API Configuration
MAX_RETRIES = 3
REQUEST_TIMEOUT = 60
