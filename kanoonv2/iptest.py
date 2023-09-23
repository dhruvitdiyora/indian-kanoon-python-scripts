import random
import time
import cfscrape # scrape clouflare websites
from fp.fp import FreeProxy

from bs4 import BeautifulSoup as bs # for parsing html
import os


scraper = cfscrape.create_scraper() # create cfscrape object

url_home = "https://indiankanoon.org" # home url
url_browse = "https://indiankanoon.org/search/?formInput=doctypes%3A%20supremecourt%20fromdate%3A%201-1-1947%20todate%3A%2031-12-1947"
count = 0
def get_proxy():
    proxy =  FreeProxy(https=True,anonym=True).get_proxy_list(False)
    # proxy = FreeProxy().get()
    

    return proxy
def crawler(url,proxy) : # scrape content from web pages
    try:
        # proxy ='http://'+proxy
        # random.choice()
        # os.environ['http_proxy'] = proxy 
        # os.environ['HTTP_PROXY'] = proxy
        # os.environ['https_proxy'] = proxy
        # os.environ['HTTPS_PROXY'] = proxy
        # scraper.proxies = {"http": proxy,'https':proxy}
        # content_home = scraper.get(url,verify=False,proxies = {"http": proxy,'https':proxy})
        content_home = scraper.get(url)
        print(content_home.elapsed.total_seconds())
        print(content_home.status_code)
        if content_home.status_code == 200:
            global count 
            count = count +1
            return bs(content_home.content, features="html.parser")
    except Exception as e:
        pass
        # print(f"An error occurred: {str(e)}")

proxie = ['15.152.49.12:9091']

start_time = time.time()

for lp in range(100):
# proxie = get_proxy()
# for i in proxie:
    # i =random.choice(proxie)
    
    # print(i)
    hm= crawler(url_browse,1)
    # print("-----")
end_time = time.time()
print(end_time - start_time)
print(count)
# for item in proxie:
#     proxy = {
#       "http": item
#     }
#     hm= crawler(url_browse,item)
#     print("-----")