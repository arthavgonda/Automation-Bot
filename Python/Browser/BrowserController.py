
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re

class BrowserController:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    def click_first_link(self):
        try:
            print("🖱️  Clicking first link...")
            selectors = [
                "a[href]",
                "div[role='link']",
                "button[type='button']",
            ]
            for selector in selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        first_link = links[0]
                        self.driver.execute_script("arguments[0].scrollIntoView();", first_link)
                        time.sleep(0.5)
                        first_link.click()
                        print("✓ Clicked first link!")
                        return True
                except:
                    continue
            print("✗ No clickable links found")
            return False
        except Exception as e:
            print(f"✗ Click failed: {e}")
            return False
    def click_nth_element(self, n, element_type="link"):
        try:
            print(f"🖱️  Clicking {n}th {element_type}...")
            selectors = {
                'link': "a[href]",
                'video': "video, ytd-video-renderer, ytd-grid-video-renderer",
                'button': "button",
                'image': "img",
                'result': "div.g, div.result, div[data-testid='result']",
            }
            selector = selectors.get(element_type.lower(), "a[href]")
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elements) >= n:
                target = elements[n - 1]
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
                time.sleep(1)
                target.click()
                print(f"✓ Clicked {n}th {element_type}!")
                return True
            else:
                print(f"✗ Only found {len(elements)} {element_type}s, cannot click {n}th")
                return False
        except Exception as e:
            print(f"✗ Click failed: {e}")
            return False
    def scroll_down(self, amount="medium"):
        try:
            print("📜 Scrolling down...")
            scroll_amounts = {
                'small': 300,
                'medium': 600,
                'large': 1000,
                'page': 'window.innerHeight',
            }
            pixels = scroll_amounts.get(amount, 600)
            if isinstance(pixels, str):
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            time.sleep(0.5)
            print("✓ Scrolled down!")
            return True
        except Exception as e:
            print(f"✗ Scroll failed: {e}")
            return False
    def scroll_up(self, amount="medium"):
        try:
            print("📜 Scrolling up...")
            scroll_amounts = {
                'small': 300,
                'medium': 600,
                'large': 1000,
                'page': 'window.innerHeight',
            }
            pixels = scroll_amounts.get(amount, 600)
            if isinstance(pixels, str):
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            time.sleep(0.5)
            print("✓ Scrolled up!")
            return True
        except Exception as e:
            print(f"✗ Scroll failed: {e}")
            return False
    def scroll_to_element(self, text):
        try:
            print(f"📜 Scrolling to: {text}")
            xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements:
                target = elements[0]
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
                time.sleep(1)
                print(f"✓ Scrolled to: {text}")
                return True
            else:
                print(f"✗ Could not find: {text}")
                return False
        except Exception as e:
            print(f"✗ Scroll failed: {e}")
            return False
    def close_popup(self):
        try:
            print("❌ Closing popup...")
            close_selectors = [
                "button[aria-label*='close' i]",
                "button[title*='close' i]",
                "[class*='close' i]",
                "button.close",
                "div[role='button'][aria-label*='close' i]",
                "svg[aria-label='Close']",
            ]
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    close_btn.click()
                    time.sleep(0.5)
                    print("✓ Popup closed!")
                    return True
                except:
                    continue
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
                print("✓ Pressed Escape key!")
                return True
            except:
                pass
            print("✗ No popup found or could not close")
            return False
        except Exception as e:
            print(f"✗ Close popup failed: {e}")
            return False
    def volume_up(self):
        try:
            print("🔊 Increasing volume...")
            video = self.driver.find_element(By.TAG_NAME, "video")
            current_volume = self.driver.execute_script("return arguments[0].volume;", video)
            new_volume = min(current_volume + 0.1, 1.0)
            self.driver.execute_script(f"arguments[0].volume = {new_volume};", video)
            print(f"✓ Volume increased to {int(new_volume * 100)}%")
            return True
        except Exception as e:
            print(f"✗ Volume up failed: {e}")
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ARROW_UP).perform()
                print("✓ Sent volume up key")
                return True
            except:
                return False
    def volume_down(self):
        try:
            print("🔉 Decreasing volume...")
            video = self.driver.find_element(By.TAG_NAME, "video")
            current_volume = self.driver.execute_script("return arguments[0].volume;", video)
            new_volume = max(current_volume - 0.1, 0.0)
            self.driver.execute_script(f"arguments[0].volume = {new_volume};", video)
            print(f"✓ Volume decreased to {int(new_volume * 100)}%")
            return True
        except Exception as e:
            print(f"✗ Volume down failed: {e}")
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ARROW_DOWN).perform()
                print("✓ Sent volume down key")
                return True
            except:
                return False
    def click_element_by_text(self, text, page_reader=None):
        try:
            print(f"🖱️  Clicking element: {text}")
            import re
            text_clean = re.sub(r'\b(called|titled|named|file|page|link|button|there is a|can you)\b', '', text.lower()).strip()
            if text_clean != text.lower():
                print(f"   Cleaned search text: '{text_clean}'")
            wait = WebDriverWait(self.driver, 5)
            try:
                xpath = f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text_clean}')]"
                element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].click();", element)
                print(f"✓ Clicked: {element.text.strip()}")
                return True
            except:
                pass
            try:
                xpath = f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text_clean}')]"
                element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].click();", element)
                print(f"✓ Clicked: {element.text.strip()}")
                return True
            except:
                pass
            try:
                words = text_clean.split()
                if len(words) > 1:
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
                    for link in links:
                        try:
                            if link.is_displayed():
                                link_text = link.text.lower()
                                matches = sum(1 for word in words if word in link_text)
                                if matches >= min(2, len(words)):
                                    self.driver.execute_script("arguments[0].click();", link)
                                    print(f"✓ Clicked (partial match): {link.text.strip()}")
                                    return True
                        except:
                            continue
            except:
                pass
            if page_reader:
                element = page_reader.find_element_by_partial_text(text_clean)
                if element:
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        print(f"✓ Clicked via PageReader!")
                        return True
                    except:
                        pass
            print(f"✗ Could not find element: {text}")
            return False
        except Exception as e:
            print(f"✗ Click failed: {e}")
            return False
    def highlight_element(self, element):
        try:
            css = """
            @keyframes pulse-circle {
                0% {
                    box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7),
                                0 0 0 0 rgba(255, 0, 0, 0.7);
                }
                50% {
                    box-shadow: 0 0 0 15px rgba(255, 0, 0, 0),
                                0 0 0 30px rgba(255, 0, 0, 0);
                }
                100% {
                    box-shadow: 0 0 0 0 rgba(255, 0, 0, 0),
                                0 0 0 0 rgba(255, 0, 0, 0);
                }
            }
            .ai-highlight {
                animation: pulse-circle 2s infinite !important;
                border: 3px solid red !important;
                border-radius: 8px !important;
                padding: 5px !important;
                transition: all 0.3s ease !important;
            }
            """
            self.driver.execute_script(f"""
                if (!document.getElementById('ai-highlight-style')) {{
                    var style = document.createElement('style');
                    style.id = 'ai-highlight-style';
                    style.textContent = `{css}`;
                    document.head.appendChild(style);
                }}
            """)
            self.driver.execute_script("""
                arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                arguments[0].classList.add('ai-highlight');
            """, element)
            print("✨ Element highlighted with animation!")
            return True
        except Exception as e:
            print(f"⚠ Could not highlight element: {e}")
            return False
    def remove_highlight(self, element=None):
        try:
            if element:
                self.driver.execute_script("""
                    arguments[0].classList.remove('ai-highlight');
                """, element)
            else:
                self.driver.execute_script("""
                    document.querySelectorAll('.ai-highlight').forEach(el => {
                        el.classList.remove('ai-highlight');
                    });
                """)
            return True
        except:
            return False
    def play_video_by_title(self, title):
        try:
            print(f"▶️  Playing video: {title}")
            youtube_selectors = [
                f"//ytd-video-renderer//a[@title[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{title.lower()}')]]",
                f"//ytd-grid-video-renderer//a[@title[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{title.lower()}')]]",
            ]
            for selector in youtube_selectors:
                try:
                    video_link = self.driver.find_element(By.XPATH, selector)
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", video_link)
                    time.sleep(1)
                    video_link.click()
                    print(f"✓ Playing video: {title}")
                    return True
                except:
                    continue
            xpath = f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{title.lower()}')]"
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements:
                target = elements[0]
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
                time.sleep(1)
                target.click()
                print(f"✓ Playing video: {title}")
                return True
            print(f"✗ Video not found: {title}")
            return False
        except Exception as e:
            print(f"✗ Play video failed: {e}")
            return False