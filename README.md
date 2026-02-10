# Business Scraper - Professional Lead Generation System

Professional Google Maps business lead generation system with Playwright, FastAPI, and smart proxy management.

## ✨ Features

- ✅ **Playwright-based scraping** - Reliable, modern browser automation
- ✅ **Smart proxy management** - Auto-detection, rotation, health tracking
- ✅ **FastAPI dashboard** - Real-time updates and job management
- ✅ **CSV/PDF export** - Professional reports with filtering
- ✅ **Job queue system** - Manage multiple scraping jobs
- ✅ **SQLite database** - Persistent storage with quality scoring
- ✅ **Environment-based config** - Type-safe configuration with `.env`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install packages
uv pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your settings (optional)
```

### 3. Run Application

```bash
python app.py
```

### 4. Access Dashboard

Open http://localhost:8000 in your browser

## 📖 Documentation

- **[Documentation Index](docs/README.md)** - All documentation
- **[Dashboard Guide](docs/guides/dashboard.md)** - Using the web interface
- **[CSV Import Guide](docs/guides/csv-import.md)** - Bulk job import
- **[PDF Generation Guide](docs/guides/pdf-generation.md)** - Export reports
- **[Architecture](docs/technical/architecture.md)** - System design
- **[Deployment Checklist](docs/deployment/checklist.md)** - Production deployment

## ⚙️ Configuration

All configuration is managed through the `.env` file. Key settings:

```bash
# Database
DATABASE_PATH=business_leads.db

# Scraping
MAX_RESULTS_PER_JOB=50
HEADLESS_MODE=false

# Proxy (optional - auto-detected)
PROXIES_FILE=proxies.txt

# Server
HOST=0.0.0.0
PORT=8000
```

See [`.env.example`](.env.example) for all available options.

## 🔒 Proxy Support

The scraper includes smart proxy management:

- **Auto-detection** - Checks for `proxies.txt` automatically
- **Works with or without proxies** - No code changes needed
- **Rotation & health tracking** - Skips failed proxies
- **Multiple formats supported** - `ip:port:user:pass`, `http://user:pass@ip:port`

**To use proxies:**
1. Create `proxies.txt` in project root
2. Add proxies (one per line)
3. Run scraper - proxies automatically detected!

**To disable proxies:**
- Delete or rename `proxies.txt`

See [Smart Proxy Guide](docs/guides/proxy-setup.md) for details.

## 📁 Project Structure

```
business-scraper/
├── config.py              # Configuration management
├── proxy_manager.py       # Smart proxy system
├── database_manager.py    # Database operations
├── google_maps_scraper.py # Main scraper
├── app.py                 # FastAPI application
├── .env                   # Environment configuration
├── .env.example           # Configuration template
├── docs/                  # Documentation
│   ├── guides/            # User guides
│   ├── technical/         # Technical docs
│   └── deployment/        # Deployment guides
└── templates/             # Web templates
```

## 🧪 Development

```bash
# Run tests
pytest

# Format code
black .

# Lint code
ruff check .

# Type check
mypy .
```

## 📊 Tech Stack

- **Backend**: FastAPI, Pydantic
- **Scraping**: Playwright
- **Database**: SQLite
- **Export**: Pandas, ReportLab
- **Config**: Pydantic Settings, python-dotenv

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read the documentation first.

---

**Professional product ready for production use** 🚀
