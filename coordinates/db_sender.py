import asyncio

from vk_geo_parser.database.database import temp_db


async def send_data():
    with open('test_city.txt', 'r') as file:
        res = [x.strip().split(',', maxsplit=4) + [1 , 1, '1970-01-01 01:01:01'] for x in file.readlines()]
        await temp_db.insert_into_vk_locations_info('vk_locations_info', [x for x in res if x[1] == '57'])


asyncio.run(send_data())