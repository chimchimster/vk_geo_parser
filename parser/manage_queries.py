import asyncio
import os
import random
import string
import time

from parser import ParseData
from vk_geo_parser.responses.response_api import RequestAPIAttachment
from vk_geo_parser.database.database import temp_db


vk_token = os.environ.get('VK_TOKEN')


class DataManager:
    """ Distributes coordinates between
        dynamically created classes. """

    async def __get_coordinates(self) -> tuple:
        return await temp_db.get_coordinates('vk_locations_info')

    async def __get_tokens(self) -> list:
        return os.environ.get('VK_TOKEN').split(',')

    async def merge_coordinates_and_tokens(self):
        start = 0
        coordinates = await self.__get_coordinates()

        tokens = await self.__get_tokens()

        shifter_coordinates, shifter_tokens = 0, 0
        merged = []
        while start < len(coordinates):
            if shifter_tokens == len(tokens):
                shifter_tokens = 0

            merged.append((coordinates[shifter_coordinates:shifter_coordinates+3], tokens[shifter_tokens]))
            shifter_coordinates += 3
            shifter_tokens += 1
            start += 3

        return merged


async def manage_number_of_queries(coordinates, number: int = 3):
    """ Determines how many queries
        should be in one flow and
        then creates them. """

    def create_class_names() -> list:
        """ :returns: list of class_names
            for queries based on given number. """

        def random_string(length):
            pool = string.ascii_letters + string.digits
            return ''.join(random.choice(pool) for i in range(length))

        number_list = ['Query' + random_string(64) + str(num) for num in range(1, number+1)]

        return number_list

    async def create_query_objects():
        """ Creates objects which will
            decorate dynamic classes. """

        return [RequestAPIAttachment(coordinates[0][i][0], 1000, 6000, coordinates[1],
                                     coordinates[0][i][1], coordinates[0][i][2], coordinates[0][i][3]) for i in range(number)]

    class_names = create_class_names()
    query_objects = await create_query_objects()

    # Dynamic class creation
    for number, class_name in enumerate(class_names):
        globals()[class_name] = type(class_name, (ParseData,), {
            'fill_collection': query_objects[number](ParseData.fill_collection),
        })

    print(f'I have successfully created {len(class_names)} classes')


async def fill(obj):
    await manage_number_of_queries(obj)

    query_classes = {query_class_name: query_class_value for (query_class_name, query_class_value) in globals().items()
                     if query_class_name.startswith('Query')}

    await asyncio.gather(
        *(query.fill_collection() for query in query_classes.values())
    )


async def launch_tree():
    objects = await DataManager().merge_coordinates_and_tokens()

    for obj in objects:
        try:
            await fill(obj)
        except Exception as e:
            print(e)

asyncio.run(launch_tree())
