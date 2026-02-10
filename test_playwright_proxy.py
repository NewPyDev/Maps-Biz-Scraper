"""
Playwright Proxy Verification Test
Tests if Playwright correctly routes traffic through authenticated proxies
"""
from playwright.sync_api import sync_playwright
import time

def test_playwright_proxy():
    print("=" * 60)
    print("PLAYWRIGHT PROXY VERIFICATION TEST")
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
                print(f"\n✓ Testing proxy: {user}:***@{host}:{port}")
            else:
                print("❌ Invalid proxy format. Expected: ip:port:user:pass")
                return
    except FileNotFoundError:
        print("❌ proxies.txt not found")
        return
    
    # Configure proxy for Playwright
    proxy_config = {
        "server": f"http://{host}:{port}",
        "username": user,
        "password": password
    }
    
    print("\n🔧 Starting Playwright with proxy...")
    
    with sync_playwright() as p:
        # Launch browser with proxy
        browser = p.chromium.launch(
            headless=True,
            proxy=proxy_config
        )
        
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Test 1: Check IP via httpbin.org
            print("\n📡 Test 1: Checking IP via httpbin.org/ip...")
            page.goto("https://httpbin.org/ip", timeout=30000)
            time.sleep(2)
            
            page_text = page.content()
            body_text = page.locator("body").inner_text()
            
            print(f"   Response: {body_text}")
            
            if host in body_text:
                print(f"   ✅ SUCCESS! Traffic is going through proxy {host}")
                proxy_working = True
            else:
                print(f"   ⚠️  Expected to see {host} in response")
                proxy_working = False
            
            # Test 2: Access Google Maps
            print("\n🗺️  Test 2: Accessing Google Maps...")
            page.goto("https://www.google.com/maps", timeout=30000)
            time.sleep(3)
            
            if "google" in page.url.lower():
                print("   ✅ Successfully accessed Google Maps through proxy")
            else:
                print("   ⚠️  Failed to access Google Maps")
            
            # Test 3: Search on Google Maps
            print("\n🔍 Test 3: Testing Google Maps search...")
            page.goto("https://www.google.com/maps/search/plumbers+in+Prague", timeout=30000)
            time.sleep(5)
            
            # Check if results loaded
            if page.locator("div[role='feed']").count() > 0:
                print("   ✅ Search results loaded successfully")
            else:
                print("   ⚠️  Search results did not load")
            
            print("\n" + "=" * 60)
            print("PLAYWRIGHT PROXY TEST COMPLETE")
            print("=" * 60)
            
            if proxy_working:
                print("\n✅ PROXY IS WORKING CORRECTLY!")
                print("   Playwright successfully routes traffic through your proxy.")
                print("   You can now use Playwright for scraping with confidence.")
            else:
                print("\n⚠️  PROXY VERIFICATION UNCLEAR")
                print("   Check the responses above to verify proxy usage.")
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_playwright_proxy()
