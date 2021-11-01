import json
import time
from typing import Union

from random import randrange
from bs4 import BeautifulSoup
from src.tools.logger import Logger

LOGGER = Logger("TOOLBOX").getLogger()

DEFAULT_TIMEOUT = 5  # seconds


def time_waiting(min_time=2, max_time=6):
    """
    The time to wait between to requests

    Parameters
    ----------
    min_time
        The min range of seconds
    max_time
        The max range of seconds

    Returns
    -------

    """
    wait = randrange(min_time, max_time)
    LOGGER.info('waiting for {} seconds'.format(wait))
    time.sleep(wait)


def bs4_soup(response_content: Union[str, bytes]) -> BeautifulSoup:
    """
    Try different soup parser

    Parameters
    ----------
    response_content:
        The response content

    Returns
    -------
        The soup object
    """
    try:
        soup = BeautifulSoup(response_content, "lxml")
        return soup
    except:
        try:
            soup = BeautifulSoup(response_content, "html.parser")
            return soup
        except:
            try:
                soup = BeautifulSoup(response_content, "html5lib")
                return soup
            except:
                LOGGER.info("Error soup the page")


def get_application_data(soup, key='@type', value='ItemList'):
    doms = soup.find_all("script", {"type": "application/ld+json"})
    for dom in doms:
        try:
            if json.loads("".join(dom.contents), strict=False)[key] == value:
                return json.loads("".join(dom.contents), strict=False)
        except:
            try:
                if json.loads("".join(dom.contents))[key] == value:
                    return json.loads("".join(dom.contents))
            except:
                pass