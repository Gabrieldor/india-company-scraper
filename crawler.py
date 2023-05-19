from selenium.webdriver import ChromeOptions, Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from multiprocessing import Pool
import pickle
import os


class Scraper():

    def load(self) -> None:
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = Chrome(ChromeDriverManager().install(), options=chrome_options)
        self.driver.set_page_load_timeout(60)
        self.wait = WebDriverWait(self.driver, 60)
        
    def __init__(self) -> None:
        try:
            with open("queue.pickle", 'rb') as f:
                self.q = pickle.load(f)
        except:
            self.q = set()
            self.q.add("https://www.thecompanycheck.com/org/yorfie/8508975a0d")
            with open("queue.pickle", 'wb') as f:
                pickle.dump(self.q, f)
        

    def scrap(self, url) -> None:
        self.load()
        self.q.remove(url)
        self.driver.get(url)
        html = self.driver.page_source
        self.save(url, html)
        similars = self.driver.find_elements(By.XPATH, "//ul[@class='similar-msme-wrap']/li/div[2]/a")
        for similar in similars:
            s = similar.get_attribute("onclick").split("; ")[1].split(",")
            name = s[0].split('(')[1][1:-1].replace(' ', '-')
            ids = s[1][1:-2]
            url = f"https://www.thecompanycheck.com/org/{name}/{ids}"
            self.q.add(url)

        with open("queue.pickle", 'wb') as f:
                pickle.dump(self.q, f)

    def save(self, name, html) -> None:
        name = name.split("://")[1].replace("/", '-')
        if not os.path.exists(f"{name}.html"):
                with open(f"output/{name}.html", 'w', encoding='utf-8') as f:
                    f.write(html)

def main():
    s = Scraper()
    while s.q:
        with Pool(8) as p:
            res = p.imap_unordered(s.scrap, s.q)
            for r in res:
                pass



if __name__ == '__main__':
    main()