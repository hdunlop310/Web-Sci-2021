# Web Science 2021



In order to run the code, you must create a file called credentials.py in the same directory as the rest of the .py files and add in your Twitter Developer credentials. For example:

```python
ACCESS_TOKEN = " "
ACCESS_TOKEN_SECRET = " "
CONSUMER_KEY = " "
CONSUMER_SECRET = " "
```

1. Firstly, you should run basic_crawler.py for an hour to collect some tweets. This crawler filters words from the text file called keywords.txt, filters tweets only in English and tweets only from the UK.
2. To get the information about the collected tweets (such as number of verified, number of geo-enabled, etc...), run generate_info.py.
3. To cluster the findings, run cluster.py
4. Now, run the enhanced_crawler.py to get more specific tweets. To get the info and to cluster the new collection, follow the instructions above.
5. To analyse the locations of the tweets, run geolocation.py
6. To analyse the events in each collection, run event_detection.py
