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
    Transform content based on selected options using GEOOptimizer.
    
    Args:
        parsed_data: Parsed data from crawler
        transformation_options: Dictionary with transformation flags:
            - add_statistics: Add statistics
            - add_citations: Add citations
            - add_expert_quotes: Add expert quotes
            - optimize_structure: Optimize structure (opening paragraph)
            - generate_schema: Generate schema markup
            
    Returns:
        Dictionary with transformation results:
        - original_content: Original text content
        - transformed_content: Transformed text content
        - original_score: Original GEO score
        - transformed_score: Transformed GEO score
        - transformations_applied: List of applied transformations
        - score_improvement: Score improvement
    """
    # Get original score
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
    original_content = parsed_data.get("text_content", "")
    
    # Use GEOOptimizer for transformations
    # If apply_all is True, it will apply all transformations
    # Otherwise, we need to check which ones are selected
    apply_all = all(transformation_options.values())
    
    # If specific options are selected, we'll use apply_all but filter results
    # For MVP, we'll use apply_all when any option is selected
    if not any(transformation_options.values()):
        # No transformations selected, return original
        return {
            "original_content": original_content,
            "transformed_content": original_content,
            "original_score": original_score,
            "transformed_score": original_score,
            "transformations_applied": [],
            "score_improvement": 0
        }
    
    # Run optimization
    optimizer = GEOOptimizer()
    optimization_result = optimizer.optimize(
        parsed_data=parsed_data,
        apply_all=apply_all
    )
    
    # Extract transformation types applied
    transformations_applied = []
    for trans in optimization_result.get("transformations_applied", []):
        trans_type = trans.get("type", "unknown")
        if trans_type == "opening":
            transformations_applied.append("Opening paragraph optimized")
        elif trans_type == "statistics":
            transformations_applied.append("Statistics added")
        elif trans_type == "citations":
            transformations_applied.append("Citations added")
        elif trans_type == "quotes":
            transformations_applied.append("Expert quotes added")
    
    # Add schema if requested
    if transformation_options.get("generate_schema") and optimization_result.get("schema_markup"):
        transformations_applied.append("Schema markup generated")
    
    return {
        "original_content": original_content,
        "transformed_content": optimization_result.get("transformed_content", original_content),
        "original_score": original_score,
        "transformed_score": optimization_result.get("optimized_score", original_score),
        "transformations_applied": transformations_applied,
        "score_improvement": optimization_result.get("score_improvement", 0),
        "schema_markup": optimization_result.get("schema_markup", ""),
        "usage_stats": optimization_result.get("usage_stats", {})
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

