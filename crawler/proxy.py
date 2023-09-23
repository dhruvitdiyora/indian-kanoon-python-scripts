from email import utils
from fp.fp import FreeProxy
from selenium_stealth import stealth


u = utils()

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-features=GenericSensorExtraClasses')

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

timeout=60

def get_proxy():
    proxy= FreeProxy().get()
    return(proxy.split('/')[-1])

driver = webdriver.Chrome(chrome_options=options)
wait = WebDriverWait(driver, 30)
driver.implicitly_wait(15)
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
        
def reinitialize(rotate_proxy:bool): #rotate_proxy when true . it reinitializes wendriver in new proxy 
        print("\n\nReInitializing\n\n")
        if rotate_proxy:
            print("\n\nRotating proxy\n\n")
            PROXY=get_proxy()
            webdriver.DesiredCapabilities.CHROME['proxy'] = {
                "httpProxy": PROXY,
                "ftpProxy": PROXY,
                "sslProxy": PROXY,
                "proxyType": "MANUAL",
            }
            webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True
        print(webdriver.DesiredCapabilities.CHROME)

        driver = webdriver.Chrome(chrome_options=options)
        wait = WebDriverWait(driver, 30)
        driver.implicitly_wait(15)

        return driver