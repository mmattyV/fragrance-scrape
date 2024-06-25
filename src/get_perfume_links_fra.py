import time
import csv
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# Ruta al ChromeDriver (reemplaza con la ruta real en tu sistema)
chrome_driver_path = 'C:\\chromedriver\\chromedriver.exe'

# Configuración del servicio de Chrome
service = Service(chrome_driver_path)

# Ruta al archivo de control
control_file_path = 'control.txt'

def read_control_file():
    with open(control_file_path, 'r') as file:
        return file.read().strip()

# Función para configurar el navegador con un User Agent aleatorio
def get_webdriver():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
    ]
    user_agent = random.choice(user_agents)
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Leer los enlaces de los diseñadores desde el archivo designerslinksfrag.txt
with open('designerslinksfrag.txt', 'r') as file:
    designer_links = file.read().splitlines()

# Archivo de salida para los enlaces de perfumes
output_file = 'perfume_links.txt'

# Función para simular la interacción humana
def simulate_human_interaction(driver):
    actions = webdriver.ActionChains(driver)
    body = driver.find_element(By.TAG_NAME, 'body')
    for _ in range(10):
        actions.move_to_element_with_offset(body, random.randint(0, body.size['width']), random.randint(0, body.size['height'])).perform()
        time.sleep(random.uniform(0.1, 0.3))
    actions.send_keys(Keys.PAGE_DOWN).perform()

# Abrir el archivo de salida en modo de escritura
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Designer', 'Perfume Link'])  # Escribir la cabecera

    driver = get_webdriver()

    # Iterar sobre cada enlace de diseñador
    for designer_link in designer_links:
        # Verificar el archivo de control
        control_status = read_control_file()
        if control_status == 'pause':
            print("Ejecución pausada. Cambia el estado en el archivo de control para continuar.")
            while read_control_file() == 'pause':
                time.sleep(5)  # Esperar 5 segundos antes de volver a verificar
        elif control_status == 'stop':
            print("Ejecución detenida por el archivo de control.")
            break

        try:
            driver.get(designer_link)
            time.sleep(random.uniform(3, 5))  # Esperar para cargar la página completamente
            simulate_human_interaction(driver)  # Simular interacción humana

            # Extraer el contenido de la página
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Seleccionar todos los enlaces a páginas de perfumes
            perfume_elements = soup.select('#brands > div > div > div.flex-child-auto > h3 > a')

            # Iterar sobre cada elemento de perfume y escribir el enlace en el archivo
            for element in perfume_elements:
                perfume_link = element.get('href')
                if perfume_link:
                    writer.writerow([designer_link, f"https://www.fragrantica.com{perfume_link}"])

        except Exception as e:
            print(f'Error al procesar {designer_link}: {e}')
            driver.quit()
            driver = get_webdriver()

# Cerrar el driver
driver.quit()

print(f"Extracción completada. Los enlaces de perfumes se han guardado en '{output_file}'.")
