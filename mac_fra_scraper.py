import csv
import os
import random
import time
import requests
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
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

# Path to control file
control_file_path = os.path.join(os.getcwd(), 'control.txt')

# Function to read control file
def read_control_file():
    if not os.path.exists(control_file_path):
        with open(control_file_path, 'w') as f:
            f.write('run')
    with open(control_file_path, 'r') as file:
        return file.read().strip()

# Function to make requests via FlareSolverr with retries
def flaresolverr_request(url, retries=3, delay=2):
    print(f"Requesting URL via FlareSolverr: {url}")
    payload = {
        'cmd': 'request.get',
        'url': url,
        'maxTimeout': 60000
    }
    for attempt in range(retries):
        try:
            response = requests.post(FLARESOLVERR_URL, json=payload)
            response.raise_for_status()  # Raise error for non-successful HTTP status codes
            print(f"Response status: {response.status_code}")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
    return None

# Function to extract perfume information
def extract_perfume_info(url):
    try:
        print(f"Extracting perfume information from: {url}")
        response = flaresolverr_request(url)
        if response and 'solution' in response and 'response' in response['solution']:
            soup = BeautifulSoup(response['solution']['response'], 'html.parser')

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
            print(f"Extracted brand: {brand}")
            
            # Clean the name by removing the brand name if it appears at the end
            if brand != 'N/A' and name.endswith(brand):
                name = name[:-len(brand)].strip()
                
            print(f"Extracted name: {name}")

            # Extract gender
            gender_element = soup.select_one('h1 small')
            gender = gender_element.get_text(strip=True) if gender_element else 'N/A'
            print(f"Extracted gender: {gender}")

            # Extract year launched
            year = 'N/A'
            description_element = soup.select_one('div[itemprop="description"]')
            if description_element:
                description_text = description_element.get_text(strip=True)
                import re
                year_match = re.search(r'launched in (\d{4})', description_text)
                if year_match:
                    year = year_match.group(1)
            print(f"Extracted year: {year}")

            # Extract ratings
            rating_value_element = soup.select_one('span[itemprop="ratingValue"]')
            rating_value = rating_value_element.get_text(strip=True) if rating_value_element else 'N/A'
            print(f"Extracted rating value: {rating_value}")

            rating_count_element = soup.select_one('span[itemprop="ratingCount"]')
            rating_count = rating_count_element.get_text(strip=True) if rating_count_element else 'N/A'
            print(f"Extracted rating count: {rating_count}")

            # Extract main accords
            main_accords_elements = soup.select('.accord-bar')
            main_accords = [element.get_text(strip=True) for element in main_accords_elements]
            print(f"Extracted main accords: {main_accords}")

            # Extract perfumer information
            perfumers_elements = soup.select('.cell a[href*="/noses/"]')
            perfumers = [element.get_text(strip=True) for element in perfumers_elements]
            print(f"Extracted perfumers: {perfumers}")

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
            print(f"Extracted description: {len(description)} characters")

            # Extract longevity and sillage ratings
            longevity_element = soup.select_one('longevity-rating p')
            longevity = longevity_element.get_text(strip=True).replace('Perfume longevity:', '').strip() if longevity_element else 'N/A'
            print(f"Extracted longevity: {longevity}")

            sillage_element = soup.select_one('sillage-rating p')
            sillage = sillage_element.get_text(strip=True).replace('Perfume sillage:', '').strip() if sillage_element else 'N/A'
            print(f"Extracted sillage: {sillage}")

            # Extract image URL
            image_element = soup.select_one('img[itemprop="image"]')
            image_url = image_element['src'] if image_element and 'src' in image_element.attrs else 'N/A'
            print(f"Extracted image URL: {image_url}")

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
                    print(f"Error parsing notes from description: {e}")
            
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
                    print(f"Error finding note sections: {e}")
            
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
            
            print(f"Extracted top notes: {top_notes}")
            print(f"Extracted middle notes: {middle_notes}")
            print(f"Extracted base notes: {base_notes}")

            return {
                "Name": name,
                "Brand": brand,
                "Gender": gender,
                "Year": year,
                "Rating Value": rating_value,
                "Rating Count": rating_count,
                "Main Accords": ','.join(main_accords) if isinstance(main_accords, list) else main_accords,
                "Perfumers": ','.join(perfumers) if isinstance(perfumers, list) else perfumers,
                "Top Notes": ','.join(top_notes) if top_notes else 'N/A',
                "Middle Notes": ','.join(middle_notes) if middle_notes else 'N/A',
                "Base Notes": ','.join(base_notes) if base_notes else 'N/A',
                "Longevity": longevity,
                "Sillage": sillage,
                "Description": description,
                "Image URL": image_url,
                "URL": url
            }
        else:
            print(f"Error processing URL: {url}")
            return {
                "Name": 'N/A',
                "Brand": 'N/A',
                "Gender": 'N/A',
                "Year": 'N/A',
                "Rating Value": 'N/A',
                "Rating Count": 'N/A',
                "Main Accords": 'N/A',
                "Perfumers": 'N/A',
                "Top Notes": 'N/A',
                "Middle Notes": 'N/A',
                "Base Notes": 'N/A',
                "Longevity": 'N/A',
                "Sillage": 'N/A',
                "Description": 'N/A',
                "Image URL": 'N/A',
                "URL": url
            }
    except Exception as e:
        print(f"Error extracting info from {url}: {e}")
        return {
            "Name": 'Error',
            "Brand": 'N/A',
            "Gender": 'N/A',
            "Year": 'N/A',
            "Rating Value": 'N/A',
            "Rating Count": 'N/A',
            "Main Accords": 'N/A',
            "Perfumers": 'N/A',
            "Top Notes": 'N/A',
            "Middle Notes": 'N/A',
            "Base Notes": 'N/A',
            "Longevity": 'N/A',
            "Sillage": 'N/A',
            "Description": f'Error: {str(e)}',
            "Image URL": 'N/A',
            "URL": url
        }

# Function to get links to process
def get_perfume_links(filename='fra_per_links.txt'):
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found. Creating an empty file.")
        with open(filename, 'w') as f:
            pass
        return []
    
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

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
        with self.lock:
            with open(self.output_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(row_dict)

# Process a batch of URLs
def process_url_batch(urls, csv_writer, start_idx, total_urls):
    results = []
    for i, url in enumerate(urls):
        try:
            # Check control file
            control_command = read_control_file()
            if control_command == "pause":
                print("Script paused. Change control.txt to 'run' to continue.")
                while read_control_file() == "pause":
                    time.sleep(10)
            elif control_command == "abort":
                print("Script aborted.")
                break
                
            overall_idx = start_idx + i
            print(f"Processing URL {overall_idx+1}/{total_urls}: {url}")
            
            # Get the perfume info
            perfume_info = extract_perfume_info(url)
            
            # Write to CSV
            csv_writer.write_row(perfume_info)
            print(f"Data from {url} written to CSV")
            
            # Short random delay between requests within a worker
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
    
    return results

# Main function
def main():
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    # Output CSV file
    output_csv = os.path.join(output_dir, 'fragrance_data.csv')
    
    # Get perfume links
    urls = get_perfume_links()
    if not urls:
        print("No perfume links found. Please add links to fra_per_links.txt.")
        print("Example link format: https://www.fragrantica.com/perfume/Brand/Perfume-Name-ID.html")
        return
    
    total_urls = len(urls)
    print(f"Total URLs to process: {total_urls}")
    
    # Define CSV fields
    fieldnames = [
        "Name", "Brand", "Gender", "Year", "Rating Value", "Rating Count", "Main Accords", 
        "Perfumers", "Top Notes", "Middle Notes", "Base Notes", "Longevity", "Sillage", "Description", "Image URL", "URL"
    ]
    
    # Create thread-safe CSV writer
    csv_writer = ThreadSafeWriter(output_csv, fieldnames)
    
    # Parallel processing settings
    batch_size = 10  # URLs per batch
    max_workers = 5  # Parallel workers
    total_batches = (total_urls + batch_size - 1) // batch_size  # Ceiling division
    
    print(f"Processing URLs in {total_batches} batches with {max_workers} parallel workers")
    
    # Process in batches
    for batch_idx in tqdm(range(0, total_batches), desc="Processing batches", unit="batch"):
        # Check if we should abort
        if read_control_file() == "abort":
            print("Script aborted.")
            break
            
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, total_urls)
        batch_urls = urls[start_idx:end_idx]
        
        print(f"\nProcessing batch {batch_idx+1}/{total_batches} (URLs {start_idx+1}-{end_idx})")
        
        # For small batches, process sequentially to avoid overhead
        if len(batch_urls) <= 2:
            process_url_batch(batch_urls, csv_writer, start_idx, total_urls)
        else:
            # Split the batch into chunks for parallel processing
            chunk_size = max(1, len(batch_urls) // max_workers)
            chunks = [batch_urls[i:i+chunk_size] for i in range(0, len(batch_urls), chunk_size)]
            
            # Process chunks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit tasks
                futures = []
                for i, chunk in enumerate(chunks):
                    chunk_start_idx = start_idx + (i * chunk_size)
                    futures.append(executor.submit(process_url_batch, chunk, csv_writer, chunk_start_idx, total_urls))
                
                # Wait for completion with progress bar
                for future in tqdm(concurrent.futures.as_completed(futures), 
                                  total=len(futures), 
                                  desc=f"Batch {batch_idx+1} progress", 
                                  unit="chunk"):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error in batch processing: {e}")
        
        # Pause between batches to avoid being rate-limited
        if batch_idx < total_batches - 1:  # Skip pause after the last batch
            pause_duration = 5  # 5 seconds between batches
            print(f"Pausing for {pause_duration} seconds between batches...")
            time.sleep(pause_duration)
    
    print(f"Scraping completed. Data saved to {output_csv}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Browser closed.")
