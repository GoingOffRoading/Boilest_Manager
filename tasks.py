from celery import Celery 
import logging, os, time, requests

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
app.conf.task_default_queue = 'worker_queue'
app.conf.task_queues = {
    'worker_queue': {
        'exchange': 'tasks',
        'exchange_type': 'direct',
        'routing_key': 'worker_queue',
        'queue_arguments': {'x-max-priority': 10},
    }
}
app.conf.task_routes = {
    'locate_files': {'queue': 'worker_queue'},
    'requires_encoding': {'queue': 'worker_queue'},
    'process_ffmpeg': {'queue': 'worker_queue'}
}


def queue_workers_if_queue_empty(arg):
    logger.debug(arg)
    try:
        queue_depth = check_queue('worker_queue')        
        logger.debug(f'Current Worker queue depth is: {queue_depth}')       
        if queue_depth == 0:
            logger.info('Starting locate_files')
            # >>>>>>>>>>><<<<<<<<<<<<<<<<
            # >>>>>>>>>>><<<<<<<<<<<<<<<<
            send_task()
            # >>>>>>>>>>><<<<<<<<<<<<<<<<
            # >>>>>>>>>>><<<<<<<<<<<<<<<<
        elif queue_depth > 0:
            logger.debug(f'{queue_depth} tasks in queue. No rescan needed at this time.')
        else:
            logger.error('Something went wrong checking the Worker Queue')
    
    except Exception as e:
        logger.error(f"Error in queue_workers_if_queue_empty: {e}")


def send_task():
    task_name = 'tasks.locate_files'
    task_arg = 'farts'  # Replace 'your_argument' with the actual argument you want to pass
    queue_name = 'worker_queue'
    
    app.send_task(task_name, args=[task_arg], queue=queue_name, priority=1)
    logger.info(f"Task sent to queue: {queue_name}")


def check_queue(queue_name):
    try:
        rabbitmq_host = 'http://' + os.environ.get('rabbitmq_host')
        rabbitmq_port = os.environ.get('rabbitmq_port')
        user = os.environ.get('celery_user')
        password = os.environ.get('celery_password')
        celery_vhost = os.environ.get('celery_vhost')

        url = f"{rabbitmq_host}:{rabbitmq_port}/api/queues/{celery_vhost}/{queue_name}"
        logger.debug(f'Checking RabbitMQ queue depth for: {queue_name}')

        response = requests.get(url, auth=(user, password))
        response.raise_for_status()  # Ensure we raise an exception for HTTP errors

        worker_queue = response.json()
        queue_depth = worker_queue.get("messages_unacknowledged", 0)

        logger.debug (f'check_queue queue depth is: ' + str(queue_depth))
        return queue_depth
    except Exception as e:
        logger.error(f"Error getting active tasks count: {e}")
        return -1 # Return -1 to indicate an error


if __name__ == "__main__":
    while True:
        queue_workers_if_queue_empty('farts_schedule')
        # Wait for one hour (3600 seconds)
        time.sleep(3600)

