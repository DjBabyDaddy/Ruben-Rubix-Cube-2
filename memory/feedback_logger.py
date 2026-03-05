import json
import os
from datetime import datetime
from threading import Lock

FEEDBACK_LOG_PATH = "memory/feedback_log.json"
MAX_ENTRIES = 500
_lock = Lock()

def log_execution(intent: str, parameters: dict, response: str, success: bool, exec_time_ms: float) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "intent": intent,
        "parameters": parameters,
        "response": (response or "")[:500],
        "success": success,
        "exec_time_ms": round(exec_time_ms, 1)
    }
    with _lock:
        try:
            os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)
            if os.path.exists(FEEDBACK_LOG_PATH):
                with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
                    log = json.load(f)
                if not isinstance(log, list):
                    log = []
            else:
                log = []
            log.append(entry)
            if len(log) > MAX_ENTRIES:
                log = log[-MAX_ENTRIES:]
            with open(FEEDBACK_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Feedback Logger Error: {e}")
