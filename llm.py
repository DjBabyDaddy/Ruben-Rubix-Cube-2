import os
import json
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from memory.feedback_logger import get_recent_lessons

# CONFIGURATION
PROMPT_PATH = "core/prompt.txt"
BRAIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RUBE_SUPER_BRAIN.md")

print("🧠 RUBE is linking his cognitive matrix to the Claude 4.6 Sonnet network...")

def load_system_prompt() -> str:
    try:
        if os.path.exists(PROMPT_PATH):
            with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        return "You are RUBE. Respond only in JSON format."
    except Exception:
        return "You are RUBE. Respond in JSON."

def load_brain() -> str:
    """Load RUBE's AI framework knowledge base (LangGraph, CrewAI, MCP, LlamaIndex, Anthropic).
    Call this during self-improvement tasks so RUBE reasons against best-practice patterns."""
    try:
        if os.path.exists(BRAIN_PATH):
            with open(BRAIN_PATH, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return ""

SYSTEM_PROMPT = load_system_prompt()

# Structured output schema — guarantees valid JSON from Claude API
INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "parameters": {"type": "object"},
        "text": {"type": "string"},
        "confidence": {"type": "number"},
        "memory_update": {"type": "object"},
    },
    "required": ["intent", "text"],
}

# Check if SDK supports structured outputs (anthropic >= 0.84.0)
_STRUCTURED_OUTPUTS_AVAILABLE = hasattr(anthropic.types, "JSONSchemaOutputConfig") if hasattr(anthropic, "types") else False

def safe_json_parse(text: str) -> dict | None:
    if not text: return None
    text = text.strip()
    for block in ["```json", "```"]:
        if block in text:
            try:
                start = text.index(block) + len(block)
                end = text.index("```", start)
                text = text[start:end].strip()
            except: pass
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return None

def get_llm_output(user_text: str, memory_block: dict = None, use_brain: bool = False) -> dict:
    """The primary cognitive routing matrix powered by Claude 4.6 Sonnet.

    Pass use_brain=True from self_improver.py to inject the AI framework knowledge
    base (RUBE_SUPER_BRAIN.md) so RUBE reasons against proven patterns when
    proposing code changes."""
    if not user_text or not user_text.strip():
        return {"intent": "chat", "text": "Boss, I didn't catch that."}
        
    load_dotenv()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        return {"intent": "chat", "text": "Boss, my Claude cognitive matrix is disconnected. I need an Anthropic API key."}
        
    client = anthropic.Anthropic(api_key=anthropic_key)

    recent_convo = memory_block.pop("recent_conversation", "") if memory_block else ""
    memory_str = "\n".join(f"{k}: {v}" for k, v in (memory_block or {}).items())
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    dynamic_system_prompt = f"{SYSTEM_PROMPT}\n\n[SYSTEM CLOCK: {current_time}]\n\n[PERMANENT MEMORY]\n{memory_str}\n\n[RECENT CONVERSATION BUFFER]\n{recent_convo}"

    # Inject recent failure patterns so the LLM can learn from mistakes
    lessons = get_recent_lessons(50)
    if lessons:
        dynamic_system_prompt += f"\n\n[RECENT LESSONS - Avoid repeating these failure patterns]\n{lessons}"

    # Inject AI framework knowledge base for self-improvement calls
    # Keeps all standard calls lean — only loads the brain when explicitly needed
    if use_brain:
        brain = load_brain()
        if brain:
            dynamic_system_prompt += f"\n\n[AI FRAMEWORK KNOWLEDGE BASE - Reference these proven patterns when proposing code changes]\n{brain}"

    try:
        api_kwargs = {
            "model": "claude-sonnet-4-6",
            "system": dynamic_system_prompt,
            "messages": [{"role": "user", "content": user_text}],
            "temperature": 0.2,
            "max_tokens": 1024,
        }

        # Use structured outputs if SDK supports it — guarantees valid JSON
        if _STRUCTURED_OUTPUTS_AVAILABLE:
            try:
                api_kwargs["output_config"] = {
                    "type": "json_schema",
                    "json_schema": {"name": "rube_intent", "schema": INTENT_SCHEMA},
                }
            except Exception:
                pass  # Fall through to standard parsing

        response = client.messages.create(**api_kwargs)

        output_text = response.content[0].text.strip()
        parsed = safe_json_parse(output_text)

        if parsed and "intent" in parsed:
            return {
                "intent": parsed.get("intent", "chat"),
                "parameters": parsed.get("parameters", {}),
                "text": parsed.get("text", "Task complete, boss."),
                "memory_update": parsed.get("memory_update"),
                "confidence": parsed.get("confidence", 1.0)
            }
        return {"intent": "chat", "text": "I apologize, boss, my reasoning matrix misunderstood that format."}
        
    except Exception as e:
        print(f"🧠 RUBE Matrix Error: {e}")
        return {
            "intent": "chat", 
            "parameters": {}, 
            "text": "I encountered an error connecting to the Claude neural network.", 
            "memory_update": {}
        }

def get_llm_multimodal_output(base64_imgs: list, prompt_text: str) -> str:
    """Routes visual data directly into Claude's optical cortex."""
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key: 
        return "My visual cortex lacks an API connection, boss."

    client = anthropic.Anthropic(api_key=api_key)
    
    content_block = []
    
    for b64 in base64_imgs:
        content_block.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg", 
                "data": b64
            }
        })
        
    content_block.append({
        "type": "text",
        "text": f"Analyze these images. {prompt_text}. Keep your response concise, sharp, and conversational as if you are my AI assistant RUBE speaking to me."
    })

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            temperature=0.4,
            messages=[{"role": "user", "content": content_block}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ CLAUDE VISUAL ERROR: {e}")
        return "My visual matrix crashed while attempting to process the frames through Claude."