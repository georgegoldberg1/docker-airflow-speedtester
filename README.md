# docker-airflow-speedtester
Containerised scheduler app for broadband speed monitoring

## Intro
This Project consists of 3 parts:
- [Docker](https://www.docker.com/get-started) containers to isolate the coding environment
- [Apache-Airflow](https://airflow.apache.org/) to schedule speedtests, using DAGs and tasks
- [Speedtest.net CLI](https://www.speedtest.net/apps/cli) to run speedtests (command line tool)

This project uses a tweaked version of the official Airflow docker-compose.yaml file ([instructions here](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)), essentially it adapts the official docker image by using 'Apt-get' to install the speedtest cli inside it, so containers will launch with it installed. Then the Airflow DAG runs the speedtests through the command line using the BashOperator

## Set up from git clone
- Clone the repo, then build the image from the Dockerfile, run the containers from the docker-compose file, and you're good to go.

### Build the custom docker image locally
```docker build . --tag speedtest-airflow:speedtest_app```

### Initialise the airflow database  
```docker-compose up airflow-init```

### Start all containers  
```docker-compose up```

### OR START THEM ONE BY ONE if it fails.
```
docker-compose up airflow-init
docker-compose up postgres
docker-compose up redis
docker-compose up airflow-scheduler
docker-compose up airflow-worker

docker-compose up airflow-webserver
flower
```
### Note: You can close down the two UIs (flower and airflow-webserver) to save memory - good if running on raspberry pi! 
```
docker-compose down airflow-webserver
docker-compose down flower
```
(Restart if needed for troubleshooting)
You could create a daily emailer dag for when dagruns fail, so you know when to start the UI up and have a look. Why should an automation platform have to be checked manually after all!

### You can docker exec into you container (the airflow-worker) at anytime:
    ``docker exec -it <workers_container_id> bash``
    ``Ctrl+D``  

### Stop all containers
```docker-compose down```

## How this repo was set up from scratch:

1) Make folders for airflow:
```mkdir dags logs plugins results```

2) Write Dockerfile and build the custom airflow image, using Dockerfile and the [speedtest.net CLI program](https://www.speedtest.net/apps/cli):
```
docker build . --tag speedtest-airflow:speedtest_app
```

3) Download the airflow docker-compose file:
```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.1.2/docker-compose.yaml' > docker-compose.yaml
```

4) Tweak the docker-compose file, so it uses your custom airflow image:
    - Remove:  
    ``image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.1.2}``
    - Insert:  
    ``image: speedtest-airflow:speedtest_app``
    - Remove:
    ``AIRFLOW__CORE__LOAD_EXAMPLES: 'true'``
    - Insert:
    ``AIRFLOW__CORE__LOAD_EXAMPLES: 'false'``
    - ALSO, add this line to the volumes section near the top:  
    ``./results:/opt/airflow/results``  
    so it looks like the below:
```
volumes:
- ./results:/opt/airflow/results
- ./dags:/opt/airflow/dags
- ./logs:/opt/airflow/logs
- ./plugins:/opt/airflow/plugins
```

## note - for emergencies only
 (it will deleted ALL your saved Dagruns and results - only when removeing the app entirely from your system): docker-compose down --volumes --rmi all
 
 
## CONTACT
George Goldberg (ggoldberg.inbox@gmail.com)
