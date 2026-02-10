"""
Load jobs from CSV files into database
"""
import csv
import logging
from db import Database
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_jobs():
    """Load jobs from CSV files"""
    db = Database(config.DATABASE_PATH)
    
    jobs = []
    places = []
    
    # Load jobs
    logger.info(f"Loading jobs from {config.JOBS_CSV}...")
    with open(config.JOBS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                jobs.append(row[0].strip())
    
    logger.info(f"Loaded {len(jobs)} job categories")
    
    # Load places
    logger.info(f"Loading places from {config.PLACES_CSV}...")
    with open(config.PLACES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 2:
                places.append({'city': row[0].strip(), 'country': row[1].strip()})
    
    logger.info(f"Loaded {len(places)} places")
    
    # Calculate total
    total = len(jobs) * len(places)
    logger.info(f"Total combinations: {total:,}")
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    print(f"This will create {total:,} jobs")
    print(f"  {len(jobs)} categories × {len(places)} places")
    print("=" * 60)
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        logger.info("Cancelled")
        return
    
    # Add jobs
    added = 0
    skipped = 0
    
    logger.info("Adding jobs to database...")
    for i, job in enumerate(jobs):
        for j, place in enumerate(places):
            if db.add_job(job, place['city'], place['country']):
                added += 1
            else:
                skipped += 1
            
            if (added + skipped) % 100 == 0:
                logger.info(f"Progress: {added + skipped}/{total} ({added} added, {skipped} skipped)")
    
    db.close()
    
    logger.info("=" * 60)
    logger.info("Load complete")
    logger.info(f"Added: {added:,}")
    logger.info(f"Skipped: {skipped:,} (duplicates)")
    logger.info("=" * 60)


if __name__ == "__main__":
    load_jobs()
