from celery import Celery
import logging, os, requests
import celeryconfig

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
    celery_user = os.environ.get('user')
    celery_password = os.environ.get('password')
    celery_host = os.environ.get('celery_host')
    celery_port = os.environ.get('celery_port')
    celery_vhost = os.environ.get('celery_vhost')
    thing = thing + celery_user + ':' + celery_password + '@' + celery_host + ':' + celery_port + '/' + celery_vhost
    logger.debug('celery_url_path is: ' + thing)
    return thing

app = Celery('worker_queue', broker = celery_url_path('amqp://') )


@app.on_after_configure.connect
# Celery's scheduler.  Kicks off queue_workers_if_queue_empty every hour
# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#entries
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3600.0, queue_workers_if_queue_empty.s('hit it'))


