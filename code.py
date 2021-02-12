from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
from pymongo import MongoClient
import credentials

'''
Code Not Needed Right Now

def get_location():
    return [-10.392627, 49.681847, 1.055039, 61.122019]  # coords for uk and ireland
    
def db_setup():
    client = MongoClient('127.0.0.1', 27017)  # is assigned local port
    dbName = "TwitterDump"  # set-up a MongoDatabase
    db = client[dbName]
    collName = 'colTest'  # here we create a collection
    collection = db[collName]  # This is for the Collection  put in the DB
'''


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
        print(raw_data)
        return True

    def on_error(self, status_code):
        print(status_code)


def main():
    keywords = read_keywords()
    print(keywords)


if __name__ == '__main__':
    listener = APIStreamListener()
    auth = authorise()
    stream = Stream(auth, listener)
    stream.filter(track=read_keywords())
