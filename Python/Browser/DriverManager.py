import os
import platform
import subprocess
import sys
from pathlib import Path

class DriverManager:
    def __init__(self):
        self.system = platform.system()
        self.use_existing_profile = True
    def find_existing_path(self, paths_to_check):
        for path in paths_to_check:
            if os.path.exists(path):
                return path
        return None
    def is_profile_locked(self, profile_path):
        lock_files = ['SingletonLock', 'lockfile', '.parentlock', 'lock']
        for lock_file in lock_files:
            lock_path = os.path.join(profile_path, lock_file)
            if os.path.exists(lock_path):
                try:
                    with open(lock_path, 'a') as f:
                        pass
                    return False
                except (IOError, OSError):
                    return True
        return False
    def get_chrome_user_data_dir(self):
        paths_to_check = []
        if self.system == 'Windows':
            paths_to_check = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data'),
                os.path.join(os.environ.get('APPDATA', ''), 'Google', 'Chrome', 'User Data'),
            ]
        elif self.system == 'Darwin':
            paths_to_check = [
                os.path.join(str(Path.home()), 'Library', 'Application Support', 'Google', 'Chrome'),
            ]
        else:
            paths_to_check = [
                os.path.join(str(Path.home()), '.config', 'google-chrome'),
                os.path.join(str(Path.home()), 'snap', 'chromium', 'current', '.config', 'chromium'),
                os.path.join(str(Path.home()), 'snap', 'chrome', 'current', '.config', 'google-chrome'),
                os.path.join(str(Path.home()), '.var', 'app', 'com.google.Chrome', 'config', 'google-chrome'),
            ]
        user_data_dir = self.find_existing_path(paths_to_check)
        if user_data_dir:
            return user_data_dir
        if self.system == 'Windows':
            return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
        elif self.system == 'Darwin':
            return os.path.join(str(Path.home()), 'Library', 'Application Support', 'Google', 'Chrome')
        else:
            return os.path.join(str(Path.home()), '.config', 'google-chrome')
    def get_chromium_user_data_dir(self):
        paths_to_check = []
        if self.system == 'Windows':
            paths_to_check = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Chromium', 'User Data'),
                os.path.join(os.environ.get('APPDATA', ''), 'Chromium', 'User Data'),
            ]
        elif self.system == 'Darwin':
            paths_to_check = [
                os.path.join(str(Path.home()), 'Library', 'Application Support', 'Chromium'),
            ]
        else:
            paths_to_check = [
                os.path.join(str(Path.home()), '.config', 'chromium'),
                os.path.join(str(Path.home()), 'snap', 'chromium', 'current', '.config', 'chromium'),
                os.path.join(str(Path.home()), '.var', 'app', 'org.chromium.Chromium', 'config', 'chromium'),
            ]
        user_data_dir = self.find_existing_path(paths_to_check)
        if user_data_dir:
            return user_data_dir
        if self.system == 'Windows':
            return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Chromium', 'User Data')
        elif self.system == 'Darwin':
            return os.path.join(str(Path.home()), 'Library', 'Application Support', 'Chromium')
        else:
            return os.path.join(str(Path.home()), '.config', 'chromium')
    def get_brave_user_data_dir(self):
        paths_to_check = []
        if self.system == 'Windows':
            paths_to_check = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data'),
                os.path.join(os.environ.get('APPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data'),
            ]
        elif self.system == 'Darwin':
            paths_to_check = [
                os.path.join(str(Path.home()), 'Library', 'Application Support', 'BraveSoftware', 'Brave-Browser'),
            ]
        else:
            paths_to_check = [
                os.path.join(str(Path.home()), '.config', 'BraveSoftware', 'Brave-Browser'),
                os.path.join(str(Path.home()), 'snap', 'brave', 'current', '.config', 'BraveSoftware', 'Brave-Browser'),
                os.path.join(str(Path.home()), '.var', 'app', 'com.brave.Browser', 'config', 'BraveSoftware', 'Brave-Browser'),
            ]
        user_data_dir = self.find_existing_path(paths_to_check)
        if user_data_dir:
            return user_data_dir
        if self.system == 'Windows':
            return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data')
        elif self.system == 'Darwin':
            return os.path.join(str(Path.home()), 'Library', 'Application Support', 'BraveSoftware', 'Brave-Browser')
        else:
            return os.path.join(str(Path.home()), '.config', 'BraveSoftware', 'Brave-Browser')
    def get_edge_user_data_dir(self):
        paths_to_check = []
        if self.system == 'Windows':
            paths_to_check = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data'),
                os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Edge', 'User Data'),
            ]
        elif self.system == 'Darwin':
            paths_to_check = [
                os.path.join(str(Path.home()), 'Library', 'Application Support', 'Microsoft Edge'),
            ]
        else:
            paths_to_check = [
                os.path.join(str(Path.home()), '.config', 'microsoft-edge'),
                os.path.join(str(Path.home()), '.config', 'microsoft-edge-dev'),
                os.path.join(str(Path.home()), 'snap', 'microsoft-edge', 'current', '.config', 'microsoft-edge'),
                os.path.join(str(Path.home()), '.var', 'app', 'com.microsoft.Edge', 'config', 'microsoft-edge'),
            ]
        user_data_dir = self.find_existing_path(paths_to_check)
        if user_data_dir:
            return user_data_dir
        if self.system == 'Windows':
            return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data')
        elif self.system == 'Darwin':
            return os.path.join(str(Path.home()), 'Library', 'Application Support', 'Microsoft Edge')
        else:
            return os.path.join(str(Path.home()), '.config', 'microsoft-edge')
    def get_default_profile_directory(self, user_data_dir):
        return 'Default'
    def install_webdriver_manager(self):
        try:
            import webdriver_manager
            print("webdriver-manager already installed")
            return True
        except ImportError:
            print("Installing webdriver-manager...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "webdriver-manager", "selenium"
                ])
                print("webdriver-manager installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Failed to install webdriver-manager: {e}")
                return False
    def get_chrome_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--remote-debugging-port=9222')
            user_data_dir = self.get_chrome_user_data_dir()
            profile_directory = self.get_default_profile_directory(user_data_dir)
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument(f'--profile-directory={profile_directory}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            print(f"✓ Using Chrome profile: {user_data_dir}/{profile_directory}")
            print("  Note: Close Chrome if you encounter 'profile in use' errors")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            try:
                driver.maximize_window()
            except:
                pass
            print("✓ Chrome driver initialized")
            return driver
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Chrome driver failed: {error_msg[:150]}")
            if 'user data directory is already in use' in error_msg.lower() or 'profile' in error_msg.lower():
                print("   Retrying with different profile...")
                try:
                    options = Options()
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--window-size=1920,1080')
                    options.add_argument('--remote-debugging-port=9222')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_experimental_option('excludeSwitches', ['enable-automation'])
                    user_data_dir = self.get_chrome_user_data_dir()
                    profile_directory = self.get_default_profile_directory(user_data_dir)
                    options.add_argument(f'--user-data-dir={user_data_dir}')
                    options.add_argument(f'--profile-directory={profile_directory}')
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.set_page_load_timeout(30)
                    driver.implicitly_wait(10)
                    try:
                        driver.maximize_window()
                    except:
                        pass
                    print(f"✓ Chrome driver initialized (fallback mode)")
                    return driver
                except Exception as e2:
                    print(f"❌ Retry also failed: {str(e2)[:100]}")
            return None
    def get_firefox_driver(self):
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
        from webdriver_manager.firefox import GeckoDriverManager
        try:
            firefox_paths = {
                'Windows': [
                    r'C:\Program Files\Mozilla Firefox\firefox.exe',
                    r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
                ],
                'Darwin': [
                    '/Applications/Firefox.app/Contents/MacOS/firefox',
                ],
                'Linux': [
                    '/usr/bin/firefox',
                    '/usr/lib/firefox/firefox',
                    '/snap/bin/firefox',
                ]
            }
            firefox_found = False
            for path in firefox_paths.get(self.system, []):
                if os.path.exists(path):
                    firefox_found = True
                    break
            if not firefox_found:
                print("Firefox browser not found")
                return None
            options = Options()
            options.add_argument('--width=1920')
            options.add_argument('--height=1080')
            paths_to_check = []
            if self.system == 'Windows':
                paths_to_check = [
                    os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Mozilla', 'Firefox', 'Profiles'),
                ]
            elif self.system == 'Darwin':
                paths_to_check = [
                    os.path.join(str(Path.home()), 'Library', 'Application Support', 'Firefox', 'Profiles'),
                ]
            else:
                paths_to_check = [
                    os.path.join(str(Path.home()), '.mozilla', 'firefox'),
                    os.path.join(str(Path.home()), 'snap', 'firefox', 'common', '.mozilla', 'firefox'),
                    os.path.join(str(Path.home()), '.var', 'app', 'org.mozilla.firefox', '.mozilla', 'firefox'),
                ]
            firefox_profile_path = self.find_existing_path(paths_to_check)
            if not firefox_profile_path:
                if self.system == 'Windows':
                    firefox_profile_path = os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
                elif self.system == 'Darwin':
                    firefox_profile_path = os.path.join(str(Path.home()), 'Library', 'Application Support', 'Firefox', 'Profiles')
                else:
                    firefox_profile_path = os.path.join(str(Path.home()), '.mozilla', 'firefox')
            if os.path.exists(firefox_profile_path):
                try:
                    profiles = [d for d in os.listdir(firefox_profile_path) if os.path.isdir(os.path.join(firefox_profile_path, d))]
                    default_profile = None
                    for profile in profiles:
                        if 'default' in profile.lower():
                            default_profile = profile
                            break
                    if default_profile:
                        profile_path = os.path.join(firefox_profile_path, default_profile)
                        profile = FirefoxProfile(profile_path)
                        options.profile = profile
                        print(f"Using existing Firefox profile: {profile_path}")
                    else:
                        print(f"Warning: No default Firefox profile found in {firefox_profile_path}")
                        print("Firefox will create a new profile. Update firefox_profile_path if your profile is elsewhere.")
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not access Firefox profile directory: {e}")
                    print("Firefox will create a new profile.")
            else:
                print(f"Warning: Firefox profile directory not found at {firefox_profile_path}")
                print("Firefox will create a new profile.")
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            try:
                driver.maximize_window()
            except:
                pass
            print("✓ Firefox driver initialized")
            return driver
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Firefox driver failed: {error_msg[:150]}")
            try:
                options = Options()
                options.add_argument('--width=1920')
                options.add_argument('--height=1080')
                service = Service(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)
                try:
                    driver.maximize_window()
                except:
                    pass
                print("✓ Firefox driver initialized (default profile)")
                return driver
            except Exception as e2:
                print(f"❌ Retry also failed: {str(e2)[:100]}")
            return None
    def get_edge_driver(self):
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            user_data_dir = self.get_edge_user_data_dir()
            profile_directory = self.get_default_profile_directory(user_data_dir)
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument(f'--profile-directory={profile_directory}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            print(f"✓ Using Edge profile: {user_data_dir}/{profile_directory}")
            print("  Note: Close Edge if you encounter 'profile in use' errors")
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            try:
                driver.maximize_window()
            except:
                pass
            print("✓ Edge driver initialized")
            return driver
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Edge driver failed: {error_msg[:150]}")
            if 'user data directory is already in use' in error_msg.lower() or 'profile' in error_msg.lower():
                print("   Retrying with different profile...")
                try:
                    import time
                    options = Options()
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--window-size=1920,1080')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    user_data_dir = self.get_edge_user_data_dir()
                    profile_directory = self.get_default_profile_directory(user_data_dir)
                    options.add_argument(f'--user-data-dir={user_data_dir}')
                    options.add_argument(f'--profile-directory={profile_directory}')
                    service = Service(EdgeChromiumDriverManager().install())
                    driver = webdriver.Edge(service=service, options=options)
                    driver.set_page_load_timeout(30)
                    driver.implicitly_wait(10)
                    try:
                        driver.maximize_window()
                    except:
                        pass
                    print(f"✓ Edge driver initialized (fallback mode)")
                    return driver
                except Exception as e2:
                    print(f"❌ Retry also failed: {str(e2)[:100]}")
            return None
    def get_brave_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType
        try:
            brave_paths = {
                'Windows': [
                    r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                    r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe',
                ],
                'Darwin': [
                    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
                ],
                'Linux': [
                    '/usr/bin/brave-browser',
                    '/opt/brave.com/brave/brave-browser',
                    '/snap/bin/brave',
                ]
            }
            brave_path = None
            for path in brave_paths.get(self.system, []):
                if os.path.exists(path):
                    brave_path = path
                    break
            if not brave_path:
                print("Brave browser not found")
                return None
            brave_version = None
            try:
                if self.system == 'Windows':
                    import winreg
                    try:
                        key = winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BraveSoftware Brave-Browser"
                        )
                        brave_version, _ = winreg.QueryValueEx(key, "DisplayVersion")
                    except:
                        pass
                elif self.system == 'Darwin':
                    result = subprocess.run(['defaults', 'read', '/Applications/Brave Browser.app/Contents/Info', 'CFBundleShortVersionString'], capture_output=True, text=True)
                    if result.returncode == 0:
                        brave_version = result.stdout.strip()
                elif self.system == 'Linux':
                    result = subprocess.run([brave_path, '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        brave_version = result.stdout.strip().split()[-1]
            except:
                pass
            if brave_version:
                print(f"Detected Brave version: {brave_version}")
                major_version = brave_version.split('.')[0]
                service = Service(ChromeDriverManager(driver_version=major_version).install())
            else:
                print("Using latest ChromeDriver")
                service = Service(ChromeDriverManager(driver_version='latest').install())
            options = Options()
            options.binary_location = brave_path
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--remote-debugging-port=9223')
            user_data_dir = self.get_brave_user_data_dir()
            profile_directory = self.get_default_profile_directory(user_data_dir)
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument(f'--profile-directory={profile_directory}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            print(f"✓ Using Brave profile: {user_data_dir}/{profile_directory}")
            print("  Note: Close Brave if you encounter 'profile in use' errors")
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            try:
                driver.maximize_window()
            except:
                pass
            print("✓ Brave driver initialized")
            return driver
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Brave driver failed: {error_msg[:150]}")
            if 'user data directory is already in use' in error_msg.lower() or 'profile' in error_msg.lower():
                print("   Retrying with different profile...")
                try:
                    import time
                    options = Options()
                    options.binary_location = brave_path
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--window-size=1920,1080')
                    options.add_argument('--remote-debugging-port=9223')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    user_data_dir = self.get_brave_user_data_dir()
                    profile_directory = self.get_default_profile_directory(user_data_dir)
                    options.add_argument(f'--user-data-dir={user_data_dir}')
                    options.add_argument(f'--profile-directory={profile_directory}')
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.set_page_load_timeout(30)
                    driver.implicitly_wait(10)
                    try:
                        driver.maximize_window()
                    except:
                        pass
                    print(f"✓ Brave driver initialized (fallback mode)")
                    return driver
                except Exception as e2:
                    print(f"❌ Retry also failed: {str(e2)[:100]}")
            return None
    def get_chromium_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--remote-debugging-port=9224')
            user_data_dir = self.get_chromium_user_data_dir()
            profile_directory = self.get_default_profile_directory(user_data_dir)
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument(f'--profile-directory={profile_directory}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            print(f"✓ Using Chromium profile: {user_data_dir}/{profile_directory}")
            print("  Note: Close Chromium if you encounter 'profile in use' errors")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            try:
                driver.maximize_window()
            except:
                pass
            print("✓ Chromium driver initialized")
            return driver
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Chromium driver failed: {error_msg[:150]}")
            if 'user data directory is already in use' in error_msg.lower() or 'profile' in error_msg.lower():
                print("   Retrying with different profile...")
                try:
                    import time
                    options = Options()
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--window-size=1920,1080')
                    options.add_argument('--remote-debugging-port=9224')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    user_data_dir = self.get_chromium_user_data_dir()
                    profile_directory = self.get_default_profile_directory(user_data_dir)
                    options.add_argument(f'--user-data-dir={user_data_dir}')
                    options.add_argument(f'--profile-directory={profile_directory}')
                    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.set_page_load_timeout(30)
                    driver.implicitly_wait(10)
                    try:
                        driver.maximize_window()
                    except:
                        pass
                    print(f"✓ Chromium driver initialized (fallback mode)")
                    return driver
                except Exception as e2:
                    print(f"❌ Retry also failed: {str(e2)[:100]}")
            return None
    def get_default_browser_driver(self):
        browsers = [
            ('Brave', self.get_brave_driver),
            ('Firefox', self.get_firefox_driver),
            ('Chrome', self.get_chrome_driver),
            ('Chromium', self.get_chromium_driver),
            ('Edge', self.get_edge_driver),
        ]
        print("\n" + "="*60)
        print("BROWSER DRIVER INITIALIZATION")
        print("="*60)
        for browser_name, get_driver_func in browsers:
            print(f"\nTrying {browser_name}...")
            try:
                driver = get_driver_func()
                if driver:
                    print(f"\nSuccessfully initialized {browser_name} driver")
                    print("="*60 + "\n")
                    return driver
            except Exception as e:
                print(f"{browser_name} initialization error: {str(e)[:100]}")
                continue
        print("\nNo browser driver could be initialized")
        print("\nTroubleshooting tips:")
        print("Make sure at least one browser is installed (Chrome/Firefox/Brave/Edge)")
        print("On Linux, try: sudo apt install chromium-browser firefox")
        print("Check if browsers can run normally on your system")
        print("="*60 + "\n")
        return None

def setup_driver():
    manager = DriverManager()
    if not manager.install_webdriver_manager():
        return None
    return manager.get_default_browser_driver()

if __name__ == "__main__":
    driver = setup_driver()
    if driver:
        print("Driver is ready to use!")
        driver.get("https://www.google.com")
        input("Press Enter to close the browser...")
        driver.quit()
    else:
        print("Failed to setup driver")