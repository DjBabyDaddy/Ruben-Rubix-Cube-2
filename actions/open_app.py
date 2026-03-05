import os
import webbrowser
import time
import pyautogui
import urllib.parse
import platform
import subprocess
import psutil
from tts import edge_speak

def force_focus_media():
    pyautogui.press('playpause')
    return True

def web_navigate(parameters: dict, response: str, player, session_memory):
    query = parameters.get("url", "").strip()
    if not query: return
    
    if "music" in query.lower() and len(query.split()) > 2:
        search_term = query.lower().replace("apple music", "").replace("spotify", "").replace("play", "").replace("on", "").replace("some", "").strip()
        encoded = urllib.parse.quote(search_term)
        url = f"https://open.spotify.com/search/{encoded}"
        print(f"🎵 RUBE Searching Spotify for: {search_term}")
        webbrowser.open(url)
        return

    if query.lower().strip() in ["apple music", "spotify", "music"]:
        force_focus_media()
        return

    if query.startswith("http"): url = query
    elif "." in query and " " not in query: url = "https://" + query
    else:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
    print(f"🌐 RUBE Navigating to: {url}")
    webbrowser.open(url)

def play_soundcloud(parameters: dict, response: str, player, session_memory):
    category = parameters.get("category", "likes").lower()
    query = parameters.get("query", "")
    print(f"☁️ RUBE Accessing SoundCloud: {category}")
    if category == "likes": url = "https://soundcloud.com/you/likes"
    elif category == "sets" or category == "playlists": url = "https://soundcloud.com/you/sets"
    elif category == "search" and query:
        encoded_query = urllib.parse.quote(query)
        url = f"https://soundcloud.com/search/sets?q={encoded_query}"
    else: url = "https://soundcloud.com/discover"
    webbrowser.open(url)
    time.sleep(4.5) 
    pyautogui.press('space')

def system_launch(parameters: dict, response: str, player, session_memory):
    program = parameters.get("program_name", "").lower()
    print(f"🚀 RUBE Launching '{program}' on Windows Matrix...")
    if platform.system() != "Windows": return

    try:
        app_map = {
            "chrome": "chrome", "browser": "chrome",
            "obs": "obs64", "obs studio": "obs64",
            "streamlabs": "streamlabs", "stream labs": "streamlabs",
            "discord": "discord", "spotify": "spotify", "music": "spotify"
        }
        
        target_app = app_map.get(program, program)
        target_exe = f"{target_app}.exe" if not target_app.endswith(".exe") else target_app
        
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write(target_app, interval=0.05)
        time.sleep(0.5)
        pyautogui.press('enter')

        print(f"🔄 Verifying launch of {target_exe}...")
        time.sleep(3.5) 
        running = False
        
        for _ in range(3):
            processes = [p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info['name']]
            if any(target_exe.replace(".exe", "") in p for p in processes):
                running = True
                break
            time.sleep(1.5)
            
        if running:
            edge_speak(f"Verification complete. {program.title()} is now online, boss.", player)
        else:
            edge_speak(f"Boss, I attempted to launch {program}, but the process failed to verify.", player)

    except Exception as e: print(f"⚠️ Launch Error: {e}")

def system_close(parameters: dict, response: str, player, session_memory):
    program = parameters.get("program_name", "").lower()
    print(f"🛑 RUBE Closing '{program}' on Windows Matrix...")
    if platform.system() != "Windows": return

    try:
        app_map = {
            "chrome": "chrome.exe", "browser": "chrome.exe",
            "obs": "obs64.exe", "obs studio": "obs64.exe",
            "streamlabs": "Streamlabs Desktop.exe", "stream labs": "Streamlabs Desktop.exe",
            "spotify": "Spotify.exe", "music": "Spotify.exe",
            "discord": "Discord.exe"
        }
        
        target_exe = app_map.get(program, f"{program}.exe")
        result = subprocess.run(["taskkill", "/F", "/IM", target_exe, "/T"], capture_output=True)
        status = result.returncode
        
        time.sleep(1.5)
        processes = [p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info['name']]
        
        if any(target_exe.lower() in p for p in processes):
            edge_speak(f"Boss, {program} is resisting termination. Manual override may be required.", player)
        else:
            if status == 0:
                edge_speak(f"Confirmed. {program.title()} has been terminated.", player)
            else:
                edge_speak(f"I could not find a running application named {program}.", player)

    except Exception as e: print(f"⚠️ Close Error: {e}")

def play_media(parameters: dict, response: str, player, session_memory):
    print("🎵 RUBE Toggling Media Playback")
    force_focus_media()

def system_control(parameters: dict, response: str, player, session_memory):
    command = parameters.get("command", "").lower()
    print(f"⚙️ RUBE Executing System Command: {command}")
    if platform.system() != "Windows": return
    
    if command in ["minimize_all", "show_desktop"]: pyautogui.hotkey('win', 'd')
    elif command in ["close_window", "close"]: pyautogui.hotkey('alt', 'f4')
    elif command in ["volume_up", "vol_up", "louder"]: pyautogui.press('volumeup', presses=5) 
    elif command in ["volume_down", "vol_down", "quieter"]: pyautogui.press('volumedown', presses=5)
    elif command in ["mute_system", "mute", "silence"]: pyautogui.press('volumemute')
    elif command in ["unmute_system", "unmute"]: pyautogui.press('volumemute')
    elif command in ["play_pause", "play", "pause", "toggle_media"]: force_focus_media()
    elif command in ["next_track", "skip_track", "skip", "next"]: pyautogui.press('nexttrack')
    elif command in ["previous_track", "prev_track", "back", "previous"]: pyautogui.press('prevtrack')
    elif command in ["new_tab", "open_tab"]: pyautogui.hotkey('ctrl', 't')
    elif command in ["close_tab"]: pyautogui.hotkey('ctrl', 'w')
    elif command in ["next_tab", "switch_tab"]: pyautogui.hotkey('ctrl', 'tab')
    elif command in ["refresh_page", "refresh", "reload"]: pyautogui.hotkey('ctrl', 'r')
    
    elif command in ["take_screenshot", "screenshot"]:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = os.path.join(desktop, f"RUBE_Screenshot_{int(time.time())}.png")
        pyautogui.screenshot(filename)
        edge_speak("Screenshot captured and saved to your desktop, boss.", player)
        
    elif command in ["start_screen_record", "record_screen"]:
        pyautogui.hotkey('win', 'alt', 'r')
        edge_speak("Windows screen recording initiated. Just tell me to stop recording when you're finished.", player)
        
    elif command in ["stop_screen_record", "stop_recording"]:
        pyautogui.hotkey('win', 'alt', 'r')
        edge_speak("Screen recording stopped. Windows has saved it to your Captures folder.", player)
        
    elif command == "power_off_pc": os.system("shutdown /s /t 5")
    elif command == "restart_pc": os.system("shutdown /r /t 5")
    elif command == "close_rube":
        print("🛑 Initiating RUBE shutdown sequence...")
        time.sleep(3.5)
        os._exit(0)
    else: print(f"⚠️ Unknown system command from AI: {command}")