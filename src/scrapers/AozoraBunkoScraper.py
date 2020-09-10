import requests
import os
from time import sleep

from . import AozoraBunkoAPI
from .utils import logger, _write_json, _shape_params

# 参考 : https://github.com/aozorahack/pubserver2
# 参考 : https://github.com/aozorahack/aozora-cli

class AozoraBunkoScraper:

    SLEEP_TIME = 5

    def __init__(self, save_dir, logger=logger(__name__)):
        self.aozorapi = AozoraBunkoAPI()
        self.logger = logger
        self.save_dir = save_dir
        self.gotton_books = []

    def get_thepersons_books(self,
        auther_name, maximum=100, save_n=10
        ) -> list:
        pass

    def get_ranking_books(self,
        maximum=500, save_n=50, year=2020, month=1
        ) -> list:

        ranking = self.aozorapi.get_ranking(year, month).json()
        ranking_books = []
        self.logger.info(f"got ranking : num {len(ranking)}")
        for i, book_info in enumerate(ranking):
            if i >= maximum:
                break

            book_data = {
                'id' : book_info["book_id"],
                'title' : book_info["title"],
                'authors' : book_info["authors"],
                'content' : self.aozorapi.get_booktxt(book_info["book_id"]).text
            }
            ranking_books.append(book_data)

            if i % save_n == 0:
                self.save()

            sleep(self.SLEEP_TIME)

        self.gotton_books.extend(ranking_books)
        self.logger.info(f"got {len(ranking_books)} books")
        return ranking_books

    def save(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        _write_json(
            os.path.join(self.save_dir, "books.json"),
            {"books":self.gotton_books}
        )
        self.logger.info(f"saved {self.save_dir}")