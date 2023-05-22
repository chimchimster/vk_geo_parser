import asyncio
import os
from parser import ParseData
from vk_geo_parser.responses.response_api import RequestAPI


coordinates = [('55.733647398995075', '37.61603658440511'), ('55.168822388426136', '61.4167578224923'), ('21.15839201715473', '79.05503789744886')]
vk_token = os.environ.get('VK_TOKEN')


def manage_number_of_queries(number: int = 3):
    """ Determines how many queries
        should be in one flow and
        then creates them. """

    def create_class_names() -> list:
        """ :returns: list of class_names
            for queries based on given number. """

        number_list = ['Query' + str(num) for num in range(1, number+1)]

        return number_list

    def create_query_objects():
        """ Creates objects which will
            decorate dynamic classes. """

        return [RequestAPI(coordinates[i], 100, 6000, vk_token) for i in range(number)]

    class_names = create_class_names()
    query_objects = create_query_objects()

    # Dynamic class creation
    for number, class_name in enumerate(class_names):
        globals()[class_name] = type(class_name, (ParseData,), {
            'fill_collection': query_objects[number](ParseData.fill_collection),
        })

    print(f'I have successfully created {len(class_names)} classes')


manage_number_of_queries()

async def fill():
    query_classes = {query_class_name: query_class_value for (query_class_name, query_class_value) in globals().items()
                     if query_class_name.startswith('Query')}

    await asyncio.gather(
        *(query.fill_collection() for query in query_classes.values())
    )


asyncio.run(fill())