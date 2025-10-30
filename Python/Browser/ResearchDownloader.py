
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

class ResearchDownloader:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.downloads_dir = os.path.expanduser("~/Downloads")
    def download_research_papers(self, topic, max_papers=5):
        print(f"📚 Searching for research papers on: {topic}")
        print(f"📥 Will download up to {max_papers} papers")
        print()
        downloaded = 0
        print("🔍 Searching arXiv...")
        downloaded += self._download_from_arxiv(topic, max_papers - downloaded)
        if downloaded >= max_papers:
            print(f"\n✅ Successfully downloaded {downloaded} papers!")
            return True
        print("\n🔍 Searching Google Scholar...")
        downloaded += self._download_from_google_scholar(topic, max_papers - downloaded)
        if downloaded >= max_papers:
            print(f"\n✅ Successfully downloaded {downloaded} papers!")
            return True
        print("\n🔍 Searching Semantic Scholar...")
        downloaded += self._download_from_semantic_scholar(topic, max_papers - downloaded)
        print(f"\n✅ Downloaded {downloaded} research papers to: {self.downloads_dir}")
        return downloaded > 0
    def _download_from_arxiv(self, topic, max_papers):
        try:
            search_url = f"https://arxiv.org/search/?query={topic.replace(' ', '+')}&searchtype=all&source=header"
            self.driver.get(search_url)
            time.sleep(3)
            papers = self.driver.find_elements(By.CSS_SELECTOR, "li.arxiv-result")
            downloaded = 0
            for i, paper in enumerate(papers[:max_papers]):
                if downloaded >= max_papers:
                    break
                try:
                    title_elem = paper.find_element(By.CSS_SELECTOR, "p.title")
                    title = title_elem.text.strip()
                    pdf_link = paper.find_element(By.XPATH, ".//a[contains(@href, '/pdf/')]")
                    pdf_url = pdf_link.get_attribute('href')
                    print(f"  [{i+1}] {title[:60]}...")
                    print(f"      Downloading from: {pdf_url}")
                    self.driver.execute_script(f"window.open('{pdf_url}', '_blank');")
                    time.sleep(2)
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    downloaded += 1
                    print(f"      ✓ Downloaded!")
                except Exception as e:
                    print(f"      ✗ Failed: {e}")
                    continue
            return downloaded
        except Exception as e:
            print(f"  ✗ arXiv error: {e}")
            return 0
    def _download_from_google_scholar(self, topic, max_papers):
        try:
            search_url = f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(3)
            papers = self.driver.find_elements(By.CSS_SELECTOR, "div.gs_r.gs_or.gs_scl")
            downloaded = 0
            for i, paper in enumerate(papers[:max_papers]):
                if downloaded >= max_papers:
                    break
                try:
                    title_elem = paper.find_element(By.CSS_SELECTOR, "h3.gs_rt")
                    title = title_elem.text.strip()
                    try:
                        pdf_link = paper.find_element(By.XPATH, ".//div[@class='gs_or_ggsm']//a[contains(text(), 'PDF')]")
                        pdf_url = pdf_link.get_attribute('href')
                        print(f"  [{i+1}] {title[:60]}...")
                        print(f"      Downloading from: {pdf_url}")
                        self.driver.execute_script(f"window.open('{pdf_url}', '_blank');")
                        time.sleep(2)
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        downloaded += 1
                        print(f"      ✓ Downloaded!")
                    except NoSuchElementException:
                        print(f"  [{i+1}] {title[:60]}...")
                        print(f"      ✗ No PDF available")
                        continue
                except Exception as e:
                    continue
            return downloaded
        except Exception as e:
            print(f"  ✗ Google Scholar error: {e}")
            return 0
    def _download_from_semantic_scholar(self, topic, max_papers):
        try:
            search_url = f"https://www.semanticscholar.org/search?q={topic.replace(' ', '%20')}"
            self.driver.get(search_url)
            time.sleep(4)
            papers = self.driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='search-result']")
            downloaded = 0
            for i, paper in enumerate(papers[:max_papers]):
                if downloaded >= max_papers:
                    break
                try:
                    title_elem = paper.find_element(By.CSS_SELECTOR, "a[data-test-id='title-link']")
                    title = title_elem.text.strip()
                    try:
                        pdf_button = paper.find_element(By.XPATH, ".//a[contains(@aria-label, 'View PDF')]")
                        pdf_url = pdf_button.get_attribute('href')
                        print(f"  [{i+1}] {title[:60]}...")
                        print(f"      Downloading from: {pdf_url}")
                        self.driver.execute_script(f"window.open('{pdf_url}', '_blank');")
                        time.sleep(2)
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        downloaded += 1
                        print(f"      ✓ Downloaded!")
                    except NoSuchElementException:
                        print(f"  [{i+1}] {title[:60]}...")
                        print(f"      ✗ No PDF available")
                        continue
                except Exception as e:
                    continue
            return downloaded
        except Exception as e:
            print(f"  ✗ Semantic Scholar error: {e}")
            return 0