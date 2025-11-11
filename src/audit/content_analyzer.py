"""Content analyzer for website audits."""

import re
from typing import Any, Dict, List, Optional

import textstat

from src.utils.logger import logger


class ContentAnalyzer:
    """Analyzer for content quality and structure."""

    def __init__(self):
        """Initialize the content analyzer."""
        pass

    def analyze_first_paragraph(self, text_content: str) -> Dict[str, Any]:
        """
        Check if first paragraph answers main question (40-60 words).

        Args:
            text_content: Full text content

        Returns:
            Dictionary with first paragraph analysis:
            - first_paragraph: Text of first paragraph
            - word_count: Word count of first paragraph
            - meets_length: Boolean (40-60 words)
            - score: Score for this metric (0-100)
        """
        # Extract first paragraph
        paragraphs = [p.strip() for p in text_content.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in text_content.split("\n") if p.strip()]

        if not paragraphs:
            return {
                "first_paragraph": "",
                "word_count": 0,
                "meets_length": False,
                "score": 0
            }

        first_paragraph = paragraphs[0]
        word_count = len(first_paragraph.split())

        # Check if word count is in optimal range (40-60 words)
        meets_length = 40 <= word_count <= 60

        # Calculate score
        score = 0
        if meets_length:
            score = 100
        elif 30 <= word_count < 40 or 60 < word_count <= 70:
            score = 70  # Close to optimal
        elif 20 <= word_count < 30 or 70 < word_count <= 80:
            score = 50  # Acceptable
        elif word_count > 0:
            score = 30  # Too short or too long

        return {
            "first_paragraph": first_paragraph[:200],  # Truncate for display
            "word_count": word_count,
            "meets_length": meets_length,
            "score": score
        }

    def count_statistics_and_numbers(self, text_content: str) -> Dict[str, Any]:
        """
        Count statistics and numbers in content.

        Args:
            text_content: Full text content

        Returns:
            Dictionary with statistics analysis:
            - number_count: Count of numeric values
            - percentage_count: Count of percentages
            - statistic_phrases: Count of statistic-related phrases
            - total_statistics: Total count of statistics indicators
            - score: Score based on statistics presence (0-100)
        """
        # Count numbers (integers and decimals)
        number_pattern = r'\b\d+\.?\d*\b'
        numbers = re.findall(number_pattern, text_content)
        number_count = len(numbers)

        # Count percentages
        percentage_pattern = r'\d+\.?\d*\s*%'
        percentages = re.findall(percentage_pattern, text_content)
        percentage_count = len(percentages)

        # Count statistic-related phrases
        statistic_phrases = [
            r'\b\d+\s*(percent|%)',
            r'\b\d+\s*(million|billion|thousand)',
            r'\b(study|research|survey|data|statistic)',
            r'\b(according to|research shows|studies indicate)',
        ]
        statistic_phrase_count = 0
        for pattern in statistic_phrases:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            statistic_phrase_count += len(matches)

        total_statistics = number_count + percentage_count + statistic_phrase_count

        # Calculate score (more statistics = better, up to a point)
        if total_statistics >= 10:
            score = 100
        elif total_statistics >= 5:
            score = 75
        elif total_statistics >= 3:
            score = 50
        elif total_statistics >= 1:
            score = 25
        else:
            score = 0

        return {
            "number_count": number_count,
            "percentage_count": percentage_count,
            "statistic_phrases": statistic_phrase_count,
            "total_statistics": total_statistics,
            "score": min(score, 100)
        }

    def detect_citations_and_links(self, links: List[Dict], text_content: str) -> Dict[str, Any]:
        """
        Detect citations and external links.

        Args:
            links: List of link dictionaries
            text_content: Full text content

        Returns:
            Dictionary with citation analysis:
            - external_link_count: Count of external links
            - citation_patterns: Count of citation patterns
            - has_citations: Boolean
            - score: Score based on citations (0-100)
        """
        external_link_count = sum(1 for link in links if link.get("is_external", False))

        # Detect citation patterns
        citation_patterns = [
            r'\([A-Z][a-z]+ et al\.?\s+\d{4}\)',  # (Author et al. 2024)
            r'\[?\d+\]?',  # [1] or 1
            r'\(source:',  # (source: ...)
            r'according to',
            r'cited in',
            r'reference',
            r'study by',
            r'research from',
        ]
        citation_count = 0
        for pattern in citation_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            citation_count += len(matches)

        has_citations = external_link_count > 0 or citation_count > 0

        # Calculate score
        total_citations = external_link_count + citation_count
        if total_citations >= 5:
            score = 100
        elif total_citations >= 3:
            score = 75
        elif total_citations >= 1:
            score = 50
        else:
            score = 0

        return {
            "external_link_count": external_link_count,
            "citation_patterns": citation_count,
            "has_citations": has_citations,
            "total_citations": total_citations,
            "score": min(score, 100)
        }

    def count_expert_quotes(self, text_content: str) -> Dict[str, Any]:
        """
        Count expert quotes in content.

        Args:
            text_content: Full text content

        Returns:
            Dictionary with expert quote analysis:
            - quote_count: Count of quoted text
            - expert_indicators: Count of expert-related phrases
            - score: Score based on expert quotes (0-100)
        """
        # Count quoted text (text within quotes)
        quote_patterns = [
            r'"[^"]{20,}"',  # Double quotes with substantial content
            r''[^']{20,}'',  # Single quotes with substantial content
            r'"[^"]{20,}"',  # Smart quotes
        ]
        quote_count = 0
        for pattern in quote_patterns:
            matches = re.findall(pattern, text_content)
            quote_count += len(matches)

        # Count expert-related phrases
        expert_indicators = [
            r'(expert|specialist|professor|doctor|researcher|analyst)',
            r'(says|states|explains|notes|according to)',
            r'(interview|quoted|statement)',
        ]
        expert_indicator_count = 0
        for pattern in expert_indicators:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            expert_indicator_count += len(matches)

        # Calculate score
        total_expert_indicators = quote_count + expert_indicator_count
        if total_expert_indicators >= 3:
            score = 100
        elif total_expert_indicators >= 2:
            score = 75
        elif total_expert_indicators >= 1:
            score = 50
        else:
            score = 0

        return {
            "quote_count": quote_count,
            "expert_indicators": expert_indicator_count,
            "total_expert_indicators": total_expert_indicators,
            "score": min(score, 100)
        }

    def assess_readability(self, text_content: str) -> Dict[str, Any]:
        """
        Assess content readability using Flesch Reading Ease score.

        Args:
            text_content: Full text content

        Returns:
            Dictionary with readability analysis:
            - flesch_score: Flesch Reading Ease score
            - reading_level: Estimated reading level
            - score: Normalized score (0-100) for GEO purposes
        """
        if not text_content or len(text_content.split()) < 10:
            return {
                "flesch_score": 0,
                "reading_level": "Unknown",
                "score": 0
            }

        try:
            flesch_score = textstat.flesch_reading_ease(text_content)
            flesch_kincaid = textstat.flesch_kincaid_grade(text_content)

            # Determine reading level
            if flesch_score >= 90:
                reading_level = "Very Easy"
            elif flesch_score >= 80:
                reading_level = "Easy"
            elif flesch_score >= 70:
                reading_level = "Fairly Easy"
            elif flesch_score >= 60:
                reading_level = "Standard"
            elif flesch_score >= 50:
                reading_level = "Fairly Difficult"
            elif flesch_score >= 30:
                reading_level = "Difficult"
            else:
                reading_level = "Very Difficult"

            # For GEO, we want content that's readable but not too simple
            # Optimal range: 60-80 (Standard to Easy)
            if 60 <= flesch_score <= 80:
                score = 100
            elif 50 <= flesch_score < 60 or 80 < flesch_score <= 90:
                score = 75
            elif 40 <= flesch_score < 50 or 90 < flesch_score <= 100:
                score = 50
            elif flesch_score >= 30:
                score = 25
            else:
                score = 0

        except Exception as e:
            logger.warning(f"Readability calculation failed: {e}")
            return {
                "flesch_score": 0,
                "reading_level": "Unknown",
                "score": 0
            }

        return {
            "flesch_score": round(flesch_score, 2),
            "flesch_kincaid_grade": round(flesch_kincaid, 2),
            "reading_level": reading_level,
            "score": min(score, 100)
        }

    def analyze(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete content analysis.

        Args:
            parsed_data: Dictionary from crawler.parse_html()

        Returns:
            Dictionary with content analysis results:
            - first_paragraph_analysis: First paragraph analysis
            - statistics_analysis: Statistics and numbers analysis
            - citations_analysis: Citations and links analysis
            - expert_quotes_analysis: Expert quotes analysis
            - readability_analysis: Readability analysis
            - content_score: Overall content score (0-100)
        """
        text_content = parsed_data.get("text_content", "")
        links = parsed_data.get("links", [])

        first_paragraph_analysis = self.analyze_first_paragraph(text_content)
        statistics_analysis = self.count_statistics_and_numbers(text_content)
        citations_analysis = self.detect_citations_and_links(links, text_content)
        expert_quotes_analysis = self.count_expert_quotes(text_content)
        readability_analysis = self.assess_readability(text_content)

        # Calculate overall content score
        # Weighted average of all components
        content_score = (
            (first_paragraph_analysis["score"] * 0.25) +
            (statistics_analysis["score"] * 0.20) +
            (citations_analysis["score"] * 0.25) +
            (expert_quotes_analysis["score"] * 0.15) +
            (readability_analysis["score"] * 0.15)
        )

        return {
            "first_paragraph_analysis": first_paragraph_analysis,
            "statistics_analysis": statistics_analysis,
            "citations_analysis": citations_analysis,
            "expert_quotes_analysis": expert_quotes_analysis,
            "readability_analysis": readability_analysis,
            "content_score": round(content_score, 2)
        }

