import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
from tts import edge_speak
from groq import Groq

AWAITING_KEY_NAME = None
AWAITING_SERVICE_NAME = None

def request_api_key(key_name, service_name, url_hint, player):
    global AWAITING_KEY_NAME, AWAITING_SERVICE_NAME
    AWAITING_KEY_NAME = key_name
    AWAITING_SERVICE_NAME = service_name
    msg = f"Boss, I need an API key for {service_name}. You can get it for free at {url_hint}. Please paste it into my terminal."
    
    if player and hasattr(player, 'write_log'):
        player.write_log(f"RUBE: {msg}")
        
    edge_speak(msg, player)
    try:
        player.trigger_hotkey() 
    except:
        pass

def conversational_readout(raw_data, query, player):
    """Routes raw internet data through Groq, protected by a Token Shield, and pushes to UI Logs."""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        system_instructions = "You are RUBE, a highly advanced AI. Your job is to translate raw JSON or web data into a natural, conversational spoken response for text-to-speech. For single-item lookups, be concise (1-3 sentences). For schedules, game slates, or multi-item lists, enumerate ALL items clearly — do not cut the list short. Do not use markdown, asterisks, or bullet points. Use natural transitions like 'also' and 'then' to connect multiple items."
        
        safe_data = str(raw_data)
        if len(safe_data) > 6000:
            safe_data = safe_data[:6000] + "... [DATA TRUNCATED]"
            
        user_prompt = f"The user asked: '{query}'. The internet returned this raw data: {safe_data}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        final_text = completion.choices[0].message.content.strip()
        
        # THE FIX: Pushing Search Output to Terminal Logs
        if player and hasattr(player, 'write_log'):
            player.write_log(f"RUBE: {final_text}")
            
        edge_speak(final_text, player)
    except Exception as e:
        print(f"Groq Translation Error: {e}")
        msg = "I found the data, boss, but I am having trouble formatting it for speech."
        if player and hasattr(player, 'write_log'):
            player.write_log(f"RUBE: {msg}")
        edge_speak(msg, player)

def web_search(parameters: dict, response: str = "", player=None, session_memory=None, api_key: str = "", geo_context: dict = None):
    query = (parameters or {}).get("query", "").strip()
    if not query: return
    
    if geo_context and geo_context.get("city") != "Unknown":
        city = geo_context["city"]
        state = geo_context["region"]
        if "weather" in query.lower() or "news" in query.lower():
            if city.lower() not in query.lower():
                query = f"{query} in {city}, {state}"

    q_lower = query.lower()
    print(f"🔍 RUBE API Router analyzing query: {query}")
    
    # 1. ENTERTAINMENT
    if any(w in q_lower for w in ["movie", "actor", "actress", "tv show", "episode", "film", "cinema"]):
        tmdb_key = os.getenv("TMDB_API_KEY")
        if not tmdb_key: return request_api_key("TMDB_API_KEY", "Entertainment Data", "TMDB.org", player)
        try:
            base_url = "https://" + "api.themoviedb.org/3/search/multi"
            url = f"{base_url}?api_key={tmdb_key}&query={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("results"):
                    return conversational_readout(json.dumps(data["results"][0]), query, player)
        except Exception as e: print(f"TMDB Error: {e}")

    # 2. GAMING
    elif any(w in q_lower for w in ["video game", "playstation", "xbox", "nintendo", "pc game", "steam", "gameplay"]):
        rawg_key = os.getenv("RAWG_API_KEY")
        if not rawg_key: return request_api_key("RAWG_API_KEY", "Gaming Data", "rawg.io", player)
        try:
            base_url = "https://" + "api.rawg.io/api/games"
            url = f"{base_url}?key={rawg_key}&search={urllib.parse.quote(query)}&page_size=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("results"):
                    return conversational_readout(json.dumps(data["results"][0]), query, player)
        except Exception as e: print(f"RAWG Error: {e}")

    # 3. WORLD NEWS 
    elif any(w in q_lower for w in ["news", "headlines", "world news"]):
        news_key = os.getenv("NEWS_API_KEY")
        if not news_key: return request_api_key("NEWS_API_KEY", "World News", "NewsAPI.org", player)
        try:
            base_url = "https://" + "newsapi.org/v2/top-headlines"
            url = f"{base_url}?country=us&apiKey={news_key}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("articles"):
                    return conversational_readout(json.dumps(data["articles"][:2]), query, player)
        except Exception as e: print(f"NewsAPI Error: {e}")

    # 4. CRYPTO
    elif any(c in q_lower for c in ["bitcoin", "ethereum", "crypto", "price of btc", "price of eth"]):
        coin = "bitcoin" if "bitcoin" in q_lower or "btc" in q_lower else "ethereum"
        try:
            base_url = "https://" + f"api.coingecko.com/api/v3/simple/price"
            url = f"{base_url}?ids={coin}&vs_currencies=usd"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return conversational_readout(json.dumps(data), query, player)
        except Exception as e: print(f"CoinGecko Error: {e}")

    # 5. ALL OTHER QUERIES (SerpAPI Matrix)
    serp_key = api_key or os.getenv("SERPAPI_API_KEY")
    if not serp_key:
        return request_api_key("SERPAPI_API_KEY", "Live Web Search", "serpapi.com", player)
        
    now = datetime.now()
    current_day_str = now.strftime("%A, %B %d, %Y") 
    time_words = ["tonight", "today", "now", "current", "this week", "yesterday", "tomorrow"]
    
    optimized_query = query
    if any(word in q_lower for word in time_words):
        optimized_query = f"{query} {current_day_str}"
        
    base_url = "https://" + "serpapi.com/search.json"
    url = f"{base_url}?q={urllib.parse.quote(optimized_query)}&hl=en&gl=us&api_key={serp_key}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            extracted_data = None
            if "sports_results" in data:
                extracted_data = data["sports_results"]
            elif "answer_box" in data:
                extracted_data = data["answer_box"]
            elif "finance_results" in data:
                extracted_data = data["finance_results"]
            elif "organic_results" in data and data["organic_results"]:
                extracted_data = data["organic_results"][0].get("snippet", "")
                
            if extracted_data:
                return conversational_readout(json.dumps(extracted_data), query, player)
                
            msg = "I could not find clear data on that topic, boss."
            if player and hasattr(player, 'write_log'): player.write_log(f"RUBE: {msg}")
            edge_speak(msg, player)
            
    except Exception as e:
        print(f"SerpApi Error: {e}")
        msg = "I am having trouble connecting to the data stream."
        if player and hasattr(player, 'write_log'): player.write_log(f"RUBE: {msg}")
        edge_speak(msg, player)