# par_test00.py

import requests
from bs4 import BeautifulSoup
import csv

# Encabezados para imitar una solicitud del navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Rutas de archivo
perfume_links_file = "cleaned_par_link_per.txt"
output_csv_file = "par_per_datos.csv"

# Leer los enlaces de perfumes del archivo
def read_perfume_links():
    with open(perfume_links_file, "r") as file:
        return [line.strip() for line in file.readlines()]

# Scraping de la información del perfume
def scrape_perfume_data(perfume_url):
    try:
        response = requests.get(perfume_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        name_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1")
        brand_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(1) > span")
        release_year_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(2) > span")
        concentration_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > span")
        rating_value_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span[itemprop='ratingValue']")
        rating_count_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span.text-xs > span")
        main_accords_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.mb-3.pointer > span > div > div.text-xs.grey")
        top_notes_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_t.w-100.mt-2 > div.right > span.clickable_note_img.notefont4")
        middle_notes_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_m.w-100.mt-2 > div.right > span.clickable_note_img.notefont4 > span")
        base_notes_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_b.w-100.mt-2 > div.right > span.clickable_note_img.notefont5 > span")

        name = name_element.get_text(strip=True) if name_element else "N/A"
        brand = brand_element.get_text(strip=True) if brand_element else "N/A"
        release_year = release_year_element.get_text(strip=True) if release_year_element else "N/A"
        concentration = concentration_element.get_text(strip=True) if concentration_element else "N/A"
        rating_value = rating_value_element.get_text(strip=True) if rating_value_element else "N/A"
        rating_count = rating_count_element.get_text(strip=True) if rating_count_element else "N/A"
        main_accords = ", ".join([elem.get_text(strip=True) for elem in main_accords_elements])
        top_notes = ", ".join([elem.get_text(strip=True) for elem in top_notes_elements])
        middle_notes = ", ".join([elem.get_text(strip=True) for elem in middle_notes_elements])
        base_notes = ", ".join([elem.get_text(strip=True) for elem in base_notes_elements])

        return {
            "Name": name,
            "Brand": brand,
            "Release Year": release_year,
            "Concentration": concentration,
            "Rating Value": rating_value,
            "Rating Count": rating_count,
            "Main Accords": main_accords,
            "Top Notes": top_notes,
            "Middle Notes": middle_notes,
            "Base Notes": base_notes,
            "URL": perfume_url
        }
    except Exception as e:
        print(f"Error scraping {perfume_url}: {e}")
        return {
            "Name": "N/A",
            "Brand": "N/A",
            "Release Year": "N/A",
            "Concentration": "N/A",
            "Rating Value": "N/A",
            "Rating Count": "N/A",
            "Main Accords": "N/A",
            "Top Notes": "N/A",
            "Middle Notes": "N/A",
            "Base Notes": "N/A",
            "URL": perfume_url
        }

# Guardar los datos en un archivo CSV
def save_to_csv(data):
    try:
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Name", "Brand", "Release Year", "Concentration", "Rating Value", "Rating Count", "Main Accords", "Top Notes", "Middle Notes", "Base Notes", "URL"])
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"Datos guardados en {output_csv_file}")
    except Exception as e:
        print(f"Error guardando datos en CSV: {e}")

def main():
    perfume_links = read_perfume_links()
    perfume_data = []

    # Limitar a los primeros 15 enlaces para la prueba
    for perfume_url in perfume_links[:15]:
        print(f"Scraping {perfume_url}...")
        data = scrape_perfume_data(perfume_url)
        perfume_data.append(data)

    save_to_csv(perfume_data)
    print("Scraping completado. Datos guardados en par_per_datos.csv")

if __name__ == "__main__":
    main()




