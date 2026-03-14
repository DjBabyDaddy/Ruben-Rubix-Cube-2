"""RUBE Speech-to-Text — Cloud STT via Deepgram Nova-3 with wake word detection.

Replaces the local Vosk model with Deepgram's streaming WebSocket API.
Falls back to keyboard-only mode when STT is disabled or unavailable.
"""

import os
import sys
import threading
import time

SAMPLE_RATE = 16000

is_awake = False

# --- STT provider (loaded in background thread) ---
_stt_provider = None
stt_ready = threading.Event()  # renamed from vosk_ready

stop_listening_flag = threading.Event()
jarvis_last_speech = ""


def initialize_stt():
    """Initialize the STT provider in a background thread. Call from main.py at startup."""
    global _stt_provider

    from core.stt_providers import get_stt_provider

    print("🎤 RUBE is initializing speech recognition...")
    _stt_provider = get_stt_provider()

    try:
        _stt_provider.start()
    except Exception as e:
        print(f"⚠️ STT provider failed to start: {e}")

    stt_ready.set()
    print("✅ Voice matrix online.")


# Keep backward compatibility for main.py imports
initialize_vosk = initialize_stt
vosk_ready = stt_ready


def set_ai_speech(text):
    global jarvis_last_speech
    cleaned = "".join(c for c in text.lower() if c.isalnum() or c.isspace())
    jarvis_last_speech = cleaned


def apply_echo_scalpel(heard_text):
    global jarvis_last_speech
    if not jarvis_last_speech: return heard_text

    ai_text = jarvis_last_speech.strip()
    heard = heard_text.strip()
    if heard.startswith(ai_text) and len(ai_text) > 0:
        return heard.replace(ai_text, "", 1).strip()

    return heard


def has_command_substance(text, is_reply=False, has_explicit_wake_word=False):
    if is_reply: return True

    cleaned = text.lower().strip()
    if not cleaned: return False

    words = cleaned.split()
    if has_explicit_wake_word and len(words) > 1: return True

    strong_triggers = {
        "open", "close", "play", "pause", "stop", "cancel", "mute", "unmute",
        "weather", "time", "screenshot", "record", "switch", "live", "brb",
        "text", "call", "search", "what", "who", "where", "how", "tell", "email",
        "can", "could", "would", "do", "is", "are", "set", "turn", "make", "post",
        "save", "import", "contact"
    }

    if any(w in strong_triggers for w in words):
        return True

    return False


def record_voice():
    """Record voice via cloud STT with wake word detection.

    Uses Deepgram streaming transcription instead of local Vosk model.
    Preserves the same wake word, echo cancellation, and command detection logic.
    """
    global is_awake

    # Wait for STT provider to finish loading
    stt_ready.wait()

    if _stt_provider is None or not getattr(_stt_provider, 'is_running', False):
        time.sleep(1)
        return ""

    try:
        import tts
    except ImportError:
        tts = None

    # Reset provider state
    _stt_provider.reset()

    INTERRUPTS = {"stop", "cancel", "quiet", "shut up", "abort", "silence"}
    WAKE_WORDS = ["ruben", "reuben", "rubin"]

    awake_until = 0.0
    cumulative_text = ""
    last_spoken_time = time.time()

    while not stop_listening_flag.is_set():
        # Skip processing while RUBE is speaking
        if tts and getattr(tts, 'is_speaking', False):
            _stt_provider.reset()
            cumulative_text = ""
            time.sleep(0.1)
            continue

        is_expecting_reply = (tts and time.time() < tts.expecting_reply_until[0])

        # Get partial transcript for real-time display
        current_partial = _stt_provider.get_partial()

        # Check for final transcript (non-blocking with short timeout)
        final_text = _stt_provider.get_transcript(timeout=0.15)
        if final_text:
            cumulative_text += " " + final_text
            cumulative_text = cumulative_text.strip()
            last_spoken_time = time.time()

        full_heard = (cumulative_text + " " + current_partial).strip()

        if full_heard:
            explicit_wake_heard = any(w in full_heard.lower() for w in WAKE_WORDS)

            if not is_awake and explicit_wake_heard:
                sys.stdout.write("\r\033[K")
                print("[Wake Word Detected] RUBE is online.")
                is_awake = True
                awake_until = time.time() + 8.0

            if is_awake or is_expecting_reply:
                display = full_heard if len(full_heard) < 50 else "..." + full_heard[-45:]
                sys.stdout.write(f"\r Hearing: {display}".ljust(80))
                sys.stdout.flush()
                awake_until = time.time() + 8.0

        # Discard ambient noise when not awake
        if not is_awake and not is_expecting_reply and full_heard and (time.time() - last_spoken_time > 2.0):
            cumulative_text = ""
            _stt_provider.reset()
            continue

        # Command detection when awake or expecting reply
        if (is_awake or is_expecting_reply) and full_heard and (time.time() - last_spoken_time > 1.5):
            filtered = apply_echo_scalpel(full_heard)

            if any(cmd in filtered.split() for cmd in INTERRUPTS):
                is_awake = False
                return filtered

            explicit_wake_heard = any(w in filtered.lower() for w in WAKE_WORDS)
            if has_command_substance(filtered, is_expecting_reply, explicit_wake_heard):
                sys.stdout.write("\r\033[K")
                print(f"\nRUBE Command Locked: {filtered}")
                is_awake = False
                return filtered
            else:
                cumulative_text = ""
                _stt_provider.reset()
                awake_until = time.time() + 8.0

        # Auto-sleep after timeout
        if is_awake and time.time() > awake_until:
            print("\nCommand window closed. Going back to sleep.")
            is_awake = False
            cumulative_text = ""
            _stt_provider.reset()
            sys.stdout.write("\r\033[K I'm listening... (Say 'Ruben' to wake me)\n")

    return ""
