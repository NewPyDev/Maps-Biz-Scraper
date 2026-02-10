"""
Business Data Database Manager
Professional SQLite database for commercial lead generation business
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)

class BusinessDatabase:
    """Manage business leads database for commercial use"""
    
    def __init__(self, db_path='business_leads.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        logging.info(f"Connected to database: {self.db_path}")
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        # Main businesses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                website TEXT,
                has_website BOOLEAN,
                maps_url TEXT UNIQUE,
                latitude REAL,
                longitude REAL,
                scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                proxy_used TEXT,
                data_quality_score INTEGER DEFAULT 0,
                is_verified BOOLEAN DEFAULT 0,
                notes TEXT,
                UNIQUE(name, city, category)
            )
        ''')
        
        # Scraping jobs queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                max_results INTEGER DEFAULT 300,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                businesses_found INTEGER DEFAULT 0,
                businesses_with_website INTEGER DEFAULT 0,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                UNIQUE(category, city, country)
            )
        ''')
        
        # Proxy management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                username TEXT,
                password TEXT,
                proxy_type TEXT DEFAULT 'http',
                country TEXT,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                cost_per_gb REAL,
                notes TEXT,
                UNIQUE(host, port)
            )
        ''')
        
        # Export history (for tracking what you've sold)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                export_name TEXT NOT NULL,
                category TEXT,
                city TEXT,
                country TEXT,
                filter_criteria TEXT,
                record_count INTEGER,
                export_format TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                customer_name TEXT,
                price REAL,
                notes TEXT
            )
        ''')
        
        # Categories master list
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                avg_price_per_lead REAL,
                priority INTEGER DEFAULT 5
            )
        ''')
        
        # Cities master list
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                population INTEGER,
                is_active BOOLEAN DEFAULT 1,
                priority INTEGER DEFAULT 5,
                UNIQUE(name, country)
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_category ON businesses(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_city ON businesses(city)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_website ON businesses(has_website)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_country ON businesses(country)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_status ON scraping_jobs(status)')
        
        self.conn.commit()
        logging.info("Database tables created successfully")
    
    def add_business(self, business_data):
        """Add a single business to database"""
        cursor = self.conn.cursor()
        
        # Calculate data quality score (0-100)
        quality_score = 0
        if business_data.get('name') and business_data['name'] != 'N/A':
            quality_score += 20
        if business_data.get('address') and business_data['address'] != 'N/A':
            quality_score += 20
        if business_data.get('phone') and business_data['phone'] != 'N/A':
            quality_score += 30
        if business_data.get('has_website') == 'Yes':
            quality_score += 30
        
        business_data['data_quality_score'] = quality_score
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO businesses 
                (name, category, city, country, address, phone, website, has_website, 
                 maps_url, proxy_used, data_quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                business_data.get('name'),
                business_data.get('category'),
                business_data.get('city'),
                business_data.get('country', 'Unknown'),
                business_data.get('address'),
                business_data.get('phone'),
                business_data.get('website'),
                1 if business_data.get('has_website') == 'Yes' else 0,
                business_data.get('maps_url'),
                business_data.get('proxy_used'),
                quality_score
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logging.warning(f"Duplicate business: {business_data.get('name')} in {business_data.get('city')}")
            return None
    
    def add_scraping_job(self, category, city, country, max_results=300, priority=5):
        """Add a scraping job to the queue"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO scraping_jobs (category, city, country, max_results, priority, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            ''', (category, city, country, max_results, priority))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logging.warning(f"Job already exists: {category} in {city}, {country}")
            return None
    
    def get_next_job(self):
        """Get the next pending job (highest priority first)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM scraping_jobs 
            WHERE status = 'pending' 
            ORDER BY priority DESC, id ASC 
            LIMIT 1
        ''')
        return cursor.fetchone()
    
    def update_job_status(self, job_id, status, businesses_found=None, error_message=None):
        """Update scraping job status"""
        cursor = self.conn.cursor()
        
        if status == 'running':
            cursor.execute('''
                UPDATE scraping_jobs 
                SET status = ?, started_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, job_id))
        elif status == 'completed':
            cursor.execute('''
                UPDATE scraping_jobs 
                SET status = ?, completed_at = CURRENT_TIMESTAMP, businesses_found = ?
                WHERE id = ?
            ''', (status, businesses_found, job_id))
        elif status == 'failed':
            cursor.execute('''
                UPDATE scraping_jobs 
                SET status = ?, error_message = ?, retry_count = retry_count + 1
                WHERE id = ?
            ''', (status, error_message, job_id))
        
        self.conn.commit()
    
    def export_to_csv(self, filters=None, output_file=None, customer_name=None, price=None):
        """
        Export businesses to CSV with filters
        
        filters = {
            'category': 'plumbers',
            'city': 'Madrid',
            'country': 'Spain',
            'has_website': True,
            'min_quality_score': 70
        }
        """
        query = "SELECT * FROM businesses WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('category'):
                query += " AND category = ?"
                params.append(filters['category'])
            if filters.get('city'):
                query += " AND city = ?"
                params.append(filters['city'])
            if filters.get('country'):
                query += " AND country = ?"
                params.append(filters['country'])
            if filters.get('has_website') is not None:
                query += " AND has_website = ?"
                params.append(1 if filters['has_website'] else 0)
            if filters.get('min_quality_score'):
                query += " AND data_quality_score >= ?"
                params.append(filters['min_quality_score'])
        
        df = pd.read_sql_query(query, self.conn, params=params)
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"export_{timestamp}.csv"
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # Log the export
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO exports 
            (export_name, category, city, country, filter_criteria, record_count, 
             export_format, file_path, customer_name, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            output_file,
            filters.get('category') if filters else None,
            filters.get('city') if filters else None,
            filters.get('country') if filters else None,
            str(filters),
            len(df),
            'CSV',
            output_file,
            customer_name,
            price
        ))
        self.conn.commit()
        
        logging.info(f"Exported {len(df)} records to {output_file}")
        return output_file, len(df)
    
    def get_statistics(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total businesses
        cursor.execute("SELECT COUNT(*) FROM businesses")
        stats['total_businesses'] = cursor.fetchone()[0]
        
        # Businesses with websites
        cursor.execute("SELECT COUNT(*) FROM businesses WHERE has_website = 1")
        stats['with_website'] = cursor.fetchone()[0]
        
        # By category
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM businesses 
            GROUP BY category 
            ORDER BY count DESC
        ''')
        stats['by_category'] = dict(cursor.fetchall())
        
        # By city
        cursor.execute('''
            SELECT city, COUNT(*) as count 
            FROM businesses 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        stats['top_cities'] = dict(cursor.fetchall())
        
        # Job statistics
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM scraping_jobs 
            GROUP BY status
        ''')
        stats['jobs'] = dict(cursor.fetchall())
        
        # Average quality score
        cursor.execute("SELECT AVG(data_quality_score) FROM businesses")
        stats['avg_quality_score'] = round(cursor.fetchone()[0] or 0, 2)
        
        return stats
    
    def bulk_add_jobs(self, categories, cities_countries):
        """
        Bulk add scraping jobs
        
        categories = ['plumbers', 'electricians', 'dentists']
        cities_countries = [
            ('Madrid', 'Spain'),
            ('Barcelona', 'Spain'),
            ('Paris', 'France')
        ]
        """
        added = 0
        for category in categories:
            for city, country in cities_countries:
                job_id = self.add_scraping_job(category, city, country)
                if job_id:
                    added += 1
        
        logging.info(f"Added {added} scraping jobs to queue")
        return added
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = BusinessDatabase('business_leads.db')
    
    # Add some categories
    categories = [
        'Plumbers', 'Electricians', 'Carpenters', 'HVAC/Air conditioning',
        'Roofing contractors', 'Painters', 'Locksmith', 'Pest control',
        'Cleaning services', 'Landscaping', 'Dentists', 'Doctors/Medical clinics',
        'Lawyers', 'Accountants', 'Real estate agents', 'Restaurants/Cafes',
        'Hair salons/Barber shops', 'Fitness gyms', 'Hotels/Accommodations', 'Pharmacies'
    ]
    
    # Add some cities (example)
    cities_countries = [
        ('Madrid', 'Spain'),
        ('Barcelona', 'Spain'),
        ('Paris', 'France'),
        ('London', 'UK'),
        ('Berlin', 'Germany'),
        ('Rome', 'Italy'),
        ('Prague', 'Czech Republic'),
        ('Amsterdam', 'Netherlands'),
        ('Vienna', 'Austria'),
        ('Brussels', 'Belgium')
    ]
    
    # Bulk add jobs
    db.bulk_add_jobs(categories, cities_countries)
    
    # Show statistics
    stats = db.get_statistics()
    print("\n=== DATABASE STATISTICS ===")
    print(f"Total businesses: {stats['total_businesses']}")
    print(f"With websites: {stats['with_website']}")
    print(f"Average quality score: {stats['avg_quality_score']}")
    print(f"\nJobs: {stats['jobs']}")
    
    db.close()
