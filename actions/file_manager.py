import os
import shutil
import json
from tkinter import messagebox

TRASH_DIR = os.path.join(os.getcwd(), ".rube_trash")
LOG_FILE = os.path.join(os.getcwd(), ".rube_file_log.json")

def _ensure_setup():
    """Ensure the hidden trash folder and log file exist."""
    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

def _log_action(action_type, source, destination=None):
    """Save the transaction so RUBE can undo it later."""
    _ensure_setup()
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)
    
    logs.append({
        "action": action_type,
        "source": source,
        "destination": destination
    })
    
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def manage_files(parameters, response, player, session_memory):
    """Handles moving, organizing, and soft-deleting files with user approval."""
    _ensure_setup()
    
    action = parameters.get("file_action") # 'move', 'delete', or 'rename'
    source_path = parameters.get("source_path")
    destination_path = parameters.get("destination_path") # Not needed for delete
    
    if not source_path or not os.path.exists(source_path):
        player.write_log(f"RUBE ERROR: Could not find file at {source_path}")
        return

    # THE SAFEGUARD: Human-in-the-Loop Pop-up
    msg = f"RUBE wants to {action.upper()}:\n\nFile: {source_path}"
    if action in ["move", "rename"]:
        msg += f"\n\nTo: {destination_path}"
    
    # Using Tkinter messagebox safely from a background thread
    approved = messagebox.askyesno("RUBE Security Override", msg, parent=player.root)
    
    if not approved:
        player.write_log("ЁЯЫС RUBE: File action denied by Boss.")
        return

    try:
        if action == "delete":
            # SOFT DELETE: Move to hidden trash instead of permanent deletion
            file_name = os.path.basename(source_path)
            trash_path = os.path.join(TRASH_DIR, file_name)
            shutil.move(source_path, trash_path)
            _log_action("delete", source_path, trash_path)
            player.write_log(f"RUBE: Safely trashed {file_name}")

        elif action in ["move", "rename"]:
            # Ensure target directory exists
            target_dir = os.path.dirname(destination_path)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            shutil.move(source_path, destination_path)
            _log_action(action, source_path, destination_path)
            player.write_log(f"RUBE: Moved/Renamed to {destination_path}")

    except Exception as e:
        player.write_log(f"RUBE ERROR during file op: {e}")

def undo_last_file_action(parameters, response, player, session_memory):
    """Reverses the last file transaction based on the JSON log."""
    _ensure_setup()
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)
        
    if not logs:
        player.write_log("RUBE: No file actions in my memory to undo.")
        return
        
    last_action = logs.pop() # Get the most recent action
    
    try:
        # Reversal Logic
        if last_action["action"] == "delete":
            shutil.move(last_action["destination"], last_action["source"])
            player.write_log(f"RUBE UNDO: Restored {os.path.basename(last_action['source'])}")
            
        elif last_action["action"] in ["move", "rename"]:
            shutil.move(last_action["destination"], last_action["source"])
            player.write_log(f"RUBE UNDO: Reverted file to {last_action['source']}")
            
        # Save the log without the reversed action
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)
            
    except Exception as e:
        player.write_log(f"RUBE UNDO ERROR: {e}")