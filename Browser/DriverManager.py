import os
import platform
import subprocess
import sys
from pathlib import Path

class DriverManager:
    
    def __init__(self):
        self.system = platform.system()
        
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
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("Chrome driver initialized")
            return driver
        except Exception as e:
            print(f"Chrome driver failed: {str(e)[:100]}")
            return None
    
    def get_firefox_driver(self):
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options
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
            
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            print("Firefox driver initialized")
            return driver
        except Exception as e:
            print(f"Firefox driver failed: {str(e)[:100]}")
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
            
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            print("Edge driver initialized")
            return driver
        except Exception as e:
            print(f"Edge driver failed: {str(e)[:100]}")
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
            
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix='brave_')
            options.add_argument(f'--user-data-dir={temp_dir}')
            
            driver = webdriver.Chrome(service=service, options=options)
            print("Brave driver initialized")
            return driver
        except Exception as e:
            print(f"Brave driver failed: {str(e)[:100]}")
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
            
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            driver = webdriver.Chrome(service=service, options=options)
            print("Chromium driver initialized")
            return driver
        except Exception as e:
            print(f"Chromium driver failed: {str(e)[:100]}")
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