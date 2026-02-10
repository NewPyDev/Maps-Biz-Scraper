FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Expose port
EXPOSE 8000

# Run with Python unbuffered to see logs immediately
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
