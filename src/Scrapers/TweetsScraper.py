import os
import json
import re
import codecs
import random
import logging
from functools import partial
from time import sleep

import twitter
from twitter import TwitterError

from .utils import logger, _read_json, _write_json

class TweetsScraper:
    def __init__(self, consumer_key, consumer_secret,
                        access_token_key, access_token_secret,
                        save_dir="",
                        logger=logger(__name__)):

        self.logger = logger
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.ouath()

        # {"id_str" : [{"user":"", "text":""}, ]}
        self.dialogues = {}

        # see add_tweets
        self.tweets = {}

        # チェックすべきユーザー
        self.user_queue = []

        self.save_dir = save_dir

        self.sources = ["TweetDeck", "Twitter Web Client", "Twitter Web App", "Twitter for iPhone",
               "Twitter for iPad", "Twitter for Android", "Twitter for Android Tablets",
               "ついっぷる", "Janetter", "twicca", "Keitai Web", "Twitter for Mac", "YoruFukurou"]
        self.tag_pattern = re.compile(r"<.*?>")

        self.join_save_dir = partial(os.path.join, self.save_dir)

        self.logger.info("init TweetsScraper")

    def ouath(self):
        self.api = twitter.Api( consumer_key=self.consumer_key,
                                consumer_secret=self.consumer_secret,
                                access_token_key=self.access_token_key,
                                access_token_secret=self.access_token_secret,
                                sleep_on_rate_limit=True)


    def load_data(self, load_dir):
        self.tweets = _read_json(self.join_save_dir("tweets.json"))
        self.dialogues = _read_json(self.join_save_dir("dialogues.json"))

    def shape_tweet(self, tweet):
        # Status から dict へ変換
        return {
            "id"        : tweet.id,
            "text"      : tweet.text,
            "user"      : tweet.user.id,
            "source"    : self.tag_pattern.sub("", str(tweet.source)),
            "reply_to"  : tweet.in_reply_to_status_id,
            "reply_to_user" : tweet.in_reply_to_user_id,
        }

    def add_tweets(self, tweets_list):
        tweets = {str(t["id"]) : t for t in tweets_list}
        self.tweets.update(tweets)
        return len(tweets)

    def add_dialogue(self, dialogue):
        self.dialogues[dialogue["id_str"]] = dialogue["dialogue"]
        return 1

    def get_following(self):
        self.user_queue = self.api.GetFriends()
        self.user_queue = [u.id for u in self.user_queue]
        return len(self.user_queue)

    def get_near_dialogue(self, user_n=50, dialogue_n=200, save_n=1000):
        self.get_following()
        self.logger.info(f"get : {len(self.user_queue)} users")
        self.logger.info(f"start get timeline")
        for i, user in enumerate(self.user_queue):
            try:
                timeline = self.api.GetUserTimeline(user_id=user, count=200, exclude_replies=False)
            except TwitterError as e:
                    self.logger.info(e.args[0])
                    if 'limit' not in e.args:
                        continue

                    self.logger.info("wait about 15m")
                    timeline = self.api.GetUserTimeline(user_id=user, count=200, exclude_replies=False)

            self.logger.info(f"get user {i}")

            timeline = [self.shape_tweet(t) for t in timeline]
            self.add_tweets(timeline)

            reply_tweets = [t for t in timeline if t.get("reply_to")]
            # reply_tweets から 次に探索すべき ユーザーを取り出す
            add_user_n = len([
                self.user_queue.append(t["reply_to_user"])
                    for t in reply_tweets
                    if t["reply_to_user"] not in self.user_queue
            ])
            self.logger.info(f"add {add_user_n} users")

            if i >= user_n:
                break

            sleep(1)

        self.logger.info(f"get user_queue : {i} users")
        self.logger.info(f"get {len(self.tweets)} tweets")
        self.logger.info(f"start making dialogue data")

        tweets = list(self.tweets.values())
        random.shuffle(tweets)
        for i, tweet in enumerate(tweets):
            if not tweet["reply_to"]:
                continue

            if tweet["source"] not in self.sources:
                self.logger.info(f"skip a tweet from : {tweet['source']}")
                continue

            if not(d := self.pull_dialogue(tweet)):
                continue

            dialogue_n -= self.add_dialogue(d)
            if dialogue_n <= 0:
                break

            if i % save_n == 0:
                self.save()

    def pull_dialogue(self, start_tweet):
        # 1つのリプライから、1連の会話を取得
        dialogue = {"id_str":[], "dialogue":[]}

        tweet = start_tweet
        while tweet["reply_to"]:
            if(tweet["reply_to"] in self.tweets):
                tweet = self.tweets[tweet["reply_to"]]

            else:
                try:
                    tweet = self.api.GetStatus(tweet["reply_to"])
                except TwitterError as e:
                    self.logger.info(e.args[0][0])
                    if e.args[0][0]["code"] != 88:
                        return None

                    self.logger.info("wait about 15m")
                    tweet = self.api.GetStatus(tweet["reply_to"])

                tweet = self.shape_tweet(tweet)
                self.tweets[tweet["id"]] = tweet
                sleep(1)

            dialogue["id_str"].append(str(tweet["id"]))
            dialogue["dialogue"].append({"user":tweet["user"], "text":tweet["text"]})

        if len(dialogue["dialogue"]) < 2:
            return None

        dialogue["id_str"] = ''.join(reversed(dialogue["id_str"]))
        dialogue["dialogue"].reverse()
        return dialogue

    def save(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        _write_json(self.join_save_dir("tweets.json"), self.tweets)
        _write_json(self.join_save_dir("dialogues.json"), self.dialogues)

        self.logger.info(f"saved {self.save_dir}")