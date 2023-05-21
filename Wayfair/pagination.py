import pandas as pd
import re

def create_pagination_links(base_link, page_count):
    pagination_links = []

    for page_number in range(1, page_count + 1):
        pagination_link = f"{base_link}&curpage={page_number}"

        pagination_links.append(pagination_link)

    return pagination_links

df = pd.read_csv('count.csv')
links = []

for index, row in df.iterrows():
    try:
        base_link = row['web-scraper-start-url']
        page_count = str(row['count']).replace(',', '').replace('Over', '').replace('Results', '')
        print(page_count)
        page_count = int(page_count)//48+1
        if page_count > 200:
            page_count = 200
        pagination_links = create_pagination_links(base_link, page_count)
        for link in pagination_links:
            links.append(link)
    except:
        pass

df = pd.DataFrame(links, columns=['Link']).to_csv("input_links.csv")