"""
Add a new scraping job to the queue
"""
from database_manager import BusinessDatabase

db = BusinessDatabase()

print("\n" + "="*60)
print("  ADDING NEW JOB")
print("="*60)

# Add a job for a different city to avoid duplicates
job_id = db.add_scraping_job(
    category='plumbers',
    city='Madrid',
    country='Spain',
    max_results=20,
    priority=1
)

if job_id:
    print(f"\n✅ Job added successfully! (Job ID: {job_id})")
    print("\nJob Details:")
    print("  Category: plumbers")
    print("  City: Madrid, Spain")
    print("  Max Results: 20 businesses")
    print("  Priority: 1 (high)")
else:
    print("\n❌ Failed to add job (might already exist)")

# Show current queue
cursor = db.conn.cursor()
cursor.execute('SELECT status, COUNT(*) FROM scraping_jobs GROUP BY status')
results = cursor.fetchall()

print("\n" + "="*60)
print("  CURRENT QUEUE STATUS")
print("="*60)
for row in results:
    emoji = {'pending': '⏳', 'running': '🔄', 'completed': '✅', 'failed': '❌'}.get(row[0], '❓')
    print(f"  {emoji} {row[0].capitalize()}: {row[1]} job(s)")

cursor.execute('SELECT COUNT(*) FROM scraping_jobs WHERE status="pending"')
pending = cursor.fetchone()[0]

print("="*60)

if pending > 0:
    print(f"\n✅ You have {pending} pending job(s)!")
    print("\nStart scraping:")
    print("  1. Go to dashboard: http://localhost:5000/scraping")
    print("  2. Click '▶️ Start Scraper' button")
    print("\n  OR run directly:")
    print("     python start_scraper_directly.py")
else:
    print("\n⚠️ No pending jobs")

print("\n" + "="*60 + "\n")

db.close()
