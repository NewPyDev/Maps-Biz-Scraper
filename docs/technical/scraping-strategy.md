# Large-Scale Scraping Strategy Guide

## 🛡️ Anti-Ban Measures (CRITICAL!)

### 1. **Timing & Rate Limiting**
- ✅ **Random delays**: 3-8 seconds between businesses (already implemented)
- ✅ **Session breaks**: Take 5-10 minute breaks every 50-100 businesses
- ✅ **Daily limits**: Don't scrape more than 500-1000 businesses per day per proxy
- ✅ **Time distribution**: Spread scraping across different hours (avoid patterns)

### 2. **Proxy Rotation** (MOST IMPORTANT!)
- ✅ **Rotate proxies frequently**: Every 20-50 requests (not just on failure)
- ✅ **Use residential proxies**: They're less likely to be flagged than datacenter proxies
- ✅ **Geographic matching**: Use proxies from the same country/region you're scraping
- ✅ **Proxy pool size**: Minimum 10-20 proxies for large-scale scraping

### 3. **Browser Fingerprinting**
- ✅ **Rotate user agents**: Already implemented
- ✅ **Clear cookies/cache**: Between proxy switches
- ✅ **Randomize viewport sizes**: Make each session look different
- ✅ **Mimic human behavior**: Random mouse movements, scrolling patterns

### 4. **Smart Scheduling**
```
Example Schedule for 20 categories × 100 cities = 2,000 scraping jobs:

Day 1: 10 cities × 2 categories = 20 jobs (500 businesses)
Day 2: 10 cities × 2 categories = 20 jobs (500 businesses)
...
Week 1: 100 jobs completed
Month 1: 400 jobs completed
```

### 5. **Error Handling**
- ✅ **Detect blocks early**: Monitor for CAPTCHAs, 403 errors, empty results
- ✅ **Automatic backoff**: If blocked, wait 1-24 hours before retrying
- ✅ **Proxy blacklist**: Track and skip bad proxies
- ✅ **Resume capability**: Save progress to continue after interruptions

---

## 💾 Data Storage Strategy

### Option 1: **CSV Files (Current - Good for Small Scale)**
**Pros:**
- Simple, human-readable
- Easy to share/import to Excel
- No database setup needed

**Cons:**
- Hard to query across multiple files
- Duplicate management is manual
- Doesn't scale well (1000s of files)

**Best for:** < 50 cities, < 10 categories

---

### Option 2: **SQLite Database (RECOMMENDED for Your Scale)**
**Pros:**
- Single file, portable
- Fast queries across all data
- Built-in duplicate detection
- No server setup needed
- Can still export to CSV/Excel

**Cons:**
- Requires basic SQL knowledge
- Slightly more complex setup

**Best for:** 100-1000 cities, 20+ categories (YOUR USE CASE!)

**Structure:**
```sql
Table: businesses
- id (primary key)
- name
- category
- city
- country
- address
- phone
- website
- has_website (boolean)
- maps_url
- latitude
- longitude
- scraped_date
- proxy_used

Table: scraping_jobs
- id
- category
- city
- status (pending/running/completed/failed)
- started_at
- completed_at
- businesses_found
- error_message

Table: proxies
- id
- host
- port
- username
- password
- success_count
- fail_count
- last_used
- is_active
```

---

### Option 3: **PostgreSQL/MySQL (For Very Large Scale)**
**Pros:**
- Enterprise-grade
- Multi-user access
- Advanced querying
- Better for 10,000+ cities

**Cons:**
- Requires server setup
- More complex
- Overkill for your current needs

**Best for:** > 1000 cities, team collaboration, API integration

---

## 🎯 RECOMMENDED SOLUTION FOR YOU

### **SQLite Database + CSV Exports**

**Why?**
1. Store everything in ONE database file
2. Query by city, category, website status instantly
3. Export filtered results to CSV when needed
4. Automatic duplicate detection
5. Track scraping progress
6. Resume interrupted jobs

**Example Queries:**
```sql
-- Get all plumbers in Madrid with websites
SELECT * FROM businesses 
WHERE category='plumbers' AND city='Madrid' AND has_website=1;

-- Count businesses by category
SELECT category, COUNT(*) FROM businesses GROUP BY category;

-- Find cities not yet scraped for a category
SELECT city FROM cities 
WHERE city NOT IN (
  SELECT DISTINCT city FROM businesses WHERE category='plumbers'
);

-- Export to CSV (via Python)
df = pd.read_sql("SELECT * FROM businesses WHERE city='Madrid'", conn)
df.to_csv('Madrid_all_businesses.csv')
```

---

## 📊 Recommended Workflow

### Phase 1: Setup (Day 1)
1. Create SQLite database
2. Import city list (100-500 cities)
3. Import category list (20 categories)
4. Generate scraping job queue (city × category combinations)

### Phase 2: Scraping (Weeks 1-4)
1. Process 10-20 jobs per day
2. Rotate proxies every 20-50 requests
3. Take breaks between jobs (5-10 minutes)
4. Monitor for blocks/errors
5. Auto-save to database after each business

### Phase 3: Maintenance (Ongoing)
1. Re-scrape cities every 3-6 months (data gets stale)
2. Update proxy list monthly
3. Export filtered CSVs for clients/analysis

---

## 🚀 Quick Start Commands

### Install SQLite support:
```bash
pip install sqlite3  # Usually built-in with Python
```

### Create database:
```python
import sqlite3
conn = sqlite3.connect('business_data.db')
# Run schema creation script
```

### Export to CSV:
```python
import pandas as pd
df = pd.read_sql("SELECT * FROM businesses WHERE city='Madrid'", conn)
df.to_csv('Madrid_businesses.csv', index=False)
```

---

## ⚠️ CRITICAL WARNINGS

1. **Don't scrape too fast**: Google WILL ban your IPs
2. **Use quality proxies**: Cheap proxies = quick bans
3. **Respect robots.txt**: Stay ethical
4. **Monitor daily**: Check logs for blocks/errors
5. **Have backup proxies**: Always have 2-3x more proxies than you think you need

---

## 📈 Scaling Timeline

**Conservative Approach (Recommended):**
- Week 1: 50 jobs (test proxies, refine delays)
- Week 2: 100 jobs (increase if no blocks)
- Week 3: 150 jobs
- Week 4: 200 jobs
- Month 2+: 200-300 jobs/week

**Total Time for 2,000 jobs:** 3-4 months (safe, sustainable)

**Aggressive Approach (Higher Risk):**
- 500 jobs/week with 20+ proxies
- Total time: 1 month
- Risk: Higher chance of bans, need more proxies

---

## 💡 Pro Tips

1. **Start with smaller cities**: Less competition, less monitoring
2. **Scrape at night (target timezone)**: Lower traffic = less scrutiny
3. **Use residential proxies**: 10x more expensive but 10x safer
4. **Keep proxy:job ratio at 1:50**: 1 proxy for every 50 businesses
5. **Monitor proxy health**: Track success rates, rotate out bad ones
6. **Save raw HTML**: Store page source for re-parsing later (optional)

