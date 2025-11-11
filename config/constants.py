"""Constants for GEO Crystal scoring and thresholds."""

# Scoring weights for different GEO factors
SCORING_WEIGHTS = {
    "content_quality": 0.30,  # 30% weight
    "structure": 0.25,  # 25% weight
    "metadata": 0.20,  # 20% weight
    "readability": 0.15,  # 15% weight
    "engagement": 0.10,  # 10% weight
}

# GEO score thresholds
GEO_SCORE_THRESHOLDS = {
    "excellent": 90.0,
    "good": 75.0,
    "fair": 60.0,
    "poor": 0.0,
}

# Content validation thresholds
CONTENT_THRESHOLDS = {
    "min_word_count": 100,
    "max_word_count": 10000,
    "min_title_length": 10,
    "max_title_length": 60,
    "min_description_length": 50,
    "max_description_length": 160,
}

# URL validation patterns
VALID_URL_SCHEMES = ["http", "https"]

# Content types supported
SUPPORTED_CONTENT_TYPES = [
    "text/html",
    "text/plain",
    "application/json",
]

# Default headers for web requests
DEFAULT_HEADERS = {
    "User-Agent": "GEO-Crystal/1.0 (Mozilla/5.0 compatible)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

