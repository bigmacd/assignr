import asyncio
import aiohttp
import logging
import json

from oauth import OauthToken

oauthToken = OauthToken()

def processSitesResponse(response) -> list:
    retVal = []
    for site in response['_embedded']['sites']:
        retVal.append((site['id'], site['name']))
    return retVal


async def getSites():

    url = "https://api.assignr.com/api/v2/sites?page=1&limit=50"

    while True:

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers = oauthToken.getHeader()) as response:
                    if response.status == 200:
                        answer = json.loads(await response.text())
                        return processSitesResponse(answer)
                    if response.status == 401:
                        await oauthToken.getToken()
        except (asyncio.Timeout, aiohttp.ClientError) as ex:
            logging.error(f"Failed to retrieve sites info: {ex}")


# for testing only

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    sites = loop.run_until_complete(asyncio.gather(getSites()))
    print('end')
