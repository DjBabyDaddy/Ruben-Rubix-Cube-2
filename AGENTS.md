# AGENTS.md — Cross-Tool AI Agent Instructions for RUBE

## Project Overview
RUBE is a voice-first AI desktop assistant for Windows. Python 3.12+, async + threaded,
modular action system. Claude Sonnet 4.6 for reasoning, Vosk for offline STT, Kokoro for offline TTS.

## Agent Role
When working on this project, you are a development assistant helping maintain and extend RUBE.
You should understand the intent routing pipeline, action module pattern, and memory system
before proposing changes.

## Architecture Summary
- Entry: `main.py` → async voice loop → Claude Sonnet intent parser → action dispatch
- Actions: `actions/*.py` — each file is one capability (WhatsApp, vision, search, etc.)
- Brain: `core/prompt.txt` — 650-line system prompt defining all 27 intents
- Memory: `memory/` — persistent JSON + session state managers
- Voice: `speech_to_text.py` (Vosk) + `tts.py` (Kokoro) — both fully offline
- UI: `ui.py` — floating 3D Rubik's Cube with terminal panel and developer dashboard
- Local coding agent: `actions/code_agent.py` — spawns Claude Code CLI backed by LM Studio (Qwen 3.5 9B)

## Key Patterns
1. **Adding a new intent**: Edit `core/prompt.txt` (add to AVAILABLE INTENTS), create handler in `actions/`, add import + elif in `main.py`
2. **Action handler signature**: `def handler(parameters, response, player, session_memory)`
3. **Voice output**: `edge_speak(text, player)` from `tts.py`
4. **Log output**: `player.write_log(text)` for the terminal panel
5. **API keys**: Always `os.getenv()` after `load_dotenv()`, never hardcode

## Constraints
- All file writes must go through the approval queue (`actions/self_improver.py`)
- Never modify `.env` directly in code except for the API key registration flow
- The system prompt in `core/prompt.txt` is structurally parsed — preserve its format
- Tests: no test suite yet. Validate by running `python main.py` and testing voice/keyboard

## Documentation
- `ai_docs/` — Architecture, intent catalog, action protocol, memory schema, API list
- `ai_specs/` — Current work in progress and completed task specs
- `ai_toolkit/` — Code templates and common patterns
