# Abrir el archivo de enlaces de marcas
with open('fra_brand_links.txt', 'r') as file:
    brand_links = file.readlines()

# Modificar cada enlace para que contenga una máscara universal en lugar del nombre del perfume
masked_links = [link.replace('/designers/', '/perfume/').replace('.html', '/.*.html') for link in brand_links]

# Guardar los enlaces modificados en un nuevo archivo
with open('masked_brand_links.txt', 'w') as file:
    file.writelines(masked_links)

