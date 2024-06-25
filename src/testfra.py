import requests
from bs4 import BeautifulSoup
import time
import os

# Función para cargar los links de designers desde un archivo y cambiar '.com' por '.es'
def load_designer_links(filename):
    with open(filename, 'r') as file:
        return [line.strip().replace('.com', '.es') for line in file]

# Función para guardar los links de perfumes en un archivo
def save_perfume_links(filename, perfume_links):
    with open(filename, 'w') as file:
        file.write("Designer,Perfume Link\n")
        for designer, links in perfume_links.items():
            for link in links:
                file.write(f"{designer},{link}\n")

# Función para obtener los links de perfumes desde una página de designer
def get_perfume_links(designer_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(designer_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    perfume_links = []

    try:
        perfume_elements = soup.select('#brands > div > div > div.flex-child-auto > h3 > a')
        for element in perfume_elements:
            link = element.get('href')
            perfume_links.append(f"https://www.fragrantica.es{link}")
    except Exception as e:
        print(f"Error al procesar {designer_url}: {e}")

    return perfume_links

# Función para cargar el índice del diseñador desde un archivo de control
def load_control_index(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return int(file.read().strip())
    return 0

# Función para guardar el índice del diseñador en un archivo de control
def save_control_index(filename, index):
    with open(filename, 'w') as file:
        file.write(str(index))

# Cargar los links de los designers
designer_links = load_designer_links('designerslinksfrag.txt')

# Crear un diccionario para almacenar los links de perfumes por designer
perfume_links = {}

# Cargar el índice del diseñador desde el archivo de control
current_index = load_control_index('control.txt')

# Extraer los links de perfumes para cada designer a partir del índice actual
for i in range(current_index, len(designer_links)):
    designer_url = designer_links[i]
    print(f"Procesando {designer_url}")
    designer_name = designer_url.split('/')[-1].replace('.html', '')
    perfume_links[designer_name] = get_perfume_links(designer_url)
    save_perfume_links('perfume_links_ES.txt', perfume_links)
    save_control_index('control.txt', i + 1)
    time.sleep(2)  # Esperar 2 segundos entre requests para no sobrecargar el servidor

print("Extracción completada. Los enlaces de perfumes se han guardado en 'perfume_links_ES.txt'.")


