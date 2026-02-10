"""
Quick Setup Script for Lead Generation Business
Run this to initialize your database and create your first scraping jobs
"""

from database_manager import BusinessDatabase
import logging

logging.basicConfig(level=logging.INFO)

def setup_database():
    """Initialize database with categories and cities"""
    
    print("=" * 60)
    print("🚀 LEAD GENERATION BUSINESS - SETUP")
    print("=" * 60)
    
    # Initialize database
    db = BusinessDatabase('business_leads.db')
    
    # Define all categories
    categories = [
        'Plumbers',
        'Electricians',
        'Carpenters',
        'HVAC/Air conditioning',
        'Roofing contractors',
        'Painters',
        'Locksmith',
        'Pest control',
        'Cleaning services',
        'Landscaping',
        'Dentists',
        'Doctors/Medical clinics',
        'Lawyers',
        'Accountants',
        'Real estate agents',
        'Restaurants/Cafes',
        'Hair salons/Barber shops',
        'Fitness gyms',
        'Hotels/Accommodations',
        'Pharmacies'
    ]
    
    # Top 100 cities worldwide (you can expand this)
    cities_countries = [
        # USA
        ('New York', 'USA'),
        ('Los Angeles', 'USA'),
        ('Chicago', 'USA'),
        ('Houston', 'USA'),
        ('Phoenix', 'USA'),
        ('Philadelphia', 'USA'),
        ('San Antonio', 'USA'),
        ('San Diego', 'USA'),
        ('Dallas', 'USA'),
        ('San Jose', 'USA'),
        ('Austin', 'USA'),
        ('Jacksonville', 'USA'),
        ('Fort Worth', 'USA'),
        ('Columbus', 'USA'),
        ('Charlotte', 'USA'),
        ('San Francisco', 'USA'),
        ('Indianapolis', 'USA'),
        ('Seattle', 'USA'),
        ('Denver', 'USA'),
        ('Boston', 'USA'),
        
        # UK
        ('London', 'UK'),
        ('Birmingham', 'UK'),
        ('Manchester', 'UK'),
        ('Glasgow', 'UK'),
        ('Liverpool', 'UK'),
        ('Leeds', 'UK'),
        ('Sheffield', 'UK'),
        ('Edinburgh', 'UK'),
        ('Bristol', 'UK'),
        ('Leicester', 'UK'),
        
        # Spain
        ('Madrid', 'Spain'),
        ('Barcelona', 'Spain'),
        ('Valencia', 'Spain'),
        ('Seville', 'Spain'),
        ('Zaragoza', 'Spain'),
        ('Málaga', 'Spain'),
        ('Murcia', 'Spain'),
        ('Palma', 'Spain'),
        ('Las Palmas', 'Spain'),
        ('Bilbao', 'Spain'),
        
        # France
        ('Paris', 'France'),
        ('Marseille', 'France'),
        ('Lyon', 'France'),
        ('Toulouse', 'France'),
        ('Nice', 'France'),
        ('Nantes', 'France'),
        ('Strasbourg', 'France'),
        ('Montpellier', 'France'),
        ('Bordeaux', 'France'),
        ('Lille', 'France'),
        
        # Germany
        ('Berlin', 'Germany'),
        ('Hamburg', 'Germany'),
        ('Munich', 'Germany'),
        ('Cologne', 'Germany'),
        ('Frankfurt', 'Germany'),
        ('Stuttgart', 'Germany'),
        ('Düsseldorf', 'Germany'),
        ('Dortmund', 'Germany'),
        ('Essen', 'Germany'),
        ('Leipzig', 'Germany'),
        
        # Italy
        ('Rome', 'Italy'),
        ('Milan', 'Italy'),
        ('Naples', 'Italy'),
        ('Turin', 'Italy'),
        ('Palermo', 'Italy'),
        ('Genoa', 'Italy'),
        ('Bologna', 'Italy'),
        ('Florence', 'Italy'),
        ('Bari', 'Italy'),
        ('Catania', 'Italy'),
        
        # Canada
        ('Toronto', 'Canada'),
        ('Montreal', 'Canada'),
        ('Vancouver', 'Canada'),
        ('Calgary', 'Canada'),
        ('Edmonton', 'Canada'),
        ('Ottawa', 'Canada'),
        ('Winnipeg', 'Canada'),
        ('Quebec City', 'Canada'),
        ('Hamilton', 'Canada'),
        ('Kitchener', 'Canada'),
        
        # Australia
        ('Sydney', 'Australia'),
        ('Melbourne', 'Australia'),
        ('Brisbane', 'Australia'),
        ('Perth', 'Australia'),
        ('Adelaide', 'Australia'),
        ('Gold Coast', 'Australia'),
        ('Canberra', 'Australia'),
        ('Newcastle', 'Australia'),
        ('Wollongong', 'Australia'),
        ('Hobart', 'Australia'),
        
        # Other European Cities
        ('Amsterdam', 'Netherlands'),
        ('Brussels', 'Belgium'),
        ('Vienna', 'Austria'),
        ('Prague', 'Czech Republic'),
        ('Copenhagen', 'Denmark'),
        ('Stockholm', 'Sweden'),
        ('Oslo', 'Norway'),
        ('Helsinki', 'Finland'),
        ('Dublin', 'Ireland'),
        ('Lisbon', 'Portugal'),
    ]
    
    print(f"\n📋 Creating scraping jobs...")
    print(f"   Categories: {len(categories)}")
    print(f"   Cities: {len(cities_countries)}")
    print(f"   Total jobs: {len(categories) * len(cities_countries)}")
    
    # Ask user which cities to start with
    print("\n🎯 RECOMMENDATION: Start with 10-20 cities to test")
    print("   You can always add more later!")
    
    choice = input("\nHow many cities to start with? (default: 10): ").strip()
    
    try:
        num_cities = int(choice) if choice else 10
    except:
        num_cities = 10
    
    selected_cities = cities_countries[:num_cities]
    
    print(f"\n✓ Selected {len(selected_cities)} cities:")
    for city, country in selected_cities:
        print(f"   - {city}, {country}")
    
    # Ask which categories to prioritize
    print("\n💰 HIGH-VALUE CATEGORIES (recommended to start):")
    high_value = ['Dentists', 'Doctors/Medical clinics', 'Lawyers', 'Accountants']
    for i, cat in enumerate(high_value, 1):
        print(f"   {i}. {cat}")
    
    print("\n🔧 SERVICE CATEGORIES:")
    service_cats = ['Plumbers', 'Electricians', 'HVAC/Air conditioning', 'Roofing contractors']
    for i, cat in enumerate(service_cats, 1):
        print(f"   {i}. {cat}")
    
    choice = input("\nStart with high-value categories only? (y/n, default: y): ").strip().lower()
    
    if choice == 'n':
        selected_categories = categories
    else:
        selected_categories = high_value
    
    print(f"\n✓ Selected {len(selected_categories)} categories")
    
    # Create jobs
    total_jobs = len(selected_categories) * len(selected_cities)
    print(f"\n📊 Creating {total_jobs} scraping jobs...")
    
    added = db.bulk_add_jobs(selected_categories, selected_cities)
    
    print(f"✓ Added {added} jobs to queue")
    
    # Show statistics
    stats = db.get_statistics()
    
    print("\n" + "=" * 60)
    print("📊 DATABASE STATISTICS")
    print("=" * 60)
    print(f"Total businesses: {stats['total_businesses']}")
    print(f"Pending jobs: {stats['jobs'].get('pending', 0)}")
    print(f"Completed jobs: {stats['jobs'].get('completed', 0)}")
    print(f"Failed jobs: {stats['jobs'].get('failed', 0)}")
    
    # Estimate potential
    avg_businesses_per_job = 150  # Conservative estimate
    potential_leads = added * avg_businesses_per_job
    
    print("\n" + "=" * 60)
    print("💰 REVENUE POTENTIAL")
    print("=" * 60)
    print(f"Estimated leads: ~{potential_leads:,}")
    print(f"At $0.20/lead: ${potential_leads * 0.20:,.2f}")
    print(f"At $0.50/lead: ${potential_leads * 0.50:,.2f}")
    print(f"At $1.00/lead: ${potential_leads * 1.00:,.2f}")
    
    print("\n" + "=" * 60)
    print("⏱️ TIME ESTIMATE")
    print("=" * 60)
    print(f"Jobs to complete: {added}")
    print(f"At 5 jobs/day: ~{added/5:.0f} days")
    print(f"At 10 jobs/day: ~{added/10:.0f} days")
    print(f"At 20 jobs/day: ~{added/20:.0f} days")
    
    print("\n" + "=" * 60)
    print("🚀 NEXT STEPS")
    print("=" * 60)
    print("1. Make sure proxies.txt has at least 10 proxies")
    print("2. Run: python scraper_with_database.py")
    print("3. Monitor progress in scraper.log")
    print("4. Export data: python export_data.py")
    print("5. Start selling! 💰")
    print("=" * 60)
    
    db.close()


if __name__ == "__main__":
    setup_database()
