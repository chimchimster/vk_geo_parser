import json
from datetime import datetime

import requests

from typing import Optional, Tuple, List


class LocationParser:
    """ Class which parses data from Vkontakte.ru via API """

    def __init__(self,
                 query: Optional[str],
                 token: Optional[str],
                 coordinates: Optional[Tuple],
                 publications: Optional[int] = 100) -> None:
        self.query = query
        self.token = token
        self.coordinates = coordinates
        self.publications = publications

    def form_collection(self) -> Optional[List]:
        """ Method which forms a collection to send it into database.

            :returns: collection (list). """

        # Initialize collection to send
        collection = []

        response = requests.post(f'https://api.vk.com/method/newsfeed.search?lat={self.coordinates[0]}&'
                                 f'long={self.coordinates[1]}&count={self.publications}&'
                                 f'v=5.131&q={self.query}&access_token={self.token}')

        # Converting response to JSON data
        response_json = json.loads(response.text)

        for data in response_json['response']['items']:

            if data['owner_id'] < 0:
                link = 'https://vk.com/wall-' + str(data['owner_id'])[1:] + '_' + str(data['id'])
            else:
                link = 'https://vk.com/wall-' + str(data['owner_id']) + '_' + str(data['id'])

            collection.append((
                # In DB owner_id
                data['owner_id'],
                # In DB from_id
                data['from_id'],
                # In DB post_id
                str(data['from_id']) + '_' + str(data['id']),
                # In DB res_id
                100000,
                # In DB title
                '',
                # In DB text
                data['text'],
                # Timestamp in seconds (in DB date)
                data['date'],
                # Timestamp in human-readable format (in DB s_date)
                datetime.utcfromtimestamp(data['date']).strftime('%Y-%m-%d %H:%M:%S'),
                # Timestamp in human-readable format excluded part (in DB not date)
                datetime.utcfromtimestamp(data['date']).strftime('%Y-%m-%d'),
                # Post's link
                link,
                # In DB from_type
                0,
                # In DB lang
                0,
                # In DB sentiment
                None,
                # In DB type,
                4,
                # In DB sphinx status
                '',
            ))

        return collection


l = LocationParser(' ',
                   '',
                   ('52.95492580356618', '63.082937712252765'),
                   100)
print(l.form_collection())
