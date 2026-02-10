import requests
import time
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
AUTH = ('admin', 'changeme123')

def test_integration():
    logger.info("🚀 Starting Integration Test")
    
    # 1. Check health
    try:
        r = requests.get(f"{BASE_URL}/api/status", auth=AUTH)
        if r.status_code != 200:
            logger.error(f"Server not healthy: {r.status_code}")
            return
        logger.info("✅ Server is UP")
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return

    # 2. Add Job
    logger.info("Adding test job: Florist in Dover, USA")
    job_data = {"category": "Florist", "city": "Dover", "country": "USA"}
    r = requests.post(f"{BASE_URL}/api/jobs/add", json=job_data, auth=AUTH)
    
    if r.status_code == 200:
        data = r.json()
        if data.get("success") or data.get("error") == "Job already exists":
             logger.info("✅ Job setup complete")
        else:
             logger.error(f"Failed to add job: {r.text}")
             return
    else:
        logger.error(f"Failed to add job: {r.text}")
        return

    # 3. Start Scraper
    logger.info("Starting scraper...")
    r = requests.post(f"{BASE_URL}/api/start", auth=AUTH)
    if r.status_code == 200 and r.json().get("success"):
        logger.info("✅ Scraper started")
    else:
        logger.error(f"Failed to start scraper: {r.text}")
        return

    # 4. Monitor for 30 seconds
    logger.info("Monitoring progress for 30s...")
    success = False
    for i in range(10):
        time.sleep(3)
        try:
            r = requests.get(f"{BASE_URL}/api/status", auth=AUTH)
            data = r.json()
            status = data.get("status")
            scraped = data.get("stats", {}).get("businesses_scraped", 0)
            current = data.get("stats", {}).get("current_business", "-")
            logger.info(f"[{status.upper()}] Scraped: {scraped} | Current: {str(current)[:50]}...")
            
            if scraped > 0:
                logger.info("✅ Scraper successfully found businesses!")
                success = True
                break
        except Exception as e:
            logger.error(f"Error checking status: {e}")

    # 5. Stop Scraper
    logger.info("Stopping scraper...")
    requests.post(f"{BASE_URL}/api/stop", auth=AUTH)
    
    if success:
        logger.info("✅ INTEGRATION TEST PASSED")
    else:
        logger.error("❌ INTEGRATION TEST FAILED (No businesses found in time)")

if __name__ == "__main__":
    test_integration()
