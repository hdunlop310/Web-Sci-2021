import json

import emoji
import tweepy
from pymongo import MongoClient
from tweepy.streaming import StreamListener
import re
import credentials
import datetime, time


def get_location():
    return [-10.392627, 49.681847, 1.055039, 61.122019]  # coords for uk and ireland


def read_keywords():
    with open('keywords.txt', 'r') as f:
        keywords = f.readlines()
    return keywords


def stream_authorise():
    auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    if not api:
        print('Cannot authenticate')
        print('failed consumer id ----------: ', credentials.CONSUMER_KEY)
    return auth

def rest_authorise():
    auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    if not api:
        print('Cannot authenticate')
        print('failed consumer id ----------: ', credentials.CONSUMER_KEY)
    return api



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
        verified = tweet['user']['verified']
        media = tweet['entities']['urls']

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
                          'retweets': retweets, 'quote tweets': quote, 'verified': verified, 'media': media}

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
        streamer = tweepy.Stream(auth=stream_authorise(), listener=listener)
        print("Tracking: " + str(read_keywords()))
        streamer.filter(track=read_keywords())


class APIStreamListener(StreamListener):
    """
    Basic listener class
    """

    def __init__(self, time_limit=10):
        self.start_time = time.time()
        self.limit = time_limit
        super(StreamListener, self).__init__()

    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_data(self, raw_data):
        client = MongoClient('127.0.0.1', 27017)
        db_name = "TwitterDump"  # set-up a MongoDatabase
        db = client[db_name]
        coll_name = 'Test'  # here we create a collection
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




def get_user(api, username):
    page = 1
    old_tweet = False

    client = MongoClient('127.0.0.1', 27017)
    db_name = "TwitterDump"  # set-up a MongoDatabase
    db = client[db_name]
    coll_name = 'Test_users'  # here we create a collection
    collection = db[coll_name]

    while True:
        tweets = api.user_timeline(username, page=page)

        for tweet in tweets:
            if (datetime.datetime.now() - tweet.created_at).days <= 1:
                print(tweet.user.name + ": " + tweet.text)

                try:
                    collection.insert_one(tweet)

                except Exception as e:
                    return True

            else:
                old_tweet = True
                return

        if not old_tweet:
            page += 1
            time.sleep(500)




if __name__ == '__main__':
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets()

    get_user(rest_authorise(), "NicolaSturgeon ")
    get_user(rest_authorise(), "JeaneF1MSP")
    get_user(rest_authorise(), "MattHancock")
    get_user(rest_authorise(), "uksciencechief")
    get_user(rest_authorise(), "PHE_uk")




