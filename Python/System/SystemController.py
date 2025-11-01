import os
import platform
import subprocess
import shutil
from pathlib import Path
from difflib import SequenceMatcher

class SystemController:
    def __init__(self):
        self.system = platform.system()
        self.home_dir = Path.home()
        self.installed_apps = {}
        self._discover_installed_apps()
    def create_folder(self, folder_path):
        try:
            if not os.path.isabs(folder_path):
                folder_path = self.home_dir / folder_path
            else:
                folder_path = Path(folder_path)
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"Folder created: {folder_path}")
            return True
        except Exception as e:
            print(f"Failed to create folder: {e}")
            return False
    def delete_folder(self, folder_path):
        try:
            if not os.path.isabs(folder_path):
                folder_path = self.home_dir / folder_path
            else:
                folder_path = Path(folder_path)
            if not folder_path.exists():
                print(f"Folder does not exist: {folder_path}")
                return False
            critical_paths = [
                self.home_dir,
                Path("/"),
                Path("C:\\") if self.system == "Windows" else None,
                self.home_dir / "Documents",
                self.home_dir / "Desktop",
            ]
            if folder_path in [p for p in critical_paths if p]:
                print(f"Cannot delete critical system folder: {folder_path}")
                return False
            shutil.rmtree(folder_path)
            print(f"Folder deleted: {folder_path}")
            return True
        except Exception as e:
            print(f"Failed to delete folder: {e}")
            return False
    def create_file(self, file_path, content=""):
        try:
            if not os.path.isabs(file_path):
                file_path = self.home_dir / file_path
            else:
                file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"File created: {file_path}")
            return True
        except Exception as e:
            print(f"Failed to create file: {e}")
            return False
    def delete_file(self, file_path):
        try:
            if not os.path.isabs(file_path):
                file_path = self.home_dir / file_path
            else:
                file_path = Path(file_path)
            if not file_path.exists():
                print(f"File does not exist: {file_path}")
                return False
            if not file_path.is_file():
                print(f"Not a file: {file_path}")
                return False
            file_path.unlink()
            print(f"File deleted: {file_path}")
            return True
        except Exception as e:
            print(f"Failed to delete file: {e}")
            return False
    def _discover_installed_apps(self):
        try:
            if self.system == "Linux":
                self._discover_linux_apps()
            elif self.system == "Windows":
                self._discover_windows_apps()
            elif self.system == "Darwin":
                self._discover_macos_apps()
        except Exception as e:
            self.installed_apps = {}
    def _discover_linux_apps(self):
        desktop_paths = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            str(self.home_dir / '.local/share/applications'),
            '/var/lib/snapd/desktop/applications',
            '/var/lib/flatpak/exports/share/applications',
        ]
        for desktop_path in desktop_paths:
            if not os.path.exists(desktop_path):
                continue
            try:
                for file in os.listdir(desktop_path):
                    if file.endswith('.desktop'):
                        desktop_file = os.path.join(desktop_path, file)
                        self._parse_desktop_file(desktop_file)
            except Exception as e:
                continue
    def _parse_desktop_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                name = None
                exec_cmd = None
                no_display = False
                for line in f:
                    line = line.strip()
                    if line.startswith('Name=') and not line.startswith('Name['):
                        name = line.split('=', 1)[1].strip()
                    elif line.startswith('Exec='):
                        exec_cmd = line.split('=', 1)[1].strip()
                        exec_cmd = exec_cmd.split()[0] if exec_cmd else None
                    elif line.startswith('NoDisplay=true'):
                        no_display = True
                if name and exec_cmd and not no_display:
                    self.installed_apps[name.lower()] = exec_cmd
                    clean_name = ''.join(c.lower() for c in name if c.isalnum() or c.isspace())
                    if clean_name != name.lower():
                        self.installed_apps[clean_name] = exec_cmd
                    words = name.lower().split()
                    if len(words) > 1:
                        abbrev = ''.join(w[0] for w in words if w)
                        if len(abbrev) > 1 and abbrev not in self.installed_apps:
                            self.installed_apps[abbrev] = exec_cmd
        except Exception as e:
            pass
    def _discover_windows_apps(self):
        start_menu_paths = [
            os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'Microsoft\\Windows\\Start Menu\\Programs'),
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
        ]
        for start_menu in start_menu_paths:
            if os.path.exists(start_menu):
                try:
                    for root, dirs, files in os.walk(start_menu):
                        for file in files:
                            if file.endswith('.lnk'):
                                app_name = file[:-4].lower()
                                self.installed_apps[app_name] = file[:-4]
                                clean_name = ''.join(c.lower() for c in app_name if c.isalnum() or c.isspace())
                                if clean_name != app_name:
                                    self.installed_apps[clean_name] = file[:-4]
                except:
                    pass
        program_files = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
        ]
        for base_path in program_files:
            if not os.path.exists(base_path):
                continue
            try:
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        self.installed_apps[item.lower()] = item
                        try:
                            for file in os.listdir(item_path):
                                if file.endswith('.exe'):
                                    app_name = file[:-4].lower()
                                    self.installed_apps[app_name] = file[:-4]
                        except:
                            pass
            except:
                continue
        try:
            import winreg
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            for reg_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if app_name:
                                    self.installed_apps[app_name.lower()] = app_name
                                    clean_name = ''.join(c.lower() for c in app_name if c.isalnum() or c.isspace())
                                    if clean_name != app_name.lower():
                                        self.installed_apps[clean_name] = app_name
                            except:
                                pass
                            winreg.CloseKey(subkey)
                        except:
                            pass
                    winreg.CloseKey(key)
                except:
                    pass
        except ImportError:
            pass
    def _discover_macos_apps(self):
        app_paths = [
            '/Applications',
            '/System/Applications',
            '/System/Library/CoreServices/Applications',
            str(self.home_dir / 'Applications'),
            '/Applications/Utilities',
        ]
        for app_path in app_paths:
            if not os.path.exists(app_path):
                continue
            try:
                for item in os.listdir(app_path):
                    if item.endswith('.app'):
                        full_name = item[:-4]
                        app_name = full_name.lower()
                        self.installed_apps[app_name] = full_name
                        clean_name = ''.join(c.lower() for c in full_name if c.isalnum() or c.isspace())
                        if clean_name != app_name:
                            self.installed_apps[clean_name] = full_name
                        if ' ' in app_name:
                            words = app_name.split()
                            if len(words) > 1:
                                abbrev = ''.join(w[0] for w in words if w)
                                if len(abbrev) > 1:
                                    self.installed_apps[abbrev] = full_name
            except:
                continue
    def _fuzzy_match_app(self, query):
        if not self.installed_apps:
            return None
        best_match = None
        best_score = 0.0
        min_threshold = 0.5
        query_lower = query.lower()
        query_words = query_lower.split()
        query_length = len(query_lower)
        all_apps = list(self.installed_apps.keys())
        for app_name in all_apps:
            app_lower = app_name.lower()
            app_length = len(app_lower)
            app_words = app_lower.split()
            if app_length < 3 and query_lower != app_lower:
                continue
            length_ratio = min(query_length, app_length) / max(query_length, app_length)
            if length_ratio < 0.3:
                continue
            if query_lower in app_lower or app_lower in query_lower:
                score = 0.9 * length_ratio
            else:
                char_score = SequenceMatcher(None, query_lower, app_lower).ratio()
                word_matches = 0
                for qw in query_words:
                    if len(qw) < 3:
                        continue
                    for aw in app_words:
                        if len(aw) < 3:
                            continue
                        if qw in aw or aw in qw:
                            word_matches += 1
                            break
                        elif len(qw) > 3 and len(aw) > 3:
                            word_sim = SequenceMatcher(None, qw, aw).ratio()
                            if word_sim >= 0.7:
                                word_matches += 0.7
                                break
                word_score = word_matches / max(len(query_words), len(app_words)) if query_words else 0
                score = (char_score * 0.3) + (word_score * 0.7)
            if score > best_score and score >= min_threshold:
                best_score = score
                best_match = app_name
        return best_match
    def list_installed_apps(self):
        if not self.installed_apps:
            print("No apps discovered yet.")
            return
        unique_apps = {}
        for app_name, exec_cmd in self.installed_apps.items():
            if exec_cmd not in unique_apps.values():
                unique_apps[app_name] = exec_cmd
        sorted_apps = sorted(unique_apps.items())
        print(f"\n📱 Discovered Applications ({len(sorted_apps)} apps):")
        print("=" * 70)
        for i, (app_name, exec_cmd) in enumerate(sorted_apps, 1):
            if i <= 50:
                print(f"{i:3d}. {app_name}")
        if len(sorted_apps) > 50:
            print(f"\n... and {len(sorted_apps) - 50} more apps")
        print("=" * 70)
        print(f"\n💡 Say 'open [app name]' to launch any app")
    def check_app_exists(self, app_name):
        app_lower = app_name.lower().strip()
        try:
            if self.system == "Windows":
                result = subprocess.run(['where', app_name], capture_output=True, timeout=2)
                return result.returncode == 0
            elif self.system == "Darwin":
                result = subprocess.run(['mdfind', f'kMDItemKind == "Application" && kMDItemDisplayName == "{app_name}"'], 
                                       capture_output=True, timeout=2)
                return len(result.stdout.strip()) > 0
            else:
                result = subprocess.run(['which', app_name], capture_output=True, timeout=2)
                return result.returncode == 0
        except:
            return False
    def open_app(self, app_name):
        app_name = app_name.strip().rstrip('.,!?;:')
        app_lower = app_name.lower()
        print(f"🔍 Looking for: {app_name}")
        app_mappings = {
            'chrome': {'Windows': 'chrome', 'Linux': 'google-chrome', 'Darwin': 'Google Chrome'},
            'google chrome': {'Windows': 'chrome', 'Linux': 'google-chrome', 'Darwin': 'Google Chrome'},
            'firefox': {'Windows': 'firefox', 'Linux': 'firefox', 'Darwin': 'Firefox'},
            'brave': {'Windows': 'brave', 'Linux': 'brave-browser', 'Darwin': 'Brave Browser'},
            'edge': {'Windows': 'msedge', 'Linux': 'microsoft-edge', 'Darwin': 'Microsoft Edge'},
            'microsoft edge': {'Windows': 'msedge', 'Linux': 'microsoft-edge', 'Darwin': 'Microsoft Edge'},
            'safari': {'Windows': 'safari', 'Linux': 'safari', 'Darwin': 'Safari'},
            'opera': {'Windows': 'opera', 'Linux': 'opera', 'Darwin': 'Opera'},
            'code': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'vscode': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'vs code': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'visual studio code': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'visual studio': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'vs': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'cs code': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'vc code': {'Windows': 'code', 'Linux': 'code', 'Darwin': 'Visual Studio Code'},
            'pycharm': {'Windows': 'pycharm', 'Linux': 'pycharm', 'Darwin': 'PyCharm'},
            'intellij': {'Windows': 'idea', 'Linux': 'idea', 'Darwin': 'IntelliJ IDEA'},
            'android studio': {'Windows': 'studio', 'Linux': 'studio', 'Darwin': 'Android Studio'},
            'sublime': {'Windows': 'sublime_text', 'Linux': 'subl', 'Darwin': 'Sublime Text'},
            'sublime text': {'Windows': 'sublime_text', 'Linux': 'subl', 'Darwin': 'Sublime Text'},
            'atom': {'Windows': 'atom', 'Linux': 'atom', 'Darwin': 'Atom'},
            'notepad++': {'Windows': 'notepad++', 'Linux': 'notepad++', 'Darwin': 'notepad++'},
            'vim': {'Windows': 'vim', 'Linux': 'vim', 'Darwin': 'MacVim'},
            'emacs': {'Windows': 'emacs', 'Linux': 'emacs', 'Darwin': 'Emacs'},
            'slack': {'Windows': 'slack', 'Linux': 'slack', 'Darwin': 'Slack'},
            'discord': {'Windows': 'discord', 'Linux': 'discord', 'Darwin': 'Discord'},
            'zoom': {'Windows': 'zoom', 'Linux': 'zoom', 'Darwin': 'zoom.us'},
            'teams': {'Windows': 'teams', 'Linux': 'teams', 'Darwin': 'Microsoft Teams'},
            'microsoft teams': {'Windows': 'teams', 'Linux': 'teams', 'Darwin': 'Microsoft Teams'},
            'skype': {'Windows': 'skype', 'Linux': 'skype', 'Darwin': 'Skype'},
            'telegram': {'Windows': 'telegram', 'Linux': 'telegram', 'Darwin': 'Telegram'},
            'whatsapp': {'Windows': 'whatsapp', 'Linux': 'whatsapp', 'Darwin': 'WhatsApp'},
            'vlc': {'Windows': 'vlc', 'Linux': 'vlc', 'Darwin': 'VLC'},
            'spotify': {'Windows': 'spotify', 'Linux': 'spotify', 'Darwin': 'Spotify'},
            'itunes': {'Windows': 'itunes', 'Linux': 'rhythmbox', 'Darwin': 'Music'},
            'music': {'Windows': 'wmplayer', 'Linux': 'rhythmbox', 'Darwin': 'Music'},
            'media player': {'Windows': 'wmplayer', 'Linux': 'vlc', 'Darwin': 'QuickTime Player'},
            'word': {'Windows': 'winword', 'Linux': 'libreoffice', 'Darwin': 'Microsoft Word'},
            'microsoft word': {'Windows': 'winword', 'Linux': 'libreoffice', 'Darwin': 'Microsoft Word'},
            'excel': {'Windows': 'excel', 'Linux': 'libreoffice', 'Darwin': 'Microsoft Excel'},
            'microsoft excel': {'Windows': 'excel', 'Linux': 'libreoffice', 'Darwin': 'Microsoft Excel'},
            'powerpoint': {'Windows': 'powerpnt', 'Linux': 'libreoffice', 'Darwin': 'Microsoft PowerPoint'},
            'microsoft powerpoint': {'Windows': 'powerpnt', 'Linux': 'libreoffice', 'Darwin': 'Microsoft PowerPoint'},
            'outlook': {'Windows': 'outlook', 'Linux': 'thunderbird', 'Darwin': 'Microsoft Outlook'},
            'microsoft outlook': {'Windows': 'outlook', 'Linux': 'thunderbird', 'Darwin': 'Microsoft Outlook'},
            'onenote': {'Windows': 'onenote', 'Linux': 'xournalpp', 'Darwin': 'Microsoft OneNote'},
            'libreoffice': {'Windows': 'libreoffice', 'Linux': 'libreoffice', 'Darwin': 'LibreOffice'},
            'libreoffice writer': {'Windows': 'libreoffice --writer', 'Linux': 'libreoffice --writer', 'Darwin': 'LibreOffice'},
            'libreoffice calc': {'Windows': 'libreoffice --calc', 'Linux': 'libreoffice --calc', 'Darwin': 'LibreOffice'},
            'libreoffice impress': {'Windows': 'libreoffice --impress', 'Linux': 'libreoffice --impress', 'Darwin': 'LibreOffice'},
            'libreoffice math': {'Windows': 'libreoffice --math', 'Linux': 'libreoffice --math', 'Darwin': 'LibreOffice'},
            'libreoffice draw': {'Windows': 'libreoffice --draw', 'Linux': 'libreoffice --draw', 'Darwin': 'LibreOffice'},
            'writer': {'Windows': 'libreoffice --writer', 'Linux': 'libreoffice --writer', 'Darwin': 'LibreOffice'},
            'impress': {'Windows': 'libreoffice --impress', 'Linux': 'libreoffice --impress', 'Darwin': 'LibreOffice'},
            'draw': {'Windows': 'libreoffice --draw', 'Linux': 'libreoffice --draw', 'Darwin': 'LibreOffice'},
            'calculator': {'Windows': 'calc', 'Linux': 'gnome-calculator', 'Darwin': 'Calculator'},
            'notepad': {'Windows': 'notepad', 'Linux': 'gedit', 'Darwin': 'TextEdit'},
            'paint': {'Windows': 'mspaint', 'Linux': 'gimp', 'Darwin': 'Preview'},
            'gimp': {'Windows': 'gimp', 'Linux': 'gimp', 'Darwin': 'GIMP'},
            'photoshop': {'Windows': 'photoshop', 'Linux': 'gimp', 'Darwin': 'Adobe Photoshop'},
            'terminal': {'Windows': 'cmd', 'Linux': 'gnome-terminal', 'Darwin': 'Terminal'},
            'command prompt': {'Windows': 'cmd', 'Linux': 'gnome-terminal', 'Darwin': 'Terminal'},
            'cmd': {'Windows': 'cmd', 'Linux': 'gnome-terminal', 'Darwin': 'Terminal'},
            'powershell': {'Windows': 'powershell', 'Linux': 'pwsh', 'Darwin': 'Terminal'},
            'task manager': {'Windows': 'taskmgr', 'Linux': 'gnome-system-monitor', 'Darwin': 'Activity Monitor'},
            'activity monitor': {'Windows': 'taskmgr', 'Linux': 'gnome-system-monitor', 'Darwin': 'Activity Monitor'},
            'file explorer': {'Windows': 'explorer', 'Linux': 'nautilus', 'Darwin': 'Finder'},
            'explorer': {'Windows': 'explorer', 'Linux': 'nautilus', 'Darwin': 'Finder'},
            'files': {'Windows': 'explorer', 'Linux': 'nautilus', 'Darwin': 'Finder'},
            'finder': {'Windows': 'explorer', 'Linux': 'nautilus', 'Darwin': 'Finder'},
            'git': {'Windows': 'git', 'Linux': 'git-gui', 'Darwin': 'Git'},
            'github desktop': {'Windows': 'githubdesktop', 'Linux': 'github-desktop', 'Darwin': 'GitHub Desktop'},
            'docker': {'Windows': 'docker', 'Linux': 'docker', 'Darwin': 'Docker'},
            'postman': {'Windows': 'postman', 'Linux': 'postman', 'Darwin': 'Postman'},
            'steam': {'Windows': 'steam', 'Linux': 'steam', 'Darwin': 'Steam'},
            'obs': {'Windows': 'obs', 'Linux': 'obs', 'Darwin': 'OBS'},
            'obs studio': {'Windows': 'obs', 'Linux': 'obs', 'Darwin': 'OBS'},
            'blender': {'Windows': 'blender', 'Linux': 'blender', 'Darwin': 'Blender'},
            'audacity': {'Windows': 'audacity', 'Linux': 'audacity', 'Darwin': 'Audacity'},
            'handbrake': {'Windows': 'handbrake', 'Linux': 'handbrake', 'Darwin': 'HandBrake'},
            'virtualbox': {'Windows': 'virtualbox', 'Linux': 'virtualbox', 'Darwin': 'VirtualBox'},
            'vmware': {'Windows': 'vmware', 'Linux': 'vmware', 'Darwin': 'VMware Fusion'},
            'pulseaudio': {'Windows': '', 'Linux': 'pavucontrol', 'Darwin': ''},
            'pulse audio': {'Windows': '', 'Linux': 'pavucontrol', 'Darwin': ''},
            'volume control': {'Windows': 'sndvol', 'Linux': 'pavucontrol', 'Darwin': 'open /System/Library/PreferencePanes/Sound.prefPane'},
        }
        if app_lower in app_mappings:
            app_name = app_mappings[app_lower].get(self.system, app_name)
            print(f"✓ Mapped to: {app_name}")
        elif app_lower in self.installed_apps:
            app_name = self.installed_apps[app_lower]
            print(f"✓ Found installed: {app_name}")
        else:
            matched_app = self._fuzzy_match_app(app_lower)
            if matched_app:
                app_name = self.installed_apps[matched_app]
                print(f"✓ Similar app found: {matched_app} → {app_name}")
        try:
            if ' ' in app_name and ('--' in app_name or '/' in app_name):
                parts = app_name.split()
                if self.system == "Windows":
                    subprocess.Popen(parts, shell=True)
                elif self.system == "Darwin":
                    subprocess.Popen(parts)
                else:
                    subprocess.Popen(parts)
                print(f"✓ Opened: {app_name}")
                return True
            else:
                if self.system == "Windows":
                    subprocess.Popen(['start', '', app_name], shell=True)
                elif self.system == "Darwin":
                    subprocess.Popen(['open', '-a', app_name])
                else:
                    subprocess.Popen([app_name])
                print(f"✓ Opened: {app_name}")
                return True
        except Exception as e:
            print(f"✗ Not found locally: {app_name}")
            try:
                if self.system == "Linux":
                    subprocess.Popen(['xdg-open', app_name])
                    print(f"✓ Opened via xdg-open")
                    return True
            except:
                pass
            return False
    def download_and_install_app(self, app_name):
        print(f"📥 Attempting to install: {app_name}")
        app_name_clean = app_name.lower().strip()
        if self.system == "Linux":
            return self._install_linux_app(app_name_clean)
        elif self.system == "Windows":
            return self._install_windows_app(app_name_clean)
        elif self.system == "Darwin":
            return self._install_macos_app(app_name_clean)
        return False
    def _install_linux_app(self, app_name):
        print(f"🐧 Linux: Trying package managers...")
        try:
            print(f"   Trying snap...")
            result = subprocess.run(['snap', 'info', app_name], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✓ Found in Snap! Installing...")
                subprocess.Popen(['x-terminal-emulator', '-e', f'sudo snap install {app_name}'])
                print(f"   📦 Opening terminal to install {app_name} via snap")
                return True
        except Exception as e:
            pass
        try:
            print(f"   Trying apt...")
            result = subprocess.run(['apt-cache', 'search', f'^{app_name}$'], 
                                  capture_output=True, timeout=5)
            if result.stdout:
                print(f"   ✓ Found in APT! Installing...")
                subprocess.Popen(['x-terminal-emulator', '-e', f'sudo apt install {app_name} -y'])
                print(f"   📦 Opening terminal to install {app_name} via apt")
                return True
        except Exception as e:
            pass
        try:
            print(f"   Trying flatpak...")
            result = subprocess.run(['flatpak', 'search', app_name], 
                                  capture_output=True, timeout=5)
            if result.stdout:
                print(f"   ✓ Found in Flatpak! Use: flatpak install {app_name}")
                subprocess.Popen(['x-terminal-emulator', '-e', f'flatpak install {app_name}'])
                return True
        except Exception as e:
            pass
        print(f"   ✗ Not found in package managers")
        return False
    def _install_windows_app(self, app_name):
        print(f"🪟 Windows: Trying package managers...")
        try:
            print(f"   Trying winget...")
            result = subprocess.run(['winget', 'search', app_name], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✓ Found in winget! Installing...")
                subprocess.Popen(['start', 'cmd', '/k', f'winget install {app_name}'], shell=True)
                print(f"   📦 Opening command prompt to install {app_name}")
                return True
        except Exception as e:
            pass
        try:
            print(f"   Opening Microsoft Store for: {app_name}")
            subprocess.Popen(['start', f'ms-windows-store://search/?query={app_name}'], shell=True)
            return True
        except Exception as e:
            pass
        print(f"   ✗ Could not access package managers")
        return False
    def _install_macos_app(self, app_name):
        print(f"🍎 macOS: Trying package managers...")
        try:
            print(f"   Trying brew...")
            result = subprocess.run(['brew', 'search', app_name], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0 and app_name.encode() in result.stdout:
                print(f"   ✓ Found in Homebrew! Installing...")
                subprocess.Popen(['open', '-a', 'Terminal', f'brew install {app_name}'])
                print(f"   📦 Opening Terminal to install {app_name} via brew")
                return True
        except Exception as e:
            pass
        try:
            print(f"   Opening App Store for: {app_name}")
            subprocess.Popen(['open', f'macappstore://search.itunes.apple.com/WebObjects/MZSearch.woa/wa/search?media=software&term={app_name}'])
            return True
        except Exception as e:
            pass
        print(f"   ✗ Could not access package managers")
        return False
    def install_app_terminal(self, app_name):
        print(f"Installing {app_name} via package manager...")
        try:
            if self.system == "Linux":
                return self._install_linux(app_name)
            elif self.system == "Darwin":
                return self._install_macos(app_name)
            elif self.system == "Windows":
                return self._install_windows(app_name)
            else:
                print(f"Unsupported system: {self.system}")
                return False
        except Exception as e:
            print(f"Error during installation: {e}")
            return False
    def _install_linux(self, app_name):
        print("Linux detected")
        managers = [
            ("apt", ["sudo", "apt", "install", "-y", app_name]),
            ("dnf", ["sudo", "dnf", "install", "-y", app_name]),
            ("yum", ["sudo", "yum", "install", "-y", app_name]),
            ("pacman", ["sudo", "pacman", "-S", "--noconfirm", app_name]),
            ("zypper", ["sudo", "zypper", "install", "-y", app_name]),
            ("apk", ["sudo", "apk", "add", app_name]),
            ("snap", ["sudo", "snap", "install", app_name]),
            ("flatpak", ["flatpak", "install", "-y", "flathub", app_name]),
        ]
        for manager, cmd in managers:
            if shutil.which(manager):
                print(f"Using {manager}...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{app_name} installed successfully via {manager}!")
                    return True
                else:
                    print(f"{manager} install failed")
        print(f"Could not install {app_name} on Linux")
        return False
    def _install_macos(self, app_name):
        print("macOS detected")
        if shutil.which("brew"):
            print("Using Homebrew...")
            result = subprocess.run(
                ["brew", "install", app_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"{app_name} installed successfully via Homebrew!")
                return True
            else:
                print("Homebrew install failed")
        else:
            print("Homebrew not found")
            print("\nTo install Homebrew, run:")
            print('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        print(f"Could not install {app_name} via package manager")
        return False
    def _install_windows(self, app_name):
        print("Windows detected")
        if shutil.which("choco"):
            print("Using Chocolatey...")
            result = subprocess.run(
                ["choco", "install", app_name, "-y"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                print(f"{app_name} installed successfully via chocolatey!")
                return True
            else:
                print(f"Chocolatey install failed")
        else:
            print("Chocolatey not found")
            print("\nTo install Chocolatey, run PowerShell as Admin:")
            print('Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))')
        print(f"Could not install {app_name} via any package manager")
        return False
    def open_app_store(self):
        try:
            if self.system == "Darwin":
                print("Opening Mac App Store...")
                subprocess.run(["open", "macappstore://"])
                return True
            elif self.system == "Windows":
                print("Opening Microsoft Store...")
                subprocess.run(["start", "ms-windows-store://"], shell=True)
                return True
            elif self.system == "Linux":
                stores = [
                    ("snap-store", "Snap Store"),
                    ("gnome-software", "GNOME Software"),
                    ("plasma-discover", "KDE Discover"),
                ]
                for cmd, name in stores:
                    if shutil.which(cmd):
                        print(f"Opening {name}...")
                        subprocess.Popen([cmd])
                        return True
                print("No app store found on this Linux system")
                return False
            return False
        except Exception as e:
            print(f"Failed to open app store: {e}")
            return False
    def list_files(self, directory=None):
        try:
            if directory is None:
                directory = self.home_dir
            elif not os.path.isabs(directory):
                directory = self.home_dir / directory
            else:
                directory = Path(directory)
            if not directory.exists():
                print(f"Directory does not exist: {directory}")
                return False
            print(f"\nContents of {directory}:")
            print("="*60)
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for item in items:
                if item.is_dir():
                    print(f"{item.name}/")
                else:
                    size = item.stat().st_size
                    size_str = self._format_size(size)
                    print(f"{item.name} ({size_str})")
            print("="*60 + "\n")
            return True
        except Exception as e:
            print(f"Failed to list files: {e}")
            return False
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    def get_system_info(self):
        info = {
            "system": self.system,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "home_directory": str(self.home_dir),
        }
        print("\nSystem Information:")
        print("="*60)
        for key, value in info.items():
            print(f"{key}: {value}")
        print("="*60 + "\n")
        return info