import os
import requests
from string import digits, ascii_lowercase
from time import sleep

from bs4 import BeautifulSoup

from .utils import logger, _write_json

# 参考 : https://github.com/derodero24/Deropy/blob/master/google.py

class GoogleSearch:

    SEARCH_URL = 'https://www.google.co.jp/search'
    SUGGEST_URL = 'http://www.google.co.jp/complete/search'
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
        self.gotten_data = []

    def search(self, keyword,
        maximum=10, linknum_per_page=50,
        ) -> dict:
        if maximum <= 0 or linknum_per_page <= 0:
            return

        self.logger.info(f"start google search : {keyword}")
        total = 0
        result = {"keyword":keyword, "gotten_links":[]}
        for page in range(maximum):
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
            elif len(links) > maximum - total:
                result["gotten_links"].extend(links[:maximum - total])
                break

            total += len(links)
            result["gotten_links"].extend(links)
            sleep(self.SLEEP_TIME)

        self.gotten_data.append(result)
        total = len(result["gotten_links"])
        self.logger.info(f"got {total} links")
        return result

    def suggest(self, keyword, jpn=False, alph=False, num=False) -> dict:
        # 検索ワード + 1文字
        chars = ['', ' ']
        chars += [' ' + chr(i) for i in range(12353, 12436)] if jpn else []
        chars += [' ' + c for c in ascii_lowercase] if alph else []
        chars += [' ' + c for c in digits] if num else []

        self.logger.info(f"start get google suggests : {keyword}")
        result = {"keyword":keyword, "suggested_words":[]}
        for c in chars:
            params= {
                'output':'toolbar',
                'ie':'utf-8', 'oe':'utf-8',
                'client':'firefox',
                'q':keyword+c
            }
            self.logger.info(f"suggest:{keyword+c}")
            response = self.session.get(self.SUGGEST_URL, params=params)
            if response.status_code != requests.codes.ok:
                self.logger.warn(f"got status code {response.status_code}")
                break
            result["suggested_words"] += response.json()[1]
            sleep(self.SLEEP_TIME)

        total = len(result["suggested_words"])
        self.gotten_data.append(result)
        self.logger.info(f"got {total} words")
        return result

    def get_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.select('.rc > .r > a')
        return [e['href'] for e in elements]

    def save(self, save_dir):
        os.makedirs(save_dir, exist_ok=True)

        _write_json(
            os.path.join(save_dir, "search_result.json"),
            {"result":self.gotten_data}
            )
        self.logger.info(f"saved {save_dir}")