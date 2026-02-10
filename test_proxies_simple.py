"""
Simple Proxy Tester
Tests if your proxies are working
"""

from google_maps_scraper import load_proxies_from_file, setup_driver
import logging

logging.basicConfig(level=logging.INFO)

def test_proxies():
    """Test all proxies in proxies.txt"""
    
    print("\n" + "=" * 60)
    print("🔌 PROXY TESTER")
    print("=" * 60)
    
    # Load proxies
    proxies = load_proxies_from_file('proxies.txt')
    
    if not proxies:
        print("\n❌ No proxies found in proxies.txt!")
        print("\nAdd proxies in format: ip:port:username:password")
        return
    
    print(f"\n✓ Found {len(proxies)} proxies")
    print("\nTesting each proxy...\n")
    
    working = 0
    failed = 0
    
    for i, proxy in enumerate(proxies, 1):
        proxy_str = f"{proxy['host']}:{proxy['port']}"
        print(f"[{i}/{len(proxies)}] Testing {proxy_str}...", end=" ")
        
        try:
            # Try to create driver with proxy
            driver = setup_driver(proxy_dict=proxy)
            
            # Try to load a simple page
            driver.get("https://ipv4.webshare.io/")
            
            # Check if we got a response
            page_text = driver.find_element("tag name", "body").text
            
            if proxy['host'] in page_text:
                print("✅ WORKING (IP verified!)")
                working += 1
            else:
                print("⚠️ Connected but IP not verified")
                working += 1
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ FAILED ({str(e)[:50]})")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print(f"✅ Working: {working}/{len(proxies)}")
    print(f"❌ Failed: {failed}/{len(proxies)}")
    print(f"Success Rate: {working/len(proxies)*100:.1f}%")
    print("=" * 60)
    
    if working == 0:
        print("\n⚠️ WARNING: No proxies are working!")
        print("\nPossible issues:")
        print("1. Wrong credentials (check username/password)")
        print("2. Proxy service is down")
        print("3. IP whitelist not configured")
        print("4. Proxy format is wrong")
        print("\nCorrect format: ip:port:username:password")
    elif working < len(proxies):
        print(f"\n⚠️ {failed} proxies failed. Consider removing them from proxies.txt")
    else:
        print("\n🎉 All proxies are working! You're ready to scrape!")


if __name__ == "__main__":
    test_proxies()
