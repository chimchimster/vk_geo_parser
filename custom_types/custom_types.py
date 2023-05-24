import json
from typing import NewType
from vk_geo_parser.database.database import MySQLDataBase
from vk_geo_parser.parser.parser import Post


# Applying new custom_types
response_js = NewType('response_js', json)
mysql_database = NewType('MySQL database', MySQLDataBase)
post_data = NewType('Post', Post)