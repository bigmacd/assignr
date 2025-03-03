import asyncio
import aiohttp
import os
import logging
import json


class OauthToken():

    accessToken = None
    refreshToken = None
    tokenUrl = "https://app.assignr.com/oauth/token"
    clientId = os.environ.get("clientID")
    clientSecret = os.environ.get("clientSecret")
    getGrantType = "client_credentials"
    refreshGrantType = "refresh_token"
    scope = "read"


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OauthToken, cls).__new__(cls)
        return cls.instance

    def getAccessToken(self) -> str:
        return self.accessToken


    def setAccessToken(self, tokens) -> None:
        self.accessToken = tokens['access_token']


    def setTokens(self, tokens) -> None:
        self.accessToken = tokens['access_token']
        self.refreshToken = tokens['refresh_token']


    async def getRefreshToken(self):
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.clientId,
                    "client_secret": self.clientSecret,
                    "scope": self.scope,
                    "grant_type": self.refreshGrantType
                }
                async with session.post(self.tokenUrl, data = data) as response:
                    if response .status == 200:
                        answer = json.loads(await response.text())
                        self.setToken(answer)
        except (asyncio.TimeoutError, aiohttp.ClientError) as ex:
            logging.error(f"Failed connection to refresh auth token: {ex}")


    async def getToken(self):
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.clientId,
                    "client_secret": self.clientSecret,
                    "scope": self.scope,
                    "grant_type": self.getGrantType
                }
                async with session.post(self.tokenUrl, data = data) as response:
                    if response.status == 200:
                        responseData = await response.text()
                        answer = json.loads(responseData)
                        self.setAccessToken(answer)
        except (asyncio.TimeoutError, aiohttp.ClientError) as ex:
            logging.error(f"Failed connection to refresh auth token: {ex}")


    def getHeader(self):
        return {
            'Authorization': f'Bearer {self.accessToken}',
            'Accept': 'application/vnd.assignr.v2.hal+json'
        }
