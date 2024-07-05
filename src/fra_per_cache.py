import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def main(brand_url, retries=3):
    # Modificar la URL para usar la versión en caché de Google
    cache_url = f'https://webcache.googleusercontent.com/search?q=cache:{brand_url}'
    
    print(f"Accediendo a la URL en caché: {cache_url}")

    # Inicializar el navegador usando webdriver_manager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecutar el navegador en modo headless (sin interfaz gráfica)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    attempt = 0

    while attempt < retries:
        try:
            driver = webdriver.Chrome(service=service, options=options)
            print("Navegador inicializado correctamente.")

            # Selector para los enlaces de perfumes
            selector = 'div.flex-child-auto > h3 > a'

            # Archivo de salida para los enlaces de perfumes
            output_file_path = 'fra_per_links.txt'

            # Navegar a la URL de la caché de Google de la marca
            driver.get(cache_url)
            time.sleep(5)  # Esperar a que la página cargue completamente
            print(f"Página cargada: {cache_url}")

            # Encontrar todos los enlaces de perfumes en la página de la marca
            perfume_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"Número de enlaces encontrados: {len(perfume_elements)}")

            if not perfume_elements:
                print("No se encontraron enlaces de perfumes.")
            
            # Abrir archivo para guardar los enlaces de perfumes en modo 'append'
            with open(output_file_path, 'a') as output_file:
                for perfume_element in perfume_elements:
                    perfume_link = perfume_element.get_attribute('href')
                    output_file.write(perfume_link + '\n')
                    print(f"Enlace añadido: {perfume_link}")

            # Cerrar el navegador
            driver.quit()
            break  # Salir del bucle si la solicitud es exitosa

        except (NoSuchWindowException, WebDriverException) as e:
            print(f"Error: {e}. Reintentando ({attempt + 1}/{retries})...")
            if driver:
                driver.quit()
            attempt += 1
            time.sleep(5)  # Esperar antes de reintentar

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recolección de enlaces de perfumes desde una URL de una marca.')
    parser.add_argument('brand_url', type=str, help='URL de la página de la marca')

    args = parser.parse_args()
    main(args.brand_url)

