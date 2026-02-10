"""
Google Maps Business Scraper using Playwright
Integrates with Smart Proxy Manager and centralized configuration
"""

import random
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict
from playwright.sync_api import sync_playwright, Page
import pandas as pd

from config import settings, ensure_directories
from proxy_manager import get_proxy_manager
from logging_config import setup_logging

# Setup logging with rotation
setup_logging()
logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Google Maps business scraper using Playwright"""

    def __init__(self):
        self.proxy_manager = get_proxy_manager()
        self.businesses = []
        self.current_proxy = None

    def scrape(
        self, category: str, city: str, country: str = "", max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Scrape businesses from Google Maps

        Args:
            category: Business category (e.g., "plumbers", "dentists")
            city: City name
            country: Country name (optional)
            max_results: Maximum results to scrape (uses config default if None)

        Returns:
            List of business dictionaries
        """
        max_results = max_results or settings.max_results_per_job
        search_query = f"{category} in {city}"
        if country:
            search_query += f", {country}"

        logger.info(f"Starting scrape: {search_query}")
        logger.info(f"Target: {max_results} results")
        logger.info(f"Headless mode: {settings.headless_mode}")

        max_proxy_retries = 5  # Try up to 5 different proxies per job

        for attempt in range(max_proxy_retries + 1):  # +1 for final no-proxy attempt
            try:
                with sync_playwright() as playwright:
                    # Get a single proxy for this attempt
                    self.current_proxy = None
                    proxy_config = None
                    
                    if attempt < max_proxy_retries:
                        proxy = self.proxy_manager.get_next_proxy()
                        if proxy:
                            self.current_proxy = proxy
                            proxy_config = proxy.to_playwright_config()
                            logger.info(f"Using proxy (attempt {attempt + 1}/{max_proxy_retries}): {proxy}")
                        else:
                            logger.info("No working proxy available. Trying without proxy.")
                    else:
                        logger.info(f"Attempt {attempt + 1}: Trying WITHOUT proxy")

                    # Build launch options
                    launch_options = {
                        "headless": settings.headless_mode,
                        "args": [
                            "--disable-blink-features=AutomationControlled",
                            "--disable-dev-shm-usage",
                            "--no-sandbox",
                        ],
                    }
                    if proxy_config:
                        launch_options["proxy"] = proxy_config

                    browser = playwright.chromium.launch(**launch_options)

                    context = browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    )
                    page = context.new_page()
                    page.set_default_timeout(settings.page_load_timeout * 1000)

                    # Navigate to Google Maps
                    logger.info("Navigating to Google Maps...")
                    page.goto("https://www.google.com/maps", wait_until="domcontentloaded", timeout=60000)

                    time.sleep(random.uniform(3, 5))
                    
                    # Handle Consent
                    self._handle_consent(page)

                    # Search for businesses
                    logger.info(f"Searching for: {search_query}")
                    
                    # Google Maps search box selectors (ordered by reliability)
                    # Google removed 'searchboxinput' ID in 2026 - input[name='q'] is now primary
                    search_selectors = [
                        "input[name='q']",
                        "input[role='combobox']",
                        "input[id='searchboxinput']",
                    ]
                    
                    search_box = None
                    for selector in search_selectors:
                        try:
                            logger.info(f"Trying search selector: {selector}")
                            candidate = page.locator(selector).first
                            candidate.wait_for(state="visible", timeout=10000)
                            search_box = candidate
                            logger.info(f"✅ Found search box with: {selector}")
                            break
                        except Exception:
                            logger.debug(f"Selector {selector} not found, trying next...")
                    
                    if search_box is None:
                        # Save debug info
                        timestamp = int(time.time())
                        page.screenshot(path=f"debug_error_search_{timestamp}.png")
                        logger.info(f"📸 Saved debug screenshot")
                        with open("debug_page.html", "w", encoding="utf-8") as f:
                            f.write(page.content())
                        logger.info(f"📄 Saved debug HTML")
                        raise Exception("Search box not found with any selector")
                    
                    try:
                        search_box.click()
                        time.sleep(1)
                        search_box.fill(search_query)
                        time.sleep(1)
                        search_box.press("Enter")
                    except Exception as e:
                        logger.error(f"Failed to interact with search box: {e}")
                        raise

                    # Wait for results to load
                    time.sleep(random.uniform(3, 5))

                    # Scroll and extract businesses
                    self.businesses = []
                    self._scroll_and_extract(page, max_results)

                    logger.info(f"✅ Scraped {len(self.businesses)} businesses")

                    # Mark proxy as successful if used
                    if self.current_proxy:
                        self.proxy_manager.mark_proxy_success(self.current_proxy)

                    browser.close()
                    return self.businesses

            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")

                # Mark proxy as failed
                if self.current_proxy:
                    self.proxy_manager.mark_proxy_failure(self.current_proxy)

                # If we have more retries, continue to next proxy
                if attempt < max_proxy_retries:
                    logger.info(f"🔄 Retrying with a different proxy...")
                    time.sleep(2)  # Brief pause before retry
                    continue
                else:
                    logger.error(f"❌ All {max_proxy_retries + 1} attempts failed. Giving up on this job.")
                    raise


    def _scroll_and_extract(self, page: Page, max_results: int):
        """Scroll through results and extract business data"""
        try:
            # Wait for results panel
            page.wait_for_selector("div[role='feed']", timeout=10000)

            previous_card_count = 0
            no_new_results_count = 0
            seen_names = set()

            while len(self.businesses) < max_results:
                # Get all potential business cards
                business_cards = page.locator("div[role='feed'] > div > div").all()

                logger.info(
                    f"Found {len(business_cards)} cards, extracted {len(self.businesses)} businesses so far..."
                )

                # Extract data from new cards (use card count for pagination, not business count)
                for card in business_cards[previous_card_count:]:
                    if len(self.businesses) >= max_results:
                        break

                    try:
                        business_data = self._extract_business_data(page, card)
                        if business_data:
                            biz_name = business_data.get("name", "")
                            # Skip duplicates by name
                            if biz_name in seen_names:
                                logger.debug(f"Skipping duplicate: {biz_name}")
                                continue
                            seen_names.add(biz_name)
                            self.businesses.append(business_data)
                            logger.info(
                                f"  [{len(self.businesses)}/{max_results}] {business_data['name']}"
                            )
                    except Exception as e:
                        logger.debug(f"Error extracting business: {e}")
                        continue

                # Check if we got new cards
                current_card_count = len(business_cards)
                if current_card_count == previous_card_count:
                    no_new_results_count += 1
                    if no_new_results_count >= 3:
                        logger.warning("No new results after 3 scrolls, stopping")
                        break
                else:
                    no_new_results_count = 0

                previous_card_count = current_card_count

                # Scroll to load more results
                if len(self.businesses) < max_results:
                    self._scroll_results_panel(page)
                    time.sleep(random.uniform(settings.scroll_pause_min, settings.scroll_pause_max))

        except Exception as e:
            logger.error(f"Error during scroll and extract: {e}")

    def _scroll_results_panel(self, page: Page):
        """Scroll the results panel to load more businesses"""
        try:
            page.evaluate("""
                const feed = document.querySelector('div[role="feed"]');
                if (feed) {
                    feed.scrollTo(0, feed.scrollHeight);
                }
            """)
        except Exception as e:
            logger.debug(f"Scroll error: {e}")

    def _extract_business_data(self, page: Page, card) -> Optional[Dict]:
        """Extract data from a business card"""
        try:
            # Get card text
            card_text = card.inner_text()

            # Skip if this is not a business card
            if not card_text or len(card_text) < 10:
                return None

            # Extract business name (usually first line)
            lines = card_text.split("\n")
            name = lines[0].strip() if lines else "N/A"

            # Skip ads, non-business entries, and UI elements
            skip_keywords = [
                "ad",
                "sponsored",
                "google",
                "résultats",
                "results",
                "certains de ces",
                "les prix sont",
                "partager",
            ]
            if any(skip in name.lower() for skip in skip_keywords):
                logger.debug(f"Skipping non-business card: {name}")
                return None

            # Skip if the card contains info/disclaimer text
            if (
                "personnalisés" in card_text.lower()
                or "partenaires de google" in card_text.lower()
                or "envoyer un lien" in card_text.lower()
            ):
                logger.debug(f"Skipping info/disclaimer card")
                return None

            # Check if this card has a business link (to avoid clicking share buttons, etc.)
            try:
                has_business_link = card.locator("a[href*='/maps/place/']").count() > 0
                if not has_business_link:
                    logger.debug(f"Skipping card without business link: {name}")
                    return None
            except Exception:
                pass

            # Try to click the card to get more details
            try:
                # Click on the business link specifically, not the card container
                business_link = card.locator("a[href*='/maps/place/']").first
                if business_link.is_visible(timeout=1000):
                    business_link.click(timeout=2000)
                    # Wait for detail panel to fully load (website button loads last)
                    time.sleep(random.uniform(4, 6))
                else:
                    logger.debug(f"Business link not visible for {name}")
                    return None
            except Exception as e:
                logger.debug(f"Could not click card for {name}: {e}")
                return None

            # Initialize business data
            business_data = {
                "name": name,
                "address": "N/A",
                "phone": "N/A",
                "website": "N/A",
                "has_website": "No",
                "maps_url": page.url,
                "scraped_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "proxy_used": str(self.current_proxy) if self.current_proxy else "No proxy",
            }

            # Wait for detail panel to be fully visible
            try:
                page.wait_for_selector("div[role='main']", timeout=5000)
                # Extra wait for action buttons (website/phone/etc) to render
                page.wait_for_selector("div[role='main'] button", timeout=3000)
            except Exception:
                logger.debug(f"Detail panel not fully loaded for {name}")

            # Extract address - try multiple methods
            try:
                # Method 1: Button with data-item-id='address'
                address_button = page.locator("button[data-item-id='address']").first
                if address_button.is_visible(timeout=2000):
                    aria_label = address_button.get_attribute("aria-label")
                    if aria_label:
                        # Remove common prefixes
                        for prefix in ["Address: ", "Adresse: ", "Dirección: ", "Adresa: "]:
                            aria_label = aria_label.replace(prefix, "")
                        business_data["address"] = aria_label.strip()
                        logger.debug(f"Address found (method 1): {business_data['address']}")
            except Exception as e:
                logger.debug(f"Address method 1 failed: {e}")

            # Method 2: Look for address in aria-label of buttons
            if business_data["address"] == "N/A":
                try:
                    buttons = page.locator(
                        "button[aria-label*='Address'], button[aria-label*='Adresa']"
                    ).all()
                    for btn in buttons:
                        aria = btn.get_attribute("aria-label")
                        if aria and len(aria) > 15:  # Address should be reasonably long
                            for prefix in ["Address: ", "Adresse: ", "Dirección: ", "Adresa: "]:
                                aria = aria.replace(prefix, "")
                            business_data["address"] = aria.strip()
                            logger.debug(f"Address found (method 2): {business_data['address']}")
                            break
                except Exception as e:
                    logger.debug(f"Address method 2 failed: {e}")

            # Extract phone - try multiple methods
            phone_prefixes = [
                "Phone: ",
                "Téléphone: ",
                "Tel: ",
                "Telefon: ",
                "Numéro de téléphone : ",
                "Numéro de téléphone: ",
                "Telefonnummer: ",
                "Número de teléfono: ",
                "Teléfono: ",
                "Telefone: ",
            ]
            try:
                # Method 1: Button with phone data-item-id
                phone_button = page.locator("button[data-item-id*='phone']").first
                if phone_button.is_visible(timeout=2000):
                    aria_label = phone_button.get_attribute("aria-label")
                    if aria_label:
                        for prefix in phone_prefixes:
                            aria_label = aria_label.replace(prefix, "")
                        # Only accept if it looks like a phone number
                        cleaned = aria_label.strip()
                        if any(c.isdigit() for c in cleaned):
                            business_data["phone"] = cleaned
                            logger.debug(f"Phone found (method 1): {business_data['phone']}")
            except Exception as e:
                logger.debug(f"Phone method 1 failed: {e}")

            # Method 2: Look for phone in aria-labels
            if business_data["phone"] == "N/A":
                try:
                    buttons = page.locator(
                        "button[aria-label*='Phone'], button[aria-label*='Telefon'], button[aria-label*='téléphone'], button[aria-label*='Numéro']"
                    ).all()
                    for btn in buttons:
                        aria = btn.get_attribute("aria-label")
                        if aria:
                            import re
                            if re.search(r"[\d\s\-\+\(\)]{9,}", aria):
                                for prefix in phone_prefixes:
                                    aria = aria.replace(prefix, "")
                                cleaned = aria.strip()
                                if any(c.isdigit() for c in cleaned):
                                    business_data["phone"] = cleaned
                                    logger.debug(
                                        f"Phone found (method 2): {business_data['phone']}"
                                    )
                                    break
                except Exception as e:
                    logger.debug(f"Phone method 2 failed: {e}")

            # Method 3: Look for phone in text content of detail panel
            if business_data["phone"] == "N/A":
                try:
                    import re
                    detail_panel = page.locator("div[role='main']").first
                    if detail_panel.is_visible(timeout=1000):
                        panel_text = detail_panel.inner_text()
                        phone_patterns = [
                            r"\+\d{1,4}\s?\d{3}\s?\d{3}\s?\d{3,4}",
                            r"\d{3}\s?\d{3}\s?\d{3,4}",
                        ]
                        for pattern in phone_patterns:
                            matches = re.findall(pattern, panel_text)
                            if matches:
                                business_data["phone"] = matches[0].strip()
                                logger.debug(f"Phone found (method 3): {business_data['phone']}")
                                break
                except Exception as e:
                    logger.debug(f"Phone method 3 failed: {e}")

            # ─── Extract website - MULTIPLE METHODS ─────────────────
            import re

            # Method 1: Primary selector - data-item-id='authority'
            try:
                website_link = page.locator("a[data-item-id='authority']").first
                if website_link.is_visible(timeout=3000):
                    href = website_link.get_attribute("href")
                    if href and href.startswith("http"):
                        business_data["website"] = href
                        business_data["has_website"] = "Yes"
                        logger.debug(f"Website found (method 1): {href}")
            except Exception as e:
                logger.debug(f"Website method 1 failed: {e}")

            # Method 2: Look for links with aria-label containing 'website'
            if business_data["has_website"] == "No":
                try:
                    website_selectors = [
                        "a[aria-label*='Website']",
                        "a[aria-label*='website']",
                        "a[aria-label*='Site Web']",
                        "a[aria-label*='site web']",
                        "a[aria-label*='Webová stránka']",
                        "a[aria-label*='Webseite']",
                        "a[aria-label*='Sitio web']",
                        "a[aria-label*='Site internet']",
                    ]
                    for sel in website_selectors:
                        try:
                            link = page.locator(sel).first
                            if link.is_visible(timeout=500):
                                href = link.get_attribute("href")
                                if href and href.startswith("http") and "google.com" not in href:
                                    business_data["website"] = href
                                    business_data["has_website"] = "Yes"
                                    logger.debug(f"Website found (method 2): {href}")
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"Website method 2 failed: {e}")

            # Method 3: Scan all action buttons in detail panel for website icon/text
            if business_data["has_website"] == "No":
                try:
                    # Google Maps uses action buttons, website is one of them
                    action_links = page.locator("div[role='main'] a[href^='http']").all()
                    for link in action_links:
                        try:
                            href = link.get_attribute("href")
                            aria = link.get_attribute("aria-label") or ""
                            # Skip Google's own links
                            if not href or any(skip in href for skip in [
                                "google.com", "goo.gl", "maps.app", "play.google",
                                "support.google", "accounts.google", "policies.google"
                            ]):
                                continue
                            # Skip social media and known non-website links
                            if any(skip in href for skip in [
                                "facebook.com", "instagram.com", "twitter.com",
                                "youtube.com", "linkedin.com", "tiktok.com"
                            ]):
                                continue
                            # If aria-label mentions website or the link is a business URL
                            if ("website" in aria.lower() or "web" in aria.lower()
                                    or "site" in aria.lower()):
                                business_data["website"] = href
                                business_data["has_website"] = "Yes"
                                logger.debug(f"Website found (method 3, aria): {href}")
                                break
                            # Accept if it looks like a real external business URL
                            if href.startswith("http") and "." in href:
                                business_data["website"] = href
                                business_data["has_website"] = "Yes"
                                logger.debug(f"Website found (method 3, link): {href}")
                                break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"Website method 3 failed: {e}")

            # Method 4: Check all buttons with aria-labels for website info
            if business_data["has_website"] == "No":
                try:
                    all_buttons = page.locator("div[role='main'] button[aria-label]").all()
                    for btn in all_buttons:
                        try:
                            aria = btn.get_attribute("aria-label") or ""
                            aria_lower = aria.lower()
                            # Check if button mentions a website
                            if any(kw in aria_lower for kw in [
                                "website", "site web", "webová stránka",
                                "webseite", "sitio web", "site internet", "sito web"
                            ]):
                                # The aria-label often contains the URL
                                url_match = re.search(r'https?://[^\s,]+', aria)
                                if url_match:
                                    business_data["website"] = url_match.group()
                                    business_data["has_website"] = "Yes"
                                    logger.debug(f"Website found (method 4, button): {url_match.group()}")
                                    break
                                # Sometimes just the domain name is in the aria-label
                                domain_match = re.search(r'([a-zA-Z0-9-]+\.[a-z]{2,})', aria)
                                if domain_match and domain_match.group() not in ['google.com', 'maps.app']:
                                    business_data["website"] = f"https://{domain_match.group()}"
                                    business_data["has_website"] = "Yes"
                                    logger.debug(f"Website found (method 4, domain): {domain_match.group()}")
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"Website method 4 failed: {e}")

            # Method 5: Last resort - check visible text for website URL patterns
            if business_data["has_website"] == "No":
                try:
                    detail_panel = page.locator("div[role='main']").first
                    if detail_panel.is_visible(timeout=1000):
                        panel_text = detail_panel.inner_text()
                        # Look for URL patterns in the text
                        url_patterns = [
                            r'(https?://[^\s<>"]+)',
                            r'(www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*)',
                        ]
                        for pattern in url_patterns:
                            matches = re.findall(pattern, panel_text)
                            for match in matches:
                                if not any(skip in match for skip in [
                                    'google.com', 'goo.gl', 'maps.app'
                                ]):
                                    if match.startswith("www."):
                                        match = f"https://{match}"
                                    business_data["website"] = match
                                    business_data["has_website"] = "Yes"
                                    logger.debug(f"Website found (method 5, text): {match}")
                                    break
                            if business_data["has_website"] == "Yes":
                                break
                except Exception as e:
                    logger.debug(f"Website method 5 failed: {e}")

            if business_data["has_website"] == "Yes":
                logger.info(f"  ✅ Website: {business_data['website']}")
            else:
                logger.info(f"  ❌ No website found for: {name}")

            # Small delay before next extraction
            time.sleep(random.uniform(settings.request_delay_min, settings.request_delay_max))

            return business_data

        except Exception as e:
            logger.debug(f"Error extracting business data: {e}")
            return None

    def save_to_csv(self, category: str, city: str) -> str:
        """Save scraped businesses to CSV - produces two files:
        1. All businesses (general file)
        2. Only businesses WITHOUT websites (filtered/premium file)
        """
        import pandas as pd

        if not self.businesses:
            logger.warning("No businesses to save")
            return ""

        # Create DataFrame
        df = pd.DataFrame(self.businesses)

        # Generate filename base
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{category}_{city}_{timestamp}"

        # File 1: All businesses
        all_filepath = settings.export_dir / f"{base_name}_ALL.csv"
        df.to_csv(all_filepath, index=False, encoding="utf-8-sig")
        logger.info(f"✅ Saved {len(df)} businesses to {all_filepath}")

        # File 2: Businesses WITHOUT websites only
        no_website_df = df[df["has_website"] == "No"]
        if len(no_website_df) > 0:
            no_website_filepath = settings.export_dir / f"{base_name}_NO_WEBSITE.csv"
            no_website_df.to_csv(no_website_filepath, index=False, encoding="utf-8-sig")
            logger.info(
                f"✅ Saved {len(no_website_df)} businesses WITHOUT websites to {no_website_filepath}"
            )
        else:
            logger.info("ℹ All businesses have websites - no filtered file created")

        # Summary
        with_website = len(df[df["has_website"] == "Yes"])
        without_website = len(no_website_df)
        logger.info(
            f"📊 Total: {len(df)} | With website: {with_website} | Without website: {without_website}"
        )

        return str(all_filepath)

    def _handle_consent(self, page):
        """Handle Google consent popup"""
        try:
            # Common consent buttons
            selectors = [
                # Keep list simple to match indentation
                "button[aria-label*='Accept all']",
                "button:has-text('Accept all')",
                "span:has-text('Accept all')",
                "form[action*='consent'] button",
                "button[jsname='b3VHJd']"
            ]
            for s in selectors:
                if page.locator(s).count() > 0 and page.locator(s).first.is_visible():
                    logger.info(f"Found consent button: {s}")
                    page.locator(s).first.click()
                    time.sleep(2)
                    return
        except Exception as e:
            logger.warning(f"Consent handling error: {e}")


def main(category: str, city: str, country: str = "", max_results: Optional[int] = None):
    """
    Main scraping function

    Args:
        category: Business category
        city: City name
        country: Country name (optional)
        max_results: Maximum results (uses config default if None)

    Returns:
        Path to CSV file
    """
    logger.info("=" * 60)
    logger.info("Google Maps Business Scraper - Playwright Edition")
    logger.info("=" * 60)

    scraper = GoogleMapsScraper()

    try:
        # Scrape businesses
        businesses = scraper.scrape(category, city, country, max_results)

        # Save to CSV
        csv_file = scraper.save_to_csv(category, city)

        logger.info("=" * 60)
        logger.info("✅ SCRAPING COMPLETE")
        logger.info(f"   Total businesses: {len(businesses)}")
        logger.info(f"   CSV file: {csv_file}")
        logger.info("=" * 60)

        return csv_file

    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    main(
        category="plumbers",
        city="Prague",
        country="Czech Republic",
        max_results=20,  # Small test run
    )
