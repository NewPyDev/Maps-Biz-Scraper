"""
Test if proxies are actually being used
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import zipfile

# Your proxy details
PROXY_HOST = "142.111.48.253"
PROXY_PORT = "7030"
PROXY_USER = "nnqlhtxn"
PROXY_PASS = "z1g2w2piodx9"

def create_proxy_extension():
    """Create Chrome extension for authenticated proxy"""
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    plugin_path = 'test_proxy_plugin.zip'
    
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    
    return plugin_path

print("Testing proxy usage...")
print("=" * 60)

# Setup Chrome with proxy extension
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')

# Add proxy extension
proxy_extension = create_proxy_extension()
options.add_extension(proxy_extension)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print("\n1. Checking IP WITHOUT proxy (direct connection)...")
    print("   (This should show your real IP)")
    
    # First, let's see what IP we get
    driver.get("https://api.ipify.org?format=json")
    time.sleep(2)
    ip_response = driver.find_element("tag name", "body").text
    print(f"   Response: {ip_response}")
    
    print("\n2. Checking IP WITH proxy...")
    print(f"   Expected proxy IP: {PROXY_HOST}")
    
    # Check if we're using the proxy
    driver.get("https://ipv4.webshare.io/")
    time.sleep(3)
    proxy_response = driver.find_element("tag name", "body").text
    print(f"   Response: {proxy_response[:200]}")
    
    if PROXY_HOST in proxy_response:
        print("\n✅ SUCCESS! Proxy is working!")
        print(f"   Your traffic is going through: {PROXY_HOST}")
    else:
        print("\n❌ PROBLEM! Proxy is NOT working!")
        print("   Your traffic is NOT going through the proxy")
        print("   The scraper is using your real IP!")
    
    print("\n3. Testing Google access through proxy...")
    driver.get("https://www.google.com")
    time.sleep(2)
    if "Google" in driver.title:
        print("   ✓ Can access Google through proxy")
    else:
        print("   ✗ Cannot access Google")
    
    print("\n" + "=" * 60)
    print("Test complete. Check the results above.")
    print("=" * 60)
    
    input("\nPress Enter to close browser...")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    import os
    if os.path.exists('test_proxy_plugin.zip'):
        os.remove('test_proxy_plugin.zip')
    print("Done!")
