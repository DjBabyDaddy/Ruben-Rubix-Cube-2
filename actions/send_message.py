import os
import time
import pyautogui
from tts import edge_speak
import platform

REQUIRED_PARAMS = ["receiver", "message_text", "platform"]

def send_message(parameters: dict, response: str | None = None, player=None, session_memory=None) -> bool:
    if platform.system() != "Windows": return False

    if session_memory is None:
        msg = "Session memory missing, cannot proceed."
        if player: player.write_log(f"RUBE: {msg}")
        edge_speak(msg, player)
        return False

    if parameters: session_memory.update_parameters(parameters)

    for param in REQUIRED_PARAMS:
        value = session_memory.get_parameter(param)
        if not value:
            session_memory.set_current_question(param)
            if param == "receiver": question_text = "Boss, who should I send the message to?"
            elif param == "message_text": question_text = "Boss, what should I say?"
            elif param == "platform": question_text = "Boss, which platform should I use? (WhatsApp, Telegram, etc.)"
            else: question_text = f"Boss, please provide {param}."
            edge_speak(question_text, player)
            return False  

    receiver = session_memory.get_parameter("receiver").strip()
    platform_name = session_memory.get_parameter("platform").strip().title() or "WhatsApp"
    message_text = session_memory.get_parameter("message_text").strip()

    if response: edge_speak(response, player)

    try:
        pyautogui.PAUSE = 0.1
        print(f"💬 RUBE Initiating Windows Automation for {platform_name}")

        # THE FIX: Windows Native App Launch Sequence
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write(platform_name, interval=0.05)
        time.sleep(0.5)
        pyautogui.press("enter")

        time.sleep(3.0) 
        
        # THE FIX: Windows Ctrl key
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.5)
        pyautogui.write(receiver, interval=0.03)
        time.sleep(1.0) 
        pyautogui.press("enter")
        time.sleep(0.5)

        pyautogui.write(message_text, interval=0.03)
        pyautogui.press("enter")

        session_memory.reset()

        edge_speak(f"Boss, message dispatched to {receiver} via {platform_name}.", player)
        return True
    except Exception as e:
        edge_speak(f"Boss, I failed to send the message due to a matrix error.", player)
        return False