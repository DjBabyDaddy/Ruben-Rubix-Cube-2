"""
core/groq_brain.py — Groq cloud API wrapper for RUBE.

Replaces LM Studio with Groq's hosted LLMs.
Primary model:  llama-3.3-70b-versatile  (fast, free tier)
Fallback model: llama-3.1-8b-instant     (when 70B is rate-limited)

Usage:
    from core.groq_brain import groq_completion, groq_completion_stream

    result = groq_completion("Summarize this code", system_prompt="You are a helpful assistant.")
    for chunk in groq_completion_stream("Explain quicksort"):
        print(chunk, end="", flush=True)
"""

import os
import logging

try:
    from groq import Groq, RateLimitError, APIError
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None
    RateLimitError = None
    APIError = None

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

_current_model: str = PRIMARY_MODEL
_client: "Groq | None" = None


# ---------------------------------------------------------------------------
# Client / state helpers
# ---------------------------------------------------------------------------

def get_groq_client():
    """Lazy singleton initialisation of the Groq client."""
    global _client
    if not GROQ_AVAILABLE:
        logger.error("groq package is not installed. Run: pip install groq")
        return None
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY environment variable is not set.")
            return None
        _client = Groq(api_key=api_key)
    return _client


def get_current_model() -> str:
    """Return whichever model is currently active."""
    return _current_model


def check_groq_tier_reset():
    """Reset the active model back to the primary 70B.

    Call this periodically (e.g. every few minutes) so that RUBE
    automatically tries the higher-quality model again after a
    rate-limit window expires.
    """
    global _current_model
    if _current_model != PRIMARY_MODEL:
        logger.info("Resetting Groq model back to primary: %s", PRIMARY_MODEL)
        _current_model = PRIMARY_MODEL


# ---------------------------------------------------------------------------
# Internal: model fallback logic
# ---------------------------------------------------------------------------

def _switch_to_fallback():
    """Downgrade to the smaller model after a rate-limit hit."""
    global _current_model
    if _current_model != FALLBACK_MODEL:
        print(f"\u26a0\ufe0f Groq 70B rate limited. Switching to 8B fallback.")
        logger.warning("Groq 70B rate limited — falling back to %s", FALLBACK_MODEL)
        _current_model = FALLBACK_MODEL


def _build_messages(prompt: str, system_prompt: str | None = None) -> list[dict]:
    """Build the messages list for a chat completion request."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages


# ---------------------------------------------------------------------------
# Synchronous completion
# ---------------------------------------------------------------------------

def groq_completion(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> str | None:
    """Send a single-shot completion to Groq and return the response text.

    Automatically falls back from the 70B model to the 8B model on
    rate-limit errors.  Returns ``None`` if both models fail or the
    client cannot be initialised.
    """
    client = get_groq_client()
    if client is None:
        return None

    messages = _build_messages(prompt, system_prompt)

    # Try up to two models: current, then fallback (if different).
    models_to_try = [_current_model]
    if _current_model == PRIMARY_MODEL:
        models_to_try.append(FALLBACK_MODEL)

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as exc:
            if _is_rate_limit(exc):
                _switch_to_fallback()
                continue
            logger.error("Groq API error (model=%s): %s", model, exc)
            return None

    # Both models rate-limited.
    logger.error("All Groq models rate-limited. Returning None.")
    return None


# ---------------------------------------------------------------------------
# Streaming completion
# ---------------------------------------------------------------------------

def groq_completion_stream(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
):
    """Stream a completion from Groq, yielding text chunks.

    Falls back from 70B to 8B on rate-limit errors, same as the
    non-streaming variant.  Yields nothing if both models fail.
    """
    client = get_groq_client()
    if client is None:
        return

    messages = _build_messages(prompt, system_prompt)

    models_to_try = [_current_model]
    if _current_model == PRIMARY_MODEL:
        models_to_try.append(FALLBACK_MODEL)

    for model in models_to_try:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
            return  # Success — stop trying models.
        except Exception as exc:
            if _is_rate_limit(exc):
                _switch_to_fallback()
                continue
            logger.error("Groq streaming error (model=%s): %s", model, exc)
            return

    logger.error("All Groq models rate-limited (streaming). Yielding nothing.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_rate_limit(exc: Exception) -> bool:
    """Return True if the exception represents a rate-limit / 429 error."""
    if GROQ_AVAILABLE and RateLimitError and isinstance(exc, RateLimitError):
        return True
    # Some SDK versions surface 429 via a generic APIError.
    if GROQ_AVAILABLE and APIError and isinstance(exc, APIError):
        status = getattr(exc, "status_code", None) or getattr(exc, "http_status", None)
        if status == 429:
            return True
    return False
