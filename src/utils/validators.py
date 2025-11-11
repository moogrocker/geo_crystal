"""Validation utilities for GEO Crystal."""

from typing import Optional
from urllib.parse import urlparse

from config.constants import (
    CONTENT_THRESHOLDS,
    SUPPORTED_CONTENT_TYPES,
    VALID_URL_SCHEMES,
)


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate a URL.

    Args:
        url: URL string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"

    if not parsed.scheme:
        return False, "URL must include a scheme (http:// or https://)"

    if parsed.scheme.lower() not in VALID_URL_SCHEMES:
        return (
            False,
            f"URL scheme must be one of: {', '.join(VALID_URL_SCHEMES)}",
        )

    if not parsed.netloc:
        return False, "URL must include a domain"

    return True, None


def validate_content(
    content: str,
    content_type: str = "text/html",
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
) -> tuple[bool, Optional[str]]:
    """
    Validate content.

    Args:
        content: Content string to validate
        content_type: MIME type of the content
        min_words: Minimum word count (uses default from constants if None)
        max_words: Maximum word count (uses default from constants if None)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content or not isinstance(content, str):
        return False, "Content must be a non-empty string"

    if content_type not in SUPPORTED_CONTENT_TYPES:
        return (
            False,
            f"Content type must be one of: {', '.join(SUPPORTED_CONTENT_TYPES)}",
        )

    # Word count validation
    word_count = len(content.split())
    min_words = min_words or CONTENT_THRESHOLDS["min_word_count"]
    max_words = max_words or CONTENT_THRESHOLDS["max_word_count"]

    if word_count < min_words:
        return (
            False,
            f"Content must have at least {min_words} words (found {word_count})",
        )

    if word_count > max_words:
        return (
            False,
            f"Content must have at most {max_words} words (found {word_count})",
        )

    return True, None


def validate_geo_score(score: float) -> tuple[bool, Optional[str]]:
    """
    Validate a GEO score.

    Args:
        score: Score value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(score, (int, float)):
        return False, "Score must be a number"

    if score < 0 or score > 100:
        return False, "Score must be between 0 and 100"

    return True, None

