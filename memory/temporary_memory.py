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

    def reset(self):
        self.current_question = None
        self.pending_intent = None
        self.parameters = {}
        self.last_search_query = None
        self.last_search_result = None