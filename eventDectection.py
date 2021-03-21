import json
import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')

client = MongoClient('127.0.0.1', 27017)

more_stop_words = ['!', '?', 'm', 'n', 't', 've', "'", '.', ',', 's', ';', "`", 'https', 'co', 't']
all_stopwords = stopwords.words('english')
all_stopwords.extend(more_stop_words)

with client:
    db = client["TwitterDump"]
    collection = db.March21st.find({}, {'username': 1, 'text': 1, 'geoenabled':1, 'location':1, 'verified':1, 'media':1})
    tweets = []
    users = []
    geoenabled = []
    locations = []
    verified = []
    media = []

    for tweet in collection:
        tweet['text'] = tweet['text'].lower()
        text_tokens = word_tokenize(tweet['text'])
        tokens_without_sw = [word for word in text_tokens if not word in all_stopwords]
        tweet['text'] = (" ").join(tokens_without_sw)

        tweets.append(tweet['text'])
        users.append(tweet['username'])
        geoenabled.append(tweet['geoenabled'])
        locations.append(tweet['location'])
        verified.append(tweet['verified'])
        media.append(tweet['media'])


vectorizer = TfidfVectorizer(stop_words={'english'})
x = vectorizer.fit_transform(tweets)

sq_distance_sum = []
k_vals = range(2, 10)
for k in k_vals:
    km = KMeans(n_clusters=k, max_iter=200, n_init=10)
    km = km.fit(x)
    sq_distance_sum.append(km.inertia_)

true_k = 5
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=200, n_init=10)
model.fit(x)
labels = model.labels_
tweet_col = pd.DataFrame(list(zip(users, tweets, geoenabled, locations, verified, media, labels)), columns=['users', 'tweets', 'geoenabled', 'locations', 'verified', 'media', 'cluster'])
print(tweet_col.sort_values(by=['cluster']))

results = {'clusters': labels, 'tweets': tweets, 'users': users, 'geoenabled': geoenabled, 'locations': locations, 'verified': verified, 'media': media}

result = pd.DataFrame(results)

'''
k = 3
s = result[result.cluster == k]
text = s ['tweets'].str.cat(sep=' ')
text = text.lower()
text = ' '.join([word for word in text.split()])

wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text)
print('Cluster: {}'.format(k))
clusters = tweet_col[tweet_col.cluster==k]['cluster']
print(clusters.to_string(index=False))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
'''

cluster0_locations = []
for x in db.enhanced_cluster0.find({}, {'location': 1}):
    if x['location'] != None:
        cluster0_locations.append(x['location'])

cluster1_locations = []
for x in db.enhanced_cluster1.find({}, {'location': 1}):
    if x['location'] != None:
        cluster1_locations.append(x['location'])

cluster2_locations = []
for x in db.enhanced_cluster2.find({}, {'location': 1}):
    if x['location'] != None:
        cluster2_locations.append(x['location'])

cluster3_locations = []
for x in db.enhanced_cluster3.find({}, {'location': 1}):
    if x['location'] != None:
        cluster3_locations.append(x['location'])

cluster4_locations = []
for x in db.enhanced_cluster4.find({}, {'location': 1}):
    if x['location'] != None:
        cluster4_locations.append(x['location'])

print(cluster0_locations)
print(cluster1_locations)
print(cluster2_locations)
print(cluster3_locations)
print(cluster4_locations)