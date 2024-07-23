# Use the official Python image based on Alpine
FROM python:3.9-alpine

# Install dependencies and supervisor
RUN apk update && \
    apk add --no-cache \
        build-base \
        linux-headers \
        supervisor && \
    pip install --no-cache-dir celery flower requests Flask mysql-connector-python && \
    apk upgrade

# Create a non-root user and group
ARG UID=1000
ARG GID=1000
RUN addgroup -g $GID appgroup && \
    adduser -D -u $UID -G appgroup appuser

# Create application directory and set ownership
WORKDIR /app
COPY . /app
RUN mkdir -p /app/logs
RUN chown -R appuser:appgroup /app 

# Make the entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Environment variables
ENV TZ=US/Pacific

# Used in celery and rabbitmq
ENV celery_user celery
ENV celery_password celery
ENV celery_host 192.168.1.110
ENV celery_port 31672
ENV celery_vhost celery
ENV rabbitmq_host 192.168.1.110
ENV rabbitmq_port 32311

# Used in celery and rabbitmq
ENV sql_host 192.168.1.110
ENV sql_port 32053
ENV sql_database boilest
ENV sql_user boilest
ENV sql_pswd boilest

# Used in Flask
ENV FLASK_APP=Flask.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# User in Flower: https://flower.readthedocs.io/en/latest/config.html
ENV FLOWER_FLOWER_BASIC_AUTH celery:celery
ENV FLOWER_persistent true
ENV FLOWER_db /app/flower_db
ENV FLOWER_purge_offline_workers 60
ENV FLOWER_UNAUTHENTICATED_API true

# Run as non-root user
USER appuser

EXPOSE 5000
EXPOSE 5555

# Start supervisord
CMD ["./entrypoint.sh"]