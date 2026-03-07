import os
import subprocess
import time
import pyautogui
import webbrowser
import urllib.parse
import pygetwindow as gw
from actions.contact_manager import lookup_contact
from memory.memory_manager import load_memory
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


def _verify_gmail_sent(timeout=8):
    """Check if Gmail compose window closed after send attempt (indicates success)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        titles = [w.title.lower() for w in gw.getAllWindows() if w.title]
        # If no compose/new message window remains, send likely succeeded
        if not any("compose" in t or "new message" in t or "nouveau" in t for t in titles):
            return True
        time.sleep(0.5)
    return False


def send_email_message(parameters, response, player, session_memory):
    target = parameters.get("receiver_email", "").strip()
    subject = parameters.get("subject", "Message from RUBE").strip()
    body = parameters.get("message_text", "").strip()
    attachment = parameters.get("attachment_path", "").strip()

    # Resolve contact name to email address if not already an email
    if target and "@" not in target:
        # Check new contacts system first
        contact = lookup_contact(target)
        if contact and contact.get("email"):
            print(f"Resolved contact '{target}' -> {contact['email']}")
            target = contact["email"]
        else:
            # Fall back to preferences.emails.value (LLM memory_update path)
            memory = load_memory()
            email_map = memory.get("preferences", {}).get("emails", {}).get("value", {})
            matched_email = None
            search = target.lower()
            for name, email in email_map.items():
                if search in name.lower():
                    matched_email = email
                    break

            if matched_email:
                print(f"Resolved contact '{target}' via emails memory -> {matched_email}")
                target = matched_email
            else:
                edge_speak(f"Boss, I don't have an email address for {target}. Please provide the full email.", player)
                return

    print(f"RUBE Email Matrix: Routing to {target}")

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
            edge_speak("Boss, Gmail didn't open in time. The email may not have been composed.", player)
            return

        # PowerShell Attachment Injection
        if attachment and os.path.exists(attachment):
            print(f"Injecting file into clipboard: {attachment}")
            subprocess.run(["powershell", "-Command", f"Set-Clipboard -LiteralPath '{attachment.replace(chr(39), chr(39)*2)}'"], check=False)
            time.sleep(1.0)

            # Click the body and paste the file
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2.0)  # Wait for upload bar

        # Auto-Send
        pyautogui.hotkey('ctrl', 'enter')

        # Verify send by checking if compose window closed
        if _verify_gmail_sent(timeout=8):
            if attachment:
                edge_speak(f"Email with attachment dispatched to {target}, boss.", player)
            else:
                edge_speak(f"Email dispatched to {target}, boss.", player)
        else:
            edge_speak(f"Boss, I attempted to send the email to {target} but the compose window is still open. Please verify manually.", player)

    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        edge_speak("I attempted to send the email but encountered an error in the matrix.", player)
