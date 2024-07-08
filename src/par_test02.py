import json
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# Función para inicializar el driver con undetected-chromedriver
def init_driver():
    options = uc.ChromeOptions()
    # options.add_argument("--headless")  # Ejecutar Chrome sin interfaz gráfica (comentado para ver la ejecución)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = 'C:/chrome-win64/chrome.exe'  # Actualiza esta ruta según sea necesario
    driver = uc.Chrome(driver_executable_path='C:/chromedriver/chromedriver.exe', options=options)
    return driver

# Función para extraer datos del perfume
def extract_perfume_data(driver, url):
    driver.get(url)
    perfume_data = {}
    try:
        # Esperar y obtener el nombre
        print("Buscando el nombre del perfume...")
        name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#toptop > h1'))
        )
        name = name_element.text if name_element else 'N/A'
        print(f"Nombre: {name}")

        # Esperar y obtener el género
        print("Buscando el género del perfume...")
        gender_element = driver.find_element(By.CSS_SELECTOR, '#toptop > h1 > small')
        gender = gender_element.text if gender_element else 'N/A'
        print(f"Género: {gender}")

        # Esperar y obtener la valoración
        print("Buscando la valoración del perfume...")
        rating_value_element = driver.find_element(By.CSS_SELECTOR, '#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(1)')
        rating_value = rating_value_element.text if rating_value_element else 'N/A'
        print(f"Valoración: {rating_value}")

        # Esperar y obtener la cantidad de valoraciones
        print("Buscando la cantidad de valoraciones del perfume...")
        rating_count_element = driver.find_element(By.CSS_SELECTOR, '#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div.small-12.medium-6.text-center > div > p.info-note > span:nth-child(3)')
        rating_count = rating_count_element.text if rating_count_element else 'N/A'
        print(f"Cantidad de valoraciones: {rating_count}")

        # Esperar y obtener los principales acordes
        print("Buscando los principales acordes del perfume...")
        main_accords_elements = driver.find_elements(By.CSS_SELECTOR, '#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div > div.accord-bar')
        main_accords = [element.text for element in main_accords_elements]
        print(f"Principales acordes: {main_accords}")

        # Esperar y obtener los perfumistas
        print("Buscando los perfumistas del perfume...")
        perfumers_elements = driver.find_elements(By.CSS_SELECTOR, '#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(3) > div.grid-x.grid-padding-x.grid-padding-y.small-up-2.medium-up-2 > div > a')
        perfumers = [element.text for element in perfumers_elements]
        print(f"Perfumistas: {perfumers}")

        perfume_data = {
            "Nombre": name,
            "Género": gender,
            "Valoración": rating_value,
            "Cantidad de valoraciones": rating_count,
            "Principales acordes": main_accords,
            "Perfumistas": perfumers
        }

    except Exception as e:
        print(f"Error extrayendo datos de {url}: {e}")
        perfume_data = {
            "Nombre": "Error",
            "Género": "Error",
            "Valoración": "Error",
            "Cantidad de valoraciones": "Error",
            "Principales acordes": "Error",
            "Perfumistas": "Error"
        }
    return perfume_data

# Ruta de archivos
base_dir = 'C:/Users/miufa/Aroma'
src_dir = os.path.join(base_dir, 'src')
data_dir = os.path.join(base_dir, 'data')

# Verificar existencia de directorios y archivos
if not os.path.exists(src_dir):
    raise FileNotFoundError(f"El directorio src no existe: {src_dir}")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

links_file_path = os.path.join(src_dir, 'fra_per_links.txt')
if not os.path.exists(links_file_path):
    raise FileNotFoundError(f"El archivo de enlaces no existe: {links_file_path}")

# Cargar enlaces
with open(links_file_path, 'r') as file:
    perfume_links = file.readlines()

# Iniciar driver
driver = init_driver()

# Archivos de salida y control
output_file = os.path.join(data_dir, 'fra_datos_per.json')
control_file = os.path.join(src_dir, 'control.txt')

# Asegurarse de que el archivo de control tiene el comando correcto
with open(control_file, 'w') as file:
    file.write('continue')

# Cargar progreso previo si existe
if os.path.exists(output_file):
    with open(output_file, 'r') as file:
        perfume_data_list = json.load(file)
else:
    perfume_data_list = []

# Iterar sobre todos los enlaces
for i, link in enumerate(perfume_links):
    link = link.strip()
    perfume_data = extract_perfume_data(driver, link)
    perfume_data_list.append(perfume_data)
    
    # Guardar datos después de cada iteración
    with open(output_file, 'w') as file:
        json.dump(perfume_data_list, file, indent=4, ensure_ascii=False)
    
    # Verificar archivo de control
    if os.path.exists(control_file):
        with open(control_file, 'r') as file:
            control_command = file.read().strip()
        print(f"Comando de control: {control_command}")
        if control_command == 'pause':
            print("Script paused")
            while control_command == 'pause':
                time.sleep(5)
                with open(control_file, 'r') as file:
                    control_command = file.read().strip()
                print(f"Comando de control: {control_command}")
        if control_command == 'abort':
            print("Script aborted")
            break

# Cerrar driver
driver.quit()
