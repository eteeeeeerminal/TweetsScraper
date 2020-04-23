import sys
import os
from os.path import join, dirname
from dotenv import load_dotenv

sys.path.append("../src/TweetsScraper/")
from TweetsScraper import TweetsScraper

# キーを取得
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

api = TweetsScraper(    consumer_key=os.environ.get("CONSUMER_KEY"),
                        consumer_secret=os.environ.get("CONSUMER_SECRET"),
                        access_token_key=os.environ.get("ACCESS_TOKEN_KEY"),
                        access_token_secret=os.environ.get("ACCESS_TOKEN_SECRET"),
                        save_dir="tweets_data1"
                        )

api.get_near_dialogue(user_n=5, dialogue_n=50)
api.save()