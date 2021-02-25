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


def process_tweets(tweet):
    # Pull important data from the tweet to store in the database.
    place_country_code = None
    place_name = None
    place_country = None
    place_coordinates = None

    try:
        created = tweet['created_at'] # The time tweet was created
        tweet_id = tweet['id_str']  # The Tweet ID from Twitter in string format
        username = tweet['user']['screen_name']  # The username of the Tweet author
        text = tweet['text']  # The entire body of the Tweet
        retweets = tweet['retweet_count']
        quote = tweet['quote_count']
    except Exception as e:
        # if this happens, there is something wrong with JSON, so ignore this tweet
        print(e)
        return None

    try:
        if tweet['truncated']:
            text = tweet['extended_tweet']['full_text']
        elif text.startswith('RT'):
            try:
                if tweet['retweeted_status']['truncated']:
                    # print("in .... tweet.retweeted_status.truncated == True ")
                    text = tweet['retweeted_status']['extended_tweet']['full_text']
                    # print(text)
                else:
                    text = tweet['retweeted_status']['full_text']

            except Exception as e:
                pass

    except Exception as e:
        print(e)

    text = clean_list(text)
    entities = tweet['entities']
    mentions = entities['user_mentions']
    mList = []

    for x in mentions:
        # print(x['screen_name'])
        mList.append(x['screen_name'])
    hashtags = entities['hashtags']  # Any hashtags used in the Tweet
    hList = []
    for x in hashtags:
        hList.append(x['text'])

    exactcoord = tweet['coordinates']
    coordinates = None
    if (exactcoord):
        # print(exactcoord)
        coordinates = exactcoord['coordinates']
        # print(coordinates)
    geoenabled = tweet['user']['geo_enabled']
    location = tweet['user']['location']

    if (geoenabled) and not (text.startswith('RT')):
        # print(tweet)
        # sys.exit() # (tweet['geo']):
        try:
            if tweet['place']:
                # print(tweet['place']
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_country_code = tweet['place']['country_code']
                place_coordinates = tweet['place']['bounding_box']['coordinates']
        except Exception as e:
            print(e)
            print(
                'error from place details - maybe AttributeError: ... NoneType ... object has no attribute '
                '..full_name ...')

    tweet1 = {'created_at': created, '_id': tweet_id, 'username': username, 'text': text, 'geoenabled': geoenabled,
              'coordinates': coordinates, 'location': location, 'place_name': place_name,
              'place_country': place_country, 'country_code': place_country_code,
              'place_coordinates': place_coordinates, 'retweets': retweets, 'quote tweets': quote}

    return tweet1


def clean_list(text):
    #  copied from web - don't remeber the actual link
    # remove emoji it works
    text = strip_emoji(text)
    text.encode("ascii", errors="ignore").decode()

    return text


def strip_emoji(text):
    #  copied from web - don't remeber the actual link
    new_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    return new_text


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
            t = process_tweets(t)
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
