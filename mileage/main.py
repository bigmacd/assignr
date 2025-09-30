import argparse
from datetime import datetime as dt
import json
import mechanicalsoup
import os
import requests



def getLatLong(cityStateData: dict) -> dict:
    """
    Given the cityStateData dictionary, find the latitude and longitude for
    each item and add the lat/long info to the dictionary.
    This uses an API from Texas A&M University for which you must request
    an API key and the key is conveyed via the environment.
    """
    geoCodeKey = os.environ['geoCodeKey']
    geocodeUrl = "https://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsedAdvanced_V04_01.aspx?apiKey={0}&version=4.1&format=json&verbose=true&StreetAddress=%20%20%20%20%20%20&city={1}&state={2}&zip=&ratts=PreDirectional,Suffix,PostDirectional,City,Zip&souatts=StreetName,City"
    geocodeUrlDetail = "https://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsedAdvanced_V04_01.aspx?apiKey={0}&version=4.1&format=json&verbose=true&StreetAddress={1}&city={2}&state={3}&zip={4}&ratts=PreDirectional,Suffix,PostDirectional,City,Zip&souatts=StreetName,City"
    for location in cityStateData.items():
        city = location[1]['city']
        state = location[1]['state']
        url = geocodeUrl.format(geoCodeKey, city, state)
        response = requests.get(url)
        jsonData = json.loads(response.content)
        latitude = jsonData['OutputGeocodes'][0]['OutputGeocode']['Latitude']
        longitude = jsonData['OutputGeocodes'][0]['OutputGeocode']['Longitude']
        location[1]['latitude'] = latitude
        location[1]['longitude'] = longitude
    return cityStateData


def getLatLongForFacility(city: str, state: str, zip: str) -> tuple:
    """
    Given the city and state provided, find the latitude and longitude for
    it and return both latitude and longitude.
    This uses an API from Texas A&M University for which you must request
    an API key and the key is conveyed via the environment.
    """
    geoCodeKey = os.environ['geoCodeKey']
    geocodeUrl = "https://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsedAdvanced_V04_01.aspx?apiKey={0}&version=4.1&format=json&verbose=true&StreetAddress=%20%20%20%20%20%20&city={1}&state={2}&zip={3}&ratts=PreDirectional,Suffix,PostDirectional,City,Zip&souatts=StreetName,City"
    geocodeUrlDetail = "https://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsedAdvanced_V04_01.aspx?apiKey={0}&version=4.1&format=json&verbose=true&StreetAddress={1}&city={2}&state={3}&zip={4}&ratts=PreDirectional,Suffix,PostDirectional,City,Zip&souatts=StreetName,City"
    url = geocodeUrl.format(geoCodeKey, city, state, zip)
    response = requests.get(url)
    jsonData = json.loads(response.content)
    latitude = jsonData['OutputGeocodes'][0]['OutputGeocode']['Latitude']
    longitude = jsonData['OutputGeocodes'][0]['OutputGeocode']['Longitude']
    return latitude, longitude


def getMilage(cityStateData: dict) -> dict:
    """
    Given the cityStateData dictionary, retrieve the latitude and longitude for
    each item and use them to make an API request to the Bing mapping endpoint.
    The data from the API call we are interested in is called travelDistance.
    This API from Bing requires you to register for an API key and that API key
    is conveyed via the environment.
    """
    bingKey = os.environ['bingKey']
    distanceUrl = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins=38.9062046,-77.2777969&destinations={0},{1}&travelMode=driving&key={2}"
    for data in cityStateData.values():
        latitude = data['latitude']
        longitude = data['longitude']
        url = distanceUrl.format(latitude, longitude, bingKey)
        response = requests.get(url)
        jsonData = json.loads(response.content)
        distance = jsonData['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']
        data['distance'] = distance
    return cityStateData


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
