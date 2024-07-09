import csv
import os
import random
import json
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

# Ruta al archivo de control
control_file_path = 'control.txt'

# Función para leer el archivo de control
def read_control_file():
    with open(control_file_path, 'r') as file:
        return file.read().strip()

# Función para extraer información del perfume
def extract_perfume_info(driver, url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    name = soup.find('span', class_='perfume-page__title-name').text.strip() if soup.find('span', class_='perfume-page__title-name') else 'N/A'
    brand = soup.find('span', class_='perfume-page__title-brand').text.strip() if soup.find('span', class_='perfume-page__title-brand') else 'N/A'
    type_ = soup.find('span', class_='perfume-page__title-type').text.strip() if soup.find('span', class_='perfume-page__title-type') else 'N/A'
    
    rating_value = soup.find('div', class_='comments-and-reviews__value').text.strip() if soup.find('div', class_='comments-and-reviews__value') else 'N/A'
    rating_count = soup.find('div', class_='comments-and-reviews__reviews-count').text.strip() if soup.find('div', class_='comments-and-reviews__reviews-count') else 'N/A'
    
    # Limpiar los valores extraídos
    rating_value = rating_value.replace("\n", "").strip()
    rating_count = rating_count.replace("\n", "").strip()
    
    gender = soup.select_one('#facts > div > div > div:nth-child(6) > div.info-table-row__entry').text.strip() if soup.select_one('#facts > div > div > div:nth-child(6) > div.info-table-row__entry') else 'N/A'
    country = soup.select_one('#facts > div > div > div:nth-child(5) > div.info-table-row__entry > span > a').text.strip() if soup.select_one('#facts > div > div > div:nth-child(5) > div.info-table-row__entry > span > a') else 'N/A'
    
    return [name, brand, type_, rating_value, rating_count, gender, country]

# Función para cargar cookies desde archivos JSON y filtrarlas
def load_cookies(file_path):
    with open(file_path, 'r') as file:
        cookies = json.load(file)
    # Filtrar cookies para asegurarse de que 'sameSite' esté correcto
    for cookie in cookies:
        if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
            del cookie['sameSite']
    return cookies

# Lista de archivos de cookies
cookie_files = [
    'arocook00.json', 'arocook01.json', 'arocook02.json', 'arocook03.json', 'arocook04.json',
    'arocook05.json', 'arocook06.json', 'arocook07.json', 'arocook08.json', 'arocook09.json',
    'arocook10.json', 'arocook11.json', 'arocook12.json', 'arocook13.json', 'arocook14.json',
    'arocook15.json', 'arocook16.json', 'arocook17.json', 'arocook18.json', 'arocook19.json',
    'arocook20.json'
]

# Función para añadir cookies al navegador
def add_cookies(driver, cookies):
    driver.get('https://www.aromo.ru')  # Navegar al dominio correcto antes de añadir cookies
    for cookie in cookies:
        driver.add_cookie(cookie)
    print(f"Cookies from {current_cookie_file} added successfully.")

# Cargar la primera cookie
current_cookie_file = cookie_files[0]
current_cookies = load_cookies(current_cookie_file)
add_cookies(driver, current_cookies)

# Contador de iteraciones
iteration_count = 0
max_iterations = 800

# Función principal
def main():
    # Leer las URLs desde el archivo perfume_links.txt
    with open('perfume_links.txt', 'r') as file:
        urls = [line.strip() for line in file]

    with open('perfumes.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Brand', 'Type', 'Rating Value', 'Rating Count', 'Gender', 'Country'])

        for url in urls:
            if iteration_count >= max_iterations:
                # Pausar el script por 5 minutos
                print('Pausando por 5 minutos...')
                time.sleep(300)
                
                # Seleccionar un archivo de cookies al azar y cargarlo
                current_cookie_file = random.choice(cookie_files)
                current_cookies = load_cookies(current_cookie_file)
                
                # Limpiar cookies actuales y agregar las nuevas
                driver.delete_all_cookies()
                add_cookies(driver, current_cookies)
                
                # Reiniciar el contador de iteraciones
                iteration_count = 0
            
            perfume_info = extract_perfume_info(driver, url)
            writer.writerow(perfume_info)
            print(f"Scraped data from {url}")

            iteration_count += 1
            time.sleep(1)  # Pausa opcional para evitar bloqueos

if __name__ == "__main__":
    main()

driver.quit()
print("Scraping completado.")



