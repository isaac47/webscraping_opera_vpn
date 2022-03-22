from src.tools.logger import Logger
from src.tools.utils import bs4_soup
from src.tools.opera_vpn import init_driver, get_page_data
import time
import re
from src.tools.utils import time_waiting


driver = None

LOGGER = Logger("TEST SCRAPER").getLogger()


def apply_scraping(urls):
    LOGGER.info("Start scrapping urls")
    global driver
    driver = init_driver()
    for url in urls:
        LOGGER.info("start scraping url: {}".format(url))
        try_again = True
        while try_again:
            time_waiting()
            # We can set the part of the page text to detect in other to consider the page open is 403
            response = get_page_data(driver=driver, url=url, error_403_text="Access Denied", new_tab=True)
            if response is not None and bs4_soup(response).find_all('div'):
                try_again = False
            else:
                LOGGER.info("Try again to open the page..")
                driver.quit()
                time.sleep(3)
                LOGGER.info("launch a new driver..")
                driver = init_driver()
                try_again = True

        soup_page = bs4_soup(response)
        articles = soup_page.find_all('article', {'class': '_1MR-U _2bDr_'})
        print(articles)
        LOGGER.info(f"Number of articles found: {len(articles)}")
        for article in articles:
            #if article.find('span', {'class': '_1uDOY'}):
            print("Article url: {}".format(article.find('a', {'class': 'Wz9wg'}).attrs['href']))
            print("Article number reviews: {}".format(int(re.findall(
                r'[0-9]+', article.find('span', {'class': 'wQ2tY'}).text)[0])))
            print("-----------------------------------------")

    LOGGER.info("End scraping..")
