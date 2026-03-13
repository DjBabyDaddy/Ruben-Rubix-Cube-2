# RUBE (Ruben Rubix Cube) — AI Desktop Assistant

RUBE is a **voice-first, self-improving AI desktop assistant** built in Python. He runs locally on Windows, uses Claude Sonnet as his cognitive engine, and can control your entire desktop through natural language.

## What Makes RUBE Different

- **Self-Improving** — RUBE analyzes his own failure logs, proposes code fixes via Claude Code CLI, and queues them for human approval before writing anything
- **Voice-First** — Fully offline speech recognition (Vosk) and text-to-speech (Kokoro) with wake word activation
- **27+ Intent Types** — From sending WhatsApp messages to controlling OBS scenes to analyzing your webcam feed
- **AI Framework Knowledge Base** — 1,900+ lines of LangGraph, CrewAI, MCP, LlamaIndex, and Anthropic best practices injected during self-improvement cycles

## Quick Start

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys (only `ANTHROPIC_API_KEY` is required)
4. Download the [Vosk model](https://alphacephei.com/vosk/models) and place it in a `model/` directory
5. Run:
   ```bash
   python main.py
   ```

## Core Capabilities

See [CAPABILITIES.md](CAPABILITIES.md) for the full breakdown, but highlights include:

- **Communication** — WhatsApp, Email, generic messaging, contact management
- **Vision** — Camera, screen capture, video analysis, document reading, facial recognition
- **Broadcasting** — OBS Studio and Streamlabs control via WebSocket
- **Web Search** — Multi-API routing (TMDB, RAWG, NewsAPI, CoinGecko, SerpAPI)
- **Social Media** — AI copywriting + image generation + n8n webhook posting
- **System Control** — App launching, keyboard shortcuts, volume, screenshots, diagnostics
- **File Management** — Move/rename/delete with soft-delete, undo, and human approval
- **Self-Improvement** — Automated bug detection, subagent code generation, approval queue

## Architecture

- **Pure Python** with asyncio + threading
- **Modular action system** — each capability is a plug-in in `actions/`
- **Preflight validation** — every action type has pre-execution safety checks
- **Zero cloud dependency for voice** — both STT and TTS run offline
- **10+ external API integrations** via environment variables

## API Keys

Only `ANTHROPIC_API_KEY` is required. All others are optional and unlock additional features. See `.env.example` for the full list. RUBE can also register new API keys via voice command at runtime.

## Credits

Originally inspired by the [Jarvis Mark X tutorial](https://youtu.be/ZD6kf9w9Sy0) by FatihMakes. RUBE has since been extensively rebuilt with self-improvement systems, vision analysis, broadcasting control, social media automation, facial recognition, file management, and an AI framework knowledge base.

## License

MIT
