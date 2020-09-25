import os
import requests
from time import sleep
from typing import Union

from bs4 import BeautifulSoup

from .NarouAPI import narou_get
from .utils import get_logger, _write_json

class NarouScraper:

    NOVEL_URL = "https://ncode.syosetu.com"
    SLEEP_TIME = 5

    def __init__(self, save_dir, logger=get_logger(__name__)):
        self.make_session()
        self.save_dir = save_dir
        self.logger = logger
        self.gotten_books = {}

    def make_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                "Mozilla/5.0 (X11; Linux x86_64; rv:57.0)"
                "Gecko/20100101 Firefox/57.0"
            )
        })

    def get_books_thegenre(self, genre, novel_n=50, parts_per_novel=10, save_n=50):
        lim = min(novel_n, 100)
        total = 0
        self.logger.info("start getting novel list")
        while novel_n > total:
            book_datas = narou_get("t-n-u-w-ga", lim, total, genre=genre)
            if (n := len(book_datas)) <= 0:
                break

            total += n
            self.gotten_books.update({
                d.get('ncode'): d
                for d in book_datas
            })
            sleep(self.SLEEP_TIME)
        self.logger.info("got novel list")
        self.download_novels(save_n, parts_per_novel)

    def get_novel(self, ncode:str, n:Union[str, int]) -> Union[str, None]:
        url = f"{self.NOVEL_URL}/{ncode}/{n}"
        try:
            response = self.session.get(url)
            if response.status_code != requests.codes.ok:
                self.logger.warn(f"got status code {response.status_code}")
                return None

        except requests.exceptions.ConnectionError:
            self.logger.error(f"connection error, restart session")
            sleep(self.SLEEP_TIME)
            self.make_session()
            response = self.session.get(url)

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        return soup.select_one("#novel_honbun").text


    def download_novels(self, save_n, parts_per_novel):
        self.logger.info("start download novels")
        gotten_parts_n = 0
        for ncode, ndata in self.gotten_books.items():
            if ncode is None:
                continue
            self.logger.info(f"start downloading {ndata.get('title')}")
            story_n = ndata.get('general_all_no', 1)
            bodies = []
            for n in range(1, story_n+1):
                if n > parts_per_novel:
                    self.logger.info("over parts_n break")
                    break
                text = self.get_novel(ncode, n)
                if text is None:
                    break

                bodies.append(text)
                gotten_parts_n += 1
                if gotten_parts_n % save_n == 0:
                    self.save()
                sleep(self.SLEEP_TIME)

            self.gotten_books[ncode]['content'] = bodies
            gotten_n = min(parts_per_novel,story_n+1)
            self.logger.info(
                f"got {gotten_n}(out_of {story_n+1}) parts of novel {ndata.get('title')}"
                )
            sleep(self.SLEEP_TIME*4)

    def save(self):
        os.makedirs(self.save_dir, exist_ok=True)

        _write_json(
            os.path.join(self.save_dir, "books.json"),
            self.gotten_books
        )
        self.logger.info(f"saved {self.save_dir}")