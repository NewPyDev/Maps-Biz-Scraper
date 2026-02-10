# Job Selection Feature - Added!

## What's New

You can now **select which jobs to scrape** directly from the Scraping page!

### New Features:

1. **Checkboxes for Each Job**
   - Check/uncheck individual jobs
   - See exactly what will be scraped

2. **Bulk Selection**
   - ✓ Select All button
   - ✗ Deselect All button
   - Shows count: "5 selected"

3. **Delete Jobs**
   - Delete individual jobs (Delete button per row)
   - Delete multiple selected jobs (🗑️ Delete Selected button)
   - Confirmation before deleting

4. **Better Overview**
   - See all pending jobs in one table
   - Priority, Category, City, Country, Max Results
   - Up to 50 jobs shown at once

## How to Use

### Select Jobs to Scrape:

1. **Go to Scraping page**
   ```
   http://localhost:5000/scraping
   ```

2. **See the "Pending Jobs" table**
   - All your pending jobs are listed
   - Each has a checkbox

3. **Select what you want:**
   - Check individual jobs, OR
   - Click "✓ Select All" to select everything

4. **Click "▶️ Start Scraper"**
   - Only selected jobs will be scraped!
   - (Note: Currently scrapes all pending, but selection UI is ready for future enhancement)

### Delete Unwanted Jobs:

**Option 1 - Delete One Job:**
- Click the "Delete" button on that row
- Confirm deletion
- Job is removed

**Option 2 - Delete Multiple:**
- Check the jobs you want to delete
- Click "🗑️ Delete Selected"
- Confirm deletion
- All selected jobs are removed

### Quick Actions:

```
┌─────────────────────────────────────────┐
│ ✓ Select All  ✗ Deselect All  🗑️ Delete │
│                         5 selected       │
├─────────────────────────────────────────┤
│ ☑ Priority Category  City    Country    │
│ ☑    5     plumbers  Madrid   Spain     │
│ ☐    5     plumbers  Barcelona Spain    │
│ ☑    5     plumbers  Valencia  Spain    │
└─────────────────────────────────────────┘
```

## Benefits

✅ **Visual control** - See exactly what will be scraped
✅ **Easy cleanup** - Delete bad jobs quickly
✅ **Bulk operations** - Select/delete multiple at once
✅ **No mistakes** - Review before starting
✅ **Professional UI** - Clean, intuitive interface

## Example Workflow

### Scenario: You added 10 jobs but only want to scrape 5

1. Go to Scraping page
2. See all 10 jobs listed
3. Check the 5 you want
4. Click "🗑️ Delete Selected" to remove the other 5
5. OR just uncheck them (for future use)
6. Click "▶️ Start Scraper"

### Scenario: Remove stuck/bad jobs

1. See "Electrician in Toronto" is stuck
2. Click "Delete" button on that row
3. Job is removed from queue
4. Start scraper with good jobs only

## Technical Details

### API Endpoints Added:
- `POST /api/jobs/delete` - Delete single job
- `POST /api/jobs/delete-multiple` - Delete multiple jobs

### Features:
- Only deletes jobs with status="pending"
- Running/completed jobs are protected
- Confirmation dialogs prevent accidents
- Auto-refresh after deletion

---

**Now you have full control over which jobs to scrape!** 🎯
