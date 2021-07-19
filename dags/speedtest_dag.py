import os
from time import sleep
from datetime import datetime, timedelta

from airflow import DAG
from airflow.configuration import get
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'start_date': datetime(2021,7,1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

from python_functions import (
    get_date,
    get_month,
    get_file_path,
    create_files_folders,
    check_file_updated)        

with DAG(dag_id='speedtest_dag',
    schedule_interval='*/5 * * * *',
    catchup=False,
    default_args=default_args
    ) as dag:
    
    #task1 - python check if folder exists for the day
    create_folder = PythonOperator(
        task_id='create_files_folders',
        python_callable=create_files_folders
    )

    #task2 - run speedtest
    bash_cmd = f"""
    cd /opt/airflow/results/{get_month()}
    speedtest --accept-license --accept-gdpr -f jsonl >> {get_date()}.jl
    """
    run_speedtest = BashOperator(
        task_id='run_speedtest',
        bash_command=bash_cmd
    )

    # #task3
    check_file_saved = PythonOperator(
        task_id='check_file_updated',
        python_callable=check_file_updated
    )

    create_folder >> run_speedtest >> check_file_saved
    