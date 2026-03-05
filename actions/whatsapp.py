import queue
import time
import threading
import urllib.parse
from playwright.sync_api import sync_playwright
from memory.memory_manager import load_memory
from tts import edge_speak

whatsapp_queue = queue.Queue()
whatsapp_initialized = threading.Event()
SESSION_DIR = "memory/whatsapp_session"

def initialize_whatsapp_matrix():
    """Starts the persistent background WhatsApp Web worker at boot."""
    print("📱 RUBE Spawning background WhatsApp automation matrix...")
    threading.Thread(target=_whatsapp_web_thread, daemon=True).start()

def _whatsapp_web_thread():
    """Maintains an active headless browser session for WhatsApp Web."""
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch_persistent_context(SESSION_DIR, headless=True)
            page = browser.new_page()
            
            page.goto("https://web.whatsapp.com/")
            print("📱 WhatsApp Web loaded. Awaiting session authentication (Scan QR if needed)...")
            
            try:
                page.wait_for_selector('canvas[aria-label="Scan me!"]', timeout=3000)
                print("⚠️ ACTION REQUIRED: Please scan the WhatsApp QR Code in the pop-up browser!")
            except Exception:
                pass 
                
            try:
                page.wait_for_selector('div#pane-side', timeout=60000)
                whatsapp_initialized.set()
                print("✅ WhatsApp Matrix Authenticated and Online.")
            except Exception:
                print("❌ WhatsApp Matrix Failed to Authenticate.")
                return

            while True:
                try:
                    msg_data = whatsapp_queue.get(timeout=1)
                except queue.Empty:
                    continue

                number = msg_data['number']
                text = msg_data['text']

                try:
                    encoded_text = urllib.parse.quote(text)
                    page.goto(f"https://web.whatsapp.com/send?phone={number}&text={encoded_text}")

                    send_btn = page.wait_for_selector('span[data-icon="send"]', timeout=15000)
                    send_btn.click()
                    print(f"✅ WhatsApp Broadcast sent to {number}.")
                    time.sleep(2)
                except Exception as e:
                    print(f"❌ Failed to send WhatsApp message: {e}")
                finally:
                    whatsapp_queue.task_done()
                
    except Exception as e:
        print(f"⚠️ Fatal error in WhatsApp background thread: {e}")

def send_whatsapp_message(parameters, response, player, session_memory):
    nickname = parameters.get("receiver_nickname", "").strip().lower()
    message_text = parameters.get("message_text", "").strip()

    time.sleep(1.2) 

    if not whatsapp_initialized.is_set():
        edge_speak("Boss, the WhatsApp matrix is still initializing or requires QR authentication.", player)
        return

    memory = load_memory()
    nickname_map = memory.get("preferences", {}).get("nicknames", {}).get("value", {})
    
    matched_number = None
    for n in nickname_map:
        if nickname in n.lower():
            matched_number = nickname_map[n]
            break
            
    if not matched_number:
        msg = f"Boss, I cannot locate a phone number for {nickname} in my local memory."
        print(f"\n👤 [CONTACT REQUIRED] To add this person, edit memory/memory.json and add: \"{nickname}\": \"1234567890\" under preferences -> nicknames.")
        edge_speak(msg, player)
        return

    whatsapp_queue.put({"number": matched_number, "text": message_text})
    edge_speak(f"The broadcast to {nickname} has been queued for background transmission, boss.", player)