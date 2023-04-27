import os
from dotenv import load_dotenv
from datetime import datetime
from copy import deepcopy
from responses.response_api import ResponseAPI

import asyncio


load_dotenv()

vk_token = os.environ.get('VK_TOKEN')


resAPI = ResponseAPI(('55.733647398995075', '37.61603658440511'), 100, 6000, vk_token)


class ParseData:
    """ Class which represents main parser. """

    @resAPI
    async def fill_collection(*args, **kwargs):
        response_json = kwargs.pop('response')

        collection = []

        def lead_link_to_unique_format(_owner_id) -> str:
            """ Method which leads owner_id in link to unique format.

                :returns: owner_id (str). """

            # Since we should form links in a unique appearance
            # lets create deepcopy of owner_id object
            owner_id_copy = str(deepcopy(_owner_id))

            if owner_id_copy.startswith('-'):
                return owner_id_copy[1:]

            return owner_id_copy

        for data in response_json['response']['items']:
            if 'post_id' in data:
                # In DB owner_id and from_id
                owner_id = from_id = data['owner_id']

                # In DB item_id
                item_id = data['id']

                # In DB res_id
                res_id = None

                # In DB title
                title = None

                # In DB text
                text = data['text']

                # In DB date
                date = data['date']

                # In DB s_date
                s_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

                # In DB not_date
                not_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')

                owner_id_link = lead_link_to_unique_format(owner_id)

                link = ''
                try:
                    # In DB link
                    link = f'https://vk.com/id{owner_id_link}?w=wall{owner_id_link}_{data["post_id"]}'
                except:
                    pass

                post_id = ''
                try:
                    post_id = data['post_id']
                except:
                    pass

                # In DB from_type
                from_type = 6

                # In DB lang
                lang = 0

                # In DB sentiment
                sentiment = None

                # In DB type
                _type = 5

                # In DB sphinx_status
                sphinx_status = None

                collection.append((
                    owner_id,
                    from_id,
                    item_id,
                    res_id,
                    title,
                    text,
                    date,
                    s_date,
                    not_date,
                    link,
                    from_type,
                    lang,
                    sentiment,
                    _type,
                    sphinx_status,
                    post_id,
                ))

        print(collection)


async def main():
    await asyncio.gather(
        ParseData.fill_collection(),
        ParseData.fill_collection(),
        ParseData.fill_collection(),
    )

asyncio.run(main())