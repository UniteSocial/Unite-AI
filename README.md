# Unite-I

**Empowering healthier online discourse through transparent AI analysis**

Unite-I is an open-source content analysis service designed to help platforms and users better understand social media content. Built with transparency and trust in mind, it provides multi-dimensional analysis of text to combat misinformation and promote informed online conversations.

## What it does

Unite-I analyzes social media posts through three complementary lenses:

- **Content Classification** — Automatically identifies whether content is a factual claim, opinion, question, personal update, or promotional material
- **Veracity Analysis** — Fact-checks claims using web search and provides sourced justifications with clear verification methods
- **Nuance Detection** — Surfaces political tendency and communicative intent (informative, persuasive, satirical, provocative, etc.) to help readers understand context

## Why we built this

Social media has become a primary source of information for billions of people, yet distinguishing fact from fiction, news from opinion, and genuine content from manipulation has never been harder. Unite-I was created as part of [Unitesocial](https://unitesocial.eu), a European social media platform committed to fostering healthier digital spaces.

We believe transparency tools should be accessible to everyone. By open-sourcing Unite-I, we invite developers, researchers, and platforms to use, improve, and adapt these tools for their own communities.

## Features

- **Multi-provider AI** — Supports Claude (Anthropic) and Mistral models
- **Web-verified fact-checking** — Integrates with Brave Search for real-time source verification
- **Multilingual** — English and German support out of the box
- **Production-ready** — Rate limiting, CORS protection, and proper error handling
- **Simple API** — Clean REST endpoints built with FastAPI
- **Extensible** — Modular service architecture for easy customization

## Quick Start

```bash
# Clone and install
git clone https://github.com/UniteSocial/Unite-I.git
cd Unite-I
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure (see .env.example)
cp .env.example .env
# Add your API keys

# Run
uvicorn src.main:app --reload
```

## API Usage

### Analyze Content

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "example_001",
    "post_text": "The Earth revolves around the Sun.",
    "language": "en"
  }'
```

### Response

```json
{
  "post_id": "example_001",
  "analysis_timestamp": "2026-01-20T10:30:00Z",
  "language": "en",
  "post_analysis": {
    "post_type": "Factual Claim",
    "is_spam": false
  },
  "veracity_analysis": {
    "status": "Factually Correct",
    "justification": "Multiple scientific sources confirm...",
    "verification_method": "Web search",
    "sources": [...]
  },
  "nuance_analysis": {
    "political_tendency": {
      "primary": "Neutral",
      "scores": {...}
    },
    "detected_intents": ["Informative"]
  }
}
```

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `AI_PROVIDER` | `claude` or `mistral` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `MISTRAL_API_KEY` | Your Mistral API key |
| `BRAVE_API_KEY` | Brave Search API key for fact-checking |

## Project Structure

```
unite-i/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   └── services/
│       ├── base_llm_service.py # Shared LLM logic
│       ├── claude_service.py   # Claude integration
│       ├── mistral_service.py  # Mistral integration
│       └── evaluation_service.py
├── prompts/                    # Public system prompts
├── tests/
├── Dockerfile
└── requirements.txt
```

## Transparency

All system prompts that influence AI decisions are published in the `prompts/` directory. See our blog post: [Why We're Open-Sourcing Our Fact-Checking AI](https://unitesocial.eu/blog/why-we-are-open-sourcing-our-fact-checking-ai)

## Docker

```bash
docker build -t unite-i .
docker run -p 8000:8000 --env-file .env unite-i
```

## Contributing

We welcome contributions! Whether it's adding new languages, improving detection accuracy, or enhancing documentation — every contribution helps make online spaces safer and more transparent.

## License

MIT License — free to use, modify, and distribute.

---

**Built with the belief that understanding context is the first step toward better conversations.**
