"""
TTS Provider Abstraction Layer for RUBE.

Supports multiple TTS backends with automatic fallback:
  - CartesiaTTSProvider  (primary — Cartesia Sonic via REST API)
  - EdgeTTSProvider      (free fallback — Microsoft Edge TTS)

Usage:
    provider = get_tts_provider()
    audio_bytes, duration_ms = provider.generate_tts("Hello world")
"""

import os
import io
import struct
import wave
import asyncio
import tempfile
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

OUTPUT_FILE = "output.wav"


class TTSProvider(ABC):
    """Abstract base for all TTS providers."""

    @abstractmethod
    def generate_tts(self, text: str, voice_id: str = None) -> tuple[bytes, float]:
        """
        Generate speech audio from text.

        Args:
            text: The text to synthesize.
            voice_id: Optional voice identifier (provider-specific).

        Returns:
            (audio_bytes, duration_ms) — WAV bytes and duration in milliseconds.
        """
        ...


def _wav_duration_ms(wav_bytes: bytes) -> float:
    """Calculate duration in milliseconds from WAV file bytes."""
    try:
        with io.BytesIO(wav_bytes) as buf:
            with wave.open(buf, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate == 0:
                    return 0.0
                return (frames / rate) * 1000.0
    except Exception:
        return 0.0


def _pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Wrap raw PCM 16-bit data in a WAV header."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Cartesia TTS Provider
# ---------------------------------------------------------------------------

class CartesiaTTSProvider(TTSProvider):
    """Primary TTS provider using Cartesia Sonic via the cartesia Python SDK."""

    def __init__(self):
        self.api_key = os.getenv("TTS_API_KEY")
        if not self.api_key:
            raise ValueError("TTS_API_KEY environment variable is not set")

        self.default_voice_id = os.getenv(
            "TTS_VOICE_ID", "a0e99841-438c-4a64-b679-ae501e7d6091"
        )
        self.model_id = "sonic-2"

        # Verify SDK is importable
        try:
            import cartesia  # noqa: F401
        except ImportError:
            raise ImportError(
                "cartesia package is not installed. Run: pip install cartesia"
            )

        self._client = None

    def _get_client(self):
        if self._client is None:
            from cartesia import Cartesia
            self._client = Cartesia(api_key=self.api_key)
        return self._client

    def generate_tts(self, text: str, voice_id: str = None) -> tuple[bytes, float]:
        voice = voice_id or self.default_voice_id

        try:
            client = self._get_client()

            # Request raw PCM 16-bit 24kHz mono
            output_format = {
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": 24000,
            }

            try:
                response = client.tts.bytes(
                    model_id=self.model_id,
                    transcript=text,
                    voice_id=voice,
                    output_format=output_format,
                )
            except Exception:
                # Fallback to alternate model name
                print("⚠️ Cartesia sonic-2 failed, trying sonic-english fallback...")
                self.model_id = "sonic-english"
                response = client.tts.bytes(
                    model_id=self.model_id,
                    transcript=text,
                    voice_id=voice,
                    output_format=output_format,
                )

            # response is raw PCM bytes — wrap in WAV
            pcm_data = response if isinstance(response, bytes) else b"".join(response)
            wav_bytes = _pcm_to_wav(pcm_data, sample_rate=24000, channels=1, sample_width=2)

            # Save to output file
            with open(OUTPUT_FILE, "wb") as f:
                f.write(wav_bytes)

            duration_ms = _wav_duration_ms(wav_bytes)
            return wav_bytes, duration_ms

        except Exception as e:
            print(f"⚠️ Cartesia TTS error: {e}")
            raise


# ---------------------------------------------------------------------------
# Edge TTS Provider (free fallback)
# ---------------------------------------------------------------------------

class EdgeTTSProvider(TTSProvider):
    """Free fallback TTS provider using Microsoft Edge TTS (edge-tts package)."""

    def __init__(self):
        self.default_voice = os.getenv("EDGE_TTS_VOICE", "en-US-GuyNeural")

        try:
            import edge_tts  # noqa: F401
        except ImportError:
            raise ImportError(
                "edge_tts package is not installed. Run: pip install edge-tts"
            )

    def generate_tts(self, text: str, voice_id: str = None) -> tuple[bytes, float]:
        voice = voice_id or self.default_voice

        try:
            import edge_tts

            async def _synthesize():
                communicate = edge_tts.Communicate(text, voice)
                tmp_path = os.path.join(tempfile.gettempdir(), "rube_edge_tts.mp3")
                await communicate.save(tmp_path)
                return tmp_path

            # Run async edge-tts in a sync context
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # We're inside an existing event loop — use a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    tmp_path = pool.submit(
                        lambda: asyncio.run(_synthesize())
                    ).result()
            else:
                tmp_path = asyncio.run(_synthesize())

            # Read the generated audio
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()

            # Convert MP3 to WAV using pydub if available, otherwise save as-is
            try:
                from pydub import AudioSegment
                seg = AudioSegment.from_mp3(tmp_path)
                seg.export(OUTPUT_FILE, format="wav")
                with open(OUTPUT_FILE, "rb") as f:
                    wav_bytes = f.read()
                duration_ms = len(seg)
            except ImportError:
                # pydub not available — save MP3 directly and estimate duration
                print("⚠️ pydub not installed, saving edge-tts output as MP3")
                with open(OUTPUT_FILE, "wb") as f:
                    f.write(audio_bytes)
                wav_bytes = audio_bytes
                # Rough MP3 duration estimate: bitrate ~48kbps for edge-tts
                duration_ms = (len(audio_bytes) * 8) / 48.0

            # Clean up temp file
            try:
                os.remove(tmp_path)
            except OSError:
                pass

            return wav_bytes, duration_ms

        except Exception as e:
            print(f"⚠️ Edge TTS error: {e}")
            raise


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_tts_provider() -> TTSProvider:
    """
    Return a TTS provider based on the TTS_PROVIDER env var.

    Supported values: cartesia, edge_tts
    Falls back to EdgeTTSProvider if the requested provider fails to initialize.
    """
    provider_name = os.getenv("TTS_PROVIDER", "cartesia").lower().strip()

    provider_map = {
        "cartesia": CartesiaTTSProvider,
        "edge_tts": EdgeTTSProvider,
    }

    provider_class = provider_map.get(provider_name, CartesiaTTSProvider)

    try:
        return provider_class()
    except Exception as e:
        print(f"⚠️ Failed to initialize {provider_name} TTS provider: {e}")
        print("⚠️ Falling back to Edge TTS...")

        try:
            return EdgeTTSProvider()
        except Exception as fallback_err:
            print(f"⚠️ Edge TTS fallback also failed: {fallback_err}")
            raise RuntimeError(
                "No TTS provider could be initialized. "
                "Install either 'cartesia' or 'edge-tts' package."
            ) from fallback_err
