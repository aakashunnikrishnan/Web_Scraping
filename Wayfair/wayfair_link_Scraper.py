
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import datetime

import random
import argparse
import pandas as pd
import numpy as np

class Wayfair_Link_Crawler:
    def __init__(self,url,proxy_file,i):
        self.i = i
        self.url = url
        self.proxy_dict = proxy_file
        self.scrape()

    def sleep(self):
        time.sleep(np.random.randint(5, 10))

    def get_proxy(self):
        proxy = random.choice(self.proxy_dict)
        host = proxy['host']
        port = proxy['port']
        username = proxy['username']
        password = proxy['password']
        return host,port,username,password

    def get_options(self):
        proxy_host, proxy_port, proxy_username, proxy_password = self.get_proxy()
        options = Options()
        options.add_argument('--proxy-server=http://%s:%s@%s:%s' % (proxy_username, proxy_password, proxy_host, proxy_port))
        #options.add_argument('--headless')
        return options

    def get_service(self):
        service = Service('/home/aakash/Selenium/WAYFAIR/chromedriver')
        return service
    def scrape(self):
        options = self.get_options()
        service = self.get_service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        driver.maximize_window()
        self.sleep()
        dict = self.get_basic_details(driver)
        print( dict)
        return dict
    def get_basic_details(self,driver):
        self.sleep()
        dict = []
        self.sleep()

        elements = driver.find_elements(By.XPATH, "//div[@class='TrackedProductCardWrapper-extendedInView']")
        for element in elements:
            try:
                sku = element.find_element(By.XPATH, ".//h2/span").text
            except:
                sku = None
            try:
                Brand = element.find_element(By.XPATH, ".//p").text
            except:
                Brand = None
            try:
                link = element.find_element(By.XPATH, ".//a").get_attribute('href')
            except:
                link = None
            try:
                rating = element.find_element(By.XPATH, ".//div[@class='_1xxktfu7_6101 _1xxktfu3_6101 _1xxktfu8_6101']").get_attribute('style').split(";")[0]
            except:
                rating = None
            try:
                count = element.find_element(By.XPATH, ".//div[@class='_1xxktfua_6101 undefined']").text
            except:
                count = None
            try:
                price_overall = element.find_element(By.XPATH, ".//div[@class='SFPrice']").text
            except:
                price_overall = None

            try:
                colors = element.find_element(By.XPATH, ".//div[@class='ProductCardReviews-options']").text
            except:
                colors = None

            dict.append({'SKU':sku,'Brand':Brand,'link':link,'Rating':rating,'Count':count,'Colors Available':colors,
                         'Price Overall':price_overall,'Root':self.url,'Source':"Wayfair"})
        # current_time = datetime.datetime.now().time()
        #
        df = pd.DataFrame(dict)
        df.to_csv("output"+str(self.i)+".csv")


def read_csv(path) :
    input = pd.read_csv(path)
    row_list = []
    for ind in input.index:
        link = input["root"][ind]
        row_list.append(link)
    return row_list
def read_proxy(proxy_file_path) :
    with open(proxy_file_path) as file:
        proxy_lists = file.read().split("\n")
    proxies = [x for x in proxy_lists if x != ""]
    proxy_lists = list()
    for i in proxies:
        proxy_host, proxy_port, username, password = i.split(":")
        proxy_dict = {'host':proxy_host, 'port':proxy_port,'username': username, 'password': password}
        proxy_lists.append(proxy_dict)
    return proxy_lists


def main(input_file_path, proxy_file_path):
    i = 1
    links = read_csv(input_file_path)
    proxy_file = read_proxy(proxy_file_path)
    for link in links:
        print(link)
        Wayfair_Link_Crawler(link, proxy_file,i)
        i = i+1
        print(link)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file_path", help="input_file_path")
    parser.add_argument("--proxy_file_path", help="proxy_file_path")
    args = parser.parse_args()
    main(args.input_file_path, args.proxy_file_path)

#python3 wayfair_link_Scraper.py --input_file_path="input.csv" --proxy_file_path="proxy.txt"

