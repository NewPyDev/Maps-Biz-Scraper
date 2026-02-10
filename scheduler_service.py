import asyncio
import logging
from proxy_scraper import fetch_proxies, verify_proxies
from proxy_manager import get_proxy_manager
from pathlib import Path

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.running = False
        self.task = None

    def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._run_loop())
            logger.info("✅ Scheduler started: Will verify proxies every 8 hours")

    async def _run_loop(self):
        logger.info("🕒 Scheduler: First background check will run in 8 hours (use 'Fetch' button for immediate run)")
        while self.running:
            try:
                # Wait 8 hours
                await asyncio.sleep(8 * 3600)

                logger.info("🕒 Scheduler: Starting scheduled proxy update...")
                
                # Run content in thread to avoid blocking event loop
                raw_proxies = await asyncio.to_thread(fetch_proxies)
                
                if raw_proxies:
                    logger.info(f"🕒 Scheduler: Fetched {len(raw_proxies)} proxies. Verifying...")
                    
                    working_proxies = await asyncio.to_thread(verify_proxies, raw_proxies)
                    
                    if working_proxies:
                        # Save
                        proxy_file = Path("proxies.txt")
                        with open(proxy_file, "w", encoding="utf-8") as f:
                            f.write("\n".join(working_proxies))
                        
                        # Reload
                        manager = get_proxy_manager()
                        count = manager.reload_proxies()
                        logger.info(f"🕒 Scheduler: Complete! Saved {count} verified proxies.")
                    else:
                        logger.warning("🕒 Scheduler: No working proxies found after verification.")
                else:
                    logger.warning("🕒 Scheduler: No proxies fetched.")

            except asyncio.CancelledError:
                logger.info("Scheduler task cancelled")
                break
            except Exception as e:
                logger.error(f"🕒 Scheduler Error: {e}")
                await asyncio.sleep(60) # Retry after 1 min on error

# Singleton instance
scheduler = SchedulerService()
