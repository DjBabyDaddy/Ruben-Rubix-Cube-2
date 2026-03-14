"""RUBE Code Agent — Two-tier system for coding tasks.

Tier 1 (Heavy): Anthropic API (Claude Sonnet 4.6)
    For project-level work, self-improvement, multi-file edits.

Tier 2 (Quick): Groq API (Llama 3.3 70B → 8B fallback)
    For simple code questions, write-a-function, explain-this-code.
    Free tier, lightning fast. Streams tokens to the terminal in real-time.

Falls back to Tier 1 if Groq is unavailable.
"""
import os
import threading
import time

from dotenv import load_dotenv

from tts import edge_speak

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _progress_ticker(player, stop_event, start_time, label="Code Agent"):
    """Background thread that posts elapsed-time updates to the log panel."""
    milestones = {15, 30, 60, 90, 120, 180, 240}
    last_reported = 0
    while not stop_event.is_set():
        stop_event.wait(5)
        if stop_event.is_set():
            break
        elapsed = int(time.time() - start_time)
        should_report = elapsed in milestones or (elapsed > 60 and elapsed - last_reported >= 30)
        if should_report and elapsed != last_reported:
            last_reported = elapsed
            if elapsed < 60:
                player.write_log(f"RUBE [{label}]: Working... {elapsed}s elapsed")
            else:
                mins = elapsed // 60
                secs = elapsed % 60
                player.write_log(f"RUBE [{label}]: Working... {mins}m {secs}s elapsed")


# ---------------------------------------------------------------------------
# Tier 1: Anthropic API (Claude Sonnet) — Heavy tasks
# ---------------------------------------------------------------------------

def _invoke_anthropic(task, context, player):
    """Tier 1: Direct Anthropic API call with Claude Sonnet for complex tasks."""
    import anthropic

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        player.write_log("RUBE [Anthropic]: No API key configured")
        return None

    prompt_parts = [f"Task: {task}"]
    if context and context.strip():
        prompt_parts.append(f"Context:\n{context.strip()}")
    prompt_parts.append(
        "Provide a clear, complete answer. If writing code, include the full "
        "implementation with brief inline comments. Be concise and practical."
    )
    full_prompt = "\n\n".join(prompt_parts)

    stop_ticker = threading.Event()
    start_time = time.time()
    ticker = threading.Thread(
        target=_progress_ticker,
        args=(player, stop_ticker, start_time, "Claude Sonnet"),
        daemon=True,
    )
    ticker.start()

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            temperature=0.2,
            messages=[{"role": "user", "content": full_prompt}],
        )
        return response.content[0].text.strip() or None
    except Exception as e:
        print(f"⚠️ Anthropic API error: {e}")
        player.write_log(f"RUBE [Claude Sonnet]: Error — {str(e)[:200]}")
        return None
    finally:
        stop_ticker.set()
        elapsed = int(time.time() - start_time)
        player.write_log(f"RUBE [Claude Sonnet]: Finished in {elapsed}s")


# ---------------------------------------------------------------------------
# Tier 2: Groq API (Llama 70B → 8B) — Quick tasks
# ---------------------------------------------------------------------------

def _invoke_groq_stream(task, context, player):
    """Tier 2: Groq API with streaming. Free, fast, auto-fallback."""
    from core.groq_brain import groq_completion_stream, get_current_model

    system_prompt = (
        "You are a concise coding assistant. Provide clear, complete answers. "
        "If writing code, include the full implementation with brief inline comments."
    )
    user_prompt = f"Task: {task}" + (f"\n\nContext:\n{context}" if context else "")

    model_name = get_current_model().split("/")[-1]
    player.write_log(f"RUBE [Groq {model_name}]: Streaming response...")
    start_time = time.time()

    full_text = ""
    buffer = ""
    chunk_count = 0

    try:
        for delta in groq_completion_stream(user_prompt, system_prompt=system_prompt):
            full_text += delta
            buffer += delta
            chunk_count += 1
            if len(buffer) >= 100 or chunk_count % 10 == 0:
                player.write_log(f"  {buffer}")
                buffer = ""
    except Exception as e:
        player.write_log(f"RUBE [Groq]: Error — {e}")
        return None

    if buffer:
        player.write_log(f"  {buffer}")

    elapsed = int(time.time() - start_time)
    player.write_log(f"RUBE [Groq]: Done in {elapsed}s ({len(full_text)} chars)")

    return full_text.strip() or None


# ---------------------------------------------------------------------------
# Keywords that indicate heavy task → Tier 1
# ---------------------------------------------------------------------------

HEAVY_KEYWORDS = [
    "edit", "fix", "improve", "refactor", "rube", "project", "module",
    "file", "debug", "update", "self-improve", "review", "analyze",
    "actions/", "core/", "memory/", ".py",
]


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

def handle_code_task(parameters, response, player, session_memory):
    """Handle the 'code_task' intent — route to Tier 1 or Tier 2 based on task complexity."""
    task = str(parameters.get("task", "")).strip()
    context = str(parameters.get("context", "")).strip()

    if not task:
        edge_speak("Boss, I need a description of the coding task.", player)
        return

    task_lower = task.lower()
    use_claude = any(kw in task_lower for kw in HEAVY_KEYWORDS)

    if use_claude:
        edge_speak("Routing that to Claude Sonnet for deep analysis. Stand by, boss.", player)
        player.write_log(f"RUBE [Code Agent]: Tier 1 (Claude Sonnet) — {task}")
        result_text = _invoke_anthropic(task, context, player)
    else:
        edge_speak("Sending that to the Groq speed brain. Stand by.", player)
        player.write_log(f"RUBE [Code Agent]: Tier 2 (Groq) — {task}")
        result_text = _invoke_groq_stream(task, context, player)

        if not result_text:
            # Fallback to Tier 1 if Groq fails
            edge_speak("Groq is unavailable. Routing to Claude Sonnet instead.", player)
            player.write_log(f"RUBE [Code Agent]: Groq failed, falling back to Tier 1 — {task}")
            result_text = _invoke_anthropic(task, context, player)

    if not result_text:
        edge_speak(
            "The coding agent couldn't complete that task. Check the log panel for details.",
            player,
        )
        return

    player.write_log(f"RUBE [Code Agent Result]:\n{result_text}")

    summary = result_text.strip()
    if len(summary) > 300:
        summary = summary[:300].rstrip() + "... Check the log panel for the full output."
    edge_speak(summary, player)
