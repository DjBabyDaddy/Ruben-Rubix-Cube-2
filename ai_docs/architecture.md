# RUBE System Architecture

## Runtime Flow

```
User speaks → Vosk STT → text string
                              ↓
                    main.py:ai_loop()
                              ↓
              llm.py:get_llm_output()
              (Claude Sonnet 4.6 API)
                              ↓
                 JSON: {intent, parameters, text}
                              ↓
              main.py: if/elif routing chain
                              ↓
              actions/<module>.py handler
              (runs in daemon thread via _run_and_log)
                              ↓
              edge_speak() → Kokoro TTS → audio out
              player.write_log() → terminal panel
```

## Core Modules

### main.py (Entry Point)
- Creates `RubeUI` (Tkinter window with 3D cube)
- Starts async event loop with two input sources: voice (Vosk) and keyboard (terminal)
- Routes intents to handlers via if/elif chain
- Wraps every action in `_run_and_log()` for metrics collection
- Manages compound command queue (deferred actions)
- Periodic reminder system for pending code edits

### llm.py (Brain)
- `get_llm_output()` — Primary cognitive function. Takes user text + memory, returns structured JSON
- `get_llm_multimodal_output()` — Vision analysis (base64 images → Claude)
- Injects: system prompt, current time, permanent memory, conversation buffer, recent lessons
- Optional: loads `RUBE_SUPER_BRAIN.md` for self-improvement calls (`use_brain=True`)

### ui.py (Interface)
- `RubeUI` class — borderless, transparent, always-on-top Tkinter window
- 3D animated Rubik's Cube rendered on a Canvas (6 face colors, sticker projection)
- Terminal panel (Toplevel) — toggled by single-click on cube
- Developer Dashboard (Toplevel) — toggled by double-click on cube
- Thread-safe logging via `root.after(0, callback)`
- Drag-to-move, file drop support (VCF auto-import)

### speech_to_text.py (Voice Input)
- Vosk offline model (1.8GB, `model/` directory)
- Wake word detection: "Ruben" / "Reuben" / "Rubin" (phonetic fuzzy match)
- `record_voice()` blocks until speech detected, returns transcription
- Echo cancellation: filters out RUBE's own TTS from mic input

### tts.py (Voice Output)
- Kokoro offline TTS (American English)
- `edge_speak(text, player)` — primary voice output function
- Gatekeeper thread prevents overlapping speech
- `stop_speaking()` / `stop_event` for interrupt support

## Action System

Every file in `actions/` is a plug-in module. Each exports one or more handler functions.

### Handler Contract
```python
def handler_name(parameters: dict, response: str, player: RubeUI, session_memory: TemporaryMemory):
    # Do work
    # Speak result: edge_speak("message", player)
    # Log result:   player.write_log("RUBE: message")
```

### Execution Wrapper
All handlers run inside `_run_and_log()` which:
1. Records start time
2. Calls the handler
3. Catches exceptions
4. Logs success/failure + elapsed time to `memory/feedback_log.json`

### Current Action Modules (18)
| Module | Intent(s) | What It Does |
|--------|----------|--------------|
| `open_app.py` | web_navigate, system_launch, system_close, play_media, system_control, play_soundcloud | OS + browser control |
| `broadcast_control.py` | broadcast_control | OBS/Streamlabs WebSocket |
| `web_search.py` | search | Multi-API routing (TMDB, RAWG, News, Crypto, SerpAPI) |
| `whatsapp.py` | whatsapp_message | WhatsApp Desktop automation |
| `email_manager.py` | email_message | Gmail send with attachments |
| `send_message.py` | send_message | Generic desktop app messaging |
| `contact_manager.py` | save_contact, import_contacts | Contact CRUD + VCF import |
| `vision.py` | vision_analysis | Camera, screen, video, file analysis via Claude |
| `face_recognizer.py` | facial_recognition | LBPH face detection + identification |
| `social_manager.py` | generate_social_post | Copywriting + image gen + n8n posting |
| `analytics_manager.py` | generate_analytics_report | n8n data warehouse queries |
| `system_status.py` | system_diagnostics, hardware_control | PC health + mic control |
| `keyboard_matrix.py` | execute_shortcut | Windows keyboard shortcut execution |
| `weather_report.py` | (via search) | Weather lookups |
| `file_editor.py` | (internal) | Safe file editing with backup + diff |
| `file_manager.py` | (internal) | Move/rename/delete with soft-delete |
| `self_improver.py` | self_improve, request_file_edit, review/approve/reject edits | Self-healing code system |
| `code_agent.py` | code_task | Local Claude Code CLI → LM Studio (Qwen 3.5 9B) |

## Memory System

### Persistent (`memory/memory.json`)
User identity, preferences, contacts, nicknames, email map. Loaded at boot, updated after each interaction.

### Session (`memory/temporary_memory.py`)
In-memory only. Tracks: conversation history (last 10), pending actions queue, pending edits queue, interaction count, last search query/result.

### Feedback (`memory/feedback_log.json`)
Every action logged with: timestamp, intent, parameters, success/fail, exec time, error detail. Max 500 entries (rotated). Used by self-assessment engine at startup.

## Self-Improvement Pipeline
1. `feedback_logger.py:generate_self_assessment()` analyzes failure patterns at boot
2. User says "improve yourself" → `self_improver.py:handle_self_improve()`
3. Identifies failing intents → reads the source file → sends to Claude Code CLI (via LM Studio)
4. Subagent proposes fix → queued for human approval
5. User says "show pending edits" → reviews diff → "approve edit X" or "reject edit X"
6. Approved edits backed up then written; rejected edits discarded

## Developer Dashboard
Double-click the cube to open. Shows 4 live-refreshing panels:
- System Status (LM Studio, Vosk, n8n, API keys)
- Action Log (last 20 actions with pass/fail and timing)
- Session State (interactions, pending edits, last I/O)
- Self-Assessment (current failure patterns and insights)
