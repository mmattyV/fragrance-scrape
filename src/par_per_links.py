# par_per.py

import requests
from bs4 import BeautifulSoup
import time
import os

# Encabezados para imitar una solicitud del navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Rutas de archivo
brand_links_file = "par_brand_links.txt"  # Archivo con los enlaces corregidos
perfume_links_file = "par_link_per.txt"
control_file = "control.txt"

# Leer el archivo de control para reanudar el scraping
def read_control_file():
    if os.path.exists(control_file):
        with open(control_file, "r") as file:
            last_processed_brand = file.readline().strip()
            return last_processed_brand
    return None

# Escribir la última marca procesada en el archivo de control
def write_control_file(brand_url):
    with open(control_file, "w") as file:
        file.write(brand_url + "\n")

# Leer los enlaces de marcas del archivo
def read_brand_links():
    with open(brand_links_file, "r") as file:
        return [line.strip() for line in file.readlines()]

# Agregar enlaces de perfumes al archivo
def append_perfume_links(perfume_links):
    with open(perfume_links_file, "a") as file:
        for link in perfume_links:
            file.write(link + "\n")

# Scraping de enlaces de perfumes de una página de marca
def scrape_perfume_links(brand_url):
    perfume_links = []
    page = 1
    while True:
        paginated_url = f"{brand_url}?current_page={page}&v=grid&o=n_asc&g_f=1&g_m=1&g_u=1"
        print(f"Scraping URL: {paginated_url}")
        response = requests.get(paginated_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page} for {brand_url}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        perfume_elements = soup.select("body > div.body-wrapper.w-100 > div > div.main > div.pgrid.mb-1.mt-1 > div > div.image > a")
        
        if not perfume_elements:
            break

        for element in perfume_elements:
            perfume_url = element.get("href")
            full_url = f"https://www.parfumo.com{perfume_url}"
            perfume_links.append(full_url)

        # Comprobar si hay más páginas
        next_page = soup.select_one("body > div.body-wrapper.w-100 > div > div.main > div:nth-child(5) > div.paging_nrs.flex > div.numbers > div.active + div > a")
        if not next_page:
            break

        page += 1
        time.sleep(1)  # Para evitar abrumar el servidor

    return perfume_links

def main():
    brand_links = read_brand_links()
    last_processed_brand = read_control_file()
    
    start_index = 0
    if last_processed_brand:
        start_index = brand_links.index(last_processed_brand) + 1

    for index in range(start_index, len(brand_links)):
        brand_url = brand_links[index]
        print(f"Procesando {brand_url}...")
        perfume_links = scrape_perfume_links(brand_url)
        append_perfume_links(perfume_links)
        write_control_file(brand_url)
        time.sleep(2)  # Para evitar abrumar el servidor

    print("Scraping completado.")

if __name__ == "__main__":
    main()


