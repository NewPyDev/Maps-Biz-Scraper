"""
Scraper controller - manages scraper state and execution
Uses Playwright-based scraper for Google Maps scraping
"""
import threading
import time
import logging
from datetime import datetime
from db import Database
from proxy_manager import get_proxy_manager
from scraper_playwright import GoogleMapsScraper
from config import settings

logger = logging.getLogger(__name__)


class ScraperController:
    """Singleton controller for scraper"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.db = Database(str(settings.database_path))
        self.proxy_manager = get_proxy_manager()

        # State
        self.status = 'stopped'  # stopped, running, paused, error
        self.current_job = None
        self.thread = None

        # Statistics
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'current_job_index': 0,
            'businesses_scraped': 0,
            'current_business': None,
            'current_proxy': None,
            'error_message': None,
            'started_at': None
        }

        # Control flags
        self.should_stop = False
        self.should_pause = False
        self.should_skip = False
        
        # Config (dynamic)
        self.max_results = settings.max_results_per_job

    def set_config(self, max_results: int):
        """Update scraper configuration"""
        self.max_results = max_results
        logger.info(f"Updated max_results to {max_results}")

    def start(self):
        """Start scraper in background thread"""
        if self.status == 'running':
            return {'success': False, 'error': 'Already running'}

        # Check for pending jobs
        jobs = self.db.get_pending_jobs()
        if not jobs:
            return {'success': False, 'error': 'No pending jobs. Add jobs first.'}

        self.should_stop = False
        self.should_pause = False
        self.status = 'running'
        self.stats['started_at'] = datetime.now().isoformat()
        self.stats['error_message'] = None
        self.stats['businesses_scraped'] = 0

        self.thread = threading.Thread(target=self._run_scraper, daemon=True)
        self.thread.start()

        return {'success': True, 'message': f'Started with {len(jobs)} pending jobs'}

    def pause(self):
        """Pause scraper"""
        if self.status != 'running':
            return {'success': False, 'error': 'Not running'}

        self.should_pause = True
        self.status = 'paused'
        return {'success': True}

    def resume(self):
        """Resume scraper"""
        if self.status != 'paused':
            return {'success': False, 'error': 'Not paused'}

        self.should_pause = False
        self.status = 'running'
        return {'success': True}

    def stop(self):
        """Stop scraper"""
        self.should_stop = True
        self.status = 'stopped'
        return {'success': True}

    def skip_current(self):
        """Skip current job"""
        if self.status != 'running':
            return {'success': False, 'error': 'Not running'}

        self.should_skip = True
        return {'success': True}

    def force_unstuck(self):
        """Force unstuck scraper"""
        # Reset running jobs to pending
        cursor = self.db.conn.cursor()
        cursor.execute('UPDATE jobs SET status = "pending" WHERE status = "running"')
        self.db.conn.commit()
        reset_count = cursor.rowcount

        self.status = 'stopped'
        self.current_job = None
        self.should_stop = True

        return {'success': True, 'jobs_reset': reset_count}

    def get_status(self):
        """Get current status"""
        # Update job counts
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM jobs')
        self.stats['total_jobs'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "completed"')
        self.stats['completed_jobs'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "pending"')
        pending = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM businesses')
        total_businesses = cursor.fetchone()[0]

        return {
            'status': self.status,
            'current_job': self.current_job,
            'stats': {
                **self.stats,
                'total_businesses': total_businesses,
                'pending_jobs': pending
            }
        }

    def _run_scraper(self):
        """Main scraper loop (runs in background thread)"""
        # Create thread-local DB connection
        local_db = Database(str(settings.database_path))
        
        try:
            while not self.should_stop:
                # Check pause
                while self.should_pause and not self.should_stop:
                    time.sleep(1)

                if self.should_stop:
                    break

                # Get next job
                jobs = local_db.get_pending_jobs()
                if not jobs:
                    logger.info("No pending jobs — scraper finished")
                    break

                job = jobs[0]
                self._process_job(job, local_db)

                # Delay between jobs (anti-detection)
                if not self.should_stop:
                    import random
                    delay = random.randint(30, 90)
                    logger.info(f"Waiting {delay}s before next job...")
                    for _ in range(delay):
                        if self.should_stop:
                            break
                        time.sleep(1)

        except Exception as e:
            logger.error(f"Scraper error: {e}")
            self.status = 'error'
            self.stats['error_message'] = str(e)

        finally:
            self.status = 'stopped'
            logger.info("Scraper stopped")

    def _process_job(self, job, db):
        """Process single job using Playwright scraper"""
        job_id = job['id']
        category = job['category']
        city = job['city']
        country = job['country']

        self.current_job = {
            'id': job_id,
            'category': category,
            'city': city,
            'country': country
        }

        logger.info(f"Starting job #{job_id}: {category} in {city}, {country}")
        db.update_job_status(job_id, 'running')
        self.should_skip = False

        scraper = None
        try:
            # Create Playwright scraper
            scraper = GoogleMapsScraper()

            # Run scrape
            businesses = scraper.scrape(
                category=category,
                city=city,
                country=country,
                max_results=self.max_results
            )

            if not businesses:
                logger.warning(f"No results for {category} in {city}")
                db.update_job_status(job_id, 'completed', 0)
                return

            # Save businesses to DB
            saved_count = 0
            for biz in businesses:
                if self.should_stop or self.should_skip:
                    break

                biz_data = {
                    'name': biz.get('name'),
                    'category': category,
                    'city': city,
                    'country': country,
                    'address': biz.get('address'),
                    'phone': biz.get('phone'),
                    'website': biz.get('website') if biz.get('has_website') == 'Yes' else None,
                    'maps_url': None, # Scraper doesn't return this yet?
                    'reviews': biz.get('reviews')
                }
                
                # Use local db
                db.add_business(biz_data)
                saved_count += 1
                self.stats['businesses_scraped'] += 1
                self.stats['current_business'] = biz.get('name', '')

            # Also save to CSV
            scraper.save_to_csv(category, city)

            if self.should_skip:
                self.db.update_job_status(job_id, 'failed', error='Skipped by user')
                logger.info(f"Job #{job_id} skipped")
            else:
                self.db.update_job_status(job_id, 'completed', saved_count)
                logger.info(f"Job #{job_id} completed: {saved_count} businesses saved to DB")

        except Exception as e:
            logger.error(f"Job #{job_id} failed: {e}")
            self.db.update_job_status(job_id, 'failed', error=str(e))
            self.stats['error_message'] = str(e)

        finally:
            self.current_job = None
