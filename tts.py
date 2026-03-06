import os
import pygame
import threading
import time
import queue
from memory.temporary_memory import TemporaryMemory
import speech_to_text 

OUTPUT_FILE = "output.wav"

_kokoro_pipeline = None

def _get_pipeline():
    global _kokoro_pipeline
    if _kokoro_pipeline is None:
        from kokoro import KPipeline
        _kokoro_pipeline = KPipeline(lang_code='a')  # American English
    return _kokoro_pipeline

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
        time.sleep(0.1)

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
        _generate_tts(text)
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
        audio_data = pygame.mixer.Sound(OUTPUT_FILE)
        total_audio_ms = audio_data.get_length() * 1000
    except Exception:
        total_audio_ms = max(len(text) * 75, 1000)

    try:
        if player_ui: 
            player_ui.start_speaking()

        try:
            silence = bytearray(int(44100 * 0.20 * 4)) 
            pygame.mixer.Sound(buffer=silence).play()
            time.sleep(0.20)
        except Exception: pass

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
    import numpy as np
    import soundfile as sf

    pipeline = _get_pipeline()
    chunks = []
    for _, _, audio in pipeline(text, voice='af_heart', speed=1.0):
        chunks.append(audio)
    audio_np = np.concatenate(chunks) if chunks else np.zeros(24000, dtype=np.float32)
    sf.write(OUTPUT_FILE, audio_np, 24000)

def stop_speaking():
    global is_speaking
    stop_event.set()
    expecting_reply_until[0] = 0.0