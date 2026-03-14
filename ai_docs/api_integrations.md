# RUBE API Integrations

Every external service RUBE connects to, the env var it needs, and what it powers.

## Required

| Service | Env Var | Used By | Purpose |
|---------|---------|---------|---------|
| **Anthropic (Claude)** | `ANTHROPIC_API_KEY` | `llm.py` | Primary brain — intent parsing, reasoning, vision |

## Local (No API Key Needed)

| Service | Config | Used By | Purpose |
|---------|--------|---------|---------|
| **LM Studio** | `LM_STUDIO_URL`, `LM_STUDIO_MODEL`, `LM_STUDIO_TOKEN` | `code_agent.py`, `self_improver.py` | Local coding agent (Qwen 3.5 9B) via Claude Code CLI |
| **Vosk** | `model/` directory | `speech_to_text.py` | Offline speech-to-text |
| **Kokoro** | bundled | `tts.py` | Offline text-to-speech |

## Optional — Web Search & Data

| Service | Env Var | Used By | Purpose |
|---------|---------|---------|---------|
| **SerpAPI** | `SERPAPI_API_KEY` | `web_search.py` | General web search, sports scores, answer boxes |
| **Exa** | `EXA_API_KEY` | `web_search.py` | Semantic search fallback |
| **Firecrawl** | `FIRECRAWL_API_KEY` | `web_search.py` | Web scraping for search results |
| **NewsAPI** | `NEWS_API_KEY` | `web_search.py` | News headlines and articles |
| **Groq** | `GROQ_API_KEY` | `web_search.py` | Fast LLM for summarizing search results |
| **The Odds API** | `ODDS_API_API_KEY` | `web_search.py` | Sports betting odds and scores |

## Optional — Communication

| Service | Env Var | Used By | Purpose |
|---------|---------|---------|---------|
| **Gmail** | (OAuth or app password) | `email_manager.py` | Send emails |
| **WhatsApp Desktop** | (browser session) | `whatsapp.py` | Send messages, calls, images |

## Optional — Content & Analytics

| Service | Env Var | Used By | Purpose |
|---------|---------|---------|---------|
| **n8n Webhook** | `N8N_WEBHOOK_URL` | `social_manager.py`, `analytics_manager.py` | Social posting, analytics, daily self-assessment |
| **Cartesia** | `CARTESIA_API_KEY` | (reserved) | Alternative TTS |
| **OpenRouter** | `OPENROUTER_API_KEY` | (reserved) | Alternative LLM routing |

## No-Auth APIs (Used Directly)

| Service | Used By | Purpose |
|---------|---------|---------|
| **CoinGecko** | `web_search.py` | Crypto prices (free tier, no key) |
| **TMDB** | `web_search.py` | Movie/TV data |
| **RAWG** | `web_search.py` | Video game data |
| **Pollinations** | `social_manager.py` | AI image generation (free, no auth) |
| **ipapi.co** | `main.py` | Geo-location context at startup |

## Adding a New API

1. Add the env var to `.env` and `.env.example`
2. In your handler: `load_dotenv()` then `os.getenv("YOUR_KEY")`
3. If the key is missing, speak a helpful message and return gracefully
4. Document it in this file
