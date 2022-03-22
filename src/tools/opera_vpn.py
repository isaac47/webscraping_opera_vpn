import numpy as np
import random
import scipy.interpolate as si
from time import sleep

from webdriver_manager.opera import OperaDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from src.tools.logger import Logger
import requests

LOGGER = Logger("OPERA VPN").getLogger()


def init_driver(active_vpn=True):
    """
    Initialize the driver

    Parameters
    ----------
    active_vpn
            Active vpn or not

    Returns
    -------

    """
    # Add access to browser network panel data
    try:
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        options = webdriver.ChromeOptions()
        options.add_argument("--start-minimized")
        # This replace the --headless option
        # display = Display(visible=0, size=(800, 600))
        # display.start()

        driver = webdriver.Chrome(OperaDriverManager(version="v.98.0.4758.82").install(), desired_capabilities=caps,
                                  options=options)

        # To use if using display
        driver.set_window_position(0, 0)
        driver.set_window_size(1024, 768)

        driver.set_page_load_timeout(30)  # set the max to 10s
        if active_vpn:
            driver = activate_vnp(driver)
    except Exception as err:
        print(str(err))
        driver = init_driver()

    return driver


def activate_vnp(driver, location="meilleur emplacement"):
    """
    The activate sequence is: opera://settings/vpnWithDisclaimer + 3 esc + 2 tab + 1 Enter
    change location sequence is: new tab + 2 (up+tab) + 1 Enter + 3 tab + 1 Enter
    """
    location_action = {"meilleur emplacement": 1,
                       "europe": 2,
                       "asie": 3,
                       "amerique": 4}
    location_action_value = location_action[location]

    driver.get("opera://settings/vpnWithDisclaimer")
    sleep(3)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    sleep(1)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    sleep(1)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    sleep(1)

    webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
    sleep(1)
    webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
    sleep(1)

    webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
    sleep(2)

    # Set location
    if location_action_value != 1:
        driver.execute_script('''window.open("","_blank");''')
        driver.switch_to.window(driver.window_handles[-1])
        sleep(1)
        webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()

    return driver


def close_popup(driver, xpath):
    """This function helps to close the cookies popup page"""
    pop_up_close_button = driver.find_elements_by_xpath(xpath)
    if pop_up_close_button:
        try:
            pop_up_close_button[0].click()
            time.sleep(2)
        except:
            pass


def wait_for_ajax(driver):
    """This function implement the ajax loading of the page"""
    wait = WebDriverWait(driver, 60)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        pass
    return driver


def get_page_data(driver, url, error_403_text, new_tab=False, scroll=False, mouse_mov=False, mouse_kw: str = None,
                  apply_EC: bool = False, popup_xpath: str = None, new_driver: bool = True):
    """
    Get the page source response from selenium driver

    Parameters
    ----------
    driver
        The driver
    url
        The url to open
    error_403_text
        The error text found in the page when the error occur. It can be any text portion
    new_tab
        boolean to open new tab or not
    scroll
        boolean to open new tab or not
    mouse_mov
        boolean to apply mouse movement or not
    mouse_kw
        A word found in the element of the page. It will be the starting point for the mouse movement
    popup_xpath
        The xpath of the button using to close popup
    new_driver
        bool new driver or not
    apply_EC
        bool use to wait a particular element

    Returns
    -------

    """
    # try:
    driver.get(url)
    if popup_xpath is not None and new_driver:
        close_popup(driver, popup_xpath)
    driver = wait_for_ajax(driver)
    driver.execute_script('''window.open("{}","_blank");'''.format(url))
    driver.switch_to.window(driver.window_handles[1])
    sleep(30)
    # driver.implicitly_wait(30)
    response = driver.page_source
    if error_403_text.lower() in response.lower():
        # close the browser and open a new one
        LOGGER.info('403 found!!')
        return None
    else:
        if apply_EC:
            try:
                element1 = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//meta[contains(@itemprop, 'reviewCount')]"))
                )
            except:
                LOGGER.warning("Element not show!")
        # Extract data
        return response
