import aiohttp
import argparse
import asyncio
import json
import logging
import pprint

from oauth import OauthToken
oauthToken = OauthToken()

from games import getGames, getGamesReffed
from payments import getPayments
from sites import getSites


loop = asyncio.get_event_loop()

paymentDetails = None
games = None


def saveToFile(data: dict, filetype: str) -> None:
    with open(filetype, 'w') as fp:
        json.dump(data, fp, indent=2)
        #pprint.pprint(data, stream = fp, indent=2)


# you have to get some site data first before you can get all the games
#tasks = getSites()
#sites = loop.run_until_complete(asyncio.gather(tasks))
def main(year: str) -> tuple:
    tasks = getPayments(year), getGames(year)
    paymentDetails, gameDetails = loop.run_until_complete(asyncio.gather(*tasks))
    gamesIreffed = loop.run_until_complete(asyncio.gather(getGamesReffed(gameDetails)))

    return gameDetails, paymentDetails, gamesIreffed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action="store_true")
    parser.add_argument('-y', "--year", type = str)
    args = parser.parse_args()

    gameDetails, paymentDetails, gamesIreffed = main(args.year)

    if args.c is True:
        saveToFile(gameDetails, "gamedetails.json")
        saveToFile(paymentDetails, "paymentdetails.json")
        saveToFile(gamesIreffed, 'gamesireffed.json')
