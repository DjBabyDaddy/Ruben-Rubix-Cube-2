import copy
import json
import os
from threading import Lock
from datetime import datetime

MEMORY_PATH = "memory/memory.json"
_lock = Lock()

# --- CPU FIX: THE RAM CACHE ---
_memory_cache = None
_last_mtime = 0

def _empty_memory() -> dict:
    """Return an empty memory structure."""
    return {
        "identity": {},
        "preferences": {},
        "relationships": {},
        "emotional_state": {}
    }

def load_memory() -> dict:
    """Load memory from disk instantly using RAM caching."""
    global _memory_cache, _last_mtime

    with _lock:
        try:
            if not os.path.exists(MEMORY_PATH):
                return _empty_memory()

            current_mtime = os.path.getmtime(MEMORY_PATH)
            if _memory_cache is not None and current_mtime == _last_mtime:
                return copy.deepcopy(_memory_cache)

            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    _memory_cache = data
                    _last_mtime = current_mtime
                    return copy.deepcopy(data)
                return _empty_memory()
        except Exception:
            return _empty_memory()

def save_memory(memory: dict) -> None:
    """Save memory to disk and update RAM cache."""
    global _memory_cache, _last_mtime
    if not isinstance(memory, dict): return

    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with _lock:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        _memory_cache = copy.deepcopy(memory)
        _last_mtime = os.path.getmtime(MEMORY_PATH)

def _recursive_update(target: dict, updates: dict) -> bool:
    """Recursively merge updates into target memory."""
    changed = False
    for key, value in updates.items():
        if value is None or (isinstance(value, str) and not value.strip()): continue

        if isinstance(value, dict) and "value" not in value:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
                changed = True
            if _recursive_update(target[key], value): changed = True
        else:
            entry = value if isinstance(value, dict) and "value" in value else {"value": value}
            if key not in target or target[key] != entry:
                target[key] = entry
                changed = True
    return changed

def update_memory(memory_update: dict) -> dict:
    """Merge LLM memory update into global memory and save."""
    if not isinstance(memory_update, dict): return load_memory()
    memory = load_memory()
    if _recursive_update(memory, memory_update): save_memory(memory)
    return memory