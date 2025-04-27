import csv
import os
import random
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import chromedriver_autoinstaller

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
def flaresolverr_request(url, retries=3, delay=5):
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
    print(f"Extracting perfume information from: {url}")
    response = flaresolverr_request(url)
    if response and 'solution' in response and 'response' in response['solution']:
        soup = BeautifulSoup(response['solution']['response'], 'html.parser')

        # Update CSS selectors
        name_element = soup.select_one('#toptop > h1')
        name = name_element.get_text(strip=True) if name_element else 'N/A'
        print(f"Extracted name: {name}")

        gender_element = soup.select_one('#toptop > h1 > small')
        gender = gender_element.get_text(strip=True) if gender_element else 'N/A'
        print(f"Extracted gender: {gender}")

        rating_value_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(1)')
        rating_value = rating_value_element.get_text(strip=True) if rating_value_element else 'N/A'
        print(f"Extracted rating value: {rating_value}")

        rating_count_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(3)')
        rating_count = rating_count_element.get_text(strip=True) if rating_count_element else 'N/A'
        print(f"Extracted rating count: {rating_count}")

        main_accords_elements = soup.select('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div > div.accord-bar')
        main_accords = [element.get_text(strip=True) for element in main_accords_elements]
        print(f"Extracted main accords: {main_accords}")

        perfumers_elements = soup.select('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(3) > div.grid-x.grid-padding-x.grid-padding-y.small-up-2.medium-up-2 > div > a')
        perfumers = [element.get_text(strip=True) for element in perfumers_elements]
        print(f"Extracted perfumers: {perfumers}")

        description_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(5) > div > p:nth-child(1)')
        description = description_element.get_text(strip=True) if description_element else 'N/A'
        print(f"Extracted description: {description}")

        # Try to extract notes
        top_notes_div = soup.select_one('div.cell.notes-box.top-notes')
        top_notes = []
        if top_notes_div:
            note_elements = top_notes_div.select('div.cell.text-center')
            top_notes = [note.select_one('div.nowrap').get_text(strip=True) if note.select_one('div.nowrap') else "Unknown" for note in note_elements]
        
        middle_notes_div = soup.select_one('div.cell.notes-box.middle-notes')
        middle_notes = []
        if middle_notes_div:
            note_elements = middle_notes_div.select('div.cell.text-center')
            middle_notes = [note.select_one('div.nowrap').get_text(strip=True) if note.select_one('div.nowrap') else "Unknown" for note in note_elements]
        
        base_notes_div = soup.select_one('div.cell.notes-box.base-notes')
        base_notes = []
        if base_notes_div:
            note_elements = base_notes_div.select('div.cell.text-center')
            base_notes = [note.select_one('div.nowrap').get_text(strip=True) if note.select_one('div.nowrap') else "Unknown" for note in note_elements]

        return {
            "Name": name,
            "Gender": gender,
            "Rating Value": rating_value,
            "Rating Count": rating_count,
            "Main Accords": ','.join(main_accords) if isinstance(main_accords, list) else main_accords,
            "Perfumers": ','.join(perfumers) if isinstance(perfumers, list) else perfumers,
            "Top Notes": ','.join(top_notes) if top_notes else 'N/A',
            "Middle Notes": ','.join(middle_notes) if middle_notes else 'N/A',
            "Base Notes": ','.join(base_notes) if base_notes else 'N/A',
            "Description": description,
            "URL": url
        }
    else:
        print(f"Error processing URL: {url}")
        return {
            "Name": 'N/A',
            "Gender": 'N/A',
            "Rating Value": 'N/A',
            "Rating Count": 'N/A',
            "Main Accords": 'N/A',
            "Perfumers": 'N/A',
            "Top Notes": 'N/A',
            "Middle Notes": 'N/A',
            "Base Notes": 'N/A',
            "Description": 'N/A',
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
    
    print(f"Total URLs to process: {len(urls)}")
    
    # Open CSV file in append mode
    file_exists = os.path.exists(output_csv)
    with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = [
            "Name", "Gender", "Rating Value", "Rating Count", "Main Accords", 
            "Perfumers", "Top Notes", "Middle Notes", "Base Notes", "Description", "URL"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header only if file doesn't exist
        if not file_exists:
            writer.writeheader()
        
        iteration_count = 0
        max_iterations = 10  # Process 10 fragrances before pausing
        
        for i, url in enumerate(urls):
            # Check control file
            control_command = read_control_file()
            if control_command == "pause":
                print("Script paused. Change control.txt to 'run' to continue.")
                while read_control_file() == "pause":
                    time.sleep(10)
            elif control_command == "abort":
                print("Script aborted.")
                break
            
            # Pause periodically to avoid being blocked
            if iteration_count >= max_iterations:
                pause_duration = 300  # 5 minutes
                print(f'Pausing for {pause_duration // 60} minutes to avoid rate limiting...')
                time.sleep(pause_duration)
                iteration_count = 0
            
            print(f"Processing URL {i+1}/{len(urls)}: {url}")
            perfume_info = extract_perfume_info(url)
            writer.writerow(perfume_info)
            print(f"Data from {url} written to CSV")
            
            iteration_count += 1
            time.sleep(random.uniform(2, 5))  # Random delay between requests
    
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
