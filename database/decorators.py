import asyncio

import aiomysql
from functools import wraps
from mysql.connector import Error
from asynch.connection import connect as ch_connection
from asynch.errors import ServerException


def throw_params_db(host: str, user: str, password: str) -> callable:
    """ Function which allows throwing parameters to connect database. """

    def connect_db(func: callable) -> callable:
        """ Function which allows placing specified function into inner scope. """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> list | tuple | None:
            """ Function decorator which allows the operations in database. """
            connection = await aiomysql.connect(
                host=host,
                user=user,
                password=password,
                connect_timeout=5,
            )
            try:
                result = await func(*args, connection=connection, **kwargs)
            except Error as e:
                print(e)
            else:
                await connection.commit()
                return result
            finally:
                await connection.ensure_closed()

        return wrapper

    return connect_db


def throw_params_db_ch(host: str, user: str, password: str):
    def connect_db_click_house(func):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> list | tuple | None:

            connection = await ch_connection(
                host=host,
                user=user,
                password=password,
            )
            result = None
            try:
                async with connection.cursor() as cursor:
                    result = await func(*args, cursor=cursor, **kwargs)
            except ServerException as e:
                print(e)

            return result

        return wrapper

    return connect_db_click_house
