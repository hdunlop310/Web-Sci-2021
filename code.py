import json

import emoji
import tweepy
from pymongo import MongoClient
from tweepy import Stream
from tweepy.streaming import StreamListener
import re
import credentials
import time


def get_location():
    return [-10.392627, 49.681847, 1.055039, 61.122019]  # coords for uk and ireland


def read_keywords():
    with open('keywords.txt', 'r') as f:
        keywords = f.readlines()
    return keywords


def authorise():
    auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    if not api:
        print('Cannot authenticate')
        print('failed consumer id ----------: ', credentials.CONSUMER_KEY)
    return auth


class TwitterStreamer:
    """
    Class for streaming & processing live tweets
    """

    def stream_tweets(self):
        listener = APIStreamListener()
        streamer = tweepy.Stream(auth=authorise(), listener=listener)
        print("Tracking: " + str(read_keywords()))
        streamer.filter(track=read_keywords())


class APIStreamListener(StreamListener):
    """
    Basic listener class
    """

    def __init__(self, time_limit=5):
        self.start_time = time.time()
        self.limit = time_limit
        super(StreamListener, self).__init__()

    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_data(self, raw_data):
        try:
            client = MongoClient('127.0.0.1', 27017)
            db_name = "TwitterDump"  # set-up a MongoDatabase
            db = client[db_name]
            coll_name = 'colTest2'  # here we create a collection
            collection = db[coll_name]

            t = json.loads(raw_data)
            created_at = t['created_at']
            print("Tweet collected at " + str(created_at))
            collection.insert_one(t)
        except Exception as e:
            print(e)
        return True

    def on_error(self, status_code):
        print(status_code)


if __name__ == '__main__':
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets()
