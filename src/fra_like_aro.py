import csv
import os
import random
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

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

    return {
        "Name": name,
        "Gender": gender,
        "Rating Value": rating_value,
        "Rating Count": rating_count,
        "Main Accords": main_accords,
        "Perfumers": perfumers,
        "URL": url
    }

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
    'cookies00.json', 'cookies01.json', 'cookies02.json', 'cookies03.json', 'cookies04.json',
    'cookies05.json', 'cookies06.json', 'cookies07.json', 'cookies08.json', 'cookies09.json',
    'cookies10.json', 'cookies11.json', 'cookies12.json', 'cookies13.json', 'cookies14.json',
    'cookies15.json', 'cookies16.json', 'cookies17.json', 'cookies18.json', 'cookies19.json',
    'cookies20.json', 'cookies21.json', 'cookies22.json', 'cookies23.json', 'cookies24.json',
    'cookies25.json', 'cookies26.json', 'cookies27.json', 'cookies28.json', 'cookies29.json',
    'cookies30.json', 'cookies31.json', 'cookies32.json', 'cookies33.json', 'cookies34.json',
    'cookies35.json', 'cookies36.json', 'cookies37.json', 'cookies38.json', 'cookies39.json',
    'cookies40.json', 'cookies41.json', 'cookies42.json', 'cookies43.json', 'cookies44.json',
    'cookies45.json', 'cookies46.json', 'cookies47.json', 'cookies48.json', 'cookies49.json',
    'cookies50.json', 'cookies51.json', 'cookies52.json', 'cookies53.json', 'cookies54.json',
    'cookies55.json', 'cookies56.json', 'cookies57.json', 'cookies58.json', 'cookies59.json',
    'cookies60.json', 'cookies61.json', 'cookies62.json', 'cookies63.json', 'cookies64.json',
    'cookies65.json', 'cookies66.json', 'cookies67.json', 'cookies68.json', 'cookies69.json',
    'cookies70.json'
]

# Función para añadir cookies al navegador
def add_cookies(driver, cookies):
    driver.get('https://www.fragrantica.com')  # Navegar al dominio correcto antes de añadir cookies
    for cookie in cookies:
        driver.add_cookie(cookie)
    print(f"Cookies from {current_cookie_file} added successfully.")

# Cargar la primera cookie
current_cookie_file = cookie_files[0]
current_cookies = load_cookies(current_cookie_file)
add_cookies(driver, current_cookies)

# Contador de iteraciones
iteration_count = 0
max_iterations = 10

# Función principal
def main():
    global iteration_count  # Declarar iteration_count como global

    # Leer las URLs desde el archivo perfume_links.txt
    with open('fra_per_links.txt', 'r') as file:
        urls = [line.strip() for line in file]

    # Verificar si el archivo ya existe
    file_exists = os.path.isfile('fragrance_data_test.csv')

    with open('fragrance_data_test.csv', mode='a', newline='', encoding='utf-8') as file:
        fieldnames = [
            "Name", "Gender", "Rating Value", "Rating Count", "Main Accords", "Perfumers", "URL"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Escribir el encabezado solo si el archivo no existe
        if not file_exists:
            writer.writeheader()

        for url in urls:
            # Verificar si se debe pausar la ejecución
            if read_control_file() == "pause":
                print("Script pausado. Cambia el contenido de control.txt para continuar.")
                while read_control_file() == "pause":
                    time.sleep(10)

            if read_control_file() == "abort":
                print("Script abortado.")
                break

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
