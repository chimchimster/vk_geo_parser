import os
from dotenv import load_dotenv

load_dotenv()

tokens_list = os.environ.get('VK_TOKEN').split(',')


