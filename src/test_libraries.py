import numpy as np
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import requests
from bs4 import BeautifulSoup
import chromedriver_autoinstaller

# Comprobando Numpy
print("Numpy version:", np.__version__)
array = np.array([1, 2, 3])
print("Numpy array:", array)

# Comprobando lxml
root = etree.Element("root")
etree.SubElement(root, "child").text = "This is a test."
print("lxml is working, generated XML:")
print(etree.tostring(root, pretty_print=True).decode())

# Configurar opciones de Chrome
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')  # Asegurar que la GUI esté apagada
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

# Configurar el path a chromedriver usando chromedriver_autoinstaller
chromedriver_autoinstaller.install()

# Comprobando Selenium
try:
    # Inicializar el driver de Chrome
    driver = webdriver.Chrome(options=chrome_options)
    
    # Navegar a la página de Python
    driver.get("https://www.python.org")
    title = driver.title
    driver.quit()
    print("Selenium is working. Title of python.org is:", title)
except Exception as e:
    print("Selenium encountered an error:", str(e))

# Comprobando Pandas
df = pd.DataFrame({'column1': [1, 2], 'column2': [3, 4]})
print("Pandas DataFrame:")
print(df)

# Comprobando Requests
response = requests.get("https://www.python.org")
print("Requests status code:", response.status_code)

# Comprobando BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')
print("BeautifulSoup parsed title:", soup.title.string)



