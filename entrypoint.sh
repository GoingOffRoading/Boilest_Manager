#!/bin/bash

# Start Redis server in the background
redis-server &

# Start Celery Beat in the background
celery -A task.celery beat -l info &

# Start Celery Flower in the background
celery -A task.celery flower --port=5555 &

# Start Flask application
flask run --host=0.0.0.0
