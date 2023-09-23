from requests.structures import CaseInsensitiveDict
import os
import warnings
import sys
from pathlib import Path
import time
import csv  # Import the csv module
import asyncio # for asynchronous process
import aiofiles
import pandas as pd
import requests

try: 
    import cfscrape
except (ModuleNotFoundError, ImportError):
    print("cfscrape module not found")
    os.system(f"{sys.executable} -m pip install -U cfscrape")
finally:
    import cfscrape

try:
    from bs4 import BeautifulSoup as bs
except (ModuleNotFoundError, ImportError):
    print("BeautifulSoup module not found")
    os.system(f"{sys.executable} -m pip install -U beautifulsoup4")
finally:
    from bs4 import BeautifulSoup as bs

session = requests.Session()
scraper = cfscrape.create_scraper(sess=session)

url_home = "https://indiankanoon.org"
url_browse = url_home + "/browse/"
df = []

def crawler(url):
    try:
        content_home = scraper.get(url).content
        return bs(content_home, features="lxml")
    except Exception as e:
        print(f"Error while fetching {url}: {e}")
        return None

async def write_to_csv(csv_path, list):
    try:
        async with aiofiles.open(csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(list)
    except Exception as e:
        print(f"Error while writing to CSV: {e}")

async def results(court, id, year, month, s, csv_path, df):
    try:
        for res in s.find_all('div', attrs={'class': 'result_title'}):
            title = res.a.string
            file_num = res.a['href'].split('/')[2]
            # print(f"{title} : {file_num}")

            url = url_home + '/doc/' + file_num + '/'
            object = {
                    "court": court,
                    "year": year,
                    "title": title,
                    "month": month,
                    "url": url,
                    "file_num": file_num,
                }
            if object not in df:
                df.append(object)
        print(year , " + ",len(df))
        # await write_to_csv(csv_path, list)
    except Exception as e:
        print(f"Error while processing search results: {e}")

async def months(court, id, year, s, csv_path,df):
    try:
        data = []
        months, months_url = [], []
        for month in s.find_all('a', href=True):
            month_name = month.string.strip()
         
            months.append(month_name)
            months_url.append(month['href'])

        for i in range(3, len(months)):
            url = url_home + months_url[i]
            s =  crawler(url)
            await results(court, id, year, months[i], s, csv_path,df)
            pages_url = []
            for res in s.find_all('span', attrs={'class':'pagenum'}) :
                pages_url.append(res.a['href'])
                data.append(res.a['href'])

            for n in range(0, len(pages_url)):
                url1 = url_home+pages_url[n]
                s1 = crawler(url1)
                await results(court, id, year, months[i], s1, csv_path,df)
                if n == len(pages_url)-1:
                    for res1 in s1.find_all('span', attrs={'class':'pagenum'}) :
                        if res1.a['href'] not in data:
                            pages_url.append(res1.a['href'])
                            data.append(res1.a['href'])
                    await scroll_next(pages_url[n:len(pages_url)],court,id,year,months[i],data, csv_path,df)

            # ... (same code as before)
    except Exception as e:
        print(f"Error while processing months: {e}")


async def scroll_next(pages,court,id,year,months,data,csv_path,df):
    for j in range(0, len(pages)-1):
        url2 = url_home+pages[j]
        s2 = crawler(url2)
        await results(court, id, year, months, s2,csv_path,df)
        if j == len(pages)-1:
            for ress1 in s2.find_all('span', attrs={'class':'pagenum'}) :
                if ress1.a['href'] not in data:
                    pages.append(ress1.a['href'])
                    data.append(ress1.a['href'])
            if len(pages)-1 > j:
                await scroll_next(pages[j+1:len(pages)-1],court,id,year,months,data,csv_path,df)

# ... (rest of the code remains the same)

async def court_years(court, id, csv_path,df):
    try:
        s = crawler(url_home + id)
        years = []

        for year in s.find_all('a', href=True):
            years.append(year.string)

        for i in range(3, len(years)):
            url = url_home + id + '/' + years[i]
            s = crawler(url)
            await months(court, id, years[i], s, csv_path,df)
    except Exception as e:
        print(f"Error while processing court years: {e}")

async def courts(s, csv_path,df):
    try:
        courts_name, courts_id = [], []
        for court in s.find_all('a', href=True):
            courts_name.append(court.string)
            courts_id.append(court['href'])

        for i in range(3, len(courts_name)):
            await court_years(courts_name[i], courts_id[i], csv_path,df)
    except Exception as e:
        print(f"Error while processing courts: {e}")

async def main():
    print("---- Indian Kanoon web crawler ----")

    csv_path = 'document_info.csv'  # CSV file path
    if os.path.exists(csv_path):
        os.remove(csv_path)  # Remove existing CSV file

    

    soup = crawler(url_browse)
    await courts(soup, csv_path, df)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(df)  # Write header

if __name__ == '__main__':
    asyncio.run(main()) # invoke function to run async
