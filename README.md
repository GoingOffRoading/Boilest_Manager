# boilest_manager
A management GUI for Boilest-Scaling-Video-Encoder 

---
# Abstraction

A management UI that:

- Manages the cron schedule for scanning for content in the Boilest_Worker(s)
- Reports on the status of Celery workers
- Reports on the status of encoding stats

---
# Prerequisites  

Same prerequisites as [Boilest-Scaling-Video-Encoder](https://github.com/GoingOffRoading/Boilest-Scaling-Video-Encoder).  If these steps were followed when setting up [Boilest-Scaling-Video-Encoder](https://github.com/GoingOffRoading/Boilest-Scaling-Video-Encoder) then these steps can be skipped for Boilest-Management-GUI as the prerequisites are already in place.

## RabbitMQ

The backbone of Boilest is a distributed task Python library called [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html). Celery needs a message transport (a place to store the task queue), and we leverage RabbitMQ for that.

RabbitMQ will need to be deployed with it's management plugin.

From the management plugin:

- Create a 'celery' vhost
- Create a user with the user/pwd of celery/celery
- Give the celery .* configure, write, read permissions in the celery vhost

---
## MariaDB

Technically, the workflow works fine (at this time) without access to MariaDB (mysql).  MariaDB is where the results of the encoding are tracked.  If Maria is not deployed, the final task will fail, and this will only be noticeable in the logs.

In Maria, create a database called 'boilest'.

In the 'boilest' database, create a table called 'ffmpeghistory' with the following columns:

| Column Name              | Type                            |
|--------------------------|---------------------------------|
| unique_identifier        | varchar(100)                    |
| recorded_date            | datetime                        |
| file_name                | varchar(100)                    |
| file_path                | varchar(100)                    |
| config_name              | varchar(100)                    |
| new_file_size            | int(11)                         |
| new_file_size_difference | int(11)                         |
| old_file_size            | int(11)                         |
| watch_folder             | varchar(100)                    |
| ffmpeg_encoding_string   | varchar(1000)                   |

In a future iteration, I'll include a python script that populates database and table into Maria automatically.

---
# How to deploy

- Create your deployment (Docker/Kubernetes/etc) with the ghcr.io/goingoffroading/boilest-manager:latest container image.
- Change the container variables to reflect your environment:

| ENV                             | Default Value           | Notes                                               |
|---------------------------------|-------------------------|-----------------------------------------------------|
| celery_user                     | celery                  | The user setup for Celery in your RabbitMQ          |
| celery_password                 | celery                  | The password setup for Celery in your RabbitMQ      |
| celery_host                     | 192.168.1.110           | The IP address of RabbitMQ                          |
| celery_port                     | 31672                   | The port RabbitMQ's port 5672 or 5673 are mapped to |
| celery_vhost                    | celery                  | The RabbitMQ vhost setup for Boilest                |
| rabbitmq_host                   | 192.168.1.110           | The IP address of RabbitMQ management UI            |
| rabbitmq_port                   | 32311                   | The port of RabbitMQ management UI                  |
| sql_host                        | 192.168.1.110           | The IP address of MariaDB                           |
| sql_port                        | 32053                   | The port mapped to MariaDB's port 3306              |
| sql_database                    | boilest                 | The database name setup for Boilest                 |
| sql_user                        | boilest                 | The username setup for Boilest                      |
| sql_pswd                        | boilest                 | The password setup for Boilest                      |
| TZ                              | US/Pacific              | Time zone                                           |                   |
| FLASK_APP                       | Flask.py                | Used in Flask                                       |
| FLASK_ENV                       | development             | Used in Flask                                       |
| FLASK_RUN_HOST                  | 0.0.0.0                 | Used in Flask                                       |
| FLASK_RUN_PORT                  | 5000                    | Used in Flask                                       |
| FLOWER_FLOWER_BASIC_AUTH        | celery:celery           | Used in Flower                                      |
| FLOWER_persistent               | true                    | Used in Flower                                      |
| FLOWER_db                       | /app/flower_db          | Used in Flower                                      |
| FLOWER_purge_offline_workers    | 60                      | Used in Flower                                      |
| FLOWER_UNAUTHENTICATED_API      | true                    | Used in Flower                                      |

- Deploy the container.
- Access the UIs via whatever ports 5000 and 5555 were mapped to

Done.

- See 'boilest_kubernetes.yml' for an example of a Kubernetes deployment





# Work in progress


Todo:

- [x] Flask UI for encoding stats
- [x] Celery Flower worker reporting
- [x] Celery Beat job kickoff
- [x] Consider moving queue_workers_if_queue_empty to the manager container
- [ ] Fix funny table label errors