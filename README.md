# RUBE (Ruben Rubix Cube) — AI Desktop Assistant

RUBE is a **voice-first, self-improving AI desktop assistant** built in Python. He runs on Windows, uses Claude Sonnet 4.6 as his cognitive engine, and controls your entire desktop through natural language.

## What Makes RUBE Different

- **Cloud-powered voice** — Deepgram Nova-3 streaming STT (<300ms latency) + Cartesia Sonic TTS (40ms response), no bulky local models to download
- **Self-Improving** — RUBE analyzes his own failure logs, proposes code fixes via the Anthropic API, and queues them for human approval before writing anything
- **Two-tier AI brain** — Claude Sonnet 4.6 for deep reasoning + Groq (Llama 70B → 8B auto-fallback) for lightning-fast queries
- **28+ Intent Types** — From sending WhatsApp messages to controlling OBS scenes to analyzing your webcam feed
- **Feature-flagged modules** — Enable only what you need; unused modules don't load
- **Remote OTA updates** — Secure HMAC-signed updates pushed from the server with auto-rollback

## Quick Start

1. Clone the repo
2. Install core dependencies:
   ```bash
   pip install -r requirements-core.txt
   ```
3. Run the setup wizard (first boot launches it automatically, or run manually):
   ```bash
   python setup_wizard.py
   ```
4. Start RUBE:
   ```bash
   python main.py
   ```

The wizard configures your `.env` with API keys, voice providers, and optional feature flags. Only `ANTHROPIC_API_KEY` is required to boot.

## Optional Dependencies

Install only what you need:

```bash
pip install -r requirements-optional.txt  # everything
# or individual packages:
pip install opencv-contrib-python          # camera / video / facial recognition
pip install pdfplumber python-docx openpyxl  # document analysis
pip install obsws-python pyautogui         # OBS / desktop automation
```

## Core Capabilities

See [CAPABILITIES.md](CAPABILITIES.md) for the full breakdown:

- **Communication** — WhatsApp, Email, generic messaging, contact management
- **Vision** — Camera, screen capture, video analysis, document reading, facial recognition
- **Broadcasting** — OBS Studio and Streamlabs control via WebSocket
- **Web Search** — Multi-API routing (TMDB, RAWG, NewsAPI, CoinGecko, SerpAPI, Exa, Firecrawl)
- **Social Media** — AI copywriting + image generation + n8n webhook posting
- **System Control** — App launching, keyboard shortcuts, volume, screenshots, diagnostics
- **Code Agent** — Two-tier coding assistant (Claude Sonnet for complex tasks, Groq for quick queries)
- **Self-Improvement** — Automated bug detection, subagent code generation, approval queue

## Architecture

- **Pure Python** with asyncio + threading
- **Modular action system** — each capability is a plug-in in `actions/`
- **Provider abstraction** — `core/tts_providers.py`, `core/stt_providers.py`, `core/platform.py`
- **Preflight validation** — every action type has pre-execution safety checks
- **Feature flags** — optional modules controlled via `.env`, graceful degradation when missing
- **Approval-gated self-improvement** — no autonomous file writes, ever

## API Keys

Only `ANTHROPIC_API_KEY` is required. All others unlock optional features. See `.env.example` for the full list. RUBE can register new API keys via voice command at runtime.

## Voice Providers

| Provider | Role | Cost | Notes |
|---|---|---|---|
| Deepgram Nova-3 | STT | ~$0.0043/min | 40ms latency, streaming WebSocket |
| Cartesia Sonic | TTS | ~$47/1M chars | 40ms TTFB, best value |
| Edge TTS | TTS fallback | Free | No API key needed |

## License

MIT
