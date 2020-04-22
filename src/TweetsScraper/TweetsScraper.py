import os
import json

import twitter
from .utils import *

# 要素が増えてきたらクラスを分ける

class TweetsScraper:
    def __init__(self, consumer_key, consumer_secret,
                        access_token, access_secret,
                        save_dir=""):

        self.api = twitter.Api( consumer_key=consumer_key,
                                consumer_secret=consumer_secret,
                                access_token=access_token,
                                access_secret=access_secret)

        # {"id_str" : [{"user":"", "text":""}, ]}
        self.dialogues = {}

        # see add_tweets
        self.tweets = {}

        # チェックすべきユーザー
        self.user_queue = []

        self.save_dir = save_dir

    def load_data(self, load_dir):
        with open(os.path.join(self.save_dir, "tweets.json"), 'r', encoding='utf-8', errors='ignore') as f:
            self.tweets = json.load(f)

        with open(os.path.join(self.save_dir, "dialogues.json"), 'r', encoding='utf-8', errors='ignore') as f:
            self.dialogues = json.load(f)

    @staticmethod
    def shape_tweet(tweet):
        return {
            "id"        : tweet["id"],
            "text"      : tweet["text"],
            "user"      : tweet["user"]["id"],
            "reply_to"  : tweet.get("in_reply_to_status_id", 0)
        }

    def add_tweets(self, tweets_list):
        tweets = {t["id"] : self.shape_tweet(t) for t in tweets_list}
        self.tweets = {**self.tweets, **tweets}

    def add_dialogues(self, dialogue_list):
        dialogues = {d["id_str"] : d["dialogue"] for d in dialogue_list}
        self.dialogues = {**self.dialogues, **dialogues}
        remove_n = self.remove_same_dialogue()
        return len(dialogues) - remove_n

    def get_following(self):
        self.user_queue = self.api.GetFriends()

    def get_near_dialogue(self, dialogue_n=200):
        self.get_following()
        for user in self.user_queue:
            timeline = self.api.GetUserTimeline(user_id=user, count=200, exclude_replies=False)
            timeline = {self.shape_tweet(t) for t in timeline}

            reply_tweets = {t for t in timeline.values() if t.get("reply_to")}
            dialogue_n -= self.add_dialogues([self.pull_dialogue(t) for t in reply_tweets])

            # reply_tweets から 次に探索すべき ユーザーを取り出す
            [self.user_queue.append(t["user"]) for t in reply_tweets if t["user"] not in self.user_queue]

            if dialogue_n <= 0:
                break

    def pull_dialogue(self, start_tweet):
        # 1つのリプライから、1連の会話を取得
        dialogue = {"id_str":"", "dialogue":[]}

        tweet = start_tweet
        while tweet["reply_to"]:
            if(tweet["reply_to"] in self.tweets):
                tweet = self.tweets[tweet["reply_to"]]

            else:
                tweet = self.api.GetStatus(tweet["reply_to"])
                self.tweets[tweet["id"]] = self.shape_tweet(tweet)

            dialogue["id_str"] += str(tweet["id"])
            dialogue["dialogue"].append({"user":tweet["user"], "text":tweet["text"]})

        return dialogue

    def remove_same_dialogue(self):
        # 消した dialogue の数を返す
        dialogue_ids = [self.dialogues.keys()]
        dialogue_ids.sort()
        remove_n = 0
        for (i, dialogue_id) in enumerate(dialogue_ids):
            if any([d.find(dialogue_id) for d in dialogue_ids[i:]]):
                del self.dialogues[dialogue_id]
                remove_n += 1

        return remove_n

    def save(self):
        with open(os.path.join(self.save_dir, "tweets.json"), 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(self.tweets, f, indent=4)

        with open(os.path.join(self.save_dir, "dialogues.json"), 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(self.dialogues, f, indent=4)