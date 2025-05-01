import time
import os
import requests
import concurrent.futures
import random
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm
import cloudscraper
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='brand_scraper.log',
    filemode='a'
)

# Configure SmartProxy
SMARTPROXY_USERNAME = os.getenv('SMARTPROXY_USERNAME')
SMARTPROXY_PASSWORD = os.getenv('SMARTPROXY_PASSWORD')
SMARTPROXY_ENDPOINT = os.getenv('SMARTPROXY_ENDPOINT')
PROXY_URL = f"http://{SMARTPROXY_USERNAME}:{SMARTPROXY_PASSWORD}@{SMARTPROXY_ENDPOINT}"
PROXIES = {
    'http': PROXY_URL,
    'https': PROXY_URL
}

# 1) Create one global, pooled scraper
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome','platform': 'darwin','mobile': False}
)
scraper.proxies = PROXIES

# 2) Grab CloudScraper's existing HTTPS adapter
cf_adapter = scraper.get_adapter("https://")

# 3) Bump its pool sizes
cf_adapter.pool_connections = 50
cf_adapter.pool_maxsize = 50

# Output files
BRAND_LINKS_FILE = 'fra_brand_links.txt'
PERFUME_LINKS_FILE = 'fra_per_links.txt'
FAILED_BRAND_URLS_FILE = 'failed_brand_urls.txt'
SUCCESS_BRANDS_URLS_FILE = 'success_brands_urls.txt'

# Function to log failed brand URLs
def log_failed_brand_url(url):
    with open(FAILED_BRAND_URLS_FILE, 'a') as f:
        f.write(f"{url}\n")
    logging.info(f"Logged failed brand URL to {FAILED_BRAND_URLS_FILE}: {url}")

# Function to log successful brand URLs
def log_successful_brand_url(url):
    with open(SUCCESS_BRANDS_URLS_FILE, 'a') as f:
        f.write(f"{url}\n")
    logging.info(f"Logged successful brand URL to {SUCCESS_BRANDS_URLS_FILE}: {url}")

# Function to make requests via cloudscraper with retries
def cloudscraper_request(url, retries=3, delay=3):
    logging.info(f"Requesting URL: {url}")
    for attempt in range(retries):
        try:
            # reuse the global scraper/session
            response = scraper.get(url, timeout=30)
            response.raise_for_status()
            html = response.text
            response.close()
            return html
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e}")
            log_failed_brand_url(url)
        except requests.exceptions.Timeout as e:
            logging.error(f"Connection timeout: {e}")
            log_failed_brand_url(url)
        except Exception as e:
            logging.error(f"Connection error: {e}")
            log_failed_brand_url(url)

        backoff = delay + random.uniform(5, 10)
        logging.info(f"Retrying in {backoff:.1f}s…")
        time.sleep(backoff)

    # If all retries failed, log the URL as a general failure
    log_failed_brand_url(url)
    return None

# Function to get brand links from Fragrantica
def get_brand_links():
    # Check if brand links file already exists and has content
    if os.path.exists(BRAND_LINKS_FILE) and os.path.getsize(BRAND_LINKS_FILE) > 0:
        print(f"Reading brand links from existing file: {BRAND_LINKS_FILE}")
        with open(BRAND_LINKS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    
    # Fragrantica brands directory uses a new URL structure
    # designers-1/ through designers-11/
    print("Fetching brand links from Fragrantica...")
    all_brand_links = []
    
    # There are 11 pages of designers on Fragrantica
    for page_num in tqdm(range(1, 12), desc="Processing designer pages"):
        page_url = f"https://www.fragrantica.com/designers-{page_num}/"
        html = cloudscraper_request(page_url)
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all brand links on the page (the structure has changed)
            brand_elements = soup.select('div.designerlist a')
            
            for brand_element in brand_elements:
                brand_link = brand_element.get('href')
                if brand_link and 'designers' in brand_link:
                    # Convert relative URLs to absolute URLs if needed
                    if brand_link.startswith('/'):
                        brand_link = f"https://www.fragrantica.com{brand_link}"
                    all_brand_links.append(brand_link)
            
            # Random sleep to avoid being blocked
            sleep_time = random.uniform(3, 6)
            time.sleep(sleep_time)
    
    # Save brand links to file
    with open(BRAND_LINKS_FILE, 'w') as f:
        for link in all_brand_links:
            f.write(f"{link}\n")
    
    print(f"Total brands found: {len(all_brand_links)}")
    return all_brand_links

# Process a single brand to extract perfume links
def process_brand(brand_url, existing_links):
    try:
        # Use cloudscraper to get the page content
        html = cloudscraper_request(brand_url)
        
        if not html:
            logging.error(f"Failed to get content for brand: {brand_url}")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all perfume links on the page
        perfume_elements = soup.select('div.flex-child-auto > h3 > a')
        
        new_links = []
        for perfume_element in perfume_elements:
            perfume_link = perfume_element.get('href')
            if perfume_link:
                # Make sure it's an absolute URL
                if perfume_link.startswith('/'):
                    perfume_link = f"https://www.fragrantica.com{perfume_link}"
                
                # Check if it's a new link
                if perfume_link not in existing_links:
                    new_links.append(perfume_link)
        
        if new_links:
            print(f"Found {len(new_links)} new perfume links from {brand_url}")
        else:
            print(f"No new perfume links found for {brand_url}")
        
        # Log this brand as successfully processed
        log_successful_brand_url(brand_url)
            
        return new_links
    except Exception as e:
        logging.error(f"Error processing brand {brand_url}: {e}")
        return []

# Process brands in parallel batches
def process_brands_in_batches(brand_links, existing_links, batch_size=6, max_workers=3):
    all_new_links = []
    
    # Create batches of brands to process
    batches = [brand_links[i:i + batch_size] for i in range(0, len(brand_links), batch_size)]
    
    for batch_idx, batch in enumerate(tqdm(batches, desc="Processing brand batches")):
        new_links_from_batch = []
        
        # Process this batch in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map brand URLs to process_brand function
            future_to_brand = {executor.submit(process_brand, brand_url, existing_links): brand_url for brand_url in batch}
            
            for future in concurrent.futures.as_completed(future_to_brand):
                brand_url = future_to_brand[future]
                try:
                    new_links = future.result()
                    new_links_from_batch.extend(new_links)
                    # Update existing links set to avoid duplicates in future batches
                    existing_links.update(new_links)
                except Exception as e:
                    logging.error(f"Error processing {brand_url}: {e}")
        
        # Save batch results immediately to avoid losing progress
        if new_links_from_batch:
            with open(PERFUME_LINKS_FILE, 'a') as f:
                for link in new_links_from_batch:
                    f.write(f"{link}\n")
            
            all_new_links.extend(new_links_from_batch)
            print(f"Batch {batch_idx+1}/{len(batches)}: Added {len(new_links_from_batch)} new perfume links")
        
        # Random sleep between batches to be nice to the server
        sleep_time = random.uniform(5, 10)
        time.sleep(sleep_time)
    
    return all_new_links

# Main function
def main():
    # Get all brand links
    brand_links = get_brand_links()
    print(f"Found {len(brand_links)} total brands...")
    
    # Check if the perfume links file exists, if not create it
    if not os.path.exists(PERFUME_LINKS_FILE):
        open(PERFUME_LINKS_FILE, 'w').close()
    
    # Ensure success and failed brand URLs files exist
    if not os.path.exists(SUCCESS_BRANDS_URLS_FILE):
        open(SUCCESS_BRANDS_URLS_FILE, 'w').close()
        
    if not os.path.exists(FAILED_BRAND_URLS_FILE):
        open(FAILED_BRAND_URLS_FILE, 'w').close()
        
    # Load failed brand URLs
    failed_brands = set()
    with open(FAILED_BRAND_URLS_FILE, 'r') as f:
        for line in f:
            failed_brands.add(line.strip())
    
    # Load successfully processed brand URLs
    successful_brands = set()
    with open(SUCCESS_BRANDS_URLS_FILE, 'r') as f:
        for line in f:
            successful_brands.add(line.strip())
    
    # Filter out brands that have already been processed
    brands_to_process = [brand for brand in brand_links if brand not in failed_brands and brand not in successful_brands]
    
    print(f"Skipping {len(failed_brands)} failed brands")
    print(f"Skipping {len(successful_brands)} successfully processed brands")
    print(f"Processing {len(brands_to_process)} remaining brands...")
    
    # Get existing perfume links to avoid duplicates
    existing_links = set()
    with open(PERFUME_LINKS_FILE, 'r') as f:
        for line in f:
            existing_links.add(line.strip())
    
    print(f"Found {len(existing_links)} existing perfume links")
    
    # You can define the number of brands to process per batch
    # and the maximum number of parallel workers
    batch_size = 6
    max_workers = 3
    
    # Process brands in parallel batches
    all_new_links = process_brands_in_batches(brands_to_process, existing_links, batch_size, max_workers)
    
    print(f"\nFinished processing all brands.")
    print(f"Total new perfume links added: {len(all_new_links)}")
    print(f"Total perfume links in file: {len(existing_links) + len(all_new_links)}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")