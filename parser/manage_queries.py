import asyncio
import os
from parser import ParseData
from vk_geo_parser.responses.response_api import RequestAPIAttachment
from vk_geo_parser.database.database import temp_db


vk_token = os.environ.get('VK_TOKEN')


async def get_coordinates():
    """ Getting coordinates from database. """

    result = await temp_db.get_coordinates('vk_locations_info', 3)

    return result


async def manage_number_of_queries(number: int = 3):
    """ Determines how many queries
        should be in one flow and
        then creates them. """

    coordinates = await get_coordinates()

    def create_class_names() -> list:
        """ :returns: list of class_names
            for queries based on given number. """

        number_list = ['Query' + str(num) for num in range(1, number+1)]

        return number_list

    async def create_query_objects():
        """ Creates objects which will
            decorate dynamic classes. """

        return [RequestAPIAttachment(coordinates[i][0], 1000, 6000, vk_token) for i in range(number)]

    class_names = create_class_names()
    query_objects = await create_query_objects()

    # Dynamic class creation
    for number, class_name in enumerate(class_names):
        globals()[class_name] = type(class_name, (ParseData,), {
            'fill_collection': query_objects[number](ParseData.fill_collection),
            'coordinates': coordinates[number][0],
        })

    print(f'I have successfully created {len(class_names)} classes')


async def fill():
    await manage_number_of_queries()

    query_classes = {query_class_name: query_class_value for (query_class_name, query_class_value) in globals().items()
                     if query_class_name.startswith('Query')}

    await asyncio.gather(
        *(query.fill_collection() for query in query_classes.values())
    )


asyncio.run(fill())