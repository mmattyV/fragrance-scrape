import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Ruta al ChromeDriver (reemplaza con la ruta real en tu sistema)
chrome_driver_path = 'C:\\chromedriver\\chromedriver.exe'

# Configuración del servicio de Chrome
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

def extract_perfume_info(driver, url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def extract_href(soup, pattern):
        elements = soup.find_all('a', href=lambda href: href and pattern in href)
        return [element.text.strip() for element in elements]

    name = soup.find('h1', class_='product-name').text.strip() if soup.find('h1', class_='product-name') else 'N/A'
    brand = ', '.join(extract_href(soup, '/brands/'))
    segment = ', '.join(extract_href(soup, '/segments/'))
    nose = ', '.join(extract_href(soup, '/noses/'))
    year = ', '.join(extract_href(soup, '/years/'))
    family = ', '.join(extract_href(soup, '/families/'))
    concentration = ', '.join(extract_href(soup, '/concentrations/'))
    region = ', '.join(extract_href(soup, '/regions/'))
    gender = soup.find('div', class_='info-table-row__entry').text.strip() if soup.find('div', class_='info-table-row__entry') else 'N/A'
    
    main_accords = soup.find('div', string='Основные аккорды').find_next('div').text.strip() if soup.find('div', string='Основные аккорды') else 'N/A'
    notes = ', '.join(extract_href(soup, '/notes/'))

    rating_value = soup.find('span', class_='comments-and-reviews__value').text.strip() if soup.find('span', class_='comments-and-reviews__value') else 'N/A'
    rating_count = soup.find('span', class_='comments-and-reviews__count').text.strip() if soup.find('span', class_='comments-and-reviews__count') else 'N/A'

    return {
        "name": name,
        "brand": brand,
        "segment": segment,
        "nose": nose,
        "year": year,
        "family": family,
        "concentration": concentration,
        "region": region,
        "gender": gender,
        "main_accords": main_accords,
        "notes": notes,
        "rating_value": rating_value,
        "rating_count": rating_count,
        "url": url
    }

# Inicializar el WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Leer los enlaces desde el archivo perfume_links.txt
with open('perfume_links.txt', 'r', encoding='utf-8') as file:
    all_links = file.read().splitlines()

# Leer los enlaces ya procesados desde el archivo perfumes_test.csv (archivo temporal)
processed_links = set()
if os.path.exists('perfumes_test.csv'):
    with open('perfumes_test.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar la cabecera
        for row in reader:
            processed_links.add(row[-1])  # Asumimos que la URL está en la última columna

# Filtrar los enlaces que no han sido procesados
remaining_links = [link for link in all_links if link not in processed_links]

# Limitar a 10 enlaces para el modo de prueba
test_links = remaining_links[:10]

# Continuar guardando los datos en el archivo CSV temporal
with open('perfumes_test.csv', mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    for link in test_links:
        print(f'Extrayendo información del perfume: {link}')
        try:
            perfume_info = extract_perfume_info(driver, link)
            # Imprimir los datos extraídos para verificación
            print(perfume_info)
            writer.writerow([
                perfume_info["name"],
                perfume_info["brand"],
                perfume_info["segment"],
                perfume_info["nose"],
                perfume_info["year"],
                perfume_info["family"],
                perfume_info["concentration"],
                perfume_info["region"],
                perfume_info["gender"],
                perfume_info["main_accords"],
                perfume_info["notes"],
                perfume_info["rating_value"],
                perfume_info["rating_count"],
                perfume_info["url"]
            ])
            time.sleep(2)  # Espera para evitar ser bloqueado por el sitio web
        except Exception as e:
            print(f'Error al extraer información del perfume: {link} - {e}')

# Cerrar el driver
driver.quit()

print("Modo de prueba completado. Revisa los resultados en 'perfumes_test.csv' antes de continuar.")

