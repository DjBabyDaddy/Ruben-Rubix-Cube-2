import asyncio
import threading
import random
import datetime
import time
import os
import platform
import urllib.request
import json
import requests
from dotenv import load_dotenv

# THE FIX: Keeping the Email and Analytics Managers properly imported
from actions.analytics_manager import generate_analytics_report
from actions.email_manager import send_email_message

load_dotenv()

from speech_to_text import record_voice, stop_listening_flag, initialize_vosk, vosk_ready
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
from actions.contact_manager import import_contacts, save_contact

from memory.memory_manager import load_memory, update_memory, get_startup_suggestions
from memory.feedback_logger import log_action_result, generate_self_assessment
from memory.temporary_memory import TemporaryMemory
from core.preflight import run_preflight

interrupt_commands = ["stop", "cancel", "silence", "shut up", "shut down", "quiet", "abort"]
temp_memory = TemporaryMemory()


def _run_and_log(action_fn, intent_name, args):
    """Wrap an action function to capture real execution time and success/failure."""
    start = time.time()
    success, error = True, ""
    try:
        action_fn(**args)
    except Exception as e:
        success, error = False, str(e)
        print(f"ACTION ERROR [{intent_name}]: {e}")
    finally:
        elapsed_ms = (time.time() - start) * 1000
        log_action_result(intent_name, args.get("parameters", {}), success, elapsed_ms, error)

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

    # Start boot animation while heavy systems load in background
    ui.start_booting()

    # Kick off all heavy initialization concurrently
    threading.Thread(target=initialize_vosk, daemon=True).start()
    threading.Thread(target=tts.preload_pipeline, daemon=True).start()

    temp_memory.parameters["location"] = {"city": "New Orleans", "region": "Louisiana", "timezone": "America/Chicago"}
    threading.Thread(target=fetch_geo_context_threaded, daemon=True).start()

    def check_n8n_health():
        webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if not webhook_url: return
        try:
            requests.head(webhook_url, timeout=5)
            print("n8n pipeline is reachable.")
        except Exception:
            print("n8n pipeline is OFFLINE — social posts will fail.")
    threading.Thread(target=check_n8n_health, daemon=True).start()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        ui.stop_booting()
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

    # Wait for Vosk to finish loading before greeting
    await asyncio.to_thread(vosk_ready.wait)

    ui.stop_booting()

    memory = load_memory()
    user_name = memory.get("identity", {}).get("name", {}).get("value", "boss")

    # Self-assessment: analyze past execution data for actionable insights
    local_insights = generate_self_assessment()
    for insight in local_insights:
        print(f"🔍 RUBE Self-Assessment: {insight}")

    hour = datetime.datetime.now().hour
    if hour < 12: greeting = f"Good morning, {user_name}. RUBE systems fully online."
    elif hour < 18: greeting = f"Good afternoon, {user_name}. RUBE systems fully online."
    else: greeting = f"Good evening, {user_name}. RUBE systems fully online."

    edge_speak(greeting, ui)

    suggestions = get_startup_suggestions() + local_insights
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
            llm_output = await asyncio.wait_for(
                asyncio.to_thread(get_llm_output, user_text=user_text, memory_block=memory_for_prompt),
                timeout=30.0
            )
            ui.stop_processing()
        except asyncio.TimeoutError:
            ui.stop_processing()
            edge_speak("My cognitive matrix timed out. Try again, boss.", ui)
            continue
        except Exception:
            ui.stop_processing()
            continue

        intent = llm_output.get("intent", "chat")
        params = llm_output.get("parameters", {})
        response = llm_output.get("text")
        confidence = llm_output.get("confidence", 1.0)

        # Confidence gate: if the LLM is unsure, ask for clarification
        if confidence < 0.5 and intent != "chat":
            response = response or f"Boss, I'm not confident I understood that. Did you mean {intent.replace('_', ' ')}?"
            intent = "chat"

        if llm_output.get("memory_update"):
            mem_update = llm_output.get("memory_update")
            # Extract pending compound actions before persisting to memory
            pending = mem_update.pop("pending_actions", []) if isinstance(mem_update, dict) else []
            update_memory(mem_update)
            for pa in pending:
                if isinstance(pa, dict) and "intent" in pa:
                    temp_memory.push_pending_action(pa)

        temp_memory.set_last_ai_response(response)

        # Pre-flight validation: catch doomed-to-fail actions before wasting time
        preflight_ok, preflight_reason = run_preflight(intent, params)
        if not preflight_ok:
            edge_speak(preflight_reason, ui)
            log_action_result(intent, params, False, 0, "preflight_failed")
            continue

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
        elif intent == "vision_analysis": threading.Thread(target=_run_and_log, args=(analyze_multimodal_view, "vision_analysis", args), daemon=True).start()
        elif intent == "facial_recognition": threading.Thread(target=_run_and_log, args=(identity_scan_room, "facial_recognition", args), daemon=True).start()
        elif intent == "whatsapp_message": threading.Thread(target=_run_and_log, args=(send_whatsapp_message, "whatsapp_message", args), daemon=True).start()
        elif intent == "system_control": threading.Thread(target=_run_and_log, args=(system_control, "system_control", args), daemon=True).start()
        elif intent == "broadcast_control": threading.Thread(target=_run_and_log, args=(broadcast_control, "broadcast_control", args), daemon=True).start()
        elif intent == "web_navigate": threading.Thread(target=_run_and_log, args=(web_navigate, "web_navigate", args), daemon=True).start()
        elif intent == "play_soundcloud": threading.Thread(target=_run_and_log, args=(play_soundcloud, "play_soundcloud", args), daemon=True).start()
        elif intent == "system_launch": threading.Thread(target=_run_and_log, args=(system_launch, "system_launch", args), daemon=True).start()
        elif intent == "system_close": threading.Thread(target=_run_and_log, args=(system_close, "system_close", args), daemon=True).start()
        elif intent == "play_media": threading.Thread(target=_run_and_log, args=(play_media, "play_media", args), daemon=True).start()
        elif intent == "system_diagnostics": threading.Thread(target=_run_and_log, args=(system_diagnostics, "system_diagnostics", args), daemon=True).start()
        elif intent == "hardware_control": threading.Thread(target=_run_and_log, args=(hardware_control, "hardware_control", args), daemon=True).start()
        elif intent == "execute_shortcut": threading.Thread(target=_run_and_log, args=(execute_shortcut, "execute_shortcut", args), daemon=True).start()
        elif intent == "search":
            search_args = {**args, "api_key": serpapi_key, "geo_context": geo_ctx}
            threading.Thread(target=_run_and_log, args=(web_search, "search", search_args), daemon=True).start()
        elif intent == "generate_social_post": threading.Thread(target=_run_and_log, args=(generate_social_post, "generate_social_post", args), daemon=True).start()
        elif intent == "generate_analytics_report": threading.Thread(target=_run_and_log, args=(generate_analytics_report, "generate_analytics_report", args), daemon=True).start()
        elif intent == "email_message": threading.Thread(target=_run_and_log, args=(send_email_message, "email_message", args), daemon=True).start()
        elif intent == "send_message": threading.Thread(target=_run_and_log, args=(send_message, "send_message", args), daemon=True).start()
        elif intent == "save_contact": threading.Thread(target=_run_and_log, args=(save_contact, "save_contact", args), daemon=True).start()
        elif intent == "import_contacts": threading.Thread(target=_run_and_log, args=(import_contacts, "import_contacts", args), daemon=True).start()
        elif intent == "show_suggestions":
            suggestions = get_startup_suggestions()
            if suggestions:
                for i, s in enumerate(suggestions, 1):
                    ui.write_log(f"RUBE Suggestion {i}: {s}")
                edge_speak(f"I have {len(suggestions)} suggestions ready. Check the log panel for the full list, boss.", ui)
            else:
                edge_speak("No suggestions on file yet. The n8n analysis workflow needs to run first.", ui)
            continue

        if response and intent != "register_api_key":
             edge_speak(response, ui)

        # Compound command dispatch: process deferred actions sequentially
        if temp_memory.has_pending_actions():
            next_action = temp_memory.pop_pending_action()
            if next_action and isinstance(next_action, dict):
                deferred_intent = next_action.get("intent", "")
                deferred_params = next_action.get("parameters", {})
                deferred_args = {"parameters": deferred_params, "response": None, "player": ui, "session_memory": temp_memory}
                def _dispatch_deferred(d_intent, d_args):
                    time.sleep(3.0)  # let primary action settle
                    DEFERRED_HANDLERS = {
                        "whatsapp_message": send_whatsapp_message, "email_message": send_email_message,
                        "system_launch": system_launch, "system_close": system_close,
                        "web_navigate": web_navigate, "broadcast_control": broadcast_control,
                        "execute_shortcut": execute_shortcut, "search": web_search,
                        "system_control": system_control, "send_message": send_message,
                    }
                    handler = DEFERRED_HANDLERS.get(d_intent)
                    if handler:
                        _run_and_log(handler, d_intent, d_args)
                threading.Thread(target=_dispatch_deferred, args=(deferred_intent, deferred_args), daemon=True).start()

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