# RUBE — Claude Code Project Instructions

## What This Project Is
RUBE (Ruben Rubix Cube) is a voice-first, self-improving AI desktop assistant for Windows.
He uses Claude Sonnet 4.6 as his brain, Vosk for offline STT, Kokoro for offline TTS,
and a modular action system to control the user's entire desktop via natural language.

## Project Layout
```
main.py              — Entry point: async voice loop + intent router
llm.py               — Claude Sonnet API wrapper (intent parsing, multimodal)
ui.py                — Tkinter UI: floating 3D cube + terminal + developer dashboard
speech_to_text.py    — Vosk offline STT with wake word detection
tts.py               — Kokoro offline TTS with audio playback
actions/             — One file per capability (18 modules, each is a plug-in)
core/prompt.txt      — The 650-line system prompt that defines all intent routing rules
core/preflight.py    — Pre-execution validation (catches doomed actions before they run)
memory/              — Persistent + session state (JSON files + Python managers)
ai_docs/             — Architecture knowledge for AI tools (you're one of them)
ai_specs/            — Current work-in-progress specs
ai_toolkit/          — Reusable code patterns and templates
```

## How Intent Routing Works
1. User speaks or types → STT transcribes
2. `llm.py:get_llm_output()` sends text + memory + system prompt to Claude Sonnet
3. Claude returns JSON: `{"intent": "...", "parameters": {...}, "text": "..."}`
4. `main.py` routes intent string to the matching handler function via if/elif chain
5. Handler runs in a daemon thread, wrapped by `_run_and_log()` for metrics

## Action Handler Signature
Every action module in `actions/` exports a handler with this signature:
```python
def handler_name(parameters, response, player, session_memory):
    # parameters: dict from LLM output
    # response: string acknowledgment from LLM
    # player: RubeUI instance (call player.write_log() for terminal output)
    # session_memory: TemporaryMemory instance
```
Use `edge_speak(text, player)` from `tts.py` to speak to the user.

## Coding Rules
- Python 3.12+, pure stdlib + pip packages
- All action handlers must be non-blocking (they run in daemon threads)
- NEVER write to files without going through the approval queue (see `actions/self_improver.py`)
- Load API keys via `os.getenv()` after `load_dotenv()` — never hardcode secrets
- Use `player.write_log()` for terminal output, `edge_speak()` for voice output
- Keep the system prompt (`core/prompt.txt`) as the single source of truth for intent definitions
- When adding a new intent: update `core/prompt.txt`, create `actions/new_module.py`, add routing in `main.py`

## Key Environment Variables
- `ANTHROPIC_API_KEY` — Required. Powers the Claude Sonnet brain.
- `LM_STUDIO_URL` / `LM_STUDIO_MODEL` / `LM_STUDIO_TOKEN` — Local coding agent (Qwen 3.5 9B via LM Studio)
- `SERPAPI_API_KEY` — Web search
- `EXA_API_KEY` — Semantic search fallback
- See `.env.example` for the full list

## Do NOT
- Delete or rename files in `core/` or `memory/` without understanding the import chain
- Modify `core/prompt.txt` formatting (the LLM parses it structurally)
- Add new dependencies without checking `requirements.txt`
- Push secrets or API keys (`.env` is gitignored)
- Run destructive git operations without explicit user approval

## Reference Docs
- `ai_docs/architecture.md` — Full system architecture walkthrough
- `ai_docs/intent_catalog.md` — All 27 intents with parameters and routing rules
- `ai_docs/action_protocol.md` — How to write a new action module
- `ai_docs/memory_schema.md` — Memory system structure
- `ai_docs/api_integrations.md` — Every external API integration
- `CAPABILITIES.md` — User-facing feature list
- `RUBE_SUPER_BRAIN.md` — AI framework knowledge base (injected during self-improvement)
