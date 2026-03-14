"""RUBE Self-Improvement System — Approval queue, subagent invocation, and edit handlers.

All proposed code changes go through a pending queue. The user must explicitly
approve each edit before any file is written. The subagent (Claude Code CLI)
runs in a subprocess so it never pollutes the main context window.
"""
import os
import re
import json
import uuid
import subprocess
import time
from datetime import datetime

from tts import edge_speak
from actions import file_editor
from memory.feedback_logger import generate_self_assessment

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Queue management
# ---------------------------------------------------------------------------

def add_to_queue(session_memory, file_path, reason, old_content, new_content, diff, source):
    """Create a queue item for a proposed edit and add it to the approval queue.
    Returns the 8-char hex edit ID.
    """
    edit_id = uuid.uuid4().hex[:8]
    item = {
        "id": edit_id,
        "file_path": file_path,
        "reason": reason,
        "old_content": old_content,
        "new_content": new_content,
        "diff": diff,
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "status": "pending",
    }
    session_memory.add_pending_edit(item)
    return edit_id


def get_pending_queue(session_memory):
    """Return all pending edits from the queue."""
    return [e for e in session_memory.get_pending_edits() if e.get("status") == "pending"]


def get_queue_count(session_memory):
    """Return the number of pending edits."""
    return len(get_pending_queue(session_memory))


def present_edit(edit):
    """Format a single edit item for display in the UI log panel."""
    lines = [
        f"{'=' * 50}",
        f"  Edit ID   : {edit.get('id', '???')}",
        f"  File      : {edit.get('file_path', '???')}",
        f"  Reason    : {edit.get('reason', '???')}",
        f"  Source    : {edit.get('source', '???')}",
        f"  Queued at : {edit.get('timestamp', '???')}",
        f"  Diff preview:",
        edit.get("diff", "(no diff)")[:400],
        f"{'=' * 50}",
    ]
    return "\n".join(lines)


def approve_edit(session_memory, edit_id, player):
    """Approve a queued edit: backup the file, write the change, log it.
    Returns (True, success_message) or (False, error_message).
    """
    # Find the edit in the queue
    edits = session_memory.get_pending_edits()
    target = None
    for e in edits:
        if e.get("id") == edit_id:
            target = e
            break

    if not target:
        return False, f"Edit '{edit_id}' not found in the queue."

    fp = target["file_path"]

    # Step 1: Create backup
    ok, backup_result = file_editor.create_backup(fp)
    if not ok:
        return False, f"Backup failed for {fp}: {backup_result}"

    # Step 2: Write the new content
    ok, write_result = file_editor.write_file(fp, target["new_content"])
    if not ok:
        return False, f"Write failed for {fp}: {write_result}"

    # Step 3: Log the approval
    file_editor.log_edit({
        "file_path": fp,
        "action": "approved",
        "reason": target.get("reason", ""),
        "source": target.get("source", ""),
        "diff": target.get("diff", ""),
    })

    # Step 4: Remove from queue
    session_memory.remove_pending_edit(edit_id)

    return True, f"Edit {edit_id} approved and applied to {os.path.basename(fp)}."


def reject_edit(session_memory, edit_id):
    """Reject a queued edit: log the rejection and remove from queue.
    Returns (True, message) or (False, error).
    """
    edits = session_memory.get_pending_edits()
    target = None
    for e in edits:
        if e.get("id") == edit_id:
            target = e
            break

    if not target:
        return False, f"Edit '{edit_id}' not found in the queue."

    # Log the rejection
    file_editor.log_edit({
        "file_path": target.get("file_path", ""),
        "action": "rejected",
        "reason": target.get("reason", ""),
        "source": target.get("source", ""),
        "diff": target.get("diff", ""),
    })

    # Remove from queue
    session_memory.remove_pending_edit(edit_id)

    return True, f"Edit {edit_id} rejected and discarded."


# ---------------------------------------------------------------------------
# Subagent invocation
# ---------------------------------------------------------------------------

def invoke_subagent(file_path, reason):
    """Spawn Claude Code CLI (real Anthropic API) to analyze a file and propose a fix.

    Claude Code reads CLAUDE.md and ai_docs/ automatically for full project context.
    No need to inject RUBE_SUPER_BRAIN.md — the folder-as-architecture provides it.
    Returns {"proposed_fix": str, "reason": str} or None on any failure.
    """
    # Read the file first
    ok, content = file_editor.read_file(file_path)
    if not ok:
        print(f"⚠️ Subagent: could not read {file_path}: {content}")
        return None

    prompt = (
        f"You are analyzing a Python file from the RUBE AI assistant project.\n"
        f"File: {file_path}\n"
        f"Issue: {reason}\n\n"
        f"Current file content:\n```\n{content}\n```\n\n"
        f"Propose a fix. Return ONLY a JSON object with exactly these keys:\n"
        f'{{"proposed_fix": "<the complete new file content>", "reason": "<one sentence explaining what changed>"}}\n'
        f"No markdown. No explanation outside the JSON."
    )

    start_time = time.time()
    try:
        # Use real Anthropic API — no env overrides.
        # Claude Code reads CLAUDE.md and ai_docs/ automatically for project context.
        proc = subprocess.Popen(
            ["claude", "--print", "-p", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT,
        )
        try:
            stdout, stderr = proc.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            elapsed = int(time.time() - start_time)
            print(f"⚠️ Subagent: Claude Code timed out after {elapsed}s")
            return None
    except FileNotFoundError:
        print("⚠️ Subagent: 'claude' CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
        return None
    except Exception as e:
        print(f"⚠️ Subagent subprocess error: {e}")
        return None
    finally:
        elapsed = int(time.time() - start_time)
        print(f"🔧 Subagent finished in {elapsed}s")

    if proc.returncode != 0:
        print(f"⚠️ Subagent exited with code {proc.returncode}: {stderr[:300]}")
        return None

    # Parse JSON from Claude Code's output
    raw = stdout.strip()

    # Try to extract JSON from the response (may be wrapped in markdown code blocks)
    json_text = raw
    if "```json" in raw:
        try:
            start = raw.index("```json") + 7
            end = raw.index("```", start)
            json_text = raw[start:end].strip()
        except ValueError:
            pass
    elif "```" in raw:
        try:
            start = raw.index("```") + 3
            end = raw.index("```", start)
            json_text = raw[start:end].strip()
        except ValueError:
            pass

    # Find the JSON object boundaries
    try:
        obj_start = json_text.index("{")
        obj_end = json_text.rindex("}") + 1
        parsed = json.loads(json_text[obj_start:obj_end])
    except (ValueError, json.JSONDecodeError):
        print(f"⚠️ Subagent: could not parse output as JSON.")
        return None

    if not isinstance(parsed, dict):
        print("⚠️ Subagent: output is not a JSON object.")
        return None

    proposed = parsed.get("proposed_fix")
    fix_reason = parsed.get("reason", reason)

    if not proposed or not isinstance(proposed, str):
        print("⚠️ Subagent: missing 'proposed_fix' in output.")
        return None

    return {"proposed_fix": proposed, "reason": fix_reason}


# ---------------------------------------------------------------------------
# Reminder system
# ---------------------------------------------------------------------------

def get_reminder_message(session_memory):
    """Return a reminder string if there are pending edits, else None."""
    count = get_queue_count(session_memory)
    if count == 0:
        return None
    s = "s" if count > 1 else ""
    return f"Boss, you've got {count} pending edit{s} waiting for review. Say 'show pending edits' when you're ready."


# ---------------------------------------------------------------------------
# Intent handler functions (match the action module signature)
# ---------------------------------------------------------------------------

def handle_review_pending(parameters, response, player, session_memory):
    """Show all pending code edits to the user."""
    edits = get_pending_queue(session_memory)
    if not edits:
        edge_speak("No pending edits in the queue, boss.", player)
        return

    for edit in edits:
        formatted = present_edit(edit)
        player.write_log(f"RUBE:\n{formatted}")

    count = len(edits)
    s = "s" if count > 1 else ""
    edge_speak(
        f"I have {count} pending edit{s}. Check the log panel for details. "
        f"Say 'approve edit' followed by the ID to apply, or 'reject edit' to discard.",
        player,
    )


def handle_approve(parameters, response, player, session_memory):
    """Approve and apply a specific queued edit."""
    edit_id = str(parameters.get("edit_id", "")).strip()
    if not edit_id:
        edge_speak("Boss, I need the edit ID. Say 'show pending edits' to see available IDs.", player)
        return

    success, msg = approve_edit(session_memory, edit_id, player)
    if success:
        edge_speak(msg, player)
    else:
        edge_speak(f"Could not apply that edit. {msg}", player)


def handle_reject(parameters, response, player, session_memory):
    """Reject and discard a specific queued edit."""
    edit_id = str(parameters.get("edit_id", "")).strip()
    if not edit_id:
        edge_speak("Boss, I need the edit ID to reject.", player)
        return

    success, msg = reject_edit(session_memory, edit_id)
    if success:
        edge_speak(msg, player)
    else:
        edge_speak(f"Could not reject that edit. {msg}", player)


def handle_request_file_edit(parameters, response, player, session_memory):
    """User requests an edit to a specific file — invoke subagent to propose it."""
    file_path = str(parameters.get("file_path", "")).strip()
    reason = str(parameters.get("reason", "")).strip()

    if not file_path or not reason:
        edge_speak("Boss, I need a file path and a description of what to change.", player)
        return

    edge_speak("Dispatching a subagent to analyze that file. Stand by.", player)

    result = invoke_subagent(file_path, reason)
    if not result:
        edge_speak("My subagent matrix could not generate a fix for that one, boss.", player)
        return

    # Read the original file for the diff
    ok, old_content = file_editor.read_file(file_path)
    if not ok:
        edge_speak(f"Could not read the target file. {old_content}", player)
        return

    new_content = result["proposed_fix"]
    diff = file_editor.generate_diff(old_content, new_content, file_path)

    if diff == "(no changes)":
        edge_speak("The subagent analyzed the file but found no changes needed.", player)
        return

    edit_id = add_to_queue(session_memory, file_path, result["reason"], old_content, new_content, diff, "user_request")
    player.write_log(f"RUBE: Proposed edit {edit_id} queued.\n{diff[:400]}")
    edge_speak(f"Edit {edit_id} is queued for your review. Say 'show pending edits' to inspect it.", player)


def handle_self_improve(parameters, response, player, session_memory):
    """Analyze RUBE's own failure patterns and propose code fixes via subagent."""
    insights = generate_self_assessment()
    if not insights:
        edge_speak("My systems are running clean. No improvements needed right now, boss.", player)
        return

    edge_speak(f"I found {len(insights)} area{'s' if len(insights) > 1 else ''} for improvement. Analyzing now.", player)

    queued = 0
    for insight in insights[:2]:  # Cap at 2 subagent calls per invocation
        intent_name = _extract_intent_from_insight(insight)
        if not intent_name:
            continue

        file_path = f"actions/{intent_name}.py"
        if not os.path.isfile(os.path.join(PROJECT_ROOT, file_path)):
            continue

        result = invoke_subagent(file_path, insight)
        if not result:
            continue

        ok, old_content = file_editor.read_file(file_path)
        if not ok:
            continue

        new_content = result["proposed_fix"]
        diff = file_editor.generate_diff(old_content, new_content, file_path)
        if diff == "(no changes)":
            continue

        edit_id = add_to_queue(session_memory, file_path, result["reason"], old_content, new_content, diff, "self_assessment")
        player.write_log(f"RUBE: Self-improvement edit {edit_id} queued for {file_path}")
        queued += 1

    if queued > 0:
        edge_speak(f"I've queued {queued} improvement{'s' if queued > 1 else ''} for your review, boss.", player)
    else:
        edge_speak("I analyzed the issues but couldn't generate actionable fixes this time.", player)


def _extract_intent_from_insight(insight):
    """Try to extract an intent/module name from a self-assessment insight string.
    Looks for quoted strings like 'whatsapp_message' in the insight text.
    """
    match = re.search(r"'(\w+)'", insight)
    return match.group(1) if match else None
