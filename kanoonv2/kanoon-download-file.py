from requests.structures import CaseInsensitiveDict # request CaseInsensitiveDicts
import cfscrape # scrape clouflare websites
from fp.fp import FreeProxy

from bs4 import BeautifulSoup as bs # for parsing html
from pathlib import Path # for creating directories

import asyncio # for asynchronous process
import aiofiles
import time
import csv  # Import the csv module
import os
import random


url_browse = "https://indiankanoon.org" # home url

scraper = cfscrape.create_scraper() # create cfscrape object


def get_proxy():
    proxy =  FreeProxy().get_proxy_list(False)
    return proxy

async def download(url, path, title) : # downloads pdfs from url
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            print("url:", url)
            path = 'Documents/'+path
            Path(path).mkdir(parents=True, exist_ok=True)
            
            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/x-www-form-urlencoded"

            payload = "type=pdf"
            r = scraper.post(url, data=payload, headers=headers, proxies=)

            if r.status_code == 409:
                print("HTTP 409 error - Too Many Requests. Retrying...")
                retries += 1
                time.sleep(10)  # Wait for a few seconds before retrying
                continue
            if r.status_code == 200:
                title = title.replace('/', '-')
                filename = Path(path+'/'+title+'.pdf')
                filename.write_bytes(r.content)

        except Exception as e:
            print(f"Error while downloading: {e}")

def crawler(url) : # scrape content from web pages
    retries = 0
    max_retries = 5
    while retries < max_retries:

        try:
            # proxy = get_proxy()
            # print(proxy)
            # random.choice()
            # content_home = scraper.get(url,proxies=proxy)
            content_home = scraper.get(url)
            if content_home.status_code == 409:
                print("HTTP 409 error - Too Many Requests. Retrying...")
                retries += 1
                time.sleep(10)  # Wait for a few seconds before retrying
                continue
            if content_home.status_code == 200:
                return bs(content_home.content, features="html.parser")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        print(f"Failed to retrieve {url}. Retrying...")
        retries += 1
        time.sleep(10)  # Wait for a few seconds before retrying

    print(f"Max retries reached for {url}. Giving up.")
    return None


async def main() :  
    try:

        print("---- Indian Kanoon web crawler ----")

        # get base url and total record from csv file using entire year column condition
        csv_file_path = 'document_info.csv'

        with open(csv_file_path, mode="r", newline="") as file:
            csv_reader = csv.DictReader(file)
            
            # Use a list comprehension to filter rows
            matching_rows = [row for row in csv_reader if row["Month"] == "Entire Year"]
        
        for row in matching_rows:
            total_records = row["number"]
            base_url = row["url"]
            if total_records.isdigit():
                total_records = int(total_records)
            else:
                # Handle the case where total_records is not a valid number
                print(f"Skipping row with invalid 'number': {total_records}")
                continue


            num_pages = -(-total_records // 10)  # Ceiling division

        # Generate the dynamic URLs using a list comprehension
            dynamic_urls = [f"{base_url}&pagenum={page_num}" for page_num in range(num_pages)]

        # set proxy list updated for every year in global list so  that can get it random proxy from that only
            proxy_list = get_proxy()





        

        #     soup = crawler(url_browse) # scrape browse page for courts
            #await courts(soup)


    except Exception as e:
        print(f"Error in main function: {e}")
    
if __name__ == '__main__':
    asyncio.run(main()) # invoke function to run async  