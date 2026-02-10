"""
Quick test to demonstrate the 3-file CSV output
"""
import pandas as pd

# Read your existing CSV
df = pd.read_csv('plumbers_Prague_2025-12-29_202208.csv')

print("=" * 60)
print("📊 CSV SPLITTING DEMONSTRATION")
print("=" * 60)

# Show statistics
total = len(df)
with_website = len(df[df['has_website'] == 'Yes'])
without_website = len(df[df['has_website'] == 'No'])

print(f"\n📈 Statistics from your current data:")
print(f"   Total businesses: {total}")
print(f"   WITH website: {with_website} ({with_website/total*100:.1f}%)")
print(f"   WITHOUT website: {without_website} ({without_website/total*100:.1f}%)")

# Create the 3 files
print(f"\n📁 Creating 3 CSV files...")

# 1. ALL businesses
df.to_csv('plumbers_Prague_DEMO_ALL.csv', index=False, encoding='utf-8-sig')
print(f"   ✓ plumbers_Prague_DEMO_ALL.csv ({total} businesses)")

# 2. WITH websites
with_df = df[df['has_website'] == 'Yes']
with_df.to_csv('plumbers_Prague_DEMO_WITH_website.csv', index=False, encoding='utf-8-sig')
print(f"   ✓ plumbers_Prague_DEMO_WITH_website.csv ({len(with_df)} businesses)")

# 3. WITHOUT websites
without_df = df[df['has_website'] == 'No']
if len(without_df) > 0:
    without_df.to_csv('plumbers_Prague_DEMO_WITHOUT_website.csv', index=False, encoding='utf-8-sig')
    print(f"   ✓ plumbers_Prague_DEMO_WITHOUT_website.csv ({len(without_df)} businesses)")
else:
    print(f"   ℹ No businesses without websites found")

print("\n" + "=" * 60)
print("✅ Done! Check the 3 CSV files created.")
print("=" * 60)

# Show sample data
print("\n📋 Sample from WITH_website.csv (first 5):")
print(with_df[['name', 'has_website']].head())

if len(without_df) > 0:
    print("\n📋 Sample from WITHOUT_website.csv (first 5):")
    print(without_df[['name', 'has_website']].head())
