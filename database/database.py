import os

from datetime import datetime
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
            await cursor.execute(query, collection[0])

    async def get_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> int | None:

        cursor = await self.retrieve_connection(kwargs)

        await cursor.execute(f'SELECT id FROM {self._db_name}.{table_name} WHERE s_id="{s_id}" AND type={_type}')

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

        query = f'INSERT IGNORE INTO {self._db_name}.{table_name} (post_id, attachment, type, owner_id, from_id, item_id, ' \
                f'status) VALUES (%s,%s,%s,%s,%s,%s,%s)'

        if len(collection) > 1:
            await cursor.executemany(query, collection)
        else:
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

    async def get_tokens(self, table_name: str, method: str, *args, **kwargs):

        cursor = await self.retrieve_connection(kwargs)

        query = f'SELECT token FROM {self._db_name}.{table_name} WHERE method="{method}"'

        await cursor.execute(query)

        return await cursor.fetchall()

    async def insert_into_vk_locations_info(self, table_name: str, collection: list | tuple, *args, **kwargs) -> None:

        cursor = await self.retrieve_connection(kwargs)

        query = f'INSERT IGNORE INTO {self._db_name}.{table_name} (city_id, country_id, region_id, location_name, coordinates,' \
                f' stability, is_work, last_update) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'

        await cursor.executemany(query, collection)

    @staticmethod
    async def retrieve_connection(kwargs: dict):
        """ Retrieves connection from kwargs.

            :returns: MySQL DBMS cursor. """

        connection = kwargs.pop('connection')

        cursor = await connection.cursor()

        return cursor


class ImasDB(MySQLDataBase):
    @throw_params_db(host=os.environ.get('MYSQL_HOST_IMAS'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def insert_into_temp_posts(self, table_name: str, collection: tuple, *args, **kwargs) -> None:
        await super().insert_into_temp_posts(table_name, collection, *args, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST_IMAS'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def insert_into_attachment(self, table_name: str, collection: list, *args, **kwargs):
        await super().insert_into_attachment(table_name, collection, *args, **kwargs)


class SocialServicesDB(MySQLDataBase):
    @throw_params_db(host=os.environ.get('MYSQL_HOST_SOCIAL_SERVICES'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def get_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> int | None:
        return await super().get_res_id(table_name, s_id, *args, _type=1, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST_SOCIAL_SERVICES'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def insert_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> None:
        await super().insert_res_id(table_name, s_id, *args, _type=1, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST_SOCIAL_SERVICES'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def get_coordinates(self, table_name: str, _limit=3, *args, **kwargs):
        return await super().get_coordinates(table_name, _limit, *args, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST_SOCIAL_SERVICES'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    async def update_coordinates_last_update_field(self, table_name: str, coordinates: str, *args, **kwargs):
        await super().update_coordinates_last_update_field(table_name, coordinates, *args, **kwargs)


@dataclass
class ClickHouseDB:

    _db_name: str

    def __enter__(self):
        return self

    @throw_params_db_ch(host=os.environ.get('CLICK_HOUSE_HOST'), user=os.environ.get('CLICK_HOUSE_USER'),
                        password=os.environ.get('CLICK_HOUSE_PASSWORD'))
    async def insert_into_resource_social(self, table_name: str, collection: list | tuple, *args, **kwargs) -> None:

        cursor = kwargs.pop('cursor')

        await cursor.execute(
                f'INSERT INTO {self._db_name}.{table_name} (id, country_id, region_id, city_id, resource_name,'
                f' link, screen_name, type, stability, image_profile, s_id, start_date_imas, members, info_check,'
                f' datetime_enable, worker) VALUES',
                collection,
            )


imas_db = ImasDB('imas')
social_services_db = SocialServicesDB('social_services')
imas_ch = ClickHouseDB('imas')


# class TestDB(MySQLDataBase):
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def insert_into_temp_posts(self, table_name: str, collection: tuple, *args, **kwargs) -> None:
#         await super().insert_into_temp_posts(table_name, collection, *args, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def get_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> int | None:
#         return await super().get_res_id(table_name, s_id, *args, _type=1, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def insert_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> None:
#         await super().insert_res_id(table_name, s_id, *args, _type=1, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def insert_into_attachment(self, table_name: str, collection: list, *args, **kwargs):
#         await super().insert_into_attachment(table_name, collection, *args, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def get_coordinates(self, table_name: str, _limit=3, *args, **kwargs):
#         return await super().get_coordinates(table_name, _limit, *args, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def update_coordinates_last_update_field(self, table_name: str, coordinates: str, *args, **kwargs):
#         await super().update_coordinates_last_update_field(table_name, coordinates, *args, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def get_coordinates_last_update_field(self, table_name: str, coordinates: str, *args, **kwargs):
#         return await super().get_coordinates_last_update_field(table_name, coordinates, *args, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def get_tokens(self, table_name: str, method: str, *args, **kwargs):
#         return await super().get_tokens(table_name, method, *args, **kwargs)
#
#     @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
#                      password=os.environ.get('MYSQL_PASSWORD'))
#     async def insert_into_vk_locations_info(self, table_name: str, collection: list | tuple, *args, **kwargs) -> None:
#         await super().insert_into_vk_locations_info(table_name, collection, *args, **kwargs)