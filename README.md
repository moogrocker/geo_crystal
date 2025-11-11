# GEO Autopilot MVP

A Generative Engine Optimization (GEO) SaaS MVP for optimizing content for AI-powered search engines. This tool analyzes web content and provides AI-powered transformations to improve GEO scores.

## 🚀 Features

- **GEO Audit**: Comprehensive analysis of web content with detailed scoring
- **Content Transformation**: AI-powered content optimization with statistics, citations, expert quotes, and schema markup
- **Streamlit UI**: Beautiful, interactive web interface for easy use
- **CLI Interface**: Command-line tool for automation and integration
- **Demo Mode**: Instant results with sample data for testing

## 📋 Prerequisites

- Python 3.12 or higher
- OpenAI API key OR Anthropic API key (at least one required)

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd geo_crystal
```

### 2. Install Dependencies

**Option A: Using pip (recommended for quick start)**

```bash
pip install -r requirements.txt
```

**Option B: Using uv (faster, recommended for development)**

```bash
uv sync
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```bash
cp .env.template .env  # If template exists
# Or create .env manually
```

Edit `.env` and add your API keys:

```env
# Required: At least one API key must be set
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Model configuration
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-opus-20240229

# Optional: Application settings
DEBUG=false
LOG_LEVEL=INFO
```

**Note**: You need at least one API key (OpenAI or Anthropic) for the transformation features to work. Audit features work without API keys.

### 4. Verify Installation

Test the CLI:

```bash
python main.py --help
```

## 🎯 Usage

### Streamlit Web UI (Recommended)

Launch the web interface:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

**Features:**
- **Audit Page**: Enter a URL to get a comprehensive GEO score and recommendations
- **Transform Page**: Load content and apply AI-powered transformations
- **Results Page**: View audit history and track improvements

**Demo Mode**: Use the sample URLs button to try the tool with pre-generated demo data (no API calls needed).

### CLI Interface

**Run an Audit:**

```bash
python main.py https://example.com/article --mode audit
```

**Run Optimization:**

```bash
python main.py https://example.com/article --mode optimize --apply-all
```

**Options:**
- `--mode {audit,optimize}`: Operation mode (default: audit)
- `--apply-all`: Apply all transformations (optimize mode only)
- `--no-save`: Don't save results to file
- `--json`: Output results as JSON
- `--verbose`: Enable verbose logging

**Example Output:**

```
============================================================
GEO AUDIT RESULTS
============================================================
URL: https://example.com/article
Date: 2024-01-15T10:30:00

Overall GEO Score: 65.50/100

Score Breakdown:
  - First Paragraph Score: 70.00
  - Statistics Score: 60.00
  - Citations Score: 55.00
  - Expert Quotes Score: 50.00
  - Readability Score: 75.00
  - Headings Structure Score: 72.00
  - Schema Score: 60.00

Top Recommendations:
  1. Add more statistics and data points to improve fact density
  2. Include expert quotes from industry leaders
  3. Add external citations to authoritative sources
  4. Optimize the first paragraph to directly answer the main question
  5. Generate structured data (JSON-LD) schema markup
============================================================
```

## 📁 Project Structure

```
geo_crystal/
├── app.py                 # Streamlit main app
├── main.py                # CLI entry point
├── streamlit_helpers.py    # Helper functions for Streamlit
├── demo_data.py           # Demo data and sample URLs
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config/
│   ├── config.py         # Application settings
│   └── constants.py      # Scoring weights and thresholds
├── src/
│   ├── audit/            # Audit engine
│   │   ├── crawler.py    # Web crawler
│   │   ├── content_analyzer.py
│   │   ├── technical_analyzer.py
│   │   └── geo_scorer.py
│   ├── transformation/   # Transformation engine
│   │   ├── ai_client.py  # AI API client
│   │   ├── content_transformer.py
│   │   ├── geo_optimizer.py
│   │   └── schema_generator.py
│   ├── analysis/         # Analysis tools
│   ├── models/           # Data models
│   └── utils/           # Utilities
├── pages/               # Streamlit pages
│   ├── 1_audit.py
│   ├── 2_transform.py
│   └── 3_results.py
├── components/          # Streamlit components
└── data/               # Storage for results
    ├── audits/         # Audit results
    ├── optimizations/  # Optimization results
    └── demo/          # Demo data
```

## 🎨 Demo Mode

The app includes demo mode for testing without API calls:

1. **In Streamlit UI**: Click "Sample URLs" button to use pre-generated demo data
2. **Environment Variable**: Set `GEO_DEMO_MODE=true` to enable demo mode globally
3. **Sample URLs**: Three sample URLs are available with instant results

## 🔧 Configuration

### API Models

Configure which AI model to use in `.env`:

- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`

### Scoring Weights

Edit `config/constants.py` to adjust GEO scoring weights and thresholds.

## 📊 GEO Score Components

The GEO score is calculated from:

1. **First Paragraph Score**: How well the opening answers the main question (40-60 words optimal)
2. **Statistics Score**: Presence of data points and statistics
3. **Citations Score**: External links to authoritative sources
4. **Expert Quotes Score**: Quotes from industry experts
5. **Readability Score**: Content readability (Flesch Reading Ease)
6. **Headings Structure Score**: Proper heading hierarchy (H1-H6)
7. **Schema Score**: Structured data markup (JSON-LD)

## 🧪 Testing

Test the end-to-end flow:

```bash
# Test audit
python main.py https://example.com/article --mode audit --verbose

# Test optimization (requires API key)
python main.py https://example.com/article --mode optimize --apply-all --verbose
```

## 🐛 Troubleshooting

**Issue**: "No API keys configured"
- **Solution**: Make sure `.env` file exists with at least one API key

**Issue**: "Failed to fetch URL"
- **Solution**: Check internet connection and URL validity. Some sites may block automated requests.

**Issue**: Import errors
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Streamlit not starting
- **Solution**: Check if port 8501 is available, or use `streamlit run app.py --server.port 8502`

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Support

[Add support contact information here]
