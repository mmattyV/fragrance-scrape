import requests
from bs4 import BeautifulSoup
import json
import re
import time

def extract_perfume_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract Name
        name = soup.select_one('#toptop > h1').get_text(strip=True)

        # Extract Gender
        gender = soup.select_one('#toptop > h1 > small').get_text(strip=True)

        # Extract Rating Value
        rating_value = soup.select_one('#main-content span[itemprop="ratingValue"]').get_text(strip=True)

        # Extract Rating Count
        rating_count = soup.select_one('#main-content span[itemprop="ratingCount"]').get_text(strip=True)

        # Extract Main Accords
        main_accords_elements = soup.select('#main-content div.accord-bar')
        main_accords = [elem.get_text(strip=True) for elem in main_accords_elements]

        # Extract Perfumers
        perfumers_elements = soup.select('#main-content div.grid-x a[href*="/noses/"]')
        perfumers = [elem.get_text(strip=True) for elem in perfumers_elements]

        # Extract Notes
        def extract_notes(soup, note_type):
            note_section = soup.find('h4', string=note_type)
            if note_section:
                notes_div = note_section.find_next_sibling('div')
                note_elements = notes_div.select('a span.link-span') if notes_div else []
                return [note.get_text(strip=True) for note in note_elements]
            else:
                return []

        top_notes = extract_notes(soup, "Top Notes")
        middle_notes = extract_notes(soup, "Middle Notes")
        base_notes = extract_notes(soup, "Base Notes")

        data = {
            'Name': name,
            'Gender': gender,
            'Rating Value': rating_value,
            'Rating Count': rating_count,
            'Main Accords': main_accords,
            'Perfumers': perfumers,
            'Top Notes': top_notes,
            'Middle Notes': middle_notes,
            'Base Notes': base_notes
        }

        return data
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def read_brand_links(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def check_control_file():
    try:
        with open('control.txt', 'r') as file:
            content = file.read().strip().lower()
            if content == 'pause':
                print("Pausing... Change 'control.txt' to 'resume' to continue.")
                while True:
                    with open('control.txt', 'r') as file:
                        if file.read().strip().lower() == 'resume':
                            print("Resuming...")
                            break
                    time.sleep(5)
            elif content == 'abort':
                print("Aborting the script.")
                exit()
    except FileNotFoundError:
        pass

def main():
    brand_links = read_brand_links('fra_masked_brand_links.txt')
    all_perfume_data = []

    for brand_link in brand_links:
        # Simulate replacing ".*" with actual perfume names
        for i in range(1, 4):  # This is just an example to create a few test URLs
            perfume_link = re.sub(r'\.\*\.', f'{i}.', brand_link)
            print(f"Processing URL: {perfume_link}")

            check_control_file()  # Check control file for pause or abort

            data = extract_perfume_data(perfume_link)
            if data:
                all_perfume_data.append(data)

    with open('all_perfume_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_perfume_data, f, ensure_ascii=False, indent=4)

    print(f"Data saved to all_perfume_data.json: {all_perfume_data}")

if __name__ == '__main__':
    main()








