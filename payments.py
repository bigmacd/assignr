import aiohttp
import asyncio
import json
import logging
from typing import Union

from oauth import OauthToken

oauthToken = OauthToken()


def processPaymentsResponse(response) -> dict:
    retVal = {}
    numRecords = response['page']['records']
    print(f"Got {numRecords} payment entries")
    for entry in response['_embedded']['statements']:
        # keys = ['id', 'statement_date', 'description', 'status', 'amount', 'amount_paid', 'currency',
        # 'formatted_amount', 'formatted_amount_paid', 'payor_name', 'created', 'updated', '_links', '_embedded']
        assignor = entry['_embedded']['site']['id']
        if assignor not in retVal:
            retVal[assignor] = []
        retVal[assignor].append( {
            'name': entry['payor_name'],
            'date': entry['statement_date'],
            'description': entry['description'],
            'amount': entry['amount'],
            'amount_paid': entry['amount_paid']
        } )
    return retVal


def getPaymentsForYear(payments: dict, year: str) -> dict:
    # The assignr API doesn't support filtering by year, so we have to do it here
    retVal = {}
    for assignor in payments:
        if assignor not in retVal:
            retVal[assignor] = []
        for payment in payments[assignor]:
            if payment['date'].startswith(year):
                retVal[assignor].append(payment)
    return retVal


async def getPayments(year: Union[str, None] = None):

    retVal = None
    while True:

        url = "https://api.assignr.com/api/v2/statements?page=1&limit=50"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers = oauthToken.getHeader()) as response:
                    if response.status == 200:
                        answer = json.loads(await response.text())
                        retVal = processPaymentsResponse(answer)
                        break
                    if response.status == 401:
                        await oauthToken.getToken()
        except (asyncio.TimeoutError, aiohttp.ClientError) as ex:
            logging.error(f"Failed to retrieve payment info: {ex}")

    if year is None:
       return retVal
    else:
        return getPaymentsForYear(retVal, year)


# for testing only

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    payments = loop.run_until_complete(asyncio.gather(getPayments("2024")))
    print(payments)

