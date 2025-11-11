"""Main entry point for GEO Autopilot MVP - CLI interface for end-to-end pipeline."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.config import settings
from src.audit.content_analyzer import ContentAnalyzer
from src.audit.crawler import WebCrawler
from src.audit.geo_scorer import GEOScorer
from src.audit.technical_analyzer import TechnicalAnalyzer
from src.transformation.geo_optimizer import GEOOptimizer
from src.utils.logger import logger


def run_audit(url: str, save_results: bool = True) -> dict:
    """
    Run a complete GEO audit on a URL.
    
    Args:
        url: URL to audit
        save_results: Whether to save results to file
        
    Returns:
        Dictionary with audit results
    """
    logger.info(f"Starting GEO audit for: {url}")
    
    # Initialize components
    crawler = WebCrawler()
    content_analyzer = ContentAnalyzer()
    technical_analyzer = TechnicalAnalyzer()
    geo_scorer = GEOScorer()
    
    # Fetch and parse URL
    html_response, error = crawler.fetch_url(url)
    if error:
        raise Exception(f"Failed to fetch URL: {error}")
    
    # Get HTML content from response
    html_content = str(html_response)
    parsed_data = crawler.parse_html(html_content, url)
    
    # Run analyses
    logger.info("Running content analysis...")
    content_analysis = content_analyzer.analyze(parsed_data)
    
    logger.info("Running technical analysis...")
    technical_analysis = technical_analyzer.analyze(parsed_data)
    
    # Calculate GEO score
    logger.info("Calculating GEO score...")
    score_result = geo_scorer.score(
        content_analysis,
        technical_analysis,
        parsed_data
    )
    
    audit_result = {
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
    
    # Save results if requested
    if save_results:
        output_dir = Path(settings.DATA_DIR) / "audits"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        url_safe = url.replace("https://", "").replace("http://", "").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{url_safe}_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(audit_result, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {filepath}")
    
    return audit_result


def run_optimization(url: str, apply_all: bool = False, save_results: bool = True) -> dict:
    """
    Run full optimization pipeline: audit + transformation.
    
    Args:
        url: URL to optimize
        apply_all: Apply all transformations regardless of gaps
        save_results: Whether to save results to file
        
    Returns:
        Dictionary with optimization results
    """
    logger.info(f"Starting GEO optimization for: {url}")
    
    # First, run audit to get baseline
    audit_result = run_audit(url, save_results=False)
    parsed_data = audit_result["parsed_data"]
    original_score = audit_result["geo_score"]["total_score"]
    
    logger.info(f"Original GEO score: {original_score:.2f}")
    
    # Run optimization
    logger.info("Running content optimization...")
    optimizer = GEOOptimizer()
    optimization_result = optimizer.optimize(
        parsed_data=parsed_data,
        apply_all=apply_all
    )
    
    # Combine results
    result = {
        "url": url,
        "optimization_date": datetime.now().isoformat(),
        "original_score": original_score,
        "optimized_score": optimization_result["optimized_score"],
        "score_improvement": optimization_result["score_improvement"],
        "transformations_applied": optimization_result["transformations_applied"],
        "transformed_content": optimization_result["transformed_content"],
        "schema_markup": optimization_result["schema_markup"],
        "before_after_comparison": optimization_result["before_after_comparison"],
        "usage_stats": optimization_result["usage_stats"],
        "audit_data": audit_result
    }
    
    # Save results if requested
    if save_results:
        output_dir = Path(settings.DATA_DIR) / "optimizations"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        url_safe = url.replace("https://", "").replace("http://", "").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{url_safe}_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {filepath}")
    
    return result


def print_audit_summary(audit_result: dict):
    """Print a formatted summary of audit results."""
    print("\n" + "="*60)
    print("GEO AUDIT RESULTS")
    print("="*60)
    print(f"URL: {audit_result['url']}")
    print(f"Date: {audit_result['audit_date']}")
    print(f"\nOverall GEO Score: {audit_result['geo_score']['total_score']:.2f}/100")
    print("\nScore Breakdown:")
    for category, score in audit_result['geo_score']['breakdown'].items():
        display_name = category.replace("_", " ").title()
        print(f"  - {display_name}: {score:.2f}")
    
    print("\nTop Recommendations:")
    recommendations = audit_result.get("recommendations", [])
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"  {i}. {rec}")
    
    print("="*60 + "\n")


def print_optimization_summary(optimization_result: dict):
    """Print a formatted summary of optimization results."""
    print("\n" + "="*60)
    print("GEO OPTIMIZATION RESULTS")
    print("="*60)
    print(f"URL: {optimization_result['url']}")
    print(f"Date: {optimization_result['optimization_date']}")
    print(f"\nScore Improvement:")
    print(f"  Before: {optimization_result['original_score']:.2f}/100")
    print(f"  After:  {optimization_result['optimized_score']:.2f}/100")
    print(f"  Change: {optimization_result['score_improvement']:+.2f}")
    
    print("\nTransformations Applied:")
    transformations = optimization_result.get("transformations_applied", [])
    if transformations:
        for i, trans in enumerate(transformations, 1):
            trans_type = trans.get("type", "unknown")
            print(f"  {i}. {trans_type}")
    else:
        print("  None")
    
    usage_stats = optimization_result.get("usage_stats", {})
    if usage_stats:
        print("\nAI API Usage:")
        print(f"  Total Tokens: {usage_stats.get('total_tokens', 0):,}")
        print(f"  Estimated Cost: ${usage_stats.get('cost_usd', 0):.4f}")
    
    print("="*60 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GEO Autopilot MVP - CLI for GEO audit and optimization"
    )
    parser.add_argument(
        "url",
        help="URL to audit or optimize"
    )
    parser.add_argument(
        "--mode",
        choices=["audit", "optimize"],
        default="audit",
        help="Operation mode: audit (default) or optimize"
    )
    parser.add_argument(
        "--apply-all",
        action="store_true",
        help="Apply all transformations (optimize mode only)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate API keys
    if not settings.validate():
        print("ERROR: No API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file.")
        sys.exit(1)
    
    try:
        if args.mode == "audit":
            result = run_audit(args.url, save_results=not args.no_save)
            
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print_audit_summary(result)
        
        elif args.mode == "optimize":
            result = run_optimization(args.url, apply_all=args.apply_all, save_results=not args.no_save)
            
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print_optimization_summary(result)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
