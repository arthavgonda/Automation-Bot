
from CommandClassifier import CommandClassifier, CommandType
from Browser.IntelligentBrowser import EnhancedIntelligentBrowser
from GeminiAPI import GeminiAssistant
from ConfirmationManager import ConfirmationManager
from Application.ApplicationController import ApplicationController
from Application.ContextManager import ContextManager
import platform
import time
from pathlib import Path

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
        self.app_controller = ApplicationController()
        self.context_manager = ContextManager()
        print("✓ Application Controller initialized for app control")
    def process_command(self, transcription):
        if not transcription or transcription.strip() == "":
            return False, "Empty transcription"
        transcription = transcription.strip().rstrip('.,!?;:')
        print(f"\n🎤 {transcription}")
        
        current_context = self.context_manager.get_current_context()
        if current_context:
            print(f"📱 Current context: {current_context}")
        
        if self.confirmation_manager.has_pending():
            return self._handle_confirmation(transcription)
        if self.gemini_available:
            try:
                command_json = self.gemini.parse_command_to_json(transcription)
                print(f"🤖 Action: {command_json.get('action', 'unknown')}")
                action = command_json.get('action', 'unknown')
                
                if action == 'web_search':
                    query = command_json.get('query', '')
                    if any(keyword in query.lower() for keyword in ['create', 'make', 'file']) and 'file' in transcription.lower():
                        print("🔍 Detected file command misclassified as web_search, attempting to parse...")
                        result = self._handle_fallback_file_commands(transcription)
                        if result[0]:
                            return result
                
                if action == 'open_app':
                    app_name = command_json.get('app_name', '')
                    app_name_normalized = app_name.lower().replace(',', ' and ')
                    
                    search_variations = ['search', 'searc', 'serch', 'find', 'lookup']
                    has_search = any(var in app_name_normalized for var in search_variations)
                    browsers = ['chrome', 'firefox', 'edge', 'safari', 'brave', 'opera', 'browser']
                    
                    if ('and' in app_name_normalized or ',' in app_name.lower()) and has_search:
                        import re
                        for browser in browsers:
                            if browser in app_name_normalized:
                                pattern = r'^(.+?)\s+and\s+(?:search|searc|serch|find|lookup)\s+(?:for\s+)?(.+)'
                                match = re.search(pattern, app_name_normalized)
                                if match:
                                    browser_name = match.group(1).strip()
                                    query = match.group(2).strip()
                                    if any(b in browser_name for b in browsers):
                                        return self._execute_complex_command([
                                            {"action": "open_app", "app_name": browser_name},
                                            {"action": "web_search", "query": query}
                                        ])
                    
                    if ('and' in app_name_normalized or ',' in app_name.lower()) and ('create' in app_name_normalized or 'make' in app_name_normalized) and 'file' in app_name_normalized:
                        import re
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
                                    return self._execute_complex_command([
                                        {"action": "open_app", "app_name": actual_app},
                                        {"action": "create_file", "file_path": file_name, "create_folder_if_missing": True, "open_in_app": actual_app}
                                    ])
                    return self._execute_open_app(app_name)
                elif action == 'switch_app':
                    app_name = command_json.get('app_name', '')
                    return self._execute_switch_app(app_name)
                elif action == 'app_command':
                    command = command_json.get('command', '')
                    params = command_json.get('params', {})
                    return self._execute_app_command(command, params)
                elif action == 'clear_context':
                    return self._execute_clear_context()
                elif action == 'web_search':
                    query = command_json.get('query', '')
                    if any(keyword in transcription.lower() for keyword in ['create', 'make']) and 'file' in transcription.lower():
                        print("🔍 Detected file command in web_search, attempting fallback...")
                        result = self._handle_fallback_file_commands(transcription)
                        if result[0]:
                            return result
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
                    source = command_json.get('source', 'web')  # default to web
                    return self._execute_download_app(app_name, source)
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
                elif action == 'complex_command':
                    steps = command_json.get('steps', [])
                    return self._execute_complex_command(steps)
                elif action == 'create_file':
                    file_path = command_json.get('file_path', '')
                    create_folder_if_missing = command_json.get('create_folder_if_missing', True)
                    open_in_app = command_json.get('open_in_app', None)
                    return self._execute_create_file(file_path, create_folder_if_missing, open_in_app)
                elif action == 'create_folder':
                    folder_path = command_json.get('folder_path', '')
                    return self._execute_create_folder(folder_path)
                elif action == 'move_file':
                    source = command_json.get('source', '')
                    destination = command_json.get('destination', '')
                    return self._execute_move_file(source, destination)
                elif action == 'copy_file':
                    source = command_json.get('source', '')
                    destination = command_json.get('destination', '')
                    return self._execute_copy_file(source, destination)
                else:
                    if self.context_manager.is_in_app_context():
                        return self._try_generic_app_command(transcription)
                    if any(keyword in transcription.lower() for keyword in ['create', 'make', 'file', 'folder', 'move', 'copy', 'open app', 'switch']):
                        print(f"⚠ Command not fully recognized, attempting fallback parsing...")
                        return self._handle_conversation(transcription)
                    return self._execute_web_search(transcription)
            except Exception as e:
                print(f"⚠ Gemini parsing failed: {e}")
                if self.context_manager.is_in_app_context():
                    return self._try_generic_app_command(transcription)
                if any(keyword in transcription.lower() for keyword in ['create', 'make', 'file', 'folder']):
                    return self._handle_fallback_file_commands(transcription)
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
                self.context_manager.set_context(app_name)
                print(f"✓ Context set to: {app_name}")
                return True, f"Opened {app_name}"
            else:
                print(f"🌐 App not found, searching online for: {app_name}")
                return self._execute_web_search(app_name)
        return False, "System controller not available"
    
    def _execute_switch_app(self, app_name):
        if not app_name or app_name == 'previous' or app_name == 'back':
            switched_app = self.context_manager.switch_to_previous()
            if switched_app:
                self.app_controller.focus_application(switched_app)
                return True, f"Switched to {switched_app}"
            return False, "No previous application"
        
        if self.context_manager.set_context(app_name):
            success = self.app_controller.focus_application(app_name)
            if success:
                return True, f"Switched to {app_name}"
            return True, f"Context set to {app_name}"
        return False, "Failed to switch application"
    
    def _execute_app_command(self, command, params):
        current_app = self.context_manager.get_current_context()
        if not current_app:
            return False, "No active application context. Say 'Open [app name]' first"
        
        print(f"🎮 Executing '{command}' in {current_app}")
        success = self.app_controller.execute_command(current_app, command, params)
        if success:
            return True, f"Executed: {command}"
        return False, f"Failed to execute: {command}"
    
    def _execute_clear_context(self):
        self.context_manager.clear_context()
        return True, "Application context cleared"
    
    def _execute_complex_command(self, steps):
        results = []
        for i, step in enumerate(steps, 1):
            step_action = step.get('action', '')
            print(f"Step {i}/{len(steps)}: {step_action}")
            
            if step_action == 'open_app':
                success, message = self._execute_open_app(step.get('app_name', ''))
            elif step_action == 'create_file':
                success, message = self._execute_create_file(
                    step.get('file_path', ''),
                    step.get('create_folder_if_missing', True),
                    step.get('open_in_app', None)
                )
            elif step_action == 'create_folder':
                success, message = self._execute_create_folder(step.get('folder_path', ''))
            elif step_action == 'web_search':
                success, message = self._execute_web_search(step.get('query', ''))
            elif step_action == 'switch_app':
                success, message = self._execute_switch_app(step.get('app_name', ''))
            elif step_action == 'app_command':
                success, message = self._execute_app_command(
                    step.get('command', ''),
                    step.get('params', {})
                )
            else:
                success, message = False, f"Unknown step action: {step_action}"
            
            results.append(f"Step {i}: {message}")
            if not success:
                print(f"⚠ Step {i} failed: {message}")
                return False, f"Step {i} failed: {message}"
        
        return True, " | ".join(results)
    
    def _execute_create_file(self, file_path, create_folder_if_missing=True, open_in_app=None):
        if not file_path:
            return False, "No file path provided"
        
        if not self.system_controller:
            return False, "System controller not available"
        
        try:
            import os
            from pathlib import Path
            
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.system_controller.home_dir, file_path)
            
            file_path_obj = Path(file_path)
            folder_path = file_path_obj.parent
            
            folder_created = False
            if create_folder_if_missing and not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                folder_created = True
                print(f"📁 Created folder: {folder_path}")
            
            content = ""
            success = self.system_controller.create_file(str(file_path), content)
            
            if success:
                message = f"Created file: {file_path_obj.name}"
                if folder_created:
                    message += f" | Created folder: {folder_path.name}"
                
                if open_in_app:
                    print(f"Opening {file_path_obj.name} in {open_in_app}")
                    self._execute_switch_app(open_in_app)
                    time.sleep(1.5)
                    
                    if open_in_app.lower() in ['vscode', 'code', 'visual studio code', 'vs']:
                        import subprocess
                        try:
                            subprocess.Popen(['code', str(file_path)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                            message += f" | Opened in {open_in_app}"
                        except FileNotFoundError:
                            try:
                                subprocess.Popen(['code-insiders', str(file_path)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                                message += f" | Opened in {open_in_app}"
                            except FileNotFoundError:
                                ctrl_or_cmd = 'command' if platform.system() == 'Darwin' else 'ctrl'
                                import pyautogui
                                pyautogui.hotkey(ctrl_or_cmd, 'p')
                                time.sleep(0.8)
                                pyautogui.write(str(file_path))
                                time.sleep(0.3)
                                pyautogui.press('enter')
                                message += f" | Opened in {open_in_app}"
                    else:
                        ctrl_or_cmd = 'command' if platform.system() == 'Darwin' else 'ctrl'
                        import pyautogui
                        pyautogui.hotkey(ctrl_or_cmd, 'o')
                        time.sleep(0.8)
                        pyautogui.write(str(file_path))
                        time.sleep(0.3)
                        pyautogui.press('enter')
                        message += f" | Opened in {open_in_app}"
                elif self.context_manager.get_current_context():
                    current_app = self.context_manager.get_current_context()
                    print(f"File created, current context: {current_app}")
                    if current_app.lower() in ['vscode', 'code', 'visual studio code']:
                        time.sleep(1.5)
                        import subprocess
                        try:
                            subprocess.Popen(['code', str(file_path)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                            message += f" | Opened in {current_app}"
                        except FileNotFoundError:
                            try:
                                subprocess.Popen(['code-insiders', str(file_path)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                                message += f" | Opened in {current_app}"
                            except FileNotFoundError:
                                ctrl_or_cmd = 'command' if platform.system() == 'Darwin' else 'ctrl'
                                import pyautogui
                                pyautogui.hotkey(ctrl_or_cmd, 'p')
                                time.sleep(0.8)
                                pyautogui.write(str(file_path))
                                time.sleep(0.3)
                                pyautogui.press('enter')
                                message += f" | Opened in {current_app}"
                
                return True, message
            else:
                return False, "Failed to create file"
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
    
    def _execute_create_folder(self, folder_path):
        if not folder_path:
            return False, "No folder path provided"
        
        if not self.system_controller:
            return False, "System controller not available"
        
        success = self.system_controller.create_folder(folder_path)
        if success:
            folder_name = Path(folder_path).name if '/' in folder_path or '\\' in folder_path else folder_path
            return True, f"Created folder: {folder_name}"
        return False, "Failed to create folder"
    
    def _execute_move_file(self, source, destination):
        if not source or not destination:
            return False, "Source and destination required"
        
        if not self.system_controller:
            return False, "System controller not available"
        
        try:
            import os
            import shutil
            from pathlib import Path
            
            if not os.path.isabs(source):
                source = os.path.join(self.system_controller.home_dir, source)
            if not os.path.isabs(destination):
                destination = os.path.join(self.system_controller.home_dir, destination)
            
            if not os.path.exists(source):
                return False, f"Source file not found: {source}"
            
            dest_path = Path(destination)
            if not dest_path.parent.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created folder: {dest_path.parent}")
            
            shutil.move(source, destination)
            print(f"📦 Moved: {Path(source).name} → {Path(destination).name}")
            return True, f"Moved file to {Path(destination).name}"
        except Exception as e:
            return False, f"Error moving file: {str(e)}"
    
    def _execute_copy_file(self, source, destination):
        if not source or not destination:
            return False, "Source and destination required"
        
        if not self.system_controller:
            return False, "System controller not available"
        
        try:
            import os
            import shutil
            from pathlib import Path
            
            if not os.path.isabs(source):
                source = os.path.join(self.system_controller.home_dir, source)
            if not os.path.isabs(destination):
                destination = os.path.join(self.system_controller.home_dir, destination)
            
            if not os.path.exists(source):
                return False, f"Source file not found: {source}"
            
            dest_path = Path(destination)
            if not dest_path.parent.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created folder: {dest_path.parent}")
            
            shutil.copy2(source, destination)
            print(f"📋 Copied: {Path(source).name} → {Path(destination).name}")
            return True, f"Copied file to {Path(destination).name}"
        except Exception as e:
            return False, f"Error copying file: {str(e)}"
    
    def _try_generic_app_command(self, text):
        current_app = self.context_manager.get_current_context()
        if not current_app:
            return False, "No active context"
        
        text_lower = text.lower()
        params = {'text': text}
        
        if 'type' in text_lower or 'write' in text_lower:
            text_to_type = text
            for prefix in ['type', 'write', 'enter']:
                if text_lower.startswith(prefix):
                    text_to_type = text[len(prefix):].strip()
                    break
            params['text'] = text_to_type
            return self._execute_app_command('type', params)
        
        elif any(word in text_lower for word in ['save', 'copy', 'paste', 'undo', 'redo', 'find', 'close']):
            for cmd in ['save', 'copy', 'paste', 'cut', 'undo', 'redo', 'find', 'select all', 'close']:
                if cmd in text_lower:
                    return self._execute_app_command(cmd, params)
        
        elif 'scroll' in text_lower:
            if 'down' in text_lower:
                return self._execute_app_command('scroll_down', params)
            elif 'up' in text_lower:
                return self._execute_app_command('scroll_up', params)
        
        elif any(word in text_lower for word in ['enter', 'return', 'press enter']):
            return self._execute_app_command('enter', params)
        
        elif any(word in text_lower for word in ['delete', 'backspace']):
            return self._execute_app_command('delete', params)
        
        elif 'tab' in text_lower and 'new' not in text_lower:
            return self._execute_app_command('tab', params)
        
        else:
            pyautogui_text = text
            for remove in ['type', 'write', 'enter', 'please', 'can you']:
                pyautogui_text = pyautogui_text.replace(remove, '')
            pyautogui_text = pyautogui_text.strip()
            
            if len(pyautogui_text) > 2:
                params['text'] = pyautogui_text
                return self._execute_app_command('type', params)
        
        return False, f"Command not recognized in {current_app}"
    
    def _handle_fallback_file_commands(self, text):
        import re
        text_lower = text.lower()
        
        if ('create' in text_lower or 'make' in text_lower) and 'file' in text_lower:
            app_mentioned = None
            app_keywords = {
                'vscode': ['vscode', 'vs code', 'visual studio code'],
                'chrome': ['chrome'],
                'notepad': ['notepad'],
            }
            
            for app_key, keywords in app_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        app_mentioned = app_key
                        break
                if app_mentioned:
                    break
            
            file_patterns = [
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+(?:called|named|titled)?\s*([^\s]+(?:\.[^\s]+)?)',
                r'(?:create|make)\s+(?:a\s+|the\s+)?file\s+([^\s]+(?:\.[^\s]+)?)',
            ]
            
            for pattern in file_patterns:
                file_match = re.search(pattern, text_lower)
                if file_match:
                    file_name = file_match.group(1).strip().rstrip('.,!?;:')
                    if file_name and file_name not in ['called', 'named', 'titled', 'a', 'the', 'it']:
                        target_app = app_mentioned if app_mentioned else ('vscode' if 'open it' in text_lower or 'open in' in text_lower else None)
                        return self._execute_create_file(file_name, True, target_app)
        
        return False, "Could not parse file command"
    
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
    def _execute_download_app(self, app_name, source='web'):
        """
        Download/install application from specified source
        
        Args:
            app_name: Name of the application to install
            source: Installation source - 'web', 'terminal', 'snap', 'flatpak', 'appstore'
        """
        print(f"📥 Downloading/Installing: {app_name} (source: {source})")
        
        if source == 'web':
            # Default: Download from web via browser
            if self.browser:
                print(f"🌐 Opening web download for: {app_name}")
                self.browser.download_and_install(app_name)
                return True, f"Web download initiated for {app_name}"
            else:
                print(f"❌ Browser not available for web download")
                return False, "Browser not available"
                
        elif source == 'terminal':
            # Install via package manager (apt/dnf/brew/choco)
            if self.system_controller:
                print(f"📦 Installing via package manager: {app_name}")
                self.system_controller.install_app_terminal(app_name)
                return True, f"Terminal installation initiated for {app_name}"
            else:
                return False, "System controller not available"
                
        elif source == 'snap':
            # Install via Snap Store
            if self.browser:
                print(f"📦 Installing via Snap: {app_name}")
                self.browser.install_via_snap(app_name)
                return True, f"Snap installation initiated for {app_name}"
            else:
                return False, "Browser not available"
                
        elif source == 'flatpak':
            # Install via Flatpak
            if self.browser:
                print(f"📦 Installing via Flatpak: {app_name}")
                self.browser.install_via_flatpak(app_name)
                return True, f"Flatpak installation initiated for {app_name}"
            else:
                return False, "Browser not available"
                
        elif source == 'appstore':
            # Install via native app store
            if self.browser:
                print(f"🏪 Opening App Store for: {app_name}")
                self.browser.install_via_appstore(app_name)
                return True, f"App Store opened for {app_name}"
            else:
                return False, "Browser not available"
                
        else:
            # Unknown source - fallback to web
            print(f"⚠️ Unknown source '{source}', defaulting to web download")
            return self._execute_download_app(app_name, 'web')
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
                
                # ===== TAB MANAGEMENT =====
                elif command == 'new_tab':
                    url = command_json.get('url', None)
                    success = controller.create_new_tab(url)
                elif command == 'switch_to_tab':
                    tab_index = command_json.get('tab_index', 1)
                    success = controller.switch_to_tab(tab_index)
                elif command == 'first_tab':
                    success = controller.switch_to_first_tab()
                elif command == 'last_tab':
                    success = controller.switch_to_last_tab()
                elif command == 'next_tab':
                    success = controller.switch_to_next_tab()
                elif command == 'previous_tab' or command == 'prev_tab':
                    success = controller.switch_to_previous_tab()
                elif command == 'close_tab':
                    success = controller.close_current_tab()
                elif command == 'close_other_tabs':
                    success = controller.close_other_tabs()
                elif command == 'list_tabs':
                    success = controller.list_all_tabs()
                
                # ===== WINDOW MANAGEMENT =====
                elif command == 'new_window':
                    url = command_json.get('url', None)
                    success = controller.create_new_window(url)
                elif command == 'incognito_window' or command == 'private_window':
                    success = controller.create_incognito_window()
                elif command == 'maximize':
                    success = controller.maximize_window()
                elif command == 'minimize':
                    success = controller.minimize_window()
                elif command == 'fullscreen':
                    success = controller.fullscreen_window()
                
                # ===== NAVIGATION =====
                elif command == 'go_back' or command == 'back':
                    success = controller.go_back()
                elif command == 'go_forward' or command == 'forward':
                    success = controller.go_forward()
                elif command == 'refresh' or command == 'reload':
                    success = controller.refresh_page()
                elif command == 'get_url':
                    url = controller.get_current_url()
                    success = url is not None
                elif command == 'get_title':
                    title = controller.get_page_title()
                    success = title is not None
                
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
        if self.gemini_available:
            try:
                success, response = self.gemini.query(f"Answer this question concisely and clearly: {text}")
                if success:
                    print(f"🤖 {response}")
                    return True, response
            except Exception as e:
                print(f"⚠ Gemini query failed: {e}")
        
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
        if driver:
            try:
                driver.quit()
            except:
                pass
        return True, "Goodbye!"
    success, message = assistant.process_command(transcription)
    return success, message