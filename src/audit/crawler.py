"""Web crawler for fetching and parsing HTML content."""

import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from requests_html import HTMLSession
from requests_html import HTML as HTMLResponse

from config.config import settings
from src.utils.logger import logger


class WebCrawler:
    """Crawler for fetching and parsing HTML content from URLs."""

    def __init__(self, timeout: Optional[int] = None, max_retries: Optional[int] = None):
        """
        Initialize the web crawler.

        Args:
            timeout: Request timeout in seconds. Uses config default if None.
            max_retries: Maximum number of retries. Uses config default if None.
        """
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.max_retries = max_retries or settings.MAX_RETRIES
        self.session = HTMLSession()

    def fetch_url(self, url: str) -> Tuple[Optional[HTMLResponse], Optional[str]]:
        """
        Fetch HTML content from a URL with JavaScript rendering support.

        Args:
            url: URL to fetch

        Returns:
            Tuple of (HTMLResponse object, error_message). Returns (None, error) on failure.
        """
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(
                url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()

            # Render JavaScript if needed
            try:
                response.html.render(timeout=20, wait=2)
            except Exception as render_error:
                logger.warning(f"JavaScript rendering failed for {url}: {render_error}")
                # Continue with static HTML if rendering fails

            return response.html, None

        except Exception as e:
            error_msg = f"Failed to fetch {url}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    def parse_html(self, html_content: str, base_url: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract structured data.

        Args:
            html_content: HTML content as string
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary containing extracted data:
            - text_content: Main text content
            - headings: List of headings with hierarchy
            - meta_tags: Dictionary of meta tags
            - links: List of external links
            - images: List of image URLs
            - schema_markup: List of schema.org JSON-LD objects
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract text content (remove scripts, styles, etc.)
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()

        text_content = soup.get_text(separator=" ", strip=True)

        # Extract headings with hierarchy
        headings = []
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            for heading in soup.find_all(tag):
                level = int(tag[1])  # Extract number from h1, h2, etc.
                headings.append({
                    "level": level,
                    "text": heading.get_text(strip=True),
                    "tag": tag
                })

        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property") or meta.get("itemprop")
            content = meta.get("content")
            if name and content:
                meta_tags[name.lower()] = content

        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            meta_tags["title"] = title_tag.get_text(strip=True)

        # Extract description
        description = meta_tags.get("description") or meta_tags.get("og:description")
        if not description:
            # Try to get from meta description
            desc_meta = soup.find("meta", attrs={"name": "description"})
            if desc_meta:
                meta_tags["description"] = desc_meta.get("content", "")

        # Extract links
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            if href:
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                if parsed.netloc and parsed.netloc != urlparse(base_url).netloc:
                    links.append({
                        "url": absolute_url,
                        "text": link.get_text(strip=True),
                        "is_external": True
                    })
                else:
                    links.append({
                        "url": absolute_url,
                        "text": link.get_text(strip=True),
                        "is_external": False
                    })

        # Extract images
        images = []
        for img in soup.find_all("img", src=True):
            src = img.get("src")
            if src:
                absolute_url = urljoin(base_url, src)
                images.append({
                    "url": absolute_url,
                    "alt": img.get("alt", ""),
                    "title": img.get("title", "")
                })

        # Extract schema.org JSON-LD markup
        schema_markup = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                schema_data = json.loads(script.string)
                if isinstance(schema_data, dict):
                    schema_markup.append(schema_data)
                elif isinstance(schema_data, list):
                    schema_markup.extend(schema_data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON-LD schema: {script.string[:100]}")

        # Extract microdata
        microdata = []
        for item in soup.find_all(attrs={"itemscope": True}):
            item_data = {}
            item_type = item.get("itemtype", "")
            if item_type:
                item_data["@type"] = item_type.split("/")[-1]  # Extract type name

            for prop in item.find_all(attrs={"itemprop": True}):
                prop_name = prop.get("itemprop")
                prop_value = prop.get("content") or prop.get_text(strip=True)
                if prop_name and prop_value:
                    item_data[prop_name] = prop_value

            if item_data:
                microdata.append(item_data)

        return {
            "text_content": text_content,
            "headings": headings,
            "meta_tags": meta_tags,
            "links": links,
            "images": images,
            "schema_markup": schema_markup,
            "microdata": microdata,
            "html": str(soup)
        }

    def crawl(self, url: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Complete crawl operation: fetch and parse URL.

        Args:
            url: URL to crawl

        Returns:
            Tuple of (parsed_data dictionary, error_message). Returns (None, error) on failure.
        """
        html_response, error = self.fetch_url(url)
        if error:
            return None, error

        if html_response is None:
            return None, "Failed to fetch HTML content"

        try:
            # Convert HTML object to string (requests-html HTML object can be converted directly)
            html_string = str(html_response)
            parsed_data = self.parse_html(html_string, url)
            parsed_data["url"] = url
            logger.info(f"Successfully crawled {url}")
            return parsed_data, None
        except Exception as e:
            error_msg = f"Failed to parse HTML for {url}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    def close(self):
        """Close the session."""
        if hasattr(self, "session"):
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

