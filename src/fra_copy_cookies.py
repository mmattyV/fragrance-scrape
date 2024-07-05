import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

def save_cookies(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

if __name__ == "__main__":
    options = Options()
    service = ChromeService(executable_path='C:/chromedriver/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get('https://www.fragrantica.com')
    input("Complete the CAPTCHA and log in, then press Enter to continue...")
    save_cookies(driver, 'cookies.pkl')
    driver.quit()


