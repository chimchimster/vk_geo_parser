import os
import logging
import requests

from dotenv import load_dotenv


class TelegramCriticalLogger(logging.Logger):

    load_dotenv()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = os.environ.get('vk_token_tg')
        self.chat_id = os.environ.get('chat_id')

    def send_message(self, message: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={message}"

        # Send request
        requests.get(url).json()


logger = TelegramCriticalLogger('VK_GEO')
logger.setLevel('DEBUG')
handler = logging.StreamHandler()
logger.addHandler(handler)


def catch_log(message: str, level='DEBUG'):
    logger.send_message(logger.name + ' ' + message)

    if level == 'DEBUG':
        logger.debug(logger.name + ' ' + message)
    if level == 'ERROR':
        logger.error(logger.name + ' ' + message)





