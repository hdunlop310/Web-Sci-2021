from pymongo import MongoClient
import pandas as pd


def get_locations():
    client = MongoClient('127.0.0.1', 27017)

    with client:
        db = client["TwitterDump"]
        locations = db.March21New.distinct('location')

    for location in locations:
        locations.remove(location)
        location = str(location)
        locations.append(location)

    return locations


def get_uk_cities():
    cities_list = []
    with open('gb.csv', 'r') as f:
        for row in f:
            array = []
            array = row.strip().split(',')
            cities_list.append(array[0])

    cities_list.remove('city')

    return cities_list


def get_uk_towns():
    town_list = []
    with open('uk-towns-sample.csv', 'r') as f:
        for row in f:
            array = []
            array = row.strip().split(',')
            town_list.append(array[1])

    town_list.remove('name')
    return town_list


def get_uk_county():
    county_list = []
    with open('uk-towns-sample.csv', 'r') as f:
        for row in f:
            array = []
            array = row.strip().split(',')
            county_list.append(array[2])

    county_list.remove('county')
    return county_list


def plot_cities_graph():
    locations = get_locations()
    cities_list = get_uk_cities()

    cities = []
    for location in locations:
        for city in cities_list:
            if city in location:
                cities.append(city)

    pd.Series(cities).value_counts().plot(kind='pie', title='Geographical Breakdown: Cities', legend=True, labels=None)


def plot_country_graph():
    country_list = ['Scotland', 'England', 'Northern Ireland', 'Wales']
    locations = get_locations()

    countries = []
    for location in locations:
        for country in country_list:
            if country in location:
                countries.append(country)

    pd.Series(countries).value_counts().plot(kind='pie', title='Geographical Breakdown: Countries', legend=True, labels=None)


def plot_towns_graph():
    locations = get_locations()
    town_list = get_uk_towns()

    towns = []
    for location in locations:
        for town in town_list:
            if town in location:
                towns.append(town)

    pd.Series(towns).value_counts().plot(kind='pie', title='Geographical Breakdown: Towns',  legend=True, labels=None)


def plot_county_graph():
    locations = get_locations()
    county_list = get_uk_county()

    counties = []
    for location in locations:
        for county in county_list:
            if county in location:
                counties.append(county)

    pd.Series(counties).value_counts().plot(kind='pie', title='Geographical Breakdown: Counties', legend=True, labels=None)


if __name__ == '__main__':
    #plot_cities_graph()
    #plot_country_graph()
    #plot_towns_graph()
    #plot_county_graph()
    pass
