"""
Proxy Verification Test
Tests if proxies from proxies.txt are working with Playwright
"""
import logging
from playwright.sync_api import sync_playwright
from proxy_manager import get_proxy_manager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_proxy(proxy_config):
    """Test a single proxy configuration"""
    try:
        with sync_playwright() as p:
            logger.info(f"Testing proxy: {proxy_config['server']}")
            
            browser = p.chromium.launch(
                headless=True,
                proxy=proxy_config
            )
            
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(30000)  # 30 second timeout
            
            # Test 1: Check IP
            logger.info("  → Checking IP address...")
            page.goto("https://api.ipify.org?format=json", wait_until="domcontentloaded")
            ip_response = page.content()
            logger.info(f"  ✓ Response: {ip_response[:100]}")
            
            # Test 2: Check Google
            logger.info("  → Testing Google access...")
            page.goto("https://www.google.com", wait_until="domcontentloaded")
            title = page.title()
            logger.info(f"  ✓ Google title: {title}")
            
            browser.close()
            
            logger.info("  ✅ PROXY WORKS!")
            return True
            
    except Exception as e:
        logger.error(f"  ❌ PROXY FAILED: {e}")
        return False


def main():
    """Test all proxies from proxies.txt"""
    logger.info("="*60)
    logger.info("PROXY VERIFICATION TEST")
    logger.info("="*60)
    
    # Load proxies
    proxy_mgr = get_proxy_manager()
    
    if not proxy_mgr.has_proxies():
        logger.warning("No proxies found in proxies.txt")
        return
    
    logger.info(f"Found {len(proxy_mgr.proxies)} proxies to test\n")
    
    # Test each proxy
    working_proxies = []
    failed_proxies = []
    
    for i, proxy in enumerate(proxy_mgr.proxies, 1):
        logger.info(f"[{i}/{len(proxy_mgr.proxies)}] Testing proxy...")
        proxy_config = proxy.to_playwright_config()
        
        if test_proxy(proxy_config):
            working_proxies.append(proxy)
        else:
            failed_proxies.append(proxy)
        
        logger.info("")  # Blank line
    
    # Summary
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info(f"✅ Working proxies: {len(working_proxies)}")
    logger.info(f"❌ Failed proxies: {len(failed_proxies)}")
    
    if working_proxies:
        logger.info("\n✅ Working proxies:")
        for proxy in working_proxies:
            logger.info(f"  - {proxy}")
    
    if failed_proxies:
        logger.info("\n❌ Failed proxies:")
        for proxy in failed_proxies:
            logger.info(f"  - {proxy}")
    
    logger.info("="*60)
    
    if len(working_proxies) == 0:
        logger.warning("\n⚠️ NO WORKING PROXIES FOUND")
        logger.warning("The scraper will work WITHOUT proxies.")
        logger.warning("To use proxies, verify your proxy server credentials.")
    else:
        logger.info(f"\n✅ {len(working_proxies)} proxies are ready to use!")


if __name__ == "__main__":
    main()
