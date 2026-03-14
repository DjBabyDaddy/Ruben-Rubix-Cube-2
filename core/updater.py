"""RUBE Secure OTA Update System.

Checks for updates from the update server, verifies signatures,
backs up the current installation, and applies updates with auto-rollback.

Usage (in main.py boot sequence):
    threading.Thread(target=check_and_apply_updates, daemon=True).start()
"""

import hashlib
import hmac
import json
import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / ".rube_version"
BACKUP_DIR = PROJECT_ROOT / ".rube_backup"
UPDATE_KEY_FILE = PROJECT_ROOT / ".rube_update_key"

# Files and directories that should NEVER be overwritten by updates
PROTECTED_PATHS = {".env", "memory", ".rube_backup", ".rube_version", ".rube_update_key"}


def get_current_version():
    """Read the current RUBE version from .rube_version."""
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "0.0.0"


def get_instance_id():
    """Read the RUBE_INSTANCE_ID from environment."""
    return os.getenv("RUBE_INSTANCE_ID", "")


def _get_update_server():
    return os.getenv("RUBE_UPDATE_SERVER", "").rstrip("/")


def _get_signing_key():
    """Read the HMAC signing key for signature verification."""
    if UPDATE_KEY_FILE.exists():
        return UPDATE_KEY_FILE.read_text().strip().encode()
    return None


def check_for_updates():
    """Check the update server for a newer version.

    Returns dict with {version, changelog, download_url, signature} or None.
    """
    server = _get_update_server()
    instance_id = get_instance_id()
    if not server or not instance_id:
        return None

    try:
        import requests
        resp = requests.get(
            f"{server}/api/check-update",
            params={
                "instance_id": instance_id,
                "current_version": get_current_version(),
            },
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("update_available"):
                return data
    except Exception as e:
        print(f"⚠️ Update check failed: {e}")
    return None


def download_update(url):
    """Download an update package. Returns bytes or None."""
    try:
        import requests
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"⚠️ Update download failed: {e}")
        return None


def verify_signature(data, signature):
    """Verify the HMAC-SHA256 signature of an update package."""
    key = _get_signing_key()
    if not key:
        print("⚠️ No update signing key found. Cannot verify update.")
        return False

    expected = hmac.new(key, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def backup_current():
    """Backup critical project files to .rube_backup/."""
    try:
        if BACKUP_DIR.exists():
            shutil.rmtree(BACKUP_DIR)
        BACKUP_DIR.mkdir(parents=True)

        # Backup Python files and core/ directory
        for pattern in ["*.py", "core/*.py", "actions/*.py", "memory/*.py"]:
            for src in PROJECT_ROOT.glob(pattern):
                rel = src.relative_to(PROJECT_ROOT)
                dst = BACKUP_DIR / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Backup version file
        if VERSION_FILE.exists():
            shutil.copy2(VERSION_FILE, BACKUP_DIR / ".rube_version")

        print("✅ Backup created before update.")
        return True
    except Exception as e:
        print(f"⚠️ Backup failed: {e}")
        return False


def apply_update(package_data):
    """Extract zip update package and apply to project.

    Never overwrites .env, memory/, or other protected paths.
    """
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_path = os.path.join(tmp_dir, "update.zip")
            with open(zip_path, "wb") as f:
                f.write(package_data)

            with zipfile.ZipFile(zip_path, "r") as zf:
                for member in zf.namelist():
                    # Skip protected paths
                    top_level = member.split("/")[0] if "/" in member else member
                    if top_level in PROTECTED_PATHS:
                        continue
                    # Skip directories
                    if member.endswith("/"):
                        continue

                    target = PROJECT_ROOT / member
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(target, "wb") as dst:
                        dst.write(src.read())

        print("✅ Update files extracted.")
        return True
    except Exception as e:
        print(f"⚠️ Update extraction failed: {e}")
        return False


def rollback():
    """Restore files from .rube_backup/."""
    if not BACKUP_DIR.exists():
        print("⚠️ No backup found for rollback.")
        return False

    try:
        for src in BACKUP_DIR.rglob("*"):
            if src.is_file():
                rel = src.relative_to(BACKUP_DIR)
                dst = PROJECT_ROOT / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        print("🔄 Rollback completed from backup.")
        return True
    except Exception as e:
        print(f"⚠️ Rollback failed: {e}")
        return False


def _boot_test():
    """Quick sanity check that the updated code can import."""
    try:
        import importlib
        # Try importing the main modules
        for mod_name in ["llm", "tts", "core.preflight"]:
            importlib.import_module(mod_name)
        return True
    except Exception as e:
        print(f"⚠️ Boot test failed after update: {e}")
        return False


def check_and_apply_updates():
    """Main update flow: check → download → verify → backup → apply → test → rollback on failure."""
    if os.getenv("RUBE_AUTO_UPDATE", "true").lower() != "true":
        return

    update_info = check_for_updates()
    if not update_info:
        return

    version = update_info.get("version", "unknown")
    print(f"🔄 Update available: v{version}")
    print(f"   Changelog: {update_info.get('changelog', 'No changelog')}")

    # Download
    package_data = download_update(update_info.get("download_url", ""))
    if not package_data:
        return

    # Verify signature
    signature = update_info.get("signature", "")
    if not verify_signature(package_data, signature):
        print("⚠️ Update signature verification FAILED. Update rejected.")
        return

    # Backup
    if not backup_current():
        print("⚠️ Could not create backup. Update aborted.")
        return

    # Apply
    if not apply_update(package_data):
        print("⚠️ Update application failed. Rolling back...")
        rollback()
        return

    # Boot test
    if not _boot_test():
        print("⚠️ Update broke imports. Rolling back...")
        rollback()
        return

    # Success — update version file
    VERSION_FILE.write_text(version)
    print(f"✅ RUBE updated to v{version}")
