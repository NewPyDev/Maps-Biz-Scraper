"""
Google Maps Scraper with Database Integration
For commercial lead generation business
"""

import time
import random
import logging
from google_maps_scraper import (
    setup_driver, search_google_maps, scroll_and_load_results,
    extract_business_data, load_proxies_from_file
)
from database_manager import BusinessDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Reduce selenium-wire logging noise
logging.getLogger('seleniumwire').setLevel(logging.WARNING)
logging.getLogger('seleniumwire.handler').setLevel(logging.WARNING)
logging.getLogger('seleniumwire.proxy').setLevel(logging.WARNING)

# Global scraper stats for dashboard live updates
scraper_stats = {
    'status': 'idle',
    'current_job': None,
    'businesses_scraped': 0,
    'jobs_completed': 0,
    'started_at': None
}


class DatabaseScraper:
    """Scraper that saves directly to database"""
    
    def __init__(self, db_path='business_leads.db', proxy_file='proxies.txt'):
        self.db = BusinessDatabase(db_path)
        self.proxies = load_proxies_from_file(proxy_file)
        self.proxy_index = 0
        self.proxy_fail_count = {}
        self.proxies_used = set()  # Track unique proxies used
        self.current_proxy = None
        self.driver = None
        self.requests_with_proxy = 0
    
    def get_next_proxy(self):
        """Get next working proxy"""
        if not self.proxies:
            return None
        
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.proxy_index % len(self.proxies)]
            proxy_str = f"{proxy['host']}:{proxy['port']}"
            
            # Skip if proxy failed too many times
            if self.proxy_fail_count.get(proxy_str, 0) >= 3:
                logging.warning(f"Skipping proxy {proxy_str} (failed 3 times)")
                self.proxy_index += 1
                attempts += 1
                continue
            
            self.proxy_index += 1
            return proxy
        
        return None
    
    def setup_new_driver(self):
        """Setup driver with new proxy"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.current_proxy = self.get_next_proxy()
        
        try:
            self.driver = setup_driver(proxy_dict=self.current_proxy)
            self.requests_with_proxy = 0
            
            # Track proxy usage
            if self.current_proxy:
                proxy_str = f"{self.current_proxy['host']}:{self.current_proxy['port']}"
                self.proxies_used.add(proxy_str)
            
            return True
        except Exception as e:
            if self.current_proxy:
                proxy_str = f"{self.current_proxy['host']}:{self.current_proxy['port']}"
                self.proxy_fail_count[proxy_str] = self.proxy_fail_count.get(proxy_str, 0) + 1
            logging.error(f"Failed to setup driver: {e}")
            return False
    
    def scrape_job(self, job):
        """Scrape a single job from the queue"""
        global scraper_stats
        
        job_id = job['id']
        category = job['category']
        city = job['city']
        country = job['country']
        max_results = job['max_results']
        
        logging.info(f"Starting job #{job_id}: {category} in {city}, {country}")
        
        # Update scraper stats
        scraper_stats['current_job'] = f"{category} in {city}, {country}"
        scraper_stats['status'] = 'running'
        
        # Update job status to running
        self.db.update_job_status(job_id, 'running')
        
        businesses_scraped = 0
        businesses_with_website = 0
        job_start_time = time.time()
        last_progress_time = time.time()
        
        # Timeout settings
        MAX_JOB_TIME = 1800  # 30 minutes max per job
        STUCK_THRESHOLD = 600  # 10 minutes without progress = stuck
        
        try:
            # Setup driver with proxy
            if not self.setup_new_driver():
                raise Exception("Failed to setup driver")
            
            logging.info(f"🌐 Using proxy: {self.current_proxy['host']}:{self.current_proxy['port']}" if self.current_proxy else "🌐 No proxy (direct connection)")
            
            # Search Google Maps
            if not search_google_maps(self.driver, category, city):
                raise Exception("Failed to search Google Maps")
            
            # Check if stuck (no results after search)
            if time.time() - last_progress_time > STUCK_THRESHOLD:
                raise Exception(f"Job stuck: No progress for {STUCK_THRESHOLD//60} minutes")
            
            # Scroll and load results
            businesses = scroll_and_load_results(self.driver, max_results)
            
            if not businesses:
                logging.warning(f"No businesses found for {category} in {city}")
                self.db.update_job_status(job_id, 'completed', 0)
                return
            
            logging.info(f"Found {len(businesses)} businesses, starting extraction...")
            last_progress_time = time.time()  # Reset progress timer
            
            # Extract data from each business
            for i, business in enumerate(businesses):
                try:
                    # Check for timeout
                    elapsed_time = time.time() - job_start_time
                    if elapsed_time > MAX_JOB_TIME:
                        logging.warning(f"⏰ Job timeout: {elapsed_time//60} minutes elapsed (max {MAX_JOB_TIME//60} minutes)")
                        raise Exception(f"Job timeout after {elapsed_time//60} minutes")
                    
                    # Check if stuck (no progress)
                    if time.time() - last_progress_time > STUCK_THRESHOLD:
                        logging.warning(f"⚠️ Job appears stuck: No progress for {STUCK_THRESHOLD//60} minutes")
                        raise Exception(f"Job stuck: No progress for {STUCK_THRESHOLD//60} minutes")
                    
                    # Rotate proxy if needed (more frequent rotation for ban prevention)
                    if self.requests_with_proxy >= random.randint(8, 15):
                        proxy_str = f"{self.current_proxy['host']}:{self.current_proxy['port']}" if self.current_proxy else 'None'
                        logging.info(f"🔄 Rotating proxy after {self.requests_with_proxy} requests (was using {proxy_str})...")
                        if not self.setup_new_driver():
                            logging.warning("Failed to rotate proxy, continuing with current")
                        else:
                            new_proxy_str = f"{self.current_proxy['host']}:{self.current_proxy['port']}" if self.current_proxy else 'None'
                            logging.info(f"✓ Switched to new proxy: {new_proxy_str}")
                            # Re-search after proxy rotation
                            if not search_google_maps(self.driver, category, city):
                                raise Exception("Failed to re-search after proxy rotation")
                            businesses = scroll_and_load_results(self.driver, max_results)
                            business = businesses[i] if i < len(businesses) else None
                            if not business:
                                continue
                    
                    # Extract business data
                    data = extract_business_data(self.driver, business, self.current_proxy)
                    
                    if data:
                        # Add country to data
                        data['category'] = category
                        data['city'] = city
                        data['country'] = country
                        
                        # Save to database
                        business_id = self.db.add_business(data)
                        
                        if business_id:
                            businesses_scraped += 1
                            if data.get('has_website') == 'Yes':
                                businesses_with_website += 1
                            
                            # Update scraper stats
                            scraper_stats['businesses_scraped'] = businesses_scraped
                            
                            # Update job progress in database for live dashboard updates
                            self.db.update_job_status(job_id, 'running', businesses_scraped)
                            
                            # Reset progress timer (we made progress!)
                            last_progress_time = time.time()
                            
                            logging.info(f"[{i+1}/{len(businesses)}] Saved: {data['name'][:40]}")
                    
                    self.requests_with_proxy += 1
                    
                    # Random delay between businesses
                    time.sleep(random.uniform(3, 7))
                    
                    # Take a break every 50 businesses
                    if (i + 1) % 50 == 0:
                        break_time = random.randint(300, 600)  # 5-10 minutes
                        logging.info(f"Taking a {break_time//60} minute break after 50 businesses...")
                        time.sleep(break_time)
                
                except Exception as e:
                    logging.error(f"Error processing business {i+1}: {e}")
                    continue
            
            # Update job as completed
            self.db.update_job_status(job_id, 'completed', businesses_scraped)
            scraper_stats['jobs_completed'] = scraper_stats.get('jobs_completed', 0) + 1
            
            # Log proxy usage statistics
            logging.info(f"✓ Job #{job_id} completed: {businesses_scraped} businesses saved ({businesses_with_website} with websites)")
            logging.info(f"📊 Proxies used in this job: {len(self.proxies_used)} different IPs")
            if self.proxies_used:
                logging.info(f"   Proxy IPs: {', '.join(list(self.proxies_used)[:5])}{'...' if len(self.proxies_used) > 5 else ''}")
        
        except Exception as e:
            logging.error(f"Job #{job_id} failed: {e}")
            self.db.update_job_status(job_id, 'failed', error_message=str(e))
        
        finally:
            # ALWAYS close browser and cleanup after each job
            if self.driver:
                try:
                    logging.info("🔒 Closing browser...")
                    self.driver.quit()
                    logging.info("✓ Browser closed successfully")
                except Exception as e:
                    logging.warning(f"Error closing browser: {e}")
                self.driver = None
            
            # Reset proxy tracking for next job
            self.proxies_used.clear()
            self.requests_with_proxy = 0
            logging.info("🔄 Ready for next job with fresh proxy")
    
    def run_queue(self, max_jobs=None, daily_limit=500):
        """
        Process scraping queue
        
        max_jobs: Maximum number of jobs to process (None = all)
        daily_limit: Maximum businesses to scrape per day
        """
        jobs_processed = 0
        total_businesses = 0
        
        logging.info("=" * 60)
        logging.info("🚀 Starting scraping queue processor")
        logging.info("=" * 60)
        
        while True:
            # Check daily limit
            if total_businesses >= daily_limit:
                logging.info(f"Daily limit reached ({daily_limit} businesses). Stopping.")
                break
            
            # Check max jobs
            if max_jobs and jobs_processed >= max_jobs:
                logging.info(f"Max jobs limit reached ({max_jobs} jobs). Stopping.")
                break
            
            # Get next job
            job = self.db.get_next_job()
            
            if not job:
                logging.info("No more pending jobs in queue")
                break
            
            # Scrape the job
            self.scrape_job(job)
            jobs_processed += 1
            
            # Update total businesses count
            stats = self.db.get_statistics()
            total_businesses = stats['total_businesses']
            
            # Random delay between jobs (5-10 minutes)
            if jobs_processed < (max_jobs or float('inf')):
                delay = random.randint(300, 600)
                logging.info(f"Waiting {delay//60} minutes before next job...")
                time.sleep(delay)
        
        # Final statistics
        logging.info("=" * 60)
        logging.info("🎉 QUEUE PROCESSING COMPLETE")
        logging.info("=" * 60)
        stats = self.db.get_statistics()
        logging.info(f"Jobs processed: {jobs_processed}")
        logging.info(f"Total businesses in database: {stats['total_businesses']}")
        logging.info(f"Businesses with websites: {stats['with_website']}")
        logging.info(f"Average quality score: {stats['avg_quality_score']}")
        logging.info("=" * 60)
    
    def close(self):
        """Cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.db.close()


if __name__ == "__main__":
    # Example: Process 5 jobs from the queue
    scraper = DatabaseScraper()
    
    try:
        scraper.run_queue(
            max_jobs=5,          # Process 5 jobs
            daily_limit=500      # Stop after 500 businesses
        )
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    finally:
        scraper.close()
