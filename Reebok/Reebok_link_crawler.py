import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ReebokScraper:
    def __init__(self,url):
        self.start_url = url
        self.driver = None

    def initialize_driver(self):
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)
        self.driver = webdriver.Chrome(options=options)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def scrape_product_links(self):
        self.initialize_driver()
        self.driver.get(self.start_url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="col-lg-4 col-md-4 col-sm-4 col-xs-4 category-list-col"]')))
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="col-lg-4 col-md-4 col-sm-4 col-xs-4 category-list-col"]')

        dict = []
        for element in elements:
            link = element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            sku = element.find_element(By.CSS_SELECTOR, '.row div.col-lg-12:nth-of-type(1)').text
            actual_price = element.find_element(By.CSS_SELECTOR, 'div.actual_price').text
            discounted_price = element.find_element(By.CSS_SELECTOR, 'div.off_price').text
            discount = element.find_element(By.CSS_SELECTOR, 'span.off_bg').text
            dict.append({"Root":self.url,"SKU":sku,"Actual Price":actual_price,"Discounted Price":discounted_price,"Discount":discount,"link":link})

        self.close_driver()
        return dict

    def export_to_csv(self, data, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Root","SKU","Actual Price","Discounted Price","Discount","link"])
            writer.writerows([[link] for link in data])
        print(f"Data exported to {filename} successfully.")

# Usage example
scraper = ReebokScraper("https://www.reebok.in/category/Men-9112?page=3&orderway=asc&orderby=popular")
product_links = scraper.scrape_product_links()
scraper.export_to_csv(product_links, "reebok_product_links.csv")
