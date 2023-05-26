import asyncio
import os
import time
from copy import deepcopy
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from vk_geo_parser.database.database import temp_db, temp_db_ch
from vk_geo_parser.responses.response_api import RequestAPIResource


load_dotenv()
vk_token = os.environ.get('VK_TOKEN')


class ParseData:
    """ Class which represents main parser. """

    coordinates = None
    country_id = None
    region_id = None
    city_id = None

    async def fill_collection(self, *args, **kwargs):
        # Retrieving response from kwargs
        response_json = kwargs.pop('response')

        global collection_of_owners_ids_for_resources

        collection_for_temp_posts = []
        collection_for_attachments = []
        collection_of_owners_ids_for_resources = set()

        async def send_to_resources():
            result = await RequestAPIResource(','.join(map(str, collection_of_owners_ids_for_resources)), vk_token)()

            result = [(await temp_db.get_res_id('resource_social_ids', lst['id']),
                       self.country_id, self.region_id, self.city_id,
                       # In DB resource_social: resource_name
                       lst['first_name'] if 'first_name' in lst else '' + ' ' + lst['last_name'] if 'last_name' in lst else '',
                       # In DB link
                       f'https://vk.com/id{Post.lead_link_to_unique_format(lst["id"])}',
                       # In DB resource_social: screen name
                       lst['screen_name'] if 'screen_name' in lst else '',
                       # In DB resource_social: type, stability
                       1, 0,
                       # In DB resource_social: image profile
                       lst['crop_photo']['photo']['sizes'][-1]['url'] if 'crop_photo' in lst else '',
                       # In DB resource_social: s_id
                       str(lst['id']),
                       # In DB resource_social: start_date_imas
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       # In DB resource_social: members,
                       lst['followers_count'],
                       # In DB resource_social: info check
                       1,
                       # In DB datetime_enable
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       # In DB resource_social: worker
                       4,
                       ) for lst in result['response']]

            await temp_db_ch.insert_into_resource_social('resource_social', result)

        async def append_data(collection: list, _post):
            collection.append(_post)

        for data in response_json['response']['items']:
            post = await Post(data).generate_post()

            if post[0]:
                await append_data(collection_for_temp_posts, post[0])
                await append_data(collection_for_attachments, post[1])

        if collection_of_owners_ids_for_resources:
            await send_to_resources()

        if collection_for_temp_posts:
            await temp_db.insert_into_temp_posts('temp_posts', collection_for_temp_posts)
            await temp_db.insert_into_attachment('temp_attachments', collection_for_attachments)

        await temp_db.update_coordinates_last_update_field('vk_locations_info', self.coordinates)


class Post:
    def __init__(self, data) -> None:
        self._data = data
        self._coordinates = None

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

        owner_id_link = self.lead_link_to_unique_format(owner_id)

        if 'post_id' in self._data:
            # In DB temp_posts: link
            link = f'https://vk.com/id{owner_id_link}?w=wall{owner_id_link}_{self._data["post_id"]}'
        else:
            link = f'https://vk.com/photo{owner_id}_{item_id}'

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

                    collection_of_owners_ids_for_resources.add(_data['owner_id'])
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
    def lead_link_to_unique_format(_owner_id) -> str:
        """ Method which leads owner_id in link to unique format.

            :returns: owner_id (str). """

        # Since we should form links in a unique appearance
        # lets create deepcopy of owner_id object
        owner_id_copy = str(deepcopy(_owner_id))

        if owner_id_copy.startswith('-'):
            return owner_id_copy[1:]

        return owner_id_copy