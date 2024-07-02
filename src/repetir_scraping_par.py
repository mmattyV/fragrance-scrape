# Define the paths to your text files
file1_path = 'par_per_datos.txt'
file2_path = 'cleaned_par_link_per.txt'
unique_file_path = 'par_lineas_unicas.txt'

# Load the contents of the two text files
with open(file1_path, 'r') as file1:
    lines_file1 = set(file1.readlines())

with open(file2_path, 'r') as file2:
    lines_file2 = set(file2.readlines())

# Find the unique lines in cleaned_par_link_per.txt
unique_lines_file2 = lines_file2 - lines_file1

# Save the unique lines to a new text file
with open(unique_file_path, 'w') as unique_file:
    unique_file.writelines(unique_lines_file2)

print(f'Archivo de líneas únicas creado en: {unique_file_path}')
