import os
import re
import difflib
from memory.memory_manager import load_memory, save_memory
from tts import edge_speak

REQUIRED_SAVE_PARAMS = ["contact_name"]


def _get_contacts() -> dict:
    """Load the contacts dict from memory. Returns {nickname: {phone, email, name}}."""
    memory = load_memory()
    contacts = memory.get("preferences", {}).get("contacts", {}).get("value", {})
    if isinstance(contacts, dict):
        return contacts
    return {}


def _get_legacy_nicknames() -> dict:
    """Load old-format nicknames for backwards compatibility."""
    memory = load_memory()
    return memory.get("preferences", {}).get("nicknames", {}).get("value", {})


def _save_contacts(contacts: dict):
    """Persist contacts dict to memory."""
    memory = load_memory()
    if "preferences" not in memory:
        memory["preferences"] = {}
    memory["preferences"]["contacts"] = {"value": contacts}
    save_memory(memory)


def _migrate_legacy_contacts():
    """One-time migration from old nicknames format to new contacts format."""
    contacts = _get_contacts()
    if contacts:
        return  # already migrated or has new-format data

    legacy = _get_legacy_nicknames()
    if not legacy:
        return

    migrated = {}
    for nickname, phone in legacy.items():
        nick_lower = nickname.lower()
        if nick_lower not in migrated:
            migrated[nick_lower] = {"phone": str(phone), "email": "", "name": nickname.title()}

    if migrated:
        _save_contacts(migrated)
        print(f"📇 Migrated {len(migrated)} legacy contacts to new format.")


def lookup_contact(name: str) -> dict | None:
    """Look up a contact by name. Returns {phone, email, name} or None.

    Search priority: exact match -> substring match -> fuzzy match.
    Checks new contacts format first, then falls back to legacy nicknames.
    """
    if not name:
        return None

    search = name.lower().strip()

    # Check new contacts format
    contacts = _get_contacts()
    if contacts:
        # Exact match
        if search in contacts:
            return contacts[search]

        # Substring match
        for nick, data in contacts.items():
            if search in nick.lower():
                return data

        # Check against full names
        for nick, data in contacts.items():
            full_name = data.get("name", "").lower()
            if search in full_name:
                return data

        # Fuzzy match
        all_names = list(contacts.keys())
        matches = difflib.get_close_matches(search, all_names, n=1, cutoff=0.6)
        if matches:
            return contacts[matches[0]]

    # Fall back to legacy nicknames
    legacy = _get_legacy_nicknames()
    if legacy:
        for nick, phone in legacy.items():
            if search in nick.lower():
                return {"phone": str(phone), "email": "", "name": nick.title()}

    return None


def _parse_vcf(file_path: str) -> list:
    """Parse a .vcf (vCard) file. Returns list of {name, phone, email} dicts."""
    results = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Split into individual vCards
    cards = re.split(r'(?=BEGIN:VCARD)', content)

    for card in cards:
        if 'BEGIN:VCARD' not in card:
            continue

        name = ""
        phone = ""
        email = ""

        # Extract full name (FN field preferred, fall back to N field)
        fn_match = re.search(r'FN[;:](.+)', card)
        if fn_match:
            name = fn_match.group(1).strip()
        else:
            n_match = re.search(r'^N[;:]([^;]*);([^;]*)', card, re.MULTILINE)
            if n_match:
                last = n_match.group(1).strip()
                first = n_match.group(2).strip()
                name = f"{first} {last}".strip()

        # Extract phone (first TEL field)
        tel_match = re.search(r'TEL[^:]*:(.+)', card)
        if tel_match:
            raw_phone = tel_match.group(1).strip()
            # Clean phone: keep only digits and leading +
            phone = re.sub(r'[^\d+]', '', raw_phone)

        # Extract email (first EMAIL field)
        email_match = re.search(r'EMAIL[^:]*:(.+)', card)
        if email_match:
            email = email_match.group(1).strip()

        if name:
            results.append({"name": name, "phone": phone, "email": email})

    return results


def _generate_nickname(name: str, existing: dict) -> str:
    """Generate a unique nickname from a full name."""
    parts = name.lower().split()
    if not parts:
        return name.lower()

    # Try first name
    nick = parts[0]
    if nick not in existing:
        return nick

    # Try first name + last initial
    if len(parts) > 1:
        nick = f"{parts[0]}_{parts[-1][0]}"
        if nick not in existing:
            return nick

    # Append number
    counter = 2
    base = parts[0]
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def import_contacts(parameters: dict, response: str, player, session_memory):
    """Import contacts from a VCF file dropped into the terminal."""
    file_path = parameters.get("file_path", "").strip().replace('"', '')

    if not file_path:
        edge_speak("Boss, I need a contacts file. Drop a .vcf file into my terminal.", player)
        return

    if not os.path.exists(file_path):
        edge_speak("Boss, that file doesn't exist. Check the path and try again.", player)
        return

    ext = file_path.lower().split('.')[-1]
    if ext != 'vcf':
        edge_speak("Boss, I can only import .vcf contact files right now.", player)
        return

    try:
        parsed = _parse_vcf(file_path)
    except Exception as e:
        print(f"VCF Parse Error: {e}")
        edge_speak("Boss, I couldn't read that contacts file.", player)
        return

    if not parsed:
        edge_speak("Boss, that file didn't contain any contacts I could read.", player)
        return

    contacts = _get_contacts()
    imported = 0

    for entry in parsed:
        name = entry["name"]
        if not name:
            continue

        nick = _generate_nickname(name, contacts)
        contacts[nick] = {
            "phone": entry.get("phone", ""),
            "email": entry.get("email", ""),
            "name": name
        }
        imported += 1

    _save_contacts(contacts)

    msg = f"Contacts imported. {imported} entries loaded into my memory matrix, boss."
    print(f"📇 Imported {imported} contacts from {file_path}")
    player.write_log(f"RUBE: {msg}")
    edge_speak(msg, player)


def save_contact(parameters: dict, response: str, player, session_memory):
    """Multi-turn voice flow to save a new contact."""
    if parameters:
        session_memory.update_parameters(parameters)

    # Require contact name
    contact_name = session_memory.get_parameter("contact_name")
    if not contact_name:
        session_memory.set_current_question("contact_name")
        edge_speak("Boss, what's the contact's name?", player)
        return

    # Require at least phone or email
    phone = session_memory.get_parameter("phone_number")
    email = session_memory.get_parameter("email")

    if not phone and not email:
        session_memory.set_current_question("phone_number")
        edge_speak("What's their phone number?", player)
        return

    # Save the contact
    contacts = _get_contacts()
    nick = _generate_nickname(contact_name.strip(), contacts)

    contacts[nick] = {
        "phone": (phone or "").strip(),
        "email": (email or "").strip(),
        "name": contact_name.strip().title()
    }

    _save_contacts(contacts)
    session_memory.reset()

    msg = f"{contact_name.strip().title()} has been locked into my contact matrix, boss."
    print(f"📇 Contact saved: {nick} -> {contacts[nick]}")
    player.write_log(f"RUBE: {msg}")
    edge_speak(msg, player)


# Run migration on import
_migrate_legacy_contacts()
