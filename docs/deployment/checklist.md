# 🚀 Business Scraper - OCI Deployment Checklist

## Pre-Deployment (Windows)

### ✅ Files Ready
- [x] `start.sh` - Startup script
- [x] `deploy.sh` - Deployment automation
- [x] `nginx-business-scraper.conf` - Nginx config
- [x] `supervisor-business-scraper.conf` - Supervisor config
- [x] `.env.example` - Environment template
- [x] `requirements.txt` - Python dependencies (uv compatible)
- [x] `README_DEPLOYMENT.md` - Deployment guide

### ✅ Project Status
- [x] FastAPI app with health check endpoint
- [x] Database initialization code
- [x] Configuration management
- [x] Static files handling
- [x] Export functionality
- [x] Scraper controller

### ⚠️ Before Upload
- [ ] Review `.gitignore` (don't commit `.env`, `*.db`, `proxies.txt`)
- [ ] Test locally: `uvicorn app:app --reload`
- [ ] Verify all templates exist in `templates/` folder
- [ ] Check `proxies.txt` format (if using proxies)
- [ ] Update domain in `nginx-business-scraper.conf`
- [ ] Update domain in `deploy.sh`

## Deployment Steps

### 1️⃣ Upload to Server

**Option A: Git (Recommended)**
```bash
# Windows
git init
git add .
git commit -m "Initial deployment"
git push origin main

# OCI Server
ssh ubuntu@129.159.26.245
cd ~/projects
git clone <your-repo> business-scraper
```

**Option B: SCP**
```powershell
# Windows PowerShell
scp -r "D:\Business scraper" ubuntu@129.159.26.245:~/projects/business-scraper
```

### 2️⃣ Server Setup
```bash
ssh ubuntu@129.159.26.245
cd ~/projects/business-scraper
chmod +x *.sh
./deploy.sh
```

### 3️⃣ DNS Configuration
- [ ] Add A record: `scraper.yourdomain.com` → `129.159.26.245`
- [ ] Wait for DNS propagation (5-30 min)
- [ ] Test: `nslookup scraper.yourdomain.com`

### 4️⃣ SSL Setup
```bash
sudo certbot --nginx -d scraper.yourdomain.com
```

### 5️⃣ Verification
- [ ] Service running: `sudo supervisorctl status business-scraper`
- [ ] Nginx working: `sudo nginx -t`
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Dashboard accessible: `https://scraper.yourdomain.com`
- [ ] Logs clean: `sudo tail -f /var/log/supervisor/business-scraper-out.log`

## Post-Deployment

### Configuration
- [ ] Edit `.env` with production settings
- [ ] Add proxies to `proxies.txt` (if needed)
- [ ] Set `HEADLESS_MODE=True` in config
- [ ] Configure firewall (OCI Security List: ports 80, 443)

### Testing
- [ ] Access dashboard
- [ ] Add test job
- [ ] Start scraper
- [ ] Check database
- [ ] Export data
- [ ] Download CSV

### Monitoring
- [ ] Setup log rotation
- [ ] Monitor disk space: `df -h`
- [ ] Monitor memory: `htop`
- [ ] Check supervisor logs
- [ ] Check nginx logs

## Quick Commands

### Service Management
```bash
# Status
sudo supervisorctl status business-scraper

# Restart
sudo supervisorctl restart business-scraper

# Logs
sudo tail -f /var/log/supervisor/business-scraper-out.log
```

### Updates
```bash
cd ~/projects/business-scraper
git pull
source .venv/bin/activate
uv pip install -r requirements.txt
sudo supervisorctl restart business-scraper
```

### Backup
```bash
# Database
cp business_leads.db backups/business_leads_$(date +%Y%m%d).db

# Exports
tar -czf exports_backup.tar.gz exports/
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo tail -100 /var/log/supervisor/business-scraper-err.log

# Check port
sudo netstat -tulpn | grep 8000

# Restart supervisor
sudo systemctl restart supervisor
```

### Chrome Issues
```bash
# Install dependencies
sudo apt-get install -y chromium-browser chromium-chromedriver

# Test Chrome
chromium-browser --version
```

### Database Locked
```bash
sudo supervisorctl stop business-scraper
lsof business_leads.db
sudo supervisorctl start business-scraper
```

## Resource Allocation

**OCI Free Tier (2 OCPU, 12GB RAM):**
- Business Scraper: 2GB RAM, 50% CPU
- Chrome instances: 1GB RAM per instance
- Nginx: 100MB RAM
- System: 1GB reserved

## Security

- [x] HTTPS enabled (certbot)
- [x] Firewall configured (OCI Security List)
- [x] `.env` file secured (not in git)
- [x] Rate limiting (nginx)
- [x] Input validation (FastAPI)

## URLs

- **Dashboard**: https://scraper.yourdomain.com
- **API Docs**: https://scraper.yourdomain.com/docs
- **Health**: https://scraper.yourdomain.com/health

## Support

**Logs:**
- Application: `/var/log/supervisor/business-scraper-*.log`
- Nginx: `/var/log/nginx/business-scraper-*.log`
- System: `journalctl -u supervisor`

**Status:**
- Service: `sudo supervisorctl status`
- Nginx: `sudo systemctl status nginx`
- Disk: `df -h`
- Memory: `free -h`

---

## ✅ Deployment Complete!

Your Business Scraper is now running on:
- **Server**: 129.159.26.245
- **Port**: 8000
- **Domain**: scraper.yourdomain.com
- **Protocol**: HTTPS (after certbot)

**Next Steps:**
1. Add scraping jobs via dashboard
2. Configure proxies (optional)
3. Start scraper
4. Monitor logs
5. Export data
