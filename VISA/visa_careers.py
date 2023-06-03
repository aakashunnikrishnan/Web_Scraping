import requests
import json
import pandas as pd

class JobScraper:
    def __init__(self, url):
        self.url = "https://search.visa.com/CAREERS/careers/jobs?q="
    def get_payload_and_heasers(self,i):
        payload = json.dumps({
            "from": i,
            "size": 10
        })
        headers = {
            'authority': 'search.visa.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://www.visa.co.in',
            'referer': 'https://www.visa.co.in/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Cookie': '__cfruid=6dc367627b0f379bdf192beb66a7086c45c556ea-1685820794; lbs=!H3CfNWSeQue7AdPgKmkuYjg/8B7WL0q1/tKcF9iGwgoIA90R0JpIZZLfYHLRFMu8BDframQx7FJhLTginF46aA3e/giMMHLwfQaO6OLd'
        }
        return payload,headers

    def fetch_page(self):
        job_count = self.get_job_count()
        response_jsons = []
        for i in range(0, job_count, 10):
            payload, headers = self.get_payload_and_heasers(i)
            response = requests.request("POST", self.url, headers=headers, data=payload)
            response_jsons.append(response.json())
        return response_jsons

    def get_job_count(self):
        payload, headers = self.get_payload_and_heasers(0)
        response = requests.request("POST", self.url, headers=headers, data=payload)
        response = response.json()
        job_count = response["totalRecords"]
        return job_count


    def extract_jobs(self):
        response_jsons = self.fetch_page()
        jobs = []
        for json in response_jsons:
            job_listings = json["jobDetails"]
            for listing in job_listings:
                job = {}
                job['title'] = listing["jobTitle"]
                job['apply_link'] = listing["applyUrl"]
                job['description'] = listing["jobDescription"]
                job['qualifications'] = listing['qualifications']
                jobs.append(job)
        return jobs

    def crawl_jobs(self):
        jobs = self.extract_jobs()
        return jobs


# Usage example
scraper = JobScraper("https://www.visa.co.in/en_in/jobs/")
job_data = scraper.crawl_jobs()
df = pd.DataFrame(job_data)
df.to_csv("data.csv",index=False)
