import sys
import os
from os.path import join, dirname
from dotenv import load_dotenv

sys.path.append("../src")
from scrapers import TweetsScraper

# キーを取得
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

i = 1
while os.path.exists(save_dir:=f"tweets_data{i}"):
    i += 1

api = TweetsScraper(    consumer_key=os.environ.get("CONSUMER_KEY"),
                        consumer_secret=os.environ.get("CONSUMER_SECRET"),
                        access_token_key=os.environ.get("ACCESS_TOKEN_KEY"),
                        access_token_secret=os.environ.get("ACCESS_TOKEN_SECRET"),
                        save_dir=save_dir
                        )

api.search_tweets("python", maximum=15)
api.save()