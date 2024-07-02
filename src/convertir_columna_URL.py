import pandas as pd

# Cargar el archivo CSV
file_path = 'par_per_datos.csv'
data = pd.read_csv(file_path)

# Extraer la columna 'URL'
urls = data['URL']

# Guardar los valores de la columna URL en un archivo de texto
txt_file_path = 'par_per_datos.txt'
urls.to_csv(txt_file_path, index=False, header=False)

print(f'Archivo de URLs creado en: {txt_file_path}')
