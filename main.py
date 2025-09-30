import argparse
import asyncio
from dateutil import parser as dateparser
import json

from oauth import OauthToken
oauthToken = OauthToken()
import time

from games import getGames
from database import LocationDb
from mileage import getAssignmentsForMileageData
from outputAssignrData import printGameSummary, printPaymentInfo
from payments import getPayments


loop = asyncio.get_event_loop()


locationdb = LocationDb()

def calculateMileageForYear(gameData: dict) -> None:
    mileage = 0.0
    assignments = getAssignmentsForMileageData(gameData)
    for v in assignments.values():

        mileage += v['distance'] * v['count']

    print(f"Total mileage is {mileage}")


def filterByDateRangeAnyYear(data, start_month_day, end_month_day):
    """
    Filter by month-day range across any year
    start_month_day and end_month_day are tuples like (6, 21) for June 21
    """
    filtered = []

    for item in data:
        try:
            timestamp = dateparser.parse(item['created'])
            month_day = (timestamp.month, timestamp.day)

            # Handle range that crosses year boundary (e.g., Dec 1 to Jan 31)
            if start_month_day <= end_month_day:
                if start_month_day <= month_day <= end_month_day:
                    filtered.append(item)
            else:  # Range crosses year
                if month_day >= start_month_day or month_day <= end_month_day:
                    filtered.append(item)

        except (ValueError, KeyError):
            continue

    return filtered

# Usage: June 21 to July 24
# filtered_data = filterByDateRangeAnyYear(data, (6, 21), (7, 24))

def saveToFile(data: dict, filetype: str) -> None:
    with open(filetype, 'w') as fp:
        json.dump(data, fp, indent=2)
        #pprint.pprint(data, stream = fp, indent=2)


def main(year: str) -> tuple:
    tasks = getPayments(year), getGames(year)
    paymentDetails, gameDetails = loop.run_until_complete(asyncio.gather(*tasks))
    return gameDetails, paymentDetails


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', "--year", type = str, help="get the data for a different year")
    parser.add_argument('-m', action="store_true", help="get the year-to-date mileage")
    args = parser.parse_args()

    gameDetails, paymentDetails = main(args.year)

    if args.m is True:
        # get the mileage for the year to date
        calculateMileageForYear(gameDetails)

    else:
        saveToFile(gameDetails, 'gamesdetails.json')
        print(f"Got data for {len(gameDetails)} assignors with games and {len(paymentDetails)} assignors with payments")
        gameFees = printGameSummary(gameDetails)
        print('--------------------------------------------------------------------------')
        gamePayments = printPaymentInfo(paymentDetails)

        for k in gameFees.keys():
            if k not in gamePayments:
                gamePayments[k] = 0.0
        print('--------------------------------------------------------------------------')

        for k, v in gameFees.items():
            print(f"Assignor: {k}, fees: {v}, paid: {gamePayments[k]}, diff: {v - gamePayments[k]}")

        # gameDetails is a dict of lists, keyed by assignor id
        # the value is a list of games as dicts:
        # the keys in this dict are gameid, venue, site, and assignments
        #     venue is a dict
        #         keys in venue are id, name, longitude, latitude, street_1, city, state_or_province, postal, created, updated, _links
        #     site is a dict (this is the assignor)
        #         keys in site are id, name, timezone, created, updated, _links
        #     assignments is a list of dicts
        #         keys in assignments are id, position_id, position, position_abbreviation, accepted, declined, assigned, sort_order, lock_version, created, updated, updated, _links, _embedded
        #             assignments._embedded has keys of official and fees ('fees' is present only if I am this entry (not other officials))
        #                 fees is a list of dicts
        #                     keys in fees are value, formatted, currency, description, game_fees, travel_fees

        # paymentDetails is a dict of lists, keyed by assignor id
        # the value is a list of payments as dicts:
        #     the keys in this dict are name, date, description, amount, amount_paid
        #         no further dictionaries inside
