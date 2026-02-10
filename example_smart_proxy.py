"""
Example: Using Playwright with Smart Proxy Manager
Shows how the app works with or without proxies automatically
"""
from playwright.sync_api import sync_playwright
from proxy_manager import get_proxy_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_with_smart_proxy():
    """
    Example scraper that automatically uses proxies if available
    No code changes needed when adding/removing proxies!
    """
    # Get proxy manager (automatically detects proxies.txt)
    proxy_mgr = get_proxy_manager()
    
    # Get proxy config (None if no proxies available)
    proxy_config = proxy_mgr.get_playwright_config()
    
    with sync_playwright() as p:
        # Launch browser with proxy if available, without if not
        launch_options = {"headless": True}
        if proxy_config:
            launch_options["proxy"] = proxy_config
        
        browser = p.chromium.launch(**launch_options)
        page = browser.new_page()
        
        try:
            # Your scraping code here
            logger.info("Accessing Google Maps...")
            page.goto("https://www.google.com/maps/search/plumbers+in+Prague", timeout=30000)
            
            # Wait for results
            page.wait_for_selector("div[role='feed']", timeout=15000)
            
            logger.info("✅ Successfully loaded Google Maps!")
            logger.info(f"   URL: {page.url}")
            
            # If using proxy, mark it as successful
            if proxy_config and proxy_mgr.has_proxies():
                current_proxy = proxy_mgr.proxies[(proxy_mgr.current_index - 1) % len(proxy_mgr.proxies)]
                proxy_mgr.mark_proxy_success(current_proxy)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            
            # If using proxy, mark it as failed and try next one
            if proxy_config and proxy_mgr.has_proxies():
                current_proxy = proxy_mgr.proxies[(proxy_mgr.current_index - 1) % len(proxy_mgr.proxies)]
                proxy_mgr.mark_proxy_failure(current_proxy)
        
        finally:
            browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("SMART PROXY EXAMPLE")
    print("=" * 60)
    print("\nThis example automatically:")
    print("  - Uses proxies if proxies.txt exists")
    print("  - Works without proxies if file doesn't exist")
    print("  - No code changes needed!")
    print("\n" + "=" * 60 + "\n")
    
    scrape_with_smart_proxy()
