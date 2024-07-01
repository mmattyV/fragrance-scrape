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
    base_url = "https://www.parfumo.com"
    full_url = perfume_url if perfume_url.startswith("http") else f"{base_url}{perfume_url}"
    response = requests.get(full_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        name_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1")
        brand_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(1) > span")
        release_year_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(2) > span")
        concentration_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > span")
        rating_value_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span.ratingvalue")
        rating_count_element = soup.select_one("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div:nth-child(1) > span.text-xs > span")

        main_accords_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.mb-3.pointer > span > div > div.text-xs.grey")
        top_notes_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_t.w-100.mt-2 > div.right > span > span")
        middle_notes_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_m.w-100.mt-2 > div.right > span > span")
        base_notes_elements = soup.select("#pd_inf > div.cb.pt-1 > main > div.p_details_holder_second > div.notes_list.mb-2 > div.pyramid_block.nb_b.w-100.mt-2 > div.right > span > span")

        perfumers_elements = soup.select("div.w-100.mt-0-5.mb-3 > a")

        name = name_element.get_text(strip=True) if name_element else "N/A"
        brand = brand_element.get_text(strip=True) if brand_element else "N/A"
        release_year = release_year_element.get_text(strip=True) if release_year_element else "N/A"
        concentration = concentration_element.get_text(strip=True) if concentration_element else "N/A"
        rating_value = rating_value_element.get_text(strip=True) if rating_value_element else "N/A"
        rating_count = rating_count_element.get_text(strip=True) if rating_count_element else "N/A"

        main_accords = ", ".join([element.get_text(strip=True) for element in main_accords_elements]) if main_accords_elements else "N/A"
        top_notes = ", ".join([element.get_text(strip=True) for element in top_notes_elements]) if top_notes_elements else "N/A"
        middle_notes = ", ".join([element.get_text(strip=True) for element in middle_notes_elements]) if middle_notes_elements else "N/A"
        base_notes = ", ".join([element.get_text(strip=True) for element in base_notes_elements]) if base_notes_elements else "N/A"
        perfumers = ", ".join([element.get_text(strip=True) for element in perfumers_elements]) if perfumers_elements else "N/A"

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
            "Perfumers": perfumers,
            "URL": full_url
        }
    except Exception as e:
        print(f"Error scraping {full_url}: {e}")
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
            "Perfumers": "N/A",
            "URL": full_url
        }

# Guardar los datos en un archivo CSV
def save_to_csv(data):
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Brand", "Release Year", "Concentration", "Rating Value", "Rating Count", "Main Accords", "Top Notes", "Middle Notes", "Base Notes", "Perfumers", "URL"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main():
    perfume_links = read_perfume_links()
    perfume_data = []

    # Limitar a los primeros 10 enlaces para la prueba
    for perfume_url in perfume_links[:10]:
        print(f"Scraping {perfume_url}...")
        data = scrape_perfume_data(perfume_url)
        perfume_data.append(data)

    save_to_csv(perfume_data)
    print("Scraping completado. Datos guardados en par_per_datos.csv")

if __name__ == "__main__":
    main()

