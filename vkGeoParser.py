import json
from datetime import datetime
from copy import deepcopy
import requests
from typing import NewType

response_js = NewType('response_js', json)

class LocationParser:
    """ Class which parses data from vk.ru via API. """

    def __init__(self,
                 query: str,
                 token: str,
                 coordinates: tuple | list,
                 publications: int = 100) -> None:
        self.query = query
        self.token = token
        self.coordinates = coordinates
        self.publications = publications
        self.collection = None

    def response_api_photo(self) -> response_js:
        response = requests.post(f'https://api.vk.com/method/photos.search?lat={self.coordinates[0]}&'
                                 f'long={self.coordinates[1]}&count={self.publications}&'
                                 f'v=5.131&access_token={self.token}&radius=800')

        # Converting response to JSON data
        response_json = json.loads(response.text)

        return response_json

    def generate_slugs(self):
        collection = []

        response = self.response_api_photo()

        for data in response['response']['items']:

            if 'post_id' in data:
                collection.append(str(data['owner_id']) + '_' + str(data['post_id']))
            else:
                collection.append(str(data['owner_id']) + '_' + str(data['id']))

        return collection

    def form_collection(self) -> None:
        """ Method which forms a collection to send it into database.

            :returns: collection (list). """

        # Initialize collection to send
        collection = []

        response_json = self.response_api_photo()

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
                    try:
                        link = f'https://vk.com/id{owner_id_link}?z=photo{owner_id_link}_{item_id}'
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

            self.collection = collection

    def update_text_field_on_valid(self) -> None:
        """ Since parsing by geo is only available using photos
            we can't be sure that all posts would include text filed.

            To ensure that we must send another API request to vk.com
            using specific method :wall.getById: """

        posts = ','.join(self.generate_slugs())
        print(posts)
        response = requests.post(f'https://api.vk.com/method/wall.getById?posts={posts}&'
                                 f'v=5.131&access_token={self.token}&')

        response_json = json.loads(response.text)

        for data in response_json['response']:
            print(data)


l = LocationParser('Рудный',
                   '',
                   ('55.19319090327282', '61.36051174894654'),
                   200)
# print(l.generate_slugs())

l.form_collection()
# l.update_text_field_on_valid()
for tp in l.collection:
    print(tp, end='\n')
