import os
import pygame
import threading
import time
import queue
from memory.temporary_memory import TemporaryMemory
import speech_to_text 

OUTPUT_FILE = "output.wav"

# TTS provider instance (lazy-loaded via core/tts_providers.py)
_tts_provider = None
_provider_lock = threading.Lock()

def _get_provider():
    global _tts_provider
    if _tts_provider is None:
        with _provider_lock:
            if _tts_provider is None:
                from core.tts_providers import get_tts_provider
                _tts_provider = get_tts_provider()
    return _tts_provider

is_speaking = False
is_processing = False
stop_event = threading.Event()
expecting_reply_until = [0.0]

output_queue = queue.Queue()
internal_dialogue_log = [] 

def edge_speak(text: str, ui=None, fast_ack=False):
    if not text: return
    if fast_ack:
        output_queue.put({"text": text, "ui": None, "ack": True})
    else:
        internal_dialogue_log.append(text)
        output_queue.put({"text": text, "ui": ui, "ack": False})

def start_gatekeeper_thread(ui):
    t = threading.Thread(target=_gatekeeper_worker, args=(ui,), daemon=True)
    t.start()

def _gatekeeper_worker(ui):
    print("🧠 RUBE Sonic Output Matrix engaged.")
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize primary audio mixer: {e}")
        
    while True:
        output_data = output_queue.get() 
        _process_output(output_data, ui)
        output_queue.task_done()
        time.sleep(0.02)

def _process_output(output_data, ui):
    global is_speaking, is_processing
    text = output_data["text"]
    player_ui = output_data["ui"]
    fast_ack = output_data["ack"]
    
    speech_to_text.set_ai_speech(text)

    is_speaking = True
    stop_event.clear()

    try:
        from actions.face_recognizer import identity_lock_queue
        if identity_lock_queue:
            try: identity_lock_queue.put_nowait("speaking_start")
            except Exception: pass
    except Exception: pass

    try:
        total_audio_ms = _generate_tts(text)
    except Exception as e:
        print(f"TTS Error: {e}")
        is_speaking = False
        return

    if stop_event.is_set():
        is_speaking = False
        return

    # THE FIX: Pushing text to the UI Log exactly as the audio is ready to play!
    if player_ui and not fast_ack:
        player_ui.write_log(f"RUBE: {text}")

    try:
        if player_ui:
            player_ui.start_speaking()

        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if stop_event.is_set():
                pygame.mixer.music.stop()
                break
            
            if player_ui and not fast_ack:
                current_pos = pygame.mixer.music.get_pos()
                if current_pos >= 0 and total_audio_ms > 0:
                    progress = min((current_pos / total_audio_ms) + 0.05, 1.0)
                    player_ui.update_subtitle_sync(text, progress)

            time.sleep(0.03)
        
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Audio Playback Error: {e}")
        
    is_speaking = False
    
    if player_ui:
        player_ui.stop_speaking()
        if not fast_ack:
            player_ui.update_subtitle_sync(text, 1.0)
            player_ui.schedule_subtitle_clear()
    
    try:
        from actions.face_recognizer import identity_lock_queue
        if identity_lock_queue:
            try: identity_lock_queue.put_nowait("speaking_stop")
            except Exception: pass
    except Exception: pass

    if not fast_ack:
        if text.strip().endswith('?'):
            expecting_reply_until[0] = time.time() + 8.0
        else:
            expecting_reply_until[0] = 0.0
            
def _generate_tts(text):
    """Generate TTS audio via the configured cloud provider (Cartesia/Edge)."""
    provider = _get_provider()
    _, duration_ms = provider.generate_tts(text)
    return duration_ms

def preload_pipeline():
    """Initialize TTS provider connection (replaces Kokoro preload)."""
    try:
        _get_provider()
        print("✅ TTS provider initialized.")
    except Exception as e:
        print(f"⚠️ TTS provider init failed: {e}")

def stop_speaking():
    global is_speaking
    stop_event.set()
    expecting_reply_until[0] = 0.0