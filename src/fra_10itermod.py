import csv
import os
import random
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Configuración de FlareSolverr
FLARESOLVERR_URL = 'http://localhost:8191/v1'

# Ruta al ChromeDriver
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

# Función para realizar solicitudes a través de FlareSolverr
def flaresolverr_request(url):
    payload = {
        'cmd': 'request.get',
        'url': url,
        'maxTimeout': 60000
    }
    response = requests.post(FLARESOLVERR_URL, json=payload)
    return response.json()

# Función para extraer información del perfume
def extract_perfume_info(url):
    response = flaresolverr_request(url)
    soup = BeautifulSoup(response['solution']['response'], 'html.parser')

    # Actualización de los selectores CSS
    name_element = soup.select_one('#toptop > h1')
    name = name_element.get_text(strip=True) if name_element else 'N/A'

    gender_element = soup.select_one('#toptop > h1 > small')
    gender = gender_element.get_text(strip=True) if gender_element else 'N/A'

    rating_value_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(1)')
    rating_value = rating_value_element.get_text(strip=True) if rating_value_element else 'N/A'

    rating_count_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(3)')
    rating_count = rating_count_element.get_text(strip=True) if rating_count_element else 'N/A'

    main_accords_elements = soup.select('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div > div.accord-bar')
    main_accords = [element.get_text(strip=True) for element in main_accords_elements]

    perfumers_elements = soup.select('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(3) > div.grid-x.grid-padding-x.grid-padding-y.small-up-2.medium-up-2 > div > a')
    perfumers = [element.get_text(strip=True) for element in perfumers_elements]

    return {
        "Name": name,
        "Gender": gender,
        "Rating Value": rating_value,
        "Rating Count": rating_count,
        "Main Accords": main_accords,
        "Perfumers": perfumers,
        "url": url
    }

# Lista de archivos de cookies
cookie_files = [
    'cookies00.json', 'cookies01.json', 'cookies02.json', 'cookies03.json', 'cookies04.json',
    'cookies05.json', 'cookies06.json', 'cookies07.json', 'cookies08.json', 'cookies09.json',
    'cookies10.json', 'cookies11.json', 'cookies12.json', 'cookies13.json', 'cookies14.json',
    'cookies15.json', 'cookies16.json', 'cookies17.json', 'cookies18.json', 'cookies19.json',
    'cookies20.json', 'cookies21.json', 'cookies22.json', 'cookies23.json', 'cookies24.json',
    'cookies25.json', 'cookies26.json', 'cookies27.json', 'cookies28.json', 'cookies29.json',
    'cookies30.json', 'cookies31.json', 'cookies32.json', 'cookies33.json', 'cookies34.json',
    'cookies35.json', 'cookies36.json', 'cookies37.json', 'cookies38.json', 'cookies39.json'
    ]

# Función para añadir cookies al navegador
def add_cookies(driver, cookies):
    driver.get('https://www.fragrantica.com')  # Navegar al dominio correcto antes de añadir cookies
    for cookie in cookies:
        if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
            del cookie['sameSite']
        driver.add_cookie(cookie)
    print(f"Cookies from {current_cookie_file} added successfully.")

# Cargar la primera cookie
current_cookie_file = cookie_files[0]
with open(current_cookie_file, 'r') as file:
    current_cookies = json.load(file)
add_cookies(driver, current_cookies)

# Contador de iteraciones
iteration_count = 0
max_iterations = 10

# Función principal
def main():
    global iteration_count  # Declarar iteration_count como global

    # Leer las URLs desde el archivo perfume_links.txt
    with open('perfume_links.txt', 'r') as file:
        urls = [line.strip() for line in file]

    # Abrir el archivo CSV en modo append
    with open('perfumes.csv', mode='a', newline='', encoding='utf-8') as file:
        fieldnames = [
            "Name", "Gender", "Rating Value", "Rating Count", "Main Accords", "Perfumers", "url"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Escribir el encabezado solo si el archivo está vacío
        if os.stat('perfumes.csv').st_size == 0:
            writer.writeheader()

        for url in urls:
            # Verificar el archivo de control
            control_command = read_control_file()
            if control_command == "pause":
                print("Script pausado. Cambia el contenido de control.txt para continuar.")
                while read_control_file() == "pause":
                    time.sleep(10)
            elif control_command == "abort":
                print("Script abortado.")
                break

            if iteration_count >= max_iterations:
                # Pausar el script por 5 minutos
                print('Pausando por 5 minutos...')
                time.sleep(300)
                
                # Seleccionar un archivo de cookies al azar y cargarlo
                current_cookie_file = random.choice(cookie_files)
                with open(current_cookie_file, 'r') as file:
                    current_cookies = json.load(file)
                
                # Limpiar cookies actuales y agregar las nuevas
                driver.delete_all_cookies()
                add_cookies(driver, current_cookies)
                
                # Reiniciar el contador de iteraciones
                iteration_count = 0
            
            perfume_info = extract_perfume_info(url)
            writer.writerow(perfume_info)
            print(f"Scraped data from {url}")

            iteration_count += 1
            time.sleep(1)  # Pausa opcional para evitar bloqueos

if __name__ == "__main__":
    main()

driver.quit()
print("Scraping completado.")
