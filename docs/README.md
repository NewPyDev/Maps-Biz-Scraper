# Documentation Index

Welcome to the Business Scraper documentation!

## Quick Links

- [Getting Started](../README.md#quick-start) - Set up and run the scraper
- [Dashboard Guide](guides/dashboard.md) - Using the web dashboard
- [Configuration](../README.md#configuration) - Environment variables and settings

## Guides

### User Guides
- **[Dashboard Guide](guides/dashboard.md)** - Complete dashboard usage guide
- **[CSV Import Guide](guides/csv-import.md)** - Bulk job import from CSV
- **[PDF Generation Guide](guides/pdf-generation.md)** - Export data to PDF

### Technical Guides
- **[Architecture Overview](technical/architecture.md)** - System design and components
- **[Scraping Strategy](technical/scraping-strategy.md)** - How the scraper works

## Deployment

- **[Deployment Checklist](deployment/checklist.md)** - Pre-deployment checklist

## Business

- **[Business Plan](business-plan.md)** - Business strategy and monetization

---

## Project Structure

```
business-scraper/
├── config.py              # Configuration management
├── proxy_manager.py       # Smart proxy system
├── database_manager.py    # Database operations
├── google_maps_scraper.py # Main scraper
├── app.py                 # FastAPI application
├── .env                   # Environment configuration
└── docs/                  # Documentation (you are here)
    ├── guides/            # User guides
    ├── technical/         # Technical documentation
    └── deployment/        # Deployment guides
```

## Configuration

All configuration is managed through the `.env` file. See [`.env.example`](../.env.example) for all available options.

Key settings:
- `DATABASE_PATH` - SQLite database location
- `PROXIES_FILE` - Proxy list file
- `MAX_RESULTS_PER_JOB` - Results per scraping job
- `HEADLESS_MODE` - Run browser in headless mode
- `LOG_LEVEL` - Logging verbosity

## Support

For issues or questions, check the relevant guide above or review the code documentation.
