import os
import sys
import time
import requests
from bs4 import BeautifulSoup

try:
    import cfscrape
except ImportError:
    print("cfscrape module not found")
    os.system(f"{sys.executable} -m pip install -U cfscrape")
    import cfscrape

# Define constants
BASE_URL = "https://indiankanoon.org"
DATA_PATH = "Documents"

# Create a session to persist cookies and headers
session = requests.Session()
scraper = cfscrape.create_scraper(sess=session)

def crawl_url(url):
    try:
        response = scraper.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching {url}: {e}")
        return None

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Error while creating directory {path}: {e}")

def download_pdf(url, save_path, title):
    try:
        response = scraper.get(url)
        response.raise_for_status()
        title = title.replace('/', '-')
        file_path = os.path.join(DATA_PATH, save_path, f"{title}.pdf")
        create_directory(os.path.dirname(file_path))
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error while downloading {url}: {e}")

def scrape_results(court, year, month, soup):
    try:
        results = soup.find_all('div', class_='result_title')
        for result in results:
            title = result.a.string
            file_num = result.a['href'].split('/')[2]
            print(f"{title} : {file_num}")
            # Download the PDF
            download_url = f"{BASE_URL}/doc/{file_num}/"
            download_pdf(download_url, f"{court}/{year}/{month}", title)
    except Exception as e:
        print(f"Error while processing search results: {e}")

def scrape_months(court, year, soup):
    try:
        months = soup.find_all('a', href=True)
        for month_tag in months[3:]:
            month_name = month_tag.string.strip()
            if month_name.lower() == "entire year":
                continue
            month_url = month_tag['href']
            month_soup = crawl_url(f"{BASE_URL}{month_url}")
            if month_soup:
                scrape_results(court, year, month_name, month_soup)
    except Exception as e:
        print(f"Error while processing months: {e}")

def scrape_years(court, id):
    try:
        court_url = f"{BASE_URL}{id}"
        court_soup = crawl_url(court_url)
        if not court_soup:
            return
        years = court_soup.find_all('a', href=True)
        for year_tag in years[3:]:
            year = year_tag.string
            year_url = year_tag['href']
            year_soup = crawl_url(f"{BASE_URL}{year_url}")
            if year_soup:
                scrape_months(court, year, year_soup)
            time.sleep(2)  # Delay to avoid scraping rate limits
    except Exception as e:
        print(f"Error while processing court years: {e}")

def scrape_courts(soup):
    try:
        court_links = soup.find_all('a', href=True)
        for court_link in court_links[3:]:
            court_name = court_link.string
            court_id = court_link['href']
            scrape_years(court_name, court_id)
    except Exception as e:
        print(f"Error while processing courts: {e}")

def main():
    print("---- Indian Kanoon web crawler ----")
    create_directory(DATA_PATH)
    browse_soup = crawl_url(f"{BASE_URL}/browse")
    if browse_soup:
        scrape_courts(browse_soup)

if __name__ == '__main__':
    main()
