"""Demo data and sample URLs for GEO Autopilot MVP."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Sample URLs for demo
SAMPLE_URLS = [
    {
        "url": "https://example.com/article/what-is-artificial-intelligence",
        "title": "What is Artificial Intelligence?",
        "description": "A comprehensive guide to understanding AI"
    },
    {
        "url": "https://example.com/blog/how-to-start-a-business",
        "title": "How to Start a Business in 2024",
        "description": "Step-by-step guide for entrepreneurs"
    },
    {
        "url": "https://example.com/guide/climate-change-solutions",
        "title": "Climate Change Solutions: What Works",
        "description": "Evidence-based approaches to combat climate change"
    }
]


def create_demo_audit_result(url: str, title: str, description: str) -> Dict[str, Any]:
    """
    Create a demo audit result with realistic scores.
    
    Args:
        url: URL of the page
        title: Page title
        description: Page description
        
    Returns:
        Demo audit result dictionary
    """
    # Generate realistic scores (between 45-75 for demo)
    import random
    base_score = random.randint(45, 75)
    
    return {
        "url": url,
        "audit_date": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
        "geo_score": {
            "total_score": base_score,
            "breakdown": {
                "first_paragraph_score": max(0, min(100, base_score + random.randint(-10, 10))),
                "statistics_score": max(0, min(100, base_score + random.randint(-15, 15))),
                "citations_score": max(0, min(100, base_score + random.randint(-20, 10))),
                "expert_quotes_score": max(0, min(100, base_score + random.randint(-25, 5))),
                "readability_score": max(0, min(100, base_score + random.randint(-5, 15))),
                "headings_structure_score": max(0, min(100, base_score + random.randint(-10, 10))),
                "schema_score": max(0, min(100, base_score + random.randint(-30, 10)))
            }
        },
        "recommendations": [
            "Add more statistics and data points to improve fact density",
            "Include expert quotes from industry leaders",
            "Add external citations to authoritative sources",
            "Optimize the first paragraph to directly answer the main question",
            "Generate structured data (JSON-LD) schema markup"
        ],
        "parsed_data": {
            "url": url,
            "title": title,
            "text_content": f"{title}\n\n{description}\n\nThis is a sample article about {title.lower()}. "
                           f"It contains some basic information but could benefit from additional statistics, "
                           f"citations, and expert quotes to improve its GEO score.",
            "headings": [
                {"level": 1, "text": title},
                {"level": 2, "text": "Introduction"},
                {"level": 2, "text": "Key Points"},
                {"level": 2, "text": "Conclusion"}
            ],
            "meta_tags": {
                "title": title,
                "description": description
            }
        },
        "content_analysis": {
            "first_paragraph_analysis": {
                "word_count": random.randint(20, 80),
                "meets_length": False,
                "score": max(0, min(100, base_score + random.randint(-15, 15)))
            },
            "statistics_analysis": {
                "statistics_count": random.randint(0, 3),
                "score": max(0, min(100, base_score + random.randint(-20, 10)))
            },
            "citations_analysis": {
                "external_links_count": random.randint(0, 2),
                "score": max(0, min(100, base_score + random.randint(-25, 5)))
            },
            "expert_quotes_analysis": {
                "quotes_count": random.randint(0, 1),
                "score": max(0, min(100, base_score + random.randint(-30, 0)))
            },
            "readability_analysis": {
                "flesch_reading_ease": random.randint(50, 80),
                "score": max(0, min(100, base_score + random.randint(-10, 15)))
            }
        },
        "technical_analysis": {
            "headings_analysis": {
                "h1_count": 1,
                "total_headings": 4,
                "structure_score": max(0, min(100, base_score + random.randint(-10, 10)))
            },
            "schema_analysis": {
                "has_schema": random.choice([True, False]),
                "schema_types": ["Article"] if random.choice([True, False]) else [],
                "valid_types": []
            }
        }
    }


def load_demo_audits() -> List[Dict[str, Any]]:
    """
    Load or create demo audit results.
    
    Returns:
        List of demo audit results
    """
    demo_dir = Path("data/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    audits = []
    
    # Create demo audits for sample URLs
    for sample in SAMPLE_URLS:
        demo_file = demo_dir / f"{sample['url'].replace('https://', '').replace('/', '_')}.json"
        
        if demo_file.exists():
            # Load existing demo audit
            try:
                with open(demo_file, "r") as f:
                    audit = json.load(f)
                    audits.append(audit)
            except Exception:
                # If loading fails, create new one
                audit = create_demo_audit_result(
                    sample["url"],
                    sample["title"],
                    sample["description"]
                )
                with open(demo_file, "w") as f:
                    json.dump(audit, f, indent=2, default=str)
                audits.append(audit)
        else:
            # Create new demo audit
            audit = create_demo_audit_result(
                sample["url"],
                sample["title"],
                sample["description"]
            )
            with open(demo_file, "w") as f:
                json.dump(audit, f, indent=2, default=str)
            audits.append(audit)
    
    return audits


def get_demo_audit_by_url(url: str) -> Dict[str, Any]:
    """
    Get a demo audit result by URL.
    
    Args:
        url: URL to get demo audit for
        
    Returns:
        Demo audit result or None if not found
    """
    demo_audits = load_demo_audits()
    for audit in demo_audits:
        if audit["url"] == url:
            return audit
    
    # If URL not in sample list, create a generic demo
    return create_demo_audit_result(url, "Sample Article", "A sample article for demonstration")


def is_demo_mode() -> bool:
    """
    Check if demo mode is enabled (via environment variable or config).
    
    Returns:
        True if demo mode is enabled
    """
    import os
    return os.getenv("GEO_DEMO_MODE", "false").lower() == "true"

