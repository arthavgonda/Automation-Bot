
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
        
        cleaned = re.sub(r',\s+', ' and ', cleaned, flags=re.IGNORECASE)
        
        if ('create' in cleaned.lower() or 'make' in cleaned.lower()) and 'file' in cleaned.lower():
            cleaned = re.sub(r'^(i\s+want\s+you\s+to|i\s+want|please|can\s+you|could\s+you|would\s+you)\s+', '', cleaned, flags=re.IGNORECASE)
        
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

🔄 SWITCH_APP - Switch control to another application
Examples:
• "switch to chrome" → {{"action": "switch_app", "app_name": "chrome"}}
• "switch to vscode" → {{"action": "switch_app", "app_name": "vscode"}}
• "go to browser" → {{"action": "switch_app", "app_name": "browser"}}
• "switch to previous app" → {{"action": "switch_app", "app_name": "previous"}}
• "switch back" → {{"action": "switch_app", "app_name": "back"}}

🎮 APP_COMMAND - Execute commands within active application
Examples:
• "save file" → {{"action": "app_command", "command": "save"}}
• "type hello world" → {{"action": "app_command", "command": "type", "params": {{"text": "hello world"}}}}
• "copy this" → {{"action": "app_command", "command": "copy"}}
• "paste" → {{"action": "app_command", "command": "paste"}}
• "undo" → {{"action": "app_command", "command": "undo"}}
• "press enter" → {{"action": "app_command", "command": "enter"}}
• "new tab" → {{"action": "app_command", "command": "new tab"}}
• "close tab" → {{"action": "app_command", "command": "close tab"}}
• "bold" → {{"action": "app_command", "command": "bold"}}
• "find" → {{"action": "app_command", "command": "find"}}
• "scroll down" → {{"action": "app_command", "command": "scroll down"}}

2️⃣ WEB_SEARCH - Search on Google (NOT when in app context)
Examples:
• "search Python" → {{"action": "web_search", "query": "python"}}
• "Hello, search for weather" → {{"action": "web_search", "query": "weather"}}
• "open browser and go to steam" → {{"action": "web_search", "query": "steam"}}
• "search steam" → {{"action": "web_search", "query": "steam"}}

🔥 IMPORTANT: If user is already in an application and says something generic, use app_command with type!
• In VSCode + "hello world" → {{"action": "app_command", "command": "type", "params": {{"text": "hello world"}}}}
• In Notepad + "my name is john" → {{"action": "app_command", "command": "type", "params": {{"text": "my name is john"}}}}

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
🔥 CRITICAL: User can specify WHERE to download from!

Source Options (in order of priority):
A) EXPLICIT SOURCE SPECIFIED:
• "download X from web" → {{"action": "download_app", "app_name": "X", "source": "web"}}
• "download X from terminal" → {{"action": "download_app", "app_name": "X", "source": "terminal"}}
• "install X from snap" → {{"action": "download_app", "app_name": "X", "source": "snap"}}
• "install X from flatpak" → {{"action": "download_app", "app_name": "X", "source": "flatpak"}}
• "download X from app store" → {{"action": "download_app", "app_name": "X", "source": "appstore"}}
• "get X via snap store" → {{"action": "download_app", "app_name": "X", "source": "snap"}}
• "install X via package manager" → {{"action": "download_app", "app_name": "X", "source": "terminal"}}

B) NO SOURCE SPECIFIED (DEFAULT TO WEB):
• "download steam" → {{"action": "download_app", "app_name": "steam", "source": "web"}}
• "install chrome" → {{"action": "download_app", "app_name": "chrome", "source": "web"}}
• "get discord" → {{"action": "download_app", "app_name": "discord", "source": "web"}}

Source Keywords:
• "web", "internet", "online", "website" → source: "web"
• "terminal", "package manager", "apt", "dnf", "brew", "choco" → source: "terminal"
• "snap", "snap store" → source: "snap"
• "flatpak" → source: "flatpak"
• "app store", "microsoft store", "mac app store", "gnome software" → source: "appstore"

🔥 ALWAYS include "source" field in download_app actions!
🔥 If user says "from [SOURCE]" or "via [SOURCE]", extract it!
🔥 Default to "web" if no source is mentioned!

7️⃣ DOWNLOAD_RESEARCH - Download research papers
Examples:
• "download research on machine learning" → {{"action": "download_research", "topic": "machine learning", "max_papers": 5}}
• "download me all research of quantum computing" → {{"action": "download_research", "topic": "quantum computing", "max_papers": 5}}
• "fetch research papers on AI" → {{"action": "download_research", "topic": "AI", "max_papers": 5}}

8️⃣ LIST_APPS - Show installed apps
Example: "list apps" → {{"action": "list_apps"}}

9️⃣ BROWSER_CONTROL - Interactive browser commands

📑 TAB MANAGEMENT:
• "create new tab" or "open new tab" → {{"action": "browser_control", "command": "new_tab"}}
• "new tab and open youtube" → {{"action": "browser_control", "command": "new_tab", "url": "youtube.com"}}
• "switch to first tab" or "go to first tab" → {{"action": "browser_control", "command": "first_tab"}}
• "switch to last tab" or "go to last tab" → {{"action": "browser_control", "command": "last_tab"}}
• "go to next tab" or "next tab" → {{"action": "browser_control", "command": "next_tab"}}
• "go to previous tab" or "previous tab" → {{"action": "browser_control", "command": "previous_tab"}}
• "switch to tab 3" or "go to 3rd tab" → {{"action": "browser_control", "command": "switch_to_tab", "tab_index": 3}}
• "close this tab" or "close current tab" → {{"action": "browser_control", "command": "close_tab"}}
• "close other tabs" or "close all other tabs" → {{"action": "browser_control", "command": "close_other_tabs"}}
• "list all tabs" or "show tabs" → {{"action": "browser_control", "command": "list_tabs"}}

🪟 WINDOW MANAGEMENT:
• "create new window" or "open new window" → {{"action": "browser_control", "command": "new_window"}}
• "open incognito window" or "create private window" → {{"action": "browser_control", "command": "incognito_window"}}
• "maximize window" → {{"action": "browser_control", "command": "maximize"}}
• "minimize window" → {{"action": "browser_control", "command": "minimize"}}
• "fullscreen" or "enter fullscreen" → {{"action": "browser_control", "command": "fullscreen"}}

🧭 NAVIGATION:
• "go back" or "back" → {{"action": "browser_control", "command": "go_back"}}
• "go forward" or "forward" → {{"action": "browser_control", "command": "go_forward"}}
• "refresh page" or "reload" → {{"action": "browser_control", "command": "refresh"}}
• "what's the current url" → {{"action": "browser_control", "command": "get_url"}}
• "what's the page title" → {{"action": "browser_control", "command": "get_title"}}

🖱️ PAGE INTERACTION:
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

🔟 COMPLEX_COMMAND - Multi-step commands with AND/THEN
Examples:
• "open VS Code and create file tut1.cpp" → {{"action": "complex_command", "steps": [
  {{"action": "open_app", "app_name": "vscode"}},
  {{"action": "create_file", "file_path": "tut1.cpp", "open_in_app": "vscode"}}
]}}
• "I want you to create a file tut1.cpp and open it in VS Code" → {{"action": "complex_command", "steps": [
  {{"action": "create_file", "file_path": "tut1.cpp", "open_in_app": "vscode"}}
]}}
• "create file tut1.cpp and open it in VS Code" → {{"action": "complex_command", "steps": [
  {{"action": "create_file", "file_path": "tut1.cpp", "open_in_app": "vscode"}}
]}}
• "open VS Code and make a file called tut1.cpp" → {{"action": "complex_command", "steps": [
  {{"action": "open_app", "app_name": "vscode"}},
  {{"action": "create_file", "file_path": "tut1.cpp", "open_in_app": "vscode"}}
]}}
• "can you open VS Code and make a file called tut1.cpp" → {{"action": "complex_command", "steps": [
  {{"action": "open_app", "app_name": "vscode"}},
  {{"action": "create_file", "file_path": "tut1.cpp", "open_in_app": "vscode"}}
]}}
• "open Chrome and search Python tutorials" → {{"action": "complex_command", "steps": [
  {{"action": "open_app", "app_name": "chrome"}},
  {{"action": "web_search", "query": "Python tutorials"}}
]}}
• "open firefox and search youtube" → {{"action": "complex_command", "steps": [
  {{"action": "open_app", "app_name": "firefox"}},
  {{"action": "web_search", "query": "youtube"}}
]}}
• "open browser and search for cats" → {{"action": "complex_command", "steps": [
  {{"action": "open_app", "app_name": "chrome"}},
  {{"action": "web_search", "query": "cats"}}
]}}
• "create folder projects and make file main.py" → {{"action": "complex_command", "steps": [
  {{"action": "create_folder", "folder_path": "projects"}},
  {{"action": "create_file", "file_path": "projects/main.py"}}
]}}

1️⃣1️⃣ CREATE_FILE - Create a new file (with folder creation if needed)
Examples:
• "create file tut1.cpp" → {{"action": "create_file", "file_path": "tut1.cpp"}}
• "make a file called tut1.cpp" → {{"action": "create_file", "file_path": "tut1.cpp"}}
• "create file named test.py" → {{"action": "create_file", "file_path": "test.py"}}
• "make file test.py in folder scripts" → {{"action": "create_file", "file_path": "scripts/test.py", "create_folder_if_missing": true}}
• "create document.txt" → {{"action": "create_file", "file_path": "document.txt"}}

1️⃣2️⃣ CREATE_FOLDER - Create a new folder/directory
Examples:
• "create folder projects" → {{"action": "create_folder", "folder_path": "projects"}}
• "make directory test" → {{"action": "create_folder", "folder_path": "test"}}

1️⃣3️⃣ MOVE_FILE - Move file from one location to another
Examples:
• "move file.txt to folder backup" → {{"action": "move_file", "source": "file.txt", "destination": "backup/file.txt"}}
• "move document.pdf from downloads to documents" → {{"action": "move_file", "source": "downloads/document.pdf", "destination": "documents/document.pdf"}}

1️⃣4️⃣ COPY_FILE - Copy file from one location to another
Examples:
• "copy file.txt to folder backup" → {{"action": "copy_file", "source": "file.txt", "destination": "backup/file.txt"}}
• "copy document.pdf to documents folder" → {{"action": "copy_file", "source": "document.pdf", "destination": "documents/document.pdf"}}

🔟 CONVERSATION - ONLY if there's NO command at all
Examples:
• "hello" (nothing else) → {{"action": "conversation", "text": "hello"}}
• "thank you" (nothing else) → {{"action": "conversation", "text": "thank you"}}
• "how are you" (nothing else) → {{"action": "conversation", "text": "how are you"}}

Rules:
✨ Return ONLY valid JSON (no explanation, no markdown, no code blocks)
✨ IGNORE greetings AND politeness phrases - focus on ACTION
✨ "I want you to create file X" = create_file action (ignore "I want you to")
✨ "I want you to open X and create file Y" = complex_command with steps
✨ "create file X and open it in Y" = complex_command with steps
✨ "create file X in Y" where Y is an app = complex_command
✨ "open X and create file Y" = complex_command with steps
✨ "open X and make a file called Y" = complex_command with steps (extract Y, not "called")
✨ "open X and [action]" = complex_command for multi-step operations
✨ "create file X" = create_file action (auto-create folder if missing)
✨ "make a file called X" = create_file with file_path: "X" (NOT "called")
✨ When user says "called X", "named X", or "titled X", extract X as the filename
✨ If command contains "create file" or "make file" AND mentions an app, use complex_command
✨ "create folder X" = create_folder action
✨ "move file X to Y" = move_file action
✨ "copy file X to Y" = copy_file action
✨ "switch to X" or "go to X" (for apps) = switch_app action
✨ "switch back" or "previous app" = switch_app with app_name: "previous"
✨ Commands like "save", "copy", "paste", "undo" = app_command action
✨ "type X" or "write X" = app_command with command: "type" and params
✨ Generic text in app context = app_command with type
✨ "go to [WEBSITE]" without "search" = open_website action (e.g., "go to youtube" → youtube.com)
✨ "open [WEBSITE]" without "search" = open_website action (e.g., "open google" → google.com)
✨ "visit [WEBSITE]" = open_website action
✨ "click on [TEXT]" where TEXT is not a number = browser_control with click_by_text
✨ "click on the [NUMBER]" = browser_control with click_nth
✨ "scroll" in browser = browser_control action
✨ "scroll" in app = app_command action
✨ "volume up/down" = browser_control action
✨ "new tab" or "create new tab" = browser_control with new_tab OR app_command (if not browser)
✨ "first tab" or "last tab" = browser_control with first_tab/last_tab
✨ "next tab" or "previous tab" = browser_control with next_tab/previous_tab
✨ "tab X" or "Xth tab" = browser_control with switch_to_tab
✨ "close tab" = browser_control with close_tab OR app_command
✨ "new window" = browser_control with new_window
✨ "incognito" or "private window" = browser_control with incognito_window
✨ "go back" or "go forward" = browser_control with go_back/go_forward
✨ "refresh" or "reload" = browser_control with refresh
✨ "play X" or "play first" (without "on page") = play_media action
✨ "play X on page" or "play video X" = browser_control with play_video
✨ "download research on X" or "fetch research papers" = download_research action
✨ 🔥 "download/install X from/via [SOURCE]" = download_app with source field (CRITICAL!)
✨ "download X" or "install X" (for apps) = download_app action with source: "web" (default)
✨ "open browser and search X" OR "open [BROWSER] and search X" = complex_command: open_app + web_search
✨ Browsers (Chrome, Firefox, Edge, Safari, Brave, Opera) = open_app, NOT platform_search
✨ "open/go to [WEBSITE] and search X" = platform_search (WEBSITE like youtube, instagram, etc.)
✨ "search X on [WEBSITE]" = platform_search
✨ Prefer action over conversation when unsure
✨ 🔥 ALWAYS extract download source if mentioned: "from web", "from snap", "via terminal", etc.
✨ 🔥 App control keywords: save, copy, paste, cut, undo, redo, find, close, bold, italic, etc.

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
            platform_or_browser, query = match2.groups()
            query = query.strip()
            platform_or_browser = platform_or_browser.strip().lower()
            
            browsers = ['chrome', 'firefox', 'edge', 'safari', 'brave', 'opera']
            if any(browser in platform_or_browser for browser in browsers):
                import re
                app_match = re.search(r'(?:open|use)\s+(\w+)', text_lower)
                if app_match:
                    browser_name = app_match.group(1).strip()
                    return {"action": "complex_command", "steps": [
                        {"action": "open_app", "app_name": browser_name},
                        {"action": "web_search", "query": query}
                    ]}
            
            web_indicators = ['youtube', 'google', 'instagram', 'facebook', 'twitter', 'amazon', 
                             'reddit', 'wikipedia', 'spotify', 'linkedin', 'github', 'chatgpt',
                             'netflix', 'pinterest', 'tiktok', 'snapchat', 'whatsapp', 'telegram',
                             'stackoverflow', 'medium', 'quora', 'ebay', 'imdb', 'yelp', 'twitch']
            if any(indicator in platform_or_browser for indicator in web_indicators) or len(platform_or_browser) > 3:
                return {"action": "platform_search", "platform": platform_or_browser, "query": query}
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
        if ('open' in text_lower or 'launch' in text_lower or 'start' in text_lower) and any(word in text_lower for word in ['search', 'searc', 'serch', 'find', 'lookup']) and any(browser in text_lower for browser in ['chrome', 'firefox', 'edge', 'safari', 'brave', 'opera', 'browser']):
            import re
            browsers = ['chrome', 'firefox', 'edge', 'safari', 'brave', 'opera', 'browser']
            for browser in browsers:
                if browser in text_lower:
                    pattern = r'(?:open|launch|start)\s+(' + browser + r')\s+and\s+(?:search|searc|serch|find|lookup)\s+(?:for\s+)?(.+)'
                    match = re.search(pattern, text_lower)
                    if match:
                        browser_name = match.group(1).strip()
                        query = match.group(2).strip()
                        return {"action": "complex_command", "steps": [
                            {"action": "open_app", "app_name": browser_name},
                            {"action": "web_search", "query": query}
                        ]}
        
        if ('open' in text_lower or 'launch' in text_lower or 'start' in text_lower) and ('create' in text_lower or 'make' in text_lower) and 'file' in text_lower:
            import re
            patterns = [
                r'(?:open|launch|start)\s+(.+?)\s+(?:and|,)\s+(?:create|make)\s+(?:and\s+)?(?:open\s+)?(?:a\s+|the\s+)?file\s+(?:called|named|titled)?\s*([^\s]+(?:\.[^\s]+)?)',
                r'(?:open|launch|start)\s+(.+?)\s+and\s+(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)?\s*([^\s]+(?:\.[^\s]+)?)',
                r'(?:open|launch|start)\s+(.+?)\s+and\s+(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
            ]
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    app_name = match.group(1).strip().rstrip(',')
                    file_name = match.group(2).strip().rstrip('.,!?;:')
                    
                    app_name = app_name.replace('vs code', 'vscode').replace('visual studio code', 'vscode').replace(' vs ', ' vscode ')
                    if app_name.lower() == 'vs' or app_name.lower().strip() == 'vs':
                        app_name = 'vscode'
                    
                    if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the', 'it']:
                        return {"action": "complex_command", "steps": [
                            {"action": "open_app", "app_name": app_name},
                            {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": app_name}
                        ]}
        
        if text_lower.startswith(('search ', 'google ', 'find ', 'lookup ')):
            query = text_lower.split(None, 1)[1] if len(text_lower.split()) > 1 else text_lower
            return {"action": "web_search", "query": query}
        elif text_lower.startswith(('switch to ', 'switch back', 'go to ', 'focus on ')):
            if 'switch back' in text_lower or 'previous app' in text_lower:
                return {"action": "switch_app", "app_name": "previous"}
            
            app_name = text_lower
            for prefix in ['switch to ', 'go to ', 'focus on ']:
                if text_lower.startswith(prefix):
                    app_name = text_lower[len(prefix):].strip()
                    break
            
            app_keywords = ['chrome', 'firefox', 'vscode', 'code', 'terminal', 'calculator', 
                           'notepad', 'word', 'excel', 'browser', 'spotify', 'discord', 
                           'steam', 'vlc', 'gimp', 'photoshop']
            
            if any(keyword in app_name for keyword in app_keywords):
                return {"action": "switch_app", "app_name": app_name}
        
        elif text_lower.startswith(('open ', 'launch ', 'start ', 'run ')):
            app_name = text_lower.split(None, 1)[1] if len(text_lower.split()) > 1 else text_lower
            
            if ('and' in app_name.lower() or ',' in app_name.lower()) and ('create' in app_name.lower() or 'make' in app_name.lower()) and 'file' in app_name.lower():
                import re
                app_name_normalized = app_name.lower().replace(',', ' and ')
                patterns = [
                    r'^(.+?)\s+and\s+(?:create|make)\s+(?:and\s+)?(?:open\s+)?(?:a\s+|the\s+)?file\s+(?:called|named|titled)?\s*([^\s]+(?:\.[^\s]+)?)',
                    r'^(.+?)\s+and\s+(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)?\s*([^\s]+(?:\.[^\s]+)?)',
                    r'^(.+?)\s+and\s+(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, app_name_normalized)
                    if match:
                        actual_app = match.group(1).strip().rstrip(',')
                        file_name = match.group(2).strip().rstrip('.,!?;:')
                        
                        actual_app = actual_app.replace('vs code', 'vscode').replace('visual studio code', 'vscode').replace(' vs ', ' vscode ')
                        if actual_app.lower() == 'vs' or actual_app.lower().strip() == 'vs':
                            actual_app = 'vscode'
                        
                        if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the', 'it']:
                            return {"action": "complex_command", "steps": [
                                {"action": "open_app", "app_name": actual_app},
                                {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": actual_app}
                            ]}
            
            search_variations = ['search', 'searc', 'serch', 'find', 'lookup']
            has_search = any(var in app_name.lower() for var in search_variations)
            
            if ('and' in app_name.lower() or ',' in app_name.lower()) and has_search:
                import re
                app_name_normalized = app_name.lower().replace(',', ' and ')
                browsers = ['chrome', 'firefox', 'edge', 'safari', 'brave', 'opera', 'browser']
                
                for browser in browsers:
                    if browser in app_name_normalized:
                        pattern = r'^(.+?)\s+and\s+(?:search|searc|serch|find|lookup)\s+(?:for\s+)?(.+)'
                        match = re.search(pattern, app_name_normalized)
                        if match:
                            browser_name = match.group(1).strip()
                            query = match.group(2).strip()
                            if any(b in browser_name for b in browsers):
                                return {"action": "complex_command", "steps": [
                                    {"action": "open_app", "app_name": browser_name},
                                    {"action": "web_search", "query": query}
                                ]}
                
                parts = app_name.split('and')
                if len(parts) >= 2:
                    browser_or_app = parts[0].strip().lower()
                    query_parts = []
                    for part in parts[1:]:
                        cleaned = part.replace('search', '').replace('searc', '').replace('serch', '').replace('find', '').replace('lookup', '').strip()
                        if cleaned:
                            query_parts.append(cleaned)
                    query = ' '.join(query_parts).strip()
                    
                    if any(browser in browser_or_app for browser in browsers):
                        return {"action": "complex_command", "steps": [
                            {"action": "open_app", "app_name": parts[0].strip()},
                            {"action": "web_search", "query": query}
                        ]}
                    
                    return {"action": "platform_search", "platform": parts[0].strip(), "query": query}
            
            if app_name.lower() in ['vs', 'vscode', 'visual studio', 'visual studio code', 'code']:
                app_name = 'vscode'
            
            return {"action": "open_app", "app_name": app_name}
        
        elif 'create file' in text_lower or 'make file' in text_lower:
            import re
            patterns = [
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)\s+([^\s]+(?:\.[^\s]+)?(?:\s|$))',
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s+and|\s+in|\s+to|$)',
            ]
            for pattern in patterns:
                file_match = re.search(pattern, text_lower)
                if file_match:
                    file_name = file_match.group(1).strip()
                    file_name = file_name.rstrip('.,!?;:')
                    if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the']:
                        open_in_app = None
                        if 'vscode' in text_lower or 'visual studio' in text_lower or 'code' in text_lower:
                            open_in_app = 'vscode'
                        return {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": open_in_app}
        
        elif ('create' in text_lower or 'make' in text_lower) and 'file' in text_lower:
            import re
            app_mentioned = None
            app_keywords = {
                'vscode': ['vscode', 'vs code', 'visual studio code', 'code editor'],
                'chrome': ['chrome', 'browser', 'google chrome'],
                'firefox': ['firefox'],
                'notepad': ['notepad'],
            }
            
            for app_key, keywords in app_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        app_mentioned = app_key
                        break
                if app_mentioned:
                    break
            
            if 'open it' in text_lower or 'open in' in text_lower or app_mentioned:
                file_patterns = [
                    r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)?\s*([^\s]+(?:\.[^\s]+)?)',
                    r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
                ]
                for pattern in file_patterns:
                    file_match = re.search(pattern, text_lower)
                    if file_match:
                        file_name = file_match.group(1).strip()
                        file_name = file_name.rstrip('.,!?;:')
                        if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the', 'it']:
                            target_app = app_mentioned if app_mentioned else 'vscode'
                            return {"action": "complex_command", "steps": [
                                {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": target_app}
                            ]}
            
            file_patterns = [
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)\s+([^\s]+(?:\.[^\s]+)?(?:\s|$))',
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s+and|\s+in|\s+to|$)',
            ]
            for pattern in file_patterns:
                file_match = re.search(pattern, text_lower)
                if file_match:
                    file_name = file_match.group(1).strip()
                    file_name = file_name.rstrip('.,!?;:')
                    if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the']:
                        open_in_app = app_mentioned
                        if 'vscode' in text_lower or 'visual studio' in text_lower or 'code' in text_lower:
                            open_in_app = 'vscode'
                        return {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": open_in_app}
        
        elif 'open' in text_lower and ('create' in text_lower or 'make' in text_lower) and 'file' in text_lower:
            import re
            patterns = [
                r'open\s+([^\s]+(?:\s+[^\s]+)*?)\s+and\s+(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)\s+([^\s]+(?:\.[^\s]+)?(?:\s|$))',
                r'open\s+([^\s]+(?:\s+[^\s]+)*?)\s+and\s+(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
            ]
            for pattern in patterns:
                app_match = re.search(pattern, text_lower)
                if app_match:
                    app_name = app_match.group(1).strip()
                    file_name = app_match.group(2).strip()
                    file_name = file_name.rstrip('.,!?;:')
                    if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the']:
                        app_name = app_name.replace('vs code', 'vscode').replace('visual studio code', 'vscode')
                        return {"action": "complex_command", "steps": [
                            {"action": "open_app", "app_name": app_name},
                            {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": app_name}
                        ]}
        
        elif text_lower.startswith(('type ', 'write ', 'enter ')):
            text_to_type = text_lower
            for prefix in ['type ', 'write ', 'enter ']:
                if text_lower.startswith(prefix):
                    text_to_type = text[len(prefix):].strip()
                    break
            return {"action": "app_command", "command": "type", "params": {"text": text_to_type}}
        
        elif any(cmd in text_lower for cmd in ['save', 'copy', 'paste', 'cut', 'undo', 'redo', 
                                                 'select all', 'bold', 'italic', 'underline',
                                                 'find', 'replace']):
            for cmd in ['save file', 'save', 'copy', 'paste', 'cut', 'undo', 'redo', 
                       'select all', 'bold', 'italic', 'underline', 'find', 'replace']:
                if cmd in text_lower:
                    return {"action": "app_command", "command": cmd}
        elif text_lower.startswith(('play ', 'play the ', 'play first ')):
            query = text_lower.replace('play ', '').replace('the ', '').replace('first ', '').strip()
            return {"action": "play_media", "query": query, "platform": "youtube"}
        elif 'research' in text_lower and ('download' in text_lower or 'fetch' in text_lower or 'get' in text_lower):
            topic = text_lower
            for remove in ['download', 'fetch', 'get', 'me', 'all', 'research', 'of', 'on', 'about', 'for']:
                topic = topic.replace(remove, '')
            topic = topic.strip()
            return {"action": "download_research", "topic": topic, "max_papers": 5}
        elif text_lower.startswith(('download ', 'install ', 'get ')):
            app_name = text_lower.split(None, 1)[1] if len(text_lower.split()) > 1 else text_lower
            app_name = app_name.replace('for me', '').strip()
            
            # Check for research download
            if 'research' in app_name or 'papers' in app_name:
                topic = app_name.replace('research', '').replace('papers', '').replace('on', '').replace('about', '').strip()
                return {"action": "download_research", "topic": topic, "max_papers": 5}
            
            # Detect download source
            source = "web"  # default
            source_patterns = [
                (r'(?:from|via|through|using)\s+(?:the\s+)?(web|internet|online|website)', 'web'),
                (r'(?:from|via|through|using)\s+(?:the\s+)?(terminal|package\s+manager|apt|dnf|brew|choco)', 'terminal'),
                (r'(?:from|via|through|using)\s+(?:the\s+)?(snap(?:\s+store)?)', 'snap'),
                (r'(?:from|via|through|using)\s+(?:the\s+)?(flatpak)', 'flatpak'),
                (r'(?:from|via|through|using)\s+(?:the\s+)?(app\s+store|microsoft\s+store|mac\s+app\s+store|gnome\s+software)', 'appstore'),
            ]
            
            for pattern, src in source_patterns:
                match = re.search(pattern, app_name)
                if match:
                    source = src
                    # Remove the source specification from app_name
                    app_name = re.sub(pattern, '', app_name).strip()
                    break
            
            return {"action": "download_app", "app_name": app_name, "source": source}
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
        
        # Tab management
        elif re.search(r'(create|open|new)\s+(?:a\s+)?(?:new\s+)?tab', text_lower):
            url_match = re.search(r'(?:and\s+)?(?:open|go to)\s+(\w+(?:\.\w+)?)', text_lower)
            if url_match:
                url = url_match.group(1)
                return {"action": "browser_control", "command": "new_tab", "url": url}
            return {"action": "browser_control", "command": "new_tab"}
        elif re.search(r'(switch to|go to|move to)\s+first\s+tab', text_lower):
            return {"action": "browser_control", "command": "first_tab"}
        elif re.search(r'(switch to|go to|move to)\s+last\s+tab', text_lower):
            return {"action": "browser_control", "command": "last_tab"}
        elif re.search(r'(switch to|go to|move to)\s+next\s+tab', text_lower) or 'next tab' in text_lower:
            return {"action": "browser_control", "command": "next_tab"}
        elif re.search(r'(switch to|go to|move to)\s+prev(?:ious)?\s+tab', text_lower) or 'previous tab' in text_lower:
            return {"action": "browser_control", "command": "previous_tab"}
        elif re.search(r'(switch to|go to|move to)\s+tab\s+(\d+)', text_lower):
            match = re.search(r'(switch to|go to|move to)\s+tab\s+(\d+)', text_lower)
            tab_index = int(match.group(2))
            return {"action": "browser_control", "command": "switch_to_tab", "tab_index": tab_index}
        elif re.search(r'(switch to|go to|move to)\s+(\d+)(?:st|nd|rd|th)\s+tab', text_lower):
            match = re.search(r'(switch to|go to|move to)\s+(\d+)(?:st|nd|rd|th)\s+tab', text_lower)
            tab_index = int(match.group(2))
            return {"action": "browser_control", "command": "switch_to_tab", "tab_index": tab_index}
        elif re.search(r'close\s+(?:this\s+|current\s+)?tab', text_lower):
            return {"action": "browser_control", "command": "close_tab"}
        elif re.search(r'close\s+(?:all\s+)?other\s+tabs', text_lower):
            return {"action": "browser_control", "command": "close_other_tabs"}
        elif re.search(r'(list|show)\s+(?:all\s+)?tabs', text_lower):
            return {"action": "browser_control", "command": "list_tabs"}
        
        # Window management
        elif re.search(r'(create|open|new)\s+(?:a\s+)?(?:new\s+)?window', text_lower):
            return {"action": "browser_control", "command": "new_window"}
        elif re.search(r'(create|open|new)\s+(?:an?\s+)?(?:incognito|private)\s+window', text_lower):
            return {"action": "browser_control", "command": "incognito_window"}
        elif 'maximize' in text_lower and 'window' in text_lower:
            return {"action": "browser_control", "command": "maximize"}
        elif 'minimize' in text_lower and 'window' in text_lower:
            return {"action": "browser_control", "command": "minimize"}
        elif 'fullscreen' in text_lower or 'full screen' in text_lower:
            return {"action": "browser_control", "command": "fullscreen"}
        
        # Navigation
        elif re.search(r'\bgo\s+back\b|\bback\b', text_lower) and 'go back' not in ['go to back', 'search go back']:
            return {"action": "browser_control", "command": "go_back"}
        elif re.search(r'\bgo\s+forward\b|\bforward\b', text_lower):
            return {"action": "browser_control", "command": "go_forward"}
        elif 'refresh' in text_lower or 'reload' in text_lower:
            return {"action": "browser_control", "command": "refresh"}
        elif re.search(r'(what\s+is|show|get|tell)\s+(the\s+)?current\s+url', text_lower):
            return {"action": "browser_control", "command": "get_url"}
        elif re.search(r'(what\s+is|show|get|tell)\s+(the\s+)?page\s+title', text_lower):
            return {"action": "browser_control", "command": "get_title"}
        elif 'click' in text_lower and 'first' in text_lower:
            return {"action": "browser_control", "command": "click_first_link"}
        elif any(word in text_lower for word in ['press enter', 'hit enter', 'press return']):
            return {"action": "app_command", "command": "enter"}
        
        elif any(word in text_lower for word in ['press escape', 'hit escape', 'press esc']):
            return {"action": "app_command", "command": "escape"}
        
        elif any(word in text_lower for word in ['press tab', 'hit tab']):
            return {"action": "app_command", "command": "tab"}
        
        elif 'delete' in text_lower or 'backspace' in text_lower:
            return {"action": "app_command", "command": "delete"}
        
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
        if ('create' in text_lower or 'make' in text_lower) and 'file' in text_lower:
            import re
            app_mentioned = None
            app_keywords = {
                'vscode': ['vscode', 'vs code', 'visual studio code', 'code editor'],
                'chrome': ['chrome', 'browser', 'google chrome'],
                'firefox': ['firefox'],
                'notepad': ['notepad'],
            }
            
            for app_key, keywords in app_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        app_mentioned = app_key
                        break
                if app_mentioned:
                    break
            
            if 'open it' in text_lower or 'open in' in text_lower or app_mentioned:
                file_patterns = [
                    r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)?\s*([^\s]+(?:\.[^\s]+)?)',
                    r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
                ]
                for pattern in file_patterns:
                    file_match = re.search(pattern, text_lower)
                    if file_match:
                        file_name = file_match.group(1).strip()
                        file_name = file_name.rstrip('.,!?;:')
                        if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the', 'it']:
                            target_app = app_mentioned if app_mentioned else 'vscode'
                            return {"action": "complex_command", "steps": [
                                {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": target_app}
                            ]}
        
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