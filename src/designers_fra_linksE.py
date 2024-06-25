import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Ruta al ChromeDriver (reemplaza con la ruta real en tu sistema)
chrome_driver_path = 'C:\\chromedriver\\chromedriver.exe'

# Configuración del servicio de Chrome
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# URL de la página de diseñadores en Fragrantica
url = 'https://www.fragrantica.com/designers-11/#T'

# Navegar a la página
driver.get(url)
time.sleep(5)  # Espera para cargar la página completamente

# Extraer el contenido de la página
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Seleccionar todos los enlaces de los diseñadores utilizando un selector más robusto
designer_elements = soup.select('div.designerlist a')

# Extraer los enlaces y guardarlos en una lista
designer_links = []
for element in designer_elements:
    href = element.get('href')
    if href:
        designer_links.append(f"https://www.fragrantica.com{href}")

# Guardar los enlaces en un archivo de texto
with open('designerslinksfrag.txt', 'w') as file:
    for link in designer_links:
        file.write(link + '\n')

# Cerrar el driver
driver.quit()

print("Extracción completada. Los enlaces se han guardado en 'designerslinksfrag.txt'.")
