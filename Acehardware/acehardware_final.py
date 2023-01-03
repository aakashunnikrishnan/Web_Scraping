import re
import time
import requests
import json
import random
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class acehardwareStockAvailability:
    def __init__(self,url,store_id):
        self.url = url
        self.store_id = store_id
    def get_payload(self,productCode,storeCode):
        payload = json.dumps({
            "productCode": productCode,
            "storeCode": storeCode,
            "quantity": 1
        })
        return payload
    def get_headers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Referer': 'https://www.acehardware.com',
            'x-vol-currency': 'USD',
            'x-vol-locale': 'en-US',
            'x-vol-tenant': '24645',
            'x-vol-site': '37138',
            'x-vol-master-catalog': '1',
            'x-vol-catalog': '1',
            'Origin': 'https://www.acehardware.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'TE': 'trailers'
        }
        return headers
    def get_product_id(self):
        product_id = self.url.split("/")[-1]
        return product_id

    def get_responce(self):
        headers = self.get_headers()
        product_id = self.get_product_id()
        payload = self.get_payload(product_id,self.store_id)
        url = "https://www.acehardware.com/getProductDetailInventory"
        host = 'brd.superproxy.io'
        port = 22225
        username = 'brd-customer-hl_4ac99c27-zone-aakash_lowes_testing_residen'
        password = 'leawkdgn91zl'
        session_id = random.random()
        proxy_url = ('http://{}-session-{}:{}@{}:{}'.format(username, session_id, password, host, port))
        proxies = {'http': proxy_url, 'https': proxy_url}
        response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies, verify=False)
        return response

    def get_stock_details(self):
        response = self.get_responce()
        response = response.json()
        raw = {}
        raw["Root"] = self.url
        raw["store_stockAvailable"] = response["storeInventory"]["stockAvailable"]
        raw["store_softStockAvailable"] = response["storeInventory"]["softStockAvailable"]
        raw["store_Product ID"] = response["storeInventory"]["productCode"]
        raw["store_Store ID"] = response["storeInventory"]["locationCode"]
        raw["store_inventoryLocatorName"] = response["storeInventory"]["inventoryLocatorName"]

        raw["sts_stockAvailable"] = response["stsInventory"]["stockAvailable"]
        raw["sts_softStockAvailable"] = response["stsInventory"]["softStockAvailable"]
        raw["sts_Product ID"] = response["stsInventory"]["productCode"]
        raw["sts_Store ID"] = response["stsInventory"]["locationCode"]

        raw["rsc_stockAvailable"] = response["rscInventory"]["stockAvailable"]
        raw["rsc_softStockAvailable"] = response["rscInventory"]["softStockAvailable"]
        raw["rsc_Product ID"] = response["rscInventory"]["productCode"]
        raw["rsc_Store ID"] = response["rscInventory"]["locationCode"]
        return raw

class acehardwareStock:
    def __init__(self,urls,zipcodes):
        self.urls = urls
        self.zipcodes = zipcodes
        self.data = []
        self.iterate()

    def close_popup(self,driver):
        popup = driver.find_element(By.XPATH, '//div[@id="onetrust-close-btn-container"]/button')
        popup.click()
    def close_driver(self,driver):
        driver.close()
        driver.quit()
    def get_driver(self):
        uc.TARGET_VERSION = 111
        driver = uc.Chrome()
        time.sleep(10)
        driver.get("https://www.acehardware.com/departments/paint-and-supplies/painting-tools-and-supplies/paint-brushes/1188192")
        time.sleep(20)
        return driver
    def set_address(self,driver,zipcode):
        button = driver.find_element(By.XPATH,'//button[@class="storeInfoHeader"]')
        button.click()
        time.sleep(10)
        input = driver.find_element(By.XPATH,'//input[@id="store-location-search"]')
        input.send_keys(zipcode)
        button = driver.find_element(By.XPATH, '//button[@id="store-locator-search-btn"]')
        button.click()
        time.sleep(10)
        overlay_element = WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, 'onetrust-reject-all-handler')))
        dynamic_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@id, "shop-this-store-btn-")]')))
        dynamic_button.click()
        return driver

    def iterate(self):
        driver = self.get_driver()
        self.close_popup(driver)
        for zipcode in self.zipcodes:
            driver = self.set_address(driver,zipcode)
            for url in self.urls:
                # driver.get(url)
                # time.sleep(10)
                # page_source = driver.page_source
                # store_id = self.get_storeID(page_source)
                # row = self.get_details(page_source)
                # stock_data = acehardwareStockAvailability(url, store_id).get_stock_details()
                # row.update(stock_data)
                # row.update({"input url": url, "input zipcode": zipcode})
                # self.data.append(row)
                # print(row)
                # self.write_csv(self.data)
                try:
                    driver.get(url)
                    time.sleep(10)
                    page_source = driver.page_source
                    store_id = self.get_storeID(page_source)
                    row = self.get_details(page_source)
                    try:
                        stock_data = acehardwareStockAvailability(url,store_id).get_stock_details()
                        row.update(stock_data)
                    except:
                        pass
                    row.update({"input url":url,"input zipcode":zipcode})
                    self.data.append(row)
                    print(row)
                    self.write_csv(self.data)
                except:
                    pass
        self.close_driver(driver)

    def get_storeID(self,page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        store_id = soup.find('div', {'class': 'store-card-details-link'}).find('a').get('href')
        store_id = store_id.split("/")[-1]
        return store_id

    def write_csv(self,data):
        df = pd.DataFrame(data)
        df = df.drop_duplicates()
        df.to_csv("acehardware_stock_data_6564345346.csv", index=False)
    def get_details(self,page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        row = {}

        property_json = str(soup.find('script', {'id': 'data-mz-preload-routeData'}))
        property_json = property_json.replace('<script id="data-mz-preload-routeData" type="text/json">','')
        property_json = property_json.replace('</script>','')
        property_json = json.loads(property_json)

        address_json = str(soup.find('script', {'id': 'data-mz-preload-globalCustomData'}))
        address_json = address_json.replace('<script id="data-mz-preload-globalCustomData" type="text/json">', '')
        address_json = address_json.replace('</script>', '')
        address_json = json.loads(address_json)
        print(address_json)



        element_1 = soup.find('div', {'class': 'col-lg-12 col-xs-12 adjust-padding'})
        row["Store Name"] = element_1.find('h2', {'class': 'store-name'}).text.strip()
        row["Store Address"] = address_json["address"]["address1"]+address_json["address"]["address2"]+address_json["address"]["address3"]+address_json["address"]["address4"]
        row["City"] = address_json["address"]["cityOrTown"]
        row["Store State"] = address_json["address"]["stateOrProvince"]
        row["Store Zipcode"] = address_json["address"]["postalOrZipCode"]
        row["StoreID"] = address_json["code"]
        row["Item No"] = soup.find('span', {'itemprop': 'sku'}).text.strip()
        row["Mfr No"] = soup.find('span', {'itemprop': 'mpn'}).text.strip()
        row["SKU"] = soup.find('h1', {'class': 'mz-pagetitle'}).text.strip()
        row["Price"] = soup.find('span', {'class': 'custom-price mz-price'}).text.strip()
        #row["Discounted Price"] = soup.find('span', {'class': 'custom-price mz-price'}).text.strip()
        row["Brand"] = property_json["tenant~A00413"]
        row["Overall Rating"] = soup.find('div', {'class': 'pr-snippet-rating-decimal'}).text.strip()
        row["Review Count"] = soup.find('span', {'class': 'pr-review-count'}).text.strip().replace("-","")
        try:
            row["Estimation of Reviews in Last 12 Months"] = (int(row["Review Count"])//12)+1
        except:
            pass
        try:
            package = property_json["tenant~A02370"]
            if package != "1-pack":
                row["Multi-Pack or Individual"] = "Multi-Pack"
                row["Units in Multi-Pack"] = package
            else:
                row["Multi-Pack or Individual"] = "Individual"
                row["Units in Multi-Pack"] = "Not Applicable"
        except:
            pass
        try:
            row["Availability"] = element_1.find('p').text.strip()
        except:
            row["Availability"] = "Unavailable"
        row["Pickup Date"] = soup.find('span', {'class': 'ispu-epud'}).text.strip()
        row["Delivery Date"] = soup.find('span', {'class': 'custom-span'}).find('span').text
        current_time = datetime.now().time()
        row["Crawled time"] = current_time.strftime("%H:%M:%S")
        current_date = datetime.now().date()
        row["Crawled date"] = current_date.strftime("%Y-%m-%d")
        
        return row
# zipcodes = ["30062","60134","97224"]
zipcodes = ["60134"]

urls = ["https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/45892",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/4595534",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/4595542",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/47522",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/47889",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/4924494",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/6406383",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/6406417",
"https://www.acehardware.com/departments/heating-and-cooling/thermostats-and-heating-supplies/duct-tape/6406425",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/1025261",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/1025328",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/1339241",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/1590413",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/1590421",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/1614775",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/2114635",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/2135309",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/22020",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/22021",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/22022",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/3808623",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/4596623",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/4651519",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/6013200",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/6035841",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/8938912",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9001074",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9004151",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9005752",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9009861",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9009879",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9023686",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9027477",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9027478",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9039587",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/90706",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/90707",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/90709",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9071678",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/90823",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/90877",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9090671",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9092198",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9092206",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/90968",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/90969",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91112",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91115",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91120",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91121",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91122",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91243",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9161878",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9162215",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91623",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91624",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91644",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91646",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/91807",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9196528",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9221896",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9221920",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9329814",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9329822",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9329830",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9329848",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/93505",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9392549",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9429432",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9432626",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9432667",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9432675",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9432691",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9432725",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9432824",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9432857",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9434234",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9434242",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9761552",
"https://www.acehardware.com/departments/home-and-decor/office-supplies/tape/9761560"]
sc = acehardwareStock(urls,zipcodes)

























