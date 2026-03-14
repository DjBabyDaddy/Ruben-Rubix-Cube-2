# RUBE (Ruben Rubix Cube) — Full Capability Sheet

## Voice-First AI Desktop Assistant
- **Wake word activation** — "Ruben" / "Reuben" / "Rubin" with phonetic fuzzy matching
- **Cloud speech recognition** — Deepgram Nova-3 streaming WebSocket, <300ms latency, keyword-boosted for "Ruben"
- **Cloud text-to-speech** — Cartesia Sonic (40ms TTFB, ~$47/1M chars) with Edge TTS free fallback
- **Echo cancellation** — filters out its own speech from mic input
- **Keyboard input fallback** — dual input mode (voice + typing)
- **Interrupt support** — "stop", "cancel", "shut up" kills speech mid-sentence
- **No local model download** — STT and TTS are both cloud-based; boots in seconds

---

## AI Brain & Reasoning
- **Claude Sonnet 4.6** as the primary cognitive engine (Anthropic API)
- **Groq speed brain** — Llama 3.3 70B for fast queries; auto-downgrades to Llama 3.1 8B when rate-limited, upgrades back when quota resets
- **Intent routing** — natural language parsed into 28+ structured intents with confidence scoring
- **Confidence gating** — low-confidence actions (< 0.5) trigger clarification instead of guessing
- **Compound command decomposition** — "open Chrome and play my SoundCloud likes" splits into queued actions
- **Phonetic deduction** — handles STT mishearing ("weather" vs "whether", "Ruben" vs "ribbon")
- **Contextual memory injection** — conversation history, user preferences, and lessons fed into every prompt
- **Multimodal vision** — Claude's vision API for image/video/screen analysis
- **Structured outputs** — JSON schema enforcement for reliable intent parsing (auto-detected from SDK version)

---

## Self-Improvement System (Self-Healing Code)
- **Automated bug detection** — analyzes its own failure logs for patterns
- **Subagent code generation** — calls Claude Sonnet directly via Anthropic API to propose fixes (no CLI dependency)
- **Human-in-the-loop approval queue** — all code changes require explicit approval before applying
- **Backup-before-write safety** — mandatory `.rube.bak` before any file modification
- **Edit audit trail** — every approved/rejected change logged with diffs
- **AI framework knowledge base** — 1,900+ lines of LangGraph, CrewAI, MCP, LlamaIndex, and Anthropic best practices injected during self-improvement
- **Feedback loop** — n8n workflow runs daily self-assessment, generates improvement suggestions
- **Lesson learning** — recent failure patterns injected into LLM prompts to avoid repeating mistakes

---

## Code Agent (Two-Tier System)
- **Tier 1 (Heavy)** — Claude Sonnet 4.6 via Anthropic API for complex tasks: project-level edits, debugging, multi-file refactoring
- **Tier 2 (Quick)** — Groq (Llama 70B → 8B) for simple questions, write-a-function, explain-this-code (streams tokens live)
- **Auto-routing** — detects task complexity from keywords and routes accordingly
- **Groq fallback** — if Groq is unavailable, transparently falls back to Claude Sonnet

---

## Communication
- **WhatsApp messaging** — send texts, initiate calls, attach images via WhatsApp Desktop
- **Email** — compose and send via Gmail with attachment support
- **Generic messaging** — send messages on any Windows desktop app (Telegram, Discord, etc.)
- **Contact management** — save contacts with nicknames, phone numbers, emails; fuzzy lookup; VCF import

---

## Vision & Perception
- **Live camera analysis** — captures webcam frame, sends to Claude vision for interpretation (requires OpenCV)
- **Screen capture analysis** — screenshots desktop, asks Claude "what do you see?"
- **Video analysis** — extracts 6–30 frames from video files, generates storyboard analysis (requires OpenCV)
- **File analysis** — reads and interprets images (JPG, PNG, BMP, WEBP)
- **Document analysis** — reads PDF, DOCX, XLSX, TXT, MD, JSON, CSV, XML (up to 15K chars); graceful error if library missing
- **Facial recognition** — LBPH face recognizer trained on known faces, scans room via webcam, identifies people (optional module)

---

## Live Streaming & Broadcasting
- **OBS Studio control** — scene switching, stream/recording toggle, mic mute, replay buffer capture, source visibility (via WebSocket API)
- **Streamlabs control** — hotkey-based scene switching, stream/recording/mic toggle
- **Auto-detection** — detects which broadcaster is running and routes commands accordingly
- **Feature-flagged** — disabled cleanly if OBS/Streamlabs not installed

---

## Web Search & Information
- **Multi-API smart routing** based on query type:
  - Movies/TV/Actors → TMDB API
  - Video games → RAWG API
  - News → NewsAPI
  - Crypto prices → CoinGecko (free, no auth)
  - General queries → SerpAPI (sports scores, finance, answer boxes)
  - Semantic search → Exa AI
  - Web scraping → Firecrawl
- **Geo-aware queries** — auto-appends user's city/state for weather and local searches
- **Conversational readout** — search results formatted by Groq LLM into natural spoken summaries
- **Weather reports** — location and time-aware weather lookups

---

## Social Media & Content Creation
- **AI-generated graphics** — creates custom images via Pollinations API (free, zero-auth)
- **Platform-specific copywriting** — Twitter (280-char enforced), Instagram, Discord
- **Automated posting** — routes content + images to n8n webhook for scheduling
- **Client analytics reports** — pulls metrics from n8n data warehouse, formats via Groq LLM
- **Feature-flagged** — disabled cleanly if n8n webhook not configured

---

## System & App Control
- **Launch any Windows app** by name with process verification
- **Close/kill apps** via taskkill
- **System controls** — volume up/down/mute, play/pause/next/prev track, screenshot, screen recording, new/close/switch tabs, refresh page, minimize all, close window
- **Power management** — shutdown and restart with 5-second grace period
- **Keyboard shortcut execution** — any Windows shortcut with modifier translation (Mac → Windows)
- **System diagnostics** — storage, RAM, CPU utilization, CPU temperature, top processes
- **Microphone control** — mute/unmute via nircmd
- **Platform abstraction** — all desktop automation goes through `core/platform.py` for clean graceful degradation

---

## Web Navigation & Music
- **Open any URL** or fall back to Google search
- **SoundCloud** — play likes, saved sets/playlists, or search
- **Spotify/Apple Music** — direct search and playback routing

---

## File Management
- **Move, rename, delete files** with human approval popup (Tkinter)
- **Soft-delete** — files go to `.rube_trash`, not permanent deletion
- **Full undo** — reverse last file action from transaction log
- **Safe file editing** — path validation, protected files/extensions, mandatory backups

---

## Memory & Learning
- **Persistent memory** — remembers user identity, preferences, contacts, relationships across sessions
- **Session memory** — tracks conversation history (last 10 turns), pending actions, current multi-turn flows
- **Contact capture** — automatically extracts and saves contact info from conversations
- **Startup self-assessment** — analyzes past failures on boot, suggests focus areas

---

## Setup & Configuration
- **First-run wizard** — `python setup_wizard.py` walks through API keys, voice providers, and optional features
- **Auto-wizard on first boot** — if `.env` is missing, wizard launches automatically
- **Feature flags** — enable/disable optional modules (desktop automation, broadcast, facial recognition, social media) without uninstalling packages
- **Runtime API key registration** — add new API keys via voice command, persisted to `.env`

---

## OTA Update System
- **Remote updates** — server pushes signed update packages
- **HMAC-SHA256 signature verification** — rejects tampered packages
- **Backup before apply** — current files backed up before any update
- **Boot test + auto-rollback** — if update breaks boot, previous version restored automatically
- **Protected paths** — `.env`, `memory/`, keys never overwritten by updates

---

## Architecture Highlights
- **Pure Python** — asyncio + threading, runs on Windows
- **Provider abstraction** — TTS, STT, and platform automation all behind swappable provider interfaces
- **Modular action system** — each capability is a plug-in module in `actions/`
- **Preflight validation** — every action type has pre-execution checks to prevent doomed operations
- **n8n workflow integration** — social media posting, analytics, and daily self-learning feedback loop
- **12+ external API integrations** — Anthropic, Groq, Cartesia, Deepgram, SerpAPI, Exa, Firecrawl, TMDB, RAWG, NewsAPI, CoinGecko, Pollinations, OBS WebSocket, n8n
- **Dynamic API key registration** — users can add new API keys via voice command, persisted to `.env`

---

## By the Numbers
- **28+ intent types** routed by AI
- **18 action modules** + 5 core provider modules
- **12+ API integrations**
- **1,900+ lines** of AI framework knowledge base
- **650+ line** system prompt with protocol specifications
- **Two-tier AI brain** — Claude Sonnet (deep) + Groq 70B/8B (fast)
- **<300ms** STT latency (Deepgram Nova-3)
- **40ms** TTS response (Cartesia Sonic)
- **100% approval-gated** self-improvement (no autonomous code writes)
