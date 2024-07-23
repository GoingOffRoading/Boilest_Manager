#!/bin/sh

# Start Celery Beat in the background
#celery -A tasks beat -l info &

# Start Celery Flower in the background
celery -A tasks flower --port=5555 &

# Start Flask application
flask run --host=0.0.0.0
