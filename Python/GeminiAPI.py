
import requests
import json
from config import GEMINI_API_KEY

class GeminiAssistant:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        self.headers = {
            "Content-Type": "application/json"
        }
        import platform
        self.os_name = platform.system()
        self.default_browser = self._detect_default_browser()
    def _detect_default_browser(self):
        import platform
        os_name = platform.system()
        if os_name == "Linux":
            return "Chrome/Firefox"
        elif os_name == "Darwin":
            return "Safari"
        elif os_name == "Windows":
            return "Edge/Chrome"
        return "Chrome"
    def _preprocess_text(self, text):
        import re
        cleaned = text
        original = text
        if 'research' in cleaned.lower() and ('download' in cleaned.lower() or 'fetch' in cleaned.lower()):
            browser_pattern = re.search(r'\b(open|use|go to)\s+(my\s+)?(default\s+)?browser\s+(and|to)\s+', 
                                       cleaned, flags=re.IGNORECASE)
            if browser_pattern:
                cleaned = re.sub(r'\b(open|use|go to)\s+(my\s+)?(default\s+)?browser\s+(and|to)\s+', '', 
                               cleaned, flags=re.IGNORECASE)
                return cleaned.strip()
        browser_search = re.search(r'\b(open|use|go to)\s+(my\s+)?(default\s+)?browser\s+(and|to)\s+(go to|search|find|lookup)?\s*(.+)', 
                                   cleaned, flags=re.IGNORECASE)
        if browser_search:
            target = browser_search.group(6).strip()
            return f"search {target}"
        cleaned = re.sub(r'^(hello|hi|hey|good morning|good afternoon|good evening|namaste)\s+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(bot|chatbot|assistant|either)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(what i want you to do is|i want you to|i need you to)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bi would say\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^[,\s]+', '', cleaned)
        cleaned = cleaned.strip()
        return cleaned if len(cleaned) > 2 else text
    def parse_command_to_json(self, text):
        try:
            cleaned_text = self._preprocess_text(text)
            if cleaned_text != text:
                print(f"📝 Cleaned: '{text}' → '{cleaned_text}'")
            os_friendly = {
                'Windows': 'Windows',
                'Linux': 'Linux',
                'Darwin': 'macOS'
            }.get(self.os_name, self.os_name)
            prompt = f"""You are a Command Understanding AI for a cross-platform voice assistant.
You must ONLY understand English, Hindi and Hinglish.

Device Information:
Operating System: {os_friendly}
Browser: {self.default_browser}

CRITICAL INSTRUCTIONS:
🔥 IGNORE greetings and politeness - focus on the ACTION
🔥 If there's BOTH a greeting AND a command, extract the COMMAND
🔥 "Hello...open X" = open_app action, NOT conversation
🔥 "Hi...search Y" = web_search action, NOT conversation

Action Types:

1️⃣ OPEN_APP - Launch local applications
Examples:
• "open chrome" → {{"action": "open_app", "app_name": "Chrome"}}
• "Hello bot, open steam" → {{"action": "open_app", "app_name": "Steam"}}
• "Good evening, launch calculator" → {{"action": "open_app", "app_name": "Calculator"}}

2️⃣ WEB_SEARCH - Search on Google
Examples:
• "search Python" → {{"action": "web_search", "query": "python"}}
• "Hello, search for weather" → {{"action": "web_search", "query": "weather"}}
• "open browser and go to steam" → {{"action": "web_search", "query": "steam"}}
• "search steam" → {{"action": "web_search", "query": "steam"}}

3️⃣ OPEN_WEBSITE - Open a website directly
Examples:
• "go to youtube" → {{"action": "open_website", "url": "youtube.com"}}
• "open google" → {{"action": "open_website", "url": "google.com"}}
• "visit reddit" → {{"action": "open_website", "url": "reddit.com"}}

4️⃣ PLATFORM_SEARCH - Search on ANY website
Examples:
• "search cats on youtube" → {{"action": "platform_search", "platform": "youtube", "query": "cats"}}
• "open instagram and search for oman" → {{"action": "platform_search", "platform": "instagram", "query": "oman"}}
• "go to chatgpt and write hello" → {{"action": "platform_search", "platform": "chatgpt", "query": "write hello"}}
• "search on amazon for laptop" → {{"action": "platform_search", "platform": "amazon", "query": "laptop"}}

5️⃣ PLAY_MEDIA - Play first result (auto-click and play)
Examples:
• "play latest song" → {{"action": "play_media", "query": "latest song", "platform": "youtube"}}
• "play first song from playlist" → {{"action": "play_media", "query": "playlist", "platform": "youtube"}}
• "go to youtube and play latest song" → {{"action": "play_media", "query": "latest song", "platform": "youtube"}}

6️⃣ DOWNLOAD_APP - Download/Install applications
Examples:
• "download steam" → {{"action": "download_app", "app_name": "steam"}}
• "install chrome" → {{"action": "download_app", "app_name": "chrome"}}
• "download VLC for me" → {{"action": "download_app", "app_name": "VLC"}}

7️⃣ DOWNLOAD_RESEARCH - Download research papers
Examples:
• "download research on machine learning" → {{"action": "download_research", "topic": "machine learning", "max_papers": 5}}
• "download me all research of quantum computing" → {{"action": "download_research", "topic": "quantum computing", "max_papers": 5}}
• "fetch research papers on AI" → {{"action": "download_research", "topic": "AI", "max_papers": 5}}

8️⃣ LIST_APPS - Show installed apps
Example: "list apps" → {{"action": "list_apps"}}

9️⃣ BROWSER_CONTROL - Interactive browser commands
Examples:
• "what's on the page" or "show page content" → {{"action": "browser_control", "command": "show_page"}}
• "click on the first link" → {{"action": "browser_control", "command": "click_first_link"}}
• "click on YouTube" → {{"action": "browser_control", "command": "click_by_text", "text": "YouTube"}}
• "there is a title called Stranger Things" → {{"action": "browser_control", "command": "click_by_text", "text": "Stranger Things"}}
• "click on the 4th video" → {{"action": "browser_control", "command": "click_nth", "position": 4, "element_type": "video"}}
• "scroll down" → {{"action": "browser_control", "command": "scroll_down"}}
• "scroll up" → {{"action": "browser_control", "command": "scroll_up"}}
• "close popup" → {{"action": "browser_control", "command": "close_popup"}}
• "volume up" → {{"action": "browser_control", "command": "volume_up"}}
• "volume down" → {{"action": "browser_control", "command": "volume_down"}}

🔟 CONVERSATION - ONLY if there's NO command at all
Examples:
• "hello" (nothing else) → {{"action": "conversation", "text": "hello"}}
• "thank you" (nothing else) → {{"action": "conversation", "text": "thank you"}}
• "how are you" (nothing else) → {{"action": "conversation", "text": "how are you"}}

Rules:
✨ Return ONLY valid JSON (no explanation, no markdown, no code blocks)
✨ IGNORE greetings if there's a command
✨ "go to [WEBSITE]" without "search" = open_website action (e.g., "go to youtube" → youtube.com)
✨ "open [WEBSITE]" without "search" = open_website action (e.g., "open google" → google.com)
✨ "visit [WEBSITE]" = open_website action
✨ "click on [TEXT]" where TEXT is not a number = browser_control with click_by_text
✨ "click on the [NUMBER]" = browser_control with click_nth
✨ "scroll" = browser_control action  
✨ "volume up/down" = browser_control action
✨ "play X" or "play first" (without "on page") = play_media action
✨ "play X on page" or "play video X" = browser_control with play_video
✨ "download research on X" or "fetch research papers" = download_research action
✨ "download X" or "install X" (for apps) = download_app action
✨ "open browser and search X" = web_search for X
✨ "open/go to [WEBSITE] and search X" = platform_search (WEBSITE can be ANY site!)
✨ "search X on [WEBSITE]" = platform_search
✨ Prefer action over conversation when unsure

User Input: {cleaned_text}
JSON Output:"""

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 100,
                    "topK": 1,
                    "topP": 0.1,
                }
            }
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if len(parts) > 0 and 'text' in parts[0]:
                            json_text = parts[0]['text'].strip()
                            json_text = json_text.replace('```json', '').replace('```', '').strip()
                            try:
                                parsed_json = json.loads(json_text)
                                return parsed_json
                            except json.JSONDecodeError:
                                return self._fallback_parse(text)
            return self._fallback_parse(text)
        except Exception as e:
            return self._fallback_parse(text)
    def _fallback_parse(self, text):
        import re
        cleaned = self._preprocess_text(text)
        text_lower = cleaned.lower().strip()
        match1 = re.search(r'(?:search|find|lookup)\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+(\w+)', text_lower)
        if match1:
            query, platform = match1.groups()
            query = query.strip()
            platform = platform.strip()
            web_indicators = ['youtube', 'google', 'instagram', 'facebook', 'twitter', 'amazon', 
                             'reddit', 'wikipedia', 'spotify', 'linkedin', 'github', 'chatgpt',
                             'netflix', 'pinterest', 'tiktok', 'snapchat', 'whatsapp', 'telegram',
                             'stackoverflow', 'medium', 'quora', 'ebay', 'imdb', 'yelp', 'twitch']
            if any(indicator in platform for indicator in web_indicators) or len(platform) > 3:
                return {"action": "platform_search", "platform": platform, "query": query}
        match2 = re.search(r'(?:go to|open|use)\s+(\w+)\s+(?:and|to)\s+(?:search|find|lookup|write)\s+(?:for\s+)?(.+)', text_lower)
        if match2:
            platform, query = match2.groups()
            query = query.strip()
            platform = platform.strip()
            web_indicators = ['youtube', 'google', 'instagram', 'facebook', 'twitter', 'amazon', 
                             'reddit', 'wikipedia', 'spotify', 'linkedin', 'github', 'chatgpt',
                             'netflix', 'pinterest', 'tiktok', 'snapchat', 'whatsapp', 'telegram',
                             'stackoverflow', 'medium', 'quora', 'ebay', 'imdb', 'yelp', 'twitch']
            if any(indicator in platform for indicator in web_indicators) or len(platform) > 3:
                return {"action": "platform_search", "platform": platform, "query": query}
        match3 = re.search(r'(\w+)\s+(?:pe|mein|me)\s+(?:search|find|dhoondo)\s+(.+)', text_lower)
        if match3:
            platform, query = match3.groups()
            query = query.strip()
            platform = platform.strip()
            web_indicators = ['youtube', 'google', 'instagram', 'facebook', 'twitter', 'amazon', 
                             'reddit', 'wikipedia', 'spotify', 'linkedin', 'github', 'chatgpt',
                             'netflix', 'pinterest', 'tiktok', 'snapchat', 'whatsapp', 'telegram',
                             'stackoverflow', 'medium', 'quora', 'ebay', 'imdb', 'yelp', 'twitch']
            if any(indicator in platform for indicator in web_indicators) or len(platform) > 3:
                return {"action": "platform_search", "platform": platform, "query": query}
        if text_lower.startswith(('search ', 'google ', 'find ', 'lookup ')):
            query = text_lower.split(None, 1)[1] if len(text_lower.split()) > 1 else text_lower
            return {"action": "web_search", "query": query}
        elif text_lower.startswith(('open ', 'launch ', 'start ', 'run ')):
            app_name = text_lower.split(None, 1)[1] if len(text_lower.split()) > 1 else text_lower
            if 'and search' in text_lower or 'and find' in text_lower:
                parts = app_name.split('and')
                if len(parts) >= 2:
                    platform = parts[0].strip()
                    query = ' '.join(parts[1:]).replace('search', '').replace('find', '').strip()
                    return {"action": "platform_search", "platform": platform, "query": query}
            return {"action": "open_app", "app_name": app_name}
        elif text_lower.startswith(('play ', 'play the ', 'play first ')):
            query = text_lower.replace('play ', '').replace('the ', '').replace('first ', '').strip()
            return {"action": "play_media", "query": query, "platform": "youtube"}
        elif 'research' in text_lower and ('download' in text_lower or 'fetch' in text_lower or 'get' in text_lower):
            topic = text_lower
            for remove in ['download', 'fetch', 'get', 'me', 'all', 'research', 'of', 'on', 'about', 'for']:
                topic = topic.replace(remove, '')
            topic = topic.strip()
            return {"action": "download_research", "topic": topic, "max_papers": 5}
        elif text_lower.startswith(('download ', 'install ')):
            app_name = text_lower.split(None, 1)[1] if len(text_lower.split()) > 1 else text_lower
            app_name = app_name.replace('for me', '').strip()
            if 'research' in app_name or 'papers' in app_name:
                topic = app_name.replace('research', '').replace('papers', '').replace('on', '').replace('about', '').strip()
                return {"action": "download_research", "topic": topic, "max_papers": 5}
            return {"action": "download_app", "app_name": app_name}
        elif text_lower.startswith(('go to ', 'goto ', 'open ', 'visit ')):
            target = text_lower.replace('go to ', '').replace('goto ', '').replace('open ', '').replace('visit ', '').strip()
            if 'and search' in target or 'and find' in target or 'and write' in target:
                parts = target.split('and')
                if len(parts) >= 2:
                    platform = parts[0].strip()
                    query = ' '.join(parts[1:]).replace('search', '').replace('find', '').replace('write', '').strip()
                    return {"action": "platform_search", "platform": platform, "query": query}
            known_websites = ['youtube', 'google', 'facebook', 'instagram', 'twitter', 'reddit', 
                             'github', 'amazon', 'netflix', 'spotify', 'linkedin', 'wikipedia',
                             'flipkart', 'gmail', 'yahoo', 'bing', 'chatgpt', 'whatsapp']
            if any(site in target for site in known_websites):
                return {"action": "open_website", "url": f"{target}.com"}
            if any(app in target for app in ['steam', 'chrome', 'firefox', 'calculator', 'discord', 'vscode', 'code']):
                return {"action": "open_app", "app_name": target}
            if '.com' in target or '.org' in target or '.net' in target or '.io' in target:
                return {"action": "open_website", "url": target}
            return {"action": "open_website", "url": f"{target}.com"}
        elif 'list app' in text_lower or 'show app' in text_lower:
            return {"action": "list_apps"}
        elif "what's on" in text_lower or 'show page' in text_lower or 'read page' in text_lower or 'page content' in text_lower:
            return {"action": "browser_control", "command": "show_page"}
        elif 'scroll down' in text_lower:
            return {"action": "browser_control", "command": "scroll_down"}
        elif 'scroll up' in text_lower:
            return {"action": "browser_control", "command": "scroll_up"}
        elif 'close popup' in text_lower or 'close pop up' in text_lower or 'press cross' in text_lower or 'click cross' in text_lower:
            return {"action": "browser_control", "command": "close_popup"}
        elif 'volume up' in text_lower or 'increase volume' in text_lower:
            return {"action": "browser_control", "command": "volume_up"}
        elif 'volume down' in text_lower or 'decrease volume' in text_lower:
            return {"action": "browser_control", "command": "volume_down"}
        elif 'click' in text_lower and 'first' in text_lower:
            return {"action": "browser_control", "command": "click_first_link"}
        elif 'click' in text_lower or 'press' in text_lower or 'select' in text_lower:
            import re
            number_match = re.search(r'(\d+)(st|nd|rd|th)?', text_lower)
            if number_match:
                n = int(number_match.group(1))
                element_type = 'link'
                if 'video' in text_lower:
                    element_type = 'video'
                elif 'link' in text_lower:
                    element_type = 'link'
                elif 'button' in text_lower:
                    element_type = 'button'
                elif 'result' in text_lower:
                    element_type = 'result'
                return {"action": "browser_control", "command": "click_nth", "position": n, "element_type": element_type}
            else:
                patterns = [
                    r'click\s+on\s+(?:the\s+)?(.+)',
                    r'press\s+on\s+(?:the\s+)?(.+)',
                    r'select\s+(?:the\s+)?(.+)',
                    r'click\s+(.+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        text_to_click = match.group(1).strip()
                        if 'called' in text_lower or 'titled' in text_lower or 'named' in text_lower:
                            called_match = re.search(r'(?:called|titled|named)\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s+file|\s+page|\s+link|\s+in|\s+on|\s+can|$)', text_lower)
                            if called_match:
                                text_to_click = called_match.group(1).strip()
                        if text_to_click not in ['cross', 'cross button', 'popup', 'first', 'first link', 'that', 'this', 'it'] and len(text_to_click) > 2:
                            return {"action": "browser_control", "command": "click_by_text", "text": text_to_click}
                return {"action": "browser_control", "command": "click_first_link"}
        greeting_only = re.match(r'^(hello|hi|hey|thank you|thanks|how are you|namaste|kaise ho)[\s\.,!?]*$', text_lower)
        if greeting_only:
            return {"action": "conversation", "text": text}
        if len(text_lower.split()) == 1 and len(text_lower) > 2:
            return {"action": "open_app", "app_name": text_lower}
        return {"action": "web_search", "query": cleaned}
    def query(self, prompt):
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return True, parts[0]["text"]
                return False, "No response from Gemini"
            else:
                error_msg = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                return False, error_msg
        except requests.exceptions.Timeout:
            return False, "Request timeout - check internet connection"
        except Exception as e:
            return False, f"Error: {str(e)}"
    def _regex_parse_command(self, text):
        import re
        removal_patterns = [
            r'\b(hello|hi|hey|good morning|good afternoon|good evening|namaste|namaskar)\b',
            r'\b(bot|assistant|either|either assistant|alexa|siri)\b',
            r'\b(how are you|what\'s up|kaise ho|kya hal hai)\??',
            r'\b(what i want you to do is|i want you to do is|i want you to|i need you to|i would like you to)\b',
            r'\b(what i want is|i want to|i need to|i would like to)\b',
            r'\b(go to a web and|go to the web and|go to web and|on the web|on web)\b',
            r'\b(go to a|go to the|go to)\b',
            r'\b(please|kindly|can you|could you|would you|will you|would you please|for me|thank you|thanks|dhanyavaad|shukriya|karo|kijiye)\b',
            r'^\s*(can|could|would|will|do|does|what|so)\s+',
            r'\b(just|really|actually|basically|literally|so|what)\b',
        ]
        cleaned = text.lower()
        for _ in range(2):
            for pattern in removal_patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'[,?!]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^(to|and)\s+', '', cleaned)
        if not re.search(r'^(open|close|start|launch)', cleaned):
            cleaned = re.sub(r'\b(the|a|an)\b', '', cleaned)
        cleaned = re.sub(r'\sfor\s+(?=\w+\s*$)', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^(to|for|at|in|on)\s+', '', cleaned)
        if len(cleaned) >= 3 and cleaned != text.lower():
            return cleaned
        return text
    def parse_conversational_command(self, text):
        try:
            prompt = f"""You are a command parser for a voice assistant. Extract ONLY the core action from conversational text.

Rules:
1. Remove greetings: "hello", "hi", "hey", "good morning", "namaste", etc.
2. Remove bot names: "bot", "assistant", "either", "either assistant"
3. Remove politeness: "please", "can you", "could you", "would you", "for me", "thank you", "karo"
4. Remove questions: "how are you", "what's up", "kaise ho"
5. Keep only the ACTION and OBJECT
6. Return as a simple command (2-6 words maximum)
7. Do NOT include any explanation, just the command

Examples:
Input: "Hello bot, how are you? Can you open calculator for me please?"
Output: open calculator

Input: "Hey Either assistant, please search Python tutorials on web for me"
Output: search Python tutorials

Input: "Hi, can you download Chrome browser?"
Output: download Chrome browser

Input: "Either, open Spotify and play music"
Output: open Spotify

Input: "Good morning assistant, search for weather today"
Output: search weather today

Input: "Hello, list all apps please"
Output: list apps

Input: "Namaste bot, calculator kholo please"
Output: open calculator

Now extract the core command from this:
Input: {text}
Output:"""

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 50,
                    "topK": 1,
                    "topP": 0.1,
                }
            }
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if len(parts) > 0 and 'text' in parts[0]:
                            extracted_text = parts[0]['text'].strip()
                            extracted_text = extracted_text.replace('Output:', '').strip()
                            extracted_text = extracted_text.strip('"\'')
                            extracted_text = extracted_text.split('\n')[0]
                            if 2 <= len(extracted_text) <= 50 and extracted_text.lower() != text.lower():
                                return extracted_text
            return self._regex_parse_command(text)
        except requests.exceptions.RequestException as e:
            return self._regex_parse_command(text)
        except Exception as e:
            return self._regex_parse_command(text)
    def search_and_respond(self, query):
        enhanced_query = f"""You are a helpful voice assistant. Answer this question concisely and clearly:
Question: {query}

Provide a brief, direct answer suitable for voice interaction. Keep it under 3-4 sentences."""
        success, response = self.query(enhanced_query)
        if success:
            return response
        else:
            return f"Sorry, I couldn't get information: {response}"


def test_gemini():
    print("\n" + "="*70)
    print("GEMINI API TEST")
    print("="*70)
    assistant = GeminiAssistant()
    test_queries = [
        "What is artificial intelligence?",
        "Who is the president of India?",
        "How to make tea?",
        "What is the capital of France?",
    ]
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("─"*70)
        success, response = assistant.query(query)
        if success:
            print(f"✅ Response:\n{response}")
        else:
            print(f"❌ Error: {response}")
        print("─"*70)
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_gemini()