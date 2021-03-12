from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)

db = client["TwitterDump"]


def part_one():
    count_rt = 0
    quote_tweets = 0
    geo_tagged = 0
    location_obj = 0

    for x in db.colTest.find({}, {'text': 1}):
        if x['text'][0:2] == 'RT':
            count_rt += 1

        if x['text'][0] == "'":
            quote_tweets += 1

    for x in db.colTest.find({}, {'geoenabled': 1}):
        if x['geoenabled']:
            geo_tagged += 1

    for x in db.colTest.find({}, {'location': 1}):
        if x['location'] != None:
            location_obj += 1

    print(db.colTest.count_documents({}))
    print("quote tweets = " + str(quote_tweets))
    print("retweets = " + str(count_rt))
    print("geotagged = " + str(geo_tagged))
    print("location objects = " + str(location_obj))


if __name__ == '__main__':
    part_one()

