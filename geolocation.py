from pymongo import MongoClient
import pandas as pd

if __name__ == '__main__':
    client = MongoClient('127.0.0.1', 27017)

    with client:
        db = client["TwitterDump"]
        locations = db.March7th.distinct('place_name')

    pd.Series(locations).value_counts().plot(kind='hist')