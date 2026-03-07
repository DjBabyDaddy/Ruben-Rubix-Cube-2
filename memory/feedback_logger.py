import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from threading import Lock

FEEDBACK_LOG_PATH = "memory/feedback_log.json"
MAX_ENTRIES = 500
_lock = Lock()


def _read_log() -> list:
    """Read the feedback log from disk (caller must hold _lock or accept race)."""
    try:
        if not os.path.exists(FEEDBACK_LOG_PATH):
            return []
        with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)
        return log if isinstance(log, list) else []
    except Exception:
        return []


def _write_log(log: list) -> None:
    """Write the feedback log to disk (caller must hold _lock)."""
    os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)
    if len(log) > MAX_ENTRIES:
        log = log[-MAX_ENTRIES:]
    with open(FEEDBACK_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def log_execution(intent: str, parameters: dict, response: str, success: bool, exec_time_ms: float) -> None:
    """Legacy dispatch-time logger (kept for backward compat)."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "intent": intent,
        "parameters": {k: str(v)[:100] for k, v in (parameters or {}).items()},
        "response": (response or "")[:500],
        "success": success,
        "exec_time_ms": round(exec_time_ms, 1)
    }
    with _lock:
        try:
            log = _read_log()
            log.append(entry)
            _write_log(log)
        except Exception as e:
            print(f"⚠️ Feedback Logger Error: {e}")


def log_action_result(intent: str, parameters: dict, success: bool,
                      exec_time_ms: float, error_detail: str = "") -> None:
    """Called by the _run_and_log wrapper AFTER an action finishes with real outcome data."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "intent": intent,
        "parameters": {k: str(v)[:100] for k, v in (parameters or {}).items()},
        "success": success,
        "exec_time_ms": round(exec_time_ms, 1),
        "error": (error_detail or "")[:200]
    }
    with _lock:
        try:
            log = _read_log()
            log.append(entry)
            _write_log(log)
        except Exception as e:
            print(f"⚠️ Feedback Logger Error: {e}")


def get_recent_lessons(lookback: int = 50) -> str:
    """Read the last N log entries and summarize failure patterns.
    Returns a compact string for injection into the LLM system prompt."""
    with _lock:
        log = _read_log()
    if not log:
        return ""

    recent = log[-lookback:]
    failures = [e for e in recent if not e.get("success", True)]
    if not failures:
        return ""

    intent_failures: dict[str, list[str]] = {}
    for f in failures:
        intent = f.get("intent", "unknown")
        intent_failures.setdefault(intent, []).append(f.get("error", ""))

    lines = []
    for intent, errors in intent_failures.items():
        unique_errors = list(set(e for e in errors if e))[:3]
        count = len(errors)
        detail = "; ".join(unique_errors) if unique_errors else "unspecified"
        lines.append(f"- {intent}: failed {count}x. Errors: {detail}")

    return "\n".join(lines) if lines else ""


def generate_self_assessment() -> list[str]:
    """Analyze feedback_log.json at startup and return actionable insights.
    Looks for high failure rates, slow actions, and repeated failure patterns."""
    with _lock:
        log = _read_log()
    if len(log) < 5:
        return []

    suggestions: list[str] = []

    # 1. Intents with high failure rates
    intent_counts: Counter = Counter()
    intent_fails: Counter = Counter()
    for entry in log:
        intent = entry.get("intent", "")
        intent_counts[intent] += 1
        if not entry.get("success", True):
            intent_fails[intent] += 1

    for intent, fails in intent_fails.items():
        total = intent_counts[intent]
        rate = fails / total if total > 0 else 0
        if rate > 0.3 and fails >= 3:
            suggestions.append(
                f"'{intent}' has a {rate:.0%} failure rate ({fails}/{total}). Check preconditions or API keys."
            )

    # 2. Consistently slow actions (>10s)
    slow = [e for e in log if e.get("exec_time_ms", 0) > 10000]
    if len(slow) > 3:
        slow_intents = Counter(e.get("intent", "") for e in slow)
        top_name, top_count = slow_intents.most_common(1)[0]
        suggestions.append(
            f"'{top_name}' is consistently slow ({top_count} runs over 10s). Consider timeout optimization."
        )

    # 3. Repeated failure patterns (same intent failing with same error)
    pattern_fails: defaultdict = defaultdict(int)
    for entry in log[-100:]:
        if not entry.get("success", True):
            key = f"{entry.get('intent', '')}:{entry.get('error', '')[:60]}"
            pattern_fails[key] += 1

    for pattern, count in pattern_fails.items():
        if count >= 3:
            intent_name = pattern.split(":")[0]
            suggestions.append(
                f"Repeated failure pattern in '{intent_name}' ({count} times). May need a code fix."
            )

    return suggestions[:5]
