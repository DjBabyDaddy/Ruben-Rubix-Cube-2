import os
import json


PENDING_EDITS_PATH = "memory/pending_edits.json"


class TemporaryMemory:
    def __init__(self):
        self.history = []
        self.last_user_text = ""
        self.last_ai_response = ""
        self.current_question = None
        self.pending_intent = None
        self.parameters = {}
        self.last_search_query = None
        self.last_search_result = None
        self.pending_actions = []  # Queue for compound command decomposition
        self.pending_edits = self._load_pending_edits()  # Approval queue for file edits
        self.interaction_count = 0  # Tracks interactions for periodic reminders

    def set_last_user_text(self, text):
        self.last_user_text = text
        self.history.append(f"User: {text}")

    def get_last_user_text(self): return self.last_user_text

    def set_last_ai_response(self, text):
        self.last_ai_response = text
        self.history.append(f"RUBE: {text}")

    def get_last_ai_response(self): return self.last_ai_response

    def get_history_for_prompt(self): return "\n".join(self.history[-10:])
    def set_current_question(self, question): self.current_question = question
    def get_current_question(self): return self.current_question
    def clear_current_question(self): self.current_question = None
    def set_pending_intent(self, intent): self.pending_intent = intent
    
    def update_parameters(self, params):
        for k, v in params.items(): self.parameters[k] = v
        
    def get_parameter(self, key): return self.parameters.get(key)
    def get_parameters(self): return self.parameters

    def set_last_search(self, query, result):
        self.last_search_query = query
        self.last_search_result = result

    def get_last_search(self):
        return self.last_search_query, self.last_search_result

    def push_pending_action(self, action: dict):
        """Queue a deferred action from compound command decomposition."""
        self.pending_actions.append(action)

    def pop_pending_action(self):
        """Dequeue the next pending action, or None if empty."""
        return self.pending_actions.pop(0) if self.pending_actions else None

    def has_pending_actions(self) -> bool:
        return len(self.pending_actions) > 0

    # --- Pending edits (approval queue for file changes) ---

    def _load_pending_edits(self):
        """Load pending edits from disk on startup. Returns empty list on any error."""
        try:
            if os.path.exists(PENDING_EDITS_PATH):
                with open(PENDING_EDITS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            pass
        return []

    def _save_pending_edits(self):
        """Flush pending edits to disk so they survive crashes."""
        try:
            os.makedirs(os.path.dirname(PENDING_EDITS_PATH), exist_ok=True)
            with open(PENDING_EDITS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.pending_edits, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save pending edits: {e}")

    def add_pending_edit(self, edit):
        """Add a proposed edit to the approval queue and persist to disk."""
        self.pending_edits.append(edit)
        self._save_pending_edits()

    def get_pending_edits(self):
        """Return all pending edits."""
        return list(self.pending_edits)

    def remove_pending_edit(self, edit_id):
        """Remove and return the edit with the given ID, or None if not found."""
        for i, edit in enumerate(self.pending_edits):
            if edit.get("id") == edit_id:
                removed = self.pending_edits.pop(i)
                self._save_pending_edits()
                return removed
        return None

    # --- Interaction counter (for periodic reminders) ---

    def increment_interaction(self):
        """Increment the interaction counter by 1."""
        self.interaction_count += 1

    def get_interaction_count(self):
        """Return the current interaction count."""
        return self.interaction_count

    def reset_interaction_count(self):
        """Reset the interaction counter to 0."""
        self.interaction_count = 0

    def reset(self):
        self.current_question = None
        self.pending_intent = None
        self.parameters = {}
        self.last_search_query = None
        self.last_search_result = None
        self.pending_actions = []
        # NOTE: pending_edits and interaction_count are NOT cleared on reset.
        # "stop"/"cancel" interrupts the current action, not the edit review queue.