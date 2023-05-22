import os
from celery import Celery
from dotenv import load_dotenv
import json
from datetime import datetime
from time import mktime
from kombu.serialization import register


load_dotenv()

CELERY_BROKER_USERNAME = os.environ.get('CELERY_BROKER_USERNAME')
CELERY_BROKER_PASSWORD = os.environ.get('CELERY_BROKER_PASSWORD')


app = Celery(
    'async_queue',
    broker=f'amqp://{CELERY_BROKER_USERNAME}:{CELERY_BROKER_PASSWORD}@localhost:5672/virtualhost',
)



class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, object):
            return ['ste', 'sdf']
        else:
            return

def my_decoder(obj):
    pass


def my_dumps(obj):
    return json.dumps(obj, cls=MyEncoder)

def my_loads(obj):
    return json.loads(obj, object_hook=my_decoder)

register(
    'myjson',
    my_dumps, my_loads,
    content_type='application/x-myjson',
    content_encoding='utf-8'
)

app.conf.accept_content = ['myjson']
app.conf.task_serializer = 'myjson'
app.conf.result_serializer = 'myjson'


@app.task(serializer='myjson', name='tasks.insert_into_temp_posts_task')
async def insert_into_temp_posts_task(db, collection) -> None:
    await db.insert_into_temp_posts('temp_posts', collection)


if __name__ == '__main__':
    app.autodiscover_tasks()
    app.start()
