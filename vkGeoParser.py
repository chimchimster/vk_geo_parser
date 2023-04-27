import os
from dotenv import load_dotenv
from datetime import datetime
from copy import deepcopy
from responses.response_api import ResponseAPI
from parser.parser import ParseData
import asyncio










async def main():
    await asyncio.gather(
        ParseData.fill_collection(),
        ParseData.fill_collection(),
        ParseData.fill_collection(),
    )

asyncio.run(main())