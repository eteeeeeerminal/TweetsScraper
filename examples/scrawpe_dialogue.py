import os
from os.path import join, dirname
from dotenv import load_dotenv
import TweetsScraper

# キーを取得
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CNS_KEY = os.environ.get("CONSUMER_KEY")
CNS_SEC = os.environ.get("CONSUMER_SECRET")
TOKEN_KEY = os.environ.get("ACCESS_TOKEN_KEY")
TOKEN_SEC = os.environ.get("ACCESS_TOKEN_SECRET")