import pandas as pd

# Ruta de los archivos
csv_file_path = 'C:/Users/miufa/Aroma/src/combined_fra_perfumes.csv'
txt_file_path = 'C:/Users/miufa/Aroma/src/fra_per_links_faltapoco.txt'
output_file_path = 'C:/Users/miufa/Aroma/src/fra_faltan.txt'

# Leer el archivo CSV
df = pd.read_csv(csv_file_path)

# Extraer los URLs del DataFrame
csv_urls = set(df['url'])

# Leer el archivo de texto
with open(txt_file_path, 'r') as file:
    txt_urls = set(file.read().splitlines())

# Encontrar los URLs que están en el archivo de texto pero no en el CSV
missing_urls = txt_urls - csv_urls

# Guardar los URLs que faltan en un nuevo archivo de texto
with open(output_file_path, 'w') as file:
    for url in missing_urls:
        file.write(url + '\n')

print(f"URLs faltantes guardados en '{output_file_path}'")
