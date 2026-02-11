# 🚀 Deploying Business Scraper to Oracle Cloud (OCI)

Follow these simple steps to get your scraper running on your OCI server.

## 1️⃣ Connect to Your Server
Open your terminal (PowerShell or CMD) and SSH into your instance:
```bash
ssh ubuntu@YOUR_SERVER_IP
# Replace YOUR_SERVER_IP with your actual public IP address
```

## 2️⃣ Clone the Repository
Download your code from GitHub:
```bash
git clone https://github.com/NewPyDev/Maps-Biz-Scraper.git
cd Maps-Biz-Scraper
```

## 3️⃣ Run the Deployment Script
We have a script that does everything for you (installs Python, Playwright, dependencies, and sets up a background service):
```bash
chmod +x simple-deploy.sh
./simple-deploy.sh
```
*The script will ask for your sudo password once or twice.*

## 4️⃣ Open Port 8000 (Critical Step!)
By default, OCI blocks port 8000. You must open it to see the dashboard.

### A. On the Server (Firewall)
Run these commands instantly to open the port on the server itself:
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save
```

### B. On the OCI Website (Security List)
1.  Go to your **OCI Console** > **Compute** > **Instances**.
2.  Click on your instance name.
3.  Click on the **Subnet** link (under "Primary VNIC").
4.  Click on the **Security List** (e.g., `Default Security List...`).
5.  Click **"Add Ingress Rules"**.
6.  Enter these details:
    *   **Source CIDR:** `0.0.0.0/0`
    *   **IP Protocol:** `TCP`
    *   **Destination Port Range:** `8000`
    *   **Description:** `Scraper Dashboard`
7.  Click **"Add Ingress Rules"**.

## 5️⃣ Access the Dashboard
Open your browser and visit:
```
http://YOUR_SERVER_IP:8000
```
*(Replace `YOUR_SERVER_IP` with your actual IP)*

---

## 🔄 Updating the Code Later
If you push changes to GitHub, update your live server by running:
```bash
cd ~/Maps-Biz-Scraper
git pull
sudo systemctl restart business-scraper
```

## 🛠 Troubleshooting

### 1. "Welcome to Nginx" Page
If you see the default "Success!" or "Welcome to Nginx" page instead of the dashboard:
```bash
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

### 2. "502 Bad Gateway"
This means the Python application (Supervisor) is not running.
Check logs:
```bash
sudo tail -f /var/log/supervisor/business-scraper-error.log
```

### 3. "Internal Server Error"
Check application logs:
```bash
sudo tail -f /var/log/supervisor/business-scraper.log
```

### 4. General Issues
If the site won't load:
*   Check if the service is running: `sudo systemctl status business-scraper`
*   Check the logs: `journalctl -u business-scraper -f`
*   Double-check the **OCI Security List** (Step 4B) — this is the #1 reason for failure!
