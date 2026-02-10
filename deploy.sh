#!/bin/bash
# Business Scraper Deployment Script for OCI Server

set -e  # Exit on error

PROJECT_NAME="business-scraper"
PROJECT_DIR="/home/ubuntu/projects/${PROJECT_NAME}"
DOMAIN="scraper.yourdomain.com"  # Change this to your actual domain

echo "🚀 Deploying Business Scraper to OCI Server..."

# 1. Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    python3-pip \
    nginx \
    supervisor

# 2. Install uv (Python package manager)
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 3. Create virtual environment with uv
echo "🐍 Creating virtual environment..."
cd ${PROJECT_DIR}
uv venv .venv

# 4. Install Python dependencies with uv
echo "📚 Installing Python dependencies..."
source .venv/bin/activate
uv pip install -r requirements.txt

# 5. Setup environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# 6. Create necessary directories
echo "📁 Creating directories..."
mkdir -p exports
mkdir -p downloaded_files
mkdir -p templates

# 7. Initialize database
echo "💾 Initializing database..."
python3 -c "from db import Database; db = Database(); print('Database initialized')"

# 8. Setup Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx-business-scraper.conf /etc/nginx/sites-available/${PROJECT_NAME}
sudo ln -sf /etc/nginx/sites-available/${PROJECT_NAME} /etc/nginx/sites-enabled/
sudo nginx -t

# 9. Setup Supervisor
echo "👷 Configuring Supervisor..."
sudo cp supervisor-business-scraper.conf /etc/supervisor/conf.d/${PROJECT_NAME}.conf
sudo supervisorctl reread
sudo supervisorctl update

# 10. Start services
echo "🎬 Starting services..."
sudo systemctl reload nginx
sudo supervisorctl start ${PROJECT_NAME}

# 11. Check status
echo ""
echo "=" * 60
echo "✅ Deployment Complete!"
echo "=" * 60
echo ""
echo "📊 Dashboard: http://${DOMAIN}"
echo "📊 Local: http://localhost:8000"
echo ""
echo "🔧 Management Commands:"
echo "  sudo supervisorctl status ${PROJECT_NAME}"
echo "  sudo supervisorctl restart ${PROJECT_NAME}"
echo "  sudo supervisorctl stop ${PROJECT_NAME}"
echo "  sudo tail -f /var/log/supervisor/${PROJECT_NAME}-out.log"
echo ""
echo "🔒 Setup SSL (recommended):"
echo "  sudo certbot --nginx -d ${DOMAIN}"
echo ""
echo "=" * 60
