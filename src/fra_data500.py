import time
import random
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Lista de diferentes User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:61.0) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.63"
    # Añadir más User-Agents si es necesario
]

# Función para cargar cookies desde un archivo
def load_cookies(driver, cookies_file):
    with open(cookies_file, 'r') as file:
        cookies = json.load(file)
    for cookie in cookies:
        if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
            del cookie["sameSite"]
        driver.add_cookie(cookie)

# Función para obtener un User-Agent aleatorio
def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Lista de archivos de cookies
cookies_files = [f"cookies{i:02}.json" for i in range(0, 50)]  # Usar 50 archivos de cookies

# Configuración de Selenium
def create_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    # Obtener un User-Agent aleatorio
    user_agent = get_random_user_agent()
    options.add_argument(f"user-agent={user_agent}")

    service = Service("C:/chromedriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    # Cargar cookies guardadas de un archivo aleatorio
    cookies_file = random.choice(cookies_files)
    driver.get("https://www.fragrantica.com/")
    load_cookies(driver, cookies_file)
    time.sleep(5)  # Esperar a que las cookies se carguen correctamente
    return driver

# Leer la lista de enlaces desde el archivo
with open("fra_per_links.txt", "r") as file:
    links = file.readlines()

# Limitar el número de iteraciones a 500
links = links[:500]

# Archivo CSV de salida
csv_file = open('fra_per_data.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['URL', 'Título', 'Descripción'])  # Cabecera del archivo CSV

# Leer el estado de progreso desde control.txt
try:
    with open('control.txt', 'r') as control_file:
        start_index = int(control_file.read().strip())
except FileNotFoundError:
    start_index = 0

# Inicializar el driver
driver = create_driver()

# Iterar sobre los enlaces
for i in range(start_index, len(links)):
    link = links[i]
    try:
        # Cambiar cookies y User-Agent cada 7 iteraciones
        if i % 7 == 0 and i != 0:
            driver.quit()
            driver = create_driver()

        driver.get(link.strip())
        time.sleep(5)  # Esperar a que la página cargue completamente

        # Extraer datos (esto es solo un ejemplo, ajusta según la estructura real de la página)
        title = driver.title
        description = driver.find_element(By.NAME, "description").get_attribute("content")

        # Guardar datos en el archivo CSV
        csv_writer.writerow([link.strip(), title, description])

    except Exception as e:
        print(f"Error procesando el link {link.strip()}: {e}")

    # Guardar el progreso en control.txt
    with open('control.txt', 'w') as control_file:
        control_file.write(str(i + 1))

    # Pausa de 15 segundos después de cada 7 iteraciones
    if (i + 1) % 7 == 0:
        print("Pausa de 5 segundos...")
        time.sleep(5)

# Cerrar el driver y el archivo CSV
driver.quit()
csv_file.close()
