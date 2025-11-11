"""GEO optimizer that orchestrates content transformations and calculates scores."""

from typing import Any, Dict, List, Optional

from src.analysis.gap_analyzer import GapAnalyzer, GapAnalysisResult
from src.audit.content_analyzer import ContentAnalyzer
from src.audit.geo_scorer import GEOScorer
from src.audit.technical_analyzer import TechnicalAnalyzer
from src.transformation.ai_client import AIClient
from src.transformation.content_transformer import ContentTransformer
from src.transformation.schema_generator import SchemaGenerator
from src.utils.logger import logger


class GEOOptimizer:
    """Orchestrate content transformations based on gap analysis."""

    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
        content_transformer: Optional[ContentTransformer] = None,
        schema_generator: Optional[SchemaGenerator] = None,
    ):
        """
        Initialize GEO optimizer.

        Args:
            ai_client: Optional AI client instance
            content_transformer: Optional content transformer instance
            schema_generator: Optional schema generator instance
        """
        self.ai_client = ai_client or AIClient()
        self.content_transformer = content_transformer or ContentTransformer(self.ai_client)
        self.schema_generator = schema_generator or SchemaGenerator()

        # Initialize analyzers
        self.content_analyzer = ContentAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.geo_scorer = GEOScorer()
        self.gap_analyzer = GapAnalyzer()

    def optimize(
        self,
        parsed_data: Dict[str, Any],
        gap_analysis: Optional[GapAnalysisResult] = None,
        apply_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Optimize content based on gap analysis.

        Args:
            parsed_data: Parsed data from crawler (contains text_content, headings, etc.)
            gap_analysis: Optional gap analysis result (will be generated if not provided)
            apply_all: If True, apply all transformations regardless of gaps

        Returns:
            Dictionary with:
            - original_score: Original GEO score
            - optimized_score: Optimized GEO score
            - transformations_applied: List of transformations applied
            - transformed_content: Optimized content
            - before_after_comparison: Detailed comparison
            - usage_stats: AI API usage statistics
        """
        logger.info("Starting GEO optimization")

        # Get original content
        original_content = parsed_data.get("text_content", "")
        original_html = parsed_data.get("html", "")

        # Calculate original GEO score
        original_content_analysis = self.content_analyzer.analyze(parsed_data)
        original_technical_analysis = self.technical_analyzer.analyze(parsed_data)
        original_score_result = self.geo_scorer.score(
            original_content_analysis, original_technical_analysis, parsed_data
        )
        original_score = original_score_result["total_score"]

        # Generate gap analysis if not provided
        if gap_analysis is None:
            # We need ExtractedContent for gap analysis, but we can work with parsed_data
            # For now, we'll create a simplified gap analysis based on content analysis
            gap_analysis = self._generate_gap_analysis_from_parsed_data(parsed_data)

        # Track transformations
        transformations_applied = []
        transformed_content = original_content
        transformed_html = original_html
        all_schema_markup = []

        # Extract topic/main question from content
        topic = self._extract_topic(parsed_data)
        main_question = self._extract_main_question(parsed_data, topic)

        # Apply transformations based on gap analysis
        improvements = gap_analysis.improvements if gap_analysis else []

        # Transform opening paragraph (if needed)
        if apply_all or any(
            imp.category == "structure"
            and "first paragraph" in imp.issue.lower()
            for imp in improvements
        ):
            logger.info("Transforming opening paragraph")
            opening_result = self.content_transformer.transform_opening(
                transformed_content, main_question
            )
            if "error" not in opening_result:
                transformed_content = opening_result["transformed_content"]
                transformations_applied.append({
                    "type": "opening",
                    "result": opening_result,
                })

        # Add statistics (if needed)
        if apply_all or any(imp.category == "statistics" for imp in improvements):
            logger.info("Adding statistics")
            stats_result = self.content_transformer.transform_add_statistics(
                transformed_content, topic
            )
            if "error" not in stats_result:
                transformed_content = stats_result["transformed_content"]
                transformations_applied.append({
                    "type": "statistics",
                    "result": stats_result,
                })

        # Add citations (if needed)
        if apply_all or any(imp.category == "citations" for imp in improvements):
            logger.info("Adding citations")
            citations_result = self.content_transformer.transform_add_citations(
                transformed_content, topic
            )
            if "error" not in citations_result:
                transformed_content = citations_result["transformed_content"]
                if citations_result.get("schema_markup"):
                    all_schema_markup.append(citations_result["schema_markup"])
                transformations_applied.append({
                    "type": "citations",
                    "result": citations_result,
                })

        # Add quotes (if needed)
        if apply_all or any(imp.category == "quotes" for imp in improvements):
            logger.info("Adding expert quotes")
            quotes_result = self.content_transformer.transform_add_quotes(
                transformed_content, topic
            )
            if "error" not in quotes_result:
                transformed_content = quotes_result["transformed_content"]
                if quotes_result.get("schema_markup"):
                    all_schema_markup.append(quotes_result["schema_markup"])
                transformations_applied.append({
                    "type": "quotes",
                    "result": quotes_result,
                })

        # Generate additional schema markup
        schema_markup = self._generate_comprehensive_schema(parsed_data, transformed_content)
        if schema_markup:
            all_schema_markup.append(schema_markup)

        # Update parsed_data with transformed content
        transformed_parsed_data = parsed_data.copy()
        transformed_parsed_data["text_content"] = transformed_content

        # Insert schema markup into HTML
        if all_schema_markup:
            transformed_html = self._insert_schema_markup(transformed_html, all_schema_markup)
            transformed_parsed_data["html"] = transformed_html

        # Re-calculate GEO score
        transformed_content_analysis = self.content_analyzer.analyze(transformed_parsed_data)
        transformed_technical_analysis = self.technical_analyzer.analyze(transformed_parsed_data)
        optimized_score_result = self.geo_scorer.score(
            transformed_content_analysis, transformed_technical_analysis, transformed_parsed_data
        )
        optimized_score = optimized_score_result["total_score"]

        # Generate before/after comparison
        before_after_comparison = self._generate_comparison(
            original_score_result,
            optimized_score_result,
            original_content_analysis,
            transformed_content_analysis,
        )

        # Get usage statistics
        usage_stats = self.ai_client.get_usage_stats()

        logger.info(
            f"Optimization complete: {original_score:.2f} -> {optimized_score:.2f} "
            f"(+{optimized_score - original_score:.2f})"
        )

        return {
            "original_score": original_score,
            "optimized_score": optimized_score,
            "score_improvement": optimized_score - original_score,
            "transformations_applied": transformations_applied,
            "transformed_content": transformed_content,
            "transformed_html": transformed_html,
            "schema_markup": "\n\n".join(all_schema_markup),
            "before_after_comparison": before_after_comparison,
            "usage_stats": usage_stats,
            "gap_analysis": gap_analysis.dict() if gap_analysis else None,
        }

    def _generate_gap_analysis_from_parsed_data(
        self, parsed_data: Dict[str, Any]
    ) -> GapAnalysisResult:
        """
        Generate gap analysis from parsed data.

        Args:
            parsed_data: Parsed data from crawler

        Returns:
            GapAnalysisResult
        """
        # This is a simplified version - in production, you'd use the full GapAnalyzer
        # For now, we'll create a basic gap analysis based on content analysis
        content_analysis = self.content_analyzer.analyze(parsed_data)
        text_content = parsed_data.get("text_content", "")
        word_count = len(text_content.split())

        # Create a minimal gap analysis
        from src.analysis.content_extractor import (
            ContentStatistics,
            ContentStructure,
            ExtractedContent,
        )

        # We need to create ExtractedContent-like structure
        # This is a workaround - ideally gap_analyzer would work directly with parsed_data
        stats = ContentStatistics(
            word_count=word_count,
            statistics_count=content_analysis["statistics_analysis"]["total_statistics"],
            citations_count=content_analysis["citations_analysis"]["total_citations"],
            quotes_count=content_analysis["expert_quotes_analysis"]["total_expert_indicators"],
        )

        structure = ContentStructure(headings=parsed_data.get("headings", []))

        # Determine content type
        url = parsed_data.get("url", "")
        content_type = "article"  # Default
        if any(word in url.lower() for word in ["blog", "post"]):
            content_type = "blog"
        elif any(word in url.lower() for word in ["product", "shop"]):
            content_type = "product_page"
        elif any(word in url.lower() for word in ["how-to", "guide", "tutorial"]):
            content_type = "how_to"

        extracted_content = ExtractedContent(
            main_content=text_content,
            content_type=content_type,
            statistics=stats,
            structure=structure,
        )

        return self.gap_analyzer.analyze(extracted_content)

    def _extract_topic(self, parsed_data: Dict[str, Any]) -> str:
        """
        Extract main topic from parsed data.

        Args:
            parsed_data: Parsed data from crawler

        Returns:
            Main topic string
        """
        # Try to get from meta tags
        meta_tags = parsed_data.get("meta_tags", {})
        if meta_tags.get("title"):
            return meta_tags["title"]

        # Try to get from first heading
        headings = parsed_data.get("headings", [])
        if headings:
            return headings[0].get("text", "")

        # Fallback to first sentence
        text_content = parsed_data.get("text_content", "")
        if text_content:
            return text_content.split(".")[0][:100]

        return "Unknown Topic"

    def _extract_main_question(self, parsed_data: Dict[str, Any], topic: str) -> str:
        """
        Extract main question from content.

        Args:
            parsed_data: Parsed data from crawler
            topic: Main topic

        Returns:
            Main question string
        """
        # Try to infer question from title/topic
        meta_tags = parsed_data.get("meta_tags", {})
        title = meta_tags.get("title", topic)

        # Common patterns: "What is...", "How to...", "Why..."
        if title.lower().startswith(("what", "how", "why", "when", "where", "who")):
            return title

        # Otherwise, create a question from the topic
        if "?" not in title:
            return f"What is {topic}?"

        return title

    def _generate_comprehensive_schema(
        self, parsed_data: Dict[str, Any], transformed_content: str
    ) -> str:
        """
        Generate comprehensive schema markup.

        Args:
            parsed_data: Parsed data from crawler
            transformed_content: Transformed content

        Returns:
            Schema markup HTML
        """
        meta_tags = parsed_data.get("meta_tags", {})
        url = parsed_data.get("url", "")

        # Generate Article schema
        article_data = {
            "title": meta_tags.get("title", "Article"),
            "description": meta_tags.get("description", ""),
            "url": url,
            "author_name": "Author",  # Should be extracted or provided
            "publish_date": None,  # Should be extracted from HTML
        }

        article_schema = self.schema_generator.generate_article_schema(**article_data)

        return article_schema

    def _insert_schema_markup(self, html: str, schema_markups: List[str]) -> str:
        """
        Insert schema markup into HTML.

        Args:
            html: Original HTML
            schema_markups: List of schema markup strings

        Returns:
            HTML with schema markup inserted
        """
        combined_schema = "\n\n".join(schema_markups)

        # Try to insert before </head>
        if "</head>" in html:
            html = html.replace("</head>", f"{combined_schema}\n</head>", 1)
        elif "<body>" in html:
            html = html.replace("<body>", f"<body>\n{combined_schema}\n", 1)
        else:
            # Append at the end
            html = f"{html}\n{combined_schema}"

        return html

    def _generate_comparison(
        self,
        original_score_result: Dict[str, Any],
        optimized_score_result: Dict[str, Any],
        original_content_analysis: Dict[str, Any],
        transformed_content_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate before/after comparison.

        Args:
            original_score_result: Original GEO score result
            optimized_score_result: Optimized GEO score result
            original_content_analysis: Original content analysis
            transformed_content_analysis: Transformed content analysis

        Returns:
            Comparison dictionary
        """
        original_breakdown = original_score_result.get("breakdown", {})
        optimized_breakdown = optimized_score_result.get("breakdown", {})

        comparison = {
            "scores": {
                "original": original_score_result["total_score"],
                "optimized": optimized_score_result["total_score"],
                "improvement": optimized_score_result["total_score"]
                - original_score_result["total_score"],
            },
            "breakdown_changes": {},
            "content_metrics": {
                "original": {
                    "statistics_count": original_content_analysis["statistics_analysis"][
                        "total_statistics"
                    ],
                    "citations_count": original_content_analysis["citations_analysis"][
                        "total_citations"
                    ],
                    "quotes_count": original_content_analysis["expert_quotes_analysis"][
                        "total_expert_indicators"
                    ],
                    "first_paragraph_words": original_content_analysis[
                        "first_paragraph_analysis"
                    ]["word_count"],
                },
                "optimized": {
                    "statistics_count": transformed_content_analysis["statistics_analysis"][
                        "total_statistics"
                    ],
                    "citations_count": transformed_content_analysis["citations_analysis"][
                        "total_citations"
                    ],
                    "quotes_count": transformed_content_analysis["expert_quotes_analysis"][
                        "total_expert_indicators"
                    ],
                    "first_paragraph_words": transformed_content_analysis[
                        "first_paragraph_analysis"
                    ]["word_count"],
                },
            },
        }

        # Calculate breakdown changes
        for key in original_breakdown:
            if key in optimized_breakdown:
                comparison["breakdown_changes"][key] = {
                    "original": original_breakdown[key],
                    "optimized": optimized_breakdown[key],
                    "change": optimized_breakdown[key] - original_breakdown[key],
                }

        return comparison

