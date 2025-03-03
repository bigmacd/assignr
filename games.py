import asyncio
import aiohttp
import datetime
import json
import logging
from typing import Union

from oauth import OauthToken

oauthToken = OauthToken()


# games has an assignor key, but the id in that dict is not the assignor's id
# WTF?!?
# assignors:
# 21774 is Deplitch
# 21411 is Davis
# 21927 is Tammy
# 22128 is Tarey

# in the games details,
# id 1297491 is Tarey
# id 1230378 is Deplitch
# id 1269537 is Tammy
# id 1488768 is Davis

assignorMapping = {
    1297491: 22128,
    1230378: 21774,
    1269537: 21927,
    1488768: 21411,
    "unknown": "unknown"
}

today = datetime.datetime.now()
year = today.year
startDate = f"1/1/{year}"
endDate = f"12/31/{year}"

def processGames(response) -> dict:
    retVal = {}

    # 'page': 'records', 'pages', 'current_page': 1

    # games is a dict:
    # 'id', 'start_time', 'end_time', 'localized_date', 'localized_time', 'localized_end_time',
    # 'age_group', 'home_team', 'away_team', 'game_type', 'gender', 'league', 'pattern', 'status',
    # 'cancelled', 'published', 'user_defined_id', 'external_id', 'lock_version', 'subvenue',
    # 'public_note', 'public_note_html', 'created', 'updated', '_links', '_embedded'

    # in the games dict, '_embedded' has a key of 'venue' that has:
    # id', 'name', 'longitude', 'latitude', 'street_1', 'city', 'state_or_province', 'postal', 'created', 'updated', '_links'

    games = response['_embedded']['games']
    for game in games:

        try:
            id = game['_embedded']['assignor']['id']
            # map to the assignor id from "/sites" to align with payments data
            id = assignorMapping[id]
        except KeyError:
            try:
                id = game['_embedded']['site']['id']
            except KeyError:
                id = "unknown"

        # please note: game['embedded']['venue'] contains the location
        # AND the latitude and longitude of the field!!!
        if id not in retVal:
            retVal[id] = []
        retVal[id].append(
            {
                'gameid': game['id'],
                'venue': game['_embedded']['venue'],
                'site': game['_embedded']['site'],
                'assignments':  game['_embedded']['assignments']
            }
        )

    return retVal


async def getGames(year: Union[str, None]):

    allgames = {}


    def getYearRange(year: Union[str, None]):
        if year is None:
            year = datetime.datetime.now().year

        startDate = f"1/1/{year}"
        endDate = f"12/31/{year}"
        return startDate, endDate

    startDate, endDate = getYearRange(year)

    try:
        done = False
        pageNumber = 1
        while not done:
            #url = f"https://api.assignr.com/api/v2/current_account/games?page={pageNumber}"
            url = f"https://api.assignr.com/api/v2/current_account/games?page={pageNumber}&search[start_date]={startDate}&search[end_date]={endDate}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers = oauthToken.getHeader()) as response:
                    if response.status == 200:
                        answer = json.loads(await response.text())
                        latestGames = processGames(answer)

                        # combine the games in latestGames (by key) with the games
                        # in allgames (by the same key)
                        # latestGames is a multi-key dictionary, so we need to iterate over it
                        for k, v in latestGames.items():
                            if k in allgames:
                                allgames[k].extend(v)
                            else:
                                allgames[k] = v

                        if 'next' in answer['_links']:
                            pageNumber += 1
                        else:
                            done = True
                    if response.status == 401:
                        await oauthToken.getToken()
    except Exception as ex:
        logging.error(f"Failed to retrieve game info: {ex}")
    except aiohttp.ClientError as ex:
        logging.error(f"Failed to retrieve game info: {ex}")


    return allgames


async def getAssignmentDetails(url: str):
    #try:
        allgames = []
        done = False
        pageNumber = 1
        while not done:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers = oauthToken.getHeader()) as response:
                    if response.status == 200:
                        answer = json.loads(await response.text())
                        # since we might be iterating over games in pages for the same assignor id
                        # this has to concatenate instead of merge
                        allgames.append(answer)

                        if 'next' in answer['_links']:
                            pageNumber += 1
                        else:
                            done = True
                    if response.status == 401:
                        await oauthToken.getToken()
    # except asyncio.Timeout as ex:
    #     logging.error(f"Failed to retrieve game info: {ex}")
    # except aiohttp.ClientError as ex:
    #     logging.error(f"Failed to retrieve game info: {ex}")
        return allgames


async def getGamesReffed(gamedetails: dict):

    async def processAssignments():

        url = a['_links']['self']['href']
        return await getAssignmentDetails(url)

    # assignmentKeys = ['position', 'accepted', "fees", "updated", "links"]

    assignmentDetails = []
    for k, v in gamedetails.items():
        for data in v:
            if type(data) == dict:
                for a in data['assignments']:
                    assignmentDetails.append(await processAssignments(a))
            elif type(data) == list:
            #assignments = data['assignments']
                for assignment in data:
                    for a in assignment['assignments']:
                        assignmentDetails.append(await processAssignments(a))
    return assignmentDetails
