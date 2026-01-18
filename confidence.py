"""
Confidence score analysis and reporting utilities.
"""
from typing import Dict, List, Tuple, Any
from config import LOW_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD


class ConfidenceAnalyzer:
    """Analyze and report confidence scores for mapped data."""
    
    @staticmethod
    def analyze_row(
        confidence_scores: Dict[str, float], row_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze confidence scores for a single row.
        
        Args:
            confidence_scores: Dictionary of column -> confidence score
            row_data: Mapped row data
            
        Returns:
            Analysis dictionary with statistics and warnings
        """
        scores = list(confidence_scores.values())
        
        if not scores:
            return {
                "average_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "low_confidence_fields": [],
                "medium_confidence_fields": [],
                "high_confidence_fields": [],
            }
        
        avg_confidence = sum(scores) / len(scores)
        min_confidence = min(scores)
        max_confidence = max(scores)
        
        low_confidence = [
            (col, score)
            for col, score in confidence_scores.items()
            if score < LOW_CONFIDENCE_THRESHOLD
        ]
        
        medium_confidence = [
            (col, score)
            for col, score in confidence_scores.items()
            if LOW_CONFIDENCE_THRESHOLD <= score < MEDIUM_CONFIDENCE_THRESHOLD
        ]
        
        high_confidence = [
            (col, score)
            for col, score in confidence_scores.items()
            if score >= MEDIUM_CONFIDENCE_THRESHOLD
        ]
        
        return {
            "average_confidence": round(avg_confidence, 3),
            "min_confidence": round(min_confidence, 3),
            "max_confidence": round(max_confidence, 3),
            "low_confidence_fields": sorted(low_confidence, key=lambda x: x[1]),
            "medium_confidence_fields": sorted(medium_confidence, key=lambda x: x[1]),
            "high_confidence_fields": sorted(high_confidence, key=lambda x: x[1]),
        }
    
    @staticmethod
    def format_warnings(analysis: Dict[str, Any], invoice_name: str) -> str:
        """
        Format confidence warnings for console output.
        
        Args:
            analysis: Analysis dictionary from analyze_row
            invoice_name: Name of the invoice file
            
        Returns:
            Formatted warning string
        """
        warnings = []
        
        low_fields = analysis["low_confidence_fields"]
        medium_fields = analysis["medium_confidence_fields"]
        
        if low_fields:
            warnings.append(f"\n⚠️  LOW CONFIDENCE (< {LOW_CONFIDENCE_THRESHOLD}):")
            for col, score in low_fields:
                warnings.append(f"   - {col}: {score:.2f}")
        
        if medium_fields:
            warnings.append(f"\n⚠️  MEDIUM CONFIDENCE ({LOW_CONFIDENCE_THRESHOLD}-{MEDIUM_CONFIDENCE_THRESHOLD}):")
            for col, score in medium_fields:
                warnings.append(f"   - {col}: {score:.2f}")
        
        if warnings:
            return f"\n📄 {invoice_name}\n" + "\n".join(warnings)
        
        return ""
    
    @staticmethod
    def get_summary(all_analyses: List[Dict[str, Any]]) -> str:
        """
        Generate summary statistics for all processed invoices.
        
        Args:
            all_analyses: List of analysis dictionaries
            
        Returns:
            Summary string
        """
        if not all_analyses:
            return ""
        
        avg_confidences = [a["average_confidence"] for a in all_analyses]
        overall_avg = sum(avg_confidences) / len(avg_confidences)
        
        total_low = sum(len(a["low_confidence_fields"]) for a in all_analyses)
        total_medium = sum(len(a["medium_confidence_fields"]) for a in all_analyses)
        
        summary = [
            "\n" + "=" * 60,
            "CONFIDENCE SUMMARY",
            "=" * 60,
            f"Total invoices processed: {len(all_analyses)}",
            f"Overall average confidence: {overall_avg:.3f}",
            f"Total low-confidence fields: {total_low}",
            f"Total medium-confidence fields: {total_medium}",
            "=" * 60,
        ]
        
        return "\n".join(summary)
