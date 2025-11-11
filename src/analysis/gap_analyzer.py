"""Gap analysis module for comparing content against GEO best practices."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.analysis.content_extractor import ExtractedContent
from src.utils.logger import logger


class ImprovementItem(BaseModel):
    """Model representing a single improvement recommendation."""

    priority: int = Field(
        description="Priority level (1=high, 2=medium, 3=low)",
        ge=1,
        le=3,
    )
    category: str = Field(description="Category: statistics, citations, quotes, structure")
    issue: str = Field(description="Description of the issue")
    recommendation: str = Field(description="Specific recommendation")
    current_value: Any = Field(description="Current value/metric")
    target_value: Any = Field(description="Target value/metric")
    impact_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Estimated impact on GEO score (0-100)",
    )


class GapAnalysisResult(BaseModel):
    """Model representing gap analysis results."""

    improvements: List[ImprovementItem] = Field(
        default_factory=list,
        description="List of prioritized improvements",
    )
    overall_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall compliance score (0-100)",
    )
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of gaps and compliance",
    )


class GapAnalyzer:
    """Analyze content gaps against GEO best practices."""

    # GEO Best Practice Thresholds
    STATS_PER_WORDS = 150  # Should have 1 statistic per 150-200 words
    MIN_CITATIONS = 3  # Minimum citations per page
    MAX_CITATIONS = 5  # Maximum citations per page
    MIN_EXPERT_QUOTES = 3  # Minimum expert quotes for major pages
    MAX_EXPERT_QUOTES = 4  # Maximum expert quotes for major pages
    FIRST_PARAGRAPH_MIN_WORDS = 20  # Minimum words in first paragraph
    FIRST_PARAGRAPH_MAX_WORDS = 50  # Maximum words in first paragraph (answer-first)

    def __init__(self):
        """Initialize the gap analyzer."""
        self.logger = logger

    def analyze_statistics_gap(
        self, word_count: int, statistics_count: int
    ) -> Optional[ImprovementItem]:
        """
        Analyze statistics gap.

        Args:
            word_count: Total word count
            statistics_count: Current statistics count

        Returns:
            ImprovementItem if gap exists, None otherwise
        """
        expected_stats = max(1, word_count // self.STATS_PER_WORDS)
        gap = expected_stats - statistics_count

        if gap > 0:
            # Calculate impact based on gap size
            impact = min(30.0, gap * 5.0)  # Max 30 points impact

            return ImprovementItem(
                priority=1 if gap >= 3 else 2,
                category="statistics",
                issue=f"Missing {gap} statistics. Content should have approximately 1 statistic per {self.STATS_PER_WORDS} words.",
                recommendation=f"Add {gap} relevant statistics or data points. Include percentages, numbers, or research findings that support your content.",
                current_value=statistics_count,
                target_value=expected_stats,
                impact_score=impact,
            )

        return None

    def analyze_citations_gap(
        self, citations_count: int
    ) -> Optional[ImprovementItem]:
        """
        Analyze citations gap.

        Args:
            citations_count: Current citations count

        Returns:
            ImprovementItem if gap exists, None otherwise
        """
        if citations_count < self.MIN_CITATIONS:
            gap = self.MIN_CITATIONS - citations_count
            impact = min(25.0, gap * 8.0)  # Max 25 points impact

            return ImprovementItem(
                priority=1,
                category="citations",
                issue=f"Missing {gap} citations. Content should have {self.MIN_CITATIONS}-{self.MAX_CITATIONS} citations per page.",
                recommendation=f"Add {gap} authoritative citations. Link to research studies, industry reports, or expert sources that support your claims.",
                current_value=citations_count,
                target_value=self.MIN_CITATIONS,
                impact_score=impact,
            )
        elif citations_count > self.MAX_CITATIONS:
            return ImprovementItem(
                priority=3,
                category="citations",
                issue=f"Too many citations ({citations_count}). Content should have {self.MIN_CITATIONS}-{self.MAX_CITATIONS} citations per page.",
                recommendation=f"Reduce citations to {self.MAX_CITATIONS} most relevant sources. Quality over quantity.",
                current_value=citations_count,
                target_value=self.MAX_CITATIONS,
                impact_score=5.0,
            )

        return None

    def analyze_quotes_gap(
        self, quotes_count: int, is_major_page: bool = True
    ) -> Optional[ImprovementItem]:
        """
        Analyze expert quotes gap.

        Args:
            quotes_count: Current quotes count
            is_major_page: Whether this is a major/important page

        Returns:
            ImprovementItem if gap exists, None otherwise
        """
        if not is_major_page:
            return None  # Quotes less critical for minor pages

        if quotes_count < self.MIN_EXPERT_QUOTES:
            gap = self.MIN_EXPERT_QUOTES - quotes_count
            impact = min(20.0, gap * 6.0)  # Max 20 points impact

            return ImprovementItem(
                priority=1 if gap >= 2 else 2,
                category="quotes",
                issue=f"Missing {gap} expert quotes. Major pages should have {self.MIN_EXPERT_QUOTES}-{self.MAX_EXPERT_QUOTES} expert quotes.",
                recommendation=f"Add {gap} expert quotes from industry leaders, researchers, or subject matter experts. Include attribution and context.",
                current_value=quotes_count,
                target_value=self.MIN_EXPERT_QUOTES,
                impact_score=impact,
            )
        elif quotes_count > self.MAX_EXPERT_QUOTES:
            return ImprovementItem(
                priority=3,
                category="quotes",
                issue=f"Too many quotes ({quotes_count}). Content should have {self.MIN_EXPERT_QUOTES}-{self.MAX_EXPERT_QUOTES} expert quotes.",
                recommendation=f"Reduce quotes to {self.MAX_EXPERT_QUOTES} most impactful ones. Focus on quality and relevance.",
                current_value=quotes_count,
                target_value=self.MAX_EXPERT_QUOTES,
                impact_score=3.0,
            )

        return None

    def analyze_structure_issues(
        self, content: str, structure: Any
    ) -> List[ImprovementItem]:
        """
        Analyze structural issues.

        Args:
            content: Main content text
            structure: ContentStructure object

        Returns:
            List of ImprovementItems for structural issues
        """
        improvements = []

        # Analyze first paragraph
        paragraphs = content.split("\n\n")
        if paragraphs:
            first_para = paragraphs[0].strip()
            first_para_words = len(first_para.split())

            if first_para_words < self.FIRST_PARAGRAPH_MIN_WORDS:
                improvements.append(
                    ImprovementItem(
                        priority=2,
                        category="structure",
                        issue=f"First paragraph too short ({first_para_words} words). Should be {self.FIRST_PARAGRAPH_MIN_WORDS}-{self.FIRST_PARAGRAPH_MAX_WORDS} words for answer-first structure.",
                        recommendation="Expand the first paragraph to provide a clear, concise answer upfront. This helps AI search engines understand the content immediately.",
                        current_value=first_para_words,
                        target_value=self.FIRST_PARAGRAPH_MAX_WORDS,
                        impact_score=15.0,
                    )
                )
            elif first_para_words > self.FIRST_PARAGRAPH_MAX_WORDS:
                improvements.append(
                    ImprovementItem(
                        priority=2,
                        category="structure",
                        issue=f"First paragraph too long ({first_para_words} words). Should be {self.FIRST_PARAGRAPH_MIN_WORDS}-{self.FIRST_PARAGRAPH_MAX_WORDS} words for answer-first structure.",
                        recommendation="Condense the first paragraph to provide a clear, concise answer upfront. Follow the answer-first structure for better GEO performance.",
                        current_value=first_para_words,
                        target_value=self.FIRST_PARAGRAPH_MAX_WORDS,
                        impact_score=15.0,
                    )
                )

        # Analyze heading hierarchy
        headings = structure.headings if hasattr(structure, "headings") else []
        if headings:
            # Check for proper hierarchy (h1 should come first, then h2, etc.)
            levels = [h.get("level", 0) for h in headings]
            if levels:
                # Check if h1 exists
                if 1 not in levels:
                    improvements.append(
                        ImprovementItem(
                            priority=2,
                            category="structure",
                            issue="Missing H1 heading. Content should have a clear H1 heading.",
                            recommendation="Add an H1 heading that clearly describes the main topic of the page.",
                            current_value="No H1",
                            target_value="1 H1",
                            impact_score=10.0,
                        )
                    )

                # Check for hierarchy jumps (e.g., h1 -> h3 without h2)
                prev_level = None
                for level in levels:
                    if prev_level is not None:
                        if level > prev_level + 1:
                            improvements.append(
                                ImprovementItem(
                                    priority=3,
                                    category="structure",
                                    issue=f"Heading hierarchy jump detected (level {prev_level} to {level}). Headings should follow proper hierarchy.",
                                    recommendation="Ensure headings follow proper hierarchy (H1 -> H2 -> H3, etc.) without skipping levels.",
                                    current_value=f"Jump from {prev_level} to {level}",
                                    target_value="Sequential hierarchy",
                                    impact_score=5.0,
                                )
                            )
                            break  # Only report first issue
                    prev_level = level

        return improvements

    def calculate_overall_score(
        self, content: ExtractedContent, improvements: List[ImprovementItem]
    ) -> float:
        """
        Calculate overall compliance score.

        Args:
            content: Extracted content
            improvements: List of improvements needed

        Returns:
            Overall score (0-100)
        """
        base_score = 100.0

        # Deduct points for each improvement needed
        for improvement in improvements:
            base_score -= improvement.impact_score

        # Ensure score is within bounds
        return max(0.0, min(100.0, base_score))

    def analyze(
        self, extracted_content: ExtractedContent, is_major_page: bool = True
    ) -> GapAnalysisResult:
        """
        Perform complete gap analysis.

        Args:
            extracted_content: ExtractedContent object from ContentExtractor
            is_major_page: Whether this is a major/important page

        Returns:
            GapAnalysisResult with prioritized improvements
        """
        improvements = []

        stats = extracted_content.statistics
        structure = extracted_content.structure

        # Analyze statistics gap
        stats_improvement = self.analyze_statistics_gap(
            stats.word_count, stats.statistics_count
        )
        if stats_improvement:
            improvements.append(stats_improvement)

        # Analyze citations gap
        citations_improvement = self.analyze_citations_gap(stats.citations_count)
        if citations_improvement:
            improvements.append(citations_improvement)

        # Analyze quotes gap
        quotes_improvement = self.analyze_quotes_gap(
            stats.quotes_count, is_major_page
        )
        if quotes_improvement:
            improvements.append(quotes_improvement)

        # Analyze structure issues
        structure_improvements = self.analyze_structure_issues(
            extracted_content.main_content, structure
        )
        improvements.extend(structure_improvements)

        # Sort by priority (1=high, 2=medium, 3=low) and then by impact score
        improvements.sort(key=lambda x: (x.priority, -x.impact_score))

        # Calculate overall score
        overall_score = self.calculate_overall_score(extracted_content, improvements)

        # Create summary
        summary = {
            "total_improvements": len(improvements),
            "high_priority": len([i for i in improvements if i.priority == 1]),
            "medium_priority": len([i for i in improvements if i.priority == 2]),
            "low_priority": len([i for i in improvements if i.priority == 3]),
            "by_category": {
                "statistics": len([i for i in improvements if i.category == "statistics"]),
                "citations": len([i for i in improvements if i.category == "citations"]),
                "quotes": len([i for i in improvements if i.category == "quotes"]),
                "structure": len([i for i in improvements if i.category == "structure"]),
            },
            "current_metrics": {
                "word_count": stats.word_count,
                "statistics_count": stats.statistics_count,
                "citations_count": stats.citations_count,
                "quotes_count": stats.quotes_count,
            },
        }

        return GapAnalysisResult(
            improvements=improvements,
            overall_score=overall_score,
            summary=summary,
        )

