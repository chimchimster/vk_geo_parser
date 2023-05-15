import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()


CELERY_BROKER_USERNAME = os.environ.get('CELERY_BROKER_USERNAME')
CELERY_BROKER_PASSWORD = os.environ.get('CELERY_BROKER_PASSWORD')
app = Celery('tasks', broker=f'amqp://{CELERY_BROKER_USERNAME}:{CELERY_BROKER_PASSWORD}@localhost:5672/virtualhost')
app.autodiscover_tasks()


@app.task
def add(x, y):
    return x + y


print(add.delay(1, 2))
