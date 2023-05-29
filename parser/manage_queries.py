import os
import random
import string
import asyncio

from parser import ParseData
from vk_geo_parser.database.database import temp_db
from vk_geo_parser.responses.response_api import RequestAPIAttachment

vk_token = os.environ.get('VK_TOKEN')


class Query:

    def __init__(self, coordinates, token):
        self.coordinates = coordinates
        self.token = token

    async def manage_number_of_queries(self, number: int = 3):
        """ Determines how many queries
            should be in one flow and
            then creates them. """

        def create_class_names() -> list:
            """ :returns: list of class_names
                for queries based on given number. """

            def random_string(length):
                """ Generates random string for queries class names. """

                pool = string.ascii_letters + string.digits
                return ''.join(random.choice(pool) for i in range(length))

            number_list = ['Query_' + random_string(64) + str(num) for num in range(1, number + 1)]

            return number_list

        async def create_query_objects():
            """ Creates objects which will
                decorate dynamic classes. """

            return [RequestAPIAttachment(self.coordinates[i][0], 1000, 50000, self.token,
                    self.coordinates[i][1], self.coordinates[i][2], self.coordinates[i][3])
                    for i in range(number)]

        class_names = create_class_names()
        query_objects = await create_query_objects()

        # Dynamic class creation
        for number, class_name in enumerate(class_names):
            globals()[class_name] = type(class_name, (ParseData,), {
                'fill_collection': query_objects[number](ParseData.fill_collection),
            })

        print(f'I have successfully created {len(class_names)} classes')

    async def __call__(self, *args, **kwargs):
        await self.manage_number_of_queries(len(self.coordinates))


class DataManagerDescriptor:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if isinstance(instance, DataManager):
            setattr(instance, self.name, value)
        else:
            raise TypeError('Manager must be a DataManager type!')


class DataManager:
    """ Distributes coordinates between
        dynamically created classes. """

    async def __get_coordinates(self) -> tuple:
        return await temp_db.get_coordinates('vk_locations_info')

    async def __get_tokens(self) -> list:
        return os.environ.get('VK_TOKEN').split(',')

    async def merge_coordinates_and_tokens(self):
        coordinates = await self.__get_coordinates()

        tokens = await self.__get_tokens()

        # Since vk allows only 3 queries to its API
        delimiter = 3

        lst = []
        for start in range(0, len(coordinates), delimiter):
            lst.append(coordinates[start:delimiter + start])

        tokens_list = tokens * len(lst)

        return list(zip(lst, tokens_list))


class QueryTasks:
    manager = DataManagerDescriptor()

    def __init__(self, manager):
        self._manager = manager

    async def apply_queries(self):
        queries_data = await self._manager.merge_coordinates_and_tokens()
        queries_objects = [Query(*data) for data in queries_data]

        await asyncio.gather(
            *(query() for query in queries_objects)
        )


async def fill():

    manager = DataManager()
    query_tasks_manager = QueryTasks(manager)

    await query_tasks_manager.apply_queries()

    query_classes = {query_class_name: query_class_value for (query_class_name, query_class_value) in
                     globals().items() if query_class_name.startswith('Query_')}

    await asyncio.gather(
        *(query.fill_collection() for query in query_classes.values())
    )


if __name__ == '__main__':
    asyncio.run(fill())
