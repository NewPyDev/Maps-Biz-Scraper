"""
Test PDF generation from existing CSV files
"""
import sys
sys.path.insert(0, '.')
from google_maps_scraper import create_pdf_from_csv
import os

# Find a CSV file to test with
csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and ('plumbers' in f or 'restaurants' in f)]

if not csv_files:
    print("No CSV files found to test with!")
    exit(1)

# Use the first CSV file found
test_csv = csv_files[0]
print(f"Testing PDF generation with: {test_csv}")
print("=" * 60)

# Extract category and city from filename
parts = test_csv.split('_')
category = parts[0]
city = parts[1]

# Generate PDF
pdf_file = create_pdf_from_csv(test_csv, category, city)

if pdf_file:
    print(f"\n✓ SUCCESS! PDF created: {pdf_file}")
    print(f"✓ File size: {os.path.getsize(pdf_file) / 1024:.2f} KB")
    print("\nOpen the PDF to verify it looks professional!")
else:
    print("\n✗ Failed to create PDF")

print("=" * 60)
