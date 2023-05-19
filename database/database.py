import os
from functools import wraps
from dotenv import load_dotenv
from mysql.connector import Connect, Error


def throw_params_db(host: str, user: str, password: str) -> callable:
    """ Function which allows throwing parameters to connect database. """

    def connect_db(func: callable) -> callable:
        """ Function which allows placing specified function into inner scope. """
        @wraps(func)
        def wrapper(*args: tuple[str], **kwargs: tuple[str]) -> list | tuple | None:
            """ Function decorator which allows the operations in database. """

            connection = Connect(
                host=host,
                user=user,
                password=password,
            )
            try:
                result = func(*args, connection=connection, **kwargs)
            except Error as e:
                print(e)
            else:
                connection.commit()
                return result
            finally:
                connection.close()

        return wrapper

    return connect_db


class MySQLDataBase:
    """ Base class for each unique database connection. """

    def __init__(self, db_name: str) -> None:
        self._db_name = db_name

    def get_locations(self):
        ...

    def insert_into_temp_posts(self, table_name: str, collection: tuple, *args, **kwargs) -> None:

        cursor = self.retrieve_connection(kwargs)

        query = f"INSERT IGNORE INTO {self._db_name}.{table_name} (`owner_id`, `from_id`, `item_id`, `res_id`, " \
                f"`title`, `text`, `date`, `s_date`, `not_date`, `link`, `from_type`, `lang`, `sentiment`, `type`, " \
                f"`sphinx_status`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        if len(collection) == 1:
            cursor.execute(query, collection[0])
        else:
            cursor.executemany(query, collection)

    def get_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> int | None:

        cursor = self.retrieve_connection(kwargs)

        cursor.execute(f"SELECT id from {self._db_name}.{table_name} WHERE s_id={s_id} AND type={_type}")

        res_id = cursor.fetchone()

        if res_id:
            return res_id[0]
        else:
            return None

    def insert_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> None:

        cursor = self.retrieve_connection(kwargs)

        cursor.execute(f"INSERT INTO {self._db_name}.{table_name} (type, s_id) VALUES ({_type},{s_id})")



    @staticmethod
    def retrieve_connection(kwargs: dict):
        """ Retrieves connection from kwargs.

            :returns: MySQL DBMS cursor. """

        connection = kwargs.pop('connection')

        cursor = connection.cursor()

        return cursor


class TestDB(MySQLDataBase):
    load_dotenv()

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    def insert_into_temp_posts(self, table_name: str, collection: tuple, *args, **kwargs) -> None:
        super().insert_into_temp_posts(table_name, collection, *args, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    def get_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> int | None:
        return super().get_res_id(table_name, s_id, *args, _type, **kwargs)

    @throw_params_db(host=os.environ.get('MYSQL_HOST'), user=os.environ.get('MYSQL_USER'),
                     password=os.environ.get('MYSQL_PASSWORD'))
    def insert_res_id(self, table_name: str, s_id: str, *args, _type: int = 1, **kwargs) -> None:
        super().insert_res_id(table_name, s_id, *args, _type, **kwargs)


temp_db = TestDB('temp_db')






