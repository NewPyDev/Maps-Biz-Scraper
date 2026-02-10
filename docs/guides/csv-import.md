# CSV Import Guide 📂

## Overview

You have two CSV files with massive data:
- **jobs.csv** - 130 job categories (Carpentry Workshop, Furniture Manufacturer, etc.)
- **places.csv** - 240 cities across UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, Oman, Europe, North Africa, South Africa

**Total combinations: 31,200 jobs!**

## How to Import

### Method 1: Command Line (Recommended)

Run the import script:
```bash
python import_csv_jobs.py
```

You'll get these options:

**Option 1: Import ALL** (31,200 jobs)
- Not recommended unless you have weeks to scrape
- Will take months to complete

**Option 2: First 10 jobs × all cities** (2,400 jobs)
- Good for production
- Example: First 10 categories across all 240 cities
- Still a lot of jobs!

**Option 3: First 5 jobs × first 20 cities** (100 jobs) ⭐ **RECOMMENDED FOR TESTING**
- Perfect for testing
- Example: 5 categories in 20 UAE/Saudi cities
- Can complete in a few days

**Option 4: Custom range**
- You choose how many jobs and cities
- Most flexible option

**Option 5: Cancel**
- Exit without importing

### Method 2: Dashboard

1. Go to **Settings** page
2. Scroll to **"📂 Import Jobs from CSV Files"**
3. Click **"📖 Show Import Instructions"**
4. Follow the command-line instructions

## Example Import Session

```
📋 IMPORTING JOBS FROM CSV FILES
============================================================

✓ Loaded 130 job categories from jobs.csv
✓ Loaded 240 cities from places.csv

📊 Total possible combinations: 31,200
   (130 jobs × 240 cities)

⚠️  WARNING: This will create a LOT of jobs!
   Recommended: Start with a subset first

Options:
  1. Import ALL jobs (not recommended - too many)
  2. Import first 10 jobs × all cities
  3. Import first 5 jobs × first 20 cities
  4. Import specific range (custom)
  5. Cancel

Your choice (1-5): 3

📦 Will create 100 jobs:
   - 5 job categories
   - 20 cities

Proceed? (yes/no): yes

⏳ Adding jobs to database...
   Progress: 100/100 (100 added, 0 skipped)

============================================================
✅ IMPORT COMPLETE
============================================================
✓ Added: 100 new jobs
⚠️  Skipped: 0 (duplicates or errors)
📊 Total: 100 processed

💡 Next steps:
   1. Go to dashboard: http://localhost:5000
   2. Check the Scraping page
   3. Start the scraper
============================================================
```

## What Gets Imported

### Jobs from jobs.csv (130 categories)
```
Carpentry Workshop
Furniture Manufacturer
Kitchen Cabinet Maker
Construction Company
General Contractor
Metal Fabrication Workshop
Real Estate Agency
Logistics Company
E-commerce Company
Marketing Agency
Software Company
... (130 total)
```

### Places from places.csv (240 cities)
```
Dubai, United Arab Emirates
Abu Dhabi, United Arab Emirates
Riyadh, Saudi Arabia
Jeddah, Saudi Arabia
Doha, Qatar
Kuwait City, Kuwait
Manama, Bahrain
Muscat, Oman
Paris, France
Berlin, Germany
London, United Kingdom
... (240 total)
```

## Recommendations

### For Testing (Start Here)
```bash
python import_csv_jobs.py
# Choose option 3: First 5 jobs × first 20 cities (100 jobs)
```

This creates:
- 5 job categories
- 20 cities (mostly UAE/Saudi)
- 100 total jobs
- Can complete in 2-3 days

### For Production (After Testing)
```bash
python import_csv_jobs.py
# Choose option 4: Custom range
# Enter: 50 jobs, 100 cities = 5,000 jobs
```

This creates:
- 50 job categories
- 100 cities
- 5,000 total jobs
- Can complete in 1-2 months

### For Full Scale (Advanced)
```bash
python import_csv_jobs.py
# Choose option 2: First 10 jobs × all cities (2,400 jobs)
```

This creates:
- 10 job categories
- 240 cities
- 2,400 total jobs
- Can complete in 3-4 weeks

## Time Estimates

**Per job:**
- Search: 30 seconds
- Extract 50 businesses: 5-10 minutes
- Total: ~10 minutes per job

**For different scales:**
- 100 jobs = ~17 hours (2-3 days)
- 500 jobs = ~83 hours (1-2 weeks)
- 2,400 jobs = ~400 hours (3-4 weeks)
- 31,200 jobs = ~5,200 hours (7-8 months!)

## Tips

1. **Start small** - Test with 100 jobs first
2. **Check quality** - Make sure data is good before scaling
3. **Monitor proxies** - Ensure proxies are working
4. **Use auto-skip** - Stuck jobs will auto-skip after 10 minutes
5. **Export regularly** - Export data every few days
6. **Scale gradually** - Add more jobs as you complete batches

## CSV File Format

### jobs.csv
```
Carpentry Workshop
Furniture Manufacturer
Kitchen Cabinet Maker
```
- One job per line
- No headers
- Plain text

### places.csv
```
Dubai,United Arab Emirates
Abu Dhabi,United Arab Emirates
Sharjah,United Arab Emirates
```
- Format: `City,Country`
- One place per line
- No headers

## Troubleshooting

**"File not found"**
- Make sure `jobs.csv` and `places.csv` are in the same folder as the script

**"Too many jobs"**
- Start with option 3 (100 jobs) for testing

**"Duplicates skipped"**
- Normal - the script skips jobs that already exist in database

**"Import taking too long"**
- Large imports (1000+ jobs) can take a few minutes
- Be patient, it's adding them to database

## Next Steps After Import

1. **Check dashboard** - Go to http://localhost:5000/scraping
2. **See pending jobs** - You'll see all imported jobs
3. **Start scraper** - Click "▶️ Start Scraper"
4. **Monitor progress** - Watch live updates
5. **Export data** - Export completed jobs regularly

---

**Ready to import? Run:** `python import_csv_jobs.py`
