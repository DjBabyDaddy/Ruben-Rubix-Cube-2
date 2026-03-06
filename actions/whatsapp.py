import time
import urllib.parse
import webbrowser
import pyautogui
from memory.memory_manager import load_memory
from tts import edge_speak

def initialize_whatsapp_matrix():
    """No-op: WhatsApp now routes via the installed Desktop app — no browser session needed."""
    print("📱 WhatsApp matrix ready — routing via WhatsApp Desktop URI scheme.")

def send_whatsapp_message(parameters, response, player, session_memory):
    nickname = parameters.get("receiver_nickname", "").strip().lower()
    message_text = parameters.get("message_text", "").strip()
    action = parameters.get("action", "send").strip().lower()  # "send" or "call"

    memory = load_memory()
    nickname_map = memory.get("preferences", {}).get("nicknames", {}).get("value", {})

    matched_number = None
    for n in nickname_map:
        if nickname in n.lower():
            matched_number = nickname_map[n]
            break

    if not matched_number:
        msg = f"Boss, I don't have a number stored for {nickname}. Add it to memory.json under preferences → nicknames."
        print(f"\n👤 [CONTACT REQUIRED] Edit memory/memory.json → preferences → nicknames → value → add: \"{nickname}\": \"1XXXXXXXXXX\"")
        edge_speak(msg, player)
        return

    if action == "call":
        url = f"whatsapp://call?phone={matched_number}"
        webbrowser.open(url)
        edge_speak(f"Initiating WhatsApp call to {nickname}, boss.", player)
    else:
        encoded_text = urllib.parse.quote(message_text)
        url = f"whatsapp://send?phone={matched_number}&text={encoded_text}"
        webbrowser.open(url)
        time.sleep(4.0)   # Give WhatsApp Desktop time to open the chat and populate the field
        pyautogui.press("enter")
        edge_speak(f"Message sent to {nickname} on WhatsApp, boss.", player)
