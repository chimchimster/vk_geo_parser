import asyncio
import os
from copy import deepcopy
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from vk_geo_parser.database.database import temp_db
from vk_geo_parser.custom_types.custom_types import response_js
from vk_geo_parser.responses.response_api import RequestAPI

load_dotenv()
vk_token = os.environ.get('VK_TOKEN')

lst = [('55.733647398995075', '37.61603658440511'), ('55.168822388426136', '61.4167578224923'), ('21.15839201715473', '79.05503789744886')]

query1 = RequestAPI(lst[0], 100, 6000, vk_token)
query2 = RequestAPI(lst[1], 100, 6000, vk_token)
query3 = RequestAPI(lst[2], 100, 6000, vk_token)


class ParseData:
    """ Class which represents main parser. """

    async def fill_collection(*args, **kwargs):
        # Retrieving response from kwargs
        response_json = kwargs.pop('response')

        # Collection for temp_posts
        collection = []

        for data in response_json['response']['items']:
            if 'post_id' in data:
                collection.append(
                    Post(data).generate_post()
                )

        print(collection)
        return collection


class Post:
    def __init__(self, data: response_js) -> None:
        self._data = data

    def generate_post(self) -> tuple:
        """ Generates post based on response. """

        # In DB owner_id and from_id
        owner_id = from_id = self._data['owner_id']

        # In DB item_id
        item_id = self._data['id']

        # In DB res_id
        res_id = None

        # In DB title
        title = None

        # In DB text
        text = self._data['text']

        # In DB date
        date = self._data['date']

        # In DB s_date
        s_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

        # In DB not_date
        not_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')

        owner_id_link = self.__lead_link_to_unique_format(owner_id)

        link = ''
        try:
            # In DB link
            link = f'https://vk.com/id{owner_id_link}?w=wall{owner_id_link}_{self._data["post_id"]}'
        except:
            pass

        post_id = ''
        try:
            post_id = self._data['post_id']
        except:
            pass

        # In DB from_type
        from_type = 3

        # In DB lang
        lang = 0

        # In DB sentiment
        sentiment = None

        # In DB type
        _type = 1

        # In DB sphinx_status
        sphinx_status = None

        return owner_id, from_id, item_id, res_id, title, text, date, s_date,\
            not_date, link, from_type, lang, sentiment, sphinx_status, post_id

    def check_if_res_id_already_in_db(self, func):
        @wraps
        def wrapper():

            result = func()

            if not result:
                try:
                    temp_db.insert_res_id('resource_social_ids', self._data['owner_id'])

                    return temp_db.get_res_id('resource_social_ids', self._data['owner_id'])
                except Exception as e:
                    print(e)
            else:
                return result

        return wrapper

    @check_if_res_id_already_in_db
    def get_res_id(self):

        return temp_db.get_res_id('resource_social_ids', self._data['owner_id'])


    @staticmethod
    def __lead_link_to_unique_format(_owner_id) -> str:
        """ Method which leads owner_id in link to unique format.

            :returns: owner_id (str). """

        # Since we should form links in a unique appearance
        # lets create deepcopy of owner_id object
        owner_id_copy = str(deepcopy(_owner_id))

        if owner_id_copy.startswith('-'):
            return owner_id_copy[1:]

        return owner_id_copy





