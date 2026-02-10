"""
Google Maps scraper using Selenium with selenium-wire for proxy support
"""
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wire_webdriver
import config

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    def __init__(self, proxy=None):
        self.driver = None
        self.proxy = proxy
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with selenium-wire"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            if config.HEADLESS_MODE:
                chrome_options.add_argument('--headless')
            
            # Setup selenium-wire options for proxy
            seleniumwire_options = {}
            
            if self.proxy:
                proxy_string = f"http://{self.proxy['username']}:{self.proxy['password']}@{self.proxy['host']}:{self.proxy['port']}"
                seleniumwire_options['proxy'] = {
                    'http': proxy_string,
                    'https': proxy_string,
                    'no_proxy': 'localhost,127.0.0.1'
                }
                logger.info(f"Using proxy: {self.proxy['host']}:{self.proxy['port']}")
            
            # Create driver with selenium-wire
            self.driver = wire_webdriver.Chrome(
                options=chrome_options,
                seleniumwire_options=seleniumwire_options
            )
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            logger.info("Driver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            return False
    
    def search(self, query, city):
        """Search Google Maps"""
        try:
            search_query = f"{query} in {city}"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            
            logger.info(f"Searched: {search_query}")
            return True
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False
    
    def scroll_results(self, max_results=50):
        """Scroll and load results"""
        try:
            feed = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            results = []
            last_count = 0
            no_change_count = 0
            
            while len(results) < max_results and no_change_count < 3:
                # Get current results
                elements = feed.find_elements(By.CSS_SELECTOR, "div[role='article']")
                
                if len(elements) == last_count:
                    no_change_count += 1
                else:
                    no_change_count = 0
                    last_count = len(elements)
                
                # Scroll
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                time.sleep(random.uniform(config.SCROLL_PAUSE_MIN, config.SCROLL_PAUSE_MAX))
                
                # Check for "You've reached the end"
                try:
                    end_message = self.driver.find_element(By.XPATH, "//*[contains(text(), 'reached the end')]")
                    if end_message:
                        break
                except:
                    pass
            
            results = feed.find_elements(By.CSS_SELECTOR, "div[role='article']")[:max_results]
            logger.info(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return []
    
    def extract_business_data(self, element):
        """Extract data from business element with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                data = {}
                
                # Click to open details
                try:
                    element.click()
                    time.sleep(random.uniform(2, 4))
                except:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
                
                # Name (required)
                try:
                    data['name'] = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                    if not data['name']:
                        raise Exception("No name found")
                except:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
                
                # Category
                try:
                    data['category'] = self.driver.find_element(By.CSS_SELECTOR, "button[jsaction*='category']").text
                except:
                    data['category'] = None
                
                # Address
                try:
                    data['address'] = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']").text
                except:
                    data['address'] = None
                
                # Phone
                try:
                    data['phone'] = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='phone']").text
                except:
                    data['phone'] = None
                
                # Website
                try:
                    website_elem = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                    data['website'] = website_elem.get_attribute('href')
                except:
                    data['website'] = None
                
                # Maps URL
                data['maps_url'] = self.driver.current_url
                
                # Rating
                try:
                    rating_text = self.driver.find_element(By.CSS_SELECTOR, "div[role='img'][aria-label*='stars']").get_attribute('aria-label')
                    data['rating'] = float(rating_text.split()[0])
                except:
                    data['rating'] = None
                
                # Reviews
                try:
                    reviews_text = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='reviews']").text
                    data['reviews'] = int(reviews_text.replace(',', '').replace('(', '').replace(')', ''))
                except:
                    data['reviews'] = None
                
                # Success - return data
                return data
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.debug(f"Extract attempt {attempt + 1} failed, retrying...")
                    time.sleep(1)
                    continue
                else:
                    logger.debug(f"Extract failed after {max_retries} attempts (skipping)")
                    return None
        
        return None
    
    def close(self):
        """Close driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver closed")
            except:
                pass
