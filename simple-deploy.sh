#!/bin/bash
# Simple Oracle Cloud Deployment Script
# Run this on your fresh Oracle Cloud Ubuntu instance

set -e

echo "🚀 Starting Business Scraper Deployment..."
echo ""

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv chromium-browser chromium-chromedriver nginx supervisor unzip

# Get current directory
PROJECT_DIR=$(pwd)
echo "📁 Project directory: $PROJECT_DIR"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
DATABASE_PATH=business_leads.db
HOST=0.0.0.0
PORT=5000
DEBUG=False
HEADLESS_MODE=True
MAX_RESULTS_PER_JOB=50
JOB_TIMEOUT_SECONDS=1800
STUCK_THRESHOLD_SECONDS=600
EXPORT_DIR=exports
EOF
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p exports
mkdir -p downloaded_files

# Initialize database
echo "💾 Initializing database..."
python3 << EOF
from database_manager import BusinessDatabase
db = BusinessDatabase('business_leads.db')
print("✓ Database initialized")
db.close()
EOF

# Setup Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/business-scraper > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /exports {
        alias $PROJECT_DIR/exports;
        autoindex off;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/business-scraper /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup Supervisor
echo "👷 Configuring Supervisor..."
sudo tee /etc/supervisor/conf.d/business-scraper.conf > /dev/null << EOF
[program:business-scraper]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/dashboard.py
directory=$PROJECT_DIR
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/supervisor/business-scraper.log
stderr_logfile=/var/log/supervisor/business-scraper-error.log
stdout_logfile_maxbytes=50MB
stderr_logfile_maxbytes=50MB
environment=PATH="$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin",PYTHONUNBUFFERED="1"
EOF

# Start Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start business-scraper

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📊 Dashboard: http://$PUBLIC_IP"
echo "📊 Local: http://localhost:5000"
echo ""
echo "🔧 Management Commands:"
echo "  sudo supervisorctl status business-scraper"
echo "  sudo supervisorctl restart business-scraper"
echo "  sudo tail -f /var/log/supervisor/business-scraper.log"
echo ""
echo "⚠️  IMPORTANT: Configure Oracle Cloud Firewall"
echo "   1. Go to Oracle Cloud Console"
echo "   2. Networking → Virtual Cloud Networks"
echo "   3. Security Lists → Add Ingress Rule"
echo "   4. Source: 0.0.0.0/0, Port: 80"
echo ""
echo "=========================================="
