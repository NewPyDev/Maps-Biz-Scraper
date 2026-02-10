#!/bin/bash
# Business Scraper Startup Script

cd /home/ubuntu/projects/business-scraper

# Activate virtual environment
source .venv/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start with uvicorn (production)
exec uvicorn app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    --access-log
