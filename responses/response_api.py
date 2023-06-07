import json
import time
import aiohttp



from functools import wraps
from dataclasses import dataclass
from vk_geo_parser.telegram_logs.tg_logs import catch_log
from vk_geo_parser.exceptions.exceptions import VKAPIException


@dataclass
class RequestAPIAttachment:
    """ Represents vk.ru API handler for attachment. """

    coordinates: str
    publications: int
    radius: int
    token: str
    country_id: int
    region_id: int
    city_id: int

    def __call__(self, func):
        @wraps(func)
        async def wrapper(**kwargs):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f'https://api.vk.com/method/photos.search?'
                                        f'lat={str(self.coordinates).split(",")[0]}&'
                                        f'long={str(self.coordinates).split(",")[1]}&count={self.publications}&'
                                        f'v=5.131&access_token={self.token}&radius={self.radius}&'
                                        f'start_time={int(time.time()) - 84000}&end_time={int(time.time())}') as response:

                        # Converting response to text data
                        response_json = await response.text()

                        # Converting response to JSON data
                        response_json = json.loads(response_json)

                        await check_errors(response_json)

                        result = await func(self, response=response_json, **kwargs)

            except VKAPIException as v:
                catch_log(str(v), level='ERROR')
            else:
                return result

        return wrapper


@dataclass
class RequestAPIResource:
    """ Represents VK API for resources. """

    owners_ids: str
    token: str

    async def __call__(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f'https://api.vk.com/method/users.get?user_ids={self.owners_ids}&'
                                     f'v=5.131&access_token={self.token}&'
                                     f'fields=crop_photo,screen_name,followers_count') as response:

                    # Converting response to text
                    response_json = await response.text()

                    # Converting response to JSON
                    response_json = json.loads(response_json)

                    await check_errors(response_json)

                    return response_json

        except VKAPIException as v:
            catch_log(str(v), level='ERROR')


async def check_errors(response_json):
    if response_json.get('error'):
        error_code = response_json['error']['error_code']
        log = str(VKAPIException(error_code))
        catch_log(log, level='ERROR')