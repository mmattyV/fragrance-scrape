import requests
from bs4 import BeautifulSoup
import json
import time
import random

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def parse_perfume_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extracting Name
    name_element = soup.select_one('#toptop > h1')
    name = name_element.get_text(strip=True) if name_element else 'N/A'
    
    # Extracting Gender
    gender_element = soup.select_one('#toptop > h1 > small')
    gender = gender_element.get_text(strip=True) if gender_element else 'N/A'
    
    # Extracting Rating Value
    rating_value_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(1)')
    rating_value = rating_value_element.get_text(strip=True) if rating_value_element else 'N/A'
    
    # Extracting Rating Count
    rating_count_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(3)')
    rating_count = rating_count_element.get_text(strip=True) if rating_count_element else 'N/A'
    
    return {
        'Name': name,
        'Gender': gender,
        'Rating Value': rating_value,
        'Rating Count': rating_count
    }

def save_to_json(data, filename='fra_per_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    url = 'https://www.fragrantica.com/perfume/Giorgio-Armani/Acqua-di-Gio-Profumo-29727.html'
    html = get_html(url)
    if html:
        perfume_data = parse_perfume_page(html)
        save_to_json(perfume_data)
        print("Data saved to fra_per_data.json")
    else:
        print("No data to save")

if __name__ == "__main__":
    main()









