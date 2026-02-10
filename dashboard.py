"""
Lead Generation Business Dashboard
Simple web interface to manage everything in one place
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from database_manager import BusinessDatabase
import os
import threading
import time
from datetime import datetime
import logging

app = Flask(__name__)

# Don't create a global database connection - create per request
def get_db():
    """Get database connection for current thread"""
    return BusinessDatabase('business_leads.db')

# Global scraper state
scraper_running = False
scraper_thread = None
scraper_stats = {
    'status': 'idle',
    'current_job': None,
    'businesses_scraped': 0,
    'jobs_completed': 0,
    'started_at': None
}

logging.basicConfig(level=logging.INFO)


@app.route('/')
def dashboard():
    """Main dashboard"""
    db = get_db()
    try:
        stats = db.get_statistics()
        
        # Get recent jobs
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT * FROM scraping_jobs 
            ORDER BY id DESC 
            LIMIT 10
        ''')
        recent_jobs = [dict(row) for row in cursor.fetchall()]
        
        # Get recent exports
        cursor.execute('''
            SELECT * FROM exports 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        recent_exports = [dict(row) for row in cursor.fetchall()]
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_jobs=recent_jobs,
                             recent_exports=recent_exports,
                             scraper_stats=scraper_stats)
    finally:
        db.close()


@app.route('/api/stats')
def api_stats():
    """Get current statistics (for live updates)"""
    db = get_db()
    try:
        stats = db.get_statistics()
        
        # Get job counts by status
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT status, COUNT(*) 
            FROM scraping_jobs 
            GROUP BY status
        ''')
        job_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get currently running job details from database
        cursor.execute('''
            SELECT category, city, country, businesses_found, started_at
            FROM scraping_jobs 
            WHERE status = "running"
            ORDER BY started_at DESC
            LIMIT 1
        ''')
        running_job = cursor.fetchone()
        
        # Update scraper stats based on actual database state
        if running_job:
            scraper_stats['status'] = 'running'
            scraper_stats['current_job'] = f"{running_job[0]} in {running_job[1]}, {running_job[2]}"
            scraper_stats['businesses_scraped'] = running_job[3] or 0
            scraper_stats['started_at'] = running_job[4]
        else:
            # Check if scraper thread is actually running
            if not scraper_running:
                scraper_stats['status'] = 'idle'
                scraper_stats['current_job'] = None
                scraper_stats['businesses_scraped'] = 0
        
        # Count completed jobs
        cursor.execute('SELECT COUNT(*) FROM scraping_jobs WHERE status = "completed"')
        scraper_stats['jobs_completed'] = cursor.fetchone()[0]
        
        # Return combined stats
        stats['scraper'] = scraper_stats
        stats['jobs'] = job_counts
        
        return jsonify(stats)
    finally:
        db.close()


@app.route('/scraping')
def scraping_page():
    """Scraping management page"""
    db = get_db()
    try:
        cursor = db.conn.cursor()
        
        # Get all jobs grouped by status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM scraping_jobs 
            GROUP BY status
        ''')
        job_counts = dict(cursor.fetchall())
        
        # Get pending jobs
        cursor.execute('''
            SELECT * FROM scraping_jobs 
            WHERE status = 'pending' 
            ORDER BY priority DESC, id ASC 
            LIMIT 50
        ''')
        pending_jobs = [dict(row) for row in cursor.fetchall()]
        
        # Get running/completed jobs
        cursor.execute('''
            SELECT * FROM scraping_jobs 
            WHERE status IN ('running', 'completed', 'failed')
            ORDER BY id DESC 
            LIMIT 20
        ''')
        other_jobs = [dict(row) for row in cursor.fetchall()]
        
        return render_template('scraping.html',
                             job_counts=job_counts,
                             pending_jobs=pending_jobs,
                             other_jobs=other_jobs,
                             scraper_running=scraper_running,
                             scraper_stats=scraper_stats)
    finally:
        db.close()


@app.route('/api/scraping/start', methods=['POST'])
def start_scraping():
    """Start the scraper"""
    global scraper_running, scraper_thread, scraper_stats
    
    if scraper_running:
        return jsonify({'error': 'Scraper already running'}), 400
    
    # Check if there are pending jobs
    db = get_db()
    cursor = db.conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM scraping_jobs WHERE status="pending"')
    pending_count = cursor.fetchone()[0]
    db.close()
    
    if pending_count == 0:
        return jsonify({
            'error': 'No pending jobs in queue',
            'message': 'Please add jobs first from the Settings page'
        }), 400
    
    max_jobs = request.json.get('max_jobs', 5)
    daily_limit = request.json.get('daily_limit', 500)
    
    def run_scraper():
        global scraper_running, scraper_stats
        from scraper_with_database import DatabaseScraper
        
        scraper_stats['status'] = 'running'
        scraper_stats['started_at'] = datetime.now().isoformat()
        scraper_stats['businesses_scraped'] = 0
        scraper_stats['jobs_completed'] = 0
        
        try:
            scraper = DatabaseScraper()
            scraper.run_queue(max_jobs=max_jobs, daily_limit=daily_limit)
        except Exception as e:
            logging.error(f"Scraper error: {e}")
            import traceback
            traceback.print_exc()
            scraper_stats['status'] = 'error'
            scraper_stats['error'] = str(e)
        finally:
            scraper_running = False
            if scraper_stats['status'] != 'error':
                scraper_stats['status'] = 'idle'
    
    scraper_running = True
    scraper_thread = threading.Thread(target=run_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    return jsonify({'success': True, 'message': 'Scraper started'})


@app.route('/api/scraping/stop', methods=['POST'])
def stop_scraping():
    """Stop the scraper (graceful)"""
    global scraper_running
    scraper_running = False
    return jsonify({'success': True, 'message': 'Scraper will stop after current job'})


@app.route('/api/scraping/reset', methods=['POST'])
def reset_scraping():
    """Reset everything - stop scrapers and reset stuck jobs"""
    global scraper_running, scraper_thread, scraper_stats
    
    # Force stop scraper
    scraper_running = False
    scraper_thread = None
    
    # Reset scraper stats
    scraper_stats = {
        'status': 'idle',
        'current_job': None,
        'businesses_scraped': 0,
        'jobs_completed': 0,
        'started_at': None
    }
    
    # Reset stuck jobs in database
    db = get_db()
    try:
        cursor = db.conn.cursor()
        
        # Find running jobs
        cursor.execute('SELECT COUNT(*) FROM scraping_jobs WHERE status="running"')
        stuck_count = cursor.fetchone()[0]
        
        # Reset them to pending
        cursor.execute('UPDATE scraping_jobs SET status="pending" WHERE status="running"')
        db.conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'All scrapers stopped and jobs reset',
            'jobs_reset': stuck_count
        })
    finally:
        db.close()


@app.route('/export')
def export_page():
    """Export management page"""
    db = get_db()
    try:
        cursor = db.conn.cursor()
        
        # Get available categories
        cursor.execute('SELECT DISTINCT category FROM businesses ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        # Get available cities
        cursor.execute('SELECT DISTINCT city, country FROM businesses ORDER BY city')
        cities = [{'city': row[0], 'country': row[1]} for row in cursor.fetchall()]
        
        # Get recent exports
        cursor.execute('''
            SELECT * FROM exports 
            ORDER BY created_at DESC 
            LIMIT 20
        ''')
        exports = [dict(row) for row in cursor.fetchall()]
        
        return render_template('export.html',
                             categories=categories,
                             cities=cities,
                             exports=exports)
    finally:
        db.close()


@app.route('/api/export', methods=['POST'])
def create_export():
    """Create and download export"""
    db = get_db()
    try:
        data = request.json
        
        filters = {}
        if data.get('category'):
            filters['category'] = data['category']
        if data.get('city'):
            filters['city'] = data['city']
        if data.get('country'):
            filters['country'] = data['country']
        if data.get('has_website') is not None:
            filters['has_website'] = data['has_website']
        if data.get('min_quality_score'):
            filters['min_quality_score'] = int(data['min_quality_score'])
        
        filename = data.get('filename', f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        output_file, count = db.export_to_csv(
            filters=filters,
            output_file=filename,
            customer_name=data.get('customer_name'),
            price=data.get('price')
        )
        
        return jsonify({
            'success': True,
            'filename': output_file,
            'count': count,
            'download_url': f'/download/{output_file}'
        })
    finally:
        db.close()


@app.route('/download/<filename>')
def download_file(filename):
    """Download exported CSV"""
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return "File not found", 404


@app.route('/setup')
def setup_page():
    """Initial setup wizard"""
    return render_template('setup.html')


@app.route('/settings')
def settings_page():
    """Settings page"""
    db = get_db()
    try:
        cursor = db.conn.cursor()
        
        # Get proxy count
        cursor.execute('SELECT COUNT(*) FROM proxies WHERE is_active = 1')
        proxy_count = cursor.fetchone()[0]
        
        # Get categories
        cursor.execute('SELECT * FROM categories ORDER BY name')
        categories = [dict(row) for row in cursor.fetchall()]
        
        # Get cities
        cursor.execute('SELECT * FROM cities ORDER BY name LIMIT 100')
        cities = [dict(row) for row in cursor.fetchall()]
        
        return render_template('settings.html',
                             proxy_count=proxy_count,
                             categories=categories,
                             cities=cities)
    finally:
        db.close()


@app.route('/api/jobs/add', methods=['POST'])
def add_job():
    """Add a single job to the queue"""
    try:
        data = request.json
        
        # Validate input
        if not data.get('category'):
            return jsonify({'success': False, 'error': 'Category is required'}), 400
        if not data.get('city'):
            return jsonify({'success': False, 'error': 'City is required'}), 400
        if not data.get('country'):
            return jsonify({'success': False, 'error': 'Country is required'}), 400
        
        db = get_db()
        try:
            job_id = db.add_scraping_job(
                category=data['category'].strip(),
                city=data['city'].strip(),
                country=data['country'].strip(),
                max_results=data.get('max_results', 50),
                priority=data.get('priority', 5)
            )
            
            if job_id:
                return jsonify({'success': True, 'job_id': job_id})
            else:
                return jsonify({'success': False, 'error': 'Job already exists'}), 400
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs/bulk-add', methods=['POST'])
def bulk_add_jobs():
    """Add multiple jobs at once"""
    try:
        data = request.json
        category = data.get('category', '').strip()
        cities = data.get('cities', [])
        country = data.get('country', '').strip()
        max_results = data.get('max_results', 50)
        
        # Validate input
        if not category:
            return jsonify({'success': False, 'error': 'Category is required'}), 400
        
        if not cities or len(cities) == 0:
            return jsonify({'success': False, 'error': 'At least one city is required'}), 400
        
        db = get_db()
        try:
            added = 0
            errors = []
            
            for city in cities:
                city = city.strip()
                if not city:
                    continue
                    
                try:
                    job_id = db.add_scraping_job(
                        category=category,
                        city=city,
                        country=country if country else 'Unknown',
                        max_results=max_results,
                        priority=5
                    )
                    if job_id:
                        added += 1
                    else:
                        errors.append(f"{city} (already exists)")
                except Exception as e:
                    errors.append(f"{city} (error: {str(e)})")
            
            result = {
                'success': True,
                'added': added,
                'total': len(cities),
                'errors': errors if errors else None
            }
            
            return jsonify(result)
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs/delete', methods=['POST'])
def delete_job():
    """Delete a single job"""
    try:
        data = request.json
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'success': False, 'error': 'Job ID required'}), 400
        
        db = get_db()
        try:
            cursor = db.conn.cursor()
            cursor.execute('DELETE FROM scraping_jobs WHERE id = ? AND status = "pending"', (job_id,))
            db.conn.commit()
            
            return jsonify({'success': True, 'deleted': cursor.rowcount})
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs/delete-multiple', methods=['POST'])
def delete_multiple_jobs():
    """Delete multiple jobs"""
    try:
        data = request.json
        job_ids = data.get('job_ids', [])
        
        if not job_ids:
            return jsonify({'success': False, 'error': 'No job IDs provided'}), 400
        
        db = get_db()
        try:
            cursor = db.conn.cursor()
            placeholders = ','.join('?' * len(job_ids))
            cursor.execute(f'DELETE FROM scraping_jobs WHERE id IN ({placeholders}) AND status = "pending"', job_ids)
            db.conn.commit()
            
            return jsonify({'success': True, 'deleted': cursor.rowcount})
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 LEAD GENERATION DASHBOARD")
    print("=" * 60)
    print("\n📊 Dashboard starting at: http://localhost:5000")
    print("\n✨ Features:")
    print("   - View statistics")
    print("   - Manage scraping jobs")
    print("   - Start/stop scraper")
    print("   - Export data")
    print("   - Track sales")
    print("\n" + "=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
