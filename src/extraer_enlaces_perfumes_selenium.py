from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Ruta al ChromeDriver (reemplaza con la ruta real en tu sistema)
chrome_driver_path = 'C:\\chromedriver\\chromedriver.exe'  # Asegúrate de que esta ruta es correcta

# Configuración del servicio de Chrome
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# URL de inicio
start_url = 'https://aromo.ru/perfumes/'
driver.get(start_url)

def collect_links_from_page(driver):
    links = []
    try:
        # Esperar a que los elementos carguen
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.block-offer-item__link')))
        perfume_elements = driver.find_elements(By.CSS_SELECTOR, 'a.block-offer-item__link')
        
        # Recolectar los enlaces
        for elem in perfume_elements:
            links.append(elem.get_attribute('href'))
    except Exception as e:
        print(f'Error al recolectar enlaces: {e}')
    return links

def go_to_next_page(driver, current_page):
    try:
        # Construir el URL de la siguiente página
        next_page_url = f'https://aromo.ru/perfumes/page/{current_page + 1}/'
        driver.get(next_page_url)
        time.sleep(2)  # Esperar a que la página cargue
    except Exception as e:
        print(f'Error al ir a la página siguiente: {e}')

all_links = []
current_page = 1
max_pages = 2000

while current_page <= max_pages:
    print(f'Recolectando enlaces de la página {current_page}')
    links = collect_links_from_page(driver)
    all_links.extend(links)
    
    # Ir a la siguiente página
    go_to_next_page(driver, current_page)
    current_page += 1

# Cerrar el driver
driver.quit()

# Guardar los enlaces en un archivo
with open('perfume_links.txt', 'w') as file:
    for link in all_links:
        file.write(f'{link}\n')

print(f'Recolectados {len(all_links)} enlaces.')











