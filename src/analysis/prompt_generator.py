"""Prompt generation module for AI content transformation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.analysis.content_extractor import ExtractedContent
from src.analysis.gap_analyzer import GapAnalysisResult, ImprovementItem
from src.utils.logger import logger


class TransformationPrompt(BaseModel):
    """Model representing a transformation prompt."""

    prompt_type: str = Field(
        description="Type of prompt: add_statistics, add_citations, add_quotes, rewrite_opening, other"
    )
    prompt: str = Field(description="The full prompt text")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the prompt",
    )
    original_content: str = Field(
        description="Original content snippet being transformed"
    )
    instructions: List[str] = Field(
        default_factory=list,
        description="Specific instructions for the transformation",
    )


class PromptGenerator:
    """Generate transformation prompts for AI content optimization."""

    def __init__(self):
        """Initialize the prompt generator."""
        self.logger = logger

    def generate_add_statistics_prompt(
        self,
        content: str,
        improvement: ImprovementItem,
        extracted_content: ExtractedContent,
    ) -> TransformationPrompt:
        """
        Generate prompt for adding statistics.

        Args:
            content: Content section where statistics should be added
            improvement: ImprovementItem for statistics gap
            extracted_content: Full extracted content for context

        Returns:
            TransformationPrompt for adding statistics
        """
        word_count = extracted_content.statistics.word_count
        current_stats = extracted_content.statistics.statistics_count
        target_stats = improvement.target_value
        needed = target_stats - current_stats

        # Suggest source types based on content type
        source_suggestions = self._get_statistics_source_suggestions(
            extracted_content.content_type
        )

        prompt_text = f"""Add {needed} relevant statistics or data points to the following content section.

CONTENT TO ENHANCE:
{content}

REQUIREMENTS:
1. Add {needed} statistics that are relevant to the content topic
2. Statistics should be factual, verifiable, and support the main points
3. Include context for each statistic (what it means, why it matters)
4. Integrate statistics naturally into the existing text flow
5. Use varied formats: percentages, numbers, research findings, industry data

SUGGESTED SOURCE TYPES:
{', '.join(source_suggestions)}

CONTENT TYPE: {extracted_content.content_type}
CURRENT STATISTICS COUNT: {current_stats}
TARGET STATISTICS COUNT: {target_stats}
WORD COUNT: {word_count} words

Please add the statistics in a way that enhances the content without disrupting the flow. Each statistic should be followed by brief context explaining its significance."""

        instructions = [
            f"Add {needed} statistics to the content",
            "Ensure statistics are relevant and factual",
            "Provide context for each statistic",
            "Maintain natural text flow",
        ]

        return TransformationPrompt(
            prompt_type="add_statistics",
            prompt=prompt_text,
            context={
                "needed_count": needed,
                "current_count": current_stats,
                "target_count": target_stats,
                "content_type": extracted_content.content_type,
                "source_suggestions": source_suggestions,
            },
            original_content=content,
            instructions=instructions,
        )

    def generate_add_citations_prompt(
        self,
        content: str,
        improvement: ImprovementItem,
        extracted_content: ExtractedContent,
    ) -> TransformationPrompt:
        """
        Generate prompt for adding citations.

        Args:
            content: Content section where citations should be added
            improvement: ImprovementItem for citations gap
            extracted_content: Full extracted content for context

        Returns:
            TransformationPrompt for adding citations
        """
        needed = improvement.target_value - improvement.current_value
        current_citations = extracted_content.statistics.citations

        # Suggest citation sources based on content
        source_suggestions = self._get_citation_source_suggestions(
            extracted_content.content_type, extracted_content.main_content[:500]
        )

        prompt_text = f"""Add {needed} authoritative citations to the following content section.

CONTENT TO ENHANCE:
{content}

REQUIREMENTS:
1. Add {needed} citations from authoritative sources
2. Citations should support key claims and statements
3. Use proper citation format (links, references, or inline citations)
4. Ensure citations are from reputable sources (research studies, industry reports, expert sources)
5. Integrate citations naturally without disrupting readability

SUGGESTED SOURCE TYPES:
{', '.join(source_suggestions)}

EXISTING CITATIONS IN CONTENT:
{len(current_citations)} citations found

CONTENT TYPE: {extracted_content.content_type}

Please add citations that:
- Support factual claims and statistics
- Reference authoritative sources
- Are relevant to the content topic
- Enhance credibility without overwhelming the reader

Format citations as:
- Inline links: [Source Name](URL)
- Reference style: (Author, Year) or [1]
- Natural integration: "According to [Source Name](URL)..."
"""

        instructions = [
            f"Add {needed} authoritative citations",
            "Support key claims with citations",
            "Use proper citation format",
            "Ensure sources are reputable",
            "Maintain readability",
        ]

        return TransformationPrompt(
            prompt_type="add_citations",
            prompt=prompt_text,
            context={
                "needed_count": needed,
                "current_count": improvement.current_value,
                "target_count": improvement.target_value,
                "content_type": extracted_content.content_type,
                "source_suggestions": source_suggestions,
            },
            original_content=content,
            instructions=instructions,
        )

    def generate_add_quotes_prompt(
        self,
        content: str,
        improvement: ImprovementItem,
        extracted_content: ExtractedContent,
    ) -> TransformationPrompt:
        """
        Generate prompt for adding expert quotes.

        Args:
            content: Content section where quotes should be added
            improvement: ImprovementItem for quotes gap
            extracted_content: Full extracted content for context

        Returns:
            TransformationPrompt for adding expert quotes
        """
        needed = improvement.target_value - improvement.current_value
        current_quotes = extracted_content.statistics.quotes

        prompt_text = f"""Add {needed} expert quotes to the following content section.

CONTENT TO ENHANCE:
{content}

REQUIREMENTS:
1. Add {needed} quotes from industry experts, researchers, or subject matter experts
2. Each quote should be relevant to the content topic and add value
3. Include proper attribution (expert name, title, organization)
4. Provide context before and after each quote
5. Quotes should be impactful and support key points
6. Vary quote length and style for natural integration

EXISTING QUOTES IN CONTENT:
{len(current_quotes)} quotes found

CONTENT TYPE: {extracted_content.content_type}

Please add expert quotes that:
- Come from credible experts in the field
- Support or enhance key arguments
- Include full attribution (name, title, organization)
- Are properly introduced and contextualized
- Add authority and credibility to the content

QUOTE FORMAT EXAMPLE:
"[Quote text here]," says [Expert Name], [Title] at [Organization]. "[Additional context or follow-up quote if needed]."

Or:

According to [Expert Name], [Title] at [Organization], "[Quote text here]."
"""

        instructions = [
            f"Add {needed} expert quotes",
            "Include proper attribution",
            "Provide context for each quote",
            "Ensure quotes add value",
            "Maintain natural flow",
        ]

        return TransformationPrompt(
            prompt_type="add_quotes",
            prompt=prompt_text,
            context={
                "needed_count": needed,
                "current_count": improvement.current_value,
                "target_count": improvement.target_value,
                "content_type": extracted_content.content_type,
            },
            original_content=content,
            instructions=instructions,
        )

    def generate_rewrite_opening_prompt(
        self,
        content: str,
        improvement: Optional[ImprovementItem],
        extracted_content: ExtractedContent,
    ) -> TransformationPrompt:
        """
        Generate prompt for rewriting opening paragraph (answer-first structure).

        Args:
            content: Opening paragraph/content to rewrite
            improvement: Optional ImprovementItem for structure issues
            extracted_content: Full extracted content for context

        Returns:
            TransformationPrompt for rewriting opening
        """
        target_length = improvement.target_value if improvement else 50
        current_length = len(content.split())

        prompt_text = f"""Rewrite the opening paragraph to follow answer-first structure for better GEO (Generative Engine Optimization) performance.

CURRENT OPENING:
{content}

REQUIREMENTS:
1. Start with a clear, direct answer to the main question or topic
2. Keep the opening paragraph between 20-{target_length} words
3. Provide the key information upfront (answer-first structure)
4. Make it scannable and easy for AI search engines to understand
5. Maintain engagement and readability
6. Set up the rest of the content naturally

CURRENT LENGTH: {current_length} words
TARGET LENGTH: 20-{target_length} words
CONTENT TYPE: {extracted_content.content_type}

ANSWER-FIRST STRUCTURE GUIDELINES:
- Lead with the answer or main point
- Be specific and concrete
- Avoid vague introductions or "in this article" phrases
- Make it immediately clear what the content is about
- Hook the reader while providing value upfront

EXAMPLE OF GOOD ANSWER-FIRST OPENING:
"AI-powered search engines prioritize content that answers questions directly. Here's how to optimize your content for GEO..."

Please rewrite the opening to be concise, direct, and answer-first while maintaining the core message and tone."""

        instructions = [
            "Rewrite opening in answer-first structure",
            f"Keep length between 20-{target_length} words",
            "Lead with the main answer or point",
            "Make it scannable and clear",
            "Maintain engagement",
        ]

        return TransformationPrompt(
            prompt_type="rewrite_opening",
            prompt=prompt_text,
            context={
                "current_length": current_length,
                "target_length": target_length,
                "content_type": extracted_content.content_type,
            },
            original_content=content,
            instructions=instructions,
        )

    def generate_prompts(
        self,
        extracted_content: ExtractedContent,
        gap_analysis: GapAnalysisResult,
        content_sections: Optional[Dict[str, str]] = None,
    ) -> List[TransformationPrompt]:
        """
        Generate all transformation prompts based on gap analysis.

        Args:
            extracted_content: Extracted content
            gap_analysis: Gap analysis results
            content_sections: Optional dict mapping improvement categories to content sections

        Returns:
            List of TransformationPrompts
        """
        prompts = []

        # Default content sections if not provided
        if content_sections is None:
            content_sections = {
                "statistics": extracted_content.main_content[:1000],
                "citations": extracted_content.main_content[:1000],
                "quotes": extracted_content.main_content[:1000],
                "structure": extracted_content.main_content.split("\n\n")[0] if extracted_content.main_content else "",
            }

        for improvement in gap_analysis.improvements:
            try:
                if improvement.category == "statistics":
                    prompt = self.generate_add_statistics_prompt(
                        content_sections.get("statistics", extracted_content.main_content),
                        improvement,
                        extracted_content,
                    )
                    prompts.append(prompt)

                elif improvement.category == "citations":
                    prompt = self.generate_add_citations_prompt(
                        content_sections.get("citations", extracted_content.main_content),
                        improvement,
                        extracted_content,
                    )
                    prompts.append(prompt)

                elif improvement.category == "quotes":
                    prompt = self.generate_add_quotes_prompt(
                        content_sections.get("quotes", extracted_content.main_content),
                        improvement,
                        extracted_content,
                    )
                    prompts.append(prompt)

                elif improvement.category == "structure":
                    if "first paragraph" in improvement.issue.lower() or "opening" in improvement.issue.lower():
                        opening_content = content_sections.get(
                            "structure",
                            extracted_content.main_content.split("\n\n")[0] if extracted_content.main_content else "",
                        )
                        prompt = self.generate_rewrite_opening_prompt(
                            opening_content,
                            improvement,
                            extracted_content,
                        )
                        prompts.append(prompt)

            except Exception as e:
                self.logger.error(f"Error generating prompt for {improvement.category}: {e}")
                continue

        return prompts

    def _get_statistics_source_suggestions(self, content_type: str) -> List[str]:
        """Get suggested source types for statistics based on content type."""
        suggestions_map = {
            "blog": [
                "Industry research reports",
                "Market studies",
                "Survey data",
                "Academic research",
                "Industry statistics",
            ],
            "product_page": [
                "Product performance data",
                "Customer satisfaction metrics",
                "Industry benchmarks",
                "Usage statistics",
            ],
            "landing_page": [
                "Conversion statistics",
                "Industry benchmarks",
                "Customer success metrics",
                "Market data",
            ],
            "how_to": [
                "Success rate statistics",
                "Time-saving metrics",
                "Effectiveness data",
                "Research findings",
            ],
            "article": [
                "Research studies",
                "Statistical reports",
                "Industry data",
                "Academic findings",
            ],
        }

        return suggestions_map.get(content_type, ["Research studies", "Industry data", "Statistical reports"])

    def _get_citation_source_suggestions(
        self, content_type: str, content_sample: str
    ) -> List[str]:
        """Get suggested citation source types based on content type and topic."""
        base_suggestions = [
            "Peer-reviewed research papers",
            "Industry reports from reputable organizations",
            "Government statistics and data",
            "Expert-authored articles",
            "Academic institutions",
        ]

        # Add type-specific suggestions
        type_suggestions = {
            "blog": ["Industry blogs", "Expert opinions", "Case studies"],
            "product_page": ["Product reviews", "User testimonials", "Performance studies"],
            "how_to": ["Tutorial sources", "Expert guides", "Best practice documents"],
        }

        suggestions = base_suggestions + type_suggestions.get(content_type, [])
        return suggestions[:5]  # Return top 5

