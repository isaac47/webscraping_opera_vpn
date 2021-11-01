from src.tools.logger import Logger
from src.tools.utils import bs4_soup, get_application_data
from src.tools.vpn import init_driver, get_page_data
import time
from src.tools.utils import time_waiting
import pymongo

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
            response = get_page_data(driver, url, "Access Denied")
            if response is not None:
                try_again = False
            else:
                LOGGER.info("Try again to open the page..")
                driver.quit()
                time.sleep(3)
                LOGGER.info("launch a new driver..")
                driver = init_driver()
                try_again = True

        soup_page = bs4_soup(response)
        LOGGER.info(f"Extract data from {url}")
        data = get_application_data(soup_page, key='@type', value='ItemList')
        LOGGER.info(f"storing data from {url}: {len(data)} data found!")
        # storing function
        mongodb_instance = pymongo.MongoClient("")
        mongodb_db = mongodb_instance['test_db']
        mongodb_db['store_data'].insert_many(data)

    LOGGER.info("End scraping..")
