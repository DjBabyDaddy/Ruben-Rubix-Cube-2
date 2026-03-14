"""RUBE Code Agent — Two-tier system for coding tasks.

Tier 1 (Heavy): Claude Code CLI → Anthropic API
    For project-level work, self-improvement, multi-file edits.
    Claude Code reads CLAUDE.md and ai_docs/ automatically for full project context.

Tier 2 (Quick): Direct HTTP → LM Studio (Qwen 3.5 9B at localhost:1234)
    For simple code questions, write-a-function, explain-this-code.
    Free, offline, fast. Streams tokens to the terminal in real-time.

Falls back to Tier 1 if LM Studio is offline.
"""
import os
import json
import subprocess
import threading
import time

import requests
from dotenv import load_dotenv

from tts import edge_speak

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Timeout for Claude Code CLI (Tier 1)
CLAUDE_CODE_TIMEOUT = 120
# Timeout for LM Studio HTTP (Tier 2) — (connect_timeout, read_timeout)
LM_STUDIO_TIMEOUT = (10, 300)

# Keywords that indicate the task needs full project context (Tier 1)
HEAVY_KEYWORDS = [
    "edit", "fix", "improve", "refactor", "rube", "project", "module",
    "file", "debug", "update", "self-improve", "review", "analyze",
    "actions/", "core/", "memory/", ".py",
]


def _lm_studio_online(base_url: str, timeout: int = 3) -> bool:
    """Return True if LM Studio's server is reachable."""
    try:
        resp = requests.get(f"{base_url}/v1/models", timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


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
# Tier 1: Claude Code CLI → Anthropic API
# ---------------------------------------------------------------------------

def _invoke_claude_code(task, context, player):
    """Tier 1: Full Claude Code CLI with real Anthropic API.

    Claude Code reads CLAUDE.md and ai_docs/ automatically, giving it full
    project understanding. Uses ANTHROPIC_API_KEY from .env — no overrides.
    """
    prompt_parts = [f"Task: {task}"]
    if context and context.strip():
        prompt_parts.append(f"Context:\n{context.strip()}")
    prompt_parts.append(
        "Provide a clear, complete answer. If writing code, include the full "
        "implementation with brief inline comments. Be concise and practical."
    )
    full_prompt = "\n\n".join(prompt_parts)

    # Start progress ticker
    stop_ticker = threading.Event()
    start_time = time.time()
    ticker = threading.Thread(
        target=_progress_ticker,
        args=(player, stop_ticker, start_time, "Claude Code"),
        daemon=True,
    )
    ticker.start()

    try:
        proc = subprocess.Popen(
            ["claude", "--print", "-p", full_prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT,
        )

        try:
            stdout, stderr = proc.communicate(timeout=CLAUDE_CODE_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            elapsed = int(time.time() - start_time)
            player.write_log(f"RUBE [Claude Code]: Timed out after {elapsed}s")
            print(f"⚠️ Claude Code timed out after {elapsed}s")
            return None

    except FileNotFoundError:
        print("⚠️ Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
        player.write_log("RUBE [Claude Code]: CLI not found — install claude-code first")
        return None
    except Exception as e:
        print(f"⚠️ Claude Code error: {e}")
        return None
    finally:
        stop_ticker.set()
        elapsed = int(time.time() - start_time)
        player.write_log(f"RUBE [Claude Code]: Finished in {elapsed}s")

    if proc.returncode != 0:
        print(f"⚠️ Claude Code exited with code {proc.returncode}: {stderr[:300]}")
        player.write_log(f"RUBE [Claude Code]: Error — {stderr[:200]}")
        return None

    return stdout.strip() or None


# ---------------------------------------------------------------------------
# Tier 2: Direct HTTP → LM Studio (OpenAI-compatible)
# ---------------------------------------------------------------------------

def _invoke_local_lm(task, context, lm_url, lm_model, lm_token, player):
    """Tier 2: Direct HTTP to LM Studio's OpenAI-compatible endpoint.

    Streams tokens to the terminal in real-time. Free, offline, fast.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a concise coding assistant. Provide clear, complete answers. "
                "If writing code, include the full implementation with brief inline comments."
            ),
        },
        {
            "role": "user",
            "content": f"Task: {task}" + (f"\n\nContext:\n{context}" if context else ""),
        },
    ]

    player.write_log("RUBE [LM Studio]: Streaming response...")
    start_time = time.time()

    try:
        resp = requests.post(
            f"{lm_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {lm_token}",
                "Content-Type": "application/json",
            },
            json={
                "model": lm_model,
                "messages": messages,
                "max_tokens": 2048,
                "temperature": 0.3,
                "stream": True,
            },
            stream=True,
            timeout=LM_STUDIO_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        player.write_log("RUBE [LM Studio]: Connection refused — is the server running?")
        return None
    except requests.exceptions.Timeout:
        player.write_log("RUBE [LM Studio]: Connection timed out")
        return None
    except Exception as e:
        player.write_log(f"RUBE [LM Studio]: HTTP error — {e}")
        return None

    # Stream tokens and display in real-time
    full_text = ""
    buffer = ""
    chunk_count = 0

    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[6:]  # strip "data: "
        if payload == "[DONE]":
            break
        try:
            chunk = json.loads(payload)
            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            if delta:
                full_text += delta
                buffer += delta
                chunk_count += 1
                # Flush to terminal every ~100 chars or every 10 chunks
                if len(buffer) >= 100 or chunk_count % 10 == 0:
                    player.write_log(f"  {buffer}")
                    buffer = ""
        except (json.JSONDecodeError, IndexError, KeyError):
            continue

    # Flush remaining buffer
    if buffer:
        player.write_log(f"  {buffer}")

    elapsed = int(time.time() - start_time)
    player.write_log(f"RUBE [LM Studio]: Done in {elapsed}s ({len(full_text)} chars)")

    return full_text.strip() or None


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

def handle_code_task(parameters, response, player, session_memory):
    """Handle the 'code_task' intent — route to Tier 1 or Tier 2 based on task complexity."""
    load_dotenv()
    lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
    lm_model = os.getenv("LM_STUDIO_MODEL", "qwen/qwen3.5-9b")
    lm_token = os.getenv("LM_STUDIO_TOKEN", "lmstudio")

    task = str(parameters.get("task", "")).strip()
    context = str(parameters.get("context", "")).strip()

    if not task:
        edge_speak("Boss, I need a description of the coding task.", player)
        return

    # Decide tier based on task content
    task_lower = task.lower()
    use_claude = any(kw in task_lower for kw in HEAVY_KEYWORDS)

    if use_claude:
        # Tier 1: Claude Code with full project context
        edge_speak("Routing that to Claude Code for full project analysis. Stand by, boss.", player)
        player.write_log(f"RUBE [Code Agent]: Tier 1 (Claude Code) — {task}")
        result_text = _invoke_claude_code(task, context, player)
    else:
        # Tier 2: LM Studio for quick code help
        lm_online = _lm_studio_online(lm_url)
        if lm_online:
            edge_speak("Sending that to the local coding model. Stand by.", player)
            player.write_log(f"RUBE [Code Agent]: Tier 2 (LM Studio) — {task}")
            result_text = _invoke_local_lm(task, context, lm_url, lm_model, lm_token, player)
        else:
            # Fallback to Tier 1 if LM Studio is down
            edge_speak(
                "Local model is offline. Routing to Claude Code instead.", player
            )
            player.write_log(f"RUBE [Code Agent]: Tier 2 offline, falling back to Tier 1 — {task}")
            result_text = _invoke_claude_code(task, context, player)

    if not result_text:
        edge_speak(
            "The coding agent couldn't complete that task. Check the log panel for details.",
            player,
        )
        return

    # Log the full result to the UI panel
    player.write_log(f"RUBE [Code Agent Result]:\n{result_text}")

    # Speak a short summary — trim so TTS doesn't read a wall of code
    summary = result_text.strip()
    if len(summary) > 300:
        summary = summary[:300].rstrip() + "... Check the log panel for the full output."
    edge_speak(summary, player)
