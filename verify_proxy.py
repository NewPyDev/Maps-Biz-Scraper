"""
Simple proxy verification test
Tests if selenium-wire is correctly routing traffic through proxies
"""
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_proxy():
    print("=" * 60)
    print("PROXY VERIFICATION TEST")
    print("=" * 60)
    
    # Load first proxy from proxies.txt
    try:
        with open('proxies.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if not lines:
                print("❌ No proxies found in proxies.txt")
                return
            
            # Parse first proxy (format: ip:port:user:pass)
            parts = lines[0].split(':')
            if len(parts) == 4:
                host, port, user, password = parts
                proxy_url = f"http://{user}:{password}@{host}:{port}"
                print(f"\n✓ Testing proxy: {user}:***@{host}:{port}")
            else:
                print("❌ Invalid proxy format. Expected: ip:port:user:pass")
                return
    except FileNotFoundError:
        print("❌ proxies.txt not found")
        return
    
    # Setup selenium-wire with proxy
    seleniumwire_options = {
        'proxy': {
            'http': proxy_url,
            'https': proxy_url,
        },
        'verify_ssl': False
    }
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    print("\n🔧 Setting up Chrome with selenium-wire...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(
        service=service,
        options=options,
        seleniumwire_options=seleniumwire_options
    )
    
    try:
        # Test 1: Check IP via httpbin.org
        print("\n📡 Test 1: Checking IP via httpbin.org/ip...")
        driver.get("https://httpbin.org/ip")
        time.sleep(2)
        
        page_text = driver.find_element("tag name", "body").text
        print(f"   Response: {page_text}")
        
        if host in page_text:
            print(f"   ✅ SUCCESS! Traffic is going through proxy {host}")
        else:
            print(f"   ⚠️  Expected to see {host} in response")
        
        # Test 2: Check selenium-wire captured requests
        print("\n📊 Test 2: Checking selenium-wire request capture...")
        if hasattr(driver, 'requests') and len(driver.requests) > 0:
            print(f"   ✅ Selenium-wire captured {len(driver.requests)} request(s)")
            for req in driver.requests[:3]:  # Show first 3
                print(f"      - {req.method} {req.url[:60]}")
        else:
            print("   ⚠️  No requests captured by selenium-wire")
        
        # Test 3: Access Google Maps
        print("\n🗺️  Test 3: Accessing Google Maps...")
        driver.get("https://www.google.com/maps")
        time.sleep(3)
        
        if "google" in driver.current_url.lower():
            print("   ✅ Successfully accessed Google Maps through proxy")
        else:
            print("   ⚠️  Failed to access Google Maps")
        
        print("\n" + "=" * 60)
        print("PROXY TEST COMPLETE")
        print("=" * 60)
        print("\n✅ If you see your proxy IP in Test 1, proxies are working!")
        print("⚠️  If you see your real IP, proxies are NOT working.")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_proxy()
