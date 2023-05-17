import os
from parser import ParseData
from vk_geo_parser.responses.response_api import ResponseAPI
from parser import query1


lst = [('55.733647398995075', '37.61603658440511'), ('55.168822388426136', '61.4167578224923'), ('21.15839201715473', '79.05503789744886')]
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

        return [ResponseAPI(lst[i], 100, 6000, vk_token) for i in range(len(lst))]

    query_objects = create_query_objects()

    # Dynamic class creation
    for number, class_name in enumerate(create_class_names()):
        globals()[class_name] = type(class_name, (ParseData,), {
            'fill_collection': query_objects[number](ParseData.fill_collection),
        })


manage_number_of_queries()
print(Query1.fill_collection())

