import json
from typing import NewType
from vk_geo_parser.database.database import MySQLDataBase

# Applying new custom_types
response_js = NewType('response_js', json)
mysql_database = NewType('MySQL database', MySQLDataBase)