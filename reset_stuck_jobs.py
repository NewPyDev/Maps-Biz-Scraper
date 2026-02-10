"""
Reset any stuck jobs back to pending status
"""
from database_manager import BusinessDatabase

db = BusinessDatabase()
cursor = db.conn.cursor()

# Find stuck running jobs
cursor.execute('SELECT id, category, city FROM scraping_jobs WHERE status="running"')
stuck_jobs = cursor.fetchall()

if stuck_jobs:
    print("\n" + "="*60)
    print("  FOUND STUCK JOBS")
    print("="*60)
    
    for job in stuck_jobs:
        print(f"\nJob #{job[0]}: {job[1]} in {job[2]}")
        print("  Status: Running (stuck)")
    
    # Reset them to pending
    cursor.execute('UPDATE scraping_jobs SET status="pending" WHERE status="running"')
    db.conn.commit()
    
    print("\n✓ Reset all stuck jobs to pending")
    print("\nYou can now start the scraper again!")
else:
    print("\n✓ No stuck jobs found")

print("\n" + "="*60)

# Show current status
cursor.execute('SELECT status, COUNT(*) FROM scraping_jobs GROUP BY status')
results = cursor.fetchall()

print("  CURRENT QUEUE STATUS")
print("="*60)
for row in results:
    print(f"  {row[0].capitalize()}: {row[1]} job(s)")
print("="*60 + "\n")

db.close()
