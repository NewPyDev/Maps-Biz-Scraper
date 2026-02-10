"""Custom exceptions for Business Scraper"""


class ScraperException(Exception):
    """Base exception for scraper errors"""

    pass


class ProxyException(ScraperException):
    """Proxy-related errors"""

    pass


class DatabaseException(ScraperException):
    """Database-related errors"""

    pass


class ExtractionException(ScraperException):
    """Data extraction errors"""

    pass


class ConfigurationException(ScraperException):
    """Configuration-related errors"""

    pass
