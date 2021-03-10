import json

import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from wordcloud import WordCloud

client = MongoClient('127.0.0.1', 27017)

with client:
    db = client["TwitterDump"]
    collection = db.March7th.find({}, {'username':1, 'text': 1})
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

'''
plt.plot(k_vals, sq_distance_sum, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum of the squared distances')
plt.title('Optimal k (Elbow method)')
plt.show()
'''

true_k = 7
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=200, n_init=10)
model.fit(x)
labels = model.labels_
tweet_col = pd.DataFrame(list(zip(users, tweets, labels)), columns=['users', 'tweets', 'cluster'])
print(tweet_col.sort_values(by=['cluster']))


cluster_1 = db['cluster_1']







'''
result = {'cluster': list(labels), 'tweets': tweets}
result = pd.DataFrame(result)
for k in range(0, true_k):
   s=result[result.cluster==k]
   text=s['tweets'].str.cat(sep=' ')
   text=text.lower()
   text=' '.join([word for word in text.split()])


wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text)
print('Cluster: {}'.format(k))
print('Users')
titles= tweet_col[tweet_col.cluster==k]['users']
print(titles.to_string(index=False))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
'''







