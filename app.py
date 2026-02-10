"""
Dashboard application - FastAPI
Full VPS control: manage scraper, jobs, files, and exports from browser
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import os
import csv
from pathlib import Path
from datetime import datetime
from scraper_controller import ScraperController
from db import Database
from config import settings, ensure_directories

# Import security modules
from auth import verify_credentials
from slowapi.errors import RateLimitExceeded
from rate_limit import limiter, rate_limit_handler

import logging
# Setup logging
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
ensure_directories()

app = FastAPI(title="Scraper Dashboard")

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

templates = Jinja2Templates(directory="templates")

# Initialize controller
controller = ScraperController()
db = Database(str(settings.database_path))


# ─── Pydantic Models ───────────────────────────────────────────
class JobRequest(BaseModel):
    category: str
    city: str
    country: str


class BulkJobRequest(BaseModel):
    categories: List[str]
    cities: List[dict]  # [{"city": "Paris", "country": "France"}, ...]


class FileContent(BaseModel):
    content: str


# ─── Page Routes ───────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, dependencies=[Depends(verify_credentials)])
async def dashboard(request: Request):
    """Main dashboard page"""
    stats = db.get_statistics()

    # Recent jobs
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 10")
    recent_jobs = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "recent_jobs": recent_jobs,
    })


@app.get("/scraping", response_class=HTMLResponse, dependencies=[Depends(verify_credentials)])
async def scraping_page(request: Request):
    """Scraping management page"""
    cursor = db.conn.cursor()

    # Job counts by status
    cursor.execute("""
        SELECT status, COUNT(*) as count FROM jobs GROUP BY status
    """)
    job_counts = {row['status']: row['count'] for row in cursor.fetchall()}

    # Pending jobs
    cursor.execute("SELECT * FROM jobs WHERE status = 'pending' ORDER BY id LIMIT 100")
    pending_jobs = [dict(row) for row in cursor.fetchall()]

    # Recent completed/failed
    cursor.execute("""
        SELECT * FROM jobs WHERE status IN ('completed', 'failed', 'running')
        ORDER BY id DESC LIMIT 20
    """)
    other_jobs = [dict(row) for row in cursor.fetchall()]

    # Read jobs.csv and places.csv
    jobs_content = ""
    places_content = ""
    try:
        with open("jobs.csv", "r", encoding="utf-8") as f:
            jobs_content = f.read()
    except FileNotFoundError:
        pass
    try:
        with open("places.csv", "r", encoding="utf-8") as f:
            places_content = f.read()
    except FileNotFoundError:
        pass

    # Get scraper status
    scraper_status = controller.get_status()

    return templates.TemplateResponse("scraping.html", {
        "request": request,
        "job_counts": job_counts,
        "pending_jobs": pending_jobs,
        "other_jobs": other_jobs,
        "jobs_content": jobs_content,
        "places_content": places_content,
        "scraper_status": scraper_status,
    })


@app.get("/export", response_class=HTMLResponse, dependencies=[Depends(verify_credentials)])
async def export_page(request: Request):
    """Export page"""
    cursor = db.conn.cursor()

    # Get cities and categories for filters
    cursor.execute("SELECT DISTINCT city FROM jobs ORDER BY city")
    cities = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT category FROM jobs ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]

    # List existing export files
    export_files = []
    export_dir = settings.export_dir
    if export_dir.exists():
        for f in sorted(export_dir.glob("*.csv"), key=os.path.getmtime, reverse=True):
            export_files.append({
                "name": f.name,
                "size": f"{f.stat().st_size / 1024:.1f} KB",
                "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })

    return templates.TemplateResponse("export.html", {
        "request": request,
        "cities": cities,
        "categories": categories,
        "export_files": export_files,
    })


# ─── Scraper Control API ──────────────────────────────────────
@app.get("/api/status", dependencies=[Depends(verify_credentials)])
async def get_status(request: Request):
    """Get scraper status"""
    return controller.get_status()


@app.post("/api/start", dependencies=[Depends(verify_credentials)])
async def start_scraper(request: Request):
    """Start scraper"""
    return controller.start()


@app.post("/api/pause", dependencies=[Depends(verify_credentials)])
async def pause_scraper(request: Request):
    return controller.pause()


@app.post("/api/resume", dependencies=[Depends(verify_credentials)])
async def resume_scraper(request: Request):
    return controller.resume()


@app.post("/api/stop", dependencies=[Depends(verify_credentials)])
async def stop_scraper(request: Request):
    return controller.stop()


@app.post("/api/skip", dependencies=[Depends(verify_credentials)])
async def skip_current(request: Request):
    return controller.skip_current()


@app.post("/api/unstuck", dependencies=[Depends(verify_credentials)])
async def force_unstuck(request: Request):
    return controller.force_unstuck()


# ─── Job Management API ───────────────────────────────────────
@app.post("/api/jobs/add", dependencies=[Depends(verify_credentials)])
async def add_job(request: Request, job: JobRequest):
    """Add a single job"""
    result = db.add_job(job.category, job.city, job.country)
    if result:
        return {"success": True, "job_id": result}
    return {"success": False, "error": "Job already exists"}


@app.post("/api/jobs/bulk-add", dependencies=[Depends(verify_credentials)])
async def bulk_add_jobs(request: Request):
    """Add jobs from CSV files (reads jobs.csv × places.csv)"""
    jobs = []
    places = []

    try:
        with open("jobs.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    jobs.append(row[0].strip())
    except FileNotFoundError:
        return {"success": False, "error": "jobs.csv not found"}

    try:
        with open("places.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 2:
                    city = row[0].strip()
                    country = row[1].strip()
                    if city and country:
                        places.append({"city": city, "country": country})
    except FileNotFoundError:
        return {"success": False, "error": "places.csv not found"}

    if not jobs:
        return {"success": False, "error": "No categories found in jobs.csv"}
    if not places:
        return {"success": False, "error": "No cities found in places.csv"}

    added = 0
    skipped = 0
    for job in jobs:
        for place in places:
            result = db.add_job(job, place["city"], place["country"])
            if result:
                added += 1
            else:
                skipped += 1

    return {
        "success": True,
        "added": added,
        "skipped": skipped,
        "total": added + skipped,
        "message": f"Added {added} jobs ({skipped} duplicates skipped)"
    }


@app.post("/api/jobs/delete", dependencies=[Depends(verify_credentials)])
async def delete_job(request: Request):
    """Delete a single job"""
    data = await request.json()
    job_id = data.get("job_id")
    if not job_id:
        return {"success": False, "error": "Missing job_id"}

    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ? AND status = 'pending'", (job_id,))
    db.conn.commit()

    if cursor.rowcount > 0:
        return {"success": True}
    return {"success": False, "error": "Job not found or not pending"}


@app.post("/api/jobs/delete-multiple", dependencies=[Depends(verify_credentials)])
async def delete_multiple_jobs(request: Request):
    """Delete multiple jobs"""
    data = await request.json()
    job_ids = data.get("job_ids", [])
    if not job_ids:
        return {"success": False, "error": "No job IDs provided"}

    placeholders = ",".join("?" * len(job_ids))
    cursor = db.conn.cursor()
    cursor.execute(
        f"DELETE FROM jobs WHERE id IN ({placeholders}) AND status = 'pending'",
        job_ids
    )
    db.conn.commit()

    return {"success": True, "deleted": cursor.rowcount}


@app.post("/api/jobs/clear-completed", dependencies=[Depends(verify_credentials)])
async def clear_completed_jobs(request: Request):
    """Clear completed and failed jobs"""
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE status IN ('completed', 'failed')")
    db.conn.commit()
    return {"success": True, "deleted": cursor.rowcount}


from proxy_scraper import fetch_proxies, verify_proxies
from proxy_manager import get_proxy_manager

from scheduler_service import scheduler

# Start scheduler
app.add_event_handler("startup", scheduler.start)

# ─── Settings API ─────────────────────────────────────────────
@app.get("/api/settings", dependencies=[Depends(verify_credentials)])
async def get_settings(request: Request):
    """Get current settings"""
    return {
        "max_results": controller.max_results
    }


@app.post("/api/settings", dependencies=[Depends(verify_credentials)])
async def update_settings(request: Request):
    """Update settings (max_results)"""
    data = await request.json()
    max_results = data.get("max_results")
    
    if max_results and isinstance(max_results, int) and max_results > 0:
        # Update controller
        controller.set_config(max_results)
        
        # Update .env file
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            new_lines = []
            found = False
            for line in lines:
                if line.strip().startswith("MAX_RESULTS_PER_JOB="):
                    new_lines.append(f"MAX_RESULTS_PER_JOB={max_results}\n")
                    found = True
                else:
                    new_lines.append(line)
            
            if not found:
                new_lines.append(f"MAX_RESULTS_PER_JOB={max_results}\n")
            
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        
        return {"success": True, "message": f"Updated max results to {max_results}"}
    
    return {"success": False, "error": "Invalid value"}


@app.post("/api/proxies/fetch", dependencies=[Depends(verify_credentials)])
def api_fetch_proxies(request: Request):
    """Fetch and verify free proxies from external sources (Runs in threadpool)"""
    try:
        # Run scraper
        logger.info("Fetching proxies from sources...")
        raw_proxies = fetch_proxies()
        
        if not raw_proxies:
            return {"success": False, "error": "No proxies found from sources"}
            
        # Verify proxies
        logger.info(f"Verifying {len(raw_proxies)} proxies...")
        working_proxies = verify_proxies(raw_proxies)
        
        if not working_proxies:
            return {"success": False, "error": "Found proxies but none passed verification test"}
            
        # Save to file
        proxy_file = Path("proxies.txt")
        with open(proxy_file, "w", encoding="utf-8") as f:
            f.write("\n".join(working_proxies))
            
        # Reload manager
        manager = get_proxy_manager()
        count = manager.reload_proxies()
        
        return {
            "success": True, 
            "message": f"Fetched {len(raw_proxies)}, saved {count} working proxies",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error fetching proxies: {e}")
        return {"success": False, "error": str(e)}


# ─── File Management API (jobs.csv, places.csv, proxies.txt) ──
@app.get("/api/files/{filename}", dependencies=[Depends(verify_credentials)])
async def get_file(filename: str):
    """Get file contents"""
    allowed_files = ["jobs.csv", "places.csv", "proxies.txt"]
    if filename not in allowed_files:
        raise HTTPException(400, "Invalid file")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        return {"content": ""}


@app.post("/api/files/{filename}", dependencies=[Depends(verify_credentials)])
async def save_file(filename: str, request: Request):
    """Save file contents"""
    allowed_files = ["jobs.csv", "places.csv", "proxies.txt"]
    if filename not in allowed_files:
        raise HTTPException(400, "Invalid file")

    data = await request.json()
    content = data.get("content", "")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return {"success": True, "message": f"{filename} saved"}


# ─── Export API ────────────────────────────────────────────────
@app.post("/api/export", dependencies=[Depends(verify_credentials)])
async def export_data(request: Request):
    """Export data to CSV"""
    data = await request.json()

    cursor = db.conn.cursor()
    query = "SELECT * FROM businesses WHERE 1=1"
    params = []

    if data.get("cities"):
        placeholders = ",".join("?" * len(data["cities"]))
        query += f" AND city IN ({placeholders})"
        params.extend(data["cities"])

    if data.get("categories"):
        placeholders = ",".join("?" * len(data["categories"]))
        query += f" AND category IN ({placeholders})"
        params.extend(data["categories"])

    if data.get("has_website") is not None:
        if data["has_website"]:
            query += ' AND website IS NOT NULL AND website != ""'
        else:
            query += ' AND (website IS NULL OR website = "")'

    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        raise HTTPException(400, "No data to export")

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"export_{timestamp}.csv"
    filepath = settings.export_dir / filename

    # Write CSV
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    return {
        "success": True,
        "filename": filename,
        "count": len(rows),
        "download_url": f"/download/{filename}",
    }


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download exported file"""
    filepath = settings.export_dir / filename
    if not filepath.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(str(filepath), filename=filename)


# ─── Statistics API ───────────────────────────────────────────
@app.get("/api/stats", dependencies=[Depends(verify_credentials)])
async def api_stats(request: Request):
    """Get full statistics for live updates"""
    stats = db.get_statistics()
    scraper = controller.get_status()

    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT status, COUNT(*) as count FROM jobs GROUP BY status
    """)
    jobs = {row['status']: row['count'] for row in cursor.fetchall()}

    return {
        "total_businesses": stats['total_businesses'],
        "with_website": stats['with_website'],
        "without_website": stats['without_website'],
        "jobs": jobs,
        "scraper": {
            "status": scraper["status"],
            "current_job": scraper.get("current_job"),
            "current_business": scraper["stats"].get("current_business"),
            "businesses_scraped": scraper["stats"].get("businesses_scraped", 0),
            "started_at": scraper["stats"].get("started_at"),
        }
    }


# ─── Health Check ─────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "business-scraper",
        "timestamp": datetime.now().isoformat(),
    }


# ─── Startup ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("🚀 SCRAPER DASHBOARD")
    print("=" * 60)
    print("\n📊 Dashboard: http://localhost:8000")
    print("\n" + "=" * 60)
    uvicorn.run(app, host=settings.host, port=settings.port)
