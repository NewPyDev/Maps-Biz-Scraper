"""
Main scraper orchestrator
"""
import csv
import time
import random
import logging
from datetime import datetime
from db import Database
from proxy_manager import ProxyManager
from scraper import GoogleMapsScraper
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    def __init__(self):
        self.db = Database(config.DATABASE_PATH)
        self.proxy_manager = ProxyManager(config.PROXIES_FILE)
        self.current_scraper = None
        self.requests_count = 0
    
    def load_jobs_from_csv(self):
        """Load jobs from CSV files"""
        jobs = []
        places = []
        
        # Load jobs
        with open(config.JOBS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    jobs.append(row[0].strip())
        
        # Load places
        with open(config.PLACES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 2:
                    places.append({'city': row[0].strip(), 'country': row[1].strip()})
        
        logger.info(f"Loaded {len(jobs)} jobs and {len(places)} places")
        
        # Add to database
        added = 0
        for job in jobs:
            for place in places:
                if self.db.add_job(job, place['city'], place['country']):
                    added += 1
        
        logger.info(f"Added {added} jobs to database")
        return added
    

    def process_job(self, job):
        """Process a single job"""
        job_id = job['id']
        category = job['category']
        city = job['city']
        country = job['country']
        
        logger.info(f"Starting job #{job_id}: {category} in {city}, {country}")
        
        self.db.update_job_status(job_id, 'running')
        
        businesses_found = 0
        job_start_time = time.time()
        last_progress_time = time.time()
        
        try:
            # Setup scraper with proxy
            proxy = self.proxy_manager.get_next_proxy()
            self.current_scraper = GoogleMapsScraper(proxy)
            
            if not self.current_scraper.driver:
                raise Exception("Failed to initialize scraper")
            
            # Search
            if not self.current_scraper.search(category, city):
                raise Exception("Search failed")
            
            # Check timeout
            if time.time() - last_progress_time > config.STUCK_THRESHOLD_SECONDS:
                raise Exception("Job stuck: No progress")
            
            # Scroll and get results
            results = self.current_scraper.scroll_results(config.MAX_RESULTS_PER_JOB)
            
            if not results:
                logger.warning(f"No results found for {category} in {city}")
                self.db.update_job_status(job_id, 'completed', 0)
                return
            
            last_progress_time = time.time()
            
            # Extract data
            for i, result in enumerate(results):
                # Check timeouts
                if time.time() - job_start_time > config.JOB_TIMEOUT_SECONDS:
                    raise Exception(f"Job timeout after {config.JOB_TIMEOUT_SECONDS//60} minutes")
                
                if time.time() - last_progress_time > config.STUCK_THRESHOLD_SECONDS:
                    raise Exception("Job stuck: No progress")
                
                # Rotate proxy if needed
                self.requests_count += 1
                if self.requests_count >= config.ROTATE_PROXY_AFTER_REQUESTS:
                    logger.info("Rotating proxy...")
                    self.current_scraper.close()
                    proxy = self.proxy_manager.get_next_proxy()
                    self.current_scraper = GoogleMapsScraper(proxy)
                    self.current_scraper.search(category, city)
                    self.requests_count = 0
                
                # Extract business data
                data = self.current_scraper.extract_business_data(result)
                
                if data and data.get('name'):
                    data['category'] = category
                    data['city'] = city
                    data['country'] = country
                    
                    if self.db.add_business(data):
                        businesses_found += 1
                        last_progress_time = time.time()
                        self.db.update_job_status(job_id, 'running', businesses_found)
                        logger.info(f"[{i+1}/{len(results)}] Saved: {data['name'][:40]}")
                
                time.sleep(random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX))
            
            self.db.update_job_status(job_id, 'completed', businesses_found)
            logger.info(f"Job #{job_id} completed: {businesses_found} businesses")
            
        except Exception as e:
            logger.error(f"Job #{job_id} failed: {e}")
            self.db.update_job_status(job_id, 'failed', error=str(e))
        
        finally:
            if self.current_scraper:
                self.current_scraper.close()
                self.current_scraper = None
    
    def run(self):
        """Run scraper"""
        logger.info("=" * 60)
        logger.info("Starting scraper")
        logger.info("=" * 60)
        
        while True:
            jobs = self.db.get_pending_jobs()
            
            if not jobs:
                logger.info("No pending jobs")
                break
            
            for job in jobs:
                self.process_job(job)
                
                # Delay between jobs
                delay = random.randint(300, 600)
                logger.info(f"Waiting {delay//60} minutes before next job...")
                time.sleep(delay)
        
        logger.info("=" * 60)
        logger.info("Scraping complete")
        logger.info("=" * 60)
        
        stats = self.db.get_statistics()
        logger.info(f"Total businesses: {stats['total_businesses']}")
        logger.info(f"With website: {stats['with_website']}")
        logger.info(f"Without website: {stats['without_website']}")
    
    def close(self):
        """Cleanup"""
        if self.current_scraper:
            self.current_scraper.close()
        self.db.close()


if __name__ == "__main__":
    scraper = ScraperOrchestrator()
    try:
        scraper.run()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    finally:
        scraper.close()
