from requests.structures import CaseInsensitiveDict # request CaseInsensitiveDicts
import cfscrape # scrape clouflare websites

from bs4 import BeautifulSoup as bs # for parsing html
from pathlib import Path # for creating directories

import asyncio # for asynchronous process
import aiofiles
import time
import csv  # Import the csv module
import os

scraper = cfscrape.create_scraper() # create cfscrape object
url_home = "https://indiankanoon.org" # home url
url_browse = url_home+"/browse/"

def crawler(url) : # scrape content from web pages
    retries = 0
    max_retries = 5
    while retries < max_retries:

        try:
            
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



def makedir(path): # make directories if not presesnt
    Path(path).mkdir(parents=True, exist_ok=True)

async def write_to_csv(csv_path, court,year,month,url,number):
    try:
        with open(csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([court, year, month, url, number])
    except Exception as e:
        print(f"Error while writing to CSV: {e}")

    # try:
    #     async with aiofiles.open(csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
    #         csv_writer = csv.writer(csvfile)
    #         csv_writer.writerow([court,year,month,number])
    # except Exception as e:
    #     print(f"Error while writing to CSV: {e}")

async def download(url, path, title) : # downloads pdfs from url
    try:
        print("url:", url)
        path = 'Documents/'+path
        Path(path).mkdir(parents=True, exist_ok=True)

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        payload = "type=pdf"
        r = scraper.post(url, data=payload, headers=headers)

        title = title.replace('/', '-')
        filename = Path(path+'/'+title+'.pdf')
        filename.write_bytes(r.content)

    except Exception as e:
        print(f"Error while downloading: {e}")


async def results(court, id, year, month, s): # fetches doc links from search results
    try:

        for res in s.find_all('div', attrs={'class':'result_title'}) :
            title = res.a.string
            file_num = res.a['href'].split('/')[2]
            print(f"{title} : {file_num}")
            await download(url_home+'/doc/'+file_num+'/', court+'/'+year+'/'+month+'/', title)
    except Exception as e:
        print(f"Error while processing search results: {e}")



async def months(court, id, year, s) : # fetches links for each month
    try:

        months, months_url = [], []
        for month in s.find_all('a', href=True) :
            months.append(month.string)
            months_url.append(month['href'])

        for i in range(3, len(months)):
            url = url_home+months_url[i]
            s = crawler(url)
            results_middle_div = s.find('div', class_='results_middle')
            result_count_text = results_middle_div.find('b').text

            if result_count_text == 'No matching results':
                await write_to_csv(csv_path,court,year,months[i],url,0)
            else : 
                number = result_count_text.split()[-1]
                csv_path = 'document_info.csv'  # CSV file path
                await write_to_csv(csv_path,court,year,months[i],url,number)
            # await results(court, id, year, months[i], s)
    except Exception as e:
        print(f"Error while processing months: {e}")



async def court_years(court, id): # fetches links for each year
    try:

        s = crawler(url_home+id)
        years = []
        
        for year in s.find_all('a', href=True) :
            years.append(year.string)

        for i in range(3, len(years)):
            url = url_home+id+'/'+years[i]
            s = crawler(url)
            await months(court, id, years[i], s)
    except Exception as e:
        print(f"Error while processing court years: {e}")

        

async def courts(s) : # fetches links for each court
    try:

        courts_name, courts_id = [], []
        for court in s.findAll('a', href=True) :
            courts_name.append(court.string)
            courts_id.append(court['href'])

        for i in range(3, len(courts_name)):
            await court_years(courts_name[i], courts_id[i])
    except Exception as e:
        print(f"Error while processing courts: {e}")


async def main() :  
    try:

        print("---- Indian Kanoon web crawler ----")
        csv_path = 'document_info.csv'  # CSV file path
        if os.path.exists(csv_path):
            os.remove(csv_path)  # Remove existing CSV file

        with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Court", "Year", "Month","url", "number"])  # Write header

        soup = crawler(url_browse) # scrape browse page for courts
        await courts(soup)


    except Exception as e:
        print(f"Error in main function: {e}")
    
if __name__ == '__main__':
    asyncio.run(main()) # invoke function to run async

    