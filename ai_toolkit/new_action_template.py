"""RUBE Action Module Template — Copy this file to actions/<your_module>.py

Replace all <PLACEHOLDERS> with your actual values.
See ai_docs/action_protocol.md for the full guide.
"""
import os
from dotenv import load_dotenv
from tts import edge_speak


def handle_<YOUR_INTENT>(parameters, response, player, session_memory):
    """Handle the '<YOUR_INTENT>' intent.

    Parameters expected from LLM:
      - <param_1>: <description>
      - <param_2>: <description>
    """
    # Extract parameters
    param_1 = str(parameters.get("<param_1>", "")).strip()
    if not param_1:
        edge_speak("Boss, I need <param_1> to do that.", player)
        return

    # Load API key if needed
    # load_dotenv()
    # api_key = os.getenv("<YOUR_API_KEY>")
    # if not api_key:
    #     edge_speak("I need the <service> API key for this, boss.", player)
    #     return

    # Acknowledge
    edge_speak("On it, boss.", player)

    # Do the work
    try:
        result = "your result here"
        player.write_log(f"RUBE: {result}")
        edge_speak(result, player)
    except Exception as e:
        print(f"⚠️ <YOUR_MODULE> error: {e}")
        edge_speak("That didn't work. Check the logs for details.", player)
