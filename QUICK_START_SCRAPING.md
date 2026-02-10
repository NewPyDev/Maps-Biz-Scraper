# Quick Start: How to Start Scraping

## Current Status: ⚪ Idle (No Jobs in Queue)

Your scraper is working fine, but it shows "Idle" because there are **no pending jobs** to process.

---

## Option 1: Add Jobs via Dashboard (Recommended)

### Step 1: Open Dashboard
```bash
python dashboard.py
```

### Step 2: Go to Setup Page
- Open browser: http://localhost:5000
- Click "Settings" or go to: http://localhost:5000/setup

### Step 3: Add Jobs
Fill in the form:
- **Category**: plumbers (or any category)
- **City**: Prague (or any city)
- **Country**: Czech Republic
- **Max Results**: 50
- **Priority**: 1 (higher = processed first)

Click "Add Job" - this adds it to the queue.

### Step 4: Start Scraper
- Go to "Scraping" page: http://localhost:5000/scraping
- Click "▶️ Start Scraper" button
- Enter:
  - Max jobs: 5 (how many jobs to process)
  - Daily limit: 500 (max businesses per day)

### Step 5: Watch Live Progress
The dashboard will update every 5 seconds showing:
- Current job being processed
- Businesses scraped
- Proxy rotations in terminal logs

---

## Option 2: Add Jobs via Command Line

### Quick Script to Add a Job
```bash
python -c "from database_manager import BusinessDatabase; db = BusinessDatabase(); db.add_job('plumbers', 'Prague', 'Czech Republic', 50, 1); print('Job added!'); db.close()"
```

### Then Run Scraper
```bash
python scraper_with_database.py
```

This will:
- Process up to 5 jobs from the queue
- Stop after 500 businesses
- Show detailed logs in terminal

---

## Option 3: Use Setup Wizard

### Run the Setup Wizard
```bash
python setup_business.py
```

This interactive wizard will:
1. Ask for categories (plumbers, electricians, etc.)
2. Ask for cities (Prague, Madrid, etc.)
3. Add all combinations to the job queue
4. Optionally start scraping immediately

---

## What You'll See When Scraping

### Terminal Logs
```
🚀 Starting scraping queue processor
Starting job #1: plumbers in Prague, Czech Republic
✓ Configuring authenticated proxy: nnqlhtxn:***@142.111.48.253:7030
Searching: plumbers in Prague
Loaded 20 businesses so far...
[1/20] Saved: Plumbers Prague
🔄 Rotating proxy after 12 requests (was using 142.111.48.253:7030)...
✓ Switched to new proxy: 23.95.150.145:6114
✓ Job #1 completed: 20 businesses saved (15 with websites)
📊 Proxies used in this job: 3 different IPs
   Proxy IPs: 142.111.48.253:7030, 23.95.150.145:6114, 45.12.34.56:8080
```

### Dashboard (Live Updates)
```
Status: 🟢 Running
Current Job: plumbers in Prague, Czech Republic
Businesses Scraped: 12
Jobs Completed: 0
```

---

## Verify Everything is Working

### 1. Test Proxies First (Optional)
```bash
python test_proxy_rotation.py
```

This confirms your proxies are working before you start scraping.

### 2. Check Database
```bash
python -c "from database_manager import BusinessDatabase; db = BusinessDatabase(); stats = db.get_statistics(); print(f'Total businesses: {stats[\"total_businesses\"]}'); db.close()"
```

### 3. Check Job Queue
```bash
python -c "from database_manager import BusinessDatabase; db = BusinessDatabase(); jobs = db.get_job_queue_status(); print(f'Pending: {jobs[\"pending\"]}, Completed: {jobs[\"completed\"]}'); db.close()"
```

---

## Common Issues

### "No pending jobs in queue"
**Solution:** Add jobs using one of the methods above.

### "Scraper shows Idle"
**Solution:** This is normal when there are no jobs. Add jobs first.

### "Start Scraper button doesn't work"
**Solution:** Make sure you have pending jobs in the queue first.

### "Proxies not rotating"
**Solution:** This is now fixed! Proxies rotate every 8-15 requests. Check terminal logs for "🔄 Rotating proxy" messages.

---

## Recommended Workflow

1. **Add multiple jobs** (10-20 jobs for different cities/categories)
2. **Test proxies** (optional): `python test_proxy_rotation.py`
3. **Start scraper** from dashboard or command line
4. **Monitor progress** via dashboard live updates
5. **Export data** when complete: http://localhost:5000/export

---

## Example: Quick Test Run

```bash
# 1. Add a test job
python -c "from database_manager import BusinessDatabase; db = BusinessDatabase(); db.add_job('plumbers', 'Prague', 'Czech Republic', 20, 1); print('✓ Job added'); db.close()"

# 2. Run scraper
python scraper_with_database.py

# 3. Check results
python -c "from database_manager import BusinessDatabase; db = BusinessDatabase(); stats = db.get_statistics(); print(f'✓ Scraped {stats[\"total_businesses\"]} businesses'); db.close()"
```

---

## Next Steps

Once you've tested with a small job:

1. **Add bulk jobs** using setup wizard
2. **Run overnight** for large-scale scraping
3. **Export data** in CSV/PDF format
4. **Sell the data** as per your business plan!

Your scraper is ready - it just needs jobs to process! 🚀
