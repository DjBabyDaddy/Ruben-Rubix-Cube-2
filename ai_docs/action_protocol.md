# How to Write a RUBE Action Module

## File Location
`actions/<your_module>.py`

## Handler Signature
```python
def your_handler(parameters, response, player, session_memory):
    """
    parameters:     dict — extracted by LLM from user speech
    response:       str  — LLM's acknowledgment text (already spoken by main loop)
    player:         RubeUI — the UI instance
    session_memory: TemporaryMemory — current session state
    """
```

## Required Imports
```python
from tts import edge_speak          # Voice output
from dotenv import load_dotenv      # For API keys
import os                           # For os.getenv()
```

## Speaking to the User
```python
edge_speak("Message here, boss.", player)
```

## Logging to the Terminal Panel
```python
player.write_log("RUBE: Your log message here")
```

## Loading API Keys
```python
load_dotenv()
api_key = os.getenv("YOUR_API_KEY")
if not api_key:
    edge_speak("I need the API key for this, boss.", player)
    return
```

## Wiring Into main.py
```python
# At the top of main.py:
from actions.your_module import your_handler

# In the intent routing chain:
elif intent == "your_intent":
    threading.Thread(
        target=_run_and_log,
        args=(your_handler, "your_intent", args),
        daemon=True
    ).start()
```

## Preflight Validation (Optional)
Add to `core/preflight.py` if your action can fail predictably:
```python
def _check_your_intent(params):
    if not params.get("required_field"):
        return False, "Missing required field."
    return True, ""

# Add to PREFLIGHT_CHECKS dict:
PREFLIGHT_CHECKS = {
    ...
    "your_intent": _check_your_intent,
}
```

## Common Patterns

### Subprocess with progress (for long-running tasks)
See `actions/code_agent.py` — uses `subprocess.Popen` + progress ticker thread.

### Multi-API routing
See `actions/web_search.py` — picks API based on query content (movies → TMDB, games → RAWG, etc.).

### File operations with safety
See `actions/file_editor.py` — backup before write, diff generation, approval queue.
