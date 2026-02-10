# PDF Generation Feature 📄

## Overview

The scraper now automatically generates **professional PDF reports** from all CSV files, perfect for selling your data!

## What Gets Created

For every scrape, you get **6 files total**:

### CSV Files (Data):
1. `{category}_{city}_{timestamp}_ALL.csv` - All businesses
2. `{category}_{city}_{timestamp}_WITH_website.csv` - Only businesses with websites
3. `{category}_{city}_{timestamp}_WITHOUT_website.csv` - Only businesses without websites

### PDF Files (Professional Reports):
1. `{category}_{city}_{timestamp}_ALL.pdf` - All businesses (Blue theme)
2. `{category}_{city}_{timestamp}_WITH_website.pdf` - With websites (Green theme)
3. `{category}_{city}_{timestamp}_WITHOUT_website.pdf` - Without websites (Red theme)

## PDF Features

### Professional Design:
- ✅ **Color-coded themes** - Blue (All), Green (With websites), Red (Without websites)
- ✅ **Clean table layout** - Easy to read, numbered rows
- ✅ **Header with title** - Category, city, and result count
- ✅ **Date stamp** - Shows when the report was generated
- ✅ **Alternating row colors** - Better readability
- ✅ **Compact format** - Fits more data per page
- ✅ **Footer statistics** - Total count and scrape date

### Table Columns:
- **#** - Row number
- **Business Name** - Truncated to 40 chars if too long
- **Address** - Truncated to 35 chars if too long
- **Phone** - Shows "-" if not available
- **Website** - ✓ (Yes) or ✗ (No)

## Why PDFs Are Great for Selling

### 1. Professional Appearance
- Looks polished and ready to deliver to clients
- Color-coded for easy identification
- Clean, organized layout

### 2. Easy to Share
- Single file per report type
- No need for Excel or special software
- Opens on any device

### 3. Print-Ready
- Perfect for offline use
- Can be printed and distributed
- Professional presentation

### 4. Value Perception
- PDFs feel more "finished" than raw CSV
- Clients perceive higher value
- Easier to justify pricing

## Pricing Strategy Ideas

### Package Options:

**Basic Package** - CSV only
- Raw data files
- $X per 100 businesses

**Professional Package** - CSV + PDF
- Raw data + formatted reports
- $X + 50% per 100 businesses

**Premium Package** - CSV + PDF + Analysis
- Everything + insights
- $X + 100% per 100 businesses

### Target Markets:

1. **Marketing Agencies** - Need leads for cold outreach
2. **Web Designers** - Target businesses without websites
3. **SEO Companies** - Find potential clients
4. **Sales Teams** - B2B lead generation
5. **Market Researchers** - Industry analysis

## Example Output

```
📁 Output files created:
   CSV Files:
   1. plumbers_Madrid_2025-12-29_143000_ALL.csv (all businesses)
   2. plumbers_Madrid_2025-12-29_143000_WITH_website.csv (filtered)
   3. plumbers_Madrid_2025-12-29_143000_WITHOUT_website.csv (filtered)
   
   PDF Files:
   1. plumbers_Madrid_2025-12-29_143000_ALL.pdf (all businesses)
   2. plumbers_Madrid_2025-12-29_143000_WITH_website.pdf (filtered)
   3. plumbers_Madrid_2025-12-29_143000_WITHOUT_website.pdf (filtered)
```

## Customization Options

Want to customize the PDFs? Edit these in `google_maps_scraper.py`:

### Change Colors:
```python
# Line ~490 in create_pdf_from_csv()
color_theme = colors.HexColor('#2ecc71')  # Green for WITH websites
color_theme = colors.HexColor('#e74c3c')  # Red for WITHOUT websites
color_theme = colors.HexColor('#3498db')  # Blue for ALL
```

### Change Page Size:
```python
# Line ~470
doc = SimpleDocTemplate(pdf_filename, pagesize=A4)  # Change to letter, legal, etc.
```

### Add Your Branding:
```python
# Add after line ~510 (title section)
branding = Paragraph("<b>Powered by YourCompany.com</b>", subtitle_style)
elements.append(branding)
```

### Change Font Sizes:
```python
# Line ~480-490 (title_style)
fontSize=24  # Make bigger or smaller
```

## Technical Details

### Library Used:
- **ReportLab** - Industry-standard PDF generation library
- Installed automatically with: `pip install -r requirements.txt`

### File Sizes:
- Typical PDF: 5-15 KB for 20-50 businesses
- Very efficient and fast to generate
- Small enough to email easily

### Generation Time:
- ~0.5-2 seconds per PDF
- Happens automatically after CSV creation
- No manual intervention needed

## Troubleshooting

### Issue: PDFs not created
**Solution**: Check if reportlab is installed:
```bash
pip install reportlab
```

### Issue: Unicode errors in PDF
**Solution**: Already handled! The code uses UTF-8 encoding for international characters.

### Issue: Table doesn't fit on page
**Solution**: Text is automatically truncated to fit. Adjust column widths in code if needed.

## Next Steps

1. ✅ Run a test scrape to see the PDFs
2. ✅ Open the PDFs to verify they look professional
3. ✅ Customize colors/branding if desired
4. ✅ Start selling your data packages!

## Sales Tips

### Email Template:
```
Subject: [Category] Business Leads in [City] - [Count] Verified Businesses

Hi [Name],

I've compiled a comprehensive list of [count] [category] businesses in [city].

Package includes:
✓ Complete business data (CSV format)
✓ Professional PDF reports
✓ Filtered by website availability
✓ Scraped on [date]

Perfect for:
- Lead generation
- Market research
- Competitor analysis
- Sales prospecting

Price: $[X]

Interested? Reply to this email!
```

### Upsell Ideas:
- Monthly updates (recurring revenue)
- Multiple cities (bulk discount)
- Custom categories (premium pricing)
- Phone verification service (add-on)
- Email finding service (add-on)

Happy selling! 💰
