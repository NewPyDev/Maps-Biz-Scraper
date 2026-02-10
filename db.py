"""
Database operations
"""
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path='business_leads.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Businesses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                city TEXT,
                country TEXT,
                address TEXT,
                phone TEXT,
                website TEXT,
                maps_url TEXT UNIQUE,
                rating REAL,
                reviews INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, address)
            )
        ''')
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                businesses_found INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                UNIQUE(category, city, country)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_city ON businesses(city)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_category ON businesses(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_website ON businesses(website)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_status ON jobs(status)')
        
        self.conn.commit()
        logger.info("Database tables created")
    
    
    def add_business(self, data):
        """Add business to database with retry logic"""
        import time
        retries = 5
        
        # Check which columns exist (read only, usually safe)
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(businesses)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Build dynamic insert based on available columns
        fields = ['name', 'category', 'city', 'country', 'address', 'phone', 'website', 'maps_url']
        values = [
            data.get('name'),
            data.get('category'),
            data.get('city'),
            data.get('country'),
            data.get('address'),
            data.get('phone'),
            data.get('website'),
            data.get('maps_url')
        ]
        
        # Add rating and reviews if columns exist
        if 'rating' in columns:
            fields.append('rating')
            values.append(data.get('rating'))
        if 'reviews' in columns:
            fields.append('reviews')
            values.append(data.get('reviews'))
        
        placeholders = ','.join(['?' for _ in fields])
        field_names = ','.join(fields)
        
        for attempt in range(retries):
            try:
                cursor = self.conn.cursor()
                cursor.execute(f'''
                    INSERT INTO businesses ({field_names})
                    VALUES ({placeholders})
                ''', values)
                
                self.conn.commit()
                return cursor.lastrowid
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    if attempt == retries - 1:
                        logger.error(f"DB locked after {retries} attempts")
                        return None
                    sleep_time = 0.2 * (2 ** attempt)
                    time.sleep(sleep_time)
                else:
                    logger.error(f"DB Error: {e}")
                    return None
            except sqlite3.IntegrityError:
                return None
            except Exception as e:
                logger.error(f"Error adding business: {e}")
                return None
    
    def add_job(self, category, city, country):
        """Add job to queue with retry logic"""
        import time
        retries = 5
        for attempt in range(retries):
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO jobs (category, city, country, status)
                    VALUES (?, ?, ?, 'pending')
                ''', (category, city, country))
                self.conn.commit()
                return cursor.lastrowid
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    if attempt == retries - 1:
                        raise
                    time.sleep(0.2 * (2 ** attempt))
                else:
                    raise
            except sqlite3.IntegrityError:
                return None
    
    def get_pending_jobs(self):
        """Get all pending jobs"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE status = "pending" ORDER BY id')
        return [dict(row) for row in cursor.fetchall()]
    
    def update_job_status(self, job_id, status, businesses_found=None, error=None):
        """Update job status with retry logic"""
        import time
        retries = 5
        for attempt in range(retries):
            try:
                cursor = self.conn.cursor()
                if status == 'running':
                    cursor.execute('''
                        UPDATE jobs 
                        SET status = ?, started_at = ?, businesses_found = COALESCE(?, businesses_found)
                        WHERE id = ?
                    ''', (status, datetime.now(), businesses_found, job_id))
                elif status == 'completed':
                    cursor.execute('''
                        UPDATE jobs 
                        SET status = ?, completed_at = ?, businesses_found = ?
                        WHERE id = ?
                    ''', (status, datetime.now(), businesses_found, job_id))
                elif status == 'failed':
                    cursor.execute('''
                        UPDATE jobs 
                        SET status = ?, completed_at = ?, error_message = ?
                        WHERE id = ?
                    ''', (status, datetime.now(), error, job_id))
                else:
                    cursor.execute('UPDATE jobs SET status = ? WHERE id = ?', (status, job_id))
                self.conn.commit()
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    if attempt == retries - 1:
                        logger.error(f"Failed to update job status: {e}")
                        return
                    time.sleep(0.2 * (2 ** attempt))
                else:
                    logger.error(f"DB Error: {e}")
                    return

    
    def get_statistics(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM businesses')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM businesses WHERE website IS NOT NULL AND website != ""')
        with_website = cursor.fetchone()[0]
        
        # Check if rating column exists
        cursor.execute("PRAGMA table_info(businesses)")
        columns = [row[1] for row in cursor.fetchall()]
        
        avg_rating = 0
        if 'rating' in columns:
            cursor.execute('SELECT AVG(rating) FROM businesses WHERE rating IS NOT NULL')
            avg_rating = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT status, COUNT(*) FROM jobs GROUP BY status')
        jobs = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'total_businesses': total,
            'with_website': with_website,
            'without_website': total - with_website,
            'avg_rating': round(avg_rating, 2),
            'jobs': jobs
        }
    
    def export_to_csv(self, output_file, filters=None):
        """Export businesses to CSV"""
        import csv
        
        cursor = self.conn.cursor()
        query = 'SELECT * FROM businesses WHERE 1=1'
        params = []
        
        if filters:
            if filters.get('city'):
                query += ' AND city = ?'
                params.append(filters['city'])
            if filters.get('category'):
                query += ' AND category = ?'
                params.append(filters['category'])
            if filters.get('has_website') is not None:
                if filters['has_website']:
                    query += ' AND website IS NOT NULL AND website != ""'
                else:
                    query += ' AND (website IS NULL OR website = "")'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            return 0
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))
        
        return len(rows)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
