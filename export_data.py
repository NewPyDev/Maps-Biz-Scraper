"""
Data Export Tool
Easy interface to export leads from database
"""

from database_manager import BusinessDatabase
import sys

def show_menu():
    """Display export menu"""
    print("\n" + "=" * 60)
    print("📤 LEAD EXPORT TOOL")
    print("=" * 60)
    print("\n1. Export by City")
    print("2. Export by Category")
    print("3. Export by City + Category")
    print("4. Export by Country")
    print("5. Export with Website Only")
    print("6. Export High Quality Leads (Score > 70)")
    print("7. Export ALL Leads")
    print("8. Custom Export (Advanced)")
    print("9. Show Statistics")
    print("0. Exit")
    print("\n" + "=" * 60)

def export_by_city(db):
    """Export all leads from a specific city"""
    city = input("\nEnter city name: ").strip()
    
    filters = {'city': city}
    filename = f"leads_{city.replace(' ', '_')}.csv"
    
    output_file, count = db.export_to_csv(filters, filename)
    print(f"\n✓ Exported {count} leads to {output_file}")

def export_by_category(db):
    """Export all leads from a specific category"""
    category = input("\nEnter category (e.g., Plumbers, Dentists): ").strip()
    
    filters = {'category': category}
    filename = f"leads_{category.replace(' ', '_').replace('/', '_')}.csv"
    
    output_file, count = db.export_to_csv(filters, filename)
    print(f"\n✓ Exported {count} leads to {output_file}")

def export_by_city_category(db):
    """Export leads from specific city and category"""
    city = input("\nEnter city name: ").strip()
    category = input("Enter category: ").strip()
    
    filters = {'city': city, 'category': category}
    filename = f"leads_{category.replace(' ', '_')}_{city.replace(' ', '_')}.csv"
    
    output_file, count = db.export_to_csv(filters, filename)
    print(f"\n✓ Exported {count} leads to {output_file}")

def export_by_country(db):
    """Export all leads from a specific country"""
    country = input("\nEnter country name: ").strip()
    
    filters = {'country': country}
    filename = f"leads_{country.replace(' ', '_')}.csv"
    
    output_file, count = db.export_to_csv(filters, filename)
    print(f"\n✓ Exported {count} leads to {output_file}")

def export_with_website(db):
    """Export only leads with websites"""
    city = input("\nEnter city (or press Enter for all cities): ").strip()
    category = input("Enter category (or press Enter for all categories): ").strip()
    
    filters = {'has_website': True}
    
    if city:
        filters['city'] = city
    if category:
        filters['category'] = category
    
    filename = "leads_with_website.csv"
    
    output_file, count = db.export_to_csv(filters, filename)
    print(f"\n✓ Exported {count} leads with websites to {output_file}")

def export_high_quality(db):
    """Export high quality leads (score > 70)"""
    city = input("\nEnter city (or press Enter for all cities): ").strip()
    category = input("Enter category (or press Enter for all categories): ").strip()
    
    filters = {'min_quality_score': 70}
    
    if city:
        filters['city'] = city
    if category:
        filters['category'] = category
    
    filename = "leads_high_quality.csv"
    
    output_file, count = db.export_to_csv(filters, filename)
    print(f"\n✓ Exported {count} high-quality leads to {output_file}")

def export_all(db):
    """Export all leads"""
    confirm = input("\n⚠️  Export ALL leads? This may be a large file. (y/n): ").strip().lower()
    
    if confirm == 'y':
        output_file, count = db.export_to_csv({}, "leads_all.csv")
        print(f"\n✓ Exported {count} leads to {output_file}")
    else:
        print("\n✗ Export cancelled")

def custom_export(db):
    """Advanced custom export"""
    print("\n📋 CUSTOM EXPORT")
    print("Leave blank to skip any filter\n")
    
    filters = {}
    
    city = input("City: ").strip()
    if city:
        filters['city'] = city
    
    category = input("Category: ").strip()
    if category:
        filters['category'] = category
    
    country = input("Country: ").strip()
    if country:
        filters['country'] = country
    
    website = input("Has website? (yes/no/blank): ").strip().lower()
    if website == 'yes':
        filters['has_website'] = True
    elif website == 'no':
        filters['has_website'] = False
    
    quality = input("Minimum quality score (0-100, blank for any): ").strip()
    if quality:
        try:
            filters['min_quality_score'] = int(quality)
        except:
            pass
    
    filename = input("\nOutput filename (default: custom_export.csv): ").strip()
    if not filename:
        filename = "custom_export.csv"
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    print(f"\nFilters: {filters}")
    confirm = input("Proceed with export? (y/n): ").strip().lower()
    
    if confirm == 'y':
        output_file, count = db.export_to_csv(filters, filename)
        print(f"\n✓ Exported {count} leads to {output_file}")
    else:
        print("\n✗ Export cancelled")

def show_statistics(db):
    """Display database statistics"""
    stats = db.get_statistics()
    
    print("\n" + "=" * 60)
    print("📊 DATABASE STATISTICS")
    print("=" * 60)
    print(f"\nTotal Businesses: {stats['total_businesses']:,}")
    print(f"With Websites: {stats['with_website']:,}")
    print(f"Without Websites: {stats['total_businesses'] - stats['with_website']:,}")
    print(f"Average Quality Score: {stats['avg_quality_score']}/100")
    
    print("\n📈 BY CATEGORY:")
    for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count:,}")
    
    print("\n🌍 TOP 10 CITIES:")
    for city, count in stats['top_cities'].items():
        print(f"   {city}: {count:,}")
    
    print("\n⚙️ SCRAPING JOBS:")
    for status, count in stats['jobs'].items():
        print(f"   {status.capitalize()}: {count}")
    
    # Revenue potential
    print("\n" + "=" * 60)
    print("💰 REVENUE POTENTIAL")
    print("=" * 60)
    total = stats['total_businesses']
    print(f"At $0.10/lead: ${total * 0.10:,.2f}")
    print(f"At $0.20/lead: ${total * 0.20:,.2f}")
    print(f"At $0.50/lead: ${total * 0.50:,.2f}")
    print(f"At $1.00/lead: ${total * 1.00:,.2f}")
    print("=" * 60)

def main():
    """Main export interface"""
    db = BusinessDatabase('business_leads.db')
    
    while True:
        show_menu()
        choice = input("\nSelect option: ").strip()
        
        try:
            if choice == '1':
                export_by_city(db)
            elif choice == '2':
                export_by_category(db)
            elif choice == '3':
                export_by_city_category(db)
            elif choice == '4':
                export_by_country(db)
            elif choice == '5':
                export_with_website(db)
            elif choice == '6':
                export_high_quality(db)
            elif choice == '7':
                export_all(db)
            elif choice == '8':
                custom_export(db)
            elif choice == '9':
                show_statistics(db)
            elif choice == '0':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid option")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    db.close()

if __name__ == "__main__":
    main()
