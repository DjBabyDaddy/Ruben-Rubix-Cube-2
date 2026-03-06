import os
import requests
import time
import urllib.parse
from tts import edge_speak

def generate_image(prompt: str) -> str:
    """Uses a free, zero-auth API to instantly generate graphics."""
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            save_path = os.path.join(os.path.expanduser("~"), "Downloads", f"RUBE_Generated_Graphic_{int(time.time())}.jpg")
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return save_path
    except Exception as e:
        print(f"⚠️ Graphic Generator Error: {e}")
    return None

def generate_social_post(parameters: dict, response: str, player, session_memory):
    post_content = parameters.get("post_content", "").strip()
    platform_target = parameters.get("platform", "all").strip().lower()
    image_prompt = parameters.get("image_prompt", "").strip()

    media_path = None
    if image_prompt and image_prompt.lower() != "none":
        print(f"🎨 RUBE Design Matrix: Generating graphic -> {image_prompt}")
        player.write_log("RUBE: Generating custom graphic for campaign...")
        media_path = generate_image(image_prompt)
        if media_path:
            print(f"✅ Graphic saved to: {media_path}")

    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    
    if not webhook_url:
        msg = "Boss, my n8n distribution highway is not connected. I need the webhook URL to schedule this."
        player.write_log(f"RUBE: {msg}")
        edge_speak(msg, player)
        return

    # Enforce Twitter/X 280-character hard limit
    if platform_target == "twitter" and len(post_content) > 280:
        post_content = post_content[:277] + "..."
        print(f"⚠️ Twitter post truncated to 280 characters.")

    payload = {
        "platform": platform_target,
        "content": post_content,
        "media_path": media_path or ""
    }

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        
        if res.status_code in [200, 201]:
            if media_path:
                msg = f"Campaign locked. The graphic was generated and the post was routed to n8n for {platform_target}."
            else:
                msg = f"Campaign locked. The post was routed to the n8n scheduler."
            player.write_log(f"RUBE: {msg}")
            edge_speak(msg, player)
        else:
            edge_speak(f"Boss, the n8n highway rejected the transmission.", player)
            
    except Exception as e:
        print(f"⚠️ n8n Webhook Error: {e}")
        edge_speak("I encountered a matrix error while trying to reach the n8n server.", player)