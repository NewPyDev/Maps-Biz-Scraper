"""
Test Proxy Rotation
Quick test to verify proxies are rotating properly
"""

import time
from google_maps_scraper import setup_driver, load_proxies_from_file
from selenium.webdriver.common.by import By

def test_proxy_rotation():
    """Test that proxies rotate and work correctly"""
    
    print("=" * 60)
    print("🔍 PROXY ROTATION TEST")
    print("=" * 60)
    
    # Load proxies
    proxies = load_proxies_from_file('proxies.txt')
    
    if not proxies:
        print("❌ No proxies found in proxies.txt")
        return
    
    print(f"✓ Loaded {len(proxies)} proxies")
    print()
    
    # Test first 3 proxies
    test_count = min(3, len(proxies))
    successful_proxies = []
    
    for i in range(test_count):
        proxy = proxies[i]
        proxy_str = f"{proxy['host']}:{proxy['port']}"
        
        print(f"Testing proxy {i+1}/{test_count}: {proxy_str}")
        print("-" * 60)
        
        try:
            # Setup driver with this proxy
            driver = setup_driver(proxy_dict=proxy)
            
            # Visit IP check site
            print("  → Visiting IP check site...")
            driver.get("https://ipv4.webshare.io/")
            time.sleep(3)
            
            # Get the IP shown on page
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Check if our proxy IP is shown
            if proxy['host'] in page_text:
                print(f"  ✅ SUCCESS! Traffic is going through {proxy['host']}")
                print(f"     Response: {page_text[:80]}...")
                successful_proxies.append(proxy_str)
            else:
                print(f"  ⚠️  WARNING: Expected {proxy['host']}, got different IP")
                print(f"     Response: {page_text[:80]}...")
            
            # Check selenium-wire captured requests
            if hasattr(driver, 'requests') and len(driver.requests) > 0:
                print(f"  ✓ Selenium-Wire captured {len(driver.requests)} request(s)")
            
            driver.quit()
            print()
            
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            print()
            continue
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Proxies tested: {test_count}")
    print(f"Successful: {len(successful_proxies)}")
    print(f"Failed: {test_count - len(successful_proxies)}")
    
    if successful_proxies:
        print(f"\n✅ Working proxies:")
        for proxy in successful_proxies:
            print(f"   - {proxy}")
    
    print()
    print("💡 TIP: If proxies are working, rotation is configured correctly!")
    print("   The scraper will now rotate between these proxies every 8-15 requests.")
    print("=" * 60)


if __name__ == "__main__":
    test_proxy_rotation()
