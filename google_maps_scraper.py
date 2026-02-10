"""
Google Maps Business Scraper with Proxy Support
Scrapes business data from Google Maps with rotating proxies
"""

import time
import random
import logging
import pandas as pd
import os
import zipfile
import re
from datetime import datetime
from seleniumwire import webdriver  # Changed to seleniumwire for proxy support
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Fix console encoding for Windows
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
]


def load_proxies_from_file(filename='proxies.txt'):
    """
    Load proxies from proxies.txt file
    Supports multiple formats:
    - http://ip:port
    - http://user:pass@ip:port
    - ip:port:user:pass
    - ip:port
    Returns list of proxy dictionaries with parsed components
    """
    try:
        with open(filename, 'r') as f:
            raw_proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        proxies = []
        for proxy in raw_proxies:
            # Skip empty lines and comments
            if not proxy or proxy.startswith('#'):
                continue
            
            proxy_dict = {'raw': proxy, 'host': None, 'port': None, 'user': None, 'pass': None, 'scheme': 'http'}
            
            # Handle ip:port:user:pass format (most common for your case)
            if proxy.count(':') == 3 and not proxy.startswith(('http://', 'https://', 'socks5://')):
                parts = proxy.split(':')
                proxy_dict['host'] = parts[0]
                proxy_dict['port'] = parts[1]
                proxy_dict['user'] = parts[2]
                proxy_dict['pass'] = parts[3]
                proxies.append(proxy_dict)
            # Handle http://user:pass@ip:port format
            elif '@' in proxy:
                if proxy.startswith('http://'):
                    proxy_dict['scheme'] = 'http'
                    proxy = proxy.replace('http://', '')
                elif proxy.startswith('https://'):
                    proxy_dict['scheme'] = 'https'
                    proxy = proxy.replace('https://', '')
                elif proxy.startswith('socks5://'):
                    proxy_dict['scheme'] = 'socks5'
                    proxy = proxy.replace('socks5://', '')
                
                auth, host_port = proxy.split('@')
                proxy_dict['user'], proxy_dict['pass'] = auth.split(':')
                proxy_dict['host'], proxy_dict['port'] = host_port.split(':')
                proxies.append(proxy_dict)
            # Handle ip:port format (no auth)
            elif proxy.count(':') == 1:
                parts = proxy.replace('http://', '').replace('https://', '').split(':')
                proxy_dict['host'] = parts[0]
                proxy_dict['port'] = parts[1]
                proxies.append(proxy_dict)
            else:
                logging.warning(f"Skipping invalid proxy format: {proxy}")
        
        logging.info(f"Loaded {len(proxies)} proxies from {filename}")
        return proxies
    except FileNotFoundError:
        logging.warning(f"{filename} not found. Running without proxies.")
        return []
    except Exception as e:
        logging.error(f"Error loading proxies: {e}")
        return []


def create_proxy_extension(proxy_dict):
    """
    Create a Chrome extension for authenticated proxy
    NOTE: This function is NO LONGER NEEDED with selenium-wire!
    Keeping it for reference only.
    """
    # NOT USED ANYMORE - selenium-wire handles proxies properly
    return None
    if not proxy_dict or not proxy_dict.get('user'):
        return None
    
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "%s",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_dict['scheme'], proxy_dict['host'], proxy_dict['port'], proxy_dict['user'], proxy_dict['pass'])

    plugin_path = 'proxy_auth_plugin.zip'
    
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    
    return plugin_path


def setup_driver(proxy_dict=None):
    """
    Configure Selenium-Wire WebDriver with proxy and anti-detection measures
    Selenium-Wire properly handles authenticated proxies!
    """
    try:
        # Chrome options
        options = webdriver.ChromeOptions()
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images and CSS for faster loading
        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'profile.managed_default_content_settings.stylesheets': 2
        }
        options.add_experimental_option('prefs', prefs)
        
        # Random user agent
        user_agent = random.choice(USER_AGENTS)
        options.add_argument(f'user-agent={user_agent}')
        
        # Selenium-Wire proxy configuration (supports authentication!)
        seleniumwire_options = {}
        
        if proxy_dict:
            # Build proxy URL in format: http://user:pass@host:port
            if proxy_dict.get('user') and proxy_dict.get('pass'):
                proxy_url = f"http://{proxy_dict['user']}:{proxy_dict['pass']}@{proxy_dict['host']}:{proxy_dict['port']}"
                logging.info(f"✓ Configuring authenticated proxy: {proxy_dict['user']}:***@{proxy_dict['host']}:{proxy_dict['port']}")
            else:
                proxy_url = f"http://{proxy_dict['host']}:{proxy_dict['port']}"
                logging.info(f"✓ Configuring proxy: {proxy_dict['host']}:{proxy_dict['port']}")
            
            # Selenium-Wire proxy configuration
            seleniumwire_options = {
                'proxy': {
                    'http': proxy_url,
                    'https': proxy_url,
                    'no_proxy': 'localhost,127.0.0.1'
                },
                'verify_ssl': False,  # Disable SSL verification for proxies
                'suppress_connection_errors': False  # Show connection errors for debugging
            }
        
        # Create driver with selenium-wire options
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            service=service,
            options=options,
            seleniumwire_options=seleniumwire_options if proxy_dict else {}
        )
        
        # Apply stealth settings
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        driver.set_page_load_timeout(45)  # Increased timeout for proxy connections
        
        # Verify proxy is working
        if proxy_dict:
            try:
                logging.info("🔍 Verifying proxy connection...")
                driver.get("https://ipv4.webshare.io/")
                time.sleep(3)
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Check if our proxy IP is shown
                if proxy_dict['host'] in page_text:
                    logging.info(f"✅ PROXY VERIFIED! Traffic is going through {proxy_dict['host']}")
                    logging.info(f"   Response: {page_text[:100]}")
                else:
                    logging.warning(f"⚠️ Proxy verification unclear. Expected {proxy_dict['host']}")
                    logging.warning(f"   Got response: {page_text[:100]}")
                
                # Also check selenium-wire requests to confirm proxy usage
                if hasattr(driver, 'requests') and len(driver.requests) > 0:
                    logging.info(f"✓ Selenium-Wire captured {len(driver.requests)} request(s)")
                
            except Exception as e:
                logging.warning(f"⚠️ Proxy verification error: {e}")
                logging.warning("   Continuing anyway - proxy might still work for Google Maps")
        
        return driver
    
    except Exception as e:
        logging.error(f"❌ Error setting up driver: {e}")
        raise


def search_google_maps(driver, category, city):
    """
    Navigate to Google Maps and search for businesses
    """
    try:
        search_query = f"{category} in {city}"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        logging.info(f"Searching: {search_query}")
        driver.get(url)
        
        # Wait for results to load
        time.sleep(random.uniform(3, 5))
        
        # Wait for search results container
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
        )
        
        return True
    
    except TimeoutException:
        logging.error("Timeout waiting for search results")
        return False
    except Exception as e:
        logging.error(f"Error during search: {e}")
        return False


def scroll_and_load_results(driver, max_results):
    """
    Scroll through results to load more businesses
    Returns list of business elements
    """
    businesses = []
    last_count = 0
    no_change_count = 0
    
    try:
        results_container = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
        
        while len(businesses) < max_results:
            # Find all business listings
            current_businesses = results_container.find_elements(
                By.CSS_SELECTOR, "div[role='article']"
            )
            
            if len(current_businesses) > last_count:
                businesses = current_businesses
                last_count = len(current_businesses)
                no_change_count = 0
                logging.info(f"Loaded {len(businesses)} businesses so far...")
            else:
                no_change_count += 1
            
            # Stop if no new results after 3 scrolls
            if no_change_count >= 3:
                logging.info("No more results found")
                break
            
            # Scroll to bottom
            driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                results_container
            )
            
            # Random delay
            time.sleep(random.uniform(1, 3))
        
        return businesses[:max_results]
    
    except Exception as e:
        logging.error(f"Error scrolling results: {e}")
        return businesses


def extract_business_data(driver, business_element, proxy_dict):
    """
    Extract data from a single business listing
    """
    proxy_str = f"{proxy_dict['host']}:{proxy_dict['port']}" if proxy_dict else 'No proxy'
    
    data = {
        'name': 'N/A',
        'address': 'N/A',
        'phone': 'N/A',
        'maps_url': 'N/A',
        'has_website': 'N/A',
        'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'proxy_used': proxy_str
    }
    
    try:
        # FIRST: Extract what we can from the list view (before clicking)
        try:
            # Get name and URL from the link
            name_link = business_element.find_element(By.CSS_SELECTOR, "a")
            data['name'] = name_link.get_attribute('aria-label')
            data['maps_url'] = name_link.get_attribute('href').split('?')[0]
        except:
            pass
        
        # Try to get phone from the list view (it's often visible there!)
        try:
            # Look for phone in the business card text
            card_text = business_element.text
            # Phone patterns: +34 xxx xx xx xx, +1 xxx xxx xxxx, etc.
            import re
            phone_pattern = r'\+?\d[\d\s\-\(\)]{8,}'
            phones = re.findall(phone_pattern, card_text)
            if phones:
                # Get the longest match (most likely to be complete)
                data['phone'] = max(phones, key=len).strip()
        except:
            pass
        
        # Try to get address from list view
        try:
            # Address is often in the card text too
            lines = business_element.text.split('\n')
            for line in lines:
                # Look for address-like patterns (contains comma or street indicators)
                if ',' in line or any(word in line.lower() for word in ['calle', 'street', 'rue', 'via', 'avenue', 'cl.', 'c.', 'av.']):
                    if len(line) > 10 and not line.startswith(('+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                        data['address'] = line.strip()
                        break
        except:
            pass
        
        # NOW click to get more details (website, better address/phone if missing)
        business_element.click()
        time.sleep(random.uniform(3, 5))
        
        # Wait for detail panel to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb"))
            )
        except:
            logging.warning("Detail panel did not load")
        
        time.sleep(2)  # Extra wait for content to populate
        
        # Extract address if we don't have it yet
        if data['address'] == 'N/A':
            try:
                # Method 1: Look for address button with data-item-id
                address_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id='address']")
                if address_buttons:
                    aria_label = address_buttons[0].get_attribute('aria-label')
                    if aria_label:
                        # Remove language-specific prefixes
                        for prefix in ['Address: ', 'Adresse : ', 'Adresse: ', 'Dirección: ', 'Indirizzo: ', 'Adresa: ']:
                            aria_label = aria_label.replace(prefix, '')
                        data['address'] = aria_label.strip()
                
                # Method 2: Look in all buttons for address-like content
                if data['address'] == 'N/A':
                    all_buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in all_buttons:
                        aria = btn.get_attribute('aria-label')
                        if aria and len(aria) > 15:
                            # Check if it looks like an address (has comma or numbers)
                            if ',' in aria or any(char.isdigit() for char in aria):
                                # Exclude phone numbers and other non-address content
                                if not aria.startswith(('Phone', 'Téléphone', 'Tel', '+', '0')):
                                    data['address'] = aria.strip()
                                    break
            except Exception as e:
                logging.debug(f"Address extraction error: {e}")
        
        # Extract phone number if we don't have it yet
        if data['phone'] == 'N/A':
            try:
                # Method 1: Look for phone button with data-item-id
                phone_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id*='phone']")
                if phone_buttons:
                    aria_label = phone_buttons[0].get_attribute('aria-label')
                    if aria_label:
                        for prefix in ['Phone: ', 'Téléphone : ', 'Telefon: ', 'Tel: ', 'Teléfono: ']:
                            aria_label = aria_label.replace(prefix, '')
                        data['phone'] = aria_label.strip()
                
                # Method 2: Look for tel: links
                if data['phone'] == 'N/A':
                    tel_links = driver.find_elements(By.CSS_SELECTOR, "a[href^='tel:']")
                    if tel_links:
                        href = tel_links[0].get_attribute('href')
                        data['phone'] = href.replace('tel:', '').strip()
                
                # Method 3: Look for phone in aria-labels
                if data['phone'] == 'N/A':
                    all_buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in all_buttons:
                        aria = btn.get_attribute('aria-label')
                        if aria:
                            # Check if it looks like a phone number
                            if any(word in aria.lower() for word in ['phone', 'téléphone', 'telefon', 'tel']):
                                data['phone'] = aria.strip()
                                break
                            # Or if it starts with + or contains only digits and spaces
                            elif aria.startswith(('+', '0')) and any(char.isdigit() for char in aria):
                                if len(aria.replace(' ', '').replace('+', '').replace('-', '')) >= 8:
                                    data['phone'] = aria.strip()
                                    break
            except Exception as e:
                logging.debug(f"Phone extraction error: {e}")
        
        # Check for website
        try:
            data['has_website'] = 'No'  # Default to No
            
            # Look for website link with data-item-id='authority'
            website_links = driver.find_elements(By.CSS_SELECTOR, "a[data-item-id='authority']")
            if website_links:
                href = website_links[0].get_attribute('href')
                # Make sure it's not a Google link
                if href and 'google.com' not in href and 'http' in href:
                    data['has_website'] = 'Yes'
            
            # Alternative: look for links with "website" in aria-label
            if data['has_website'] == 'No':
                all_links = driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    aria = link.get_attribute('aria-label')
                    href = link.get_attribute('href')
                    if aria and href:
                        aria_lower = aria.lower()
                        # Check for website-related keywords
                        if any(word in aria_lower for word in ['website', 'site web', 'webová stránka', 'sitio web']):
                            # Exclude Google Maps and Google-related links
                            if 'http' in href and 'google.com' not in href and 'maps' not in href.lower():
                                data['has_website'] = 'Yes'
                                break
        except Exception as e:
            data['has_website'] = 'No'
            logging.debug(f"Website check error: {e}")
        
        logging.info(f"Extracted: {data['name'][:40]} | Addr: {'✓' if data['address'] != 'N/A' else '✗'} | Phone: {'✓' if data['phone'] != 'N/A' else '✗'}")
        return data
    
    except StaleElementReferenceException:
        logging.warning("Stale element reference, skipping business")
        return None
    except Exception as e:
        logging.error(f"Error extracting business data: {e}")
        return None


def save_to_csv(data, category, city):
    """
    Save scraped data to CSV with timestamp
    Creates 3 files:
    1. Main CSV with ALL businesses
    2. Filtered CSV with businesses that HAVE websites
    3. Filtered CSV with businesses that DON'T have websites
    """
    if not data:
        logging.warning("No data to save")
        return None
    
    # Short date format: Dec29
    short_date = datetime.now().strftime('%b%d')
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Capitalize category and city for cleaner filenames
    category_clean = category.capitalize()
    city_clean = city.capitalize()
    
    # 1. Save ALL businesses (main file)
    main_filename = f"{category_clean}_{city_clean}_{short_date}_ALL.csv"
    df.to_csv(main_filename, index=False, encoding='utf-8-sig')
    logging.info(f"✓ Saved ALL businesses to: {main_filename}")
    
    # 2. Save businesses WITH websites
    with_website = df[df['has_website'] == 'Yes']
    if len(with_website) > 0:
        with_filename = f"{category_clean}_{city_clean}_{short_date}_WITH_website.csv"
        with_website.to_csv(with_filename, index=False, encoding='utf-8-sig')
        logging.info(f"✓ Saved {len(with_website)} businesses WITH websites to: {with_filename}")
    
    # 3. Save businesses WITHOUT websites
    without_website = df[df['has_website'] == 'No']
    if len(without_website) > 0:
        without_filename = f"{category_clean}_{city_clean}_{short_date}_WITHOUT_website.csv"
        without_website.to_csv(without_filename, index=False, encoding='utf-8-sig')
        logging.info(f"✓ Saved {len(without_website)} businesses WITHOUT websites to: {without_filename}")
    
    # Log statistics
    logging.info(f"📊 Total: {len(df)} | With website: {len(with_website)} | Without website: {len(without_website)}")
    
    return main_filename, short_date


def create_pdf_from_csv(csv_filename, category, city):
    """
    Create a professional PDF report from CSV file
    """
    try:
        # Read CSV
        df = pd.read_csv(csv_filename, encoding='utf-8-sig')
        
        if len(df) == 0:
            logging.warning(f"No data in {csv_filename}, skipping PDF creation")
            return None
        
        # Create PDF filename
        pdf_filename = csv_filename.replace('.csv', '.pdf')
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                                rightMargin=30, leftMargin=30,
                                topMargin=30, bottomMargin=30)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Determine report type
        if 'WITH_website' in csv_filename:
            report_type = "Businesses WITH Websites"
            color_theme = colors.HexColor('#2ecc71')  # Green
        elif 'WITHOUT_website' in csv_filename:
            report_type = "Businesses WITHOUT Websites"
            color_theme = colors.HexColor('#e74c3c')  # Red
        else:
            report_type = "All Businesses"
            color_theme = colors.HexColor('#3498db')  # Blue
        
        # Title
        title = Paragraph(f"<b>{category.title()} in {city}</b>", title_style)
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph(f"{report_type} - {len(df)} Results", subtitle_style)
        elements.append(subtitle)
        
        # Date
        date_text = Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style)
        elements.append(date_text)
        elements.append(Spacer(1, 20))
        
        # Prepare table data
        # Select columns to display (exclude proxy_used for cleaner look)
        display_columns = ['name', 'address', 'phone', 'has_website']
        table_data = [['#', 'Business Name', 'Address', 'Phone', 'Website']]
        
        for idx, row in df.iterrows():
            table_data.append([
                str(idx + 1),
                str(row['name'])[:40] + '...' if len(str(row['name'])) > 40 else str(row['name']),
                str(row['address'])[:35] + '...' if len(str(row['address'])) > 35 else str(row['address']),
                str(row['phone']) if row['phone'] != 'N/A' else '-',
                '✓' if row['has_website'] == 'Yes' else '✗'
            ])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 2.2*inch, 2.2*inch, 1.2*inch, 0.7*inch])
        
        # Table style
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), color_theme),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Index column centered
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),  # Website column centered
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph(f"Total Businesses: {len(df)} | Scraped Date: {df.iloc[0]['scraped_date']}", footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        logging.info(f"✓ Created PDF: {pdf_filename}")
        return pdf_filename
    
    except Exception as e:
        logging.error(f"Error creating PDF from {csv_filename}: {e}")
        return None


def create_all_pdfs(category, city, short_date):
    """
    Create PDFs for all CSV files (ALL, WITH, WITHOUT)
    """
    pdf_files = []
    
    # Capitalize for clean filenames
    category_clean = category.capitalize()
    city_clean = city.capitalize()
    
    # Generate PDFs for each CSV type
    csv_patterns = [
        f"{category_clean}_{city_clean}_{short_date}_ALL.csv",
        f"{category_clean}_{city_clean}_{short_date}_WITH_website.csv",
        f"{category_clean}_{city_clean}_{short_date}_WITHOUT_website.csv"
    ]
    
    for csv_file in csv_patterns:
        if os.path.exists(csv_file):
            pdf_file = create_pdf_from_csv(csv_file, category, city)
            if pdf_file:
                pdf_files.append(pdf_file)
    
    return pdf_files


def main(category, city, max_results=300):
    """
    Main execution function with proxy rotation
    """
    # Load proxies
    proxies = load_proxies_from_file('proxies.txt')
    proxy_index = 0
    proxy_fail_count = {}
    
    # Statistics
    stats = {
        'total_scraped': 0,
        'successful': 0,
        'failed': 0,
        'proxies_used': set(),
        'start_time': time.time()
    }
    
    scraped_data = []
    driver = None
    current_proxy = None
    requests_with_proxy = 0
    
    try:
        while stats['total_scraped'] < max_results:
            # Rotate proxy every 5-10 requests or on failure
            if driver is None or requests_with_proxy >= random.randint(5, 10):
                if driver:
                    driver.quit()
                
                # Get next working proxy
                if proxies:
                    attempts = 0
                    while attempts < len(proxies):
                        current_proxy = proxies[proxy_index % len(proxies)]
                        proxy_str = f"{current_proxy['host']}:{current_proxy['port']}"
                        
                        # Skip if proxy failed too many times
                        if proxy_fail_count.get(proxy_str, 0) >= 3:
                            logging.warning(f"Skipping proxy {proxy_str} (failed 3 times)")
                            proxy_index += 1
                            attempts += 1
                            continue
                        
                        try:
                            driver = setup_driver(proxy_dict=current_proxy)
                            proxy_str = f"{current_proxy['host']}:{current_proxy['port']}"
                            stats['proxies_used'].add(proxy_str)
                            requests_with_proxy = 0
                            break
                        except Exception as e:
                            proxy_str = f"{current_proxy['host']}:{current_proxy['port']}"
                            logging.error(f"Failed to setup driver with proxy {proxy_str}: {e}")
                            proxy_fail_count[proxy_str] = proxy_fail_count.get(proxy_str, 0) + 1
                            proxy_index += 1
                            attempts += 1
                    
                    if attempts >= len(proxies):
                        logging.error("All proxies failed, trying without proxy")
                        driver = setup_driver(proxy_dict=None)
                        current_proxy = None
                else:
                    driver = setup_driver(proxy_dict=None)
                    current_proxy = None
            
            # Search Google Maps
            if not search_google_maps(driver, category, city):
                if current_proxy:
                    proxy_str = f"{current_proxy['host']}:{current_proxy['port']}"
                    proxy_fail_count[proxy_str] = proxy_fail_count.get(proxy_str, 0) + 1
                driver.quit()
                driver = None
                continue
            
            # Scroll and load results
            businesses = scroll_and_load_results(driver, max_results - stats['total_scraped'])
            
            if not businesses:
                logging.warning("No businesses found")
                break
            
            # Extract data from each business
            for i, business in enumerate(businesses):
                if stats['total_scraped'] >= max_results:
                    break
                
                try:
                    data = extract_business_data(driver, business, current_proxy)
                    
                    if data:
                        scraped_data.append(data)
                        stats['successful'] += 1
                    else:
                        stats['failed'] += 1
                    
                    stats['total_scraped'] += 1
                    requests_with_proxy += 1
                    
                    # Save progress every 50 businesses
                    if stats['total_scraped'] % 50 == 0:
                        save_to_csv(scraped_data, category, city)
                        logging.info(f"Progress saved: {stats['total_scraped']}/{max_results}")
                    
                    # Random delay between requests
                    time.sleep(random.uniform(2, 5))
                
                except Exception as e:
                    logging.error(f"Error processing business {i}: {e}")
                    stats['failed'] += 1
                    continue
            
            # Break if we've processed all available businesses
            break
    
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
    
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    
    finally:
        if driver:
            driver.quit()
        
        # Clean up proxy extension file
        if os.path.exists('proxy_auth_plugin.zip'):
            try:
                os.remove('proxy_auth_plugin.zip')
            except:
                pass
        
        # Save final results
        result = save_to_csv(scraped_data, category, city)
        
        # Generate PDFs from CSVs
        if result:
            filename, short_date = result
            logging.info("=" * 60)
            logging.info("📄 Generating PDF reports...")
            logging.info("=" * 60)
            pdf_files = create_all_pdfs(category, city, short_date)
            if pdf_files:
                logging.info(f"✓ Created {len(pdf_files)} PDF report(s)")
        
        # Log summary
        elapsed_time = time.time() - stats['start_time']
        avg_time = elapsed_time / stats['total_scraped'] if stats['total_scraped'] > 0 else 0
        
        logging.info("=" * 60)
        logging.info("🎉 SCRAPING SUMMARY")
        logging.info("=" * 60)
        logging.info(f"Total scraped: {stats['total_scraped']}")
        logging.info(f"Successful: {stats['successful']}")
        logging.info(f"Failed: {stats['failed']}")
        logging.info(f"Proxies used: {len(stats['proxies_used'])}")
        logging.info(f"Total time: {elapsed_time:.2f} seconds")
        logging.info(f"Average time per business: {avg_time:.2f} seconds")
        logging.info("=" * 60)
        logging.info("📁 Output files created:")
        if result:
            filename, short_date = result
            category_clean = category.capitalize()
            city_clean = city.capitalize()
            base_name = f"{category_clean}_{city_clean}_{short_date}"
            logging.info(f"   CSV Files:")
            logging.info(f"   1. {base_name}_ALL.csv (all businesses)")
            logging.info(f"   2. {base_name}_WITH_website.csv (filtered)")
            logging.info(f"   3. {base_name}_WITHOUT_website.csv (filtered)")
            logging.info(f"   PDF Files:")
            logging.info(f"   1. {base_name}_ALL.pdf (all businesses)")
            logging.info(f"   2. {base_name}_WITH_website.pdf (filtered)")
            logging.info(f"   3. {base_name}_WITHOUT_website.pdf (filtered)")
        logging.info("=" * 60)
        
        return scraped_data


if __name__ == "__main__":
    # CONFIGURATION - Change these values for your scraping needs
    results = main(
        category="plumbers",      # Change to: restaurants, dentists, electricians, etc.
        city="Prague",            # Change to: Madrid, Barcelona, Berlin, etc.
        max_results=20            # Change to desired number (e.g., 50, 100, 300)
    )
