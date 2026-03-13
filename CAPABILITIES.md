# RUBE (Ruben Rubix Cube) — Full Capability Sheet

## Voice-First AI Desktop Assistant
- **Wake word activation** — "Ruben" / "Reuben" / "Rubin" with phonetic fuzzy matching
- **Offline speech recognition** — Vosk (1.8GB local model, no cloud dependency)
- **Natural text-to-speech** — Kokoro TTS (local inference, American English voice)
- **Echo cancellation** — filters out its own speech from mic input
- **Keyboard input fallback** — dual input mode (voice + typing)
- **Interrupt support** — "stop", "cancel", "shut up" kills speech mid-sentence

---

## AI Brain & Reasoning
- **Claude Sonnet 4.6** as the cognitive engine (Anthropic API)
- **Intent routing** — natural language parsed into 27+ structured intents with confidence scoring
- **Confidence gating** — low-confidence actions (< 0.5) trigger clarification instead of guessing
- **Compound command decomposition** — "open Chrome and play my SoundCloud likes" splits into queued actions
- **Phonetic deduction** — handles STT mishearing ("weather" vs "whether", "Ruben" vs "ribbon")
- **Contextual memory injection** — conversation history, user preferences, and lessons fed into every prompt
- **Multimodal vision** — Claude's vision API for image/video/screen analysis

---

## Self-Improvement System (Self-Healing Code)
- **Automated bug detection** — analyzes its own failure logs for patterns
- **Subagent code generation** — spawns Claude Code CLI to propose fixes
- **Human-in-the-loop approval queue** — all code changes require explicit approval before applying
- **Backup-before-write safety** — mandatory `.rube.bak` before any file modification
- **Edit audit trail** — every approved/rejected change logged with diffs
- **AI framework knowledge base** — 1,900+ lines of LangGraph, CrewAI, MCP, LlamaIndex, and Anthropic best practices injected during self-improvement
- **Feedback loop** — n8n workflow runs daily self-assessment, generates improvement suggestions
- **Lesson learning** — recent failure patterns injected into LLM prompts to avoid repeating mistakes

---

## Communication
- **WhatsApp messaging** — send texts, initiate calls, attach images via WhatsApp Desktop
- **Email** — compose and send via Gmail with attachment support
- **Generic messaging** — send messages on any Windows desktop app (Telegram, Discord, etc.)
- **Contact management** — save contacts with nicknames, phone numbers, emails; fuzzy lookup; VCF import

---

## Vision & Perception
- **Live camera analysis** — captures webcam frame, sends to Claude vision for interpretation
- **Screen capture analysis** — screenshots desktop, asks Claude "what do you see?"
- **Video analysis** — extracts 6–30 frames from video files, generates storyboard analysis
- **File analysis** — reads and interprets images (JPG, PNG, BMP, WEBP)
- **Document analysis** — reads PDF, DOCX, XLSX, TXT, MD, JSON, CSV, XML (up to 15K chars)
- **Facial recognition** — LBPH face recognizer trained on known faces, scans room via webcam, identifies people

---

## Live Streaming & Broadcasting
- **OBS Studio control** — scene switching, stream/recording toggle, mic mute, replay buffer capture, source visibility (via WebSocket API)
- **Streamlabs control** — hotkey-based scene switching, stream/recording/mic toggle
- **Auto-detection** — detects which broadcaster is running and routes commands accordingly

---

## Web Search & Information
- **Multi-API smart routing** based on query type:
  - Movies/TV/Actors → TMDB API
  - Video games → RAWG API
  - News → NewsAPI
  - Crypto prices → CoinGecko (free, no auth)
  - General queries → SerpAPI (sports scores, finance, answer boxes)
- **Geo-aware queries** — auto-appends user's city/state for weather and local searches
- **Conversational readout** — search results formatted by Groq LLM into natural spoken summaries
- **Weather reports** — location and time-aware weather lookups

---

## Social Media & Content Creation
- **AI-generated graphics** — creates custom images via Pollinations API (free, zero-auth)
- **Platform-specific copywriting** — Twitter (280-char enforced), Instagram, Discord
- **Automated posting** — routes content + images to n8n webhook for scheduling
- **Client analytics reports** — pulls metrics from n8n data warehouse, formats via Groq LLM

---

## System & App Control
- **Launch any Windows app** by name with process verification
- **Close/kill apps** via taskkill
- **System controls** — volume up/down/mute, play/pause/next/prev track, screenshot, screen recording, new/close/switch tabs, refresh page, minimize all, close window
- **Power management** — shutdown and restart with 5-second grace period
- **Keyboard shortcut execution** — any Windows shortcut with modifier translation (Mac → Windows)
- **System diagnostics** — storage, RAM, CPU utilization, CPU temperature, top processes
- **Microphone control** — mute/unmute via nircmd

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

## Architecture Highlights
- **Pure Python** — asyncio + threading, runs locally on Windows
- **No cloud dependency for voice** — both STT and TTS run offline
- **Modular action system** — each capability is a plug-in module in `actions/`
- **Preflight validation** — every action type has pre-execution checks to prevent doomed operations
- **n8n workflow integration** — social media posting, analytics, and daily self-learning feedback loop
- **10+ external API integrations** — Anthropic, Groq, SerpAPI, TMDB, RAWG, NewsAPI, CoinGecko, Pollinations, OBS WebSocket, n8n webhooks
- **Dynamic API key registration** — users can add new API keys via voice command, persisted to `.env`

---

## By the Numbers
- **27+ intent types** routed by AI
- **18 action modules**
- **10+ API integrations**
- **1,900+ lines** of AI framework knowledge base
- **650+ line** system prompt with protocol specifications
- **Zero cloud dependency** for voice (STT + TTS both local)
- **100% approval-gated** self-improvement (no autonomous code writes)
