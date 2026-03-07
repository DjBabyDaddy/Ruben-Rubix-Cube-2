import os
import json
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from memory.feedback_logger import get_recent_lessons

# CONFIGURATION
PROMPT_PATH = "core/prompt.txt"

print("🧠 RUBE is linking his cognitive matrix to the Claude 4.6 Sonnet network...")

def load_system_prompt() -> str:
    try:
        if os.path.exists(PROMPT_PATH):
            with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        return "You are RUBE. Respond only in JSON format."
    except Exception:
        return "You are RUBE. Respond in JSON."

SYSTEM_PROMPT = load_system_prompt()

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

def get_llm_output(user_text: str, memory_block: dict = None) -> dict:
    """The primary cognitive routing matrix powered by Claude 4.6 Sonnet."""
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

    try:
        # THE FIX: Using the brand new claude-sonnet-4-6 model since the 3.5 series was deprecated
        response = client.messages.create(
            model="claude-sonnet-4-6",
            system=dynamic_system_prompt,
            messages=[{"role": "user", "content": user_text}],
            temperature=0.2,
            max_tokens=1024
        )
        
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