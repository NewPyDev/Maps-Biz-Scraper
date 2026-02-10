"""
Simple Playwright Proxy Test
Quick test to verify proxy authentication works
"""
from playwright.sync_api import sync_playwright

def test_proxy():
    print("Testing Playwright with proxy...")
    
    # Load proxy
    with open('proxies.txt', 'r') as f:
        line = f.readline().strip()
        host, port, user, password = line.split(':')
    
    print(f"Proxy: {user}:***@{host}:{port}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={
                "server": f"http://{host}:{port}",
                "username": user,
                "password": password
            }
        )
        
        page = browser.new_page()
        
        try:
            print("Accessing Google Maps...")
            page.goto("https://www.google.com/maps", timeout=15000)
            print(f"✅ SUCCESS! Accessed: {page.url}")
            print("✅ Playwright proxy authentication is working!")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_proxy()
