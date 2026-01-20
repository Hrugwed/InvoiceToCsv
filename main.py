"""
Main CLI entry point for invoice-to-CSV normalization application.
"""
import sys
import argparse
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Fix encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from config import OUTPUT_FILE
from openai_client import OpenAIClient
from schema_parser import SchemaParser
from invoice_extractor import InvoiceExtractor
from mapper import SemanticMapper
from confidence import ConfidenceAnalyzer
from csv_writer import CSVWriter
from json_saver import JSONSaver
from utils import find_invoice_files, validate_csv_template


def get_user_input(prompt: str, validator=None) -> str:
    """Get user input with optional validation."""
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print("❌ Input cannot be empty. Please try again.")
                continue
            if validator:
                validator(value)
            return value
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try again.")


def validate_path(path_str: str) -> Path:
    """Validate that path exists."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    return path


def main(template_path: Optional[str] = None, invoice_dir: Optional[str] = None, auto_confirm: bool = False):
    """Main CLI application flow."""
    print("=" * 60)
    print("🤖 AI-Powered Invoice-to-CSV Normalization")
    print("=" * 60)
    print()
    
    try:
        # Initialize OpenAI client
        print("🔧 Initializing OpenAI client...")
        openai_client = OpenAIClient()
        print("✅ OpenAI client initialized")
        print()
        
        # Get CSV template path
        print("Step 1: CSV Template")
        if template_path:
            csv_template_path = Path(template_path)
            validate_csv_template(csv_template_path)
            print(f"✅ Template: {csv_template_path}")
        else:
            csv_template_path = get_user_input(
                "Enter path to CSV template file: ",
                validator=lambda x: validate_csv_template(validate_path(x))
            )
            csv_template_path = Path(csv_template_path)
            print(f"✅ Template found: {csv_template_path}")
        print()
        
        # Get invoice directory path
        print("Step 2: Invoice Files")
        if invoice_dir:
            invoice_dir_path = Path(invoice_dir)
            if not invoice_dir_path.exists():
                raise FileNotFoundError(f"Directory not found: {invoice_dir_path}")
            print(f"✅ Directory: {invoice_dir_path}")
        else:
            invoice_dir_path = get_user_input(
                "Enter directory path containing invoice files: ",
                validator=lambda x: validate_path(x)
            )
            invoice_dir_path = Path(invoice_dir_path)
            print(f"✅ Directory found: {invoice_dir_path}")
        print()
        
        # Find invoice files
        print("🔍 Scanning for invoice files...")
        invoice_files = find_invoice_files(invoice_dir_path)
        print(f"✅ Found {len(invoice_files)} invoice file(s)")
        for i, file_path in enumerate(invoice_files, 1):
            print(f"   {i}. {file_path.name}")
        print()
        
        # Confirm processing
        if not auto_confirm:
            print("Step 3: Confirmation")
            confirm = input(f"Process {len(invoice_files)} invoice(s)? (yes/no): ").strip().lower()
            if confirm not in ["yes", "y"]:
                print("❌ Processing cancelled.")
                sys.exit(0)
            print()
        else:
            print(f"Step 3: Auto-confirming processing of {len(invoice_files)} invoice(s)...")
            print()
        
        # Initialize components
        print("🔧 Initializing components...")
        schema_parser = SchemaParser(openai_client)
        invoice_extractor = InvoiceExtractor(openai_client)
        mapper = SemanticMapper(openai_client)
        confidence_analyzer = ConfidenceAnalyzer()
        csv_writer = CSVWriter()
        json_saver = JSONSaver()
        print("✅ Components initialized")
        print()
        
        # Track total API usage
        total_api_usage = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_calls": 0
        }
        
        # Parse CSV template
        print("📋 Parsing CSV template...")
        template_info, schema_usage = schema_parser.parse_template(csv_template_path)
        headers = template_info["headers"]
        schema = template_info["schema"]
        
        # Save schema JSON
        schema_json_path = json_saver.save_schema(template_info, schema_usage)
        
        # Update total usage
        total_api_usage["total_prompt_tokens"] += schema_usage.get("prompt_tokens", 0)
        total_api_usage["total_completion_tokens"] += schema_usage.get("completion_tokens", 0)
        total_api_usage["total_tokens"] += schema_usage.get("total_tokens", 0)
        total_api_usage["total_calls"] += 1
        
        print(f"✅ Template parsed: {len(headers)} columns")
        print(f"   Columns: {', '.join(headers)}")
        print()
        
        # Process each invoice
        print("=" * 60)
        print("PROCESSING INVOICES")
        print("=" * 60)
        print()
        
        all_rows = []
        all_confidence_scores = []
        all_analyses = []
        processed_invoices = []
        
        for i, invoice_file in enumerate(invoice_files, 1):
            print(f"[{i}/{len(invoice_files)}] Processing: {invoice_file.name}")
            
            try:
                # Extract invoice data
                print("   📄 Extracting invoice data...")
                invoice_data, extraction_usage = invoice_extractor.extract(invoice_file)
                
                # Save extraction JSON
                extraction_json_path = json_saver.save_extraction(
                    invoice_file.name,
                    invoice_data,
                    extraction_usage
                )
                
                # Update total usage
                total_api_usage["total_prompt_tokens"] += extraction_usage.get("prompt_tokens", 0)
                total_api_usage["total_completion_tokens"] += extraction_usage.get("completion_tokens", 0)
                total_api_usage["total_tokens"] += extraction_usage.get("total_tokens", 0)
                total_api_usage["total_calls"] += 1
                
                print("   ✅ Extraction complete")
                
                # Map to schema
                print("   🔗 Mapping to CSV schema...")
                mapped_data, confidence_scores, mapping_usage = mapper.map_invoice_to_schema(
                    invoice_data, schema
                )
                
                # Save mapping JSON
                mapping_json_path = json_saver.save_mapping(
                    invoice_file.name,
                    mapped_data,
                    confidence_scores,
                    mapping_usage
                )
                
                # Update total usage
                total_api_usage["total_prompt_tokens"] += mapping_usage.get("prompt_tokens", 0)
                total_api_usage["total_completion_tokens"] += mapping_usage.get("completion_tokens", 0)
                total_api_usage["total_tokens"] += mapping_usage.get("total_tokens", 0)
                total_api_usage["total_calls"] += 1
                
                print("   ✅ Mapping complete")
                
                # Analyze confidence
                analysis = confidence_analyzer.analyze_row(confidence_scores, mapped_data)
                all_analyses.append(analysis)
                
                # Store results
                all_rows.append(mapped_data)
                all_confidence_scores.append(confidence_scores)
                processed_invoices.append(invoice_file.name)
                
                # Show warnings
                warnings = confidence_analyzer.format_warnings(analysis, invoice_file.name)
                if warnings:
                    print(warnings)
                
                print(f"   📊 Average confidence: {analysis['average_confidence']:.3f}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error processing {invoice_file.name}: {str(e)}")
                print(f"   ⚠️  Skipping this invoice...")
                print()
                continue
        
        # Write output CSV
        print("=" * 60)
        print("GENERATING OUTPUT")
        print("=" * 60)
        print()
        
        print(f"📝 Writing {len(all_rows)} row(s) to CSV...")
        output_path = csv_writer.write(headers, all_rows, all_confidence_scores)
        print(f"✅ Output written: {output_path}")
        print()
        
        # Save summary JSON
        summary_json_path = json_saver.save_summary(
            processed_invoices,
            total_api_usage,
            all_analyses
        )
        
        # Show summary
        summary = confidence_analyzer.get_summary(all_analyses)
        if summary:
            print(summary)
            print()
        
        # Show API usage summary
        print("=" * 60)
        print("API USAGE SUMMARY")
        print("=" * 60)
        print(f"Total API calls: {total_api_usage['total_calls']}")
        print(f"Total tokens: {total_api_usage['total_tokens']:,}")
        print(f"  - Prompt tokens: {total_api_usage['total_prompt_tokens']:,}")
        print(f"  - Completion tokens: {total_api_usage['total_completion_tokens']:,}")
        
        # Estimate costs
        prompt_cost_mini = total_api_usage['total_prompt_tokens'] / 1_000_000 * 0.15
        completion_cost_mini = total_api_usage['total_completion_tokens'] / 1_000_000 * 0.60
        total_cost_mini = prompt_cost_mini + completion_cost_mini
        
        print(f"\n💰 Estimated cost (GPT-4o-mini): ${total_cost_mini:.6f}")
        print(f"   💡 Check summary JSON for detailed cost breakdown")
        print()
        
        # Show low confidence warnings
        has_warnings = any(
            len(a["low_confidence_fields"]) > 0 or len(a["medium_confidence_fields"]) > 0
            for a in all_analyses
        )
        
        if has_warnings:
            print("⚠️  WARNING: Some fields have low or medium confidence scores.")
            print("   Please review the output CSV and verify low-confidence fields.")
            print()
        
        print("=" * 60)
        print("✅ PROCESSING COMPLETE")
        print("=" * 60)
        print(f"📁 CSV output: {output_path}")
        print(f"📊 JSON data saved to: {json_saver.output_dir}")
        print(f"   - Schema: {schema_json_path.name}")
        print(f"   - Extractions: {len(processed_invoices)} files")
        print(f"   - Mappings: {len(processed_invoices)} files")
        print(f"   - Summary: {summary_json_path.name}")
        print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Powered Invoice-to-CSV Normalization")
    parser.add_argument("--template", "-t", type=str, help="Path to CSV template file")
    parser.add_argument("--invoices", "-i", type=str, help="Directory path containing invoice files")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm processing without prompting")
    
    args = parser.parse_args()
    main(template_path=args.template, invoice_dir=args.invoices, auto_confirm=args.yes)
