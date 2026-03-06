import os
import requests
from dotenv import load_dotenv
from groq import Groq
from tts import edge_speak

def generate_analytics_report(parameters: dict, response: str, player, session_memory):
    client_name = parameters.get("client_name", "the account").strip()
    
    player.write_log(f"RUBE: Querying the n8n data warehouse for {client_name}'s analytics...")
    
    load_dotenv()
    # You will create a SECOND webhook in n8n specifically for pulling data!
    analytics_webhook_url = os.getenv("N8N_ANALYTICS_WEBHOOK_URL")
    
    raw_data = ""
    if not analytics_webhook_url:
        print("⚠️ No N8N_ANALYTICS_WEBHOOK_URL found in .env. Running simulated report.")
        raw_data = "{'impressions': '+14%', 'engagement_rate': '4.2%', 'new_followers': 128, 'top_post': 'Coffee Shop Promo'}"
    else:
        try:
            res = requests.post(analytics_webhook_url, json={"client": client_name}, timeout=15)
            if res.status_code == 200:
                raw_data = str(res.json())
            else:
                raw_data = "Error fetching data from warehouse."
        except Exception:
            raw_data = "Warehouse timeout."

    # Send the raw, ugly JSON data to his Groq brain to turn it into a beautiful report
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        edge_speak("Boss, I need my Groq API key to format the analytics.", player)
        return

    client = Groq(api_key=groq_key)
    prompt = f"You are an elite Digital Marketing Director. Take this raw data for '{client_name}' and write a brief, professional 3-sentence summary of their performance. Raw Data: {raw_data}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        report_text = completion.choices[0].message.content.strip()
        player.write_log(f"RUBE: {report_text}")
        edge_speak(report_text, player)
    except Exception as e:
        print(f"⚠️ Analytics Formatting Error: {e}")
        edge_speak("My cognitive matrix failed to format the analytics report.", player)