"""RUBE First-Time Setup Wizard.

Interactive terminal wizard that configures .env with all required
API keys and feature flags. Run once before first `python main.py`.

Usage:
    python setup_wizard.py

Or called from main.py on first boot:
    from setup_wizard import run_wizard
    run_wizard()
"""

import os
import uuid


def _input_key(prompt, required=False):
    """Prompt for an API key. Returns the key or empty string."""
    while True:
        val = input(f"  {prompt}: ").strip()
        if val or not required:
            return val
        print("  This field is required. Please enter a value.")


def _choice(prompt, options, default=1):
    """Present numbered options and return the selection number."""
    for i, opt in enumerate(options, 1):
        marker = " (default)" if i == default else ""
        print(f"  [{i}] {opt}{marker}")
    while True:
        raw = input(f"  > ").strip()
        if not raw:
            return default
        try:
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice
        except ValueError:
            pass
        print(f"  Please enter a number between 1 and {len(options)}")


def _yn(prompt, default=True):
    """Yes/No prompt. Returns boolean."""
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"  {prompt} {suffix}: ").strip().lower()
    if not raw:
        return default
    return raw.startswith("y")


def run_wizard():
    """Run the interactive setup wizard. Creates .env file."""
    print()
    print("=" * 50)
    print("  RUBE First-Time Setup")
    print("=" * 50)
    print()

    env_lines = []

    # --- Step 1: Required API Keys ---
    print("Step 1 of 4: Required API Keys")
    print("-" * 40)
    print()

    anthropic_key = _input_key("Anthropic API Key (powers RUBE's brain)", required=True)
    env_lines.append(f"ANTHROPIC_API_KEY={anthropic_key}")
    print()

    groq_key = _input_key("Groq API Key (free at groq.com — powers speed layer)", required=True)
    env_lines.append(f"GROQ_API_KEY={groq_key}")
    print()

    # --- Step 2: Voice Configuration ---
    print("Step 2 of 4: Voice Configuration")
    print("-" * 40)
    print()

    print("  Text-to-Speech Provider:")
    tts_choice = _choice("", [
        "Cartesia Sonic (recommended — fastest, best value)",
        "ElevenLabs (premium voice quality)",
        "Edge TTS (free, no API key needed)",
    ], default=1)

    tts_providers = {1: "cartesia", 2: "elevenlabs", 3: "edge_tts"}
    tts_provider = tts_providers[tts_choice]
    env_lines.append(f"TTS_PROVIDER={tts_provider}")

    if tts_choice in (1, 2):
        tts_key = _input_key(f"{'Cartesia' if tts_choice == 1 else 'ElevenLabs'} API Key", required=True)
        env_lines.append(f"TTS_API_KEY={tts_key}")
        voice_id = _input_key("Voice ID (press Enter for default)")
        env_lines.append(f"TTS_VOICE_ID={voice_id or 'default'}")
    print()

    print("  Speech-to-Text Provider:")
    stt_choice = _choice("", [
        "Deepgram (recommended — fastest streaming)",
        "Skip (keyboard-only mode)",
    ], default=1)

    stt_providers = {1: "deepgram", 2: "disabled"}
    stt_provider = stt_providers[stt_choice]
    env_lines.append(f"STT_PROVIDER={stt_provider}")

    if stt_choice == 1:
        stt_key = _input_key("Deepgram API Key", required=True)
        env_lines.append(f"STT_API_KEY={stt_key}")
    print()

    # --- Step 3: Optional Features ---
    print("Step 3 of 4: Optional Features")
    print("-" * 40)
    print()

    desktop = _yn("Enable desktop automation (app control, shortcuts)?", default=True)
    env_lines.append(f"FEATURE_DESKTOP_AUTOMATION={'true' if desktop else 'false'}")

    broadcast = _yn("Enable broadcast control (OBS/Streamlabs)?", default=False)
    env_lines.append(f"FEATURE_BROADCAST_CONTROL={'true' if broadcast else 'false'}")

    facial = _yn("Enable facial recognition?", default=False)
    env_lines.append(f"FEATURE_FACIAL_RECOGNITION={'true' if facial else 'false'}")

    social = _yn("Enable social media posting via n8n?", default=False)
    env_lines.append(f"FEATURE_SOCIAL_MEDIA={'true' if social else 'false'}")

    if social:
        webhook = _input_key("n8n Webhook URL")
        if webhook:
            env_lines.append(f"N8N_WEBHOOK_URL={webhook}")
    print()

    # --- Step 4: Identity ---
    print("Step 4 of 4: Identity")
    print("-" * 40)
    print()

    user_name = _input_key("What should RUBE call you? (default: Boss)")
    if not user_name:
        user_name = "Boss"
    env_lines.append(f"RUBE_USER_NAME={user_name}")

    # Generate instance ID for remote updates
    instance_id = uuid.uuid4().hex[:16]
    env_lines.append(f"RUBE_INSTANCE_ID={instance_id}")
    env_lines.append("RUBE_UPDATE_SERVER=")
    env_lines.append("RUBE_AUTO_UPDATE=true")

    # --- Write .env ---
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path, "w") as f:
        f.write("\n".join(env_lines) + "\n")

    print()
    print("=" * 50)
    print(f"  Configuration saved to .env")
    print(f"  Instance ID: {instance_id}")
    print()
    print(f"  Run `python main.py` to start RUBE!")
    print("=" * 50)
    print()


def main():
    run_wizard()


if __name__ == "__main__":
    main()
