# RUBE Common Code Patterns

## Voice Output
```python
from tts import edge_speak
edge_speak("Message to user", player)
```

## Terminal Log
```python
player.write_log("RUBE: Your message here")
# "RUBE:" prefix renders in magenta, "You:" in cyan
```

## Environment Variables
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("SERVICE_API_KEY")
if not api_key:
    edge_speak("I need the API key for this.", player)
    return
```

## Subprocess with LM Studio
```python
import subprocess, os
from dotenv import load_dotenv

load_dotenv()
env = {
    **os.environ,
    "ANTHROPIC_BASE_URL": os.getenv("LM_STUDIO_URL", "http://localhost:1234"),
    "ANTHROPIC_AUTH_TOKEN": os.getenv("LM_STUDIO_TOKEN", "lmstudio"),
    "ANTHROPIC_API_KEY": os.getenv("LM_STUDIO_TOKEN", "lmstudio"),
}
proc = subprocess.Popen(
    ["claude", "--model", os.getenv("LM_STUDIO_MODEL"), "--print", "-p", prompt],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
)
stdout, stderr = proc.communicate(timeout=300)
```

## Progress Ticker (for long tasks)
```python
import threading, time

def _progress_ticker(player, stop_event, start_time):
    while not stop_event.is_set():
        stop_event.wait(10)
        if stop_event.is_set(): break
        elapsed = int(time.time() - start_time)
        player.write_log(f"RUBE: Working... {elapsed}s elapsed")

stop = threading.Event()
ticker = threading.Thread(target=_progress_ticker, args=(player, stop, time.time()), daemon=True)
ticker.start()
# ... do work ...
stop.set()
```

## Reachability Check
```python
import requests

def _is_online(url, timeout=3):
    try:
        return requests.get(f"{url}/v1/models", timeout=timeout).status_code == 200
    except Exception:
        return False
```

## Thread Dispatch (from main.py)
```python
threading.Thread(
    target=_run_and_log,
    args=(your_handler, "your_intent", args),
    daemon=True
).start()
```
