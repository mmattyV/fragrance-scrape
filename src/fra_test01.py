import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.fragrantica.com/perfume/Giorgio-Armani/Acqua-di-Gio-Profumo-29727.html'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Name
    name_element = soup.select_one('#toptop > h1')
    name = name_element.get_text(strip=True) if name_element else 'N/A'

    # Gender
    gender_element = soup.select_one('#toptop > h1 > small')
    gender = gender_element.get_text(strip=True) if gender_element else 'N/A'

    # Rating Value
    rating_value_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(1)')
    rating_value = rating_value_element.get_text(strip=True) if rating_value_element else 'N/A'

    # Rating Count
    rating_count_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(3)')
    rating_count = rating_count_element.get_text(strip=True) if rating_count_element else 'N/A'

    # Main Accords
    main_accords_elements = soup.select('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div > div.accord-bar')
    main_accords = [element.get_text(strip=True) for element in main_accords_elements]

    # Perfumers
    perfumers_elements = soup.select('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(3) > div.grid-x.grid-padding-x.grid-padding-y.small-up-2.medium-up-2 > div > a')
    perfumers = [element.get_text(strip=True) for element in perfumers_elements]

    data = {
        "Name": name,
        "Gender": gender,
        "Rating Value": rating_value,
        "Rating Count": rating_count,
        "Main Accords": main_accords,
        "Perfumers": perfumers
    }

    with open('fra_per_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Data saved to fra_per_data.json: {data}")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")



