from celery import Celery
from celery.schedules import crontab
import logging, os, time

# create logger
logger = logging.getLogger('boilest_logs')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def celery_url_path(thing):
    # https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#keeping-results
    celery_user = os.environ.get('celery_user')
    celery_password = os.environ.get('celery_password')
    celery_host = os.environ.get('celery_host')
    celery_port = os.environ.get('celery_port')
    celery_vhost = os.environ.get('celery_vhost')
    thing = thing + celery_user + ':' + celery_password + '@' + celery_host + ':' + celery_port + '/' + celery_vhost
    logger.debug('celery_url_path is: ' + thing)
    return thing

app = Celery('worker_queue', broker = celery_url_path('amqp://') )


def send_task():
    task_name = 'tasks.queue_workers_if_queue_empty'
    task_arg = 'farts'  # Replace 'your_argument' with the actual argument you want to pass
    queue_name = 'boilest_worker'
    
    app.send_task(task_name, args=[task_arg], queue=queue_name)
    logger.info(f"Task sent to queue: {queue_name}")

if __name__ == "__main__":
    while True:
        send_task()
        # Wait for one hour (3600 seconds)
        time.sleep(3600)

