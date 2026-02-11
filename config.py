"""
Application Configuration
Centralized configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration with environment variable support."""

    # Database
    database_path: Path = Path("business_leads.db")

    # Scraping Configuration
    max_results_per_job: int = 50
    headless_mode: bool = False
    scroll_pause_min: int = 2
    scroll_pause_max: int = 5
    request_delay_min: int = 3
    request_delay_max: int = 7

    # Proxy Configuration
    proxies_file: Path = Path("proxies.txt")
    rotate_proxy_after: int = 10
    max_proxy_failures: int = 3

    # Timeouts
    page_load_timeout: int = 45
    element_wait_timeout: int = 15
    job_timeout_seconds: int = 1800

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Logging Configuration
    log_level: str = "INFO"
    log_file: Path = Path("logs/scraper.log")
    log_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_backup_count: int = 5

    # Export Configuration
    export_dir: Path = Path("exports")

    # Security
    admin_username: str
    admin_password: str
    require_auth: bool
    secret_key: str

    # Debug / Extra
    debug: bool = False
    stuck_threshold_seconds: int = 600

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False, "extra": "ignore"}


# Global settings instance
settings = Settings()


# Helper function to ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    settings.export_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Test configuration
    print("Configuration loaded successfully!")
    print(f"Database: {settings.database_path}")
    print(f"Proxies file: {settings.proxies_file}")
    print(f"Server: {settings.host}:{settings.port}")
    print(f"Log level: {settings.log_level}")
    print(f"Headless mode: {settings.headless_mode}")
