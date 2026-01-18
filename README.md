# AI-Powered Invoice-to-CSV Normalization

A Python CLI application that uses OpenAI APIs to extract data from invoices (PDF, PNG, JPG, TXT) and normalize them into a CSV format based on a user-provided template. The application performs semantic mapping to match invoice fields to CSV columns, not just string matching.

## Features

- 🤖 **AI-Powered Extraction**: Uses OpenAI GPT-4o and Vision models to extract structured data from invoices
- 📋 **Semantic Schema Understanding**: Automatically infers the meaning of CSV template columns
- 🔗 **Intelligent Mapping**: Maps extracted invoice data to CSV columns based on semantic meaning
- 📊 **Confidence Scoring**: Assigns confidence scores (0-1) for each mapped field
- ⚠️ **Low-Confidence Warnings**: Highlights fields with low confidence for manual review
- 📁 **Multiple Formats**: Supports PDF, PNG, JPG, and TXT invoice files
- 🖥️ **CLI Interface**: Simple command-line interface for easy operation

## Requirements

- Python 3.10 or higher
- OpenAI API key
- Internet connection (for API calls)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

1. **Prepare your CSV template**:
   - Create a CSV file with headers only (no data rows)
   - Example: `template.csv`
     ```csv
     Invoice Number,Date,Vendor,Amount,Currency
     ```

2. **Prepare your invoice files**:
   - Place all invoice files (PDF, PNG, JPG, or TXT) in a directory
   - Supported formats: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Follow the prompts**:
   - Enter path to your CSV template file
   - Enter directory path containing invoice files
   - Confirm processing

5. **Review the output**:
   - Output CSV will be written to `output/final_output.csv`
   - Check console for confidence warnings

## Example

```bash
$ python main.py
============================================================
🤖 AI-Powered Invoice-to-CSV Normalization
============================================================

🔧 Initializing OpenAI client...
✅ OpenAI client initialized

Step 1: CSV Template
Enter path to CSV template file: template.csv
✅ Template found: template.csv

Step 2: Invoice Files
Enter directory path containing invoice files: ./invoices
✅ Directory found: ./invoices

🔍 Scanning for invoice files...
✅ Found 3 invoice file(s)
   1. invoice1.pdf
   2. invoice2.png
   3. invoice3.txt

Step 3: Confirmation
Process 3 invoice(s)? (yes/no): yes

🔧 Initializing components...
✅ Components initialized

📋 Parsing CSV template...
✅ Template parsed: 5 columns
   Columns: Invoice Number, Date, Vendor, Amount, Currency

============================================================
PROCESSING INVOICES
============================================================

[1/3] Processing: invoice1.pdf
   📄 Extracting invoice data...
   ✅ Extraction complete
   🔗 Mapping to CSV schema...
   ✅ Mapping complete
   📊 Average confidence: 0.92

[2/3] Processing: invoice2.png
   📄 Extracting invoice data...
   ✅ Extraction complete
   🔗 Mapping to CSV schema...
   ✅ Mapping complete
   📊 Average confidence: 0.88

[3/3] Processing: invoice3.txt
   📄 Extracting invoice data...
   ✅ Extraction complete
   🔗 Mapping to CSV schema...
   ✅ Mapping complete
   📊 Average confidence: 0.95

============================================================
GENERATING OUTPUT
============================================================

📝 Writing 3 row(s) to CSV...
✅ Output written: output/final_output.csv

============================================================
CONFIDENCE SUMMARY
============================================================
Total invoices processed: 3
Overall average confidence: 0.917
Total low-confidence fields: 0
Total medium-confidence fields: 2
============================================================

============================================================
✅ PROCESSING COMPLETE
============================================================
📁 Output file: output/final_output.csv
```

## Project Structure

```
invoice_ai_cli/
│
├── main.py                 # CLI entry point
├── config.py               # Configuration and constants
├── openai_client.py        # OpenAI API client wrapper
├── schema_parser.py        # CSV template schema parser
├── invoice_extractor.py    # Invoice data extraction
├── mapper.py               # Semantic mapping logic
├── confidence.py           # Confidence analysis
├── csv_writer.py           # CSV output writer
├── utils.py                # Utility functions
│
├── output/                 # Output directory
│   └── final_output.csv    # Generated CSV file
│
├── .env.example            # Environment variables template
├── .env                    # Your API keys (not in repo)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## How It Works

1. **Schema Parsing**: The application reads your CSV template headers and uses OpenAI to infer the semantic meaning, data type, and expected format of each column.

2. **Invoice Extraction**: For each invoice file:
   - Images (PNG, JPG) are sent to OpenAI Vision API
   - PDFs are converted to text and processed
   - Text files are processed directly
   - All data is extracted as structured JSON

3. **Semantic Mapping**: The extracted invoice data is mapped to your CSV schema using semantic matching. The AI understands that "Invoice #" matches "Invoice Number", "Total" matches "Amount", etc.

4. **Confidence Scoring**: Each mapped field receives a confidence score:
   - 1.0: Perfect match
   - 0.8-0.9: Strong semantic match
   - 0.6-0.7: Reasonable match
   - 0.4-0.5: Weak match
   - 0.0-0.3: No match found

5. **Output Generation**: All mapped data is written to a CSV file with warnings for low-confidence fields.

## Limitations

- **API Costs**: Each invoice requires multiple API calls. Costs depend on your OpenAI pricing tier.
- **Processing Time**: Processing time depends on API response times and number of invoices.
- **File Size**: Very large PDFs or images may need to be optimized.
- **Language**: Currently optimized for English invoices. Other languages may work but with reduced accuracy.
- **Complex Layouts**: Highly complex or non-standard invoice layouts may have lower extraction accuracy.
- **Line Items**: Line item aggregation may need manual review for complex invoices.

## Error Handling

The application handles:
- Missing or invalid files
- API failures with retries
- Empty or unreadable documents
- Invalid JSON responses from API
- Missing CSV columns

## Future Improvements

- [ ] Batch processing optimization
- [ ] Support for additional file formats (DOCX, XLSX)
- [ ] Multi-language support
- [ ] Custom confidence thresholds
- [ ] Interactive field mapping review
- [ ] Export confidence scores as separate CSV columns
- [ ] Progress bar for large batches
- [ ] Resume processing from failures
- [ ] Web UI option

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you've created a `.env` file with your API key
- Check that the key is correctly formatted (no quotes, no spaces)

### "No supported invoice files found"
- Verify your invoice directory path is correct
- Check that files have supported extensions (.pdf, .png, .jpg, .txt)

### "Failed to parse JSON response"
- This usually indicates an API issue. Try running again.
- Check your OpenAI API quota and billing status

### Low confidence scores
- Ensure invoices are clear and readable
- Check that CSV template headers are descriptive
- Some fields may naturally have lower confidence (e.g., optional fields)

## License

This project is provided as-is for case study purposes.

## Support

For issues or questions, please check:
- OpenAI API documentation: https://platform.openai.com/docs
- Python documentation: https://docs.python.org/3/
