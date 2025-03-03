from datetime import datetime as dt
import json
import mechanicalsoup
import os
import requests

from database import LocationDb
from refWebSites import MySoccerLeague



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


def getMilageForFacility(latitude: float, longitude: float) -> float:
    """
    Given the latitude and longitude for a facility, use them
    to make an API request to the Bing mapping endpoint.
    The data from the API call we are interested in is called travelDistance.
    This API from Bing requires you to register for an API key and that  API key
    is conveyed via the environment.
    """
    bingKey = os.environ['bingKey']
    distanceUrl = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins=38.9062046,-77.2777969&destinations={0},{1}&travelMode=driving&key={2}"
    url = distanceUrl.format(latitude, longitude, bingKey)
    response = requests.get(url)
    jsonData = json.loads(response.content)
    distance = jsonData['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']
    return distance


def augmentMSLData(venue: str) -> dict:
    # The MySoccerLeague does not have location information any fucking where
    state = 'VA'
    city = 'VIENNA'
    if venue.startswith('Marshall'):
        city = "FALLS CHURCH"
    elif venue.startswith('Luther Jackson'):
        city = 'FALLS CHURCH'
    elif venue.startswith('Oak Marr'):
        city = 'OAKTON'
    elif venue.startswith('Oakton High'):
        city = 'OAKTON'
    elif venue.startswith('Ken Lawrence'):
        city = 'TYSONS'

    return {
        'city': city,
        'count': 1,
        'state': state
    }

def alignMslData(assignments: list, data: dict):

    # from

    # 00:<td>5/14/2022 - 5:00 PM</td>
    # 01:<td>741505</td>
    # 02:<td><a href="javascript:directWindow('Quantum Field','7980 Quantum Dr, Vienna, VA 22182','No comments')">Quantum Field</a></td>
    # 03:<td>U-14</td>
    # 04:<td>Girls</td>
    # 05:<td>Rec</td>
    # 06:<td align="center">Cullison <b>[2]</b></td>
    # 07:<td align="center">Nguyen <b>[3]</b></td>
    # 08:<td align="center"><font color="green">Joseph Testa</font></td>
    # 09:<td align="center"><font color="red">Sophie  Hinton</font></td>
    # 10:<td align="center"><font color="red"><b>Martin Cooley</b></font></td>
    # 11:<td align="center"><a href="ShowAGamesReports.jsp?YSLkey=TGSKHHQCKTRGKLTGVKHKSCQKHK&amp;dateMode=selectDates&amp;refId=12920&amp;startDate=1/1/22&amp;endDate=12/26/22&amp;returnJsp=GamesReffedReport.jsp&amp;gameId=741505">View</a></td>

    # to

    #data['OAK MARR - REC CENTER TURF #2']
    #{'city': 'OAKTON', 'count': 1, 'state': 'VA'}
    for assignment in assignments:
        venue = assignment[2].text.upper()
        if venue not in data:
            data[venue] = augmentMSLData(venue)


def getcity(facility: str) -> str:
    if facility == 'QUANTUM':
        return ""
def getFacilitiesFromOtherProgram() -> dict:

    # data['OAK MARR - REC CENTER TURF #2']
    #   {'city': 'OAKTON', 'count': 1, 'state': 'VA'}
    retVal = {}

    filename = "gamedetails.json"
    with open(filename, 'r') as f:
        data = json.load(f)
        for k, v in data.items():
            for item in v:
                name = item['venue']['name'].upper()
                dbData = locationdb.findLocation(name)
                if name not in retVal:
                    retVal[name] = {}
                    retVal[name]['city'] = item['venue']['city'].upper() if 'city' in item['venue'] else getcity(name)
                    retVal[name]['state'] = item['venue']['state_or_province'].upper() if 'state_or_province' in item['venue'] else dbData[0][3]
                    retVal[name]['count'] = 1
                    # grab this extra stuff just in case we need it
                    retVal[name]['latitude'] = item['venue']['latitude'] if 'latitude' in item['venue'] else dbData[0][1]
                    retVal[name]['longitude'] = item['venue']['longitude'] if 'longitude' in item['venue'] else dbData[0][2]
                    retVal[name]['address'] = item['venue']['street_1'] if 'street_1' in item['venue'] else dbData[0][4]
                    retVal[name]['zip'] = item['venue']['postal'] if 'postal' in item['venue'] else dbData[0][5]
                else:
                    retVal[name]['count'] += 1
          # get the venue name from ['venue']['name']
    return retVal


if __name__ == "__main__":

    # what year is it?
    year = dt.now().year

    locationdb = LocationDb()
    finalData = {}

    # Get location data from the json produced by the "other" program
    data = getFacilitiesFromOtherProgram()

    # Merge in the data from MSL
    br = mechanicalsoup.StatefulBrowser(soup_config={ 'features': 'lxml'})
    br.addheaders = [('User-agent', 'Chrome')]
    msl = MySoccerLeague(br)
    assignments = msl.getYearEndAssignments()
    alignMslData(assignments, data)

    count = 0
    for k, v in data.items():
        count += v['count']
    print(count)

    for k, v in data.items():
        locationFromDb = locationdb.findLocation(k)
        distance = 0
        if len(locationFromDb) < 1:
            print(f"Facility {k} is not in the database yet!")

            # add the location after getting the rest of the data
            # try to get the details of the location (address, zip)
            # locationData = getLocationDetailsForFacility(k)
            # if locationData is None:
            #     print(f"Could not find facility info for {k}!!!")
            #     continue

            # get the lat and long from the tamu web site
            # latitude, longitude = getLatLongForFacility(locationData[k]['city'],
            #                                             locationData[k]['state'],
            #                                             locationData[k]['zip'])

            # get milage from the Bing API
            distance = getMilageForFacility(v['latitude'], v['longitude'])

            # add it
            locationdb.addLocation(k,
                                   v['address'],
                                   None,
                                   v['state'],
                                   v['zip'],
                                   v['latitude'],
                                   v['longitude'],
                                   distance)

        else:
            distance = locationFromDb[0]['distance']

        print(f'Distance to {k} is {distance}')
        finalData[k] = v
        finalData[k]['distance'] = distance

    # math
    totalMileage = 0
    for value in finalData.values():
        totalMileage += value['count'] * value['distance']

    print("Total mileage for {0} is {1}".format(dt.now().year - 1, totalMileage))
