import requests
import re
import logging
import time
import concurrent.futures
from typing import List, Set, Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_proxies() -> List[str]:
    """
    Fetch free proxies from multiple sources.
    Returns a list of unique 'ip:port' strings.
    """
    proxies: Set[str] = set()
    
    # Source 1: ProxyScrape (HTTP/S)
    try:
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        logger.info(f"Fetching from ProxyScrape: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if validate_proxy(line):
                    proxies.add(line)
            logger.info(f"Got {len(lines)} proxies from ProxyScrape")
    except Exception as e:
        logger.error(f"Error fetching from ProxyScrape: {e}")

    # Source 2: Spys.me (Text list)
    try:
        url = "http://spys.me/proxy.txt"
        logger.info(f"Fetching from Spys.me: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            count = 0
            for line in lines:
                match = re.match(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', line)
                if match:
                    proxy = match.group(1)
                    if validate_proxy(proxy):
                        proxies.add(proxy)
                        count += 1
            logger.info(f"Got {count} proxies from Spys.me")
    except Exception as e:
        logger.error(f"Error fetching from Spys.me: {e}")

    # Source 3: Daily Free Proxy List (Github raw)
    try:
        url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        logger.info(f"Fetching from TheSpeedX Github: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if validate_proxy(line):
                    proxies.add(line)
            logger.info(f"Got {len(lines)} proxies from TheSpeedX")
    except Exception as e:
        logger.error(f"Error fetching from TheSpeedX: {e}")

    unique_proxies = sorted(list(proxies))
    logger.info(f"Total unique proxies collected: {len(unique_proxies)}")
    return unique_proxies

def validate_proxy(proxy: str) -> bool:
    """Simple regex validation for IP:Port"""
    pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'
    match = re.match(pattern, proxy)
    if not match:
        return False
        
    ip_parts = match.group(1).split('.')
    if any(int(part) > 255 for part in ip_parts):
        return False
        
    port = int(match.group(2))
    if port > 65535:
        return False
        
    return True

def check_proxy(proxy, url="http://www.google.com/robots.txt", timeout=4):
    """
    Check if a proxy works by requesting a lightweight URL.
    Returns: (proxy, latency_ms) if working, False otherwise
    """
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        start_time = time.time()
        # Use verify=False to avoid SSL errors on free proxies, and short timeout
        response = requests.get(url, proxies=proxies, timeout=timeout, verify=False)
        latency = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            return (proxy, latency)
    except:
        pass
    return False

def verify_proxies(proxy_list: List[str], max_workers=100) -> List[str]:
    """
    Verify a list of proxies concurrently.
    Returns sorted list of working proxy strings (IP:Port), sorted by latency.
    """
    valid_proxies = []
    logger.info(f"Verifying {len(proxy_list)} proxies with {max_workers} threads...")
    
    # Suppress obscure SSL warnings from urllib3
    requests.packages.urllib3.disable_warnings()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(check_proxy, p): p for p in proxy_list}
        completed = 0
        total = len(proxy_list)
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            completed += 1
            if completed % 100 == 0:
                logger.info(f"Checked {completed}/{total}...")
                
            result = future.result()
            if result:
                valid_proxies.append({'proxy': result[0], 'latency': result[1]})
    
    # Sort by latency
    valid_proxies.sort(key=lambda x: x['latency'])
    
    # Extract just the proxy strings
    final_list = [p['proxy'] for p in valid_proxies]
    
    logger.info(f"Verification complete: {len(final_list)}/{total} proxies works")
    return final_list

if __name__ == "__main__":
    # Test run
    print("Fetching...")
    proxies = fetch_proxies()
    print(f"Fetched {len(proxies)} proxies. Verifying...")
    working = verify_proxies(proxies[:100]) # Test first 100
    print(f"Working: {len(working)}")
    if working:
        print("Top 5:", working[:5])
