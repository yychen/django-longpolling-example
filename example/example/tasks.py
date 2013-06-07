from celery import task
import time

@task()
def timeout(message, t):
    time.sleep(t)
    return message
