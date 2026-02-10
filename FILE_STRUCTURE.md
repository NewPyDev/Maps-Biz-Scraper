# Complete File Structure & Purpose

## 🎯 CORE FILES (What You Actually Use)

### 1. **dashboard.py** ⭐ MAIN APP
- **Purpose**: Web dashboard (Flask app)
- **Run**: `python dashboard.py`
- **URL**: http://localhost:5000
- **What it does**: 
  - Shows statistics
  - Manages jobs (add/delete/view)
  - Starts/stops scraper
  - Exports data

### 2. **scraper_with_database.py** ⭐ SCRAPER ENGINE
- **Purpose**: Main scraping engine
- **Run**: Automatically by dashboard OR `python scraper_with_database.py`
- **What it does**:
  - Processes job queue
  - Scrapes Google Maps
  - Saves to database
  - Rotates proxies
  - Auto-skips stuck jobs (30 min timeout)

### 3. **database_manager.py** ⭐ DATABASE
- **Purpose**: Database operations
- **What it does**:
  - Creates tables
  - Adds/updates businesses
  - Manages job queue
  - Exports data
  - Tracks statistics

### 4. **google_maps_scraper.py** ⭐ SCRAPING LOGIC
- **Purpose**: Google Maps scraping functions
- **What it does**:
  - Opens Chrome with proxy
  - Searches Google Maps
  - Scrolls results
  - Extracts business data
  - Detects websites

---

## 📂 DATA FILES

### 5. **business_leads.db** ⭐ DATABASE
- **Purpose**: SQLite database with all data
- **Contains**:
  - Businesses table (scraped data)
  - Jobs table (queue)
  - Exports table (export history)

### 6. **jobs.csv** ⭐ YOUR DATA
- **Purpose**: 130 job categories to scrape
- **Format**: One job per line
- **Used by**: `import_csv_jobs.py`

### 7. **places.csv** ⭐ YOUR DATA
- **Purpose**: 240 cities worldwide
- **Format**: City,Country
- **Used by**: `import_csv_jobs.py`

### 8. **proxies.txt** ⭐ PROXY CONFIG
- **Purpose**: Proxy list
- **Format**: `ip:port:username:password` (one per line)
- **Used by**: Scraper for rotation

---

## 🛠️ UTILITY SCRIPTS

### 9. **import_csv_jobs.py** ⭐ CSV IMPORTER
- **Purpose**: Import jobs from CSV files
- **Run**: `python import_csv_jobs.py`
- **What it does**: Reads jobs.csv + places.csv, creates all combinations

### 10. **export_data.py**
- **Purpose**: Export data to CSV
- **Run**: `python export_data.py`
- **What it does**: Export businesses by filters (city, category, quality)

### 11. **check_progress.py**
- **Purpose**: Check scraping status
- **Run**: `python check_progress.py`
- **What it does**: Shows current job, businesses scraped, job counts

### 12. **check_queue.py**
- **Purpose**: Check job queue
- **Run**: `python check_queue.py`
- **What it does**: Shows pending/completed/failed job counts

### 13. **reset_stuck_jobs.py**
- **Purpose**: Reset stuck jobs
- **Run**: `python reset_stuck_jobs.py`
- **What it does**: Changes running jobs back to pending

### 14. **add_test_job.py**
- **Purpose**: Add a test job
- **Run**: `python add_test_job.py`
- **What it does**: Adds "plumbers in Prague" test job

### 15. **setup_business.py**
- **Purpose**: Initial setup wizard
- **Run**: `python setup_business.py`
- **What it does**: First-time setup (not needed anymore)

---

## 🌐 TEMPLATES (HTML Files)

### 16. **templates/dashboard.html**
- Main dashboard page
- Shows statistics, recent jobs, recent exports

### 17. **templates/scraping.html** ⭐ SCRAPING PAGE
- Manage scraping
- Start/stop scraper
- View pending jobs
- Delete jobs
- Reset stuck jobs

### 18. **templates/settings.html** ⭐ SETTINGS PAGE
- Add single job
- Bulk add jobs
- Import CSV instructions
- Proxy configuration

### 19. **templates/setup.html**
- Setup wizard (bulk add multiple categories × cities)

### 20. **templates/export.html**
- Export data page
- Filter by city, category, quality, website

---

## 📄 DOCUMENTATION FILES

### 21. **START_HERE.md**
- Quick start guide

### 22. **SYSTEM_OVERVIEW.md**
- Complete system documentation

### 23. **BUSINESS_PLAN.md**
- How to make money selling data

### 24. **CSV_IMPORT_GUIDE.md** ⭐ CSV IMPORT
- How to import jobs.csv and places.csv

### 25. **AUTO_SKIP_STUCK_JOBS.md**
- Explains auto-skip feature (30 min timeout)

### 26. **BULK_JOB_FIX.md**
- Bulk job addition fix documentation

### 27. **JOB_SELECTION_FEATURE.md**
- Job selection/deletion feature

### 28. **LIVE_UPDATES.md**
- Live dashboard updates feature

### 29. Other .md files
- Various feature documentation

---

## 🗑️ OLD/TEST FILES (Can Ignore)

- `add_new_job.py` - Old way to add jobs (use dashboard now)
- `start_scraper_directly.py` - Old way to start (use dashboard now)
- `test_*.py` - Test scripts
- `debug_*.py` - Debug scripts
- `*.pyshit` - Backup files
- `page_source*.html` - Debug HTML files
- All the exported CSV/PDF files - Your scraped data

---

## 🎯 WHAT YOU NEED TO KNOW

### To Run the App:
```bash
python dashboard.py
```
Then go to: http://localhost:5000

### To Import Your CSV Jobs:
```bash
python import_csv_jobs.py
```

### To Check Status:
```bash
python check_progress.py
python check_queue.py
```

### To Reset Stuck Jobs:
```bash
python reset_stuck_jobs.py
```
OR use dashboard "🔧 Reset All" button

---

## 🔥 MOST IMPORTANT FILES

1. **dashboard.py** - The app
2. **scraper_with_database.py** - The scraper
3. **database_manager.py** - The database
4. **google_maps_scraper.py** - The scraping logic
5. **import_csv_jobs.py** - Import your CSV data
6. **business_leads.db** - Your data
7. **proxies.txt** - Your proxies
8. **jobs.csv** - Your job categories
9. **places.csv** - Your cities

Everything else is either:
- Documentation
- Utilities
- Templates
- Old files
- Test files

---

**Bottom line**: Run `python dashboard.py` and use the web interface. That's it.
