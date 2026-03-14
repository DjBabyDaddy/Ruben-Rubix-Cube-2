"""STT Provider Abstraction Layer for RUBE.

Supports multiple STT backends with automatic fallback:
  - DeepgramSTTProvider  (primary — Deepgram Nova-3 streaming)
  - KeyboardOnlyProvider (fallback — no voice input)

Usage:
    provider = get_stt_provider()
    provider.start()
    text = provider.get_transcript(timeout=10.0)
    provider.stop()
"""

import os
import queue
import threading
from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE = 16000


class DeepgramSTTProvider:
    """Primary STT provider using Deepgram Nova-3 via WebSocket streaming."""

    def __init__(self):
        self.api_key = os.getenv("STT_API_KEY")
        if not self.api_key:
            raise ValueError("STT_API_KEY environment variable is not set")

        try:
            from deepgram import DeepgramClient
        except ImportError:
            raise ImportError(
                "deepgram-sdk package is not installed. Run: pip install deepgram-sdk"
            )

        self._client = DeepgramClient(self.api_key)
        self._connection = None
        self._audio_stream = None
        self._transcript_queue = queue.Queue()
        self._partial_text = ""
        self._partial_lock = threading.Lock()
        self._running = False
        self._audio_queue = queue.Queue()

    def start(self):
        """Open the Deepgram WebSocket connection and start streaming mic audio."""
        if self._running:
            return

        from deepgram import LiveTranscriptionEvents, LiveOptions
        import sounddevice as sd

        options = LiveOptions(
            model="nova-3",
            language="en",
            smart_format=True,
            interim_results=True,
            encoding="linear16",
            sample_rate=SAMPLE_RATE,
            channels=1,
            keywords=["Ruben:2", "Reuben:2", "Rubin:2"],
        )

        self._connection = self._client.listen.live.v("1")

        # Bind event handlers
        self._connection.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
        self._connection.on(LiveTranscriptionEvents.Error, self._on_error)

        if not self._connection.start(options):
            print("⚠️ Deepgram: failed to start WebSocket connection")
            return

        self._running = True

        # Start mic stream
        def audio_callback(indata, frames, time_info, status):
            if self._running and self._connection:
                self._connection.send(bytes(indata))

        try:
            device_info = sd.query_devices(kind='input')
            print(f"🎤 Hardware matrix locked onto: {device_info['name']}")
            self._audio_stream = sd.RawInputStream(
                samplerate=SAMPLE_RATE, blocksize=1280, device=None,
                dtype='int16', channels=1, callback=audio_callback
            )
            self._audio_stream.start()
        except Exception as e:
            print(f"⚠️ Deepgram: microphone error: {e}")
            self._running = False
            return

        print("✅ Deepgram Nova-3 streaming STT online.")

    def stop(self):
        """Close the connection and stop streaming."""
        self._running = False
        if self._audio_stream:
            try:
                self._audio_stream.stop()
                self._audio_stream.close()
            except Exception:
                pass
            self._audio_stream = None
        if self._connection:
            try:
                self._connection.finish()
            except Exception:
                pass
            self._connection = None

    def _on_transcript(self, _self, result, **kwargs):
        """Callback for Deepgram transcript events."""
        try:
            transcript = result.channel.alternatives[0].transcript
            if not transcript:
                return

            is_final = result.is_final

            if is_final:
                self._transcript_queue.put(transcript)
                with self._partial_lock:
                    self._partial_text = ""
            else:
                with self._partial_lock:
                    self._partial_text = transcript
        except Exception as e:
            print(f"⚠️ Deepgram transcript parse error: {e}")

    def _on_error(self, _self, error, **kwargs):
        """Callback for Deepgram errors."""
        print(f"⚠️ Deepgram error: {error}")

    def get_transcript(self, timeout=10.0):
        """Block until a final transcript is available, or timeout."""
        try:
            return self._transcript_queue.get(timeout=timeout)
        except queue.Empty:
            return ""

    def get_partial(self):
        """Return the latest interim/partial transcript."""
        with self._partial_lock:
            return self._partial_text

    def reset(self):
        """Clear any buffered transcripts."""
        while not self._transcript_queue.empty():
            try:
                self._transcript_queue.get_nowait()
            except queue.Empty:
                break
        with self._partial_lock:
            self._partial_text = ""

    @property
    def is_running(self):
        return self._running


class KeyboardOnlyProvider:
    """Fallback provider when STT is disabled — no voice input."""

    def start(self):
        print("ℹ️ STT disabled — keyboard-only mode active.")

    def stop(self):
        pass

    def get_transcript(self, timeout=10.0):
        return ""

    def get_partial(self):
        return ""

    def reset(self):
        pass

    @property
    def is_running(self):
        return False


def get_stt_provider():
    """Return an STT provider based on the STT_PROVIDER env var.

    Supported: deepgram, disabled
    Falls back to KeyboardOnlyProvider on any failure.
    """
    provider_name = os.getenv("STT_PROVIDER", "deepgram").lower().strip()

    if provider_name == "disabled":
        return KeyboardOnlyProvider()

    if provider_name == "deepgram":
        try:
            return DeepgramSTTProvider()
        except Exception as e:
            print(f"⚠️ Failed to initialize Deepgram STT: {e}")
            print("⚠️ Falling back to keyboard-only mode.")
            return KeyboardOnlyProvider()

    print(f"⚠️ Unknown STT provider '{provider_name}'. Using keyboard-only mode.")
    return KeyboardOnlyProvider()
