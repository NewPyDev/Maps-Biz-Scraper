# Google Maps Business Scraper

Production-ready scraper for extracting business data from Google Maps using SeleniumBase.

## Features

- ✅ SeleniumBase (undetectable browser automation)
- ✅ Rotating proxies
- ✅ CSV input (jobs.csv + places.csv)
- ✅ SQLite database storage
- ✅ Duplicate prevention
- ✅ Auto-timeout for stuck jobs
- ✅ Export to 3 CSV files (all, with_website, no_website)
- ✅ Clean, modular architecture

## Installation

```bash
pip install -r requirements_new.txt
```

## Setup

### 1. Prepare CSV Files

**jobs.csv** - One job per line:
```
Plumbers
Electricians
Dentists
```

**places.csv** - City,Country format:
```
Dubai,United Arab Emirates
London,United Kingdom
Paris,France
```

### 2. Configure Proxies (Optional)

**proxies.txt** - Format: `ip:port:username:password`
```
123.45.67.89:8080:user:pass
98.76.54.32:8080:user:pass
```

### 3. Load Jobs

```bash
python load_jobs.py
```

This reads your CSV files and creates all job combinations in the database.

## Usage

### Run Scraper

```bash
python main.py
```

The scraper will:
1. Process all pending jobs from database
2. Rotate proxies automatically
3. Extract business data
4. Save to database
5. Auto-skip stuck jobs (30 min timeout)

### Export Data

```bash
python export.py
```

Creates 3 CSV files in `exports/` folder:
- `all_results.csv` - All businesses
- `with_website.csv` - Only businesses with websites
- `no_website.csv` - Only businesses without websites

## Configuration

Edit `config.py` to customize:

```python
MAX_RESULTS_PER_JOB = 50          # Results per search
HEADLESS_MODE = False              # Run browser in background
JOB_TIMEOUT_SECONDS = 1800         # 30 min max per job
STUCK_THRESHOLD_SECONDS = 600      # 10 min no progress = stuck
ROTATE_PROXY_AFTER_REQUESTS = 15   # Rotate proxy every 15 requests
```

## Database Schema

### businesses table
- id, name, category, city, country
- address, phone, website, maps_url
- rating, reviews, scraped_at

### jobs table
- id, category, city, country
- status (pending/running/completed/failed)
- businesses_found, started_at, completed_at, error_message

## Architecture

```
config.py           - Configuration settings
db.py               - Database operations
proxy_manager.py    - Proxy rotation logic
scraper.py          - SeleniumBase scraping engine
main.py             - Main orchestrator
load_jobs.py        - Load jobs from CSV
export.py           - Export to CSV
```

## Features

### Auto-Timeout Protection
- Jobs timeout after 30 minutes
- Stuck detection (10 min no progress)
- Automatic skip to next job

### Proxy Rotation
- Rotates every 15 requests
- Tracks failed proxies
- Skips proxies that failed 3+ times

### Duplicate Prevention
- Unique constraint on (name + address)
- Unique constraint on maps_url
- Unique constraint on (category + city + country) for jobs

### Data Quality
- Normalizes text
- Handles missing fields
- Consistent CSV format
- Logs errors without stopping

## Troubleshooting

**"No pending jobs"**
- Run `python load_jobs.py` first

**"Failed to setup driver"**
- Check proxy format in proxies.txt
- Try without proxies first

**"Job stuck"**
- Normal - auto-skips after 10 minutes
- Check logs in scraper.log

**"Duplicate entries"**
- Normal - database prevents duplicates

## Production Tips

1. Start with small batch (10 jobs × 10 cities = 100 jobs)
2. Test without proxies first
3. Monitor scraper.log for errors
4. Export data regularly
5. Use headless mode for production (HEADLESS_MODE = True)

## License

Commercial use allowed.
