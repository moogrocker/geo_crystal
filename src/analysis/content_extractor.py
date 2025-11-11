"""Content extraction module for preparing pages for transformation."""

import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from newspaper import Article
from pydantic import BaseModel, Field

from src.utils.logger import logger


class ContentStructure(BaseModel):
    """Model representing the structure of extracted content."""

    headings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of headings with level and text",
    )
    paragraphs: List[str] = Field(
        default_factory=list,
        description="List of paragraph texts",
    )
    lists: List[List[str]] = Field(
        default_factory=list,
        description="List of list items grouped by list",
    )
    links: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of links with text and URL",
    )


class ContentStatistics(BaseModel):
    """Model representing content statistics."""

    word_count: int = Field(default=0, description="Total word count")
    statistics_count: int = Field(
        default=0,
        description="Number of statistics found (numbers with context)",
    )
    citations_count: int = Field(
        default=0,
        description="Number of citations found (links, references)",
    )
    quotes_count: int = Field(
        default=0,
        description="Number of expert quotes found",
    )
    statistics: List[str] = Field(
        default_factory=list,
        description="List of extracted statistics",
    )
    citations: List[str] = Field(
        default_factory=list,
        description="List of extracted citations",
    )
    quotes: List[str] = Field(
        default_factory=list,
        description="List of extracted quotes",
    )


class ExtractedContent(BaseModel):
    """Model representing fully extracted content."""

    main_content: str = Field(description="Main content text (cleaned)")
    content_type: str = Field(
        description="Content type: blog, product_page, landing_page, how_to, article, other"
    )
    structure: ContentStructure = Field(description="Content structure")
    statistics: ContentStatistics = Field(description="Content statistics")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (title, description, etc.)",
    )


class ContentExtractor:
    """Extract and analyze content from web pages."""

    # Patterns for identifying content types
    CONTENT_TYPE_PATTERNS = {
        "blog": [
            r"/blog/",
            r"/post/",
            r"/article/",
            r"blog",
            r"post",
        ],
        "product_page": [
            r"/product/",
            r"/shop/",
            r"/buy/",
            r"product",
            r"purchase",
        ],
        "landing_page": [
            r"/$",
            r"/home",
            r"/index",
            r"landing",
        ],
        "how_to": [
            r"/how-to/",
            r"/guide/",
            r"/tutorial/",
            r"how to",
            r"guide",
            r"tutorial",
        ],
    }

    # Patterns for detecting statistics
    STATISTICS_PATTERNS = [
        r"\d+%",  # Percentages
        r"\d+\.\d+%",  # Decimal percentages
        r"\$\d+",  # Currency
        r"\d+\.\d+",  # Decimals
        r"\d+,\d+",  # Numbers with commas
        r"\d+\s*(million|billion|thousand|k|m|b)",  # Large numbers
        r"\d+\s*(percent|percentage|%)",  # Percentages spelled out
        r"(over|more than|less than|about|approximately)\s+\d+",  # Approximations
    ]

    # Patterns for detecting citations
    CITATION_PATTERNS = [
        r"\[.*?\]",  # Bracketed citations [1], [source]
        r"\(.*?\)",  # Parenthetical citations (source, 2024)
        r"according to",
        r"source:",
        r"reference:",
        r"study by",
        r"research from",
        r"https?://",  # URLs
    ]

    # Patterns for detecting expert quotes
    QUOTE_PATTERNS = [
        r'"[^"]{20,}"',  # Quoted text (at least 20 chars)
        r"'[^']{20,}'",  # Single quotes
        r"said",
        r"stated",
        r"explained",
        r"according to",
        r"expert",
        r"researcher",
        r"study",
    ]

    def __init__(self):
        """Initialize the content extractor."""
        self.logger = logger

    def extract_main_content(
        self, html_content: str, url: Optional[str] = None
    ) -> str:
        """
        Extract main content from webpage, removing nav, footer, ads.

        Args:
            html_content: Raw HTML content
            url: Optional URL for newspaper3k processing

        Returns:
            Cleaned main content text
        """
        try:
            # Try using newspaper3k first for better content extraction
            if url:
                try:
                    article = Article(url)
                    article.set_html(html_content)
                    article.parse()
                    if article.text and len(article.text.strip()) > 100:
                        return article.text.strip()
                except Exception as e:
                    self.logger.warning(f"Newspaper3k extraction failed: {e}")

            # Fallback to BeautifulSoup extraction
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove unwanted elements
            unwanted_tags = [
                "nav",
                "footer",
                "header",
                "aside",
                "script",
                "style",
                "noscript",
                "iframe",
                "embed",
                "object",
                "form",
                "button",
                "input",
                "select",
                "textarea",
            ]

            # Remove by tag
            for tag in unwanted_tags:
                for element in soup.find_all(tag):
                    element.decompose()

            # Remove by class/id patterns (common ad/nav patterns)
            unwanted_patterns = [
                r"ad",
                r"advertisement",
                r"sidebar",
                r"navigation",
                r"menu",
                r"cookie",
                r"popup",
                r"modal",
                r"banner",
            ]

            for pattern in unwanted_patterns:
                for element in soup.find_all(
                    class_=re.compile(pattern, re.I)
                ) + soup.find_all(id=re.compile(pattern, re.I)):
                    element.decompose()

            # Try to find main content area
            main_content = None
            for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            if main_content:
                text = main_content.get_text(separator=" ", strip=True)
            else:
                # Fallback to body text
                body = soup.find("body")
                if body:
                    text = body.get_text(separator=" ", strip=True)
                else:
                    text = soup.get_text(separator=" ", strip=True)

            # Clean up whitespace
            text = re.sub(r"\s+", " ", text).strip()

            return text

        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}")
            # Last resort: simple text extraction
            soup = BeautifulSoup(html_content, "html.parser")
            return soup.get_text(separator=" ", strip=True)

    def identify_content_type(self, url: str, content: str) -> str:
        """
        Identify content type based on URL and content.

        Args:
            url: Page URL
            content: Page content text

        Returns:
            Content type: blog, product_page, landing_page, how_to, article, other
        """
        url_lower = url.lower()
        content_lower = content.lower()[:500]  # Check first 500 chars

        # Check URL patterns
        for content_type, patterns in self.CONTENT_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower, re.I):
                    return content_type

        # Check content patterns
        if any(word in content_lower for word in ["how to", "step", "tutorial", "guide"]):
            return "how_to"
        if any(word in content_lower for word in ["buy", "price", "add to cart", "purchase"]):
            return "product_page"
        if any(word in content_lower for word in ["blog", "post", "article", "author"]):
            return "blog"

        # Default to article if it's substantial content
        word_count = len(content.split())
        if word_count > 500:
            return "article"

        return "other"

    def extract_structure(self, html_content: str) -> ContentStructure:
        """
        Extract existing structure (headings, paragraphs, lists).

        Args:
            html_content: Raw HTML content

        Returns:
            ContentStructure object with headings, paragraphs, lists, links
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract headings
        headings = []
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            for heading in soup.find_all(tag):
                level = int(tag[1])
                text = heading.get_text(strip=True)
                if text:
                    headings.append({"level": level, "text": text, "tag": tag})

        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short paragraphs
                paragraphs.append(text)

        # Extract lists
        lists = []
        for ul in soup.find_all(["ul", "ol"]):
            list_items = []
            for li in ul.find_all("li", recursive=False):
                text = li.get_text(strip=True)
                if text:
                    list_items.append(text)
            if list_items:
                lists.append(list_items)

        # Extract links
        links = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a.get("href", "")
            if text and href:
                links.append({"text": text, "url": href})

        return ContentStructure(
            headings=headings,
            paragraphs=paragraphs,
            lists=lists,
            links=links,
        )

    def count_statistics(self, content: str) -> tuple[int, List[str]]:
        """
        Count and extract statistics from content.

        Args:
            content: Content text

        Returns:
            Tuple of (count, list of statistics)
        """
        statistics = []
        found_statistics = set()

        for pattern in self.STATISTICS_PATTERNS:
            matches = re.finditer(pattern, content, re.I)
            for match in matches:
                # Get context around the statistic (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                if context not in found_statistics:
                    found_statistics.add(context)
                    statistics.append(context)

        return len(statistics), statistics

    def count_citations(self, content: str, links: List[Dict[str, str]]) -> tuple[int, List[str]]:
        """
        Count and extract citations from content.

        Args:
            content: Content text
            links: List of links from structure

        Returns:
            Tuple of (count, list of citations)
        """
        citations = []
        found_citations = set()

        # Check for citation patterns in text
        for pattern in self.CITATION_PATTERNS:
            matches = re.finditer(pattern, content, re.I)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()
                if context not in found_citations:
                    found_citations.add(context)
                    citations.append(context)

        # Add external links as citations
        for link in links:
            url = link.get("url", "")
            if url.startswith("http") and url not in found_citations:
                citations.append(url)
                found_citations.add(url)

        return len(citations), citations

    def count_quotes(self, content: str) -> tuple[int, List[str]]:
        """
        Count and extract expert quotes from content.

        Args:
            content: Content text

        Returns:
            Tuple of (count, list of quotes)
        """
        quotes = []
        found_quotes = set()

        # Find quoted text
        quote_patterns = [
            r'"([^"]{30,})"',  # Double quotes
            r"'([^']{30,})'",  # Single quotes
        ]

        for pattern in quote_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                quote_text = match.group(1).strip()
                if quote_text not in found_quotes and len(quote_text) > 20:
                    found_quotes.add(quote_text)
                    quotes.append(quote_text)

        # Also look for quote indicators with context
        quote_indicators = [
            r"(said|stated|explained|noted|added|commented|remarked)[^.]{0,100}",
        ]

        for pattern in quote_indicators:
            matches = re.finditer(pattern, content, re.I)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()
                if context not in found_quotes:
                    found_quotes.add(context)
                    quotes.append(context)

        return len(quotes), quotes

    def extract(self, html_content: str, url: Optional[str] = None) -> ExtractedContent:
        """
        Perform complete content extraction.

        Args:
            html_content: Raw HTML content
            url: Optional URL for better extraction

        Returns:
            ExtractedContent object with all extracted information
        """
        # Extract main content
        main_content = self.extract_main_content(html_content, url)

        # Identify content type
        content_type = self.identify_content_type(url or "", main_content)

        # Extract structure
        structure = self.extract_structure(html_content)

        # Count statistics
        stats_count, stats_list = self.count_statistics(main_content)

        # Count citations
        citations_count, citations_list = self.count_citations(
            main_content, structure.links
        )

        # Count quotes
        quotes_count, quotes_list = self.count_quotes(main_content)

        # Calculate word count
        word_count = len(main_content.split())

        # Extract metadata
        soup = BeautifulSoup(html_content, "html.parser")
        metadata = {}
        title_tag = soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get_text(strip=True)

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            metadata["description"] = meta_desc.get("content", "")

        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc:
            metadata["og_description"] = og_desc.get("content", "")

        return ExtractedContent(
            main_content=main_content,
            content_type=content_type,
            structure=structure,
            statistics=ContentStatistics(
                word_count=word_count,
                statistics_count=stats_count,
                citations_count=citations_count,
                quotes_count=quotes_count,
                statistics=stats_list,
                citations=citations_list,
                quotes=quotes_list,
            ),
            metadata=metadata,
        )

