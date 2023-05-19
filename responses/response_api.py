import json
import requests

from functools import wraps
from dataclasses import dataclass
from vk_geo_parser.exceptions.exceptions import VKAPIException


@dataclass
class RequestAPI:
    """ Represents vk.ru API handler. """

    coordinates: tuple
    publications: int
    radius: int
    token: str

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                response = requests.post(f'https://api.vk.com/method/photos.search?lat={self.coordinates[0]}&'
                              f'long={self.coordinates[1]}&count={self.publications}&'
                              f'v=5.131&access_token={self.token}&radius={self.radius}')

                # Converting response to JSON data
                response_json = json.loads(response.text)

                result = func(self, response=response_json, **kwargs)

            except VKAPIException as v:
                print(v)
            else:
                return result

        return wrapper
