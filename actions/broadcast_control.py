import os
import time
import platform
import logging
import difflib
from tts import edge_speak

try:
    import psutil
except ImportError:
    psutil = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import obsws_python as obs
    OBS_AVAILABLE = True
    logging.getLogger("obsws_python").setLevel(logging.CRITICAL)
except ImportError:
    OBS_AVAILABLE = False
    obs = None

STREAMLABS_HOTKEYS = {
    "live": "1", "brb": "2", "be right back": "2", "right back": "2",
    "lab": "3", "starting": "4", "chatting": "5", "dj": "6", "neon toxic": "7"
}

STREAMLABS_ACTIONS = {
    "toggle_stream": "s", "toggle_recording": "r", "toggle_mic": "m", "clip_that": "c"
}

def get_running_broadcasters():
    running = []
    if psutil is None:
        return running
    try:
        processes = [p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info['name']]
        if any("streamlabs" in p for p in processes): running.append("streamlabs")
        if any("obs64" in p for p in processes) or any("obs32" in p for p in processes): running.append("obs")
    except Exception as e:
        print(f"⚠️ Process check error: {e}")
    return running

def get_obs_client():
    if not OBS_AVAILABLE:
        return None
    hosts_to_try = ['127.0.0.1', 'localhost']
    for host in hosts_to_try:
        try:
            client = obs.ReqClient(host=host, port=4455, password='', timeout=2)
            return client
        except Exception:
            continue
    print("\n⚠️ OBS CONNECTION REFUSED: Authentication Blockade Detected.")
    return None

def execute_win_streamlabs(action, target):
    print(f"🖥️ RUBE Routing command to Streamlabs Desktop via Windows Hotkey Matrix...")
    base_key = None
    if action == "switch_scene" or action == "switch_collection":
        matched_key = next((key for key in STREAMLABS_HOTKEYS if key in target), None)
        if matched_key: base_key = STREAMLABS_HOTKEYS[matched_key]
        else: return
    elif action in STREAMLABS_ACTIONS:
        base_key = STREAMLABS_ACTIONS[action]
    else: return

    if base_key:
        pyautogui.hotkey('ctrl', 'alt', 'shift', base_key)
        print(f"✅ Executed Streamlabs Action: {action} {target}")

def execute_obs_api(client, action, target, state):
    print(f"📡 RUBE Injecting API command to OBS: {action} {target}")
    try:
        if action == "switch_scene":
            scenes_resp = client.get_scene_list()
            scene_names = [s['sceneName'] for s in scenes_resp.scenes]
            
            search_target = target.lower()
            if search_target in ["be right back", "right back"]: search_target = "brb"
            elif search_target == "starting": search_target = "starting soon"
            elif search_target == "chatting": search_target = "just chatting"
            
            matches = difflib.get_close_matches(search_target, [s.lower() for s in scene_names], n=1, cutoff=0.4)
            if matches:
                matched_scene = next(s for s in scene_names if s.lower() == matches[0])
                client.set_current_program_scene(matched_scene)
                print(f"✅ OBS Scene Swapped: {matched_scene}")
            else:
                partial = next((s for s in scene_names if search_target in s.lower()), None)
                if partial:
                    client.set_current_program_scene(partial)
                    print(f"✅ OBS Scene Swapped (Partial Match): {partial}")
                else:
                    print(f"⚠️ OBS Scene '{target}' not found. Available scenes: {scene_names}")

        elif action == "toggle_stream": client.toggle_stream(); print("✅ OBS Streaming Toggled.")
        elif action == "toggle_recording": client.toggle_record(); print("✅ OBS Recording Toggled.")
        elif action == "clip_that": client.save_replay_buffer(); print("✅ OBS Replay Buffer Captured.")
        elif action == "toggle_mic":
            inputs = client.get_input_list().inputs
            mic_input = next((i['inputName'] for i in inputs if "mic" in i['inputName'].lower() or "audio" in i['inputName'].lower()), None)
            if mic_input:
                client.toggle_input_mute(mic_input)
                print(f"✅ OBS Input Muted/Unmuted: {mic_input}")

        elif action == "toggle_source":
            current_scene = client.get_current_program_scene().current_program_scene_name
            items = client.get_scene_item_list(current_scene).scene_items
            target_item = next((i for i in items if target.lower() in i['sourceName'].lower()), None)
            if target_item:
                new_state = not target_item['sceneItemEnabled']
                if state == "on": new_state = True
                elif state == "off": new_state = False
                client.set_scene_item_enabled(current_scene, target_item['sceneItemId'], new_state)
                print(f"✅ OBS Source Visibility: {target} -> {new_state}")

    except Exception as e:
        print(f"❌ OBS Execution Error: {e}")

def broadcast_control(parameters, response, player, session_memory):
    action = parameters.get("action", "").lower()
    target = parameters.get("target", "").lower().replace("_", " ")
    state = parameters.get("state", "").lower()

    print(f"🎬 RUBE Broadcast Matrix: Action={action}, Target={target}, State={state}")
    broadcasters = get_running_broadcasters()

    if not broadcasters:
        edge_speak("Boss, neither OBS Studio nor Streamlabs is currently running.", player)
        return

    if "obs" in broadcasters:
        client = get_obs_client()
        if client:
            try:
                execute_obs_api(client, action, target, state)
                edge_speak(f"Broadcast command executed, boss.", player)
            except Exception as e:
                print(f"OBS API Error: {e}")
                edge_speak(f"Boss, I attempted the broadcast command but OBS returned an error.", player)
            return
        else:
            edge_speak("Boss, OBS blocked my API connection. Please uncheck Enable Authentication in the WebSocket tools.", player)
            return

    if "streamlabs" in broadcasters:
        execute_win_streamlabs(action, target)
        edge_speak(f"Streamlabs command sent, boss.", player)