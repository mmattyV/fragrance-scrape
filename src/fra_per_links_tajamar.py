import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main(brand_url):
    # Inicializar el navegador usando webdriver_manager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Opcional: Ejecutar el navegador en modo headless (sin interfaz gráfica)
    driver = webdriver.Chrome(service=service, options=options)

    # Selector para los enlaces de perfumes
    selector = 'div.flex-child-auto > h3 > a'

    # Archivo de salida para los enlaces de perfumes
    output_file_path = 'fra_per_links.txt'

    # Navegar a la URL de la marca
    driver.get(brand_url)
    time.sleep(5)  # Esperar a que la página cargue completamente

    # Encontrar todos los enlaces de perfumes en la página de la marca
    perfume_elements = driver.find_elements(By.CSS_SELECTOR, selector)

    # Abrir archivo para guardar los enlaces de perfumes en modo 'append'
    with open(output_file_path, 'a') as output_file:
        for perfume_element in perfume_elements:
            perfume_link = perfume_element.get_attribute('href')
            output_file.write(perfume_link + '\n')
            print(perfume_link)

    # Cerrar el navegador
    driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recolección de enlaces de perfumes desde una URL de una marca.')
    parser.add_argument('brand_url', type=str, help='URL de la página de la marca')

    args = parser.parse_args()
    main(args.brand_url)
