import json
import time

import requests

from functools import wraps
from dataclasses import dataclass
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
        def wrapper(**kwargs):
            try:
                print(str(self.coordinates).split(",")[0], str(self.coordinates).split(",")[1])
                response = requests.post(f'https://api.vk.com/method/photos.search?'
                                         f'lat={str(self.coordinates).split(",")[0]}&'
                                         f'long={str(self.coordinates).split(",")[1]}&count={self.publications}&'
                                         f'v=5.131&access_token={self.token}&radius={self.radius}&',
                                         f'start_time={int(time.time()) - 84000}&end_time={int(time.time())}',
                                         timeout=(5.0, 30.0))

                # Converting response to JSON data
                response_json = json.loads(response.text)

                result = func(self, response=response_json, **kwargs)

            except VKAPIException as v:
                print(v)
            else:
                return result

        return wrapper


@dataclass
class RequestAPIResource:
    """ Represents VK API for resources. """

    owners_ids: str
    token: str

    async def __call__(self):
        response = requests.post(f'https://api.vk.com/method/users.get?user_ids={self.owners_ids}&'
                                 f'v=5.131&access_token={self.token}&fields=crop_photo,screen_name,followers_count')

        response_json = json.loads(response.text)

        return response_json
