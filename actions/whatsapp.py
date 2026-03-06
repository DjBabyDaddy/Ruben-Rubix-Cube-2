import time
import os
import urllib.parse
import webbrowser
import pyautogui
import pygetwindow as gw
from memory.memory_manager import load_memory
from tts import edge_speak


def _wait_for_whatsapp(timeout=10):
    """Poll until WhatsApp Desktop window is visible. Returns True on success."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if gw.getWindowsWithTitle("WhatsApp"):
            time.sleep(0.4)   # let it finish rendering
            return True
        time.sleep(0.3)
    return False


def _attach_image_to_whatsapp(image_path):
    """Paste an image file into the active WhatsApp chat via clipboard."""
    try:
        from PIL import Image
        import io, win32clipboard, win32con
        img = Image.open(image_path).convert("RGB")
        output = io.BytesIO()
        img.save(output, "BMP")
        bmp_data = output.getvalue()[14:]   # strip BMP file header
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data)
        win32clipboard.CloseClipboard()
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.0)
        pyautogui.press('enter')
        return True
    except Exception as e:
        print(f"⚠️ WhatsApp image attach error: {e}")
        return False

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

    attachment_path = parameters.get("attachment_path", "").strip().replace('"', '')
    if attachment_path.lower() == "none":
        attachment_path = ""

    if action == "call":
        url = f"whatsapp://call?phone={matched_number}"
        webbrowser.open(url)
        edge_speak(f"Initiating WhatsApp call to {nickname}, boss.", player)
    else:
        encoded_text = urllib.parse.quote(message_text)
        url = f"whatsapp://send?phone={matched_number}&text={encoded_text}"
        webbrowser.open(url)

        if not _wait_for_whatsapp(timeout=10):
            edge_speak("Boss, WhatsApp took too long to open. Message not sent.", player)
            return

        pyautogui.press("enter")   # send the text message

        # Attach image if provided (PNG/JPG only — URI scheme cannot carry files)
        if attachment_path and os.path.exists(attachment_path):
            img_exts = ['jpg', 'jpeg', 'png', 'bmp', 'webp']
            ext = attachment_path.lower().split('.')[-1]
            if ext in img_exts:
                time.sleep(0.5)
                if _attach_image_to_whatsapp(attachment_path):
                    edge_speak(f"Message and image sent to {nickname} on WhatsApp, boss.", player)
                    return
            # Non-image files: note in console, text was still sent
            print(f"⚠️ WhatsApp cannot attach non-image files via URI. File: {attachment_path}")

        edge_speak(f"Message sent to {nickname} on WhatsApp, boss.", player)
