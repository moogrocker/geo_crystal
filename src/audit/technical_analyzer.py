"""Technical analyzer for website audits."""

import json
from typing import Any, Dict, List, Optional

from src.utils.logger import logger


class TechnicalAnalyzer:
    """Analyzer for technical aspects of a website."""

    # Valid schema.org types for GEO optimization
    VALID_SCHEMA_TYPES = [
        "Article",
        "BlogPosting",
        "NewsArticle",
        "Organization",
        "Person",
        "FAQPage",
        "HowTo",
        "Recipe",
        "Product",
        "Review",
        "VideoObject",
        "BreadcrumbList",
        "WebSite",
        "WebPage"
    ]

    def __init__(self):
        """Initialize the technical analyzer."""
        pass

    def check_schema_markup(self, schema_markup: List[Dict], microdata: List[Dict]) -> Dict[str, Any]:
        """
        Check for schema markup presence and validate types.

        Args:
            schema_markup: List of JSON-LD schema objects
            microdata: List of microdata objects

        Returns:
            Dictionary with schema analysis results:
            - has_schema: Boolean
            - schema_types: List of found schema types
            - valid_types: List of valid GEO-optimized types
            - invalid_types: List of invalid types
            - schema_count: Total number of schema objects
        """
        all_schema_types = []
        valid_types = []
        invalid_types = []

        # Process JSON-LD schema
        for schema in schema_markup:
            schema_type = schema.get("@type", "")
            if schema_type:
                all_schema_types.append(schema_type)
                if schema_type in self.VALID_SCHEMA_TYPES:
                    valid_types.append(schema_type)
                else:
                    invalid_types.append(schema_type)

        # Process microdata
        for item in microdata:
            schema_type = item.get("@type", "")
            if schema_type:
                all_schema_types.append(schema_type)
                if schema_type in self.VALID_SCHEMA_TYPES:
                    valid_types.append(schema_type)
                else:
                    invalid_types.append(schema_type)

        return {
            "has_schema": len(all_schema_types) > 0,
            "schema_types": list(set(all_schema_types)),
            "valid_types": list(set(valid_types)),
            "invalid_types": list(set(invalid_types)),
            "schema_count": len(schema_markup) + len(microdata)
        }

    def analyze_headings_structure(self, headings: List[Dict]) -> Dict[str, Any]:
        """
        Analyze heading hierarchy and structure.

        Args:
            headings: List of heading dictionaries with 'level' and 'text' keys

        Returns:
            Dictionary with heading analysis:
            - has_h1: Boolean
            - h1_count: Number of H1 tags
            - heading_hierarchy: Dictionary of heading counts by level
            - structure_score: Score based on proper hierarchy (0-100)
        """
        if not headings:
            return {
                "has_h1": False,
                "h1_count": 0,
                "heading_hierarchy": {},
                "structure_score": 0
            }

        h1_count = sum(1 for h in headings if h.get("level") == 1)
        has_h1 = h1_count > 0

        # Count headings by level
        heading_hierarchy = {}
        for level in range(1, 7):
            heading_hierarchy[f"h{level}"] = sum(1 for h in headings if h.get("level") == level)

        # Calculate structure score
        structure_score = 0

        # H1 presence (30 points)
        if has_h1 and h1_count == 1:
            structure_score += 30
        elif has_h1 and h1_count > 1:
            structure_score += 15  # Multiple H1s are not ideal

        # Proper hierarchy (40 points)
        # Check if headings follow logical order (h1 -> h2 -> h3, etc.)
        if headings:
            levels = [h.get("level") for h in headings]
            proper_hierarchy = True
            for i in range(len(levels) - 1):
                if levels[i + 1] > levels[i] + 1:  # Skip levels (e.g., h1 -> h3)
                    proper_hierarchy = False
                    break
            if proper_hierarchy:
                structure_score += 40

        # Heading density (30 points)
        # Good content has reasonable number of headings
        total_headings = len(headings)
        if 3 <= total_headings <= 20:
            structure_score += 30
        elif total_headings > 20:
            structure_score += 15  # Too many headings

        return {
            "has_h1": has_h1,
            "h1_count": h1_count,
            "heading_hierarchy": heading_hierarchy,
            "structure_score": min(structure_score, 100)
        }

    def check_core_web_vitals_indicators(self, html: str, meta_tags: Dict) -> Dict[str, Any]:
        """
        Check indicators related to Core Web Vitals.

        Note: This is a basic check. Full CWV requires actual performance metrics.

        Args:
            html: HTML content
            meta_tags: Dictionary of meta tags

        Returns:
            Dictionary with CWV indicators:
            - has_viewport: Boolean
            - has_preload: Boolean for preload hints
            - has_defer: Boolean for deferred scripts
            - image_count: Number of images
            - has_lazy_loading: Boolean for lazy loading images
            - cwv_score: Estimated score (0-100)
        """
        has_viewport = "viewport" in meta_tags
        has_preload = "preload" in html.lower() or "rel=\"preload\"" in html.lower()
        has_defer = "defer" in html.lower()

        # Count images (basic indicator)
        image_count = html.count("<img")

        # Check for lazy loading
        has_lazy_loading = "loading=\"lazy\"" in html.lower() or "loading='lazy'" in html.lower()

        # Calculate basic CWV score
        cwv_score = 0
        if has_viewport:
            cwv_score += 25
        if has_preload:
            cwv_score += 20
        if has_defer:
            cwv_score += 20
        if has_lazy_loading:
            cwv_score += 20
        if image_count < 50:  # Reasonable image count
            cwv_score += 15

        return {
            "has_viewport": has_viewport,
            "has_preload": has_preload,
            "has_defer": has_defer,
            "image_count": image_count,
            "has_lazy_loading": has_lazy_loading,
            "cwv_score": min(cwv_score, 100)
        }

    def analyze(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete technical analysis.

        Args:
            parsed_data: Dictionary from crawler.parse_html()

        Returns:
            Dictionary with technical analysis results:
            - schema_analysis: Schema markup analysis
            - headings_analysis: Heading structure analysis
            - cwv_analysis: Core Web Vitals indicators
            - technical_score: Overall technical score (0-100)
        """
        schema_markup = parsed_data.get("schema_markup", [])
        microdata = parsed_data.get("microdata", [])
        headings = parsed_data.get("headings", [])
        html = parsed_data.get("html", "")
        meta_tags = parsed_data.get("meta_tags", {})

        schema_analysis = self.check_schema_markup(schema_markup, microdata)
        headings_analysis = self.analyze_headings_structure(headings)
        cwv_analysis = self.check_core_web_vitals_indicators(html, meta_tags)

        # Calculate overall technical score
        # Schema: 40%, Headings: 35%, CWV: 25%
        technical_score = (
            (schema_analysis["has_schema"] * 40) +
            (headings_analysis["structure_score"] * 0.35) +
            (cwv_analysis["cwv_score"] * 0.25)
        )

        # Bonus for valid schema types
        if schema_analysis["valid_types"]:
            technical_score += min(len(schema_analysis["valid_types"]) * 5, 10)

        technical_score = min(technical_score, 100)

        return {
            "schema_analysis": schema_analysis,
            "headings_analysis": headings_analysis,
            "cwv_analysis": cwv_analysis,
            "technical_score": round(technical_score, 2)
        }

