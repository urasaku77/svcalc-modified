import simpleobsws


class Obs(object):
    """
    OBSに対して行う操作に関するクラス
    """

    def __init__(self, loop, port, password):
        """
        接続を行う
        """
        url = "ws://[::1]:" + port
        parameters = simpleobsws.IdentificationParameters(
            ignoreNonFatalRequestChecks=False
        )
        self.ws = simpleobsws.WebSocketClient(
            url=url, password=password, identification_parameters=parameters
        )
        loop.run_until_complete(self.makeRequest())

    async def makeRequest(self):
        await self.ws.connect()
        await self.ws.wait_until_identified()

    async def breakRequest(self):
        await self.ws.disconnect()

    async def takeScreenshot(self, filename, source):
        request = simpleobsws.Request(
            "SaveSourceScreenshot",
            {
                "sourceName": source,
                "imageFormat": "jpg",
                "imageFilePath": filename,
                "imageWidth": 1920,
                "imageHeight": 1080,
                "imageCompressionQuality": 100,
            },
        )
        await self.ws.call(request)

    async def getScreenshot(self, source):
        request = simpleobsws.Request(
            "GetSourceScreenshot",
            {
                "sourceName": source,
                "imageFormat": "jpg",
                "imageWidth": 1920,
                "imageHeight": 1080,
                "imageCompressionQuality": 100,
            },
        )
        ret = await self.ws.call(request)
        if ret.ok():  # Check if the request succeeded
            return ret
        else:
            return
