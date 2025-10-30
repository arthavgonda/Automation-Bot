from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import platform
import subprocess
import os
import shutil
from pathlib import Path
from Browser.MediaPlayer import MediaPlayer
from Browser.ResearchDownloader import ResearchDownloader
from Browser.BrowserController import BrowserController
from Browser.PageReader import PageReader

class EnhancedIntelligentBrowser:
    def __init__(self, driver, system_controller):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.system = system_controller
        self.platform_name = platform.system()
        self.media_player = MediaPlayer(driver)
        self.research_downloader = ResearchDownloader(driver)
        self.browser_controller = BrowserController(driver)
        self.page_reader = PageReader(driver)
        self.whatsapp_open = False
    def parse_command(self, text):
        text = text.lower().strip()
        file_patterns = [
            (r"^create\s+(?:a\s+)?file\s+(?:named\s+|called\s+)?(.+)", "create_file"),
            (r"^make\s+(?:a\s+)?file\s+(?:named\s+|called\s+)?(.+)", "create_file"),
            (r"^delete\s+(?:the\s+)?file\s+(.+)", "delete_file"),
            (r"^remove\s+(?:the\s+)?file\s+(.+)", "delete_file"),
        ]
        for pattern, action in file_patterns:
            match = re.search(pattern, text)
            if match:
                return {"action": action, "target": match.group(1).strip()}
        folder_patterns = [
            (r"^create\s+(?:a\s+)?folder\s+(?:named\s+|called\s+)?(.+)", "create_folder"),
            (r"^make\s+(?:a\s+)?folder\s+(?:named\s+|called\s+)?(.+)", "create_folder"),
            (r"^create\s+(?:a\s+)?directory\s+(?:named\s+|called\s+)?(.+)", "create_folder"),
            (r"^delete\s+(?:the\s+)?folder\s+(.+)", "delete_folder"),
            (r"^remove\s+(?:the\s+)?folder\s+(.+)", "delete_folder"),
            (r"^delete\s+(?:the\s+)?directory\s+(.+)", "delete_folder"),
        ]
        for pattern, action in folder_patterns:
            match = re.search(pattern, text)
            if match:
                return {"action": action, "target": match.group(1).strip()}
        if re.search(r"^open\s+whatsapp", text):
            return {"action": "open_whatsapp"}
        if re.search(r"send\s+(?:a\s+)?(?:message|msg)\s+to\s+(.+)", text):
            match = re.search(r"send\s+(?:a\s+)?(?:message|msg)\s+to\s+(.+)", text)
            if match:
                return {"action": "send_whatsapp_message", "recipient": match.group(1).strip()}
        if re.search(r"^list\s+files?|^show\s+files?", text):
            match = re.search(r"(?:in|from)\s+(.+)", text)
            directory = match.group(1).strip() if match else None
            return {"action": "list_files", "target": directory}
        if re.search(r"^open\s+(?:the\s+)?app\s+store", text):
            return {"action": "open_app_store"}
        terminal_patterns = [
            (r"^terminal\s+install\s+(.+)", 1),
            (r"^package\s+install\s+(.+)", 1),
            (r"(?:install|download|get)\s+(.+?)\s+(?:via|through|by|using|from)\s+terminal", 1),
            (r"(?:install|download|get)\s+(.+?)\s+(?:via|through|by|using|from)\s+package\s+manager", 1),
        ]
        for pattern, group in terminal_patterns:
            match = re.search(pattern, text)
            if match:
                app_name = match.group(group).strip()
                return {"action": "terminal_install", "item": app_name}
        download_patterns = [
            r"^download\s+(?:and\s+install\s+)?(.+)",
            r"^get\s+(.+)",
            r"^install\s+(.+)",
        ]
        for pattern in download_patterns:
            match = re.search(pattern, text)
            if match:
                item = match.group(1).strip()
                return {"action": "download", "item": item}
        platform_search_patterns = [
            r"(?:search|khojo|dhundo|find|lookup)\s+(?:for\s+)?(.+?)\s+(?:on|in|par|me)\s+(\w+)",
            r"(?:open|go to|use)\s+(\w+)\s+(?:and|to)\s+(?:search|find|order|buy)\s+(?:for\s+)?(?:me\s+)?(?:a\s+)?(.+)",
            r"(\w+)\s+(?:pe|par|me|on|in)\s+(?:search|khojo|dhundo)\s+(?:karo\s+)?(.+)",
        ]
        for idx, pattern in enumerate(platform_search_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if idx == 0:
                    query = groups[0].strip()
                    platform = groups[1].strip().lower()
                elif idx == 1:
                    platform = groups[0].strip().lower()
                    query = groups[1].strip()
                else:
                    platform = groups[0].strip().lower()
                    query = groups[1].strip()
                web_platforms = ['youtube', 'google', 'facebook', 'instagram', 'twitter', 'amazon', 
                                'reddit', 'wikipedia', 'spotify', 'linkedin', 'github', 'chatgpt',
                                'netflix', 'pinterest', 'tiktok', 'whatsapp', 'telegram', 'ebay',
                                'stackoverflow', 'medium', 'quora', 'imdb', 'yelp', 'twitch']
                if any(plat in platform for plat in web_platforms) or len(platform) > 3:
                    return {"action": "platform_search", "query": query, "platform": platform}
        open_app_patterns = [
            r"^(?:open|launch|start|run|kholo|chalu)\s+(.+?)(?:\s+from\s+system|\s+on\s+system|\s+in\s+system)?$",
        ]
        for pattern in open_app_patterns:
            match = re.search(pattern, text)
            if match:
                app_name = match.group(1).strip()
                return {"action": "open_app", "app": app_name}
        search_patterns = [
            r"^(?:search|look up|find|google)\s+(?:for\s+)?(.+)",
            r"^(?:what is|who is|tell me about|info on)\s+(.+)",
            r"^(?:browse|go to|visit|navigate to)\s+(.+)",
        ]
        for pattern in search_patterns:
            match = re.search(pattern, text)
            if match:
                query = match.group(1).strip()
                if re.match(r"^(https?://|www\.)", query):
                    return {"action": "open_website", "url": query}
                elif '.' in query and not ' ' in query:
                    return {"action": "open_website", "url": query}
                else:
                    return {"action": "search_google", "query": query}
        if re.search(r"^system\s+info", text):
            return {"action": "system_info"}
        if re.search(r"^list\s+apps?|^show\s+apps?", text):
            return {"action": "list_apps"}
        return {"action": "unknown", "command": text}
    def execute_command(self, text):
        command = self.parse_command(text)
        action = command.get("action")
        if action == "platform_search":
            query = command["query"]
            platform = command["platform"]
            self.search_on_platform(query, platform)
            return True
        elif action == "open_app":
            app_name = command["app"]
            success = self.system.open_app(app_name)
            if not success:
                print(f"🌐 Searching online for: {app_name}")
                self.search_google(app_name)
            return True
        elif action in ["create_file", "delete_file"]:
            self.system.create_file(command["target"]) if action == "create_file" else self.system.delete_file(command["target"])
            return True
        elif action in ["create_folder", "delete_folder"]:
            self.system.create_folder(command["target"]) if action == "create_folder" else self.system.delete_folder(command["target"])
            return True
        elif action == "list_files":
            self.system.list_files(command.get("target"))
            return True
        elif action == "open_app_store":
            self.system.open_app_store()
            return True
        elif action == "terminal_install":
            self.system.install_app_terminal(command["item"])
            return True
        elif action == "download":
            self.download_and_install(command["item"])
            return True
        elif action == "search_google":
            self.search_google(command["query"])
            return True
        elif action == "open_website":
            self.open_website(command["url"])
            return True
        elif action == "open_whatsapp":
            self.open_whatsapp()
            return True
        elif action == "send_whatsapp_message":
            self.send_whatsapp_message(command["recipient"], command.get("message"))
            return True
        elif action == "system_info":
            self.system.get_system_info()
            return True
        elif action == "list_apps":
            self.system.list_installed_apps()
            return True
        else:
            print(f"❓ Unknown: {text}")
            return False
    def download_research(self, topic, max_papers=5):
        try:
            return self.research_downloader.download_research_papers(topic, max_papers)
        except Exception as e:
            print(f"❌ Research download error: {e}")
            return False
    def play_first_result(self, query, platform="youtube"):
        try:
            if platform.lower() == "youtube":
                return self.media_player.play_first_youtube_result(query)
            elif platform.lower() == "spotify":
                return self.media_player.play_first_spotify_result(query)
            else:
                return self.media_player.play_first_youtube_result(query)
        except Exception as e:
            print(f"❌ Play error: {e}")
            self.search_on_platform(query, platform)
            return False, str(e)
    def search_on_platform(self, query, platform):
        platform_lower = platform.lower().strip()
        platform_urls = {
            'youtube': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}',
            'google': f'https://www.google.com/search?q={query.replace(" ", "+")}',
            'facebook': f'https://www.facebook.com/search/top?q={query.replace(" ", "%20")}',
            'instagram': f'https://www.instagram.com/explore/search/keyword/?q={query.replace(" ", "%20")}',
            'twitter': f'https://twitter.com/search?q={query.replace(" ", "%20")}',
            'linkedin': f'https://www.linkedin.com/search/results/all/?keywords={query.replace(" ", "%20")}',
            'reddit': f'https://www.reddit.com/search?q={query.replace(" ", "+")}',
            'wikipedia': f'https://en.wikipedia.org/w/index.php?search={query.replace(" ", "+")}',
            'spotify': f'https://open.spotify.com/search/{query.replace(" ", "%20")}',
            'amazon': f'https://www.amazon.com/s?k={query.replace(" ", "+")}',
            'github': f'https://github.com/search?q={query.replace(" ", "+")}',
            'stackoverflow': f'https://stackoverflow.com/search?q={query.replace(" ", "+")}',
            'pinterest': f'https://www.pinterest.com/search/pins/?q={query.replace(" ", "%20")}',
            'quora': f'https://www.quora.com/search?q={query.replace(" ", "+")}',
            'medium': f'https://medium.com/search?q={query.replace(" ", "+")}',
            'netflix': f'https://www.netflix.com/search?q={query.replace(" ", "%20")}',
            'ebay': f'https://www.ebay.com/sch/i.html?_nkw={query.replace(" ", "+")}',
            'imdb': f'https://www.imdb.com/find?q={query.replace(" ", "+")}',
            'yelp': f'https://www.yelp.com/search?find_desc={query.replace(" ", "+")}',
            'tiktok': f'https://www.tiktok.com/search?q={query.replace(" ", "%20")}',
            'twitch': f'https://www.twitch.tv/search?term={query.replace(" ", "%20")}',
            'flipkart': f'https://www.flipkart.com/search?q={query.replace(" ", "%20")}',
            'snapdeal': f'https://www.snapdeal.com/search?keyword={query.replace(" ", "%20")}',
            'meesho': f'https://www.meesho.com/search?q={query.replace(" ", "%20")}',
        }
        if 'chatgpt' in platform_lower or 'chat gpt' in platform_lower or 'gpt' in platform_lower:
            print(f"🤖 Opening ChatGPT (query: {query})")
            return self.open_website(f'https://chat.openai.com/?q={query.replace(" ", "+")}')
        if 'whatsapp' in platform_lower:
            print(f"💬 Opening WhatsApp Web")
            return self.open_website('https://web.whatsapp.com')
        if 'gmail' in platform_lower or 'mail' in platform_lower:
            print(f"📧 Searching Gmail for: {query}")
            return self.open_website(f'https://mail.google.com/mail/u/0/#search/{query.replace(" ", "+")}')
        if platform_lower in platform_urls:
            url = platform_urls[platform_lower]
            print(f"🔍 Searching '{query}' on {platform.title()}")
            return self.open_website(url)
        print(f"🌐 Attempting generic search on {platform}...")
        generic_patterns = [
            f'https://www.{platform_lower}.com/search?q={query.replace(" ", "+")}',
            f'https://{platform_lower}.com/search?q={query.replace(" ", "+")}',
        ]
        try:
            url = generic_patterns[0]
            print(f"   Trying: {url}")
            return self.open_website(url)
        except:
            print(f"   ⚠ Search URL unknown, opening homepage")
            homepage = f'https://www.{platform_lower}.com'
            return self.open_website(homepage)
    def search_google(self, query):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Searching for: {query} (attempt {attempt + 1}/{max_retries})")
                try:
                    self.driver.current_url
                except:
                    print("Browser window closed, cannot search")
                    return False
                self.driver.get("https://www.google.com")
                time.sleep(1)
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                time.sleep(2)
                print(f"Search results for: {query}")
                return True
            except TimeoutException:
                print(f"Timeout waiting for Google search page (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            except Exception as e:
                error_msg = str(e)
                if "target window already closed" in error_msg.lower() or "web view not found" in error_msg.lower():
                    print(f"Browser window was closed: {error_msg[:100]}")
                    return False
                print(f"Google search failed: {error_msg[:150]}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        return False
    def download_and_install(self, item):
        print(f"\nDownloading and installing: {item}")
        platform_buttons = {
            "Windows": ["windows", "win", "pc"],
            "Darwin": ["mac", "apple", "osx"],
            "Linux": ["linux", "deb", "ubuntu"],
        }
        current_platform = platform_buttons.get(self.platform_name, [])
        if item.lower() in ["steam", "discord", "spotify"]:
            download_urls = {
                "steam": "https://store.steampowered.com/about/",
                "discord": "https://discord.com/download",
                "spotify": "https://www.spotify.com/download/",
            }
            self.open_website(download_urls[item.lower()])
            time.sleep(2)
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'download') or contains(text(), 'Download') or contains(@href, '.exe') or contains(@href, '.dmg') or contains(@href, '.deb')]")
                for elem in elements:
                    elem_text = elem.text.lower() + (elem.get_attribute('href') or '').lower()
                    if any(p in elem_text for p in current_platform) or "download" in elem_text:
                        print(f"Found platform button: {elem.text.strip() or 'Link'}")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                        time.sleep(0.5)
                        try:
                            elem.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", elem)
                        print("Download button clicked")
                        time.sleep(2)
                        return True
            except:
                pass
        self.search_google(f"{item} official download {self.platform_name.lower()}")
        time.sleep(2)
        try:
            official_domains = [
                "steampowered.com", "discord.com", "spotify.com",
                "github.com", "microsoft.com", "apple.com",
            ]
            results = self.driver.find_elements(By.CSS_SELECTOR, "h3")
            for result in results[:3]:
                try:
                    link = result.find_element(By.XPATH, "./parent::a")
                    url = link.get_attribute("href")
                    if any(domain in url for domain in official_domains):
                        print(f"Found official site: {url}")
                        link.click()
                        time.sleep(2)
                        break
                except:
                    continue
            else:
                self.click_first_result()
        except Exception as e:
            print(f"Navigation error: {e}")
            return False
        time.sleep(2)
        if self.find_platform_specific_download(current_platform):
            return True
        if self.find_and_click_download_button():
            return True
        print(f"Could not automatically download {item}")
        print("Please download manually from the opened page.")
        return False
    def find_platform_specific_download(self, current_platform):
        print("Looking for platform-specific download...")
        selectors = [
            "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download') and (contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'windows') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'mac') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'linux'))]",
            "//a[contains(@href, 'download') or contains(@class, 'download')]",
            "//button[contains(@class, 'download')]",
        ]
        try:
            for selector in selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    elem_text = elem.text.lower()
                    if any(p in elem_text for p in current_platform):
                        print(f"Found {elem_text}")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                        time.sleep(0.5)
                        try:
                            elem.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", elem)
                        print("Download button clicked")
                        time.sleep(2)
                        return True
        except Exception as e:
            print(f"Platform detection issue: {e}")
        return False
    def find_and_click_download_button(self):
        print("Looking for download button...")
        selectors = [
            "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]",
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]",
            "//a[contains(@class, 'download')]",
            "//button[contains(@class, 'download')]",
        ]
        try:
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            print(f"Found download button: '{elem.text.strip()}'")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                            time.sleep(0.5)
                            try:
                                elem.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", elem)
                            print("Download clicked")
                            time.sleep(2)
                            return True
                except:
                    continue
            print("No download button found automatically")
            return False
        except Exception as e:
            print(f"Error finding download button: {e}")
            return False
    def open_website(self, url):
        common_sites = {
            'youtube': 'youtube.com',
            'google': 'google.com',
            'facebook': 'facebook.com',
            'twitter': 'twitter.com',
            'instagram': 'instagram.com',
            'linkedin': 'linkedin.com',
            'github': 'github.com',
            'reddit': 'reddit.com',
            'amazon': 'amazon.com',
            'netflix': 'netflix.com',
            'whatsapp': 'web.whatsapp.com',
        }
        url_lower = url.lower().strip()
        if url_lower in common_sites:
            url = common_sites[url_lower]
        if not url.startswith(('http://', 'https://')):
            if '.' in url:
                url = 'https://' + url
            else:
                return self.search_google(url)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Opening: {url} (attempt {attempt + 1}/{max_retries})")
                try:
                    self.driver.current_url
                except:
                    print("Browser window closed, cannot open website")
                    return False
                self.driver.get(url)
                time.sleep(2)
                try:
                    title = self.driver.title
                    print(f"Loaded: {title}")
                    return True
                except:
                    print("Page loaded but title unavailable")
                    return True
            except Exception as e:
                error_msg = str(e)
                if "target window already closed" in error_msg.lower() or "web view not found" in error_msg.lower():
                    print(f"Browser window was closed: {error_msg[:100]}")
                    return False
                print(f"Failed to open {url}: {error_msg[:150]}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        return False
    def click_first_result(self):
        try:
            print("Clicking first result...")
            first_result = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "h3"))
            )
            first_result.click()
            time.sleep(2)
            print(f"Opened: {self.driver.title}")
            return True
        except Exception as e:
            print(f"Could not click first result: {e}")
            return False
    def close(self):
        print("\nClosing browser...")
        self.driver.quit()


def process_voice_command(driver, system_controller, transcription):
    browser = EnhancedIntelligentBrowser(driver, system_controller)
    if not transcription or transcription.strip() == "":
        print("Empty transcription")
        return "CONTINUE"
    print(f"\n{'='*60}")
    print(f"Voice Command: {transcription}")
    print(f"{'='*60}")
    exit_commands = ["exit", "quit", "close", "stop", "close browser"]
    if any(cmd in transcription.lower() for cmd in exit_commands):
        print("Goodbye!")
        browser.close()
        return "EXIT"
    browser.execute_command(transcription)
    return "CONTINUE"