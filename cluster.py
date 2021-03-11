import json

import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

client = MongoClient('127.0.0.1', 27017)

with client:
    db = client["TwitterDump"]
    collection = db.March7th.find({}, {'username': 1, 'text': 1})
    tweets = []
    users = []

    for tweet in collection:
        tweets.append(tweet['text'])
        users.append(tweet['username'])

vectorizer = TfidfVectorizer(stop_words={'english'})
x = vectorizer.fit_transform(tweets)

sq_distance_sum = []
k_vals = range(2, 10)
for k in k_vals:
    km = KMeans(n_clusters=k, max_iter=200, n_init=10)
    km = km.fit(x)
    sq_distance_sum.append(km.inertia_)


true_k = 7
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=200, n_init=10)
model.fit(x)
labels = model.labels_
tweet_col = pd.DataFrame(list(zip(users, tweets, labels)), columns=['users', 'tweets', 'cluster'])
print(tweet_col.sort_values(by=['cluster']))

