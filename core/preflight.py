"""Pre-flight validation for RUBE action modules.

Each checker takes (intent, parameters) and returns (ok: bool, reason: str).
If ok is False, reason is spoken to the user and the action is skipped.
Fail-open design: if a checker itself crashes, the action proceeds anyway.
"""
import os
import psutil


def _check_whatsapp(intent, params):
    receiver = params.get("receiver_nickname", "").strip()
    if not receiver:
        return False, "Boss, I need to know who to message on WhatsApp."
    return True, ""


def _check_email(intent, params):
    target = params.get("receiver_email", "").strip()
    if not target:
        return False, "Boss, I need a recipient for the email."
    body = params.get("message_text", "").strip()
    if not body:
        return False, "Boss, the email has no message body."
    return True, ""


def _check_broadcast(intent, params):
    try:
        processes = [p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info['name']]
        has_obs = any("obs64" in p or "obs32" in p for p in processes)
        has_sl = any("streamlabs" in p for p in processes)
        if not has_obs and not has_sl:
            return False, "Boss, neither OBS nor Streamlabs is running. Launch one first."
    except Exception:
        pass  # fail-open
    return True, ""


def _check_file_path(intent, params):
    path = params.get("file_path", "").strip().replace('"', '')
    if path and not os.path.exists(path):
        return False, "Boss, I can't find the file at that path."
    return True, ""


def _check_social_post(intent, params):
    webhook = os.environ.get("N8N_WEBHOOK_URL")
    if not webhook:
        return False, "Boss, the n8n webhook is not configured. Social posting is offline."
    content = params.get("post_content", "").strip()
    if not content:
        return False, "Boss, I need post content to create a campaign."
    return True, ""


def _check_file_edit(intent, params):
    file_path = params.get("file_path", "").strip()
    if not file_path:
        return False, "Boss, I need to know which file to edit."
    reason = params.get("reason", "").strip()
    if not reason:
        return False, "Boss, I need a reason for the edit so my subagent knows what to fix."
    return True, ""


def _check_edit_id(intent, params):
    edit_id = str(params.get("edit_id", "")).strip()
    if not edit_id:
        return False, "Boss, I need the edit ID. Say 'show pending edits' to see available IDs."
    return True, ""


# Registry: intent -> checker function
PREFLIGHT_CHECKS = {
    "whatsapp_message": _check_whatsapp,
    "email_message": _check_email,
    "broadcast_control": _check_broadcast,
    "import_contacts": _check_file_path,
    "generate_social_post": _check_social_post,
    "request_file_edit": _check_file_edit,
    "approve_edit": _check_edit_id,
    "reject_edit": _check_edit_id,
}


def run_preflight(intent: str, parameters: dict) -> tuple:
    """Run pre-flight check for the given intent.
    Returns (ok: bool, reason: str). If no checker registered, returns (True, "")."""
    checker = PREFLIGHT_CHECKS.get(intent)
    if not checker:
        return True, ""
    try:
        return checker(intent, parameters)
    except Exception:
        return True, ""  # fail-open: don't block action on checker bugs
