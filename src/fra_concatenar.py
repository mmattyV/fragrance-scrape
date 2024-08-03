import pandas as pd
import os

# Ruta de la carpeta que contiene los archivos CSV
folder_path = 'C:/Users/miufa/Aroma/src'

if not os.path.exists(folder_path):
    print(f"La ruta especificada no existe: {folder_path}")
else:
    # Lista para almacenar cada DataFrame leído de los archivos CSV
    dataframes = []

    # Leer cada archivo CSV y añadirlo a la lista
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            dataframes.append(df)

    if dataframes:
        # Concatenar todos los DataFrames en uno solo
        combined_df = pd.concat(dataframes, ignore_index=True)

        # Guardar el DataFrame combinado en un nuevo archivo CSV
        combined_file_path = os.path.join(folder_path, 'combined_fra_perfumes.csv')
        combined_df.to_csv(combined_file_path, index=False)
        print(f"Todos los archivos CSV han sido combinados en '{combined_file_path}'")
    else:
        print("No se encontraron archivos CSV en la ruta especificada.")
