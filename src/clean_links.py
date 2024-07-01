# script para limpiar el archivo de texto

input_file_path = "par_link_per.txt"
output_file_path = "cleaned_par_link_per.txt"

def clean_links(input_file, output_file):
    with open(input_file, "r") as file:
        lines = file.readlines()

    # Eliminar "https://www.parfumo.com" de cada línea
    cleaned_lines = [line.replace('https://www.parfumo.com', '', 1) for line in lines]

    # Guardar las líneas limpiadas en un nuevo archivo
    with open(output_file, "w") as file:
        file.writelines(cleaned_lines)

if __name__ == "__main__":
    clean_links(input_file_path, output_file_path)
    print(f"Enlaces limpiados guardados en {output_file_path}")
