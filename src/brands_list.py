# src/brands_list.py

import sys

# List of popular perfume brands
brands00 = [
    'Zara', 'Avon', 'Chanel', 'Oriflame', 'Montale', 'Faberlic', 'Givenchy', 'FM by Federico Mahora', 'Gucci',
    'Jo Malone', 'Yves Rocher', 'Giorgio Armani', 'Guerlain', 'Mary Kay', 'Brocard', 'Hugo Boss', 'By Kilian',
    'Burberry', 'Kenzo', 'Dzintars', 'Yves Saint Laurent', 'Lalique', 'Tiziana Terenzi', "Victoria's Secret",
    'Azzaro', 'Tom Ford', 'Dior', 'Yodeyma Paris', 'Dolce & Gabbana', 'Lacoste', 'S Parfum', 'Mancera',
    'Amouage', 'Antonio Banderas', 'Bershka', 'Versace', 'Bvlgari', 'Новая заря', 'Pull & Bear', 'Amway',
    'Eisenberg', 'Maison Francis Kurkdjan', 'Trussardi', 'Byredo', 'Narciso Rodriguez', 'Ajmal', 'Bi-es',
    'Fragance World', 'Lanvin', 'Paco Rabanne', 'Massimo Dutti', 'Rasasi', 'Marks and Spencer', 'Ex Nihilo',
    'Mugler', "enhaligon's", 'Calvin Klein', 'La Rive',  'Dilis Parfum', 'Salvador Dali', 'Louis Vuitton',
    'Nina Ricci', 'Lattafa Perfumes', 'Carven', 'Escada', 'Fragonard', 'Carolina Herrera', 'Montblanc',
    'Reserved', 'Molinard', 'Loewe', 'Cartier', 'Shiseido', 'Cacharel', 'Jean Paul Gaultier', 'Hollister',
    'Elizabeth Arden', "L'Occitane en Provence", 'Prada', 'Rituals', 'Sephora', 'Aqua di Parma', 'Issey Miyake',
    'Rochas', 'Chopard', 'Davidoff', 'Valentino', 'Boucheron', 'Lattafa Perfumes', 'Byredo', 'O Boticário',  
    'Creed', 'Xerjoff', 'Nishane', 'Diptique', 'Serge Lutens', 'Natura', 'Parfums de Marly', 'Kayali Fragances',
    "Etat Libre d'Orange", 'Victor&Rolf', 'Initio Parfums Prives', 'Frederic Malle', 'Tommy Hilfiger', 'Omerta',
    'The Fragance Kitchen', 'Lonkoom Parfum', 'Real Time', 'Maurer & Wirtz', 'Oud Elite', 'Paris Elysees', 
    'Bottega Verde', 'Khalis', 'Creation Lamis', 'Revlon', 'Yardley', 'Karen Low', 'Ralph Lauren', 'Pierre Guillaume Paris',
    'Floris', 'Estiara', 'D.S. & Durga', 'Chris Adams', 'Entity', 'Jafra', 'Roberto Cavalli', 'Bath and Body Works',
    'Jil Sander', 'Adidas', 'Arabian Oud', 'Edgardio Chilini', 'Berdoues', 'Art Parfum', 'Evaflor', 'Lomani',
    'Christine Lavoisier Parfums', 'Donna Karan', 'Marc Jacobs', 'Police', 'Clean', 'Vittorio Bellucci', 'Ormonde Jayne',
    'Clive Christian', '10th Avenue Karl Antony', "L'Artisan Perfumeur", 'Benetton', 'Al Haramain Perfumes',
    'Carlo Bossi', 'Sergio Nero', 'Pascal Morabito', 'Ciel', 'Goutal Paris', 'Roger & Gallet', 'Roja Parfums',
    'Alan Bray', 'Fueguia 1833', 'Lush', 'Al-Rehab', 'Ulric de Varens', 'Mexx', 'Caron', 'Houbigant', 'Geparlys',
    'Abdul Samad Al Qurashi', 'Jacques Battini', 'Swiss Arabian', 'Axe', 'Parfums Genty', 'M. Micallef', 'Next',
    'The Merchant of Venice', 'And Other Stories', 'H&M', 'Nicolai Perfumeur Createur', 'Boadicea the Victorious',
    'Afnan', 'Alexandre.J', "L'Erbolario", 'Abercrombie & Fitch', 'Salvatore Ferragamo', 'Le Labo', 'Atkinsons',
    'Coty', 'Jeanne Arthes', 'Armaf', 'Emper', 'Eyfel', 'Memo', 'Adopt',  'Demeter', 'Diptique', 'Monotheme Fine Fragances Venezia',   'Van Cleef & Arpels',
    'Lancome', 'Hermès', 'Chloe', 'Estée Lauder '
    
    # Add more brands as needed
]
# Sort the list alphabetically and save it as a new list
brands01 = sorted(brands00)

# Ensure the output uses utf-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Print the sorted list
print(brands01)

# (Optional) Save the list to a file
with open('brands01.txt', 'w', encoding='utf-8') as file:
    for brand in brands01:
        file.write(f"{brand}\n")