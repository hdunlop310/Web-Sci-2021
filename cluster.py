import json
import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')

client = MongoClient('127.0.0.1', 27017)

more_stop_words = ['!', '?', 'm', 'n', 't', 've', "'", '.', ',', 's', ';', "`"]
all_stopwords = stopwords.words('english')
all_stopwords.extend(more_stop_words)

with client:
    db = client["TwitterDump"]
    collection = db.March18th.find({}, {'username': 1, 'text': 1, 'geoenabled':1})
    tweets = []
    users = []
    geoenabled = []

    for tweet in collection:
        tweet['text'] = tweet['text'].lower()
        text_tokens = word_tokenize(tweet['text'])
        tokens_without_sw = [word for word in text_tokens if not word in all_stopwords]
        tweet['text'] = (" ").join(tokens_without_sw)

        tweets.append(tweet['text'])
        users.append(tweet['username'])
        geoenabled.append(tweet['geoenabled'])


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
plt.xlabel('k_val')
plt.ylabel('sq_distance_sum')
plt.title('Optimal k (elbow method)')
plt.show()
'''


true_k = 5
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=200, n_init=10)
model.fit(x)
labels = model.labels_
tweet_col = pd.DataFrame(list(zip(users, tweets, geoenabled, labels)), columns=['users', 'tweets', 'geoenabled', 'cluster'])
print(tweet_col.sort_values(by=['cluster']))


results = {'clusters': labels, 'tweets': tweets, 'users': users, 'geoenabled': geoenabled}

cluster0 = db['cluster0']
cluster1 = db['cluster1']
cluster2 = db['cluster2']
cluster3 = db['cluster3']
cluster4 = db['cluster4']
#cluster5 = db['cluster5']
#cluster6 = db['cluster6']

k = 0
for i in results['clusters']:

    if i == 0:
        cluster0.insert_one({'username': results['users'][k], 'text': results['tweets'][k], 'geoenabled': results['geoenabled'][k]})

    if i == 1:
        cluster1.insert_one({'username': results['users'][k], 'text': results['tweets'][k], 'geoenabled': results['geoenabled'][k]})

    if i == 2:
        cluster2.insert_one({'username': results['users'][k], 'text': results['tweets'][k], 'geoenabled': results['geoenabled'][k]})

    if i == 3:
        cluster3.insert_one({'username': results['users'][k], 'text': results['tweets'][k], 'geoenabled': results['geoenabled'][k]})

    if i == 4:
        cluster4.insert_one({'username': results['users'][k], 'text': results['tweets'][k], 'geoenabled': results['geoenabled'][k]})

    k += 1
'''
    if i == 5:
        cluster5.insert_one({'username': results['users'][k], 'text': results['tweets'][k], 'geoenabled': results['geoenabled'][k]})

    if i == 6:
        cluster6.insert_one({'username': results['users'][k], 'text': results['tweets'][k], 'geoenabled': results['geoenabled'][k]})
'''
