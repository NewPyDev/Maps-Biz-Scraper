# 🚀 Business Scraper - Oracle Cloud Edition

## What This Is

A Google Maps business scraper with a web dashboard that runs on Oracle Cloud's free tier.

**Features:**
- 🌐 Web dashboard for managing scraping jobs
- 🔄 Real-time progress monitoring
- 📊 Export data to CSV
- 🔁 Automatic proxy rotation
- 💾 SQLite database storage
- 🤖 Selenium-based scraping

## Quick Deploy to Oracle Cloud

### Option 1: Super Quick (5 minutes)

See **[QUICK_START_ORACLE.md](QUICK_START_ORACLE.md)** for the fastest deployment.

### Option 2: Detailed Guide

See **[SIMPLE_ORACLE_DEPLOY.md](SIMPLE_ORACLE_DEPLOY.md)** for step-by-step instructions.

## What You Need

1. **Oracle Cloud Account** (free tier is enough)
2. **Ubuntu 22.04 instance** (VM.Standard.E2.1.Micro)
3. **Your project files** (this folder)

## Deployment Summary

```bash
# 1. Upload project to server
scp scraper.zip ubuntu@YOUR_IP:~/

# 2. SSH to server
ssh ubuntu@YOUR_IP

# 3. Extract and deploy
unzip scraper.zip -d business-scraper
cd business-scraper
chmod +x simple-deploy.sh
./simple-deploy.sh

# 4. Configure Oracle Cloud firewall (port 80)

# 5. Access dashboard
# http://YOUR_IP
```

## Files Included

### Deployment Files
- `simple-deploy.sh` - Automated deployment script
- `QUICK_START_ORACLE.md` - 5-minute quick start guide
- `SIMPLE_ORACLE_DEPLOY.md` - Detailed deployment guide
- `README_ORACLE.md` - This file

### Application Files
- `dashboard.py` - Flask web dashboard (main app)
- `app.py` - FastAPI alternative dashboard
- `scraper_controller.py` - Scraper management
- `scraper.py` - Google Maps scraper
- `database_manager.py` - Database operations
- `db.py` - Database utilities
- `proxy_manager.py` - Proxy rotation
- `config.py` - Configuration
- `requirements.txt` - Python dependencies

### Template Files
- `templates/` - HTML templates for web interface
  - `index.html` - Dashboard home
  - `scraping.html` - Scraping management
  - `export.html` - Data export
  - `settings.html` - Job configuration
  - `files.html` - File editor
  - `setup.html` - Initial setup

## How It Works

1. **Add Jobs** - Define what to scrape (category + city)
2. **Start Scraper** - Automated scraping with Chrome
3. **Monitor Progress** - Real-time updates in dashboard
4. **Export Data** - Download results as CSV

## Dashboard Pages

### 📊 Dashboard (/)
- View statistics
- Total businesses scraped
- Jobs completed
- Recent activity

### 🔄 Scraping (/scraping)
- Start/stop scraper
- View pending jobs
- Monitor current job
- Real-time progress

### ⚙️ Settings (/settings)
- Add new scraping jobs
- Bulk add jobs
- Configure categories and cities

### 📤 Export (/export)
- Filter by category, city, country
- Filter by website availability
- Download CSV files
- Track export history

## Configuration

### Environment Variables (.env)
```bash
DATABASE_PATH=business_leads.db
HOST=0.0.0.0
PORT=5000
DEBUG=False
HEADLESS_MODE=True
MAX_RESULTS_PER_JOB=50
```

### Proxy Configuration (proxies.txt)
```
host:port:username:password
host:port:username:password
```

## Management Commands

```bash
# Check status
sudo supervisorctl status business-scraper

# View logs
sudo tail -f /var/log/supervisor/business-scraper.log

# Restart
sudo supervisorctl restart business-scraper

# Stop
sudo supervisorctl stop business-scraper

# Check Nginx
sudo systemctl status nginx
sudo nginx -t
```

## Troubleshooting

### Dashboard not accessible
1. Check Oracle Cloud firewall rules (port 80)
2. Check app status: `sudo supervisorctl status`
3. Check Nginx: `sudo systemctl status nginx`

### Scraper won't start
1. Check logs: `sudo tail -100 /var/log/supervisor/business-scraper-error.log`
2. Check Chrome: `chromium-browser --version`
3. Restart: `sudo supervisorctl restart business-scraper`

### Database locked
```bash
sudo supervisorctl stop business-scraper
# Wait 5 seconds
sudo supervisorctl start business-scraper
```

### Chrome/Selenium issues
```bash
sudo apt install -y chromium-browser chromium-chromedriver
```

## Updating the Application

```bash
# Upload new files
scp -r "D:\Business scraper\*" ubuntu@YOUR_IP:~/business-scraper/

# On server
cd ~/business-scraper
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart business-scraper
```

## Resource Usage

**Oracle Free Tier (VM.Standard.E2.1.Micro):**
- 1 OCPU (AMD)
- 1 GB RAM
- 50 GB storage

**Application Usage:**
- Dashboard: ~100 MB RAM
- Chrome instance: ~500 MB RAM
- Database: ~10-100 MB (depends on data)

**Recommended:**
- Run 1 Chrome instance at a time
- Limit max results per job to 50-100
- Use proxies to avoid rate limiting

## Security Notes

- ✅ `.env` file not committed (contains sensitive config)
- ✅ `business_leads.db` not committed (contains scraped data)
- ✅ `proxies.txt` not committed (contains proxy credentials)
- ⚠️ Configure Oracle Cloud firewall properly
- ⚠️ Use strong passwords
- ⚠️ Consider adding SSL/HTTPS for production

## Optional: Add SSL/HTTPS

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

## Support

### Documentation
- `QUICK_START_ORACLE.md` - Quick start guide
- `SIMPLE_ORACLE_DEPLOY.md` - Detailed deployment
- `README_ORACLE.md` - This file

### Logs
- Application: `/var/log/supervisor/business-scraper.log`
- Errors: `/var/log/supervisor/business-scraper-error.log`
- Nginx: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### Common Issues
1. **Can't access dashboard** → Check firewall rules
2. **Scraper stuck** → Click "Reset All" in Scraping page
3. **Chrome crashes** → Reduce max results per job
4. **Database locked** → Restart application

## License

This is a commercial lead generation tool. Use responsibly and comply with Google Maps Terms of Service.

---

## 🎉 Ready to Deploy?

1. Read **[QUICK_START_ORACLE.md](QUICK_START_ORACLE.md)**
2. Create Oracle Cloud instance
3. Run `simple-deploy.sh`
4. Access dashboard at `http://YOUR_IP`

**Questions?** Check the detailed guide in `SIMPLE_ORACLE_DEPLOY.md`

---

**Dashboard URL:** `http://YOUR_PUBLIC_IP`  
**Default Port:** 5000 (Flask)  
**Alternative:** 8000 (FastAPI - edit supervisor config)
