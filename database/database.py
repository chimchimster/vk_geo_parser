from mysql.connector import Connect, Error


def throw_params_db(host: str, user: str, password: str) -> callable:
    """ Function which allows throwing parameters to connect database. """

    def connect_db(func: callable) -> callable:
        """ Function which allows placing specified function into inner scope. """

        def wraps(*args: tuple[str], **kwargs: tuple[str]) -> list | tuple | None:
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
    """ Base class for each unique database connection. """

    def __init__(self, db_name: str) -> None:
        self._db_name = db_name

    def get_locations(self):
        ...


