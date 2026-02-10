"""
Test script to verify website detection is working correctly
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup simple driver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Search for restaurants in Madrid
    driver.get("https://www.google.com/maps/search/restaurants+in+Madrid")
    print("Loaded Google Maps")
    time.sleep(5)
    
    # Wait for results
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
    )
    
    # Get first 3 businesses
    results_container = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
    businesses = results_container.find_elements(By.CSS_SELECTOR, "div[role='article']")[:3]
    
    print(f"\nTesting website detection on {len(businesses)} businesses:\n")
    print("=" * 80)
    
    for i, business in enumerate(businesses, 1):
        business.click()
        time.sleep(3)
        
        # Get business name
        try:
            name_link = business.find_element(By.CSS_SELECTOR, "a")
            name = name_link.get_attribute('aria-label')
        except:
            name = "Unknown"
        
        print(f"\n{i}. {name}")
        print("-" * 80)
        
        # Check for website link with data-item-id='authority'
        website_links = driver.find_elements(By.CSS_SELECTOR, "a[data-item-id='authority']")
        
        if website_links:
            href = website_links[0].get_attribute('href')
            aria = website_links[0].get_attribute('aria-label')
            print(f"   ✓ Found website link:")
            print(f"     - href: {href}")
            print(f"     - aria-label: {aria}")
            
            if 'google.com' in href:
                print(f"   ⚠️  WARNING: This is a Google link, should be marked as NO website!")
            else:
                print(f"   ✓ Valid external website - should be marked as YES")
        else:
            print(f"   ✗ No website link found (data-item-id='authority')")
            
            # Check alternative method
            all_links = driver.find_elements(By.TAG_NAME, "a")
            found_website = False
            for link in all_links[:30]:  # Check first 30 links
                aria = link.get_attribute('aria-label')
                href = link.get_attribute('href')
                if aria and href:
                    aria_lower = aria.lower()
                    if any(word in aria_lower for word in ['website', 'site web', 'sitio web']):
                        if 'http' in href and 'google.com' not in href:
                            print(f"   ✓ Found via alternative method:")
                            print(f"     - href: {href}")
                            print(f"     - aria-label: {aria}")
                            found_website = True
                            break
            
            if not found_website:
                print(f"   ✓ Confirmed: NO website - should be marked as NO")
        
        time.sleep(2)
    
    print("\n" + "=" * 80)
    print("Test complete! Check the results above.")
    print("=" * 80)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    input("\nPress Enter to close browser...")
    driver.quit()
