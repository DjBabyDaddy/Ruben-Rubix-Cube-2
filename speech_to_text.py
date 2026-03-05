import os
import json
import queue
import sys
import threading
import time
import sounddevice as sd
from vosk import Model as VoskModel, KaldiRecognizer

MODEL_PATH = "model" 
SAMPLE_RATE = 16000  

# THE FIX: Restoring the global flag that was missing in your uploaded file!
is_awake = False  

if not os.path.exists(MODEL_PATH):
    print("❌ ERROR: Vosk model not found! Ensure the 1.8GB folder is renamed to 'model'.")
    sys.exit(1)

print("🧠 RUBE is loading his local vocabulary matrix (Vosk)...")
vosk_model = VoskModel(MODEL_PATH)
rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)

audio_queue = queue.Queue()
stop_listening_flag = threading.Event()
jarvis_last_speech = ""

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

def audio_callback(indata, frames, time_info, status):
    if status: pass 
    audio_queue.put(bytes(indata))

try:
    device_info = sd.query_devices(kind='input')
    print(f"\n🎤 Hardware matrix locked onto: {device_info['name']}")
    global_stream = sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=1280, device=None, dtype='int16', channels=1, callback=audio_callback)
    global_stream.start()
except Exception as e:
    print("\n❌ CRITICAL HARDWARE ALERT: Windows is hiding your microphone.")
    global_stream = None

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
        "can", "could", "would", "do", "is", "are", "set", "turn", "make", "post"
    }
    
    if any(w in strong_triggers for w in words):
        return True
        
    return False

def record_voice():
    global is_awake
    if not global_stream:
        time.sleep(1)
        return ""

    try:
        import tts 
    except ImportError:
        tts = None

    rec.Reset()
    while not audio_queue.empty():
        try: audio_queue.get_nowait()
        except queue.Empty: break
    
    INTERRUPTS = {"stop", "cancel", "quiet", "shut up", "abort", "silence"}
    WAKE_WORDS = ["ruben", "reuben", "rubin"]
    
    awake_until = 0.0
    
    cumulative_text = ""
    current_partial = ""
    last_spoken_time = time.time()
    
    while not stop_listening_flag.is_set():
        try:
            data = audio_queue.get(timeout=0.1)
            has_data = True
        except queue.Empty:
            has_data = False

        if stop_listening_flag.is_set(): break

        if tts and getattr(tts, 'is_speaking', False):
            rec.Reset()
            cumulative_text = ""
            current_partial = ""
            continue

        is_expecting_reply = (tts and time.time() < tts.expecting_reply_until[0])

        if has_data:
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                final_chunk = res.get("text", "").strip()
                if final_chunk:
                    cumulative_text += " " + final_chunk
                    cumulative_text = cumulative_text.strip()
                    last_spoken_time = time.time()
                current_partial = ""
            else:
                res = json.loads(rec.PartialResult())
                partial_chunk = res.get("partial", "").strip()
                if partial_chunk and partial_chunk != current_partial:
                    current_partial = partial_chunk
                    last_spoken_time = time.time()

            full_heard = (cumulative_text + " " + current_partial).strip()

            if full_heard:
                explicit_wake_heard = any(w in full_heard for w in WAKE_WORDS)
                
                if not is_awake and explicit_wake_heard:
                    sys.stdout.write("\r\033[K")
                    print("🔔 [Wake Word Detected] RUBE is online.")
                    is_awake = True
                    awake_until = time.time() + 8.0

                if is_awake or is_expecting_reply:
                    display = full_heard if len(full_heard) < 50 else "..." + full_heard[-45:]
                    sys.stdout.write(f"\r💬 Hearing: {display}".ljust(80))
                    sys.stdout.flush()
                    awake_until = time.time() + 8.0

        full_heard = (cumulative_text + " " + current_partial).strip()
        
        if not is_awake and not is_expecting_reply and full_heard and (time.time() - last_spoken_time > 2.0):
             cumulative_text = ""
             current_partial = ""
             rec.Reset()
             continue
        
        if (is_awake or is_expecting_reply) and full_heard and (time.time() - last_spoken_time > 1.5):
            filtered = apply_echo_scalpel(full_heard)
            
            if any(cmd in filtered.split() for cmd in INTERRUPTS): 
                is_awake = False
                return filtered
            
            explicit_wake_heard = any(w in filtered for w in WAKE_WORDS)
            if has_command_substance(filtered, is_expecting_reply, explicit_wake_heard):
                sys.stdout.write("\r\033[K")
                print(f"\n🧠 RUBE Command Locked: {filtered}")
                is_awake = False
                return filtered
            else:
                cumulative_text = ""
                current_partial = ""
                rec.Reset()
                awake_until = time.time() + 8.0

        if is_awake and time.time() > awake_until:
            print("\n💤 Command window closed. Going back to sleep.")
            is_awake = False
            cumulative_text = ""
            current_partial = ""
            rec.Reset()
            sys.stdout.write("\r\033[K🎙️ I'm listening... (Say 'Ruben' to wake me)\n")

    return ""