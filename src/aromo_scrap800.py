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

# Ruta al archivo de control
control_file_path = 'control.txt'

def read_control_file():
    with open(control_file_path, 'r') as file:
        return file.read().strip()

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
    country = soup.select_one('#facts > div > div > div:nth-child(5) > div.info-table-row__entry > span > a')['href'].split('/')[-2] if soup.select_one('#facts > div > div > div:nth-child(5) > div.info-table-row__entry > span > a') else 'N/A'
    year = soup.select_one('#facts > div > div > div:nth-child(7) > div.info-table-row__entry > span > a').text.strip() if soup.select_one('#facts > div > div > div:nth-child(7) > div.info-table-row__entry > span > a') else 'N/A'
    segment = soup.select_one('#facts > div > div > div:nth-child(6) > div.info-table-row__entry > div > a')['href'].split('/')[-2] if soup.select_one('#facts > div > div > div:nth-child(6) > div.info-table-row__entry > div > a') else 'N/A'
    perfumers = [a['href'].split('/')[-2] for a in soup.select('#facts > div > div > div:nth-child(11) > div.info-table-row__content > div > div > a')]
    families = [a['href'].split('/')[-2] for a in soup.select('#pyramid > div > div > section.page-block-section.perfume-pyramid__groups > div > ul > li > a')]
    top_notes = [a['href'].split('/')[-2] for a in soup.select('#pyramid > div > div > section:nth-child(1) > div > figure > ul.composition-pyramid__top > li > a')]
    middle_notes = [a['href'].split('/')[-2] for a in soup.select('#pyramid > div > div > section:nth-child(1) > div > figure > ul.composition-pyramid__middle > li > a')]
    bottom_notes = [a['href'].split('/')[-2] for a in soup.select('#pyramid > div > div > section:nth-child(1) > div > figure > ul.composition-pyramid__bottom > li > a')]
    users_notes = [a['href'].split('/')[-2] for a in soup.select('#character > div > div > div.perfume-character__top > section.page-block-section.perfume-character__base-notes > div > div a')]

    return {
        "name": name,
        "brand": brand,
        "type": type_,
        "rating_value": rating_value,
        "rating_count": rating_count,
        "gender": gender,
        "country": country,
        "year": year,
        "segment": segment,
        "perfumers": perfumers,
        "families": families,
        "top_notes": top_notes,
        "middle_notes": middle_notes,
        "bottom_notes": bottom_notes,
        "users_notes": users_notes,
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

# Contador de iteraciones
iteration_count = 0

# Continuar guardando los datos en el archivo CSV temporal
try:
    with open('perfumes_test.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        for link in remaining_links:
            # Verificar el archivo de control
            control_status = read_control_file()
            if control_status == 'pause':
                print("Ejecución pausada. Cambia el estado en el archivo de control para continuar.")
                while read_control_file() == 'pause':
                    time.sleep(1)  # Esperar 1 segundo antes de volver a verificar

            # Detener la ejecución después de 800 iteraciones
            if iteration_count >= 800:
                print("Se han alcanzado 800 iteraciones, terminando la ejecución del script.")
                break

            print(f'Extrayendo información del perfume: {link}')
            try:
                perfume_info = extract_perfume_info(driver, link)
                # Imprimir los datos extraídos para verificación
                print(perfume_info)
                writer.writerow([
                    perfume_info["name"],
                    perfume_info["brand"],
                    perfume_info["type"],
                    perfume_info["rating_value"],
                    perfume_info["rating_count"],
                    perfume_info["gender"],
                    perfume_info["country"],
                    perfume_info["year"],
                    perfume_info["segment"],
                    ", ".join(perfume_info["perfumers"]),
                    ", ".join(perfume_info["families"]),
                    ", ".join(perfume_info["top_notes"]),
                    ", ".join(perfume_info["middle_notes"]),
                    ", ".join(perfume_info["bottom_notes"]),
                    ", ".join(perfume_info["users_notes"]),
                    perfume_info["url"]
                ])
                time.sleep(1)  # Espera para evitar ser bloqueado por el sitio web
                iteration_count += 1  # Incrementar el contador de iteraciones
            except Exception as e:
                print(f'Error al extraer información del perfume: {link} - {e}')
except PermissionError:
    print("Error de permisos: asegúrate de que el archivo 'perfumes_test.csv' no esté abierto en otra aplicación y que tengas permisos de escritura en el directorio.")
except Exception as e:
    print(f"Otro error ocurrió: {e}")

# Cerrar el driver
driver.quit()

print("Ejecución completada. Revisa los resultados en 'perfumes_test.csv'.")
