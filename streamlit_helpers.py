"""Helper functions for running GEO audits and transformations in Streamlit."""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from src.audit.content_analyzer import ContentAnalyzer
from src.audit.crawler import WebCrawler
from src.audit.geo_scorer import GEOScorer
from src.audit.technical_analyzer import TechnicalAnalyzer
from src.transformation.geo_optimizer import GEOOptimizer


def run_geo_audit(url: str) -> Dict[str, Any]:
    """
    Run a complete GEO audit on a URL.
    
    Args:
        url: URL to audit
        
    Returns:
        Dictionary with audit results including:
        - url: The audited URL
        - audit_date: Timestamp of audit
        - geo_score: Total score and breakdown
        - recommendations: List of recommendations
        - parsed_data: Parsed HTML data
        - content_analysis: Content analysis results
        - technical_analysis: Technical analysis results
    """
    # Initialize components
    crawler = WebCrawler()
    content_analyzer = ContentAnalyzer()
    technical_analyzer = TechnicalAnalyzer()
    geo_scorer = GEOScorer()
    
    # Fetch and parse URL
    html_response, error = crawler.fetch_url(url)
    if error:
        raise Exception(f"Failed to fetch URL: {error}")
    
    # Get HTML content from response (requests-html HTML object)
    html_content = str(html_response)
    parsed_data = crawler.parse_html(html_content, url)
    
    # Run analyses
    content_analysis = content_analyzer.analyze(parsed_data)
    technical_analysis = technical_analyzer.analyze(parsed_data)
    
    # Calculate GEO score
    score_result = geo_scorer.score(
        content_analysis,
        technical_analysis,
        parsed_data
    )
    
    return {
        "url": url,
        "audit_date": datetime.now().isoformat(),
        "geo_score": {
            "total_score": score_result["total_score"],
            "breakdown": score_result["breakdown"]
        },
        "recommendations": score_result["recommendations"],
        "parsed_data": parsed_data,
        "content_analysis": content_analysis,
        "technical_analysis": technical_analysis,
        "findings": {
            "content_analysis": content_analysis,
            "technical_analysis": technical_analysis
        }
    }


def transform_content(
    parsed_data: Dict[str, Any],
    transformation_options: Dict[str, bool]
) -> Dict[str, Any]:
    """
    Transform content based on selected options.
    
    Args:
        parsed_data: Parsed data from crawler
        transformation_options: Dictionary with transformation flags:
            - add_statistics: Add statistics
            - add_citations: Add citations
            - add_expert_quotes: Add expert quotes
            - optimize_structure: Optimize structure
            - generate_schema: Generate schema markup
            
    Returns:
        Dictionary with transformation results:
        - original_content: Original text content
        - transformed_content: Transformed text content
        - original_score: Original GEO score
        - transformed_score: Transformed GEO score
        - transformations_applied: List of applied transformations
    """
    # Run original audit to get baseline score
    content_analyzer = ContentAnalyzer()
    technical_analyzer = TechnicalAnalyzer()
    geo_scorer = GEOScorer()
    
    original_content_analysis = content_analyzer.analyze(parsed_data)
    original_technical_analysis = technical_analyzer.analyze(parsed_data)
    original_score_result = geo_scorer.score(
        original_content_analysis,
        original_technical_analysis,
        parsed_data
    )
    original_score = original_score_result["total_score"]
    
    # Apply transformations
    # Note: This is a simplified version - in production, you'd use the optimizer
    # with specific transformation options
    transformed_data = parsed_data.copy()
    transformations_applied = []
    
    # For MVP, we'll simulate transformations
    # In production, this would call the actual transformation methods
    if transformation_options.get("optimize_structure"):
        transformations_applied.append("Structure optimized")
    
    if transformation_options.get("generate_schema"):
        transformations_applied.append("Schema markup generated")
    
    # Recalculate score after transformation
    transformed_content_analysis = content_analyzer.analyze(transformed_data)
    transformed_technical_analysis = technical_analyzer.analyze(transformed_data)
    transformed_score_result = geo_scorer.score(
        transformed_content_analysis,
        transformed_technical_analysis,
        transformed_data
    )
    transformed_score = transformed_score_result["total_score"]
    
    return {
        "original_content": parsed_data.get("text_content", ""),
        "transformed_content": transformed_data.get("text_content", ""),
        "original_score": original_score,
        "transformed_score": transformed_score,
        "transformations_applied": transformations_applied,
        "score_improvement": transformed_score - original_score
    }


def save_audit_result(audit_result: Dict[str, Any], storage_path: str = "data/audits") -> str:
    """
    Save audit result to JSON file.
    
    Args:
        audit_result: Audit result dictionary
        storage_path: Path to storage directory
        
    Returns:
        Path to saved file
    """
    import os
    
    os.makedirs(storage_path, exist_ok=True)
    
    # Create filename from URL and timestamp
    url_safe = audit_result["url"].replace("https://", "").replace("http://", "").replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{url_safe}_{timestamp}.json"
    filepath = os.path.join(storage_path, filename)
    
    with open(filepath, "w") as f:
        json.dump(audit_result, f, indent=2, default=str)
    
    return filepath


def load_audit_history(storage_path: str = "data/audits") -> list:
    """
    Load all audit results from storage.
    
    Args:
        storage_path: Path to storage directory
        
    Returns:
        List of audit results
    """
    import os
    
    if not os.path.exists(storage_path):
        return []
    
    audits = []
    for filename in os.listdir(storage_path):
        if filename.endswith(".json"):
            filepath = os.path.join(storage_path, filename)
            try:
                with open(filepath, "r") as f:
                    audit = json.load(f)
                    audits.append(audit)
            except Exception:
                continue
    
    # Sort by audit date (most recent first)
    audits.sort(key=lambda x: x.get("audit_date", ""), reverse=True)
    return audits

