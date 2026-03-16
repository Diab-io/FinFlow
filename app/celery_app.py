from celery import Celery
import os

celery = Celery(
    "finflow",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery.conf.task_routes = {"*": {"queue": "default"}}