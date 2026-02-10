"""
Import jobs from CSV files
Reads jobs.csv and places.csv and creates all combinations
"""

import csv
from database_manager import BusinessDatabase

def import_jobs_from_csv():
    """Import jobs from CSV files"""
    
    # Read jobs
    print("\n" + "=" * 60)
    print("📋 IMPORTING JOBS FROM CSV FILES")
    print("=" * 60)
    
    jobs = []
    with open('jobs.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                jobs.append(row[0].strip())
    
    print(f"\n✓ Loaded {len(jobs)} job categories from jobs.csv")
    
    # Read places
    places = []
    with open('places.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 2:
                city = row[0].strip()
                country = row[1].strip()
                if city and country:
                    places.append({'city': city, 'country': country})
    
    print(f"✓ Loaded {len(places)} cities from places.csv")
    
    # Calculate total combinations
    total_combinations = len(jobs) * len(places)
    print(f"\n📊 Total possible combinations: {total_combinations:,}")
    print(f"   ({len(jobs)} jobs × {len(places)} cities)")
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will create a LOT of jobs!")
    print("   Recommended: Start with a subset first")
    print("\nOptions:")
    print("  1. Import ALL jobs (not recommended - too many)")
    print("  2. Import first 10 jobs × all cities")
    print("  3. Import first 5 jobs × first 20 cities")
    print("  4. Import specific range (custom)")
    print("  5. Cancel")
    
    choice = input("\nYour choice (1-5): ").strip()
    
    if choice == '1':
        selected_jobs = jobs
        selected_places = places
    elif choice == '2':
        selected_jobs = jobs[:10]
        selected_places = places
    elif choice == '3':
        selected_jobs = jobs[:5]
        selected_places = places[:20]
    elif choice == '4':
        try:
            num_jobs = int(input("How many jobs? (1-130): "))
            num_places = int(input("How many cities? (1-240): "))
            selected_jobs = jobs[:num_jobs]
            selected_places = places[:num_places]
        except:
            print("Invalid input. Cancelled.")
            return
    else:
        print("Cancelled.")
        return
    
    total_to_add = len(selected_jobs) * len(selected_places)
    
    print(f"\n📦 Will create {total_to_add:,} jobs:")
    print(f"   - {len(selected_jobs)} job categories")
    print(f"   - {len(selected_places)} cities")
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    # Connect to database
    db = BusinessDatabase('business_leads.db')
    
    # Add jobs
    added = 0
    skipped = 0
    
    print(f"\n⏳ Adding jobs to database...")
    
    for i, job in enumerate(selected_jobs):
        for j, place in enumerate(selected_places):
            try:
                job_id = db.add_scraping_job(
                    category=job,
                    city=place['city'],
                    country=place['country'],
                    max_results=50,
                    priority=5
                )
                
                if job_id:
                    added += 1
                else:
                    skipped += 1
                
                # Progress indicator
                if (added + skipped) % 100 == 0:
                    print(f"   Progress: {added + skipped}/{total_to_add} ({added} added, {skipped} skipped)")
                    
            except Exception as e:
                print(f"   Error adding {job} in {place['city']}: {e}")
                skipped += 1
    
    db.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ IMPORT COMPLETE")
    print("=" * 60)
    print(f"✓ Added: {added:,} new jobs")
    print(f"⚠️  Skipped: {skipped:,} (duplicates or errors)")
    print(f"📊 Total: {added + skipped:,} processed")
    print("\n💡 Next steps:")
    print("   1. Go to dashboard: http://localhost:5000")
    print("   2. Check the Scraping page")
    print("   3. Start the scraper")
    print("=" * 60)


if __name__ == "__main__":
    try:
        import_jobs_from_csv()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
