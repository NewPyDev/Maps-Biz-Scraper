"""
Test script to debug Google Maps scraping
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup simple driver without proxy
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Search Google Maps
    driver.get("https://www.google.com/maps/search/plumbers+in+Prague")
    print("Loaded Google Maps")
    time.sleep(5)
    
    # Wait for results
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
    )
    print("Found results feed")
    
    # Get first business
    results_container = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
    businesses = results_container.find_elements(By.CSS_SELECTOR, "div[role='article']")
    print(f"Found {len(businesses)} businesses")
    
    if businesses:
        print("\nClicking first business...")
        businesses[0].click()
        time.sleep(5)
        
        # Save page source to file for inspection
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Saved page source to page_source.html")
        
        # Try to find name
        print("\nLooking for business name...")
        name_selectors = ["h1", "h2", "div.fontHeadlineLarge", "span.fontHeadlineLarge"]
        for selector in name_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.text:
                        print(f"  {selector}: {elem.text[:100]}")
            except:
                pass
        
        # Try to find all buttons
        print("\nLooking for buttons...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(buttons[:20]):  # First 20 buttons
            try:
                aria_label = btn.get_attribute('aria-label')
                data_item_id = btn.get_attribute('data-item-id')
                if aria_label or data_item_id:
                    print(f"  Button {i}: aria-label='{aria_label}', data-item-id='{data_item_id}'")
            except:
                pass
        
        # Try to find all links
        print("\nLooking for links...")
        links = driver.find_elements(By.TAG_NAME, "a")
        for i, link in enumerate(links[:20]):  # First 20 links
            try:
                href = link.get_attribute('href')
                aria_label = link.get_attribute('aria-label')
                data_item_id = link.get_attribute('data-item-id')
                if href and ('http' in href or 'tel:' in href):
                    print(f"  Link {i}: href='{href[:50]}...', aria-label='{aria_label}', data-item-id='{data_item_id}'")
            except:
                pass
        
        print("\nKeeping browser open for 30 seconds for manual inspection...")
        time.sleep(30)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("Done!")
