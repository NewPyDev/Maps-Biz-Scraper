"""
Smart Proxy Manager for Playwright
Automatically detects and uses proxies if available, works without them if not
"""

from pathlib import Path
from typing import Optional, Dict, List
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """Proxy configuration"""

    host: str
    port: str
    username: Optional[str] = None
    password: Optional[str] = None

    def to_playwright_config(self) -> Dict:
        """Convert to Playwright proxy configuration"""
        config = {"server": f"http://{self.host}:{self.port}"}

        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password

        return config

    def __str__(self):
        if self.username:
            return f"{self.username}:***@{self.host}:{self.port}"
        return f"{self.host}:{self.port}"


class SmartProxyManager:
    """
    Smart proxy manager that:
    - Automatically detects proxies.txt
    - Uses proxies if available
    - Works normally without proxies
    - Rotates proxies automatically
    - Tracks proxy health
    """

    def __init__(self, proxy_file: Optional[str] = None, max_failures: Optional[int] = None):
        # Import config here to avoid circular imports
        try:
            from config import settings

            self.proxy_file = Path(proxy_file) if proxy_file else settings.proxies_file
            self.max_failures = (
                max_failures if max_failures is not None else settings.max_proxy_failures
            )
        except ImportError:
            # Fallback if config not available
            self.proxy_file = Path(proxy_file) if proxy_file else Path("proxies.txt")
            self.max_failures = max_failures if max_failures is not None else 3

        self.proxies = self._load_proxies()
        self.current_index = 0
        self.proxy_failures = {} # Track failures per proxy

    def reload_proxies(self):
        """Reload proxies from file"""
        self.proxies = self._load_proxies()
        self.current_index = 0
        self.proxy_failures = {}
        logger.info(f"Reloaded {len(self.proxies)} proxies from {self.proxy_file}")
        return len(self.proxies)

    def _load_proxies(self) -> List[ProxyConfig]:
        """Load proxies from file if it exists and return them"""
        loaded_proxies: List[ProxyConfig] = []
        if not self.proxy_file.exists():
            logger.info(f"No proxy file found at {self.proxy_file}. Running without proxies.")
            return loaded_proxies

        try:
            with open(self.proxy_file, "r") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            for line in lines:
                proxy = self._parse_proxy(line)
                if proxy:
                    loaded_proxies.append(proxy)

            if loaded_proxies:
                logger.info(f"✓ Loaded {len(loaded_proxies)} proxies from {self.proxy_file}")
            else:
                logger.warning(f"No valid proxies found in {self.proxy_file}")
                
            return loaded_proxies

        except Exception as e:
            logger.error(f"Error loading proxies: {e}")
            return loaded_proxies

    def _parse_proxy(self, line: str) -> Optional[ProxyConfig]:
        """
        Parse proxy from various formats:
        - ip:port:user:pass
        - http://user:pass@ip:port
        - ip:port
        """
        try:
            # Format: ip:port:user:pass
            if line.count(":") == 3 and not line.startswith(("http://", "https://")):
                host, port, username, password = line.split(":")
                return ProxyConfig(host, port, username, password)

            # Format: http://user:pass@ip:port
            elif "@" in line:
                line = line.replace("http://", "").replace("https://", "")
                auth, host_port = line.split("@")
                username, password = auth.split(":")
                host, port = host_port.split(":")
                return ProxyConfig(host, port, username, password)

            # Format: ip:port
            elif line.count(":") == 1:
                host, port = line.split(":")
                return ProxyConfig(host, port)

            else:
                logger.warning(f"Invalid proxy format: {line}")
                return None

        except Exception as e:
            logger.error(f"Error parsing proxy '{line}': {e}")
            return None

    def has_proxies(self) -> bool:
        """Check if proxies are available"""
        return len(self.proxies) > 0

    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """
        Get next working proxy, or None if no proxies available
        Automatically skips failed proxies
        """
        if not self.has_proxies():
            return None

        # Try to find a working proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index % len(self.proxies)]
            proxy_str = str(proxy)

            # Skip if proxy has failed too many times
            if self.proxy_failures.get(proxy_str, 0) >= self.max_failures:
                logger.debug(f"Skipping failed proxy: {proxy_str}")
                self.current_index += 1
                attempts += 1
                continue

            self.current_index += 1
            return proxy

        # All proxies have failed
        logger.warning("All proxies have failed. Running without proxy.")
        return None

    def mark_proxy_success(self, proxy: ProxyConfig):
        """Mark proxy as successful (reset failure count)"""
        proxy_str = str(proxy)
        if proxy_str in self.proxy_failures:
            del self.proxy_failures[proxy_str]

    def mark_proxy_failure(self, proxy: ProxyConfig):
        """Mark proxy as failed"""
        proxy_str = str(proxy)
        self.proxy_failures[proxy_str] = self.proxy_failures.get(proxy_str, 0) + 1
        logger.warning(
            f"Proxy failed ({self.proxy_failures[proxy_str]}/{self.max_failures}): {proxy_str}"
        )

    def get_playwright_config(self) -> Optional[Dict]:
        """
        Get Playwright proxy configuration
        Returns None if no proxies available (Playwright will work without proxy)
        """
        proxy = self.get_next_proxy()
        if proxy:
            logger.info(f"Using proxy: {proxy}")
            return proxy.to_playwright_config()
        else:
            logger.info("No proxy available. Running without proxy.")
            return None


# Global instance for easy access
_proxy_manager = None


def get_proxy_manager(proxy_file: str = "proxies.txt") -> SmartProxyManager:
    """Get or create the global proxy manager instance"""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = SmartProxyManager(proxy_file)
    return _proxy_manager


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create proxy manager
    manager = SmartProxyManager()

    print(f"\nProxies available: {manager.has_proxies()}")
    print(f"Number of proxies: {len(manager.proxies)}")

    if manager.has_proxies():
        # Get proxy config for Playwright
        config = manager.get_playwright_config()
        print(f"\nPlaywright config: {config}")

        # Simulate using multiple proxies
        for i in range(3):
            proxy = manager.get_next_proxy()
            if proxy:
                print(f"Proxy {i+1}: {proxy}")
    else:
        print("\nNo proxies configured. Application will work without proxies.")
