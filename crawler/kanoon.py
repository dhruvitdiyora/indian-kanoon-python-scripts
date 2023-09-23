from requests.structures import CaseInsensitiveDict # request CaseInsensitiveDicts
import os
import warnings
import sys
from pathlib import Path # for creating directories
import time


try: 
    import cfscrape # scrape clouflare websites
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


scraper = cfscrape.create_scraper() # create cfscrape object
url_home = "https://indiankanoon.org" # home url
url_browse = url_home+"/browse/"

def crawler(url) : # scrape content from web pages
    try:
        content_home = scraper.get(url).content
        return bs(content_home, features="html.parser")
    except Exception as e:
        print(f"Error while fetching {url}: {e}")
        return None

def makedir(path): # make directories if not presesnt
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error while creating directory {path}: {e}")

def download(url, path, title) : # downloads pdfs from url
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
        time.sleep(0.5) # delay for 1 second to overcome scrapping limit per second
    except Exception as e:
        print(f"Error while downloading {url}: {e}")


def results(court, id, year, month, s): # fetches doc links from search results
    try:
        for res in s.find_all('div', attrs={'class':'result_title'}) :

            title = res.a.string
            file_num = res.a['href'].split('/')[2]
            print(f"{title} : {file_num}")
            download(url_home+'/doc/'+file_num+'/', court+'/'+year+'/'+month+'/', title)
    except Exception as e:
        print(f"Error while processing search results: {e}")
 


def months(court, id, year, s) : # fetches links for each month
    try:
        data = []
        months, months_url = [], []
        for month in s.find_all('a', href=True) :
            months.append(month.    )
            months_url.append(month['href'])

        for i in range(3, len(months)):
            url = url_home+months_url[i]
            s = crawler(url)
            results(court, id, year, months[i], s)

            pages_url = []
            for res in s.find_all('span', attrs={'class':'pagenum'}) :
                pages_url.append(res.a['href'])
                data.append(res.a['href'])

            for n in range(0, len(pages_url)):
                url1 = url_home+pages_url[n]
                s1 = crawler(url1)
                results(court, id, year, months[i], s1)
                if n == len(pages_url)-1:
                    for res1 in s1.find_all('span', attrs={'class':'pagenum'}) :
                        if res1.a['href'] not in data:
                            pages_url.append(res1.a['href'])
                            data.append(res1.a['href'])
                    scroll_next(pages_url[n:len(pages_url)],court,id,year,months[i],data)
    except Exception as e:
        print(f"Error while processing months: {e}")
    
def scroll_next(pages,court,id,year,months,data):
    for j in range(0, len(pages)-1):
        url2 = url_home+pages[j]
        s2 = crawler(url2)
        results(court, id, year, months, s2)
        if j == len(pages)-1:
            for ress1 in s2.find_all('span', attrs={'class':'pagenum'}) :
                if ress1.a['href'] not in data:
                    pages.append(ress1.a['href'])
                    data.append(ress1.a['href'])
            if len(pages)-1 > j:
                scroll_next(pages[j+1:len(pages)-1],court,id,year,months,data)


def court_years(court, id): # fetches links for each year
    try:
        s = crawler(url_home+id)
        years = []
        
        for year in s.find_all('a', href=True) :
            years.append(year.string)

        for i in range(3, len(years)):
            url = url_home+id+'/'+years[i]
            s = crawler(url)
            months(court, id, years[i], s)
            time.sleep(2) # delay for 2 second to overcome scrapping limit per second
    except Exception as e:
        print(f"Error while processing court years: {e}")


def courts(s) : # fetches links for each court
    try:
        courts_name, courts_id = [], []
        for court in s.findAll('a', href=True) :
            courts_name.append(court.string)
            courts_id.append(court['href'])

        for i in range(3, len(courts_name)):
            court_years(courts_name[i], courts_id[i])
    except Exception as e:
        print(f"Error while processing courts: {e}")

def main() :  
    print("---- Indian Kanoon web crawler ----")

    soup = crawler(url_browse) # scrape browse page for courts
    courts(soup)

if __name__ == '__main__':
    main() # invoke function

    