import json
import mechanicalsoup
import os
import requests

from database import LocationDb
from refWebSites import MySoccerLeague


locationdb = LocationDb()


def augmentMSLData(venue: str) -> dict:
    # The MySoccerLeague does not have location information any fucking where
    # so we have the data we need in a separate database

    locationData = locationdb.findLocation(venue)

    lat = 0.0
    lon = 0.0
    if len(locationData) > 0:
        city = locationData[0]['facility']
        state = locationData[0]['state']
        lat = locationData[0]['latitude']
        lon = locationData[0]['longitude']
        distance = locationData[0]['distance']
    else:
        lat, lon = getLatLongForFacility(venue['city', venue['state'], venue['zip']])
        city = venue['city']
        state = venue['state']
        distance = getMileageForFacilityOpenRouteService(lat, lon)
        locationdb.addLocation(venue,
                               "street",
                               city,
                               state,
                               "zip",
                               lat,
                               lon,
                               distance)

    return {
        'city': city,
        'count': 1,
        'state': state,
        'latitude': lat,
        'longitude': lon,
        'distance': distance
    }


def alignMslData(assignments: list, data: dict):


    for assignment in assignments:
        venue = assignment[2].text.upper()

        # now why the fuck is the venue coming out as TBD?  Fuck off MSL
        if venue == 'TBD':
            venue = 'MARSHALL'

        if venue not in data:
            data[venue] = augmentMSLData(venue)


def getcity(facility: str) -> str:
    if facility == 'QUANTUM':
        return ""


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


def getFacilitiesFromOtherProgram() -> dict:

    # the data in gamesdetails.json is from assignr.com and created in the main in main.py
    retVal = {}

    filename = "gamesdetails.json"
    with open(filename, 'r') as f:
        data = json.load(f)
        for k, v in data.items():
            for item in v:
                name = item['venue']['name'].upper()
                dbData = locationdb.findLocation(name)

                if name not in retVal:
                    retVal[name] = {}
                    retVal[name]['count'] = 1
                    # grab this extra stuff just in case we need it
                    retVal[name]['latitude'] = item['venue']['latitude'] if 'latitude' in item['venue'] and item['venue']['latitude'] is not None else dbData[0][1]
                    retVal[name]['longitude'] = item['venue']['longitude'] if 'longitude' in item['venue'] and item['venue']['longitude'] is not None else dbData[0][2]
                    retVal[name]['distance'] = dbData[0][6] if len(dbData) > 0 else 0.0
                else:
                    retVal[name]['count'] += 1
    return retVal



def getAssignrFacilities(gameData: dict) -> dict:

    # the data in gamesdetails.json is from assignr.com and created in the main in main.py
    retVal = {}

    for k, v in gameData.items():
        for item in v:
            name = item['venue']['name'].upper()
            dbData = locationdb.findLocation(name)

            if len(dbData) < 1:
                print(f"Facility {name} is not in the database yet!")

                latitude = item['venue']['latitude']
                longitude = item['venue']['longitude']

                # get milage from the OpenRouteService API
                distance = getMileageForFacilityOpenRouteService(latitude, longitude)

                # add it
                locationdb.addLocation(name,
                                       item['venue']['street_1'] if 'street_1' in item['venue'] and item['venue']['street_1'] is not None else "street",
                                       item['venue']['city'] if 'city' in item['venue'] and item['venue']['city'] is not None else "city",
                                       item['venue']['state_or_province'] if 'state_or_province' in item['venue'] and item['venue']['state_or_province'] is not None else "state",
                                       item['venue']['postal'] if 'postal' in item['venue'] and item['venue']['postal'] is not None else "zip",
                                       latitude,
                                       longitude,
                                       distance)

            if name not in retVal:
                retVal[name] = {}
                retVal[name]['count'] = 1
                # grab this extra stuff just in case we need it
                retVal[name]['latitude'] = item['venue']['latitude'] if 'latitude' in item['venue'] and item['venue']['latitude'] is not None else dbData[0][1]
                retVal[name]['longitude'] = item['venue']['longitude'] if 'longitude' in item['venue'] and item['venue']['longitude'] is not None else dbData[0][2]
                retVal[name]['distance'] = dbData[0][6] if len(dbData) > 0 else 0.0
            else:
                retVal[name]['count'] += 1
    return retVal


def getMileageForFacilityOpenRouteService(latitude: float, longitude: float) -> float:
    """
    Uses OpenRouteService API for driving distance calculation.
    Free tier: 2,000 requests/day
    """
    # Get free API key from https://openrouteservice.org/dev/#/signup
    orsKey = os.environ.get('openRouteKey')

    originLatitude, originLongitude = 38.9062046, -77.2777969

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': orsKey,
        'Content-Type': 'application/json; charset=utf-8'
    }

    body = {
        "coordinates": [[originLongitude, originLatitude], [longitude, latitude]],
        "format": "json"
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 200:
        data = response.json()
        distance_km = data['routes'][0]['summary']['distance'] / 1000
        distance_miles = distance_km * 0.621371
        return distance_miles
    else:
        print(f"ORS Error: {response.status_code}")
        return 0


def getAssignmentsForMileageData(gameData: dict) -> dict:
    # Get location data from the json produced by the "other" program
    # this data is from assignr.com
    # data = getFacilitiesFromOtherProgram()
    data = getAssignrFacilities(gameData)

    # Merge in the data from MSL
    br = mechanicalsoup.StatefulBrowser(soup_config={ 'features': 'lxml'})
    br.addheaders = [('User-agent', 'Chrome')]
    msl = MySoccerLeague(br)
    assignments = msl.getYearEndAssignments()
    alignMslData(assignments, data)

    return data

# def doMileage(data: dict) -> None:

#     finalData = {}

#     for k, v in data.items():
#         locationFromDb = locationdb.findLocation(k)
#         distance = 0
#         if len(locationFromDb) < 1:
#             print(f"Facility {k} is not in the database yet!")

#             # add the location after getting the rest of the data
#             # try to get the details of the location (address, zip)
#             # locationData = getLocationDetailsForFacility(k)
#             # if locationData is None:
#             #     print(f"Could not find facility info for {k}!!!")
#             #     continue

#             # get the lat and long from the tamu web site
#             # latitude, longitude = getLatLongForFacility(locationData[k]['city'],
#             #                                             locationData[k]['state'],
#             #                                             locationData[k]['zip'])

#             # get milage from the Bing API
#             distance = getMilageForFacility(v['latitude'], v['longitude'])

#             # add it
#             locationdb.addLocation(k,
#                                    v['address'],
#                                    None,
#                                    v['state'],
#                                    v['zip'],
#                                    v['latitude'],
#                                    v['longitude'],
#                                    distance)

#         else:
#             distance = locationFromDb[0]['distance']

#         print(f'Distance to {k} is {distance}')
#         finalData[k] = v
#         finalData[k]['distance'] = distance

#     # math
#     totalMileage = 0
#     for value in finalData.values():
#         totalMileage += value['count'] * value['distance']

#     print("Total mileage for {0} is {1}".format(dt.now().year - 1, totalMileage))
