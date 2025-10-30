
from CommandClassifier import CommandClassifier, CommandType
from Browser.IntelligentBrowser import EnhancedIntelligentBrowser
from GeminiAPI import GeminiAssistant
from ConfirmationManager import ConfirmationManager
import platform

class SmartAssistant:
    def __init__(self, driver=None, system_controller=None):
        self.classifier = CommandClassifier()
        self.driver = driver
        self.system_controller = system_controller
        self.browser = EnhancedIntelligentBrowser(driver, system_controller) if driver else None
        self.platform = platform.system()
        try:
            self.gemini = GeminiAssistant()
            self.gemini_available = True
            print("✓ Gemini AI initialized for intelligent web responses")
        except Exception as e:
            self.gemini = None
            self.gemini_available = False
            print(f"⚠ Gemini AI not available: {e}")
        self.confirmation_manager = ConfirmationManager()
    def process_command(self, transcription):
        if not transcription or transcription.strip() == "":
            return False, "Empty transcription"
        transcription = transcription.strip().rstrip('.,!?;:')
        print(f"\n🎤 {transcription}")
        if self.confirmation_manager.has_pending():
            return self._handle_confirmation(transcription)
        if self.gemini_available:
            try:
                command_json = self.gemini.parse_command_to_json(transcription)
                print(f"🤖 Action: {command_json.get('action', 'unknown')}")
                action = command_json.get('action', 'unknown')
                if action == 'open_app':
                    app_name = command_json.get('app_name', '')
                    return self._execute_open_app(app_name)
                elif action == 'web_search':
                    query = command_json.get('query', '')
                    return self._execute_web_search(query)
                elif action == 'platform_search':
                    platform = command_json.get('platform', 'google')
                    query = command_json.get('query', '')
                    return self._execute_platform_search(platform, query)
                elif action == 'list_apps':
                    return self._execute_list_apps()
                elif action == 'play_media':
                    query = command_json.get('query', '')
                    platform = command_json.get('platform', 'youtube')
                    return self._execute_play_media(query, platform)
                elif action == 'download_app':
                    app_name = command_json.get('app_name', '')
                    return self._execute_download_app(app_name)
                elif action == 'download_research':
                    topic = command_json.get('topic', '')
                    max_papers = command_json.get('max_papers', 5)
                    return self._execute_download_research(topic, max_papers)
                elif action == 'open_website':
                    url = command_json.get('url', '')
                    return self._execute_open_website(url)
                elif action == 'browser_control':
                    command = command_json.get('command', '')
                    return self._execute_browser_control(command_json)
                elif action == 'conversation':
                    text = command_json.get('text', transcription)
                    return self._handle_conversation(text)
                else:
                    return self._execute_web_search(transcription)
            except Exception as e:
                print(f"⚠ Gemini parsing failed: {e}")
                pass
        cmd_type, confidence, reasoning = self.classifier.classify(transcription)
        if cmd_type == CommandType.SYSTEM:
            return self._handle_system_command(transcription)
        elif cmd_type == CommandType.WEB:
            return self._handle_web_query(transcription)
        else:
            return self._handle_conversation(transcription)
    def _execute_open_app(self, app_name):
        if self.system_controller:
            success = self.system_controller.open_app(app_name)
            if success:
                return True, f"Opened {app_name}"
            else:
                print(f"🌐 App not found, searching online for: {app_name}")
                return self._execute_web_search(app_name)
        return False, "System controller not available"
    def _execute_web_search(self, query):
        if self.browser:
            try:
                self.browser.search_google(query)
                return True, f"Searched for: {query}"
            except Exception as e:
                print(f"❌ Search failed: {e}")
                return False, str(e)
        else:
            if self.gemini_available:
                try:
                    response = self.gemini.search_and_respond(query)
                    print(f"🤖 {response}")
                    return True, response
                except:
                    pass
            return False, "Browser not available"
    def _execute_platform_search(self, platform, query):
        if self.browser:
            try:
                self.browser.search_on_platform(query, platform)
                return True, f"Searched '{query}' on {platform}"
            except Exception as e:
                print(f"❌ Platform search failed: {e}")
                return False, str(e)
        return False, "Browser not available"
    def _execute_list_apps(self):
        if self.system_controller:
            self.system_controller.list_installed_apps()
            return True, "Listed apps"
        return False, "System controller not available"
    def _execute_play_media(self, query, platform):
        if self.browser:
            try:
                print(f"🎵 Playing first result for: {query}")
                self.browser.play_first_result(query, platform)
                return True, f"Playing: {query}"
            except Exception as e:
                print(f"❌ Play failed: {e}")
                return False, str(e)
        return False, "Browser not available"
    def _execute_download_app(self, app_name):
        if self.system_controller:
            print(f"📥 Downloading/Installing: {app_name}")
            success = self.system_controller.download_and_install_app(app_name)
            if success:
                return True, f"Installed {app_name}"
            else:
                print(f"⚠ Not found in package managers, searching web for: {app_name} download")
                if self.browser:
                    self.browser.search_google(f"{app_name} download")
                    return True, f"Opened web search for {app_name}"
                return False, f"Failed to install {app_name}"
        return False, "System controller not available"
    def _execute_download_research(self, topic, max_papers=5):
        if self.browser:
            try:
                print(f"📚 Downloading research papers on: {topic}")
                success = self.browser.download_research(topic, max_papers)
                if success:
                    return True, f"Downloaded research on {topic}"
                else:
                    return False, "No papers found"
            except Exception as e:
                print(f"❌ Research download failed: {e}")
                return False, str(e)
        return False, "Browser not available"
    def _execute_open_website(self, url):
        if self.browser:
            try:
                if not url.startswith(('http://', 'https://')):
                    url = f'https://{url}'
                print(f"🌐 Opening: {url}")
                self.browser.open_website(url)
                return True, f"Opened {url}"
            except Exception as e:
                print(f"❌ Failed to open website: {e}")
                return False, str(e)
        return False, "Browser not available"
    def _handle_confirmation(self, transcription):
        text_lower = transcription.lower().strip()
        if any(word in text_lower for word in ['yes', 'yeah', 'yep', 'correct', 'right', 'ha', 'haan', 'ok', 'okay']):
            print("✅ Confirmed!")
            element = self.confirmation_manager.confirm()
            if element and self.browser:
                self.browser.browser_controller.remove_highlight()
                try:
                    self.browser.driver.execute_script("arguments[0].click();", element)
                    print("✓ Clicked confirmed element!")
                    return True, "Clicked"
                except Exception as e:
                    print(f"❌ Click failed: {e}")
                    return False, str(e)
        elif any(word in text_lower for word in ['no', 'nope', 'wrong', 'nahi', 'naa', 'cancel']):
            print("❌ Rejected - Please try again")
            if self.browser:
                self.browser.browser_controller.remove_highlight()
            self.confirmation_manager.reject()
            return False, "Rejected - please speak again"
        else:
            print("⚠ Please say 'yes' or 'no'")
            return False, "Please confirm with yes or no"
        return False, "Confirmation cancelled"
    def _execute_browser_control(self, command_json):
        if self.browser:
            try:
                command = command_json.get('command', '')
                controller = self.browser.browser_controller
                if command == 'show_page':
                    page_reader = self.browser.page_reader
                    summary = page_reader.get_page_summary()
                    success = summary is not None
                elif command == 'click_first_link':
                    success = controller.click_first_link()
                elif command == 'click_by_text':
                    text = command_json.get('text', '')
                    success = self._smart_click_with_confirmation(text)
                elif command == 'click_nth':
                    n = command_json.get('position', 1)
                    element_type = command_json.get('element_type', 'link')
                    success = controller.click_nth_element(n, element_type)
                elif command == 'scroll_down':
                    success = controller.scroll_down()
                elif command == 'scroll_up':
                    success = controller.scroll_up()
                elif command == 'close_popup':
                    success = controller.close_popup()
                elif command == 'volume_up':
                    success = controller.volume_up()
                elif command == 'volume_down':
                    success = controller.volume_down()
                elif command == 'play_video':
                    title = command_json.get('title', '')
                    success = controller.play_video_by_title(title)
                else:
                    print(f"Unknown browser command: {command}")
                    success = False
                return success, f"Executed: {command}"
            except Exception as e:
                print(f"❌ Browser control failed: {e}")
                return False, str(e)
        return False, "Browser not available"
    def _smart_click_with_confirmation(self, text):
        try:
            page_reader = self.browser.page_reader
            controller = self.browser.browser_controller
            success = controller.click_element_by_text(text, page_reader)
            if not success:
                print(f"\n🔍 Exact match not found. Searching for similar elements...")
                match = page_reader.find_closest_match(text, threshold=0.4)
                if match:
                    controller.highlight_element(match['element'])
                    print(f"\n🤔 Did you mean: '{match['text']}'?")
                    print(f"   (Similarity: {match['score']:.0%})")
                    print(f"\n💬 Please say 'YES' to click or 'NO' to try again\n")
                    self.confirmation_manager.set_pending(
                        match['element'],
                        match['text'],
                        text
                    )
                    return True
                else:
                    print("\n❌ Could not find any similar elements on the page")
                    print("💬 Please try describing it differently or say 'show page' to see all elements\n")
                    return False
            return success
        except Exception as e:
            print(f"❌ Smart click failed: {e}")
            return False
    def _handle_system_command(self, text):
        if self.system_controller:
            try:
                if self.browser:
                    result = self.browser.execute_command(text)
                    return True, "System command executed"
                else:
                    self._execute_system_operation(text)
                    return True, "System command executed"
            except Exception as e:
                print(f"❌ {e}")
                return False, f"Error: {e}"
        else:
            return False, "System controller not available"
    def _handle_web_query(self, text):
        if self.gemini_available and not self._is_url(text):
            try:
                query = self._clean_search_query(text)
                response = self.gemini.search_and_respond(query)
                print(f"🤖 {response}\n")
                return True, response
            except Exception as e:
                pass
        if self.browser:
            try:
                if self._is_url(text):
                    self.browser.open_website(text)
                else:
                    query = self._clean_search_query(text)
                    self.browser.search_google(query)
                return True, "Web search executed in browser"
            except Exception as e:
                print(f"❌ Web query error: {e}")
                return False, f"Error: {e}"
        else:
            return False, "Neither Gemini nor browser available for web queries"
    def _handle_conversation(self, text):
        response = self._generate_response(text)
        print(f"🤖 {response}")
        return True, response
    def _execute_system_operation(self, text):
        text_lower = text.lower()
        if any(word in text_lower for word in ['create', 'make', 'banao']):
            if 'file' in text_lower:
                self.system_controller.create_file(self._extract_filename(text))
            elif any(word in text_lower for word in ['folder', 'directory']):
                self.system_controller.create_folder(self._extract_filename(text))
        elif any(word in text_lower for word in ['delete', 'remove', 'hatao']):
            if 'file' in text_lower:
                self.system_controller.delete_file(self._extract_filename(text))
            elif any(word in text_lower for word in ['folder', 'directory']):
                self.system_controller.delete_folder(self._extract_filename(text))
        elif any(word in text_lower for word in ['system info', 'system information']):
            self.system_controller.get_system_info()
        elif 'app store' in text_lower or 'store' in text_lower:
            self.system_controller.open_app_store()
    def _is_url(self, text):
        import re
        url_pattern = r'(https?://|www\.|\w+\.(com|org|net|in|co|io))'
        return bool(re.search(url_pattern, text.lower()))
    def _clean_search_query(self, text):
        remove_patterns = [
            r'^(search|google|find|look up|browse|dhundo|search karo)\s+',
            r'^(what is|who is|what are|kya hai|kaun hai)\s+',
            r'^(tell me|batao|bata)\s+(about|regarding|ke bare)?\s*',
            r'\s+(online|on internet|internet par)$',
        ]
        import re
        cleaned = text
        for pattern in remove_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
    def _extract_filename(self, text):
        import re
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[0]
        named_match = re.search(r'(?:named|called|naam)\s+(\w+)', text, re.IGNORECASE)
        if named_match:
            return named_match.group(1)
        words = text.split()
        if words:
            return words[-1]
        return "untitled"
    def _generate_response(self, text):
        text_lower = text.lower()
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            return "Hello! I'm your voice assistant. How can I help you today?"
        if any(word in text_lower for word in ['how are you', 'kaise ho', 'kya hal']):
            return "I'm working great! Ready to help you with any task. What would you like me to do?"
        if any(word in text_lower for word in ['who are you', 'what are you', 'tum kaun']):
            return "I'm your intelligent voice assistant. I can help you with system commands, web searches, and answer questions in English, Hindi, or Hinglish!"
        if 'can you' in text_lower or 'what can you do' in text_lower:
            return "I can: (1) Control your computer - open apps, create files, manage system. (2) Search the web and browse websites. (3) Answer your questions and have conversations. All in English, Hindi, or Hinglish!"
        if any(word in text_lower for word in ['thank', 'thanks', 'dhanyavad', 'shukriya']):
            return "You're welcome! Happy to help anytime."
        if 'help' in text_lower or 'madad' in text_lower:
            return "I can help you with:\n- System commands (open apps, files)\n- Web searches (any information)\n- Conversations (questions, chat)\nJust speak naturally in English, Hindi, or Hinglish!"
        return "I understand. Is there anything specific you'd like me to do? I can control your system, search the web, or answer questions."


def process_voice_command_smart(driver, system_controller, transcription):
    assistant = SmartAssistant(driver, system_controller)
    exit_commands = ["exit", "quit", "close", "stop", "close browser", "band karo", "bund karo"]
    if any(cmd in transcription.lower() for cmd in exit_commands):
        print("Goodbye!")
        if driver:
            driver.quit()
        return "EXIT"
    success, message = assistant.process_command(transcription)
    return "CONTINUE"