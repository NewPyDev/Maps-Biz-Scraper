"""Pytest configuration and fixtures"""

import pytest
from pathlib import Path
from typing import Dict
from config import Settings


@pytest.fixture
def test_settings():
    """Test configuration with safe defaults"""
    return Settings(
        database_path=Path(":memory:"),
        proxies_file=Path("test_proxies.txt"),
        max_results_per_job=10,
        headless_mode=True,
        log_level="DEBUG",
    )


@pytest.fixture
def sample_business() -> Dict[str, str]:
    """Sample business data for testing"""
    return {
        "name": "Test Plumbing Co",
        "address": "123 Test St, Prague, Czech Republic",
        "phone": "+420123456789",
        "website": "https://testplumbing.cz",
        "has_website": "Yes",
        "maps_url": "https://maps.google.com/test",
        "scraped_date": "2026-02-09 22:00:00",
        "proxy_used": "No proxy",
    }


@pytest.fixture
def sample_proxy_list():
    """Sample proxy list for testing"""
    return [
        "1.2.3.4:8080:user1:pass1",
        "5.6.7.8:8080:user2:pass2",
        "http://user3:pass3@9.10.11.12:8080",
    ]


@pytest.fixture
def temp_proxy_file(tmp_path, sample_proxy_list):
    """Create temporary proxy file for testing"""
    proxy_file = tmp_path / "proxies.txt"
    proxy_file.write_text("\n".join(sample_proxy_list))
    return proxy_file
