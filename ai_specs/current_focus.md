# Current Focus — Updated 2026-03-14

## Active Work
- **Mass production migration** — executing PRD v2.0 (`ai_specs/mass_production_prd.md`)
- Phase 0: Foundation (structured outputs, requirements fix, undocumented intents)
- Phase 1: Cartesia Sonic 3 TTS (replaces Kokoro)
- Phase 2: Deepgram Nova-3 STT (replaces Vosk)
- Phase 3: Groq speed brain with 70B→8B auto-fallback (replaces LM Studio)

## Recently Completed
- PRD v2.0 audited and corrected via 6-agent research sweep
- Key decisions: Cartesia for voice, Groq for brain, Claude Agent SDK for self-improvement
- Added `code_task` intent (intent #26) with full routing
- Developer dashboard in ui.py (system status, action log, session state, self-assessment)
- Folder-as-architecture: ai_docs/, ai_specs/, ai_toolkit/ structure

## Known Issues
- Intent count mismatch: 28 intents routed but only 26 documented in prompt.txt
- requirements.txt missing critical packages (anthropic, numpy, groq, firecrawl)
- requirements.txt formatting bug (Pillow/pygetwindow on same line)
- `send_message`, `play_media`, `show_suggestions` routed in main.py but undocumented

## Next Up
- Execute Phase 0 (foundation fixes)
- Begin Phase 1 (Cartesia TTS integration)
- Design remote update server architecture (separate PRD)
