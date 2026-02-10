# 🚀 Simple Oracle Cloud Deployment Guide

## Fresh Oracle Cloud Instance Setup

### Step 1: Create Oracle Cloud Instance

1. Go to Oracle Cloud Console
2. Create a new **Compute Instance**:
   - **Image**: Ubuntu 22.04 (or latest)
   - **Shape**: VM.Standard.E2.1.Micro (Always Free)
   - **Network**: Allow HTTP (80) and HTTPS (443) traffic
   - **SSH Keys**: Add your public key

3. Note your **Public IP Address** (e.g., 129.159.26.245)

### Step 2: Connect to Your Instance

```bash
ssh ubuntu@YOUR_PUBLIC_IP
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Chrome and ChromeDriver
sudo apt install -y chromium-browser chromium-chromedriver

# Install Nginx
sudo apt install -y nginx

# Install Supervisor
sudo apt install -y supervisor
```

### Step 4: Upload Your Project

**From your Windows machine:**

```powershell
# Compress your project
Compress-Archive -Path "D:\Business scraper\*" -DestinationPath "business-scraper.zip"

# Upload to server
scp business-scraper.zip ubuntu@YOUR_PUBLIC_IP:~/
```

**On the server:**

```bash
# Extract
cd ~
unzip business-scraper.zip -d business-scraper
cd business-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Create .env file
nano .env
```

Add this content:
```
DATABASE_PATH=business_leads.db
HOST=0.0.0.0
PORT=5000
DEBUG=False
HEADLESS_MODE=True
MAX_RESULTS_PER_JOB=50
```

Save and exit (Ctrl+X, Y, Enter)

### Step 6: Setup Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/business-scraper
```

Add this content:
```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/business-scraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Setup Supervisor

```bash
# Create Supervisor config
sudo nano /etc/supervisor/conf.d/business-scraper.conf
```

Add this content:
```ini
[program:business-scraper]
command=/home/ubuntu/business-scraper/venv/bin/python /home/ubuntu/business-scraper/dashboard.py
directory=/home/ubuntu/business-scraper
user=ubuntu
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/business-scraper.log
stderr_logfile=/var/log/supervisor/business-scraper-error.log
```

Start the service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start business-scraper
```

### Step 8: Configure Oracle Cloud Firewall

1. Go to Oracle Cloud Console
2. Navigate to: **Networking** → **Virtual Cloud Networks**
3. Click your VCN → **Security Lists** → **Default Security List**
4. Click **Add Ingress Rules**:
   - **Source CIDR**: 0.0.0.0/0
   - **Destination Port**: 80
   - Click **Add Ingress Rules**

5. Repeat for port 443 (HTTPS)

### Step 9: Access Your Dashboard

Open your browser and go to:
```
http://YOUR_PUBLIC_IP
```

You should see your Business Scraper dashboard!

## 🔧 Management Commands

### Check Status
```bash
sudo supervisorctl status business-scraper
```

### View Logs
```bash
sudo tail -f /var/log/supervisor/business-scraper.log
```

### Restart Application
```bash
sudo supervisorctl restart business-scraper
```

### Stop Application
```bash
sudo supervisorctl stop business-scraper
```

## 🐛 Troubleshooting

### Application won't start
```bash
# Check logs
sudo tail -100 /var/log/supervisor/business-scraper-error.log

# Check if port is in use
sudo netstat -tulpn | grep 5000

# Restart supervisor
sudo systemctl restart supervisor
```

### Can't access from browser
```bash
# Check Nginx status
sudo systemctl status nginx

# Check if app is running
sudo supervisorctl status

# Check Oracle Cloud firewall rules (see Step 8)
```

### Chrome/Selenium issues
```bash
# Install Chrome dependencies
sudo apt install -y chromium-browser chromium-chromedriver

# Check Chrome version
chromium-browser --version
```

## 📊 Using the Dashboard

1. **Dashboard** - View statistics
2. **Scraping** - Manage scraping jobs
3. **Settings** - Add new jobs
4. **Export** - Download data as CSV

## 🔄 Updating Your Application

```bash
# On your Windows machine, upload new files
scp -r "D:\Business scraper\*" ubuntu@YOUR_PUBLIC_IP:~/business-scraper/

# On the server
cd ~/business-scraper
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart business-scraper
```

## 🔒 Optional: Setup Domain & SSL

If you have a domain name:

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

## ✅ Success Checklist

- [ ] Oracle Cloud instance created
- [ ] SSH access working
- [ ] Dependencies installed
- [ ] Project uploaded and extracted
- [ ] Virtual environment created
- [ ] Python packages installed
- [ ] .env file configured
- [ ] Nginx configured and running
- [ ] Supervisor configured and running
- [ ] Oracle Cloud firewall rules added
- [ ] Dashboard accessible from browser

---

**Your dashboard should now be running at:** `http://YOUR_PUBLIC_IP`

**Default port:** 5000 (Flask dashboard)

**To use FastAPI version (port 8000):** Change the Supervisor command to run `app.py` instead of `dashboard.py`
