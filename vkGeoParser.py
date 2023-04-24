import json
from datetime import datetime

import requests

from typing import Optional, Tuple, List


class LocationParser:
    """ Class which parses data from vk.ru via API. """

    def __init__(self,
                 query: str,
                 token: str,
                 coordinates: Optional[Tuple],
                 publications: int = 100) -> None:
        self.query = query
        self.token = token
        self.coordinates = coordinates
        self.publications = publications

    def form_collection(self) -> Optional[List]:
        """ Method which forms a collection to send it into database.

            :returns: collection (list). """

        # Initialize collection to send
        collection = []

        response = requests.post(f'https://api.vk.com/method/photos.search?q={self.query}&lat={self.coordinates[0]}&'
                                 f'long={self.coordinates[1]}&count={self.publications}&'
                                 f'v=5.131&access_token={self.token}&radius=6000')

        # Converting response to JSON data
        response_json = json.loads(response.text)

        for data in response_json['response']['items']:

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

            link = ''
            try:
                # In DB link
                link = f'https://vk.com/id{owner_id}?w=wall{owner_id}_{data["post_id"]}'
            except:
                try:
                    link = f'https://vk.com/id{owner_id}?z=photo{owner_id}_{item_id}'
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
            ))

        return collection


l = LocationParser('Рудный',
                   '',
                   ('52.9715299537596', '63.1037051905467'),
                   200)
print(l.form_collection())
