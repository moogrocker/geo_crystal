"""GEO scoring algorithm implementation."""

from typing import Any, Dict, List, Optional

from src.utils.logger import logger


class GEOScorer:
    """GEO scoring algorithm based on blueprint specifications."""

    # Scoring weights from blueprint
    SCORING_WEIGHTS = {
        "answer_first": 20,  # 20 points
        "fact_density": 15,  # 15 points
        "citations": 15,  # 15 points
        "structure": 15,  # 15 points
        "schema": 15,  # 15 points
        "readability": 10,  # 10 points
        "uniqueness": 10,  # 10 points
    }

    def __init__(self):
        """Initialize the GEO scorer."""
        pass

    def calculate_answer_first_score(self, first_paragraph_analysis: Dict) -> float:
        """
        Calculate Answer First score (20 points max).

        Args:
            first_paragraph_analysis: Analysis from ContentAnalyzer

        Returns:
            Score out of 20 points
        """
        score = first_paragraph_analysis.get("score", 0)
        # Convert 0-100 score to 0-20 points
        return (score / 100) * 20

    def calculate_fact_density_score(self, statistics_analysis: Dict, expert_quotes_analysis: Dict) -> float:
        """
        Calculate Fact Density score (15 points max).

        Args:
            statistics_analysis: Statistics analysis from ContentAnalyzer
            expert_quotes_analysis: Expert quotes analysis from ContentAnalyzer

        Returns:
            Score out of 15 points
        """
        stats_score = statistics_analysis.get("score", 0)
        expert_score = expert_quotes_analysis.get("score", 0)

        # Combine statistics and expert quotes (60% stats, 40% expert quotes)
        combined_score = (stats_score * 0.6) + (expert_score * 0.4)

        # Convert 0-100 score to 0-15 points
        return (combined_score / 100) * 15

    def calculate_citations_score(self, citations_analysis: Dict) -> float:
        """
        Calculate Citations score (15 points max).

        Args:
            citations_analysis: Citations analysis from ContentAnalyzer

        Returns:
            Score out of 15 points
        """
        score = citations_analysis.get("score", 0)
        # Convert 0-100 score to 0-15 points
        return (score / 100) * 15

    def calculate_structure_score(self, headings_analysis: Dict) -> float:
        """
        Calculate Structure score (15 points max).

        Args:
            headings_analysis: Headings analysis from TechnicalAnalyzer

        Returns:
            Score out of 15 points
        """
        score = headings_analysis.get("structure_score", 0)
        # Convert 0-100 score to 0-15 points
        return (score / 100) * 15

    def calculate_schema_score(self, schema_analysis: Dict) -> float:
        """
        Calculate Schema score (15 points max).

        Args:
            schema_analysis: Schema analysis from TechnicalAnalyzer

        Returns:
            Score out of 15 points
        """
        has_schema = schema_analysis.get("has_schema", False)
        valid_types = schema_analysis.get("valid_types", [])

        score = 0

        # Base score for having schema (8 points)
        if has_schema:
            score += 8

        # Bonus for valid GEO-optimized types (7 points max)
        if valid_types:
            # More valid types = better, up to 7 points
            type_bonus = min(len(valid_types) * 2, 7)
            score += type_bonus

        return min(score, 15)

    def calculate_readability_score(self, readability_analysis: Dict) -> float:
        """
        Calculate Readability score (10 points max).

        Args:
            readability_analysis: Readability analysis from ContentAnalyzer

        Returns:
            Score out of 10 points
        """
        score = readability_analysis.get("score", 0)
        # Convert 0-100 score to 0-10 points
        return (score / 100) * 10

    def calculate_uniqueness_score(self, text_content: str, word_count: int) -> float:
        """
        Calculate Uniqueness score (10 points max).

        This is a basic implementation. A full implementation would compare
        against other content sources.

        Args:
            text_content: Full text content
            word_count: Word count of content

        Returns:
            Score out of 10 points
        """
        # Basic heuristic: longer, unique content scores better
        # In production, this would compare against known sources

        if word_count < 300:
            return 3  # Too short, likely not unique
        elif word_count < 500:
            return 5  # Moderate length
        elif word_count < 1000:
            return 7  # Good length
        elif word_count < 2000:
            return 9  # Excellent length
        else:
            return 10  # Very comprehensive

    def generate_recommendations(self, breakdown: Dict[str, float]) -> List[str]:
        """
        Generate recommendations based on score breakdown.

        Args:
            breakdown: Dictionary of score components

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Answer First recommendations
        if breakdown.get("answer_first", 0) < 15:
            recommendations.append(
                "Optimize first paragraph to be 40-60 words and directly answer the main question"
            )

        # Fact Density recommendations
        if breakdown.get("fact_density", 0) < 10:
            recommendations.append(
                "Add more statistics, numbers, and expert quotes to increase fact density"
            )

        # Citations recommendations
        if breakdown.get("citations", 0) < 10:
            recommendations.append(
                "Add external links and citations to authoritative sources to improve credibility"
            )

        # Structure recommendations
        if breakdown.get("structure", 0) < 10:
            recommendations.append(
                "Improve heading hierarchy: ensure single H1 tag and proper H2-H6 structure"
            )

        # Schema recommendations
        if breakdown.get("schema", 0) < 10:
            recommendations.append(
                "Add structured data (JSON-LD) markup for Article, FAQPage, or other relevant schema types"
            )

        # Readability recommendations
        if breakdown.get("readability", 0) < 7:
            recommendations.append(
                "Improve readability: aim for Flesch Reading Ease score between 60-80"
            )

        # Uniqueness recommendations
        if breakdown.get("uniqueness", 0) < 7:
            recommendations.append(
                "Expand content length and ensure unique, original content (aim for 500+ words)"
            )

        return recommendations

    def score(
        self,
        content_analysis: Dict,
        technical_analysis: Dict,
        parsed_data: Dict,
    ) -> Dict[str, Any]:
        """
        Calculate complete GEO score.

        Args:
            content_analysis: Results from ContentAnalyzer.analyze()
            technical_analysis: Results from TechnicalAnalyzer.analyze()
            parsed_data: Parsed data from crawler

        Returns:
            Dictionary with GEO score breakdown:
            - total_score: Total GEO score (0-100)
            - breakdown: Dictionary of individual component scores
            - recommendations: List of improvement recommendations
        """
        # Extract analysis components
        first_paragraph_analysis = content_analysis.get("first_paragraph_analysis", {})
        statistics_analysis = content_analysis.get("statistics_analysis", {})
        citations_analysis = content_analysis.get("citations_analysis", {})
        expert_quotes_analysis = content_analysis.get("expert_quotes_analysis", {})
        readability_analysis = content_analysis.get("readability_analysis", {})

        headings_analysis = technical_analysis.get("headings_analysis", {})
        schema_analysis = technical_analysis.get("schema_analysis", {})

        text_content = parsed_data.get("text_content", "")
        word_count = len(text_content.split())

        # Calculate individual scores
        answer_first = self.calculate_answer_first_score(first_paragraph_analysis)
        fact_density = self.calculate_fact_density_score(statistics_analysis, expert_quotes_analysis)
        citations = self.calculate_citations_score(citations_analysis)
        structure = self.calculate_structure_score(headings_analysis)
        schema = self.calculate_schema_score(schema_analysis)
        readability = self.calculate_readability_score(readability_analysis)
        uniqueness = self.calculate_uniqueness_score(text_content, word_count)

        # Create breakdown
        breakdown = {
            "answer_first": round(answer_first, 2),
            "fact_density": round(fact_density, 2),
            "citations": round(citations, 2),
            "structure": round(structure, 2),
            "schema": round(schema, 2),
            "readability": round(readability, 2),
            "uniqueness": round(uniqueness, 2),
        }

        # Calculate total score
        total_score = sum(breakdown.values())

        # Generate recommendations
        recommendations = self.generate_recommendations(breakdown)

        return {
            "total_score": round(total_score, 2),
            "breakdown": breakdown,
            "recommendations": recommendations,
            "max_possible_score": 100.0
        }

