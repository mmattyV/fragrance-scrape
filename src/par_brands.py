# par_brands.py

import requests
from bs4 import BeautifulSoup

# URL to scrape
url = "https://www.parfumo.com/Popular_Brands"

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Send a GET request to the URL with headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Open a file to write the brand links
    with open("par_brand_links.txt", "w") as file:
        # Iterate over each letter section
        for letter in "abcdefghijklmnopqrstuvwxyz":
            selector = f"#letter_{letter} > div.brands_list.p-boxes-3 > a"
            brand_elements = soup.select(selector)
            for element in brand_elements:
                brand_url = element.get("href")
                full_url = f"https://www.parfumo.com{brand_url}"
                file.write(f"{full_url}\n")

    print("Brand links have been saved to par_brand_links.txt")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

