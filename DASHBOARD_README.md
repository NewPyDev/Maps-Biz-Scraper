# Scraper Dashboard - Quick Start

## Installation

```bash
pip install -r requirements_new.txt
```

## Setup

### 1. Load Jobs from CSV

```bash
python load_jobs.py
```

This reads `jobs.csv` and `places.csv` and creates all job combinations in the database.

### 2. Start Dashboard

```bash
python app.py
```

Dashboard will be available at: **http://localhost:8000**

## Dashboard Features

### 1. Scraper Control (Main Page)

**Controls:**
- ▶️ **Start** - Start scraper in background
- ⏸️ **Pause** - Pause scraper (can resume)
- ▶️ **Resume** - Resume paused scraper
- ⏹️ **Stop** - Stop scraper completely
- ⏭️ **Skip Current** - Skip current job and move to next
- 🔧 **Force Unstuck** - Reset stuck jobs to pending

**Live Status:**
- Current job category and city
- Current proxy in use
- Last scraped business name
- Real-time statistics

**Auto-refresh:** Status updates every 3 seconds

### 2. Edit Files

Edit CSV and proxy files directly in the dashboard:

**Files:**
- `jobs.csv` - Job categories (one per line)
- `places.csv` - Cities in "City,Country" format
- `proxies.txt` - Proxies in "ip:port:username:password" format

**Features:**
- View file contents
- Edit inline
- Save changes
- Changes take effect immediately (proxies reload automatically)

### 3. Export Data

Export scraped data with filters:

**Filters:**
- Website filter: All / Only with website / Only without website
- Cities: Select specific cities
- Categories: Select specific categories

**Output:**
- CSV file with all filtered results
- Automatic download
- Files saved in `exports/` folder

## How It Works

### Background Execution

The scraper runs in a **background thread**, so:
- Dashboard remains responsive
- You can control scraper while it's running
- Status updates in real-time
- No blocking

### State Management

The `ScraperController` manages:
- Scraper state (running/paused/stopped)
- Current job information
- Statistics
- Control flags (stop/pause/skip)

### Thread Safety

- Uses threading locks to prevent race conditions
- Shared state between dashboard and scraper
- Safe concurrent access to database

## API Endpoints

### Control Endpoints

```
POST /api/start      - Start scraper
POST /api/pause      - Pause scraper
POST /api/resume     - Resume scraper
POST /api/stop       - Stop scraper
POST /api/skip       - Skip current job
POST /api/unstuck    - Force unstuck
```

### Data Endpoints

```
GET  /api/status           - Get scraper status
GET  /api/jobs             - Get jobs list
GET  /api/businesses       - Get businesses (with filters)
GET  /api/files/{filename} - Get file contents
POST /api/files/{filename} - Save file contents
POST /api/export           - Export data to CSV
```

## Configuration

Edit `config.py` to customize:

```python
# Scraping
MAX_RESULTS_PER_JOB = 50
HEADLESS_MODE = False
JOB_TIMEOUT_SECONDS = 1800
STUCK_THRESHOLD_SECONDS = 600

# Proxy
ROTATE_PROXY_AFTER_REQUESTS = 15
MAX_PROXY_FAILURES = 3

# Export
EXPORT_DIR = 'exports'
```

## Troubleshooting

### "Scraper won't start"
- Check if jobs exist: `python load_jobs.py`
- Check database: `business_leads.db` should exist
- Check logs: `scraper.log`

### "Scraper stuck"
- Click "🔧 Force Unstuck" button
- This resets running jobs to pending
- Closes any open browsers

### "Can't edit files"
- Make sure files exist: `jobs.csv`, `places.csv`, `proxies.txt`
- Check file permissions

### "Export fails"
- Make sure `exports/` directory exists (created automatically)
- Check if there's data in database

## Production Tips

1. **Run in headless mode** - Set `HEADLESS_MODE = True` in `config.py`
2. **Monitor logs** - Check `scraper.log` for errors
3. **Export regularly** - Export data every few days
4. **Use Force Unstuck** - If scraper hangs, use Force Unstuck button
5. **Pause for maintenance** - Use Pause button to safely stop temporarily

## Architecture

```
app.py                    - FastAPI dashboard
scraper_controller.py     - Scraper state management
scraper.py                - SeleniumBase scraping engine
db.py                     - Database operations
proxy_manager.py          - Proxy rotation
config.py                 - Configuration
templates/                - HTML templates
  ├── index.html         - Main dashboard
  ├── files.html         - File editor
  └── export.html        - Export page
```

## Security Note

This dashboard is designed for **local use only**:
- No authentication
- No HTTPS
- Runs on localhost
- Not for public deployment

## Support

Check logs in `scraper.log` for detailed error messages.
