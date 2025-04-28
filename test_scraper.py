import os
import sys
import csv
import logging
from fra_scraper import extract_perfume_info, ThreadSafeWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Test URLs, including ones likely to have formatting challenges
TEST_URLS = [
    "https://www.fragrantica.com/perfume/A-Dozen-Roses/Gold-Rush-12963.html",  # The one with issues
    "https://www.fragrantica.com/perfume/Bond-No-9/High-Line-7503.html",       # Another problematic one
    "https://www.fragrantica.com/perfume/Byredo/Mojave-Ghost-25020.html"       # A regular one for comparison
]

def test_scraper():
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    # Output CSV file
    output_csv = os.path.join(output_dir, 'test_fragrance_data.csv')
    
    # Define CSV fields
    fieldnames = [
        "Name", "Brand", "Gender", "Year", "Rating Value", "Rating Count", "Main Accords", 
        "Perfumers", "Top Notes", "Middle Notes", "Base Notes", "Longevity", "Sillage", "Description", "Image URL", "URL"
    ]
    
    # Create CSV writer
    csv_writer = ThreadSafeWriter(output_csv, fieldnames)
    
    # Process test URLs
    for url in TEST_URLS:
        logging.info(f"Testing extraction for URL: {url}")
        try:
            # Extract perfume info
            perfume_info = extract_perfume_info(url)
            
            # Check if data was extracted successfully
            if perfume_info:
                # Write data to CSV
                csv_writer.write_row(perfume_info)
                logging.info(f"Successfully processed: {url}")
                
                # Print data for verification
                for key, value in perfume_info.items():
                    logging.info(f"{key}: {value}")
            else:
                logging.error(f"Failed to extract data from: {url}")
        except Exception as e:
            logging.error(f"Error processing {url}: {e}")
    
    logging.info(f"Test completed. Output written to {output_csv}")

if __name__ == "__main__":
    test_scraper()
