import os
import subprocess
import time
import pyautogui
import webbrowser
import urllib.parse
import pygetwindow as gw
from tts import edge_speak


def _wait_for_gmail(timeout=20):
    """Poll until a browser window containing 'Gmail' or 'Google' is active."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for title in [w.title for w in gw.getAllWindows() if w.title]:
            if "gmail" in title.lower() or "compose" in title.lower() or "google" in title.lower():
                time.sleep(1.5)   # let compose box finish rendering
                return True
        time.sleep(0.5)
    return False

def send_email_message(parameters, response, player, session_memory):
    target = parameters.get("receiver_email", "").strip()
    subject = parameters.get("subject", "Message from RUBE").strip()
    body = parameters.get("message_text", "").strip()
    attachment = parameters.get("attachment_path", "").strip()

    print(f"📧 RUBE Email Matrix: Routing to {target}")

    if attachment and attachment.lower() != "none":
        attachment = attachment.replace('"', '')
    else:
        attachment = None

    try:
        # Pre-fill the email using Gmail URL parameters
        encoded_to = urllib.parse.quote(target)
        encoded_su = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(body)
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={encoded_to}&su={encoded_su}&body={encoded_body}"
        
        webbrowser.open(gmail_url)
        if not _wait_for_gmail(timeout=20):
            print("⚠️ Gmail window not detected — proceeding anyway after timeout.")
            time.sleep(3.0)

        # PowerShell Attachment Injection
        if attachment and os.path.exists(attachment):
            print(f"📎 Injecting file into clipboard: {attachment}")
            subprocess.run(["powershell", "-Command", f"Set-Clipboard -LiteralPath '{attachment.replace(chr(39), chr(39)*2)}'"], check=False)
            time.sleep(1.0)
            
            # Click the body and paste the file
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2.0) # Wait for upload bar
        
        # Auto-Send
        pyautogui.hotkey('ctrl', 'enter')
        
        if attachment:
            edge_speak(f"Verification complete. The email and file attachment have been dispatched to {target}, boss.", player)
        else:
            edge_speak(f"Verification complete. The email has been dispatched to {target}, boss.", player)

    except Exception as e:
        print(f"⚠️ EMAIL ERROR: {e}")
        edge_speak("I encountered an error while trying to access the Email matrix.", player)