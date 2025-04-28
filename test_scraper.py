import os
import random
import time
from mac_fra_scraper import extract_perfume_info, driver
import csv

# Create a small test set of URLs (first 5 from the full list)
def get_test_links():
    with open('fra_per_links.txt', 'r') as file:
        return [line.strip() for line in file][:5]  # Get first 5 links

# Main function for testing
def main():
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    # Output CSV file for testing
    output_csv = os.path.join(output_dir, 'test_fragrances.csv')
    
    # Get test perfume links
    test_urls = get_test_links()
    print(f"Testing with {len(test_urls)} URLs")
    
    # Open CSV file
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = [
            "Name", "Brand", "Gender", "Year", "Rating Value", "Rating Count", "Main Accords", 
            "Perfumers", "Top Notes", "Middle Notes", "Base Notes", "Longevity", "Sillage", "Description", "Image URL", "URL"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, url in enumerate(test_urls):
            print(f"Processing test URL {i+1}/{len(test_urls)}: {url}")
            perfume_info = extract_perfume_info(url)
            writer.writerow(perfume_info)
            print(f"Test data from {url} written to CSV")
            
            time.sleep(random.uniform(2, 5))  # Random delay between requests
    
    print(f"Test scraping completed. Data saved to {output_csv}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        driver.quit()
        print("Browser closed.")
