import asyncio
import os

from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from vk_geo_parser.database.decorators import throw_params_db, throw_params_db_ch


@dataclass
class MySQLDataBase:
    """ Base class for each unique database connection. """

    _db_name: str

    async def insert_into_temp_posts(self, table_name: str, collection: tuple, *args, **kwargs) -> None:

        cursor = await self.retrieve_connection(kwargs)

        query = f"INSERT IGNORE INTO {self._db_name}.{table_name} (`owner_id`, `from_id`, `item_id`, `res_id`, " \
                f"`title`, `text`, `date`, `s_date`, `not_date`, `link`, `from_type`, `lang`, `sentiment`, `type`, " \
                f"`sphinx_status`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        if len(collection) > 1:
            await cursor.executemany(query, collection)
        elif len(collection) == 1:
            print(collection)
            await cursor.execute(query, collection[0])

    async def get_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> int | None:

        cursor = await self.retrieve_connection(kwargs)

        await cursor.execute(f"SELECT id FROM {self._db_name}.{table_name} WHERE s_id={s_id} AND type={_type}")

        res_id = await cursor.fetchone()

        if res_id:
            return res_id[0]
        else:
            return None

    async def insert_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> None:

        cursor = await self.retrieve_connection(kwargs)

        await cursor.execute(f"INSERT INTO {self._db_name}.{table_name} (type, s_id) VALUES ({_type},{s_id})")

    async def insert_into_attachment(self, table_name: str, collection: list, *args, **kwargs):

        cursor = await self.retrieve_connection(kwargs)

        query = f'INSERT INTO {self._db_name}.{table_name} (post_id, attachment, type, owner_id, from_id, item_id, ' \
                f'status) VALUES (%s,%s,%s,%s,%s,%s,%s)'

        if len(collection) > 1:
            await cursor.executemany(query, collection)
        else:
            print(collection)
            await cursor.execute(query, collection[0])

    async def get_coordinates(self, table_name: str, *args, **kwargs):

        cursor = await self.retrieve_connection(kwargs)

        query = f'SELECT coordinates, country_id, region_id, city_id FROM {self._db_name}.{table_name};'

        await cursor.execute(query)

        return await cursor.fetchall()

    async def update_coordinates_last_update_field(self, table_name: str, coordinates: str, *args, **kwargs):

        cursor = await self.retrieve_connection(kwargs)

        now = datetime.now()

        query = f'UPDATE {self._db_name}.{table_name} SET last_update = "{now}" WHERE coordinates = "{coordinates}";'

        await cursor.execute(query)

    async def get_coordinates_last_update_field(self, table_name: str, coordinates: str, *args, **kwargs):

        cursor = await self.retrieve_connection(kwargs)

        query = f'SELECT last_update FROM {self._db_name}.{table_name} WHERE coordinates = "{coordinates}";'

        await cursor.execute(query)

        return await cursor.fetchone()

    @staticmethod
    async def retrieve_connection(kwargs: dict):
        """ Retrieves connection from kwargs.

            :returns: MySQL DBMS cursor. """

        connection = kwargs.pop('connection')

        cursor = await connection.cursor()

        return cursor


class TestDB(MySQLDataBase):
    load_dotenv()

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def insert_into_temp_posts(self, table_name: str, collection: tuple, *args, **kwargs) -> None:
        await super().insert_into_temp_posts(table_name, collection, *args, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def get_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> int | None:
        return await super().get_res_id(table_name, s_id, *args, _type=1, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def insert_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> None:
        await super().insert_res_id(table_name, s_id, *args, _type=1, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def insert_into_attachment(self, table_name: str, collection: list, *args, **kwargs):
        await super().insert_into_attachment(table_name, collection, *args, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def get_coordinates(self, table_name: str, _limit=3, *args, **kwargs):
        return await super().get_coordinates(table_name, _limit, *args, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def update_coordinates_last_update_field(self, table_name: str, coordinates: str, *args, **kwargs):
        await super().update_coordinates_last_update_field(table_name, coordinates, *args, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def get_coordinates_last_update_field(self, table_name: str, coordinates: str, *args, **kwargs):
        return await super().get_coordinates_last_update_field(table_name, coordinates, *args, **kwargs)


@dataclass
class ClickHouseDataBase:

    _db_name: str

    def __enter__(self):
        return self

    @throw_params_db_ch(host=os.environ.get('CLICK_HOUSE_HOST'), port=os.environ.get('CLICK_HOUSE_PORT'),
                        user=os.environ.get('CLICK_HOUSE_USER'), password=os.environ.get('CLICK_HOUSE_PASSWORD'))
    async def insert_into_resource_social(self, table_name: str, collection: list | tuple, *args, **kwargs) -> None:

        cursor = kwargs.pop('cursor')

        await cursor.execute(
                f'INSERT INTO {self._db_name}.{table_name} (id, country_id, region_id, city_id, resource_name,'
                f' link, screen_name, type, stability, image_profile, s_id, start_date_imas, members, info_check,'
                f' datetime_enable, worker) VALUES',
                collection,
            )


temp_db = TestDB('temp_db')
temp_db_ch = ClickHouseDataBase('default')



# async def f():
#     await temp_db_ch.insert_into_resource_social('resource_social', ([287, 222, 0, 0, 'Арайлым', 'https://www.instagram.com/04.11.1976', '04.11.1976', 4, 0, 'https://scontent-frt3-2.cdninstagram.com/vp/4c5bf8afd35fbad9a746e97279686f46/5BA6C18D/t51.2885-19/10898993_775921005819360_54470393_a.jpg', '1674249566', '1970-01-01', 80, 1, '2017-10-12 14:03:56', 4],))
#
# asyncio.run(f())


# x = "3  287 222	    0	0	Арайлым	https://www.instagram.com/04.11.1976	04.11.1976	4	0	https://scontent-frt3-2.cdninstagram.com/vp/4c5bf8afd35fbad9a746e97279686f46/5BA6C18D/t51.2885-19/10898993_775921005819360_54470393_a.jpg	1674249566	1970-01-01	80	1	2017-10-12 14:03:56	4'"
# x = x.split()
# print(x)

