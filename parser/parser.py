import asyncio
import os
from copy import deepcopy
from functools import wraps
from datetime import datetime

from vk_geo_parser.database.database import imas_db, imas_ch, social_services_db
from vk_geo_parser.responses.response_api import RequestAPIResource
from vk_geo_parser.statistics_manager.statistics import StatisticsManager

statistics_manager = StatisticsManager()


class ParseData:
    """ Class which represents main parser. """

    coordinates = None
    country_id = None
    region_id = None
    city_id = None

    async def fill_collection(self, **kwargs):
        # Retrieving response from kwargs
        response_json = kwargs.pop('response')

        collection_for_temp_posts = []
        collection_for_attachments = []

        async def append_data(collection: list, _post):
            collection.append(_post)

        if response_json.get('response'):
            for data in response_json['response']['items']:
                post = await Post(data, self.country_id, self.city_id, self.region_id, os.environ.get('vk_token')).generate_post()

                if post is not None and post[0]:
                    await append_data(collection_for_temp_posts, post[0])
                    await append_data(collection_for_attachments, post[1])

        if collection_for_temp_posts:
            await imas_db.insert_into_temp_posts('temp_posts', collection_for_temp_posts)
            await imas_db.insert_into_attachment('temp_attachments', collection_for_attachments)
            statistics_manager.update_statistics(temp_posts=len(collection_for_temp_posts))
            statistics_manager.update_statistics(temp_attachments=len(collection_for_attachments))
        else:
            statistics_manager.update_statistics(temp_posts=len(collection_for_temp_posts))
            statistics_manager.update_statistics(temp_attachments=len(collection_for_attachments))

        await social_services_db.update_coordinates_last_update_field('vk_locations_info', self.coordinates)


class Post:
    def __init__(self, data, country_id, region_id, city_id, token) -> None:
        self._data = data
        self.country_id = country_id
        self.region_id = region_id
        self.city_id = city_id
        self.token = token
        self._coordinates = None

    async def generate_post(self) -> tuple:
        """ Generates post based on response. """

        if self._data['owner_id'] > 0:
            # In DB temp_posts: owner_id and from_id
            owner_id = from_id = self._data['owner_id']

            # In DB temp_posts: item_id
            item_id = self._data['id']

            # In DB temp_posts: res_id
            res_id = await self.get_res_id(self._data, self.country_id, self.region_id, self.city_id, self.token)

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

            # In DB temp_posts: lang
            lang = 0

            # In DB temp_posts: sentiment
            sentiment = None

            # In DB type
            _type = 1

            # In DB temp_posts: sphinx_status
            sphinx_status = ''

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
        async def wrapper(_data, *args, **kwargs):

            result = await func(_data)

            if not result:
                try:
                    if _data['owner_id'] > 0:
                        await social_services_db.insert_res_id('resource_social_ids', _data['owner_id'])

                        queue = asyncio.Queue()

                        async def send_to_resources():

                            async def get_all_items_from_queue():
                                async def add_item(item):
                                    items.append(item)

                                items = []

                                while not queue.empty():
                                    item = await queue.get()
                                    await add_item(item)

                                return items

                            collection_of_owners_ids_for_resources = await get_all_items_from_queue()

                            result = await RequestAPIResource(
                                ','.join(map(str, collection_of_owners_ids_for_resources)),args[3]
                            )()

                            if result.get('response'):
                                result = [(await social_services_db.get_res_id('resource_social_ids', lst['id']),
                                           args[0], args[1], args[2],
                                           # In DB resource_social: resource_name
                                           lst['first_name'] if 'first_name' in lst else '' + ' ' + lst[
                                               'last_name'] if 'last_name' in lst else '',
                                           # In DB link
                                           f'https://vk.com/id{Post.lead_link_to_unique_format(lst["id"])}',
                                           # In DB resource_social: screen name
                                           lst['screen_name'] if 'screen_name' in lst else '',
                                           # In DB resource_social: type, stability
                                           1, 0,
                                           # In DB resource_social: image profile
                                           lst['crop_photo']['photo']['sizes'][-1][
                                               'url'] if 'crop_photo' in lst else '',
                                           # In DB resource_social: s_id
                                           str(lst['id']),
                                           # In DB resource_social: start_date_imas
                                           datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           # In DB resource_social: members,
                                           lst['followers_count'],
                                           # In DB resource_social: info check
                                           6,
                                           # In DB datetime_enable
                                           datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           # In DB resource_social: worker
                                           4,
                                           ) for lst in result['response']]

                                if result:
                                    await imas_ch.insert_into_resource_social('resource_social', result)
                                    statistics_manager.update_statistics(resource_social=queue.qsize())

                        await send_to_resources()

                        await asyncio.sleep(1)

                        return await social_services_db.get_res_id('resource_social_ids', _data['owner_id'])
                except Exception as e:
                    print(e)
            else:
                return result

        return wrapper

    @staticmethod
    @check_if_res_id_already_in_db
    async def get_res_id(_data, *args):

        return await social_services_db.get_res_id('resource_social_ids', _data['owner_id'])

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