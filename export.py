"""
Export data to CSV files
"""
import os
import logging
from db import Database
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_all():
    """Export all data to CSV files"""
    db = Database(config.DATABASE_PATH)
    
    # Create export directory
    os.makedirs(config.EXPORT_DIR, exist_ok=True)
    
    # Export all results
    all_file = os.path.join(config.EXPORT_DIR, 'all_results.csv')
    count_all = db.export_to_csv(all_file)
    logger.info(f"Exported {count_all} records to {all_file}")
    
    # Export with website
    with_website_file = os.path.join(config.EXPORT_DIR, 'with_website.csv')
    count_with = db.export_to_csv(with_website_file, {'has_website': True})
    logger.info(f"Exported {count_with} records to {with_website_file}")
    
    # Export without website
    no_website_file = os.path.join(config.EXPORT_DIR, 'no_website.csv')
    count_without = db.export_to_csv(no_website_file, {'has_website': False})
    logger.info(f"Exported {count_without} records to {no_website_file}")
    
    db.close()
    
    logger.info("=" * 60)
    logger.info("Export complete")
    logger.info(f"Total: {count_all}")
    logger.info(f"With website: {count_with}")
    logger.info(f"Without website: {count_without}")
    logger.info("=" * 60)


if __name__ == "__main__":
    export_all()
