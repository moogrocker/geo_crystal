"""Content transformation functions using AI."""

import json
import re
from typing import Any, Dict, List, Optional

from src.transformation.ai_client import AIClient
from src.utils.logger import logger


class ContentTransformer:
    """Transform content using AI to improve GEO score."""

    def __init__(self, ai_client: Optional[AIClient] = None):
        """
        Initialize content transformer.

        Args:
            ai_client: Optional AI client instance (creates new one if not provided)
        """
        self.ai_client = ai_client or AIClient()

    def transform_add_statistics(
        self, content: str, topic: str, num_statistics: int = 6
    ) -> Dict[str, Any]:
        """
        Add relevant statistics to content using AI.

        Args:
            content: Original content
            topic: Main topic of the content
            num_statistics: Number of statistics to generate (5-7 recommended)

        Returns:
            Dictionary with:
            - transformed_content: Content with statistics inserted
            - statistics: List of generated statistics with sources
            - insertion_points: List of where statistics were inserted
        """
        # Validate topic before proceeding
        if not topic or not isinstance(topic, str) or len(topic.strip()) < 3:
            logger.warning(f"Invalid topic provided for statistics generation: '{topic}'")
            return {
                "transformed_content": content,
                "statistics": [],
                "insertion_points": [],
                "error": f"Invalid topic: '{topic}'. Cannot generate statistics.",
            }
        
        topic = topic.strip()
        # Check for placeholder/error messages
        invalid_patterns = ["unknown topic", "content extraction incomplete", "failed to extract"]
        if any(pattern in topic.lower() for pattern in invalid_patterns):
            logger.warning(f"Topic appears to be a placeholder/error message: '{topic}'")
            return {
                "transformed_content": content,
                "statistics": [],
                "insertion_points": [],
                "error": f"Topic extraction failed: '{topic}'. Cannot generate statistics.",
            }
        
        num_statistics = max(5, min(7, num_statistics))  # Clamp to 5-7

        system_prompt = """You are an expert content writer specializing in data-driven articles.
Your task is to generate relevant, accurate statistics that enhance content credibility.
Always provide real, verifiable statistics when possible, or clearly indicate if a statistic is illustrative.
Format statistics with proper attribution and sources."""

        user_prompt = f"""Given the following content about "{topic}", generate {num_statistics} relevant statistics that would enhance this content.

Content:
{content}

Requirements:
1. Generate {num_statistics} statistics (between 5-7)
2. Each statistic should be relevant to the content topic
3. Include a source or attribution for each statistic
4. Format each statistic as JSON with: {{"statistic": "the statistic text", "source": "source name/URL", "context": "where to insert this"}}
5. Return ONLY a JSON array of statistics, no other text

Return format:
[
  {{
    "statistic": "According to [source], [statistic]",
    "source": "Source name or URL",
    "context": "Brief context about where this fits in the content"
  }},
  ...
]"""

        try:
            response = self.ai_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000,
            )

            content_text = response["content"].strip()

            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r"\[.*\]", content_text, re.DOTALL)
            if json_match:
                content_text = json_match.group(0)

            statistics = json.loads(content_text)

            # Validate statistics format
            validated_statistics = []
            for stat in statistics:
                if isinstance(stat, dict) and "statistic" in stat:
                    validated_statistics.append({
                        "statistic": stat.get("statistic", ""),
                        "source": stat.get("source", "Unknown"),
                        "context": stat.get("context", ""),
                    })

            if len(validated_statistics) < num_statistics:
                logger.warning(
                    f"Generated {len(validated_statistics)} statistics, requested {num_statistics}"
                )

            # Insert statistics into content naturally
            transformed_content, insertion_points = self._insert_statistics(
                content, validated_statistics
            )

            return {
                "transformed_content": transformed_content,
                "statistics": validated_statistics,
                "insertion_points": insertion_points,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse statistics JSON: {e}")
            return {
                "transformed_content": content,
                "statistics": [],
                "insertion_points": [],
                "error": "Failed to parse AI response",
            }

        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return {
                "transformed_content": content,
                "statistics": [],
                "insertion_points": [],
                "error": str(e),
            }

    def _insert_statistics(
        self, content: str, statistics: List[Dict[str, Any]]
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Insert statistics into content at natural points.

        Args:
            content: Original content
            statistics: List of statistics to insert

        Returns:
            Tuple of (transformed_content, insertion_points)
        """
        paragraphs = content.split("\n\n")
        insertion_points = []

        # Insert statistics after relevant paragraphs
        stats_used = 0
        transformed_paragraphs = []

        for i, paragraph in enumerate(paragraphs):
            transformed_paragraphs.append(paragraph)

            # Insert statistic after every 2-3 paragraphs (distribute evenly)
            if stats_used < len(statistics) and i > 0 and (i + 1) % 2 == 0:
                stat = statistics[stats_used]
                stat_text = f"{stat['statistic']} (Source: {stat['source']})"
                transformed_paragraphs.append(f"\n\n{stat_text}\n")
                insertion_points.append({
                    "position": len("\n\n".join(transformed_paragraphs)),
                    "statistic": stat["statistic"],
                    "source": stat["source"],
                })
                stats_used += 1

        # Add remaining statistics at the end if any
        while stats_used < len(statistics):
            stat = statistics[stats_used]
            stat_text = f"{stat['statistic']} (Source: {stat['source']})"
            transformed_paragraphs.append(f"\n\n{stat_text}\n")
            insertion_points.append({
                "position": len("\n\n".join(transformed_paragraphs)),
                "statistic": stat["statistic"],
                "source": stat["source"],
            })
            stats_used += 1

        transformed_content = "\n\n".join(transformed_paragraphs)

        return transformed_content, insertion_points

    def transform_add_citations(
        self, content: str, topic: str, num_citations: int = 4
    ) -> Dict[str, Any]:
        """
        Add authoritative citations to content.

        Args:
            content: Original content
            topic: Main topic of the content
            num_citations: Number of citations to generate (3-5 recommended)

        Returns:
            Dictionary with:
            - transformed_content: Content with citations added
            - citations: List of citations with HTML markup
            - schema_markup: Citation schema markup
        """
        # Validate topic before proceeding
        if not topic or not isinstance(topic, str) or len(topic.strip()) < 3:
            logger.warning(f"Invalid topic provided for citations generation: '{topic}'")
            return {
                "transformed_content": content,
                "citations": [],
                "citations_html": "",
                "schema_markup": "",
                "error": f"Invalid topic: '{topic}'. Cannot generate citations.",
            }
        
        topic = topic.strip()
        # Check for placeholder/error messages
        invalid_patterns = ["unknown topic", "content extraction incomplete", "failed to extract"]
        if any(pattern in topic.lower() for pattern in invalid_patterns):
            logger.warning(f"Topic appears to be a placeholder/error message: '{topic}'")
            return {
                "transformed_content": content,
                "citations": [],
                "citations_html": "",
                "schema_markup": "",
                "error": f"Topic extraction failed: '{topic}'. Cannot generate citations.",
            }
        
        num_citations = max(3, min(5, num_citations))  # Clamp to 3-5

        system_prompt = """You are an expert researcher specializing in finding authoritative sources.
Your task is to identify and suggest authoritative citations that enhance content credibility.
Suggest real, reputable sources when possible (academic papers, industry reports, government sources, etc.)."""

        user_prompt = f"""Given the following content about "{topic}", generate {num_citations} authoritative citations that would enhance this content.

Content:
{content}

Requirements:
1. Generate {num_citations} citations (between 3-5)
2. Each citation should be to an authoritative, reputable source
3. Include proper HTML markup with <a> tags
4. Format each citation as JSON with: {{"title": "citation title", "url": "https://...", "description": "brief description", "authority": "why this is authoritative"}}
5. Return ONLY a JSON array of citations, no other text

Return format:
[
  {{
    "title": "Citation Title",
    "url": "https://example.com/source",
    "description": "Brief description of the source",
    "authority": "Why this source is authoritative"
  }},
  ...
]"""

        try:
            response = self.ai_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2000,
            )

            content_text = response["content"].strip()

            # Extract JSON from response
            json_match = re.search(r"\[.*\]", content_text, re.DOTALL)
            if json_match:
                content_text = json_match.group(0)

            citations_data = json.loads(content_text)

            # Validate and format citations
            citations = []
            for cit in citations_data:
                if isinstance(cit, dict) and "title" in cit and "url" in cit:
                    citations.append({
                        "title": cit.get("title", ""),
                        "url": cit.get("url", ""),
                        "description": cit.get("description", ""),
                        "authority": cit.get("authority", ""),
                    })

            # Generate HTML markup for citations
            citations_html = self._format_citations_html(citations)

            # Insert citations into content
            transformed_content = self._insert_citations(content, citations_html)

            # Generate citation schema markup
            schema_markup = self._generate_citation_schema(citations)

            return {
                "transformed_content": transformed_content,
                "citations": citations,
                "citations_html": citations_html,
                "schema_markup": schema_markup,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse citations JSON: {e}")
            return {
                "transformed_content": content,
                "citations": [],
                "citations_html": "",
                "schema_markup": "",
                "error": "Failed to parse AI response",
            }

        except Exception as e:
            logger.error(f"Error generating citations: {e}")
            return {
                "transformed_content": content,
                "citations": [],
                "citations_html": "",
                "schema_markup": "",
                "error": str(e),
            }

    def _format_citations_html(self, citations: List[Dict[str, Any]]) -> str:
        """
        Format citations as HTML.

        Args:
            citations: List of citation dictionaries

        Returns:
            HTML formatted citations
        """
        html_parts = ['<div class="citations">', "<h3>References</h3>", "<ul>"]

        for cit in citations:
            html_parts.append(
                f'<li><a href="{cit["url"]}" rel="nofollow noopener" target="_blank">'
                f'{cit["title"]}</a> - {cit["description"]}</li>'
            )

        html_parts.extend(["</ul>", "</div>"])

        return "\n".join(html_parts)

    def _insert_citations(self, content: str, citations_html: str) -> str:
        """
        Insert citations HTML into content.

        Args:
            content: Original content
            citations_html: HTML formatted citations

        Returns:
            Content with citations inserted
        """
        # Insert citations before the end of the content
        # Look for common ending patterns
        ending_patterns = [
            r"</article>",
            r"</main>",
            r"</div>",
        ]

        inserted = False
        for pattern in ending_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(
                    pattern, f"{citations_html}\n{pattern}", content, count=1, flags=re.IGNORECASE
                )
                inserted = True
                break

        if not inserted:
            # Append at the end
            content = f"{content}\n\n{citations_html}"

        return content

    def _generate_citation_schema(self, citations: List[Dict[str, Any]]) -> str:
        """
        Generate JSON-LD schema markup for citations.

        Args:
            citations: List of citation dictionaries

        Returns:
            JSON-LD schema markup as string
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "citation": [],
        }

        for cit in citations:
            schema["citation"].append({
                "@type": "CreativeWork",
                "name": cit["title"],
                "url": cit["url"],
            })

        return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'

    def transform_add_quotes(
        self, content: str, topic: str, num_quotes: int = 4
    ) -> Dict[str, Any]:
        """
        Add expert quotes to content.

        Args:
            content: Original content
            topic: Main topic of the content
            num_quotes: Number of quotes to generate (3-4 recommended)

        Returns:
            Dictionary with:
            - transformed_content: Content with quotes added
            - quotes: List of quotes with attribution
            - schema_markup: Quote schema markup
        """
        # Validate topic before proceeding
        if not topic or not isinstance(topic, str) or len(topic.strip()) < 3:
            logger.warning(f"Invalid topic provided for quotes generation: '{topic}'")
            return {
                "transformed_content": content,
                "quotes": [],
                "quotes_html": "",
                "schema_markup": "",
                "error": f"Invalid topic: '{topic}'. Cannot generate quotes.",
            }
        
        topic = topic.strip()
        # Check for placeholder/error messages
        invalid_patterns = ["unknown topic", "content extraction incomplete", "failed to extract"]
        if any(pattern in topic.lower() for pattern in invalid_patterns):
            logger.warning(f"Topic appears to be a placeholder/error message: '{topic}'")
            return {
                "transformed_content": content,
                "quotes": [],
                "quotes_html": "",
                "schema_markup": "",
                "error": f"Topic extraction failed: '{topic}'. Cannot generate quotes.",
            }
        
        num_quotes = max(3, min(4, num_quotes))  # Clamp to 3-4

        system_prompt = """You are an expert content writer specializing in authoritative content.
Your task is to generate or suggest expert quotes that enhance content credibility.
When possible, suggest real quotes from known experts. If generating illustrative quotes, make them realistic and attribute them appropriately."""

        user_prompt = f"""Given the following content about "{topic}", generate {num_quotes} expert quotes that would enhance this content.

Content:
{content}

Requirements:
1. Generate {num_quotes} expert quotes (between 3-4)
2. Each quote should be from a credible expert or authority
3. Include proper attribution (name, title, organization)
4. Format each quote as JSON with: {{"quote": "the quote text", "author": "expert name", "title": "their title", "organization": "organization name", "context": "where to insert this"}}
5. Return ONLY a JSON array of quotes, no other text

Return format:
[
  {{
    "quote": "The quote text here",
    "author": "Expert Name",
    "title": "Their Title",
    "organization": "Organization Name",
    "context": "Brief context about where this fits"
  }},
  ...
]"""

        try:
            response = self.ai_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000,
            )

            content_text = response["content"].strip()

            # Extract JSON from response
            json_match = re.search(r"\[.*\]", content_text, re.DOTALL)
            if json_match:
                content_text = json_match.group(0)

            quotes_data = json.loads(content_text)

            # Validate and format quotes
            quotes = []
            for quote in quotes_data:
                if isinstance(quote, dict) and "quote" in quote and "author" in quote:
                    quotes.append({
                        "quote": quote.get("quote", ""),
                        "author": quote.get("author", ""),
                        "title": quote.get("title", ""),
                        "organization": quote.get("organization", ""),
                        "context": quote.get("context", ""),
                    })

            # Format quotes with HTML
            quotes_html = self._format_quotes_html(quotes)

            # Insert quotes into content
            transformed_content = self._insert_quotes(content, quotes)

            # Generate quote schema markup
            schema_markup = self._generate_quote_schema(quotes)

            return {
                "transformed_content": transformed_content,
                "quotes": quotes,
                "quotes_html": quotes_html,
                "schema_markup": schema_markup,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quotes JSON: {e}")
            return {
                "transformed_content": content,
                "quotes": [],
                "quotes_html": "",
                "schema_markup": "",
                "error": "Failed to parse AI response",
            }

        except Exception as e:
            logger.error(f"Error generating quotes: {e}")
            return {
                "transformed_content": content,
                "quotes": [],
                "quotes_html": "",
                "schema_markup": "",
                "error": str(e),
            }

    def _format_quotes_html(self, quotes: List[Dict[str, Any]]) -> str:
        """
        Format quotes as HTML with proper attribution.

        Args:
            quotes: List of quote dictionaries

        Returns:
            HTML formatted quotes
        """
        html_parts = []

        for quote in quotes:
            attribution = f"{quote['author']}"
            if quote.get("title"):
                attribution += f", {quote['title']}"
            if quote.get("organization"):
                attribution += f", {quote['organization']}"

            html_parts.append(
                f'<blockquote cite="{quote.get("url", "")}">\n'
                f'  <p>"{quote["quote"]}"</p>\n'
                f'  <footer>— <cite>{attribution}</cite></footer>\n'
                f"</blockquote>"
            )

        return "\n\n".join(html_parts)

    def _insert_quotes(self, content: str, quotes: List[Dict[str, Any]]) -> str:
        """
        Insert quotes into content at natural points.

        Args:
            content: Original content
            quotes: List of quotes to insert

        Returns:
            Content with quotes inserted
        """
        paragraphs = content.split("\n\n")
        transformed_paragraphs = []
        quotes_used = 0

        for i, paragraph in enumerate(paragraphs):
            transformed_paragraphs.append(paragraph)

            # Insert quote after every 3-4 paragraphs
            if quotes_used < len(quotes) and i > 0 and (i + 1) % 3 == 0:
                quote = quotes[quotes_used]
                attribution = f"{quote['author']}"
                if quote.get("title"):
                    attribution += f", {quote['title']}"
                if quote.get("organization"):
                    attribution += f", {quote['organization']}"

                quote_html = (
                    f'<blockquote>\n  <p>"{quote["quote"]}"</p>\n'
                    f'  <footer>— <cite>{attribution}</cite></footer>\n</blockquote>'
                )
                transformed_paragraphs.append(f"\n\n{quote_html}\n")
                quotes_used += 1

        # Add remaining quotes at the end if any
        while quotes_used < len(quotes):
            quote = quotes[quotes_used]
            attribution = f"{quote['author']}"
            if quote.get("title"):
                attribution += f", {quote['title']}"
            if quote.get("organization"):
                attribution += f", {quote['organization']}"

            quote_html = (
                f'<blockquote>\n  <p>"{quote["quote"]}"</p>\n'
                f'  <footer>— <cite>{attribution}</cite></footer>\n</blockquote>'
            )
            transformed_paragraphs.append(f"\n\n{quote_html}\n")
            quotes_used += 1

        return "\n\n".join(transformed_paragraphs)

    def _generate_quote_schema(self, quotes: List[Dict[str, Any]]) -> str:
        """
        Generate JSON-LD schema markup for quotes.

        Args:
            quotes: List of quote dictionaries

        Returns:
            JSON-LD schema markup as string
        """
        schema_items = []

        for quote in quotes:
            schema_item = {
                "@type": "Quote",
                "text": quote["quote"],
                "author": {
                    "@type": "Person",
                    "name": quote["author"],
                },
            }

            if quote.get("organization"):
                schema_item["author"]["affiliation"] = {
                    "@type": "Organization",
                    "name": quote["organization"],
                }

            schema_items.append(schema_item)

        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "hasPart": schema_items,
        }

        return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'

    def transform_opening(
        self, content: str, main_question: str, target_length: int = 50
    ) -> Dict[str, Any]:
        """
        Rewrite opening paragraph to answer main question directly (40-60 words).

        Args:
            content: Original content
            main_question: Main question the content should answer
            target_length: Target word count (40-60 words recommended)

        Returns:
            Dictionary with:
            - transformed_content: Content with rewritten opening
            - original_opening: Original first paragraph
            - new_opening: New first paragraph
            - word_count: Word count of new opening
        """
        target_length = max(40, min(60, target_length))  # Clamp to 40-60

        # Extract first paragraph
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

        original_opening = paragraphs[0] if paragraphs else ""

        system_prompt = """You are an expert content writer specializing in SEO and answer-first content structure.
Your task is to rewrite opening paragraphs to directly answer the main question in 40-60 words.
Maintain the original tone and style while ensuring the answer is clear and direct."""

        user_prompt = f"""Rewrite the following opening paragraph to directly answer this question: "{main_question}"

Original opening paragraph:
{original_opening}

Requirements:
1. Answer the question directly in the first sentence
2. Keep the paragraph between 40-60 words
3. Maintain the original tone and style
4. Be clear, concise, and informative
5. Return ONLY the rewritten paragraph, no other text

Rewritten opening paragraph:"""

        try:
            response = self.ai_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=200,
            )

            new_opening = response["content"].strip()

            # Remove quotes if AI added them
            new_opening = re.sub(r'^["\']|["\']$', "", new_opening)

            word_count = len(new_opening.split())

            # Replace first paragraph in content
            if paragraphs:
                paragraphs[0] = new_opening
                transformed_content = "\n\n".join(paragraphs)
            else:
                transformed_content = new_opening

            return {
                "transformed_content": transformed_content,
                "original_opening": original_opening,
                "new_opening": new_opening,
                "word_count": word_count,
                "meets_target": 40 <= word_count <= 60,
            }

        except Exception as e:
            logger.error(f"Error rewriting opening: {e}")
            return {
                "transformed_content": content,
                "original_opening": original_opening,
                "new_opening": original_opening,
                "word_count": len(original_opening.split()),
                "error": str(e),
            }

