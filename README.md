# GEO Crystal

A Generative Engine Optimization (GEO) SaaS MVP for optimizing content for AI-powered search engines.

## Project Structure

```
geo_crystal/
├── src/
│   ├── core/           # Core business logic
│   ├── models/         # Pydantic data models
│   └── utils/          # Utility functions (logging, validation, storage)
├── config/             # Configuration files
│   ├── config.py       # Application settings
│   └── constants.py    # Scoring weights and thresholds
├── data/               # Storage for audit results (JSON files)
└── main.py             # Entry point
```

## Setup

### 1. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -e .
```

### 2. Configure Environment Variables

Copy the environment template and fill in your API keys:
```bash
cp env.template .env
```

Edit `.env` and add your API keys:
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key

### 3. Verify Installation

```python
from src.models import WebsiteAudit, PageContent, GEOScore, TransformationResult
from config import settings
from src.utils import setup_logger, validate_url, validate_content, JSONStorage

# All imports should work!
```

## Data Models

### WebsiteAudit
Represents a complete website audit with GEO score and findings.

### PageContent
Represents extracted page content with metadata.

### GEOScore
Represents a GEO score with detailed breakdown.

### TransformationResult
Represents the result of content transformation with before/after scores.

## Configuration

### Settings (`config/config.py`)
- API keys and model configuration
- Application settings (debug, log level)
- Storage configuration
- Request settings

### Constants (`config/constants.py`)
- Scoring weights for different GEO factors
- Score thresholds (excellent, good, fair, poor)
- Content validation thresholds
- Supported content types

## Utilities

### Logger (`src/utils/logger.py`)
Configured logging with console and optional file output.

### Validators (`src/utils/validators.py`)
- URL validation
- Content validation (word count, content type)
- GEO score validation

### Storage (`src/utils/storage.py`)
JSON file-based storage for MVP:
- Save/load audit data
- Save transformation results
- List stored audits

## Usage Example

```python
from src.models import WebsiteAudit, GEOScore
from src.utils import JSONStorage, validate_url
from config import settings

# Validate URL
is_valid, error = validate_url("https://example.com")
if not is_valid:
    print(f"Error: {error}")

# Create a GEO score
score = GEOScore(
    total_score=75.5,
    breakdown={
        "content_quality": 80.0,
        "structure": 70.0,
        "metadata": 75.0,
    }
)

# Create an audit
audit = WebsiteAudit(
    url="https://example.com",
    geo_score=score,
    findings={"issues": [], "recommendations": []}
)

# Save audit
storage = JSONStorage()
storage.save_audit(audit.model_dump())
```

## Dependencies

- `pydantic` - Data validation and settings management
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `streamlit` - Web UI (for future use)

## License

[Add your license here]

