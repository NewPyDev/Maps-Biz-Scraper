"""Tests for configuration module"""

import pytest
from pathlib import Path
from config import Settings


def test_default_settings():
    """Test default configuration values"""
    settings = Settings()

    assert settings.database_path == Path("business_leads.db")
    assert settings.max_results_per_job == 50
    assert settings.headless_mode == False
    assert settings.port == 8000
    assert settings.host == "0.0.0.0"
    assert settings.log_level == "INFO"


def test_custom_settings():
    """Test custom configuration"""
    settings = Settings(max_results_per_job=100, headless_mode=True, port=9000)

    assert settings.max_results_per_job == 100
    assert settings.headless_mode == True
    assert settings.port == 9000


def test_settings_from_fixture(test_settings):
    """Test using settings fixture"""
    assert test_settings.database_path == Path(":memory:")
    assert test_settings.max_results_per_job == 10
    assert test_settings.headless_mode == True


def test_timeout_settings():
    """Test timeout configuration"""
    settings = Settings()

    assert settings.page_load_timeout == 45
    assert settings.element_wait_timeout == 15
    assert settings.job_timeout_seconds == 1800


def test_proxy_settings():
    """Test proxy configuration"""
    settings = Settings()

    assert settings.proxies_file == Path("proxies.txt")
    assert settings.rotate_proxy_after == 10
    assert settings.max_proxy_failures == 3
