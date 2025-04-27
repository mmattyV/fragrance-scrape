import time
import os
import requests
import concurrent.futures
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from tqdm import tqdm

# Configure FlareSolverr
FLARESOLVERR_URL = 'http://localhost:8191/v1'

# Auto-install chromedriver
chromedriver_path = chromedriver_autoinstaller.install()

# Configure Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# Output files
BRAND_LINKS_FILE = 'fra_brand_links.txt'
PERFUME_LINKS_FILE = 'fra_per_links.txt'

# Function to make requests via FlareSolverr with retries
def flaresolverr_request(url, retries=3, delay=2):
    payload = {
        'cmd': 'request.get',
        'url': url,
        'maxTimeout': 60000
    }
    for attempt in range(retries):
        try:
            response = requests.post(FLARESOLVERR_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
    return None

# Function to get brand links from Fragrantica
def get_brand_links():
    # Check if brand links file already exists
    if os.path.exists(BRAND_LINKS_FILE):
        print(f"Reading brand links from existing file: {BRAND_LINKS_FILE}")
        with open(BRAND_LINKS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    
    # Fragrantica brands directory URL 
    brands_url = "https://www.fragrantica.com/designers/"
    print("Fetching brand links from Fragrantica...")
    all_brand_links = []
    
    # Get all letters A-Z (and others)
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["*"]
    
    for letter in tqdm(letters, desc="Processing alphabet"):
        letter_url = f"{brands_url}{letter}.html"
        response = flaresolverr_request(letter_url)
        
        if response and 'solution' in response and 'response' in response['solution']:
            soup = BeautifulSoup(response['solution']['response'], 'html.parser')
            
            # Find all brand links on the page
            brand_elements = soup.select('div.designerlist a')
            
            for brand_element in brand_elements:
                brand_link = brand_element.get('href')
                if brand_link and 'designers' in brand_link:
                    # Convert relative URLs to absolute URLs if needed
                    if brand_link.startswith('/'):
                        brand_link = f"https://www.fragrantica.com{brand_link}"
                    all_brand_links.append(brand_link)
            
            # Short sleep to avoid being blocked
            time.sleep(1)
    
    # Save brand links to file
    with open(BRAND_LINKS_FILE, 'w') as f:
        for link in all_brand_links:
            f.write(f"{link}\n")
    
    print(f"Total brands found: {len(all_brand_links)}")
    return all_brand_links

# Process a single brand to extract perfume links
def process_brand(brand_url, existing_links):
    try:
        # Use FlareSolverr to get the page content
        response = flaresolverr_request(brand_url)
        
        if not response or 'solution' not in response or 'response' not in response['solution']:
            print(f"Failed to get content for brand: {brand_url}")
            return []
        
        soup = BeautifulSoup(response['solution']['response'], 'html.parser')
        
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
            
        return new_links
    except Exception as e:
        print(f"Error processing brand {brand_url}: {e}")
        return []

# Process brands in parallel batches
def process_brands_in_batches(brand_links, existing_links, batch_size=5, max_workers=5):
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
                    print(f"Error processing {brand_url}: {e}")
        
        # Save batch results immediately to avoid losing progress
        if new_links_from_batch:
            with open(PERFUME_LINKS_FILE, 'a') as f:
                for link in new_links_from_batch:
                    f.write(f"{link}\n")
            
            all_new_links.extend(new_links_from_batch)
            print(f"Batch {batch_idx+1}/{len(batches)}: Added {len(new_links_from_batch)} new perfume links")
        
        # Short pause between batches to be nice to the server
        time.sleep(2)
    
    return all_new_links

# Main function
def main():
    # Get all brand links
    brand_links = get_brand_links()
    print(f"Processing {len(brand_links)} brands...")
    
    # Check if the perfume links file exists, if not create it
    if not os.path.exists(PERFUME_LINKS_FILE):
        open(PERFUME_LINKS_FILE, 'w').close()
    
    # Get existing perfume links to avoid duplicates
    existing_links = set()
    with open(PERFUME_LINKS_FILE, 'r') as f:
        for line in f:
            existing_links.add(line.strip())
    
    print(f"Found {len(existing_links)} existing perfume links")
    
    # You can define the number of brands to process per batch
    # and the maximum number of parallel workers
    batch_size = 10  # Process 10 brands in each batch
    max_workers = 5  # Use 5 parallel threads
    
    # Process brands in parallel batches
    all_new_links = process_brands_in_batches(brand_links, existing_links, batch_size, max_workers)
    
    print(f"\nFinished processing all brands.")
    print(f"Total new perfume links added: {len(all_new_links)}")
    print(f"Total perfume links in file: {len(existing_links) + len(all_new_links)}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Browser closed.")
