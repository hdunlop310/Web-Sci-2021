import json

import tweepy
from pymongo import MongoClient
from tweepy import Stream
from tweepy.streaming import StreamListener

import credentials
from streamCrawler import cleanList

'''
Code Not Needed Right Now

def get_location():
    return [-10.392627, 49.681847, 1.055039, 61.122019]  # coords for uk and ireland
'''

client = MongoClient('127.0.0.1', 27017)  # is assigned local port
dbName = "TwitterDump"  # set-up a MongoDatabase
db = client[dbName]
collName = 'colTest'  # here we create a collection
collection = db[collName]  # This is for the Collection  put in the DB


def read_keywords():
    keywords = []
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


class APIStreamListener(StreamListener):

    def on_data(self, raw_data):
        #t = json.loads(raw_data)
        #tweet = process_tweets(t)
        #try:
            #collection.insert_one(tweet)
        #except Exception as e:
            #print(e)
        print(raw_data)
        return True

    def on_error(self, status_code):
        print(status_code)


def main():
    keywords = read_keywords()
    print(keywords)


if __name__ == '__main__':
    print('hello')
    listener = APIStreamListener()
    auth = authorise()
    # db_setup()
    stream = Stream(auth, listener)
    stream.filter(track=read_keywords())
