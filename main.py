import asyncio
import threading
import random
import datetime
import time
import os
import platform
import urllib.request
import json
from dotenv import load_dotenv

# THE FIX: Keeping the Email and Analytics Managers properly imported
from actions.analytics_manager import generate_analytics_report
from actions.email_manager import send_email_message

load_dotenv()

from speech_to_text import record_voice, stop_listening_flag
from llm import get_llm_output
import tts 
from tts import edge_speak, stop_speaking, stop_event

from ui import RubeUI

original_write_log = RubeUI.write_log
def safe_write_log(self, message):
    if "RUBE:" in message and tts.stop_event.is_set(): return 
    original_write_log(self, message)
RubeUI.write_log = safe_write_log

from actions.open_app import web_navigate, system_launch, system_close, play_media, system_control, play_soundcloud
from actions.broadcast_control import broadcast_control
import actions.web_search as web_search_module 
from actions.web_search import web_search
from actions.weather_report import weather_action
from actions.send_message import send_message  
from actions.system_status import system_diagnostics, hardware_control 
from actions.keyboard_matrix import execute_shortcut
from actions.vision import analyze_multimodal_view
from actions.face_recognizer import identity_scan_room, initialize_facial_matrix
from actions.whatsapp import send_whatsapp_message, initialize_whatsapp_matrix
from actions.social_manager import generate_social_post

from memory.memory_manager import load_memory, update_memory, get_startup_suggestions
from memory.feedback_logger import log_execution
from memory.temporary_memory import TemporaryMemory

interrupt_commands = ["stop", "cancel", "silence", "shut up", "shut down", "quiet", "abort"]
temp_memory = TemporaryMemory()

def fetch_geo_context_threaded():
    try:
        req = urllib.request.Request("https://ipapi.co/json/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            ctx = {"city": data.get("city"), "region": data.get("region"), "timezone": data.get("timezone")}
            temp_memory.parameters["location"] = ctx
            print(f"📍 Geo-Context Locked: {ctx['city']}, {ctx['region']}")
    except: pass

async def ai_loop(ui: RubeUI, input_queue: asyncio.Queue):
    tts.start_gatekeeper_thread(ui)
    
    temp_memory.parameters["location"] = {"city": "New Orleans", "region": "Louisiana", "timezone": "America/Chicago"}
    threading.Thread(target=fetch_geo_context_threaded, daemon=True).start()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        msg = "Boss, I require an Anthropic API key to connect to the Claude cognitive matrix. Please paste it into my terminal."
        edge_speak(msg, ui)
        while True:
            source, text = await input_queue.get()
            if source == "keyboard" and text.strip():
                ack = "Key received. Linking my brain to the Claude network."
                edge_speak(ack, ui)
                await asyncio.sleep(2.5) 
                os.environ["ANTHROPIC_API_KEY"] = text.strip()
                with open(".env", "a") as f: f.write(f"\nANTHROPIC_API_KEY={text.strip()}\n")
                break

    memory = load_memory()
    user_name = memory.get("identity", {}).get("name", {}).get("value", "boss")

    await asyncio.sleep(0.8) 
    hour = datetime.datetime.now().hour
    if hour < 12: greeting = f"Good morning, {user_name}. RUBE systems fully online."
    elif hour < 18: greeting = f"Good afternoon, {user_name}. RUBE systems fully online."
    else: greeting = f"Good evening, {user_name}. RUBE systems fully online."
    
    edge_speak(greeting, ui)

    suggestions = get_startup_suggestions()
    if suggestions:
        hint = f"Boss, I have {len(suggestions)} performance suggestion{'s' if len(suggestions) > 1 else ''} from my self-analysis. Say 'show suggestions' to hear them."
        ui.write_log(f"RUBE: {hint}")

    try:
        threading.Thread(target=initialize_facial_matrix, daemon=True).start()
    except Exception: pass

    while True:
        stop_listening_flag.clear()
        source, user_text = await input_queue.get()
        if not user_text: continue

        cleaned_text = user_text.lower().strip()

        if any(cmd in cleaned_text for cmd in interrupt_commands):
            stop_speaking()
            ui.write_log("🛑 [Action Terminated by User]") 
            temp_memory.reset()
            if getattr(web_search_module, "AWAITING_KEY_NAME", None):
                web_search_module.AWAITING_KEY_NAME = None
            continue

        triggers = ["ruben", "reuben", "rubin"]
        if source != "keyboard":
            for t in triggers:
                if cleaned_text.startswith(t):
                    user_text = cleaned_text.replace(t, "", 1).strip()
                    break

        tts.stop_event.clear()
        if not user_text:
            msg = "Yes?"
            edge_speak(msg, ui)
            continue

        ui.write_log(f"You: {user_text}")
        tts.expecting_reply_until[0] = 0 

        if temp_memory.get_current_question() == "api_service_name":
            service_name = user_text.strip()
            temp_memory.clear_current_question()
            key_name = service_name.upper().replace(" ", "_").replace("-", "_") + "_API_KEY"
            if key_name.endswith("_API_KEY_API_KEY"):
                key_name = key_name.replace("_API_KEY_API_KEY", "_API_KEY")
            msg = f"Preparing the vault for {service_name}. Please paste the key into my terminal."
            edge_speak(msg, ui)
            try: ui.trigger_hotkey()
            except: pass
            web_search_module.AWAITING_KEY_NAME = key_name
            continue

        if getattr(web_search_module, "AWAITING_KEY_NAME", None):
            missing_key = web_search_module.AWAITING_KEY_NAME
            if source == "keyboard" and user_text:
                os.environ[missing_key] = user_text.strip()
                with open(".env", "a") as f: f.write(f"\n{missing_key}={user_text.strip()}\n")
                msg = f"Key secured. {missing_key} is now active in the matrix."
                edge_speak(msg, ui)
                web_search_module.AWAITING_KEY_NAME = None
                
                last_text = temp_memory.get_last_user_text()
                if last_text and "api" not in last_text.lower():
                    user_text = last_text 
                else:
                    continue 
            else:
                msg = "Please paste the key into the terminal."
                edge_speak(msg, ui)
                continue

        temp_memory.set_last_user_text(user_text)
        geo_ctx = temp_memory.parameters.get("location", {})
        
        last_user = temp_memory.get_last_user_text() or ""
        last_ai = temp_memory.get_last_ai_response() or ""
        recent_convo = f"User: {last_user}\nRUBE: {last_ai}" if last_user else ""

        memory_for_prompt = {
            "user_name": user_name,
            "current_location": f"{geo_ctx.get('city', 'New Orleans')}, {geo_ctx.get('region', 'Louisiana')}",
            "current_time_context": datetime.datetime.now().strftime("%A, %B %d, %Y - %I:%M %p"),
            "recent_conversation": recent_convo
        }

        dispatch_start = time.time()
        try:
            ui.start_processing()
            llm_output = await asyncio.to_thread(get_llm_output, user_text=user_text, memory_block=memory_for_prompt)
            ui.stop_processing()
        except Exception:
            ui.stop_processing()
            continue

        intent = llm_output.get("intent", "chat")
        params = llm_output.get("parameters", {})
        response = llm_output.get("text")
        
        if llm_output.get("memory_update"): update_memory(llm_output.get("memory_update"))
        temp_memory.set_last_ai_response(response)

        args = {"parameters": params, "response": response, "player": ui, "session_memory": temp_memory}
        serpapi_key = os.getenv("SERPAPI_API_KEY", "")

        if intent == "register_api_key": 
            service = params.get("service_name")
            if not service:
                msg = "I am ready to vault it, boss. What service is this key for?"
                edge_speak(msg, ui)
                temp_memory.set_current_question("api_service_name")
            else:
                key_name = service.upper().replace(" ", "_").replace("-", "_") + "_API_KEY"
                if key_name.endswith("_API_KEY_API_KEY"):
                    key_name = key_name.replace("_API_KEY_API_KEY", "_API_KEY")
                msg = f"Preparing the vault for {service}. Please paste the key into my terminal."
                edge_speak(msg, ui)
                try: ui.trigger_hotkey()
                except: pass
                web_search_module.AWAITING_KEY_NAME = key_name
        elif intent == "vision_analysis": threading.Thread(target=analyze_multimodal_view, kwargs=args, daemon=True).start()
        elif intent == "facial_recognition": threading.Thread(target=identity_scan_room, kwargs=args, daemon=True).start()
        elif intent == "whatsapp_message": threading.Thread(target=send_whatsapp_message, kwargs=args, daemon=True).start()
        elif intent == "system_control": threading.Thread(target=system_control, kwargs=args, daemon=True).start()
        elif intent == "broadcast_control": threading.Thread(target=broadcast_control, kwargs=args, daemon=True).start()
        elif intent == "web_navigate": threading.Thread(target=web_navigate, kwargs=args, daemon=True).start()
        elif intent == "play_soundcloud": threading.Thread(target=play_soundcloud, kwargs=args, daemon=True).start()
        elif intent == "system_launch": threading.Thread(target=system_launch, kwargs=args, daemon=True).start()
        elif intent == "system_close": threading.Thread(target=system_close, kwargs=args, daemon=True).start()
        elif intent == "play_media": threading.Thread(target=play_media, kwargs=args, daemon=True).start()
        elif intent == "system_diagnostics": threading.Thread(target=system_diagnostics, kwargs=args, daemon=True).start() 
        elif intent == "hardware_control": threading.Thread(target=hardware_control, kwargs=args, daemon=True).start()
        elif intent == "execute_shortcut": threading.Thread(target=execute_shortcut, kwargs=args, daemon=True).start()
        elif intent == "search": threading.Thread(target=web_search, kwargs={**args, "api_key": serpapi_key, "geo_context": geo_ctx}, daemon=True).start()
        elif intent == "generate_social_post": threading.Thread(target=generate_social_post, kwargs=args, daemon=True).start()
        elif intent == "generate_analytics_report": threading.Thread(target=generate_analytics_report, kwargs=args, daemon=True).start()
        elif intent == "email_message": threading.Thread(target=send_email_message, kwargs=args, daemon=True).start()
        elif intent == "send_message": threading.Thread(target=send_message, kwargs=args, daemon=True).start()
        elif intent == "show_suggestions":
            suggestions = get_startup_suggestions()
            if suggestions:
                for i, s in enumerate(suggestions, 1):
                    ui.write_log(f"RUBE Suggestion {i}: {s}")
                edge_speak(f"I have {len(suggestions)} suggestions ready. Check the log panel for the full list, boss.", ui)
            else:
                edge_speak("No suggestions on file yet. The n8n analysis workflow needs to run first.", ui)
            continue

        threading.Thread(
            target=log_execution,
            args=(intent, params, response, True, (time.time() - dispatch_start) * 1000),
            daemon=True
        ).start()

        if response and intent != "register_api_key":
             edge_speak(response, ui)

        await asyncio.sleep(0.01)

def main():
    ui = RubeUI(size=(380, 450)) 
    try:
        from actions import face_recognizer
        face_recognizer.identity_lock_queue = asyncio.Queue() 
    except Exception: pass

    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        input_queue = asyncio.Queue()
        def on_text_submitted(text):
            stop_speaking()
            stop_listening_flag.set() 
            loop.call_soon_threadsafe(input_queue.put_nowait, ("keyboard", text))
        ui.on_text_submit = on_text_submitted
        async def voice_worker():
            while True:
                if stop_listening_flag.is_set():
                    await asyncio.sleep(0.2); continue
                text = await asyncio.to_thread(record_voice)
                if text: await input_queue.put(("voice", text))
        loop.create_task(voice_worker())
        loop.run_until_complete(ai_loop(ui, input_queue))
    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()

if __name__ == "__main__":
    main()