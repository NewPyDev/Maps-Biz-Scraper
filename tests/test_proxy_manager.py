"""Tests for proxy manager module"""

import pytest
from pathlib import Path
from proxy_manager import SmartProxyManager, ProxyConfig


def test_proxy_config_creation():
    """Test creating proxy configuration"""
    proxy = ProxyConfig("1.2.3.4", "8080", "user", "pass")

    assert proxy.host == "1.2.3.4"
    assert proxy.port == "8080"
    assert proxy.username == "user"
    assert proxy.password == "pass"


def test_proxy_config_to_playwright():
    """Test proxy config conversion to Playwright format"""
    proxy = ProxyConfig("1.2.3.4", "8080", "user", "pass")
    config = proxy.to_playwright_config()

    assert config["server"] == "http://1.2.3.4:8080"
    assert config["username"] == "user"
    assert config["password"] == "pass"


def test_proxy_config_without_auth():
    """Test proxy config without authentication"""
    proxy = ProxyConfig("1.2.3.4", "8080")
    config = proxy.to_playwright_config()

    assert config["server"] == "http://1.2.3.4:8080"
    assert "username" not in config
    assert "password" not in config


def test_proxy_config_string_representation():
    """Test proxy string representation"""
    proxy_with_auth = ProxyConfig("1.2.3.4", "8080", "user", "pass")
    proxy_without_auth = ProxyConfig("1.2.3.4", "8080")

    assert str(proxy_with_auth) == "user:***@1.2.3.4:8080"
    assert str(proxy_without_auth) == "1.2.3.4:8080"


def test_proxy_manager_no_file():
    """Test proxy manager with missing file"""
    manager = SmartProxyManager("nonexistent_file.txt")

    assert not manager.has_proxies()
    assert len(manager.proxies) == 0
    assert manager.get_next_proxy() is None


def test_proxy_manager_with_file(temp_proxy_file):
    """Test proxy manager with valid proxy file"""
    manager = SmartProxyManager(str(temp_proxy_file))

    assert manager.has_proxies()
    assert len(manager.proxies) == 3


def test_proxy_manager_rotation(temp_proxy_file):
    """Test proxy rotation"""
    manager = SmartProxyManager(str(temp_proxy_file))

    proxy1 = manager.get_next_proxy()
    proxy2 = manager.get_next_proxy()
    proxy3 = manager.get_next_proxy()
    proxy4 = manager.get_next_proxy()  # Should rotate back to first

    assert proxy1 is not None
    assert proxy2 is not None
    assert proxy3 is not None
    assert proxy4 is not None

    # After 3 proxies, should rotate back
    assert str(proxy1) == str(proxy4)


def test_proxy_manager_failure_tracking(temp_proxy_file):
    """Test proxy failure tracking"""
    manager = SmartProxyManager(str(temp_proxy_file), max_failures=2)

    proxy = manager.get_next_proxy()
    assert proxy is not None

    # Mark as failed twice
    manager.mark_proxy_failure(proxy)
    manager.mark_proxy_failure(proxy)

    # Should skip this proxy now
    next_proxy = manager.get_next_proxy()
    assert str(next_proxy) != str(proxy)


def test_proxy_manager_success_resets_failures(temp_proxy_file):
    """Test that success resets failure count"""
    manager = SmartProxyManager(str(temp_proxy_file))

    proxy = manager.get_next_proxy()

    # Mark as failed
    manager.mark_proxy_failure(proxy)
    assert manager.proxy_failures.get(str(proxy), 0) == 1

    # Mark as success
    manager.mark_proxy_success(proxy)
    assert manager.proxy_failures.get(str(proxy), 0) == 0


def test_proxy_manager_playwright_config(temp_proxy_file):
    """Test getting Playwright config"""
    manager = SmartProxyManager(str(temp_proxy_file))

    config = manager.get_playwright_config()

    assert config is not None
    assert "server" in config
    assert config["server"].startswith("http://")


def test_proxy_manager_no_proxies_returns_none():
    """Test that manager returns None when no proxies available"""
    manager = SmartProxyManager("nonexistent.txt")

    config = manager.get_playwright_config()
    assert config is None
