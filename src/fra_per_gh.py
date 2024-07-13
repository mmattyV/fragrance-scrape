import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Configuración de opciones de Chrome
chrome_options = Options()
chrome_options.headless = False  # Cambia a True si no necesitas la interfaz gráfica
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/126.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-blink-features=WebRtcHideLocalIpsWithMdns")

# Ruta al chromedriver
chromedriver_path = 'C:/chromedriver/chromedriver.exe'
service = Service(chromedriver_path)

# Cargar los enlaces desde el archivo txt
with open('fra_per_links.txt', 'r') as file:
    links_clean = file.read().splitlines()

# Crear DataFrame vacío
Fragrance = pd.DataFrame({
    'name': [],
    'accords': [],
    'rating': [],
    'votes': [],
    'top_notes': [],
    'middle_notes': [],
    'base_notes': []
})

# Iterar sobre los primeros 5 enlaces
for i in range(min(50, len(links_clean))):
    # Leer el archivo de control
    with open('control.txt', 'r') as control_file:
        control_command = control_file.read().strip()
        if control_command == 'pause':
            print("Script pausado. Cambia 'pause' a 'resume' o 'abort' en control.txt para continuar.")
            while control_command == 'pause':
                time.sleep(5)
                with open('control.txt', 'r') as control_file:
                    control_command = control_file.read().strip()
        if control_command == 'abort':
            print("Script abortado.")
            break

    # Crear objeto WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(links_clean[i])
    
    # Recolección de datos
    try:
        name_element = driver.find_element(By.CSS_SELECTOR, '#toptop > h1')
        name = name_element.get_attribute('innerHTML').split('<small')[0].strip()
    except:
        name = None
    
    try:
        accords = driver.find_element(By.XPATH, '//*[@id="main-content"]/div[1]/div[1]/div/div[2]/div[1]/div[2]/div').text
    except:
        accords = None
    
    try:
        rating = driver.find_element(By.XPATH, '//*[@id="main-content"]/div[1]/div[1]/div/div[2]/div[4]/div[3]/div/p[1]/span[1]').text
    except:
        rating = None

    try:
        votes = driver.find_element(By.XPATH, '//*[@id="main-content"]/div[1]/div[1]/div/div[2]/div[4]/div[3]/div/p[1]/span[3]').text
    except:
        votes = None
    
    try:
        top_notes = driver.find_element(By.XPATH, '//*[@id="pyramid"]/div[1]/div/div[2]/div[3]/div').text
    except:
        top_notes = None
    
    try:
        middle_notes = driver.find_element(By.XPATH, '//*[@id="pyramid"]/div[1]/div/div[2]/div[4]/div').text
    except:
        middle_notes = None
    
    try:
        base_notes = driver.find_element(By.XPATH, '//*[@id="pyramid"]/div[1]/div/div[2]/div[5]/div').text
    except:
        base_notes = None

    # Agregar los datos al DataFrame
    Fragrance.loc[len(Fragrance.index)] = [name, accords, rating, votes, top_notes, middle_notes, base_notes]
    
    driver.quit()

# Crear la carpeta 'data' si no existe
output_dir = 'data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Guardar el DataFrame en un archivo JSON con formato legible
Fragrance.to_json(os.path.join(output_dir, 'fragrance_data_test.json'), orient='records', indent=4)

# Mostrar los datos recolectados para verificación
print(Fragrance)


