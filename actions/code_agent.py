"""RUBE Code Agent — Routes coding and complex tasks to Claude Code CLI backed by
LM Studio (Qwen 3.5 9B running locally at localhost:1234).

The subprocess inherits the current environment but overrides ANTHROPIC_BASE_URL
and ANTHROPIC_AUTH_TOKEN so Claude Code talks to LM Studio instead of Anthropic's API.
No Anthropic API credits are consumed for code_task calls.
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

# Max time (seconds) before we kill the subprocess
CODE_AGENT_TIMEOUT = 300


def _lm_studio_online(base_url: str, timeout: int = 3) -> bool:
    """Return True if LM Studio's server is reachable."""
    try:
        resp = requests.get(f"{base_url}/v1/models", timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def _progress_ticker(player, stop_event, start_time):
    """Background thread that posts elapsed-time updates to the log panel."""
    milestones = {15, 30, 60, 90, 120, 180, 240}
    last_reported = 0
    while not stop_event.is_set():
        stop_event.wait(5)  # check every 5 seconds
        if stop_event.is_set():
            break
        elapsed = int(time.time() - start_time)
        # Report at milestones, then every 30s after 60s
        should_report = elapsed in milestones or (elapsed > 60 and elapsed - last_reported >= 30)
        if should_report and elapsed != last_reported:
            last_reported = elapsed
            if elapsed < 60:
                player.write_log(f"RUBE [Code Agent]: Working... {elapsed}s elapsed")
            else:
                mins = elapsed // 60
                secs = elapsed % 60
                player.write_log(f"RUBE [Code Agent]: Working... {mins}m {secs}s elapsed")


def _invoke_local_claude(task, context, lm_url, lm_model, lm_token, player):
    """Spawn Claude Code CLI pointed at LM Studio with live progress updates."""
    prompt_parts = [
        "You are a coding assistant embedded in the RUBE AI system.",
        f"Task: {task}",
    ]
    if context and context.strip():
        prompt_parts.append(f"Context / extra info:\n{context.strip()}")
    prompt_parts.append(
        "Provide a clear, complete answer. If writing code, include the full implementation "
        "with brief inline comments. Be concise and practical."
    )
    full_prompt = "\n\n".join(prompt_parts)

    env = {
        **os.environ,
        "ANTHROPIC_BASE_URL": lm_url,
        "ANTHROPIC_AUTH_TOKEN": lm_token,
        "ANTHROPIC_API_KEY": lm_token,
    }

    # Start progress ticker
    stop_ticker = threading.Event()
    start_time = time.time()
    ticker = threading.Thread(
        target=_progress_ticker,
        args=(player, stop_ticker, start_time),
        daemon=True,
    )
    ticker.start()

    try:
        proc = subprocess.Popen(
            ["claude", "--model", lm_model, "--print", "--output-format", "json", "-p", full_prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT,
            env=env,
        )

        try:
            stdout, stderr = proc.communicate(timeout=CODE_AGENT_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            elapsed = int(time.time() - start_time)
            player.write_log(f"RUBE [Code Agent]: Timed out after {elapsed}s")
            print(f"⚠️ Code Agent: Claude Code timed out after {elapsed} seconds.")
            return None

    except FileNotFoundError:
        print("⚠️ Code Agent: 'claude' CLI not found. Is Claude Code installed?")
        return None
    except Exception as e:
        print(f"⚠️ Code Agent subprocess error: {e}")
        return None
    finally:
        stop_ticker.set()
        elapsed = int(time.time() - start_time)
        player.write_log(f"RUBE [Code Agent]: Finished in {elapsed}s")

    if proc.returncode != 0:
        print(f"⚠️ Code Agent exited with code {proc.returncode}: {stderr[:300]}")
        player.write_log(f"RUBE [Code Agent]: Error — {stderr[:200]}")
        return None

    # Claude Code --output-format json wraps output in {"result": "..."}
    try:
        outer = json.loads(stdout)
        if isinstance(outer, dict):
            return outer.get("result", stdout)
        return stdout
    except (json.JSONDecodeError, TypeError):
        return stdout.strip() or None


def handle_code_task(parameters, response, player, session_memory):
    """Handle the 'code_task' intent — delegate to local LM Studio coding agent."""
    load_dotenv()
    lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
    lm_model = os.getenv("LM_STUDIO_MODEL", "qwen/qwen3.5-9b")
    lm_token = os.getenv("LM_STUDIO_TOKEN", "lmstudio")

    task = str(parameters.get("task", "")).strip()
    context = str(parameters.get("context", "")).strip()

    if not task:
        edge_speak("Boss, I need a description of the coding task.", player)
        return

    # Reachability check before spinning up the subprocess
    if not _lm_studio_online(lm_url):
        edge_speak(
            "Boss, LM Studio appears to be offline. Start LM Studio, load Qwen 3.5 9B, "
            "and start the server on port 1234, then try again.",
            player,
        )
        return

    edge_speak("Routing that to the local coding agent. Stand by, boss.", player)
    player.write_log(f"RUBE [Code Agent]: Task → {task}")

    result_text = _invoke_local_claude(task, context, lm_url, lm_model, lm_token, player)

    if not result_text:
        edge_speak(
            "The local coding agent couldn't complete that task. "
            "Check the log panel for details.",
            player,
        )
        return

    # Log the full result to the UI panel
    player.write_log(f"RUBE [Code Agent Result]:\n{result_text}")

    # Speak a short summary — trim to first 300 chars so TTS doesn't read out a wall of code
    summary = result_text.strip()
    if len(summary) > 300:
        summary = summary[:300].rstrip() + "... Check the log panel for the full output."
    edge_speak(summary, player)
