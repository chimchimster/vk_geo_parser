import asyncio
import os
from copy import deepcopy
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from vk_geo_parser.database.database import temp_db
from vk_geo_parser.responses.response_api import RequestAPI
from vk_geo_parser.custom_types.custom_types import response_js

load_dotenv()
vk_token = os.environ.get('VK_TOKEN')

lst = [('55.733647398995075', '37.61603658440511'), ('55.168822388426136', '61.4167578224923'), ('21.15839201715473', '79.05503789744886')]

query1 = RequestAPI(lst[0], 100, 6000, vk_token)
query2 = RequestAPI(lst[1], 100, 6000, vk_token)
query3 = RequestAPI(lst[2], 100, 6000, vk_token)


class ParseData:
    """ Class which represents main parser. """

    async def fill_collection(self, *args, **kwargs):
        # Retrieving response from kwargs
        response_json = kwargs.pop('response')

        collection_for_temp_posts = []
        collection_for_attachments = []

        for data in response_json['response']['items']:
            if 'post_id' in data:
                post = await Post(data).generate_post()
                collection_for_temp_posts.append(
                    post[0],
                )
                collection_for_attachments.append(
                    post[1],
                )

        await temp_db.insert_into_temp_posts('temp_posts', collection_for_temp_posts)
        await temp_db.insert_into_attachment('temp_attachments', collection_for_attachments)


class Post:
    def __init__(self, data: response_js) -> None:
        self._data = data

    async def generate_post(self) -> tuple:
        """ Generates post based on response. """

        # In DB temp_posts: owner_id and from_id
        owner_id = from_id = self._data['owner_id']

        # In DB temp_posts: item_id
        item_id = self._data['id']

        # In DB temp_posts: res_id
        res_id = await self.get_res_id(self._data)

        # In DB temp_posts: title
        title = ''

        # In DB temp_posts: text
        text = self._data['text']

        # In DB temp_posts: date
        date = self._data['date']

        # In DB temp_posts: s_date
        s_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

        # In DB temp_posts: not_date
        not_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')

        owner_id_link = self.__lead_link_to_unique_format(owner_id)

        link = ''
        try:
            # In DB temp_posts: link
            link = f'https://vk.com/id{owner_id_link}?w=wall{owner_id_link}_{self._data["post_id"]}'
        except:
            pass

        # In DB temp_posts: from_type
        from_type = 3

        # In DB lang
        lang = 0

        # In DB temp_posts: sentiment
        sentiment = None

        # In DB type
        _type = 1

        # In DB temp_posts: sphinx_status
        sphinx_status = 0

        # In DB temp_attachments: post_id
        post_id = self._data['id']

        # In DB temp_attachments: attachment
        attachment = self._data['sizes'][-1]['url']

        # In DB temp_attachments: type
        attachment_type = 1

        # In DB temp_attachments: status
        status = ''

        return (owner_id, from_id, item_id, res_id, title, text, date, s_date,
            not_date, link, from_type, lang, sentiment, _type, sphinx_status,),\
            (post_id, attachment, attachment_type, owner_id, from_id, item_id, status)

    @staticmethod
    def check_if_res_id_already_in_db(func):
        @wraps(func)
        async def wrapper(_data):

            result = await func(_data)

            if not result:
                try:
                    await temp_db.insert_res_id('resource_social_ids', _data['owner_id'])

                    return await temp_db.get_res_id('resource_social_ids', _data['owner_id'])
                except Exception as e:
                    print(e)
            else:
                return result

        return wrapper

    @staticmethod
    @check_if_res_id_already_in_db
    async def get_res_id(_data):

        return await temp_db.get_res_id('resource_social_ids', _data['owner_id'])

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