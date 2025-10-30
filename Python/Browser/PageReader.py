
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from difflib import SequenceMatcher

class PageReader:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
    def get_page_summary(self):
        try:
            print("\n📄 Analyzing current page...")
            title = self.driver.title
            url = self.driver.current_url
            print(f"\n🌐 Page: {title}")
            print(f"🔗 URL: {url}\n")
            links = self._get_visible_links()
            buttons = self._get_visible_buttons()
            headings = self._get_visible_headings()
            summary = {
                'title': title,
                'url': url,
                'links': links,
                'buttons': buttons,
                'headings': headings
            }
            return summary
        except Exception as e:
            print(f"❌ Error reading page: {e}")
            return None
    def _get_visible_links(self):
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            visible_links = []
            for link in links[:50]:
                try:
                    if link.is_displayed() and link.text.strip():
                        text = link.text.strip()
                        href = link.get_attribute('href')
                        visible_links.append({'text': text, 'href': href})
                except:
                    continue
            if visible_links:
                print("🔗 Visible Links:")
                for i, link in enumerate(visible_links[:20], 1):
                    print(f"   [{i}] {link['text'][:60]}")
                if len(visible_links) > 20:
                    print(f"   ... and {len(visible_links) - 20} more links")
            return visible_links
        except Exception as e:
            return []
    def _get_visible_buttons(self):
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            visible_buttons = []
            for button in buttons[:30]:
                try:
                    if button.is_displayed() and button.text.strip():
                        text = button.text.strip()
                        visible_buttons.append(text)
                except:
                    continue
            if visible_buttons:
                print("\n🔘 Visible Buttons:")
                for i, btn in enumerate(visible_buttons[:15], 1):
                    print(f"   [{i}] {btn[:60]}")
                if len(visible_buttons) > 15:
                    print(f"   ... and {len(visible_buttons) - 15} more buttons")
            return visible_buttons
        except Exception as e:
            return []
    def _get_visible_headings(self):
        try:
            headings = []
            for tag in ['h1', 'h2', 'h3']:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for elem in elements:
                    try:
                        if elem.is_displayed() and elem.text.strip():
                            headings.append({'level': tag, 'text': elem.text.strip()})
                    except:
                        continue
            if headings:
                print("\n📌 Visible Headings:")
                for i, heading in enumerate(headings[:15], 1):
                    print(f"   [{i}] {heading['level'].upper()}: {heading['text'][:60]}")
                if len(headings) > 15:
                    print(f"   ... and {len(headings) - 15} more headings")
            return headings
        except Exception as e:
            return []
    def find_element_by_partial_text(self, text):
        try:
            text_lower = text.lower()
            text_lower = re.sub(r'\b(called|titled|named|file|page|link|button)\b', '', text_lower).strip()
            print(f"🔍 Searching for elements containing: '{text_lower}'")
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            for link in links:
                try:
                    if link.is_displayed() and text_lower in link.text.lower():
                        print(f"   ✓ Found link: {link.text.strip()}")
                        return link
                except:
                    continue
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    if button.is_displayed() and text_lower in button.text.lower():
                        print(f"   ✓ Found button: {button.text.strip()}")
                        return button
                except:
                    continue
            all_elements = self.driver.find_elements(By.XPATH, "//*")
            for elem in all_elements:
                try:
                    if elem.is_displayed() and elem.text and text_lower in elem.text.lower():
                        print(f"   ✓ Found element: {elem.text.strip()[:60]}")
                        return elem
                except:
                    continue
            print(f"   ✗ No elements found containing: '{text_lower}'")
            return None
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return None
    def get_all_clickable_elements(self):
        try:
            clickable = []
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            for link in links[:50]:
                try:
                    if link.is_displayed() and link.text.strip():
                        clickable.append(('link', link.text.strip()))
                except:
                    continue
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons[:30]:
                try:
                    if button.is_displayed() and button.text.strip():
                        clickable.append(('button', button.text.strip()))
                except:
                    continue
            return clickable
        except Exception as e:
            return []
    def find_closest_match(self, search_text, threshold=0.5):
        try:
            search_text_lower = search_text.lower().strip()
            print(f"\n🔍 Searching for closest match to: '{search_text}'")
            candidates = []
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            for link in links[:100]:
                try:
                    if link.is_displayed() and link.text.strip():
                        candidates.append((link, link.text.strip(), 'link'))
                except:
                    continue
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons[:50]:
                try:
                    if button.is_displayed() and button.text.strip():
                        candidates.append((button, button.text.strip(), 'button'))
                except:
                    continue
            matches = []
            for elem, text, elem_type in candidates:
                text_lower = text.lower()
                ratio = SequenceMatcher(None, search_text_lower, text_lower).ratio()
                search_words = set(search_text_lower.split())
                text_words = set(text_lower.split())
                if search_words and text_words:
                    word_ratio = len(search_words & text_words) / max(len(search_words), len(text_words))
                else:
                    word_ratio = 0
                combined_score = (ratio * 0.4) + (word_ratio * 0.6)
                if combined_score >= threshold:
                    matches.append({
                        'element': elem,
                        'text': text,
                        'type': elem_type,
                        'score': combined_score
                    })
            matches.sort(key=lambda x: x['score'], reverse=True)
            if matches:
                best_match = matches[0]
                print(f"   ✓ Best match: '{best_match['text']}' (score: {best_match['score']:.2f})")
                if len(matches) > 1:
                    print(f"   📋 Other matches:")
                    for match in matches[1:4]:
                        print(f"      - '{match['text']}' (score: {match['score']:.2f})")
                return best_match
            else:
                print("   ✗ No close matches found")
                return None
        except Exception as e:
            print(f"❌ Fuzzy search failed: {e}")
            return None