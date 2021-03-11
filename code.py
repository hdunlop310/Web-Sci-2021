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


def part_one():
    retweets = 0
    quote_tweets = 0
    for x in db.coltest.find({}, {'text': 1}):
        if x['text'][0:2] == 'rt':
            retweets += 1

        if x['text'][0] == "'":
            quote_tweets += 1

    print(db.March7th.count_documents({}))
    print("quote tweets = " + str(quote_tweets))
    print("retweets = " + str(count_rt))


def process_tweets(tweet):
    global count_rt
    count_rt = 0

    global count_tweets
    count_tweets = 0

    # Pull important data from the tweet to store in the database.
    try:
        created = tweet['created_at']  # The time tweet was created
        tweet_id = tweet['id_str']  # The Tweet ID from Twitter in string format
        username = tweet['user']['screen_name']  # The username of the Tweet author
        text = tweet['text']  # The entire body of the Tweet
        retweets = tweet['retweet_count']
        quote = tweet['quote_count']

    except Exception as e:
        # if this happens, there is something wrong with JSON, so ignore this tweet
        return None

    text = clean_list(text)
    geo_enabled = tweet['user']['geo_enabled']
    location = tweet['user']['location']

    if geo_enabled:
        try:

            if tweet['place']['country'] == 'United Kingdom':
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_country_code = tweet['place']['country_code']
                place_coordinates = tweet['place']['bounding_box']['coordinates']

                if text.startswith('RT'):
                    count_rt += 1

                tweet1 = {'created_at': created, '_id': tweet_id, 'username': username, 'text': text,
                          'geoenabled': geo_enabled,
                          'coordinates': place_coordinates, 'location': location, 'place_name': place_name,
                          'place_country': place_country, 'country_code': place_country_code,
                          'retweets': retweets, 'quote tweets': quote}

                tweet1['text'] = clean_list(tweet1['text'])
                tweet1['text'] = strip_emoji(tweet1['text'])

                count_tweets += 1

                return tweet1

        except Exception as e:
            return None


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
        streamer.filter(track=read_keywords())


class APIStreamListener(StreamListener):
    """
    Basic listener class
    """

    def __init__(self, time_limit=1200):
        self.start_time = time.time()
        self.limit = time_limit
        super(StreamListener, self).__init__()

    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_data(self, raw_data):
        global client
        client = MongoClient('127.0.0.1', 27017)
        global db_name
        db_name = "TwitterDump"  # set-up a MongoDatabase
        global db
        db = client[db_name]
        global coll_name
        coll_name = 'March11th'  # here we create a collection
        global collection
        collection = db[coll_name]

        if (time.time() - self.start_time) < self.limit:
            t = json.loads(raw_data)
            t = process_tweets(t)
            try:
                if t is None:
                    return True
                print(t['created_at'])
                print(t['text'])
                collection.insert_one(t)

            except Exception as e:
                return True

        else:
            return False

    def on_error(self, status_code):
        print(status_code)


def rest_api():
    auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    user = api.get_user(screen_name='theresa_may')
    print(user.id)


if __name__ == '__main__':
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets()

    #part_one()
    # print(count_tweets)
    # print(count_rt)

    #rest_api()




