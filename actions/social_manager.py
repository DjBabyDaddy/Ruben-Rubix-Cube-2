import os
import base64
import requests
import time
import urllib.parse
from tts import edge_speak

def generate_image(prompt: str) -> tuple:
    """Uses a free, zero-auth API to generate graphics. Returns (local_path, pollinations_url)."""
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"

        response = requests.get(pollinations_url, timeout=45)
        if response.status_code == 200:
            save_path = os.path.join(os.path.expanduser("~"), "Downloads", f"RUBE_Generated_Graphic_{int(time.time())}.jpg")
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return save_path, pollinations_url
    except Exception as e:
        print(f"⚠️ Graphic Generator Error: {e}")
    return None, None

def generate_social_post(parameters: dict, response: str, player, session_memory):
    post_content = parameters.get("post_content", "").strip()
    platform_target = parameters.get("platform", "all").strip().lower()
    image_prompt = parameters.get("image_prompt", "").strip()

    media_path = None
    media_url = None

    if image_prompt and image_prompt.lower() != "none":
        print(f"🎨 RUBE Design Matrix: Generating graphic -> {image_prompt}")
        player.write_log("RUBE: Generating custom graphic for campaign...")
        media_path, media_url = generate_image(image_prompt)
        if media_path:
            print(f"✅ Graphic saved to: {media_path}")
        else:
            print("⚠️ Image generation failed — posting without graphic.")

    # Instagram is visual-first: warn if no image
    if platform_target == "instagram" and not media_path and not image_prompt:
        print("⚠️ Instagram post without image — engagement will be lower.")

    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    if not webhook_url:
        msg = "Boss, my n8n distribution highway is not connected. I need the webhook URL to schedule this."
        player.write_log(f"RUBE: {msg}")
        edge_speak(msg, player)
        return

    # Enforce Twitter/X 280-character hard limit
    if platform_target == "twitter" and len(post_content) > 280:
        post_content = post_content[:277] + "..."
        print("⚠️ Twitter post truncated to 280 characters.")

    # Build payload with image data n8n can actually use
    payload = {
        "platform": platform_target,
        "content": post_content,
        "media_path": media_path or "",
        "media_url": media_url or ""
    }

    # Encode image as base64 so n8n doesn't need local file access
    if media_path and os.path.exists(media_path):
        try:
            with open(media_path, 'rb') as f:
                payload["media_base64"] = base64.b64encode(f.read()).decode('utf-8')
            payload["media_filename"] = os.path.basename(media_path)
        except Exception as e:
            print(f"⚠️ Base64 encoding failed: {e}")

    # Post to n8n with retry logic
    last_error = None
    for attempt in range(2):
        try:
            res = requests.post(webhook_url, json=payload, timeout=30)

            if res.status_code in [200, 201]:
                if media_path:
                    msg = f"Campaign locked. The graphic was generated and the post was routed to n8n for {platform_target}."
                else:
                    msg = f"Campaign locked. The post was routed to the n8n scheduler."
                player.write_log(f"RUBE: {msg}")
                edge_speak(msg, player)
                return
            else:
                last_error = f"Status {res.status_code}"
                print(f"⚠️ n8n Response [{res.status_code}]: {res.text[:500]}")

        except requests.exceptions.Timeout:
            last_error = "Timeout"
            print(f"⚠️ n8n webhook timeout (attempt {attempt + 1}/2)")
        except Exception as e:
            last_error = str(e)
            print(f"⚠️ n8n Webhook Error: {e}")

        if attempt == 0:
            time.sleep(3)

    edge_speak(f"Boss, the n8n highway failed after 2 attempts. Error: {last_error}", player)