from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_selenium():
    driver = webdriver.Chrome()  # Asegúrate de tener chromedriver en tu PATH
    
    try:
        driver.get("https://www.python.org")
        WebDriverWait(driver, 10).until(EC.title_contains("Python"))
        title = driver.title
        print(f"Selenium está funcionando. El título de la página es: {title}")
    except Exception as e:
        print(f"Error al ejecutar Selenium: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_selenium()


