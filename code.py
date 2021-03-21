import json

import emoji
import tweepy
from pymongo import MongoClient
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
    #  this module is for cleaning text and also extracting relevant twitter feilds
    # initialise placeholders
    place_countrycode = None
    place_name = None
    place_country = None
    place_coordinates = None
    source = None
    exactcoord = None
    place = None

    global count_rt
    count_rt = 0

    global count_tweets
    count_tweets = 0

    # print(t)

    # Pull important data from the tweet to store in the database.
    try:
        created = tweet['created_at']
        tweet_id = tweet['id_str']  # The Tweet ID from Twitter in string format
        username = tweet['user']['screen_name']  # The username of the Tweet author
        # followers = t['user']['followers_count']  # The number of followers the Tweet author has
        text = tweet['text']  # The entire body of the Tweet
        verified = tweet['user']['verified']
        media = tweet['entities']['urls']
    except Exception as e:
        # if this happens, there is something wrong with JSON, so ignore this tweet
        print(e)
        return None

    try:
        # // deal with truncated
        if (tweet['truncated'] == True):
            text = tweet['extended_tweet']['full_text']
        elif (text.startswith('RT') == True):
            # print(' tweet starts with RT **********')
            # print(text)

            try:
                if (tweet['retweeted_status']['truncated'] == True):
                    # print("in .... tweet.retweeted_status.truncated == True ")
                    text = tweet['retweeted_status']['extended_tweet']['full_text']
                    # print(text)
                else:
                    text = tweet['retweeted_status']['full_text']

            except Exception as e:
                pass

    except Exception as e:
        print(e)
    # print(text)
    text = clean_list(text)
    # print(text)
    entities = tweet['entities']
    # print(entities)
    mentions = entities['user_mentions']
    mList = []

    for x in mentions:
        # print(x['screen_name'])
        mList.append(x['screen_name'])
    hashtags = entities['hashtags']  # Any hashtags used in the Tweet
    hList = []
    for x in hashtags:
        # print(x['screen_name'])
        hList.append(x['text'])
    # if hashtags == []:
    #     hashtags =''
    # else:
    #     hashtags = str(hashtags).strip('[]')
    source = tweet['source']

    exactcoord = tweet['coordinates']
    coordinates = None
    if (exactcoord):
        # print(exactcoord)
        coordinates = exactcoord['coordinates']
        # print(coordinates)
    geoenabled = tweet['user']['geo_enabled']
    location = tweet['user']['location']

    if ((geoenabled) and (text.startswith('RT') == False)):
        # print(tweet)
        # sys.exit() # (tweet['geo']):
        try:
            if (tweet['place']):
                # print(tweet['place'])
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_countrycode = tweet['place']['country_code']
                place_coordinates = tweet['place']['bounding_box']['coordinates']
        except Exception as e:
            print(e)
            print(
                'error from place details - maybe AttributeError: ... NoneType ... object has no attribute ..full_name ...')

    tweet1 = {'_id': tweet_id, 'date': created, 'username': username, 'text': text, 'geoenabled': geoenabled,
              'coordinates': coordinates, 'location': location, 'place_name': place_name,
              'place_country': place_country, 'country_code': place_countrycode, 'place_coordinates': place_coordinates,
              'hashtags': hList, 'mentions': mList, 'source': source, 'verified': verified, 'media': media}

    return tweet1


def clean_list(text):
    text = strip_emoji(text)
    text.encode("ascii", errors="ignore").decode()

    return text


def strip_emoji(text):
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
        streamer.filter(locations=[-10.392627, 49.681847, 1.055039, 61.122019], track=read_keywords(), languages=['en'])


class APIStreamListener(StreamListener):
    """
    Basic listener class
    """

    def __init__(self, time_limit=7200):
        self.start_time = time.time()
        self.limit = time_limit
        super(StreamListener, self).__init__()

    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_data(self, raw_data):
        client = MongoClient('127.0.0.1', 27017)
        db_name = "TwitterDump"  # set-up a MongoDatabase
        db = client[db_name]
        coll_name = 'March21New'  # here we create a collection
        collection = db[coll_name]

        if (time.time() - self.start_time) < self.limit:
            t = json.loads(raw_data)
            t = process_tweets(t)
            try:
                if t is None:
                    return True
                print(t)
                collection.insert_one(t)

            except Exception as e:
                return True

        else:
            return False

    def on_error(self, status_code):
        print(status_code)


if __name__ == '__main__':
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets()




