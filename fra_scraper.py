import csv
import os
import random
import time
import requests
from requests.adapters import HTTPAdapter
import concurrent.futures
import cloudscraper
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='scraper.log',
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

# Path to control file
control_file_path = os.path.join(os.getcwd(), 'control.txt')
failed_urls_path = os.path.join(os.getcwd(), 'failed_urls.txt')

# Function to read control file
def read_control_file():
    if not os.path.exists(control_file_path):
        with open(control_file_path, 'w') as f:
            f.write('run')
    with open(control_file_path, 'r') as file:
        return file.read().strip()

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
        except Exception as e:
            logging.error(f"Connection error: {e}")

        backoff = delay + random.uniform(5, 10)
        logging.info(f"Retrying in {backoff:.1f}s…")
        time.sleep(backoff)

    return None

# Function to save failed URL
def save_failed_url(url):
    logging.error(f"Failed to scrape URL: {url}")
    with open(failed_urls_path, 'a') as file:
        file.write(f"{url}\n")

# Function to extract perfume information
def extract_perfume_info(url):
    try:
        logging.info(f"Extracting perfume information from: {url}")
        response = cloudscraper_request(url)
        if response:
            soup = BeautifulSoup(response, 'html.parser')

            # Extract basic information
            name_element = soup.select_one('h1[itemprop="name"]')
            name = ''
            if name_element:
                # Get the text but exclude the gender part
                full_text = name_element.get_text(strip=True)
                
                # Remove gender part
                gender_element = name_element.select_one('small')
                if gender_element:
                    gender_part = gender_element.get_text(strip=True)
                    name = full_text.replace(gender_part, '').strip()
                else:
                    # If no gender element found, clean the name by removing any "for women/men" text
                    name = full_text.split(' for women')[0].split(' for men')[0].strip()
            else:
                name = 'N/A'
                
            # Extract brand
            brand_element = soup.select_one('span[itemprop="name"]')
            brand = brand_element.get_text(strip=True) if brand_element else 'N/A'
            logging.info(f"Extracted brand: {brand}")
            
            # Clean the name by removing the brand name if it appears at the end
            if brand != 'N/A' and name.endswith(brand):
                name = name[:-len(brand)].strip()
                
            logging.info(f"Extracted name: {name}")

            # Extract gender
            gender_element = soup.select_one('h1 small')
            gender = gender_element.get_text(strip=True) if gender_element else 'N/A'
            logging.info(f"Extracted gender: {gender}")

            # Extract year launched
            year = 'N/A'
            description_element = soup.select_one('div[itemprop="description"]')
            if description_element:
                description_text = description_element.get_text(strip=True)
                import re
                year_match = re.search(r'launched in (\d{4})', description_text)
                if year_match:
                    year = year_match.group(1)
            logging.info(f"Extracted year: {year}")

            # Extract ratings
            rating_value_element = soup.select_one('span[itemprop="ratingValue"]')
            rating_value = rating_value_element.get_text(strip=True) if rating_value_element else 'N/A'
            logging.info(f"Extracted rating value: {rating_value}")

            rating_count_element = soup.select_one('span[itemprop="ratingCount"]')
            rating_count = rating_count_element.get_text(strip=True) if rating_count_element else 'N/A'
            logging.info(f"Extracted rating count: {rating_count}")

            # Extract main accords
            main_accords_elements = soup.select('.accord-bar')
            main_accords = [element.get_text(strip=True) for element in main_accords_elements]
            logging.info(f"Extracted main accords: {main_accords}")

            # Extract perfumer information
            perfumers_elements = soup.select('.cell a[href*="/noses/"]')
            perfumers = [element.get_text(strip=True) for element in perfumers_elements]
            logging.info(f"Extracted perfumers: {perfumers}")

            # Extract full description
            description = ''
            if description_element:
                # Get all paragraphs from the description section
                paragraphs = description_element.find_all('p')
                description = ' '.join(p.get_text(strip=True) for p in paragraphs)
                
                # Remove the "Read about this perfume in other languages" part
                import re
                description = re.sub(r'Read about this perfume in other languages:.*?\.', '', description)
                
                # Fix fragrance name and brand formatting - handle multiple patterns
                description = re.sub(r'([A-Za-z0-9\'\.]*)\s*by\s*([A-Za-z\s]+)is', r'\1 by \2 is', description)
                description = re.sub(r'([A-Za-z0-9\'\.]+)by([A-Za-z])', r'\1 by \2', description)
                
                # Fix spacing between words
                description = re.sub(r'is a\s+([mnp])', r'is a \1', description)  # Fix "is a mplified", "is a n", etc.
                description = re.sub(r'is a n', r'is an', description)  # Fix "is a n" to "is an"
                
                # Fix common spacing issues
                description = re.sub(r',and', r', and', description)
                description = re.sub(r'offlinty', r'of flinty', description)
                description = re.sub(r'andsoft', r'and soft', description)
                description = re.sub(r'good-\s*by\s*e', r'good-bye', description)
                description = re.sub(r'prom\s*ise', r'promise', description)
                
                # Fix concatenated words with capital letters in the middle
                description = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', description)
                
                # Remove any double spaces that might have been created
                description = re.sub(r'\s{2,}', ' ', description)
                
                # Trim any leading/trailing whitespace
                description = description.strip()
            logging.info(f"Extracted description: {len(description)} characters")

            # Extract longevity and sillage ratings
            longevity_element = soup.select_one('longevity-rating p')
            longevity = longevity_element.get_text(strip=True).replace('Perfume longevity:', '').strip() if longevity_element else 'N/A'
            logging.info(f"Extracted longevity: {longevity}")

            sillage_element = soup.select_one('sillage-rating p')
            sillage = sillage_element.get_text(strip=True).replace('Perfume sillage:', '').strip() if sillage_element else 'N/A'
            logging.info(f"Extracted sillage: {sillage}")

            # Extract image URL
            image_element = soup.select_one('img[itemprop="image"]')
            image_url = image_element['src'] if image_element and 'src' in image_element.attrs else 'N/A'
            logging.info(f"Extracted image URL: {image_url}")

            # Extract notes using multiple approaches
            top_notes = []
            middle_notes = []
            base_notes = []
            
            # Approach 1: Look for direct pyramid structure in the HTML
            pyramid_switch = soup.select_one('pyramid-switch')
            if pyramid_switch:
                # Get pyramid-notes elements
                for level_type in ['top', 'middle', 'base']:
                    pyramid_level = pyramid_switch.select_one(f'pyramid-level[notes="{level_type}"]')
                    if pyramid_level:
                        # Try to get notes from divs inside the pyramid level
                        note_divs = pyramid_level.select('div > div > div')
                        for div in note_divs:
                            # Look for the div containing the note name
                            note_name_div = div.find('div', recursive=False)
                            if note_name_div and note_name_div.text.strip():
                                if level_type == 'top':
                                    top_notes.append(note_name_div.text.strip())
                                elif level_type == 'middle':
                                    middle_notes.append(note_name_div.text.strip())
                                elif level_type == 'base':
                                    base_notes.append(note_name_div.text.strip())
            
            # Approach 2: Try parsing from the description text
            if not any([top_notes, middle_notes, base_notes]) and description:
                # Try to extract notes from description
                try:
                    # Look for common note patterns in the description
                    desc_text = description
                    
                    # Pattern for "Top notes are X, Y and Z"
                    top_match = re.search(r'[Tt]op [Nn]otes?(?:\s+are|\:|\s+include)\s+([\w\s,]+?)(?:;|\.|\n|$|middle)', desc_text)
                    if top_match:
                        notes_text = top_match.group(1).replace(' and ', ', ')
                        top_notes = [note.strip() for note in notes_text.split(',') if note.strip()]
                    
                    # Pattern for "Middle notes are X, Y and Z"
                    middle_match = re.search(r'[Mm]iddle [Nn]otes?(?:\s+are|\:|\s+include)\s+([\w\s,]+?)(?:;|\.|\n|$|base)', desc_text)
                    if middle_match:
                        notes_text = middle_match.group(1).replace(' and ', ', ')
                        middle_notes = [note.strip() for note in notes_text.split(',') if note.strip()]
                    
                    # Pattern for "Base notes are X, Y and Z"
                    base_match = re.search(r'[Bb]ase [Nn]otes?(?:\s+are|\:|\s+include)\s+([\w\s,]+?)(?:;|\.|\n|$)', desc_text)
                    if base_match:
                        notes_text = base_match.group(1).replace(' and ', ', ')
                        base_notes = [note.strip() for note in notes_text.split(',') if note.strip()]
                except Exception as e:
                    logging.error(f"Error parsing notes from description: {e}")
            
            # Approach 3: Try looking for note sections directly in the page
            if not any([top_notes, middle_notes, base_notes]):
                try:
                    # Find all divs that might contain notes
                    note_sections = soup.find_all('div', string=lambda text: text and ('top notes' in text.lower() or 'middle notes' in text.lower() or 'base notes' in text.lower()))
                    
                    for section in note_sections:
                        section_text = section.get_text().lower()
                        next_element = section.find_next_sibling()
                        
                        if next_element:
                            notes_text = next_element.get_text().strip()
                            note_list = [note.strip() for note in notes_text.split(',')]
                            
                            if 'top notes' in section_text:
                                top_notes = note_list
                            elif 'middle notes' in section_text:
                                middle_notes = note_list
                            elif 'base notes' in section_text:
                                base_notes = note_list
                except Exception as e:
                    logging.error(f"Error finding note sections: {e}")
            
            # Approach 4: Fall back to looking for classic HTML structure
            if not any([top_notes, middle_notes, base_notes]):
                top_notes_div = soup.select_one('div.cell.notes-box.top-notes')
                if top_notes_div:
                    note_elements = top_notes_div.select('div.cell.text-center')
                    top_notes = [note.select_one('div.nowrap').get_text(strip=True) if note.select_one('div.nowrap') else "Unknown" for note in note_elements]
                
                middle_notes_div = soup.select_one('div.cell.notes-box.middle-notes')
                if middle_notes_div:
                    note_elements = middle_notes_div.select('div.cell.text-center')
                    middle_notes = [note.select_one('div.nowrap').get_text(strip=True) if note.select_one('div.nowrap') else "Unknown" for note in note_elements]
                
                base_notes_div = soup.select_one('div.cell.notes-box.base-notes')
                if base_notes_div:
                    note_elements = base_notes_div.select('div.cell.text-center')
                    base_notes = [note.select_one('div.nowrap').get_text(strip=True) if note.select_one('div.nowrap') else "Unknown" for note in note_elements]
            
            logging.info(f"Extracted top notes: {top_notes}")
            logging.info(f"Extracted middle notes: {middle_notes}")
            logging.info(f"Extracted base notes: {base_notes}")

            # Check if brand or name is missing or empty
            if not brand or not name or brand.strip() == '' or name.strip() == '':
                logging.error(f"Missing brand or name for URL: {url}")
                save_failed_url(url)
                return None
            
            # Clean and format ratings properly
            if rating_value and isinstance(rating_value, str) and "out of" in rating_value:
                rating_value = rating_value.replace("out of", " out of ")
            
            if rating_count and isinstance(rating_count, str) and rating_count.isdigit():
                rating_count = int(rating_count)
            
            # Clean description from any potential problematic characters
            if description:
                # Remove any carriage returns, newlines, double quotes that could break CSV format
                description = description.replace('\r', ' ').replace('\n', ' ')
                # Replace any double quotes with single quotes to prevent CSV issues
                description = description.replace('"', "'")
            
            return {
                "Name": name.strip() if name else 'N/A',
                "Brand": brand.strip() if brand else 'N/A',
                "Gender": gender.strip() if gender else 'N/A',
                "Year": year.strip() if year else 'N/A',
                "Rating Value": rating_value,
                "Rating Count": rating_count,
                "Main Accords": ','.join(main_accords) if isinstance(main_accords, list) else (main_accords if main_accords else 'N/A'),
                "Perfumers": ','.join(perfumers) if isinstance(perfumers, list) else (perfumers if perfumers else 'N/A'),
                "Top Notes": ','.join(top_notes) if top_notes else 'N/A',
                "Middle Notes": ','.join(middle_notes) if middle_notes else 'N/A',
                "Base Notes": ','.join(base_notes) if base_notes else 'N/A',
                "Longevity": longevity if longevity else 'N/A',
                "Sillage": sillage if sillage else 'N/A',
                "Description": description if description else 'N/A',
                "Image URL": image_url if image_url else 'N/A',
                "URL": url
            }
        else:
            logging.error(f"Error processing URL: {url}")
            save_failed_url(url)
            return None
    except Exception as e:
        logging.error(f"Error extracting info from {url}: {e}")
        save_failed_url(url)
        return None

# Function to get links to process
def get_perfume_links(filename='fra_per_links.txt'):
    links_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(links_path):
        with open(links_path, 'r') as file:
            urls = [line.strip() for line in file.readlines() if line.strip()]
        logging.info(f"Loaded {len(urls)} perfume links from {filename}")
        return urls
    else:
        logging.info(f"Links file {filename} not found.")
        return []

# Function to get already processed URLs from CSV
def get_processed_urls(csv_file):
    processed_urls = set()
    if os.path.exists(csv_file):
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'URL' in row and row['URL']:
                        processed_urls.add(row['URL'])
            logging.info(f"Found {len(processed_urls)} already processed URLs in {csv_file}")
        except Exception as e:
            logging.error(f"Error reading CSV file {csv_file}: {e}")
    return processed_urls

# Function to get failed URLs
def get_failed_urls(file_path=failed_urls_path):
    failed_urls = set()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                failed_urls = {line.strip() for line in file if line.strip()}
            logging.info(f"Found {len(failed_urls)} failed URLs in {file_path}")
        except Exception as e:
            logging.error(f"Error reading failed URLs file {file_path}: {e}")
    return failed_urls

# CSV writer that's thread-safe
class ThreadSafeWriter:
    def __init__(self, output_file, fieldnames):
        self.output_file = output_file
        self.fieldnames = fieldnames
        self.lock = __import__('threading').Lock()
        
        # Create file with headers if it doesn't exist
        file_exists = os.path.exists(output_file)
        if not file_exists:
            with open(output_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
    
    def write_row(self, row_dict):
        # Sanitize CSV data to prevent formatting issues
        sanitized_dict = {}
        for key, value in row_dict.items():
            if value is None:
                sanitized_dict[key] = 'N/A'
            elif isinstance(value, str):
                # Clean rating format (e.g., "3.28out of5." -> "3.28 out of 5.")
                if "out of" in value and "." in value:
                    value = value.replace("out of", " out of ")
                # Strip any extra quotes and escape any remaining quotes
                value = value.strip()
                # Remove any carriage returns or newlines that could break CSV format
                value = value.replace('\r', ' ').replace('\n', ' ')
                sanitized_dict[key] = value
            else:
                sanitized_dict[key] = value
        
        with self.lock:
            with open(self.output_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(sanitized_dict)

# Process a batch of URLs
def process_url_batch(urls, csv_writer, start_idx, total_urls):
    results = []
    for i, url in enumerate(urls):
        try:
            # Check control file
            control_command = read_control_file()
            if control_command == "pause":
                logging.info("Script paused. Change control.txt to 'run' to continue.")
                while read_control_file() == "pause":
                    time.sleep(10)
            elif control_command == "abort":
                logging.info("Script aborted.")
                break
                
            overall_idx = start_idx + i
            logging.info(f"Processing URL {overall_idx+1}/{total_urls}: {url}")
            
            # Get the perfume info
            perfume_info = extract_perfume_info(url)
            
            # Write to CSV
            if perfume_info is not None:
                csv_writer.write_row(perfume_info)
                logging.info(f"Data from {url} written to CSV")
            
            # Moderate random delay between requests within a worker
            delay = random.uniform(4, 7)  # Balanced delay between original and previous modification
            logging.info(f"Waiting {delay:.2f} seconds before next request...")
            time.sleep(delay)
            
        except Exception as e:
            logging.error(f"Error processing {url}: {e}")
    
    return results

# Main function
def main():
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    # Output CSV file
    output_csv = os.path.join(output_dir, 'fragrance_data.csv')
    
    # Get perfume links
    all_urls = get_perfume_links()
    if not all_urls:
        logging.info("No perfume links found. Please add links to fra_per_links.txt.")
        logging.info("Example link format: https://www.fragrantica.com/perfume/Brand/Perfume-Name-ID.html")
        return
    
    # Get already processed URLs from the main CSV file only
    processed_urls = get_processed_urls(output_csv)
    
    # Get failed URLs
    failed_urls = get_failed_urls()
    
    # Filter out already processed and failed URLs
    urls_to_skip = processed_urls.union(failed_urls)
    urls = [url for url in all_urls if url not in urls_to_skip]
    
    skipped_count = len(all_urls) - len(urls)
    logging.info(f"Total URLs: {len(all_urls)}")
    logging.info(f"Skipping {skipped_count} already processed or failed URLs")
    logging.info(f"URLs to process: {len(urls)}")
    
    if not urls:
        logging.info("All URLs have been processed already. Nothing to do.")
        return
    
    total_urls = len(urls)
    
    # Define CSV fields
    fieldnames = [
        "Name", "Brand", "Gender", "Year", "Rating Value", "Rating Count", "Main Accords", 
        "Perfumers", "Top Notes", "Middle Notes", "Base Notes", "Longevity", "Sillage", "Description", "Image URL", "URL"
    ]
    
    # Create thread-safe CSV writer
    csv_writer = ThreadSafeWriter(output_csv, fieldnames)
    
    # Parallel processing settings
    batch_size = 10
    max_workers = 5
    total_batches = (len(urls) + batch_size - 1) // batch_size  # Ceiling division
    
    logging.info(f"Processing URLs in {total_batches} batches with {max_workers} parallel workers")
    
    # Process in batches
    for batch_idx in tqdm(range(0, total_batches), desc="Processing batches", unit="batch"):
        # Check if we should abort
        if read_control_file() == "abort":
            logging.info("Script aborted.")
            break
            
        batch_start_idx = batch_idx * batch_size
        batch_end_idx = min(batch_start_idx + batch_size, len(urls))
        batch_urls = urls[batch_start_idx:batch_end_idx]
        
        # Calculate the absolute indices for checkpoint saving
        abs_start_idx = batch_start_idx
        abs_end_idx = batch_end_idx
        
        logging.info(f"\nProcessing batch {batch_idx+1}/{total_batches} (URLs {abs_start_idx+1}-{abs_end_idx} of {total_urls})")
        
        # For small batches, process sequentially to avoid overhead
        if len(batch_urls) <= 2:
            process_url_batch(batch_urls, csv_writer, abs_start_idx, total_urls)
        else:
            # Split the batch into chunks for parallel processing
            chunk_size = max(1, len(batch_urls) // max_workers)
            chunks = [batch_urls[i:i+chunk_size] for i in range(0, len(batch_urls), chunk_size)]
            
            # Process chunks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit tasks
                futures = []
                for i, chunk in enumerate(chunks):
                    chunk_start_idx = abs_start_idx + (i * chunk_size)
                    futures.append(executor.submit(process_url_batch, chunk, csv_writer, chunk_start_idx, total_urls))
                
                # Wait for completion with progress bar
                for future in tqdm(concurrent.futures.as_completed(futures), 
                                  total=len(futures), 
                                  desc=f"Batch {batch_idx+1} progress", 
                                  unit="chunk"):
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"Error in batch processing: {e}")
        
        # Pause between batches to avoid being rate-limited
        if batch_idx < total_batches - 1:  # Skip pause after the last batch
            pause_duration = random.uniform(4, 7)  # More conservative to avoid detection
            logging.info(f"Pausing for {pause_duration:.2f} seconds between batches...")
            time.sleep(pause_duration)
    
    logging.info(f"Scraping completed. Data saved to {output_csv}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nScript interrupted by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
