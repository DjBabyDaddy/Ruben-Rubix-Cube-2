# RUBEN — Mass Production Readiness PRD

**Version:** 2.0
**Date:** March 14, 2026
**Author:** Trell (via Claude Architecture Session)
**Audited by:** Claude Code (Opus 4.6) — 6-agent parallel research sweep
**Executor:** Claude Code
**Status:** Ready for Implementation

---

## 1. Executive Summary

RUBEN (RUBE) is a locally-hosted, Python-based autonomous AI assistant running on Windows. The long-term vision is a fully standardized, zero-employee agentic business that can be replicated, sold, and licensed to any company.

**The problem:** RUBE currently has 7 categories of dependencies that require extra downloads, manual software installation, programming knowledge, or hardware-specific configuration. These blockers make RUBE impossible to ship as a turnkey product.

**The goal of this PRD:** Eliminate every dependency that requires a buyer to do anything beyond "paste API keys and run." No model downloads, no CLI tool installations, no manual folder creation, no OS-specific workarounds. RUBE must boot and operate with nothing more than Python, pip, and API keys.

**Business model:**
- Monthly maintenance fee covers all API costs (Anthropic, Cartesia, Groq, etc.)
- Tiered activity plans determine how much a customer's RUBE can do per month
- Customers can optionally drop in their own API keys for additional services
- All deployed RUBEs receive remote updates via a secure OTA system

**Guiding principles:**
- Zero local model downloads
- API-key-only configuration for all AI services
- Graceful degradation — missing optional modules never crash the system
- Cross-platform where possible, Windows-first where unavoidable
- No SaaS dependencies beyond the approved stack (Anthropic + Groq + Cartesia + Google)
- Secure remote update capability for all deployed instances

---

## 2. Current Architecture Overview

### Core Loop (main.py)
1. Boot → Initialize STT, TTS, UI, geo-context, n8n health check
2. Voice/keyboard input → `speech_to_text.py` (Vosk — to be replaced)
3. Intent routing → `llm.py` (Claude Sonnet API)
4. Action dispatch → 28 intent handlers across action modules
5. Response → `tts.py` (Kokoro TTS — to be replaced) → audio playback via pygame

### File Structure
```
RUBE/
├── main.py                  # Boot + main event loop
├── llm.py                   # Claude API intent router + multimodal
├── tts.py                   # Text-to-speech (currently Kokoro)
├── speech_to_text.py        # Speech-to-text (currently Vosk)
├── ui.py                    # Tkinter GUI with 3D cube animation
├── core/
│   ├── prompt.txt           # System prompt (28 intents defined)
│   └── preflight.py         # Pre-execution validation
├── actions/
│   ├── open_app.py          # App launch, web nav, media, system control
│   ├── broadcast_control.py # OBS/Streamlabs control
│   ├── web_search.py        # Web search via SerpAPI + Groq narration
│   ├── weather_report.py    # Weather lookup
│   ├── send_message.py      # iMessage/SMS via pyautogui
│   ├── whatsapp.py          # WhatsApp desktop automation
│   ├── social_manager.py    # Social media posting via n8n
│   ├── analytics_manager.py # Client analytics via Groq formatting
│   ├── email_manager.py     # Email via browser automation
│   ├── contact_manager.py   # Contact CRUD
│   ├── vision.py            # Camera/screen/video/file analysis
│   ├── face_recognizer.py   # OpenCV LBPH facial recognition
│   ├── keyboard_matrix.py   # Keyboard shortcut execution
│   ├── system_status.py     # Hardware diagnostics
│   ├── self_improver.py     # Self-improvement + subagent system
│   ├── file_editor.py       # Safe file editing with backup/audit
│   ├── file_manager.py      # File operations
│   └── code_agent.py        # Code task execution
├── memory/
│   ├── memory_manager.py    # Persistent memory CRUD
│   ├── temporary_memory.py  # Session state + pending edit queue
│   ├── feedback_logger.py   # Action result logging + self-assessment
│   ├── memory.json          # Persistent memory store
│   ├── feedback_log.json    # Execution history
│   └── pending_edits.json   # Approval queue for file edits
├── ai_docs/                 # Architecture knowledge for AI tools
├── ai_specs/                # Current work-in-progress specs (this file)
└── ai_toolkit/              # Reusable code patterns and templates
```

### Current Intent Map (from prompt.txt + main.py routing)
28 intents: chat, web_navigate, system_launch, system_close, system_control, broadcast_control, whatsapp_message, execute_shortcut, search, system_diagnostics, hardware_control, vision_analysis, facial_recognition, play_soundcloud, register_api_key, generate_social_post, email_message, generate_analytics_report, save_contact, import_contacts, review_pending_edits, approve_edit, reject_edit, request_file_edit, self_improve, code_task, send_message, play_media

> **Note:** `send_message`, `play_media`, and `show_suggestions` are routed in main.py but not formally documented in prompt.txt. Phase 6 will fix this.

---

## 3. Dependency Audit — Full Blocker List

### BLOCKER 1: Vosk Local Speech Model (CRITICAL)

**File:** `speech_to_text.py`

**Current implementation:**
```python
from vosk import Model as VoskModel, KaldiRecognizer
# Requires a 1.8GB model folder named "model" in project root
```

**Why it blocks mass production:**
- Requires downloading a 1.8GB model folder manually
- Must be renamed to `model` and placed in the project root
- The code prints an error and fails if the folder is missing
- Different languages require different model downloads
- No average buyer will do this

**Required fix:** Replace with a cloud STT provider accessed via API key only.

**Recommended provider: Deepgram Nova-3**
- Fastest real-time streaming STT (sub-300ms latency)
- Python SDK: `pip install deepgram-sdk` (v6.0.1, Feb 2026)
- WebSocket streaming with Keyterm Prompting (boosts "Ruben" recognition)
- $0.46/hr streaming, $200 free credits to start
- KeepAlive feature to maintain connections without transcription costs during idle

**Alternative providers (in priority order):**
1. ElevenLabs Scribe v2 Realtime — 150ms latency, unified vendor if using ElevenLabs TTS
2. AssemblyAI Universal-Streaming — cheapest at $0.15/hr (session-based billing)
3. Google Cloud Speech-to-Text (Chirp 3) — solid but expensive ($0.96/hr)
4. Groq Whisper — batch only (no streaming), but cheapest at $0.04/hr for non-realtime

> **OpenAI Whisper API does NOT support real-time streaming.** It processes pre-recorded files only. Not suitable as primary STT for a voice assistant.

**Wake word strategy (PRD v1 gap):**
No cloud STT provider offers native wake word detection. Three options:
1. **Recommended:** Keep a lightweight local wake word engine (Picovoice Porcupine, ~2MB, pip-installable) to trigger cloud STT only when needed — saves money on idle transcription
2. **Alternative:** Use Deepgram KeepAlive + keyword matching on streaming transcripts (simple but pays for idle audio)
3. **Budget:** Post-recognition keyword matching on all transcripts (simplest, most expensive)

**Implementation requirements:**
- Must preserve wake-word detection ("Ruben", "Reuben", "Rubin")
- Must preserve echo cancellation (`apply_echo_scalpel`)
- Must preserve `stop_listening_flag` threading model
- Must preserve the `vosk_ready` event pattern (rename to `stt_ready`)
- `sounddevice` can remain for microphone capture — only the recognition engine changes
- Add `STT_PROVIDER` and `STT_API_KEY` to `.env`
- Graceful fallback: if no STT key is configured, disable voice input but keep keyboard input working

**Key interfaces to preserve:**
```python
# These function signatures must not change:
def initialize_vosk()      → rename to initialize_stt()
def record_voice() -> str  → same signature, same return type
vosk_ready = threading.Event()  → rename to stt_ready
```

---

### BLOCKER 2: Kokoro Local TTS Model (CRITICAL)

**File:** `tts.py`

**Current implementation:**
```python
from kokoro import KPipeline
_kokoro_pipeline = KPipeline(lang_code='a')  # American English
# Generates audio locally via numpy + soundfile
```

**Why it blocks mass production:**
- `kokoro` requires pip install + model weight downloads
- Depends on PyTorch or equivalent ML runtime
- Requires `numpy` and `soundfile` for audio processing
- Different machines may have CUDA/CPU compatibility issues
- Voice quality is limited compared to cloud options

**Required fix:** Replace with a cloud TTS provider accessed via API key only.

**Primary provider: Cartesia Sonic 3**
- **40ms TTFB** — 7-12x faster than ElevenLabs, best latency in the industry
- State Space Model architecture — purpose-built for real-time voice agents
- Python SDK: `pip install cartesia` (sync/async/websocket clients, Python 3.9+)
- 42 languages, laughter via `[laughter]` tags, fine-grained volume/speed/emotion control
- Voice cloning: instant, from 3-15 seconds of audio
- **Pricing:** ~$47/1M chars. Plans: Free (10K credits), Pro ($5/mo), Startup ($49/mo), Scale ($299/mo)
- ~1/4th the cost of ElevenLabs with dramatically lower latency

**Alternative providers (in priority order):**
1. ElevenLabs v3 — best absolute voice quality, $120-206/1M chars, voice cloning
2. OpenAI gpt-4o-mini-tts — instructable voices ("speak like a sympathetic agent"), $15-30/1M chars
3. Google Gemini TTS (2.5 Flash/Pro) — context-aware pacing, multi-speaker, token-based pricing
4. Inworld TTS-1 Max — #1 on Speech Arena benchmarks, $10/1M chars (worth evaluating)

**Free fallback: edge-tts**
- Still working and maintained as of March 2026
- `pip install edge-tts` — uses Microsoft Edge's online TTS service
- No API key needed, no Windows or Edge browser required
- Risk: can be rate-limited under heavy usage (unofficial API)
- Quality: decent but noticeably below Cartesia/ElevenLabs tier

**Implementation requirements:**
- `pygame` stays for audio playback — only the generation step changes
- Must preserve the gatekeeper queue system (`output_queue`, `_gatekeeper_worker`)
- Must preserve `is_speaking` flag and `stop_event` interruption system
- Must preserve `expecting_reply_until` timing system
- Must preserve subtitle sync (`total_audio_ms` return from `_generate_tts`)
- The cloud API must return audio bytes that can be saved as WAV/MP3 and played via pygame
- Add `TTS_PROVIDER`, `TTS_API_KEY`, and `TTS_VOICE_ID` to `.env`
- Graceful fallback: if no TTS key is configured, fall back to edge-tts

**Key interfaces to preserve:**
```python
# These function signatures must not change:
def edge_speak(text: str, ui=None, fast_ack=False)  # entry point — name can stay
def _generate_tts(text) -> float  # returns duration in ms
def preload_pipeline()  # becomes a no-op or connection test
def stop_speaking()  # same behavior
```

**Audio format note:** Kokoro outputs raw numpy arrays at 24kHz. Cartesia Sonic returns PCM, WAV, or MP3 bytes via WebSocket or REST. The `_generate_tts` function should:
1. Call the Cartesia API (prefer WebSocket for streaming)
2. Save the returned audio bytes to `output.wav`
3. Return the audio duration in milliseconds
4. `pygame.mixer.music.load()` handles both WAV and MP3

---

### BLOCKER 3: Claude Code CLI Subprocess (MODERATE)

**File:** `self_improver.py` (subprocess at lines 174-180)

**Current implementation:**
```python
proc = subprocess.Popen(
    ["claude", "--print", "-p", prompt],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=PROJECT_ROOT,
)
```

**Why it blocks mass production:**
- Requires installing Claude Code (Node.js 18+ prerequisite)
- Requires separate authentication (`claude login`)
- Must be on the system PATH
- That's 3 extra setup steps most buyers won't complete
- Node.js alone is a 100MB+ download

**Required fix:** Replace with the **Claude Agent SDK** — the official programmatic replacement for the Claude Code CLI.

**Implementation using Claude Agent SDK:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def invoke_subagent(file_path, reason):
    """Propose a fix using the Claude Agent SDK (no CLI dependency)."""
    brain = load_brain()
    brain_section = f"\n\n[AI FRAMEWORK KNOWLEDGE BASE]\n{brain}" if brain else ""

    prompt = (
        f"You are analyzing a Python file from the RUBE AI assistant project.\n"
        f"File: {file_path}\n"
        f"Issue: {reason}\n"
        f"{brain_section}\n\n"
        f"Read the file, analyze the issue, and propose a fix.\n"
        f"Return ONLY a JSON object with exactly these keys:\n"
        f'{{"proposed_fix": "<the complete new file content>", "reason": "<one sentence>"}}\n'
        f"No markdown. No explanation outside the JSON."
    )

    try:
        result_text = ""
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                allowed_tools=["Read", "Glob", "Grep"],  # read-only tools
            ),
        ):
            if hasattr(message, 'content'):
                result_text += message.content

        parsed = json.loads(result_text)
        if "proposed_fix" in parsed:
            return {"proposed_fix": parsed["proposed_fix"], "reason": parsed.get("reason", reason)}
    except Exception as e:
        print(f"⚠️ Subagent API error: {e}")
    return None
```

**Why Agent SDK over raw `messages.create()`:**
- Built-in file Read/Write/Edit/Bash/Glob/Grep tools — agent reads files autonomously
- Reads `CLAUDE.md` and `ai_docs/` automatically (same context as CLI)
- Autonomous agent loop — reasons through bugs without manual orchestration
- Hook system for integrating with RUBE's approval pipeline
- Session management for multi-turn interactions
- `pip install claude-agent-sdk` — pure Python, no Node.js

**What this preserves:**
- Same `proposed_fix` + `reason` return structure
- Same error handling pattern (returns None on failure)
- All downstream code (`add_to_queue`, `handle_request_file_edit`, `handle_self_improve`) unchanged

**What this removes:**
- `subprocess` import (from self_improver.py)
- Claude Code CLI dependency entirely
- Node.js requirement entirely

---

### BLOCKER 4: LM Studio Local Model (MODERATE)

**File:** `code_agent.py`, `.env` (`LM_STUDIO_URL`, `LM_STUDIO_MODEL`, `LM_STUDIO_TOKEN`)

**Current implementation:**
- Uses LM Studio running Qwen 3.5 9B locally for code tasks
- Requires downloading LM Studio application
- Requires downloading a ~6GB model file
- Requires LM Studio to be running as a background server

**Why it blocks mass production:**
- LM Studio is a separate desktop application (manual install)
- Model download is 6GB+
- Must be manually started before RUBE can use it
- Hardware-dependent (needs sufficient RAM/VRAM)
- Average buyer won't configure this

**Required fix:** Replace with **Groq API** — cloud-hosted inference with generous free tier.

**Primary: Groq Free Tier with automatic model fallback**

Groq provides free-tier access to multiple models with rate limits that reset daily/monthly:

| Model | Speed | Free Tier Limits |
|---|---|---|
| Llama 3.3 70B | Lightning fast | ~100K tokens/day, resets daily |
| Llama 3.1 8B | Even faster | Higher limits, fallback model |

**Implementation — automatic tier management:**
```python
import os
from groq import Groq

GROQ_PRIMARY_MODEL = "llama-3.3-70b-versatile"
GROQ_FALLBACK_MODEL = "llama-3.1-8b-instant"

_groq_client = None
_current_model = GROQ_PRIMARY_MODEL
_rate_limited = False

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client

def groq_completion(prompt, system_prompt=None, max_tokens=4096):
    """Call Groq with automatic model fallback on rate limit."""
    global _current_model, _rate_limited
    client = get_groq_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=_current_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        # If we were on fallback and this succeeded, try primary next time
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        if "rate_limit" in error_str.lower() or "429" in error_str:
            if _current_model == GROQ_PRIMARY_MODEL:
                print(f"⚠️ Groq 70B rate limited. Switching to 8B fallback.")
                _current_model = GROQ_FALLBACK_MODEL
                _rate_limited = True
                return groq_completion(prompt, system_prompt, max_tokens)  # retry with 8B
            else:
                print(f"⚠️ Both Groq models rate limited. Waiting for reset.")
                return None
        raise

def check_groq_tier_reset():
    """Called periodically (e.g., hourly) to try upgrading back to 70B."""
    global _current_model, _rate_limited
    if _rate_limited:
        _current_model = GROQ_PRIMARY_MODEL
        _rate_limited = False
```

**What this replaces:**
- `LM_STUDIO_URL`, `LM_STUDIO_MODEL`, `LM_STUDIO_TOKEN` env vars → `GROQ_API_KEY`
- All LM Studio subprocess/HTTP calls → `groq_completion()` function
- Code agent's local model calls → Groq API calls
- Groq is already used in `web_search.py` and `analytics_manager.py`, so this unifies the dependency

**What this removes:**
- LM Studio application requirement
- Local model download requirement
- Hardware-dependent inference

---

### BLOCKER 5: OpenCV + Facial Recognition Stack (MODERATE)

**Files:** `face_recognizer.py`, `vision.py`

**Current implementation:**
```python
# face_recognizer.py
import cv2
import numpy as np
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# vision.py
import cv2
cam = cv2.VideoCapture(0)  # webcam access
```

**Why it blocks mass production:**
- OpenCV (`opencv-python`) is a large install (~50MB)
- `opencv-contrib-python` (needed for LBPH face recognizer) is even larger
- Windows often needs Visual C++ redistributables
- Facial recognition requires manually populating `memory/known_faces/` with photos
- Camera access varies across machines and OS versions

**Required fix:** Make OpenCV and facial recognition fully optional modules that gracefully degrade.

**Implementation — face_recognizer.py:**
```python
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("ℹ️ OpenCV not installed. Facial recognition disabled. Install opencv-contrib-python to enable.")

def initialize_facial_matrix():
    if not OPENCV_AVAILABLE:
        print("ℹ️ Facial recognition skipped — OpenCV not available.")
        return
    # ... existing implementation unchanged ...

def identity_scan_room(parameters, response, player, session_memory):
    if not OPENCV_AVAILABLE:
        edge_speak("Boss, facial recognition requires OpenCV. It's not installed on this system.", player)
        return
    # ... existing implementation unchanged ...
```

**Implementation — vision.py camera and video functions:**
```python
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

def _analyze_camera(user_prompt, player):
    if not OPENCV_AVAILABLE:
        edge_speak("Boss, camera access requires OpenCV. It's not installed on this system.", player)
        return
    # ... existing implementation ...

def _analyze_video(user_prompt, player, specific_path=None):
    if not OPENCV_AVAILABLE:
        edge_speak("Boss, video analysis requires OpenCV. It's not installed on this system.", player)
        return
    # ... existing implementation ...
```

**Screen capture:** `_analyze_screen` uses `PIL.ImageGrab` which is lightweight and cross-platform. No change needed.

**Image analysis:** `_analyze_file` for images uses PIL (Pillow), lightweight pip install. No change needed.

**Document analysis:** Wrap each in try/except:
```python
elif ext == 'pdf':
    try:
        import pdfplumber
    except ImportError:
        edge_speak("Boss, I need the pdfplumber package to read PDFs. Run: pip install pdfplumber", player)
        return
```

---

### BLOCKER 6: pyautogui + pygetwindow (MODERATE — Windows Lock-in)

**Files:** `broadcast_control.py`, `email_manager.py`, `keyboard_matrix.py`, `open_app.py`, `send_message.py`

**Current implementation:**
```python
import pyautogui
import pygetwindow as gw  # Windows-only
```

**Why it blocks mass production:**
- `pygetwindow` is Windows-only — crashes on Mac/Linux
- `pyautogui` works cross-platform for mouse/keyboard but window management differs
- These power ~40% of RUBE's intent handlers

**Required fix:** Create a platform adapter layer.

**Implementation — new file `core/platform.py`:**
```python
"""Platform abstraction layer for desktop automation.

All action modules import from here instead of directly from pyautogui/pygetwindow.
This allows RUBE to run on any OS with graceful degradation.
"""
import platform
import subprocess

PLATFORM = platform.system()  # "Windows", "Darwin", "Linux"

# --- Window management ---

def get_window_by_title(title_substring):
    """Find a window by partial title match. Returns window object or None."""
    if PLATFORM == "Windows":
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title_substring)
            return windows[0] if windows else None
        except ImportError:
            return None
    elif PLATFORM == "Darwin":
        # macOS: future implementation
        return None
    else:
        # Linux: future implementation
        return None

def focus_window(window):
    """Bring a window to the foreground."""
    if window is None:
        return False
    try:
        if hasattr(window, 'activate'):
            window.activate()
            return True
    except Exception:
        pass
    return False

def get_running_processes():
    """Return list of running process names (lowercase)."""
    try:
        import psutil
        return [p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info['name']]
    except Exception:
        return []

# --- Keyboard/mouse automation ---

def type_text(text, interval=0.02):
    """Type text with optional keystroke interval."""
    try:
        import pyautogui
        pyautogui.typewrite(text, interval=interval) if all(ord(c) < 128 for c in text) else pyautogui.write(text)
    except ImportError:
        print("⚠️ pyautogui not installed. Desktop automation disabled.")

def press_hotkey(*keys):
    """Press a keyboard shortcut."""
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
    except ImportError:
        print("⚠️ pyautogui not installed. Keyboard shortcuts disabled.")

def click(x=None, y=None):
    """Click at coordinates or current position."""
    try:
        import pyautogui
        pyautogui.click(x, y)
    except ImportError:
        pass

DESKTOP_AUTOMATION_AVAILABLE = True
try:
    import pyautogui
except ImportError:
    DESKTOP_AUTOMATION_AVAILABLE = False
    print("ℹ️ pyautogui not installed. Desktop automation features disabled.")
```

**Migration pattern:** Each action module replaces direct imports:
```python
# BEFORE:
import pyautogui
import pygetwindow as gw

# AFTER:
from core.platform import get_window_by_title, focus_window, type_text, press_hotkey, DESKTOP_AUTOMATION_AVAILABLE
```

**Note:** Full Mac/Linux implementations are NOT required for v1.0. The adapter layer ensures missing packages don't crash and supports future platform expansion.

---

### BLOCKER 7: OBS WebSocket (LOW — Niche Feature)

**File:** `broadcast_control.py`

**Current implementation:**
```python
import obsws_python as obs  # Top-level import — crashes if not installed
```

**Why it blocks mass production:**
- Requires OBS Studio installed
- Requires OBS WebSocket plugin configured
- ~1% of buyers will be broadcasters
- Top-level import crashes the entire module on ImportError

**Two options for fixing this:**

**Option A — MCP replacement (recommended):**
Replace custom `broadcast_control.py` with the `obs-mcp` server (147 OBS tools, zero maintenance):
```json
{
  "mcpServers": {
    "obs": {
      "command": "npx",
      "args": ["-y", "obs-mcp@latest"],
      "env": { "OBS_WEBSOCKET_PASSWORD": "" }
    }
  }
}
```
This gives RUBE scene management, source control, streaming/recording, replay buffer, transitions, screenshots, and system stats — far more than the current custom implementation.

**Option B — Lazy import (minimum fix):**
```python
# BEFORE (line 8):
import obsws_python as obs

# AFTER:
try:
    import obsws_python as obs
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False
    obs = None

def connect_obs():
    if not OBS_AVAILABLE:
        return None
    # ... existing implementation ...
```

---

## 4. Additional Required Changes

### 4A. Groq as RUBE's Speed Brain

RUBE's delegation architecture changes from:
- Claude = judgment/routing, Groq = narration/formatting, LM Studio = code tasks

To:
- **Claude Sonnet 4.6** = judgment, intent routing, complex reasoning
- **Groq (Llama 3.3 70B → 8B fallback)** = narration, formatting, code tasks, quick completions
- **Claude Agent SDK** = self-improvement subagent (file analysis + fix proposals)

Groq is already used in `web_search.py` and `analytics_manager.py`. This migration unifies all "speed layer" tasks under one provider and eliminates LM Studio entirely.

**Automatic tier management:** When the 70B model hits rate limits, RUBE automatically falls back to the 8B model until limits reset. This happens transparently — the user never notices. A periodic check function tries to upgrade back to 70B.

### 4B. Structured Outputs for Intent Routing

`llm.py` currently uses `safe_json_parse` to extract intent JSON from Claude's response. **Structured outputs are now GA on the Anthropic API** — guaranteed valid JSON with schema enforcement:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[...],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "intent": {"type": "string"},
                    "parameters": {"type": "object"},
                    "text": {"type": "string"}
                },
                "required": ["intent", "parameters", "text"],
                "additionalProperties": False
            }
        }
    }
)
# Zero parsing errors, guaranteed schema compliance
# safe_json_parse becomes unnecessary
```

### 4C. Requirements Splitting

**requirements-core.txt** (mandatory — the product doesn't work without these):
```
anthropic>=0.84.0
claude-agent-sdk>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
pygame>=2.5.0
psutil>=5.9.0
Pillow>=10.0.0
groq>=0.5.0
cartesia>=1.0.0
deepgram-sdk>=6.0.0
edge-tts>=6.1.0
```

**requirements-optional.txt** (buyer chooses what they need):
```
# Desktop automation (Windows recommended)
pyautogui>=0.9.54
pygetwindow>=0.0.9

# Broadcast control (requires OBS Studio)
obsws-python>=1.6.0

# Computer vision & facial recognition
opencv-contrib-python>=4.8.0
numpy>=1.24.0

# Document analysis
pdfplumber>=0.10.0
python-docx>=1.0.0
openpyxl>=3.1.0

# Drag-and-drop support
tkinterdnd2>=0.3.0

# Web search
serpapi>=0.1.0
firecrawl>=1.0.0
```

### 4D. Setup Wizard / First-Run Configuration

Create `setup_wizard.py` — a guided first-run experience:

```
RUBE First-Time Setup
=====================

Step 1 of 4: Required API Keys

  Anthropic API Key (powers RUBE's brain):
  > sk-ant-xxxx

  Groq API Key (powers RUBE's speed layer — free at groq.com):
  > gsk_xxxx

Step 2 of 4: Voice Configuration

  Text-to-Speech Provider:
  [1] Cartesia Sonic (recommended — fastest, best value)
  [2] ElevenLabs (premium voice quality)
  [3] Edge TTS (free, no API key needed)
  > 1

  Cartesia API Key:
  > xxxx

  Speech-to-Text Provider:
  [1] Deepgram (recommended — fastest streaming)
  [2] Skip (keyboard-only mode)
  > 1

  Deepgram API Key:
  > xxxx

Step 3 of 4: Optional Features

  Enable desktop automation (app control, shortcuts)? [Y/n]: Y
  Enable broadcast control (OBS/Streamlabs)? [y/N]: N
  Enable facial recognition? [y/N]: N
  Enable social media posting via n8n? [y/N]: Y

    n8n Webhook URL:
    > https://rubecube.app.n8n.cloud/webhook/rube-social

Step 4 of 4: Identity

  What should RUBE call you?
  > Boss

✅ Configuration saved to .env
✅ Run `python main.py` to start RUBE!
```

### 4E. Feature Flags in .env

```env
# === Required ===
ANTHROPIC_API_KEY=sk-ant-xxxx
GROQ_API_KEY=gsk_xxxx

# === Voice ===
STT_PROVIDER=deepgram          # deepgram | disabled
STT_API_KEY=xxxx
TTS_PROVIDER=cartesia           # cartesia | elevenlabs | edge_tts
TTS_API_KEY=xxxx
TTS_VOICE_ID=default            # Provider-specific voice ID

# === Optional: Social media ===
N8N_WEBHOOK_URL=https://...
INSTAGRAM_BUSINESS_ACCOUNT_ID=xxxx
FACEBOOK_ACCESS_TOKEN=xxxx

# === Optional: Search ===
SERPAPI_API_KEY=xxxx

# === Optional: User-added API keys ===
# Customers can drop in additional keys for services they want
# EXA_API_KEY=xxxx
# ELEVENLABS_API_KEY=xxxx

# === Feature flags ===
FEATURE_DESKTOP_AUTOMATION=true
FEATURE_BROADCAST_CONTROL=false
FEATURE_FACIAL_RECOGNITION=false
FEATURE_SOCIAL_MEDIA=true

# === Remote Updates ===
RUBE_INSTANCE_ID=                # Auto-generated on first boot
RUBE_UPDATE_SERVER=              # URL of the update server
RUBE_AUTO_UPDATE=true            # Allow OTA updates
```

### 4F. Boot Sequence Changes (main.py)

```python
from dotenv import load_dotenv
load_dotenv()

# Feature flag checks
FEATURES = {
    "desktop_automation": os.getenv("FEATURE_DESKTOP_AUTOMATION", "true").lower() == "true",
    "broadcast_control": os.getenv("FEATURE_BROADCAST_CONTROL", "false").lower() == "true",
    "facial_recognition": os.getenv("FEATURE_FACIAL_RECOGNITION", "false").lower() == "true",
    "social_media": os.getenv("FEATURE_SOCIAL_MEDIA", "false").lower() == "true",
}

# Conditional imports based on feature flags
if FEATURES["broadcast_control"]:
    try:
        from actions.broadcast_control import broadcast_control
    except ImportError:
        FEATURES["broadcast_control"] = False
        print("ℹ️ Broadcast control disabled — missing dependencies.")

if FEATURES["facial_recognition"]:
    try:
        from actions.face_recognizer import identity_scan_room, initialize_facial_matrix
    except ImportError:
        FEATURES["facial_recognition"] = False
        print("ℹ️ Facial recognition disabled — missing dependencies.")
```

The intent dispatcher checks feature flags before dispatching:
```python
elif intent == "broadcast_control":
    if not FEATURES["broadcast_control"]:
        edge_speak("Boss, broadcast control is not enabled on this system.", ui)
        continue
    threading.Thread(target=_run_and_log, args=(broadcast_control, "broadcast_control", args), daemon=True).start()
```

### 4G. Secure Remote Update System (OTA)

**Purpose:** All deployed RUBEs must be remotely updatable without requiring customer technical knowledge. This is critical for a product that will "most likely be outright replaced soon" — the update system ensures every customer automatically gets the next-gen framework.

**Architecture:**
```
Update Server (your hosting)
    │
    ├── /api/check-update     → Returns latest version + changelog
    ├── /api/download-update  → Returns signed update package
    └── /api/register         → Registers new RUBE instances

RUBE Client (customer's machine)
    │
    ├── core/updater.py       → Checks for updates, downloads, verifies, applies
    ├── core/update_signer.py → Verifies cryptographic signatures
    └── .rube_version         → Current version hash
```

**Security requirements:**
1. **Cryptographic signing** — every update package is signed with your private key. RUBE verifies the signature before applying. Prevents tampering.
2. **HTTPS only** — all update traffic over TLS
3. **Rollback capability** — RUBE backs up its current state before applying updates. If the update fails boot test, automatic rollback.
4. **Instance registration** — each RUBE gets a unique `RUBE_INSTANCE_ID` on first boot. The update server tracks which instances are on which version.
5. **Staged rollouts** — update server can target specific instances or percentages for gradual rollout
6. **Customer consent** — `RUBE_AUTO_UPDATE=true` by default, but customer can disable and update manually

**Implementation sketch — `core/updater.py`:**
```python
import hashlib
import json
import os
import shutil
import requests
from pathlib import Path

UPDATE_SERVER = os.getenv("RUBE_UPDATE_SERVER", "")
INSTANCE_ID = os.getenv("RUBE_INSTANCE_ID", "")
VERSION_FILE = Path(__file__).parent.parent / ".rube_version"
BACKUP_DIR = Path(__file__).parent.parent / ".rube_backup"

def check_for_updates():
    """Check the update server for a newer version."""
    if not UPDATE_SERVER or not INSTANCE_ID:
        return None
    try:
        resp = requests.get(
            f"{UPDATE_SERVER}/api/check-update",
            params={"instance_id": INSTANCE_ID, "current_version": get_current_version()},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("update_available"):
                return data  # {version, changelog, download_url, signature}
    except Exception:
        pass
    return None

def apply_update(update_info):
    """Download, verify, backup, and apply an update."""
    # 1. Download update package
    # 2. Verify cryptographic signature
    # 3. Backup current files to .rube_backup/
    # 4. Extract and apply update
    # 5. Run boot test (import main, check no crashes)
    # 6. If boot test fails, rollback from backup
    # 7. Update .rube_version
    pass

def get_current_version():
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "0.0.0"
```

**Boot integration:** RUBE checks for updates on every boot (non-blocking background thread):
```python
# In main.py boot sequence
if os.getenv("RUBE_AUTO_UPDATE", "true").lower() == "true":
    threading.Thread(target=check_and_apply_updates, daemon=True).start()
```

---

## 5. Migration Checklist

### Phase 0: Foundation (Structured Outputs + Requirements Fix)
- [ ] 0.1 Fix `requirements.txt` formatting (Pillow/pygetwindow on separate lines)
- [ ] 0.2 Add missing packages to requirements.txt: `anthropic`, `numpy`, `groq`, `firecrawl`
- [ ] 0.3 Implement structured outputs in `llm.py` via `output_config` JSON schema
- [ ] 0.4 Document undocumented intents (`send_message`, `play_media`, `show_suggestions`) in `core/prompt.txt`
- [ ] 0.5 Test: Intent routing still works with structured output (no `safe_json_parse` needed)

### Phase 1: Cloud TTS — Cartesia Sonic 3 (replaces Kokoro)
- [ ] 1.1 Create `core/tts_providers.py` with abstract interface
- [ ] 1.2 Implement Cartesia Sonic 3 provider (primary) — WebSocket for streaming, REST fallback
- [ ] 1.3 Implement Edge TTS provider (free fallback)
- [ ] 1.4 Refactor `tts.py` — replace `_get_pipeline()` and `_generate_tts()` with provider dispatch
- [ ] 1.5 Remove `from kokoro import KPipeline` and all numpy/soundfile TTS-specific imports
- [ ] 1.6 Add `TTS_PROVIDER`, `TTS_API_KEY`, `TTS_VOICE_ID` to `.env.example`
- [ ] 1.7 Test: RUBE speaks with Cartesia Sonic 3
- [ ] 1.8 Test: RUBE falls back to Edge TTS when no TTS_API_KEY is set
- [ ] 1.9 Test: Subtitle sync still works (duration in ms returned correctly)
- [ ] 1.10 Test: `stop_speaking()` interruption still works mid-sentence

### Phase 2: Cloud STT — Deepgram Nova-3 (replaces Vosk)
- [ ] 2.1 Create `core/stt_providers.py` with abstract interface
- [ ] 2.2 Implement Deepgram streaming provider (primary) with Keyterm Prompting for "Ruben"
- [ ] 2.3 Refactor `speech_to_text.py` — replace Vosk model loading with provider init
- [ ] 2.4 Preserve wake-word detection ("Ruben"/"Reuben"/"Rubin") via post-recognition keyword matching
- [ ] 2.5 Preserve echo cancellation (`apply_echo_scalpel`)
- [ ] 2.6 Preserve `stop_listening_flag` and `stt_ready` (renamed from `vosk_ready`) events
- [ ] 2.7 Remove `from vosk import Model as VoskModel, KaldiRecognizer`
- [ ] 2.8 Add `STT_PROVIDER`, `STT_API_KEY` to `.env.example`
- [ ] 2.9 Implement keyboard-only fallback when `STT_PROVIDER=disabled`
- [ ] 2.10 Test: Wake word detection works with cloud STT
- [ ] 2.11 Test: RUBE functions in keyboard-only mode when STT is disabled
- [ ] 2.12 Test: Echo scalpel filters out RUBE's own speech from cloud STT

### Phase 3: Groq Speed Brain (replaces LM Studio)
- [ ] 3.1 Create `core/groq_brain.py` with `groq_completion()` and automatic 70B→8B fallback
- [ ] 3.2 Implement periodic tier reset check (tries 70B again after cooldown)
- [ ] 3.3 Refactor `code_agent.py` — replace LM Studio HTTP calls with `groq_completion()`
- [ ] 3.4 Verify `web_search.py` and `analytics_manager.py` Groq usage is consistent with new module
- [ ] 3.5 Remove `LM_STUDIO_URL`, `LM_STUDIO_MODEL`, `LM_STUDIO_TOKEN` from `.env.example`
- [ ] 3.6 Test: Code tasks execute via Groq 70B
- [ ] 3.7 Test: Rate limit triggers automatic fallback to 8B
- [ ] 3.8 Test: Tier reset check upgrades back to 70B when limits clear

### Phase 4: Self-Improvement Subagent (replaces Claude Code CLI)
- [ ] 4.1 Refactor `invoke_subagent()` in `self_improver.py` — replace subprocess with Claude Agent SDK
- [ ] 4.2 Remove `import subprocess` from `self_improver.py`
- [ ] 4.3 Configure Agent SDK with read-only tools (Read, Glob, Grep) for safe analysis
- [ ] 4.4 Test: `request_file_edit` intent produces a valid queued edit
- [ ] 4.5 Test: `self_improve` intent analyzes feedback_log and queues proposals
- [ ] 4.6 Test: Approval/rejection flow still works end-to-end

### Phase 5: Optional Module System
- [ ] 5.1 Create `core/platform.py` — platform adapter for desktop automation
- [ ] 5.2 Wrap `face_recognizer.py` imports in try/except with `OPENCV_AVAILABLE` flag
- [ ] 5.3 Wrap `broadcast_control.py` OBS import in try/except with `OBS_AVAILABLE` flag
- [ ] 5.4 Wrap `vision.py` OpenCV imports in try/except with fallback messages
- [ ] 5.5 Wrap `vision.py` document library imports (pdfplumber, python-docx, openpyxl) in try/except
- [ ] 5.6 Migrate `email_manager.py` pygetwindow usage to `core/platform.py`
- [ ] 5.7 Migrate `send_message.py` pygetwindow usage to `core/platform.py`
- [ ] 5.8 Migrate `broadcast_control.py` pyautogui usage to `core/platform.py`
- [ ] 5.9 Migrate `open_app.py` pyautogui + psutil usage to `core/platform.py`
- [ ] 5.10 Migrate `keyboard_matrix.py` pyautogui usage to `core/platform.py`
- [ ] 5.11 Add feature flag checks to `main.py` intent dispatcher
- [ ] 5.12 Test: RUBE boots clean with ZERO optional dependencies installed
- [ ] 5.13 Test: Each optional feature reports a clear message when its dependency is missing
- [ ] 5.14 Test: RUBE boots and runs all non-optional features with only `requirements-core.txt`

### Phase 6: Setup, Configuration & Remote Updates
- [ ] 6.1 Create `requirements-core.txt` and `requirements-optional.txt`
- [ ] 6.2 Create `.env.example` with all keys and feature flags documented
- [ ] 6.3 Create `setup_wizard.py` — interactive first-run configuration
- [ ] 6.4 Update `main.py` to detect first run (no .env file) and launch wizard
- [ ] 6.5 Implement `core/updater.py` — secure OTA update client
- [ ] 6.6 Implement update signature verification
- [ ] 6.7 Implement rollback on failed update
- [ ] 6.8 Auto-generate `RUBE_INSTANCE_ID` on first boot
- [ ] 6.9 Test: Fresh clone → run setup_wizard → .env created → main.py boots successfully
- [ ] 6.10 Test: Update check runs on boot without blocking startup

### Phase 7: Cleanup & Documentation
- [ ] 7.1 Remove all references to Vosk model paths and download instructions
- [ ] 7.2 Remove all references to Claude Code CLI installation
- [ ] 7.3 Remove all references to Kokoro TTS
- [ ] 7.4 Remove all references to LM Studio
- [ ] 7.5 Update README.md with new setup instructions
- [ ] 7.6 Update CLAUDE.md to reflect the new dependency-free architecture
- [ ] 7.7 Document the 3 undocumented intents in `core/prompt.txt`
- [ ] 7.8 Verify no Python file has a top-level import that can crash if an optional package is missing

---

## 6. Safety & Integrity Rules

These rules from the existing codebase MUST be preserved through all changes:

1. **Approval gates are non-negotiable.** No file writes without explicit human approval. The `pending_edits` queue, `approve_edit`, `reject_edit` system must remain intact.
2. **Backup-before-write is hardcoded.** `file_editor.py` refuses to write if no `.rube.bak` exists. Do not bypass this.
3. **Protected files are untouchable.** `.env` and `memory/memory.json` are in `PROTECTED_FILES`. `PROTECTED_EXTENSIONS` blocks `.key`, `.pem`, `.secret`.
4. **Preflight validation stays.** `core/preflight.py` catches doomed actions before execution. Extend it for new providers but don't remove existing checks.
5. **Feedback logging stays.** Every action result is logged via `feedback_logger.py`. The self-assessment system depends on this data.
6. **The prompt.txt intent schema is the contract.** All 28 intents and their parameter schemas must continue to work. The LLM's JSON output format does not change.
7. **The delegation architecture stays.** Claude = judgment/routing. Groq = speed layer (narration/formatting/code). Claude Agent SDK = self-improvement. This migration does not change the delegation model, only the providers.
8. **Update signatures are mandatory.** No OTA update is applied without cryptographic signature verification. The private key never leaves the update server.

---

## 7. Business Architecture

### Tiered Activity Plans

Monthly maintenance fee covers all API costs. Tiers determine monthly usage budgets:

| Tier | Target Customer | Monthly Budget | Includes |
|---|---|---|---|
| **Starter** | Small businesses | Low activity | Voice I/O, basic intents, keyboard mode |
| **Professional** | Active users | Medium activity | Full voice, all intents, social media, search |
| **Enterprise** | Power users | High activity | Unlimited voice, priority model access, custom voice |

**How it works:**
- RUBE tracks API usage locally (token counts, TTS characters, STT minutes)
- Usage reports are sent to the update server periodically
- If a customer approaches their tier limit, RUBE warns them
- Customers can upgrade tiers or add their own API keys to bypass limits

### Customer-Added API Keys
Customers who want additional services or unlimited usage can drop their own keys into `.env`:
```env
# Customer-added keys (optional, overrides managed allocation)
ELEVENLABS_API_KEY=xxxx      # Premium TTS upgrade
EXA_API_KEY=xxxx             # Semantic search
SERPAPI_API_KEY=xxxx          # Web search
```

When a customer-provided key exists, RUBE uses it instead of the managed allocation, and that service doesn't count against their tier budget.

---

## 8. Future Opportunities (Not In Scope, But Noted)

These emerged from the research audit and should inform future PRDs:

### Gemini Live API — Single-Model Voice Pipeline
`gemini-2.5-flash-native-audio-preview` processes raw audio in → audio out in one model call. Could serve as a "fast mode" for simple queries, eliminating the STT→LLM→TTS chain entirely. Tradeoff: loses Claude's brain for those queries.

### Gemini 2.5 Flash-Lite — Ultra-Cheap Fallback Brain
At $0.10/1M input tokens, could serve as an additional Groq fallback when both 70B and 8B models are rate-limited.

### Google ADK — Agent Orchestration
`pip install google-adk` provides agent orchestration with built-in MCP support. Could complement RUBE's action dispatch system.

### MCP Architecture Migration
Several custom action modules could be replaced by MCP servers:
- `broadcast_control.py` → `obs-mcp` (147 tools)
- Browser automation → Microsoft Playwright MCP
- Music control → Spotify MCP

### SDK Migration Note
`google-generativeai` Python package is deprecated. Use `pip install google-genai` for any future Google AI integration.

---

## 9. Testing Protocol

For each phase, verify:

1. **Boot test:** `python main.py` starts without errors
2. **Voice test** (if STT enabled): Wake word → command → response → TTS playback
3. **Keyboard test:** Type a command → intent routed → action executed → response spoken
4. **Graceful degradation test:** Remove an optional dependency → RUBE boots and reports what's missing without crashing
5. **Self-improvement test:** Trigger `self_improve` → subagent proposes edit → edit appears in queue → approve → file updated with backup
6. **Groq fallback test:** Trigger rate limit → RUBE switches to 8B → continues working → resets to 70B
7. **Update test:** Simulate update check → download → verify signature → apply → boot test passes

---

## 10. What This PRD Does NOT Cover

- Cross-platform full implementations (Mac/Linux desktop automation)
- Firebase Storage integration for Instagram image hosting
- Google Opal workflow migration
- Google Flow scheduled task migration
- NotebookLM client memory integration
- Gemini Live API "fast mode" integration
- Multi-client onboarding system
- Licensing / replication packaging
- Installer executable (.exe / .dmg / .deb)
- Update server infrastructure (separate PRD needed)

---

## 11. Success Criteria

This migration is complete when:

1. A fresh `git clone` + `pip install -r requirements-core.txt` + `python setup_wizard.py` + `python main.py` produces a fully functional RUBE with voice I/O
2. Zero local model downloads are required
3. Zero CLI tools beyond Python itself are required
4. Every optional feature degrades gracefully with a clear message
5. All 28 intents still route and execute correctly
6. The self-improvement system works without Claude Code CLI
7. Groq handles all speed-layer tasks with automatic 70B→8B fallback
8. Cartesia Sonic provides sub-100ms voice response
9. Existing features (social posting, analytics, search, vision, email, contacts) are unaffected
10. Remote update system is in place and tested

---

*End of PRD v2.0*
