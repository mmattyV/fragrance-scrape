import time
import random
import cloudscraper
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Lista de User-Agents para rotar
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
    # Agregar más User-Agents si es necesario
]

def human_like_wait(min_wait=4, max_wait=8):
    time.sleep(random.uniform(min_wait, max_wait))

def simulate_human_behavior(driver):
    element = driver.find_element(By.TAG_NAME, 'body')
    action = ActionChains(driver)
    for _ in range(random.randint(1, 3)):
        action.move_to_element_with_offset(element, random.randint(0, 100), random.randint(0, 100)).perform()
        human_like_wait(0.1, 0.5)
    element.click()

def get_cookies_from_cloudscraper(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    cookies = response.cookies.get_dict()
    return cookies

def main():
    # Inicializar el navegador usando undetected_chromedriver
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--incognito')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--disable-blink-features=AutomationControlled')
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={user_agent}')

    driver = uc.Chrome(options=options)

    # Selector para los enlaces de perfumes
    selector = 'div.flex-child-auto > h3 > a'

    # Archivo de salida para los enlaces de perfumes
    output_file_path = 'fra_per_links.txt'

    # Leer las URLs de las marcas desde el archivo
    input_file_path = 'fra_brand_links_modified.txt'
    with open(input_file_path, 'r') as input_file:
        brand_urls = input_file.readlines()

    # Iterar sobre cada URL de marca
    for brand_url in brand_urls:
        brand_url = brand_url.strip()  # Eliminar espacios en blanco alrededor
        if not brand_url:
            continue  # Saltar líneas vacías

        # Obtener cookies desde cloudscraper
        cookies = get_cookies_from_cloudscraper(brand_url)

        # Navegar a la URL de la marca
        driver.get(brand_url)
        human_like_wait(5, 10)  # Esperar a que la página cargue completamente

        # Añadir las cookies al navegador de Selenium
        for cookie_name, cookie_value in cookies.items():
            driver.add_cookie({'name': cookie_name, 'value': cookie_value})

        # Refrescar la página para aplicar las cookies
        driver.refresh()
        human_like_wait(5, 10)

        # Simula un comportamiento humano
        simulate_human_behavior(driver)

        # Verificar la existencia del elemento <body> antes de proceder
        try:
            element = driver.find_element(By.TAG_NAME, 'body')
        except Exception as e:
            print(f"Error: {e}")
            continue

        # Encontrar todos los enlaces de perfumes en la página de la marca
        perfume_elements = driver.find_elements(By.CSS_SELECTOR, selector)

        # Abrir archivo para guardar los enlaces de perfumes en modo 'append'
        with open(output_file_path, 'a') as output_file:
            for perfume_element in perfume_elements:
                perfume_link = perfume_element.get_attribute('href')
                output_file.write(perfume_link + '\n')
                print(perfume_link)

        # Espera aleatoria antes de procesar la siguiente URL
        human_like_wait(10, 20)

    # Cerrar el navegador
    driver.quit()

if __name__ == '__main__':
    main()




