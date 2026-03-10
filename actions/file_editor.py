"""RUBE File Editor — Safe file editing with mandatory backup and audit trail.

Every file write requires a .rube.bak backup to exist first.
All edits are logged to memory/edit_log.json for full audit history.
"""
import os
import json
import shutil
import difflib
from datetime import datetime
from threading import Lock

EDIT_LOG_PATH = "memory/edit_log.json"
MAX_EDIT_LOG = 200
BACKUP_SUFFIX = ".rube.bak"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_edit_lock = Lock()

# Files that must never be written to by the self-improvement system
PROTECTED_FILES = {".env", "memory/memory.json"}
PROTECTED_EXTENSIONS = {".key", ".pem", ".secret"}


def _validate_path(file_path):
    """Validate that a file path is safe to operate on.
    Returns (True, absolute_path) or (False, error_message).
    """
    try:
        abs_path = os.path.abspath(file_path)
    except Exception:
        return False, "Invalid file path."

    # Must be under the project root
    if not abs_path.startswith(PROJECT_ROOT):
        return False, "File path is outside the project directory."

    # Check protected files
    rel_path = os.path.relpath(abs_path, PROJECT_ROOT).replace("\\", "/")
    if rel_path in PROTECTED_FILES:
        return False, f"'{rel_path}' is a protected file and cannot be edited."

    # Check protected extensions
    _, ext = os.path.splitext(abs_path)
    if ext.lower() in PROTECTED_EXTENSIONS:
        return False, f"Files with '{ext}' extension are protected."

    return True, abs_path


def read_file(file_path):
    """Read a file and return its content.
    Returns (True, content_string) or (False, error_message).
    """
    valid, result = _validate_path(file_path)
    if not valid:
        return False, result

    abs_path = result
    if not os.path.isfile(abs_path):
        return False, f"File not found: {file_path}"

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return True, f.read()
    except Exception as e:
        return False, f"Could not read file: {e}"


def generate_diff(old_content, new_content, file_path="file"):
    """Produce a readable unified diff between old and new content.
    Returns the diff as a string, or '(no changes)' if identical.
    """
    if old_content == new_content:
        return "(no changes)"

    diff_lines = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
    )
    return "".join(diff_lines) or "(no changes)"


def create_backup(file_path):
    """Create a backup copy of the file at file_path.rube.bak.
    Returns (True, backup_path) or (False, error_message).
    """
    valid, result = _validate_path(file_path)
    if not valid:
        return False, result

    abs_path = result
    if not os.path.isfile(abs_path):
        return False, f"Cannot backup — file not found: {file_path}"

    backup_path = abs_path + BACKUP_SUFFIX
    try:
        shutil.copy2(abs_path, backup_path)
        return True, backup_path
    except Exception as e:
        return False, f"Backup failed: {e}"


def write_file(file_path, new_content):
    """Write new content to a file. REFUSES if no .rube.bak backup exists.
    Returns (True, '') or (False, error_message).
    """
    valid, result = _validate_path(file_path)
    if not valid:
        return False, result

    abs_path = result
    backup_path = abs_path + BACKUP_SUFFIX

    # HARD SAFETY CHECK: backup must exist before any write
    if not os.path.isfile(backup_path):
        return False, "No backup found. Cannot write without a .rube.bak backup. Create one first."

    try:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True, ""
    except Exception as e:
        return False, f"Write failed: {e}"


def log_edit(edit_entry):
    """Append an edit record to the edit audit log (memory/edit_log.json).
    Thread-safe. Rotates at MAX_EDIT_LOG entries.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "file_path": edit_entry.get("file_path", ""),
        "action": edit_entry.get("action", ""),  # "approved" or "rejected"
        "reason": edit_entry.get("reason", ""),
        "source": edit_entry.get("source", ""),
        "diff_preview": edit_entry.get("diff", "")[:500],
    }
    with _edit_lock:
        try:
            log = []
            if os.path.exists(EDIT_LOG_PATH):
                with open(EDIT_LOG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    log = data if isinstance(data, list) else []
            log.append(entry)
            if len(log) > MAX_EDIT_LOG:
                log = log[-MAX_EDIT_LOG:]
            os.makedirs(os.path.dirname(EDIT_LOG_PATH), exist_ok=True)
            with open(EDIT_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Edit log error: {e}")
