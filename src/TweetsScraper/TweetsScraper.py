import os
import json
import logging
import codecs
from time import sleep

import twitter
from twitter import TwitterError

# 要素が増えてきたらクラスを分ける

class TweetsScraper:
    def __init__(self, consumer_key, consumer_secret,
                        access_token_key, access_token_secret,
                        save_dir="",
                        logger=logging.getLogger(__name__)):

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.propagate = False

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

        self.logger.info("init TweetsScraper")

    def ouath(self):
        self.api = twitter.Api( consumer_key=self.consumer_key,
                                consumer_secret=self.consumer_secret,
                                access_token_key=self.access_token_key,
                                access_token_secret=self.access_token_secret,
                                sleep_on_rate_limit=True)


    def load_data(self, load_dir):
        with open(os.path.join(self.save_dir, "tweets.json"), 'r', encoding='utf-8', errors='ignore') as f:
            self.tweets = json.load(f)

        with open(os.path.join(self.save_dir, "dialogues.json"), 'r', encoding='utf-8', errors='ignore') as f:
            self.dialogues = json.load(f)

    @staticmethod
    def shape_tweet(tweet):
        # Status から dict へ変換
        return {
            "id"        : tweet.id,
            "text"      : tweet.text,
            "user"      : tweet.user.id,
            "reply_to"  : tweet.in_reply_to_status_id,
            "reply_to_user" : tweet.in_reply_to_user_id,
        }

    def add_tweets(self, tweets_list):
        tweets = {str(t["id"]) : t for t in tweets_list}
        self.tweets.update(tweets)
        return len(tweets)

    def add_dialogue(self, dialogue):
        self.dialogues[dialogue["id_str"]] = dialogue["dialogue"]
        remove_n = self.remove_same_dialogue()
        return 1 - remove_n

    def get_following(self):
        self.user_queue = self.api.GetFriends()
        self.user_queue = [u.id for u in self.user_queue]
        return len(self.user_queue)

    def get_near_dialogue(self, user_n=50, dialogue_n=200):
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
            add_user_n = len([self.user_queue.append(t["reply_to_user"]) for t in reply_tweets if t["reply_to_user"] not in self.user_queue])
            self.logger.info(f"add {add_user_n} users")

            if i >= user_n:
                break

            sleep(1)

        self.logger.info(f"get user_queue : {i} users")
        self.logger.info(f"get {len(self.tweets)} tweets")
        self.logger.info(f"start making dialogue data")

        for i, tweet in enumerate(list(self.tweets.values())):
            if not tweet["reply_to"]:
                continue

            if not(d := self.pull_dialogue(tweet)):
                continue

            dialogue_n -= self.add_dialogue(d)
            if dialogue_n <= 0:
                break

            if i % 1000 == 0:
                self.save()

    def pull_dialogue(self, start_tweet):
        # 1つのリプライから、1連の会話を取得
        dialogue = {"id_str":"", "dialogue":[]}

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

            dialogue["id_str"] += str(tweet["id"])
            dialogue["dialogue"].append({"user":tweet["user"], "text":tweet["text"]})

        if len(dialogue["dialogue"]) < 2:
            return None

        dialogue["dialogue"].reverse()
        return dialogue

    def remove_same_dialogue(self):
        # 消した dialogue の数を返す
        dialogue_ids = [self.dialogues.keys()]
        dialogue_ids.sort()
        remove_n = 0
        for (i, dialogue_id) in enumerate(dialogue_ids):
            if any([str(d).find(str(dialogue_id)) for d in dialogue_ids[i:]]):
                del self.dialogues[dialogue_id]
                remove_n += 1

        return remove_n

    def save(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        with codecs.open(os.path.join(self.save_dir, "tweets.json"), 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(self.tweets, f, indent=4, ensure_ascii=False)

        with open(os.path.join(self.save_dir, "dialogues.json"), 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(self.dialogues, f, indent=4, ensure_ascii=False)