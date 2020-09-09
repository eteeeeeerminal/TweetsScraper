import os
import requests
from time import sleep

from bs4 import BeautifulSoup

from .utils import logger, _write_json

# 参考 : https://github.com/derodero24/Deropy/blob/master/google.py

class Google:

    SEARCH_URL = 'https://www.google.co.jp/search'
    SLEEP_TIME = 1

    def __init__(self, logger=logger(__name__)):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                "Mozilla/5.0 (X11; Linux x86_64; rv:57.0)"
                "Gecko/20100101 Firefox/57.0"
            )
        })
        self.logger = logger
        self.gotten_links = []

    def search(self, keyword,
        muximum_pagenum=10, linknum_per_page=100,
        ):
        if muximum_pagenum <= 0 or linknum_per_page <= 0:
            return

        self.logger.info(f"start google search : {keyword}")
        result = {"keyword":keyword, "gotten_links":[]}
        for page in range(muximum_pagenum):
            params = {
                'q' : keyword,
                'num' : linknum_per_page,
                'filter' : 0,
                'start' : page * linknum_per_page
            }
            response = self.session.get(self.SEARCH_URL, params=params)
            if response.status_code != requests.codes.ok:
                self.logger.warn(f"got status code {response.status_code}")
                break

            links = self.get_links(response.text)

            if not len(links):
                self.logger.info("got all links")
                break

            result["gotten_links"].extend(links)
            sleep(self.SLEEP_TIME)

        self.gotten_links.append(result)
        total = len(result["gotten_links"])
        self.logger.info(f"got {total} links")
        return result

    def get_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.select('.rc > .r > a')
        return [e['href'] for e in elements]

    def save(self, save_dir):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        _write_json(
            os.path.join(save_dir, "search_result.json"),
            {"result":self.gotten_links}
            )
        self.logger.info(f"saved {save_dir}")