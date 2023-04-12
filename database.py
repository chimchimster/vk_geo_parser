from typing import Optional, Callable, Tuple, List
from mysql.connector import Connect, Error


def throw_params_db(host: Optional[str], user: Optional[str], password: Optional[str]) -> Callable:
    """ Function which allows throwing parameters to connect database. """

    def connect_db(func: Callable) -> Callable:
        """ Function which allows placing specified function into inner scope. """

        def wraps(*args: Tuple[str], **kwargs: Tuple[str]) -> List | Tuple | None:
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

        return wraps

    return connect_db


class MySQLDataBase:
    def __init__(self, db_name: Optional[str]) -> None:
        self._db_name = db_name



