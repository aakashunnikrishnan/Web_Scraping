import requests
import json
import pandas as pd
import argparse
import csv
import re
from bs4 import BeautifulSoup
from lxml import etree

class riteaidReviewCrawler:
    def __init__(self, product_id):
        self.product_id = product_id
        self._to_csv(product_id)

    def _get_parameters(self):
        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.riteaid.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.riteaid.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        return headers, payload

    def get_url1(self, product_id):
        url1 = "https://api.bazaarvoice.com/data/products.json?passkey=cap72Fd4Mme89q1eAHJ9FSMuCzWo7B2iyEMKQNJatkIQk&locale=en_US&allowMissing=true&apiVersion=5.4&filter=id:" + str(
            product_id)
        return url1

    def get_url1_json(self, url1):
        url1 = self.get_url1(url1)
        headers, payload = self._get_parameters()
        url1_json = requests.request("GET", url1, headers=headers, data=payload)
        url1_json = url1_json.json()
        return url1_json

    def get_url1_data(self, url1_json):
        url1_json = self.get_url1_json(url1_json)
        basic_details_A = []
        SKU = url1_json["Results"][0]["Name"]
        Brand = url1_json["Results"][0]["Brand"]["Name"]
        Root = url1_json["Results"][0]["ProductPageUrl"]
        basic_details_1 = {
            "SKU": SKU,
            "Brand": Brand,
            "Root": Root
        }
        basic_details_A.append(basic_details_1)
        return basic_details_A

    def get_url2(self, product_id):
        url2 = "https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey=cap72Fd4Mme89q1eAHJ9FSMuCzWo7B2iyEMKQNJatkIQk&productid=" + str(
            product_id) + "&contentType=reviews,questions&reviewDistribution=primaryRating,recommended&rev=0&contentlocale=en*,en_US"
        return url2

    def get_url2_json(self, url2):
        url2 = self.get_url2(url2)
        headers, payload = self._get_parameters()
        url2_json = requests.request("GET", url2, headers=headers, data=payload)
        url2_json = url2_json.json()
        return url2_json

    def get_url2_data(self, url2_json):
        url2_data = self.get_url2_json(url2_json)
        RatingCount = url2_data["reviewSummary"]["numReviews"]
        Product_Rating = url2_data["reviewSummary"]["primaryRating"]["average"]
        return RatingCount, Product_Rating

    def get_product_rating(self, url2_json):
        basic_details_B = []
        RatingCount, Product_Rating = self.get_url2_data(url2_json)
        basic_details_2 = {
            "RatingCount": RatingCount,
            "Product_Rating": Product_Rating
        }
        basic_details_B.append(basic_details_2)
        return basic_details_B

    def get_page_count(self, url2_json):
        RatingCount, Product_Rating = self.get_url2_data(url2_json)
        Page_Count = ((RatingCount - 8) // 30) + 3
        return Page_Count

    def get_reviews_urls(self, product_id, q0=0, q1=8):
        Page_Count = self.get_page_count(product_id)
        headers, payload = self._get_parameters()
        final_review_details = []
        review_url = "https://api.bazaarvoice.com/data/batch.json?resource.q0=reviews&filter.q0=productid%3Aeq%3A" + str(
            product_id) + "&filter.q0=contentlocale%3Aeq%3Aen*%2Cen_US%2Cen_US&filter.q0=isratingsonly%3Aeq%3Afalse&filter_reviews.q0=contentlocale%3Aeq%3Aen*%2Cen_US%2Cen_US&include.q0=authors%2Cproducts&filteredstats.q0=reviews&limit.q0=" + str(
            q1) + "&offset.q0=" + str(
            q0) + "&sort.q0=submissiontime%3Adesc&passkey=cap72Fd4Mme89q1eAHJ9FSMuCzWo7B2iyEMKQNJatkIQk&apiversion=5.5&displaycode=28398-en_us"
        review_json = self.get_reviews_json(review_url)
        review_details = self.get_reviews(review_json)
        final_review_details.extend(review_details)
        i = 0
        q1 = 30
        q0 = 8
        while i < Page_Count:
            review_url = "https://api.bazaarvoice.com/data/batch.json?resource.q0=reviews&filter.q0=productid%3Aeq%3A" + str(
                product_id) + "&filter.q0=contentlocale%3Aeq%3Aen*%2Cen_US%2Cen_US&filter.q0=isratingsonly%3Aeq%3Afalse&filter_reviews.q0=contentlocale%3Aeq%3Aen*%2Cen_US%2Cen_US&include.q0=authors%2Cproducts&filteredstats.q0=reviews&limit.q0=" + str(
                q1) + "&offset.q0=" + str(
                q0) + "&sort.q0=submissiontime%3Adesc&passkey=cap72Fd4Mme89q1eAHJ9FSMuCzWo7B2iyEMKQNJatkIQk&apiversion=5.5&displaycode=28398-en_us"
            q0 = q0 + 30
            i = i + 1
            review_json = self.get_reviews_json(review_url)
            review_details = self.get_reviews(review_json)
            final_review_details.extend(review_details)
        return final_review_details

    def get_reviews_json(self, review_url):
        headers, payload = self._get_parameters()
        review_json = requests.request("GET", review_url, headers=headers, data=payload)
        review_json = review_json.json()
        return review_json

    def get_reviews(self, review_json):
        Elements = review_json["BatchedResults"]["q0"]["Results"]
        ReviewCount = review_json["BatchedResults"]["q0"]["TotalResults"]
        review_details = []
        for element in Elements:
            Review_Rating = element["Rating"]
            Location = element["UserLocation"]
            Review = element["ReviewText"]
            date = element["SubmissionTime"]
            Title = element["Title"]
            Author = element["UserNickname"]
            # Author_age = element["ContextDataValues"]["Age"]["Value"]
            # Author_gender = element["ContextDataValues"]["Gender"]["Value"]
            review_details_raw = {
                "Review Rating": Review_Rating,
                "Review": Review,
                "date": date,
                "Title": Title,
                "Author": Author,
                "Location": Location,
                "ReviewCount":ReviewCount
                # "Author_age":Author_age,
                # "Author_gender":Author_gender
            }
            review_details.append(review_details_raw)
        return review_details

    def _to_csv(self, product_id):
        basic_details_1 = self.get_url1_data(product_id)
        df1 = pd.DataFrame.from_dict(basic_details_1)
        basic_details_2 = self.get_product_rating(product_id)
        df2 = pd.DataFrame.from_dict(basic_details_2)
        review_1 = self.get_reviews_urls(product_id)
        df3 = pd.DataFrame.from_dict(review_1)
        df1["product_id"], df2["product_id"], df3["product_id"] = product_id, product_id, product_id
        df = pd.merge(df1, df2, on="product_id", how="inner")
        dff = pd.merge(df, df3, on="product_id", how="inner")
        dff["Source"] = "Riteaid"
        dff = dff.drop_duplicates()

        dff.to_csv("Riteaid_Reviews" + str(product_id) + ".csv", index=False)

class RiteaidReviewScraper:

    def __init__(self,input_file_path):
        self.input_file_path = input_file_path
    def _all(self):
        row_list = self._read_csv(self.input_file_path)
        product_id = self._riteaid(row_list)

    def _get_parameters(self):
        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.riteaid.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.riteaid.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        return headers, payload
    def _read_csv(self,input_file_path):
        row_list = []
        with open(input_file_path, 'r', newline="") as bf:
            csvf = csv.DictReader(bf, delimiter=',', quotechar='"')
            field_names = csvf.fieldnames
            for row in csvf:
                row_list.append(row["link"])
            return row_list

    def _riteaid(self,row_list):
        row_list = self._read_csv(self.input_file_path)
        for row in row_list:
            product_id = self._get_url_data(row)
            print(product_id)

    def _get_url_data(self,root):
        print(root)
        headers, payload = self._get_parameters()
        url_data = requests.request("GET", root, headers=headers, data=payload)
        soup = BeautifulSoup(url_data.content, "html.parser")
        dom = etree.HTML(str(soup))
        product_id = dom.xpath('/html[1]/body[1]/div[3]/main[1]/div[2]/div[1]/div[3]/div[1]/div[4]/div[1]/div[1]/p[1]')[
            0].text
        product_id = product_id.replace('Item No. ', '')
        crawler = riteaidReviewCrawler(product_id=product_id)
        crawler
        print("Completed")
        return product_id

def main(input_file_path):
    Result = RiteaidReviewScraper(input_file_path)
    Result._all()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file_path", help="input_file_path")
    args = parser.parse_args()
    main(args.input_file_path)
