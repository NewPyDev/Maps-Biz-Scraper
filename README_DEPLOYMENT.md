# Business Scraper - OCI Deployment Guide

## 🚀 Quick Deploy

### Prerequisites
- OCI Free Tier ARM64 server (Ubuntu 22.04)
- IP: 129.159.26.245
- Domain pointing to server IP
- SSH access as `ubuntu` user

### 1. Upload Project to Server

**Option A: Git (Recommended)**
```bash
# On your Windows machine
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main

# On OCI server
ssh ubuntu@129.159.26.245
cd ~/projects
git clone <your-repo-url> business-scraper
```

**Option B: SCP (Direct Upload)**
```bash
# On your Windows machine (PowerShell)
scp -r D:\Business-scraper ubuntu@129.159.26.245:~/projects/business-scraper
```

### 2. Deploy

```bash
# SSH to server
ssh ubuntu@129.159.26.245

# Navigate to project
cd ~/projects/business-scraper

# Make scripts executable
chmod +x *.sh

# Run deployment
./deploy.sh
```

### 3. Configure Domain

**DNS Settings:**
- Add A record: `scraper.yourdomain.com` → `129.159.26.245`
- Wait for DNS propagation (5-30 minutes)

**Update Configuration:**
```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/business-scraper
# Change: server_name scraper.yourdomain.com;

# Reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Setup SSL (HTTPS)

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d scraper.yourdomain.com

# Auto-renewal is configured automatically
```

## 📊 Management Commands

### Service Control
```bash
# Check status
sudo supervisorctl status business-scraper

# Start/Stop/Restart
sudo supervisorctl start business-scraper
sudo supervisorctl stop business-scraper
sudo supervisorctl restart business-scraper

# View logs
sudo tail -f /var/log/supervisor/business-scraper-out.log
sudo tail -f /var/log/supervisor/business-scraper-err.log
```

### Nginx
```bash
# Test configuration
sudo nginx -t

# Reload
sudo systemctl reload nginx

# View logs
sudo tail -f /var/log/nginx/business-scraper-access.log
sudo tail -f /var/log/nginx/business-scraper-error.log
```

### Application Updates
```bash
# Pull latest code
cd ~/projects/business-scraper
git pull

# Update dependencies
source .venv/bin/activate
uv pip install -r requirements.txt

# Restart service
sudo supervisorctl restart business-scraper
```

## 🔧 Configuration

### Environment Variables
Edit `.env` file:
```bash
nano ~/projects/business-scraper/.env
```

Key settings:
- `DATABASE_PATH`: SQLite database location
- `HEADLESS_MODE=True`: Run Chrome headless (required for server)
- `MAX_RESULTS_PER_JOB`: Results per scraping job
- `PORT=8000`: Application port

### Proxy Configuration
Add proxies to `proxies.txt`:
```
username:password@host:port
username:password@host:port
```

## 📈 Monitoring

### Resource Usage
```bash
# CPU and Memory
htop

# Disk space
df -h

# Application processes
ps aux | grep uvicorn
```

### Database
```bash
# Check database size
ls -lh ~/projects/business-scraper/business_leads.db

# Backup database
cp business_leads.db business_leads.db.backup
```

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo tail -100 /var/log/supervisor/business-scraper-err.log

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Restart supervisor
sudo systemctl restart supervisor
```

### Chrome/Selenium Issues
```bash
# Install Chrome dependencies
sudo apt-get install -y chromium-browser chromium-chromedriver

# Check Chrome version
chromium-browser --version
```

### Database Locked
```bash
# Stop application
sudo supervisorctl stop business-scraper

# Check for locks
lsof ~/projects/business-scraper/business_leads.db

# Restart
sudo supervisorctl start business-scraper
```

## 🔒 Security

### Firewall (OCI Security List)
Open ports in OCI Console:
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 22 (SSH) - restrict to your IP

### Application Security
- Always use HTTPS in production
- Keep `.env` file secure (never commit)
- Regularly update dependencies
- Monitor logs for suspicious activity

## 📦 Resource Allocation

**OCI Free Tier (2 OCPU, 12GB RAM):**
- Business Scraper: 2GB RAM, 50% CPU
- Nginx: 100MB RAM, 5% CPU
- System: 1GB RAM reserved

**Scaling:**
- Increase `--workers` in `start.sh` for more traffic
- Add more proxies for faster scraping
- Use external database (PostgreSQL) for large datasets

## 🌐 Access URLs

- **Dashboard**: https://scraper.yourdomain.com
- **API Docs**: https://scraper.yourdomain.com/docs
- **Health Check**: https://scraper.yourdomain.com/health

## 📞 Support

For issues:
1. Check logs: `/var/log/supervisor/business-scraper-*.log`
2. Verify configuration: `sudo nginx -t`
3. Test locally: `curl http://localhost:8000`
4. Check DNS: `nslookup scraper.yourdomain.com`

---

**Deployment Checklist:**
- [ ] Project uploaded to server
- [ ] Dependencies installed (uv, nginx, supervisor)
- [ ] Virtual environment created
- [ ] `.env` file configured
- [ ] Database initialized
- [ ] Nginx configured
- [ ] Supervisor configured
- [ ] DNS configured
- [ ] SSL certificate installed
- [ ] Service running
- [ ] Logs verified
- [ ] Dashboard accessible

**Port Used:** 8000 (Scraper Dashboard)
**Server:** 129.159.26.245
**OS:** Ubuntu 22.04 ARM64
