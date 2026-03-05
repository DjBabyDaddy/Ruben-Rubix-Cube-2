import os
import platform
import pyautogui
from tts import edge_speak

def execute_shortcut(parameters: dict, response: str, player, session_memory):
    if platform.system() != "Windows":
        print("⚠️ Shortcuts are currently optimized for Windows.")
        return

    base_key = parameters.get("key", "").lower().strip()
    modifiers_list = parameters.get("modifiers", [])
    
    if not base_key and not modifiers_list:
        return

    print(f"⌨️ RUBE Executing Shortcut: {modifiers_list} + {base_key}")

    # THE FIX: Translating Apple/General terms to Windows terms
    mod_map = {
        "command": "ctrl", "cmd": "ctrl", # Maps Mac CMD habits to PC CTRL
        "shift": "shift",
        "option": "alt", "alt": "alt",
        "control": "ctrl", "ctrl": "ctrl",
        "windows": "win", "win": "win"
    }

    win_mods = [mod_map.get(m.lower(), m.lower()) for m in modifiers_list]

    key_map = {
        "return": "enter", "escape": "esc", 
        "up arrow": "up", "down arrow": "down", 
        "left arrow": "left", "right arrow": "right"
    }
    
    final_key = key_map.get(base_key, base_key)

    try:
        if win_mods and final_key:
            pyautogui.hotkey(*win_mods, final_key)
        elif win_mods:
            for m in win_mods: pyautogui.press(m)
        elif final_key:
            pyautogui.press(final_key)
    except Exception as e:
        print(f"⚠️ Keyboard Matrix Error: {e}")