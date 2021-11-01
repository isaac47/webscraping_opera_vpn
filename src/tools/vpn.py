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
        # This is only use in windows system
        options.add_argument("--start-minimized")
        # # This replace the --headless option. Use only in linux system. the init is set into the src/init file
        # display = Display(visible=0, size=(800, 600))
        # display.start()

        # Check the documentation to find the right combination of versions
        driver = webdriver.Chrome(OperaDriverManager(version="v.91.0.4472.77").install(), desired_capabilities=caps,
                                  options=options)

        # To use if using display
        driver.set_window_position(0, 0)
        driver.set_window_size(1024, 768)

        driver.set_page_load_timeout(30)  # set the max to 10s
        if active_vpn:
            driver = activate_vnp(driver)
    except Exception as err:
        print(str(err))
        nb_request = 0
        while nb_request < 5:
            LOGGER.info('Wait github aurotizaton')
            request_remaining = 'https://api.github.com/rate_limit'
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(request_remaining, headers=headers)
            response_json = response.json()
            nb_request = int(response_json['resources']['core']['remaining'])
            sleep(10)
        driver = init_driver()

    return driver


def activate_vnp(driver):
    """
    The activate sequence is: opera://settings/vpnWithDisclaimer + 3 esc + 2 tab + 1 Enter
    """
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
    try:
        driver.get(url)
        if popup_xpath is not None and new_driver:
            close_popup(driver, popup_xpath)
        driver = wait_for_ajax(driver)
        if new_tab:
            driver.execute_script('''window.open("{}","_blank");'''.format(url))
            sleep(3)
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            sleep(3)
            driver.switch_to.window(driver.window_handles[0])
            driver.refresh()
        if scroll:
            driver = selenium_scroll_down(driver, 5)

        if mouse_mov:
            driver = mouse_movements(driver, key_word=mouse_kw)
        driver.implicitly_wait(30)
        response = driver.page_source
        if error_403_text.lower() in response.lower():
            # close the browser and open a new one
            LOGGER.info('403 found!!')
            return None
        else:
            if apply_EC:
                # Element to check in other to confirm that the page is well open
                try:
                    element1 = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//meta[contains(@itemprop, 'reviewCount')]"))
                    )
                except:
                    LOGGER.warning("Element not show!")
            # Extract data
            return response
    except:
        LOGGER.info('error opening url')
        return None


def selenium_scroll_down(driver, SCROLL_PAUSE_TIME=1):
    """
    Perform page scroll down.

    Parameters
    ----------
    driver
        the driver
    SCROLL_PAUSE_TIME
        The time sleep for the scroll

    Returns
    -------

    """
    # Get scroll height
    total_height = int(driver.execute_script("return document.body.scrollHeight"))

    for i in range(1, total_height, 8):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(SCROLL_PAUSE_TIME)

    return driver


def mouse_movements(driver, key_word: str):
    """
    Perform mouse movements

    Parameters
    ----------
    driver
        The driver
    key_word
        the key word contain into the tag element to find. It will be the mouse starting point

    Returns
    -------

    """
    action = ActionChains(driver)
    startElement = driver.find_element_by_xpath("//*[contains(text(), '{}')]".format(key_word))
    mouse_positions = mouse_position_generator()

    # First, go to your start point or Element:
    action.move_to_element(startElement)
    action.perform()

    for mouse_x, mouse_y in mouse_positions:
        action.move_by_offset(mouse_x, mouse_y)
        action.perform()
    LOGGER.info("mouse movements done")
    return driver


def mouse_position_generator(number_of_position=10):
    """
    Simulate mouse movements positions

    Parameters
    ----------
    number_of_position
        Number of positions to simulate

    Returns
    -------
        List of tuple of x and y positions

    """
    # Curve base:
    points = [[0, 0], [0, 2], [2, 3], [4, 0], [6, 3], [8, 2], [8, 0]]
    points = np.array(points)

    x = points[:, 0]
    y = points[:, 1]

    t = range(len(points))
    ipl_t = np.linspace(0.0, len(points) - 1, 100)

    x_tup = si.splrep(t, x, k=3)
    y_tup = si.splrep(t, y, k=3)

    x_list = list(x_tup)
    xl = x.tolist()
    x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

    y_list = list(y_tup)
    yl = y.tolist()
    y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

    x_i = si.splev(ipl_t, x_list)  # x interpolate values
    y_i = si.splev(ipl_t, y_list)  # y interpolate values

    mouse_data = list(zip(x_i, y_i))
    mouse_positions = random.sample(mouse_data, number_of_position)

    return mouse_positions
