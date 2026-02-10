# Auto-Skip Stuck Jobs Feature ✅

## What Was Added

The scraper now **automatically detects and skips stuck jobs** to prevent wasting time on problematic searches.

### 1. Job Timeout Protection

**30-minute maximum per job**
- If a job runs longer than 30 minutes, it automatically fails and moves to the next job
- Prevents jobs from running for hours like "Plumbers in New York" did

```
⏰ Job timeout: 35 minutes elapsed (max 30 minutes)
```

### 2. Stuck Detection

**10-minute progress check**
- If no businesses are saved for 10 minutes, the job is marked as stuck
- Automatically skips to next job instead of hanging forever

```
⚠️ Job appears stuck: No progress for 10 minutes
```

### 3. Browser Cleanup Between Jobs

**Each job gets a fresh start:**
1. ✅ Browser closes after each job (success or failure)
2. ✅ New proxy selected for next job
3. ✅ Fresh Chrome instance with clean state
4. ✅ Prevents memory leaks and crashes

```
🔒 Closing browser...
✓ Browser closed successfully
🔄 Ready for next job with fresh proxy
```

### 4. Progress Tracking

The scraper now tracks:
- **Job start time** - when the job began
- **Last progress time** - when the last business was saved
- **Elapsed time** - total time spent on current job

## How It Works

### Normal Job Flow
```
1. Job starts → Timer starts
2. Search Google Maps → Find businesses
3. Extract business #1 → Progress timer resets ✓
4. Extract business #2 → Progress timer resets ✓
5. Extract business #3 → Progress timer resets ✓
...
50. Job completes → Browser closes → New proxy → Next job
```

### Stuck Job Flow
```
1. Job starts → Timer starts
2. Search Google Maps → Find 0 businesses
3. Wait 10 minutes... (no progress)
4. ⚠️ STUCK DETECTED → Skip to next job
5. Browser closes → New proxy → Next job
```

### Timeout Job Flow
```
1. Job starts → Timer starts
2. Extract businesses slowly...
3. 30 minutes pass...
4. ⏰ TIMEOUT → Skip to next job
5. Browser closes → New proxy → Next job
```

## Settings

You can adjust these in `scraper_with_database.py`:

```python
MAX_JOB_TIME = 1800      # 30 minutes (1800 seconds)
STUCK_THRESHOLD = 600    # 10 minutes (600 seconds)
```

### Recommended Settings

**For fast cities (New York, London, Paris):**
- MAX_JOB_TIME = 1800 (30 minutes)
- STUCK_THRESHOLD = 600 (10 minutes)

**For slow/small cities:**
- MAX_JOB_TIME = 2400 (40 minutes)
- STUCK_THRESHOLD = 900 (15 minutes)

**For testing:**
- MAX_JOB_TIME = 300 (5 minutes)
- STUCK_THRESHOLD = 180 (3 minutes)

## Benefits

### Before (Old Behavior)
❌ Jobs could run for hours
❌ Stuck jobs blocked the queue
❌ Browser crashes from memory leaks
❌ Manual intervention required
❌ Wasted proxy bandwidth

### After (New Behavior)
✅ Jobs auto-skip after 30 minutes
✅ Stuck jobs detected in 10 minutes
✅ Fresh browser for each job
✅ Automatic recovery
✅ Efficient proxy usage

## Example Logs

### Successful Job
```
INFO: Starting job #5: Plumbers in Madrid, Spain
INFO: 🌐 Using proxy: 123.45.67.89:8080
INFO: Found 50 businesses, starting extraction...
INFO: [1/50] Saved: ABC Plumbing Services
INFO: [2/50] Saved: XYZ Plumbers
...
INFO: ✓ Job #5 completed: 50 businesses saved (45 with websites)
INFO: 🔒 Closing browser...
INFO: ✓ Browser closed successfully
INFO: 🔄 Ready for next job with fresh proxy
```

### Stuck Job (Auto-Skipped)
```
INFO: Starting job #4: Plumbers in New York, USA
INFO: 🌐 Using proxy: 123.45.67.89:8080
INFO: Found 0 businesses, starting extraction...
WARNING: ⚠️ Job appears stuck: No progress for 10 minutes
ERROR: Job #4 failed: Job stuck: No progress for 10 minutes
INFO: 🔒 Closing browser...
INFO: ✓ Browser closed successfully
INFO: 🔄 Ready for next job with fresh proxy
```

### Timeout Job (Auto-Skipped)
```
INFO: Starting job #6: Dentists in Tokyo, Japan
INFO: 🌐 Using proxy: 123.45.67.89:8080
INFO: Found 200 businesses, starting extraction...
INFO: [1/200] Saved: Tokyo Dental Clinic
...
WARNING: ⏰ Job timeout: 31 minutes elapsed (max 30 minutes)
ERROR: Job #6 failed: Job timeout after 31 minutes
INFO: 🔒 Closing browser...
INFO: ✓ Browser closed successfully
INFO: 🔄 Ready for next job with fresh proxy
```

## What Happens to Failed Jobs?

Failed jobs are marked as **"failed"** in the database with the error message:
- "Job stuck: No progress for 10 minutes"
- "Job timeout after 30 minutes"

You can:
1. **Delete them** from the dashboard (they're probably bad searches)
2. **Reset them** to pending and try again later
3. **Ignore them** and focus on successful jobs

## Testing

To test the stuck detection with a short timeout:

1. Edit `scraper_with_database.py`:
```python
MAX_JOB_TIME = 300      # 5 minutes
STUCK_THRESHOLD = 180   # 3 minutes
```

2. Add a job that will fail (e.g., "Test in NonexistentCity")
3. Watch it auto-skip after 3 minutes

## Dashboard Integration

The dashboard will show:
- ✅ **Completed jobs** - finished successfully
- ❌ **Failed jobs** - stuck or timeout
- ⏳ **Pending jobs** - waiting to run
- 🔄 **Running jobs** - currently scraping

Failed jobs won't block the queue anymore!

---

**Status**: Active and protecting your scraping queue! 🛡️
