
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class MediaPlayer:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
    def play_first_youtube_result(self, query):
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            print(f"🔍 Searching YouTube: {search_url}")
            self.driver.get(search_url)
            time.sleep(2)
            try:
                first_video = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a#video-title"))
                )
                video_url = first_video.get_attribute('href')
                video_title = first_video.get_attribute('title')
                print(f"▶️  Playing: {video_title}")
                first_video.click()
                time.sleep(2)
                return True, f"Playing: {video_title}"
            except TimeoutException:
                print("⚠ Could not find video results")
                return False, "No results found"
        except Exception as e:
            print(f"❌ Error playing video: {e}")
            return False, str(e)
    def play_first_spotify_result(self, query):
        try:
            search_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
            print(f"🔍 Searching Spotify: {search_url}")
            self.driver.get(search_url)
            time.sleep(3)
            return True, f"Opened Spotify search for: {query}"
        except Exception as e:
            print(f"❌ Error with Spotify: {e}")
            return False, str(e)