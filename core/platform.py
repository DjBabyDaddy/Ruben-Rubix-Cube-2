"""Platform abstraction layer for desktop automation.

All action modules import from here instead of directly from pyautogui/pygetwindow.
This allows RUBE to run on any OS with graceful degradation.
"""
import platform

PLATFORM = platform.system()  # "Windows", "Darwin", "Linux"

# --- Check availability ---

DESKTOP_AUTOMATION_AVAILABLE = True
try:
    import pyautogui
except ImportError:
    DESKTOP_AUTOMATION_AVAILABLE = False
    pyautogui = None
    print("ℹ️ pyautogui not installed. Desktop automation features disabled.")

WINDOW_MANAGEMENT_AVAILABLE = True
try:
    if PLATFORM == "Windows":
        import pygetwindow as gw
    else:
        gw = None
        WINDOW_MANAGEMENT_AVAILABLE = False
except ImportError:
    gw = None
    WINDOW_MANAGEMENT_AVAILABLE = False


# --- Window management ---

def get_window_by_title(title_substring):
    """Find a window by partial title match. Returns window object or None."""
    if not WINDOW_MANAGEMENT_AVAILABLE or gw is None:
        return None
    try:
        windows = gw.getWindowsWithTitle(title_substring)
        return windows[0] if windows else None
    except Exception:
        return None


def focus_window(window):
    """Bring a window to the foreground."""
    if window is None:
        return False
    try:
        if hasattr(window, 'activate'):
            window.activate()
            return True
    except Exception:
        pass
    return False


def get_running_processes():
    """Return list of running process names (lowercase)."""
    try:
        import psutil
        return [p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info['name']]
    except ImportError:
        print("⚠️ psutil not installed.")
        return []
    except Exception:
        return []


# --- Keyboard/mouse automation ---

def type_text(text, interval=0.02):
    """Type text with optional keystroke interval."""
    if not DESKTOP_AUTOMATION_AVAILABLE:
        print("⚠️ pyautogui not installed. Cannot type text.")
        return
    if all(ord(c) < 128 for c in text):
        pyautogui.typewrite(text, interval=interval)
    else:
        pyautogui.write(text)


def press_hotkey(*keys):
    """Press a keyboard shortcut."""
    if not DESKTOP_AUTOMATION_AVAILABLE:
        print("⚠️ pyautogui not installed. Keyboard shortcuts disabled.")
        return
    pyautogui.hotkey(*keys)


def click(x=None, y=None):
    """Click at coordinates or current position."""
    if not DESKTOP_AUTOMATION_AVAILABLE:
        return
    pyautogui.click(x, y)


def move_to(x, y, duration=0.2):
    """Move mouse to coordinates."""
    if not DESKTOP_AUTOMATION_AVAILABLE:
        return
    pyautogui.moveTo(x, y, duration=duration)


def screenshot():
    """Take a screenshot. Returns PIL Image or None."""
    try:
        from PIL import ImageGrab
        return ImageGrab.grab()
    except Exception:
        return None
