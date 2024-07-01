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

    name = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1").text.strip() if soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1") else 'N/A'
    brand = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(1) > span").text.strip() if soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(1) > span") else 'N/A'
    release_year = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(2) > span").text.strip() if soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(2) > span") else 'N/A'
    concentration = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > span").text.strip() if soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > span") else 'N/A'
    rating_value = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span.ratingvalue").text.strip() if soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span.ratingvalue") else 'N/A'
    rating_count = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span.text-xs > span").text.strip() if soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span.text-xs > span") else 'N/A'
    
    main_accords = [element.text.strip() for element in soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.mb-3.pointer > span > div > div.text-xs.grey")]
    top_notes = [element.text.strip() for element in soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_t.w-100.mt-2 > div.right > span > span")]
    middle_notes = [element.text.strip() for element in soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_m.w-100.mt-2 > div.right > span > span")]
    base_notes = [element.text.strip() for element in soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_b.w-100.mt-2 > div.right > span > span")]
    perfumers = [element.text.strip() for element in soup.select("div.w-100.mt-0-5.mb-3 > a")]

    return {
        "Name": name,
        "Brand": brand,
        "Release Year": release_year,
        "Concentration": concentration,
        "Rating Value": rating_value,
        "Rating Count": rating_count,
        "Main Accords": main_accords,
        "Top Notes": top_notes,
        "Middle Notes": middle_notes,
        "Base Notes": base_notes,
        "Perfumers": perfumers,
        "URL": url
    }

# Inicializar el WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Leer los enlaces desde el archivo cleaned_par_link_per.txt
with open('cleaned_par_link_per.txt', 'r', encoding='utf-8') as file:
    all_links = file.read().splitlines()

# Leer los enlaces ya procesados desde el archivo par_per_datos.csv (archivo temporal)
processed_links = set()
if os.path.exists('par_per_datos.csv'):
    with open('par_per_datos.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar la cabecera
        for row in reader:
            processed_links.add(row[-1])  # Asumimos que la URL está en la última columna

# Filtrar los enlaces que no han sido procesados
remaining_links = [link for link in all_links if link not in processed_links]

# Continuar guardando los datos en el archivo CSV temporal
try:
    with open('par_per_datos.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Name", "Brand", "Release Year", "Concentration", "Rating Value", 
            "Rating Count", "Main Accords", "Top Notes", "Middle Notes", 
            "Base Notes", "Perfumers", "URL"
        ])

        for link in remaining_links:
            # Verificar el archivo de control
            control_status = read_control_file()
            if control_status == 'pause':
                print("Ejecución pausada. Cambia el estado en el archivo de control para continuar.")
                while read_control_file() == 'pause':
                    time.sleep(1)  # Esperar 1 segundo antes de volver a verificar

            print(f'Extrayendo información del perfume: {link}')
            try:
                perfume_info = extract_perfume_info(driver, link)
                # Imprimir los datos extraídos para verificación
                print(perfume_info)
                writer.writerow([
                    perfume_info["Name"],
                    perfume_info["Brand"],
                    perfume_info["Release Year"],
                    perfume_info["Concentration"],
                    perfume_info["Rating Value"],
                    perfume_info["Rating Count"],
                    ", ".join(perfume_info["Main Accords"]),
                    ", ".join(perfume_info["Top Notes"]),
                    ", ".join(perfume_info["Middle Notes"]),
                    ", ".join(perfume_info["Base Notes"]),
                    ", ".join(perfume_info["Perfumers"]),
                    perfume_info["URL"]
                ])
                time.sleep(1)  # Espera para evitar ser bloqueado por el sitio web
            except Exception as e:
                print(f'Error al extraer información del perfume: {link} - {e}')
except PermissionError:
    print("Error de permisos: asegúrate de que el archivo 'par_per_datos.csv' no esté abierto en otra aplicación y que tengas permisos de escritura en el directorio.")
except Exception as e:
    print(f"Otro error ocurrió: {e}")

# Cerrar el driver
driver.quit()

print("Ejecución completada. Revisa los resultados en 'par_per_datos.csv'.")
