# each day at 4am for previous day
import json
from pandas import json_normalize
from datetime import datetime, timedelta

from airflow import DAG
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
    get_yesterdays_date,
    get_yesterdays_month,
    get_yesterdays_file_path,
    load_json_as_df,
    calculate_download_speed,
    calculate_upload_speed,
    clean_transform_df,
    save_daily_aggregate)

with DAG(dag_id='daily_aggregator_dag',
    schedule_interval='0 4 * * *',
    catchup=False,
    default_args=default_args
    ) as dag:

    load_data = PythonOperator(
        task_id='load_json_as_df',
        python_callable=load_json_as_df
    )

    transform_data = PythonOperator(
        task_id='clean_transform_df',
        python_callable=clean_transform_df
    )

    save_daily_agg = PythonOperator(
        task_id='save_daily_aggregate',
        python_callable=save_daily_aggregate
    )
    
    load_data >> transform_data >> save_daily_agg