# ⚡ Quick Start - Oracle Cloud Deployment

## 🎯 Deploy in 5 Minutes

### 1️⃣ Create Oracle Cloud Instance (2 min)

1. Login to [Oracle Cloud](https://cloud.oracle.com)
2. **Compute** → **Instances** → **Create Instance**
3. Choose:
   - **Image**: Ubuntu 22.04
   - **Shape**: VM.Standard.E2.1.Micro (Free Tier)
4. **Add SSH Keys** (generate or use existing)
5. Click **Create**
6. **Note your Public IP** (e.g., 129.159.26.245)

### 2️⃣ Upload Project (1 min)

**On Windows (PowerShell):**
```powershell
# Compress project
Compress-Archive -Path "D:\Business scraper\*" -DestinationPath "scraper.zip"

# Upload to server
scp scraper.zip ubuntu@YOUR_IP:~/
```

### 3️⃣ Deploy (2 min)

**SSH to server:**
```bash
ssh ubuntu@YOUR_IP
```

**Run deployment:**
```bash
# Extract project
unzip scraper.zip -d business-scraper
cd business-scraper

# Make script executable
chmod +x simple-deploy.sh

# Run deployment
./simple-deploy.sh
```

**Wait 2-3 minutes for installation...**

### 4️⃣ Configure Firewall (1 min)

**In Oracle Cloud Console:**
1. **Networking** → **Virtual Cloud Networks**
2. Click your VCN → **Security Lists** → **Default Security List**
3. **Add Ingress Rules**:
   - Source: `0.0.0.0/0`
   - Port: `80`
   - Click **Add**

### 5️⃣ Access Dashboard ✅

Open browser:
```
http://YOUR_PUBLIC_IP
```

**Done! 🎉**

---

## 📋 What You Get

- ✅ Business Scraper Dashboard running on port 5000
- ✅ Nginx reverse proxy (port 80)
- ✅ Supervisor (auto-restart on crash)
- ✅ SQLite database
- ✅ Chrome/Selenium ready
- ✅ All dependencies installed

## 🔧 Quick Commands

```bash
# Check status
sudo supervisorctl status

# View logs
sudo tail -f /var/log/supervisor/business-scraper.log

# Restart
sudo supervisorctl restart business-scraper

# Stop
sudo supervisorctl stop business-scraper
```

## 🐛 Troubleshooting

### Can't access dashboard?
1. Check Oracle Cloud firewall (Step 4)
2. Check app status: `sudo supervisorctl status`
3. Check logs: `sudo tail -100 /var/log/supervisor/business-scraper-error.log`

### App won't start?
```bash
# Check logs
sudo tail -100 /var/log/supervisor/business-scraper-error.log

# Restart supervisor
sudo systemctl restart supervisor
sudo supervisorctl restart business-scraper
```

### Chrome issues?
```bash
# Reinstall Chrome
sudo apt install -y chromium-browser chromium-chromedriver
```

---

## 📊 Using the Dashboard

1. **Dashboard** - View statistics and overview
2. **Scraping** - Start/stop scraper, manage jobs
3. **Settings** - Add new scraping jobs
4. **Export** - Download scraped data as CSV

### Adding Jobs

1. Go to **Settings** page
2. Fill in:
   - Category (e.g., "plumbers")
   - City (e.g., "Madrid")
   - Country (e.g., "Spain")
3. Click **Add Job**

### Starting Scraper

1. Go to **Scraping** page
2. Click **Start Scraper**
3. Set max jobs and daily limit
4. Click **Start**
5. Monitor progress in real-time

### Exporting Data

1. Go to **Export** page
2. Select filters (city, category, etc.)
3. Click **Export**
4. Download CSV file

---

## 🔄 Updating Your App

```bash
# Upload new files from Windows
scp -r "D:\Business scraper\*" ubuntu@YOUR_IP:~/business-scraper/

# On server
cd ~/business-scraper
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart business-scraper
```

---

## ✅ Success Checklist

- [ ] Oracle Cloud instance created
- [ ] Project uploaded
- [ ] `simple-deploy.sh` executed successfully
- [ ] Firewall rules added (port 80)
- [ ] Dashboard accessible at `http://YOUR_IP`
- [ ] Can add jobs in Settings
- [ ] Can start scraper
- [ ] Can export data

---

## 🎉 You're Ready!

Your Business Scraper is now running on Oracle Cloud!

**Dashboard URL:** `http://YOUR_PUBLIC_IP`

**Next Steps:**
1. Add scraping jobs in Settings
2. Start the scraper
3. Monitor progress
4. Export data as CSV

**Need help?** Check `SIMPLE_ORACLE_DEPLOY.md` for detailed instructions.
