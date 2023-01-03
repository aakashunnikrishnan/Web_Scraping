import time
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys



class lowesStock:
    def __init__(self,url):
        self.url = url
        self.data = []
        self.execute()
        #self.get_fetch()

    def close_popup(self,driver):
        popup = driver.find_element(By.XPATH, '//div[@id="onetrust-close-btn-container"]/button')
        popup.click()
    def set_address(self,driver,zipcode):
        button = driver.find_element(By.XPATH, '//div[@class="sc-8yiyp5-0 kUywgq mastheadstyle"]')
        button.click()
        time.sleep(10)
        input = driver.find_element(By.XPATH, '//div[@class="inputContainer"]/form/div/input')
        time.sleep(5)
        input.send_keys(zipcode)
        button = driver.find_element(By.XPATH,'//button[@class="ButtonBase-sc-1ngvxvr-0 ehyYDO backyard button size--medium variant--primary color--interactive shape--rounded updateButton"]')
        button.click()
        return driver
    def set_store(self,driver,store_id):
        button = driver.find_element(By.XPATH, '//a[@data-linkid="selected-store"]')
        button.click()
        time.sleep(10)
        input = driver.find_element(By.XPATH, '//div[@class="inputContainer"]/form/div/input')
        i = 0
        # input.clear()
        while i < 4:
            i = i + 1
            input.send_keys(Keys.BACK_SPACE)
        time.sleep(5)
        input.send_keys(store_id)
        button = driver.find_element(By.XPATH,'//button[@class="ButtonBase-sc-1ngvxvr-0 ehyYDO backyard button size--small variant--primary color--interactive shape--squared rightArrowBtn"]')
        button.click()
        time.sleep(10)
        set_store_button = driver.find_element(By.XPATH, '//div[@class="buttonsWrapper"]/button')
        set_store_button.click()
        return driver
    def read_csv(self):
        df = pd.read_csv("../Acehardware/input.csv")
        zipcode_list = [
    {"zipcode": 19335, "store_id": 1729},
    {"zipcode": 22030, "store_id": 3274},
    {"zipcode": 32818, "store_id": 642},
    {"zipcode": 45213, "store_id": 1585},
    {"zipcode": 75209, "store_id": 2280},
    {"zipcode": 80012, "store_id": 102},
    {"zipcode": 90019, "store_id": 2714},
    {"zipcode": 30004, "store_id": 615},
    {"zipcode": 97223, "store_id": 1108},
    {"zipcode": 60174, "store_id": 1738}
]
        store_links = []
        for index, row in df.iterrows():
            # zipcode_dict = {}
            # zipcode_dict["zipcode"] = row['zipcode']
            # zipcode_dict["store_id"] = row['store_id']
            # if zipcode_dict not in zipcode_list:
            #     zipcode_list.append(zipcode_dict)
            link = row['sku']
            store_links.append(link)
        return zipcode_list,store_links
    def execute(self):
        zipcode_list, store_links = self.read_csv()
        driver = self.get_driver()
        for dict in zipcode_list:
            driver.get(self.url)
            driver = self.set_store(driver,dict["store_id"])
            time.sleep(10)
            driver = self.set_address(driver,dict["zipcode"])
            time.sleep(10)
            for url in store_links:
                fetch_link = self._generate_fetch_link(url,dict["store_id"],dict["zipcode"])
                driver.get(fetch_link)
                time.sleep(10)
                page_source = driver.page_source
                self.get_fetch(page_source)
        self.close_driver(driver)

    def _generate_fetch_link(self, url,store_id,zipcode):
        sku_id = str(url).split("/")[-1]
        fetch_link =  f'https://www.lowes.com/wpd/{sku_id}/productdetail/{store_id}/Guest/{zipcode}'
        print(fetch_link)
        return fetch_link

    def get_driver(self):
        uc.TARGET_VERSION = 111
        driver = uc.Chrome()
        time.sleep(10)
        return driver

    def close_driver(self,driver):
        driver.close()
        driver.quit()
    def get_fetch(self,page_source):
        page_source  = page_source.replace('<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', '')
        page_source = page_source.replace('</pre></body></html>', '')
        page_source = json.loads(page_source)
        final_data = self._crawl_data(self.url,"https://www.lowes.com/wpd/5014261341/productdetail/1108/Guest/97223",page_source)
        self.write_csv(final_data)

    def write_csv(self,data):
        df = pd.DataFrame(data)
        #df = df.drop_duplicates()
        df.to_csv("lowes_stock_1.csv", index=False)
    def _crawl_data(self, original_link, manipulated_url, json_data):
        # Product Rating, Review/Rating Count, SKU, Address, Brand
        # global review_base, count, review_count
        try:
            store_name = json_data['storeDetails']['storeName']
        except:
            store_name = ''
        try:
            sku_id = json_data['productId']
        except:
            sku_id = ''
        try:
            review_count = json_data['ratings'][sku_id]['reviewCount']
        except:
            review_count = ''
        try:
            rating = json_data['ratings'][sku_id]['rating']
        except:
            rating = ''
        try:
            model_id = json_data['productDetails'][sku_id]['product']['modelId']
        except:
            model_id = ''

        try:
            title = json_data['productDetails'][sku_id]['product']['title']
        except:
            title = ''

        try:
            brand = json_data['productDetails'][sku_id]['product']['brand']
        except:
            brand = ''
        try:
            source = 'Lowes'
        except:
            source = 'Lowes'
        try:
            product_rating = json_data['productDetails'][sku_id]['product']['rating']
        except:
            product_rating = ''

        try:
            sellingPrice = json_data['productDetails'][sku_id]['mfePrice']['price']['additionalData']['sellingPrice']
        except:
            sellingPrice = ''
        try:
            retailPrice = json_data['productDetails'][sku_id]['mfePrice']['price']['additionalData']['retailPrice']
        except:
            retailPrice = ''
        try:
            zipcode = json_data['storeDetails']['zipCode']
        except:
            zipcode = ''

        try:
            address = json_data['storeDetails']['address']
        except:
            address = ''
        try:
            city = json_data['storeDetails']['city']
        except:
            city = ''

        try:
            state = json_data['storeDetails']['state']
        except:
            state = ''

        try:
            store_id = json_data['storeDetails']['id']
        except:
            store_id = ''

        # print(json_data)

        # 1 :https://www.lowes.com/pd/Valspar-Polyester-Angle-1-5-in-Paint-Brush/1002276942

        # Pick up data
        try:
            pickup_onhandQty = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
                'onhandQty']
        except:
            pickup_onhandQty = ''
        try:
            pickup_itmLdTm = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
                'itmLdTm']
        except:
            pickup_itmLdTm = ''
        # out of stock
        try:
            availability_Status = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
                'availabilityStatus']
        except:
            availability_Status = ''

        # try:
        #     pickup_productStockType = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
        #         'productStockType']
        # except:
        #     pickup_productStockType = ''
        try:
            pickup_deliveryMethodName = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
                'deliveryMethodName']
        except:
            pickup_deliveryMethodName = ''

        # 2:https://www.lowes.com/pd/Zibra-Chiseled-Wedge-Polyester-Angle-2-in-Paint-Brush/50053471

        # Pick up data
        try:
            nearbyStore_code = json_data['productDetails'][sku_id]['product']['nearbyStore']
        except:
            nearbyStore_code = ''

        try:
            nearbyStore_code_2 = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
                'nearestStores'][0]['lctNbr']
        except:
            nearbyStore_code_2 = ''

        # try:
        #     nearbyStore_distance = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
        #         'nearestStores'][0]['distance']
        # except:
        #     nearbyStore_distance = ''

        try:
            nearbyStore_stock_count = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
                'nearestStores'][0]['onhandQty']
        except:
            nearbyStore_stock_count = ''

        try:
            nearbyStore_stock_date = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['pickup'][
                'nearestStores'][0]['itmLdTm']
        except:
            nearbyStore_stock_date = ''

        # Truck_delivery
        try:
            Truck_Delivery_date = json_data['productDetails'][sku_id]['itemInventory']['analyticsData']['truck'][
                'itmLdTm']
        except:
            Truck_Delivery_date = ''

        # Delivery itmConsolidationApptDate
        try:
            itmConsolidationApptDate = \
                json_data['productDetails'][sku_id]['location']['itemInventory']['itemAvailList'][2][
                    'itmConsolidationApptDate']
        except:
            itmConsolidationApptDate = ''
        try:
            itmConsolidationDate = json_data['productDetails'][sku_id]['location']['itemInventory']['itemAvailList'][2][
                'itmConsolidationDate']
        except:
            itmConsolidationDate = ''

        # Product location
        try:
            aisle = json_data['productDetails'][sku_id]['itemInventory']['productLocation']['aisle']
        except:
            aisle = ''
        try:
            bay = json_data['productDetails'][sku_id]['itemInventory']['productLocation']['bay']
        except:
            bay = ''

        try:
            trace_store_number = json_data['productDetails'][sku_id]['location']['storeNumber']
        except:
            trace_store_number = ''

        global specs_count, specs_base, package_quantity_value
        try:
            specs_base = json_data['productDetails'][sku_id]['product']['specs']
            if specs_base:
                specs_count = 0
                for _ in specs_base:
                    specs_count += 1
        except Exception as e:
            print(e, "***************m", specs_base)
        package_quantity_value = None
        for page in range(specs_count):
            if specs_base[page]['key'] == 'Package Quantity':
                package_quantity_value = specs_base[page]['value']
                print("NOTE:Packing quantity found for sku:", package_quantity_value)

        temp_dict = {"sku_id": sku_id, "review_count": review_count, "rating": rating, "model_id": model_id,
                     "brand": brand, "source": source, "product_rating": product_rating, "sellingPrice": sellingPrice,
                     "retailPrice": retailPrice, "zipcode": zipcode, "address": address, "city": city, "state": state,
                     "original_link": original_link, "package_quantity": package_quantity_value,
                     "pickup_onhandQty": pickup_onhandQty,
                     "pickup_itmLdTm": pickup_itmLdTm,
                     "pickup_deliveryMethodName": pickup_deliveryMethodName,
                     "nearbyStore_code": nearbyStore_code,
                     "nearbyStore_code_2": nearbyStore_code_2,
                     "nearbyStore_stock_count": nearbyStore_stock_count,
                     "nearbyStore_stock_date": nearbyStore_stock_date,
                     "Truck_Delivery_date": Truck_Delivery_date,
                     "itmConsolidationApptDate": itmConsolidationApptDate,
                     "aisle": aisle,
                     "bay": bay, "store_id": store_id, "crawled_date": datetime.now(), "store_name": store_name,
                     "manipulated_url": manipulated_url, "raw_json": json_data,
                     "itmConsolidationDate": itmConsolidationDate, "title": title,
                     "availability_Status": availability_Status, "trace_store_number": trace_store_number}
        # print(temp_dict)
        self.data.append(temp_dict)
        # print(final_data)
        return self.data

url = "https://www.lowes.com/pd/Zibra-1-Paint-Brush-Common-Actual/1003016466"
sc = lowesStock(url)

























