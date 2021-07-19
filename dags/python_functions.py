#####
# FUNCTIONS FROM speedtest_dag
####
import os
from time import sleep
from datetime import datetime, timedelta

def get_date():
    return datetime.today().strftime('%Y_%m_%d')

def get_month():
    return datetime.today().strftime('%Y-%m')

def get_file_path():
    today_date = get_date()
    todays_month = get_month()
    file_path = f'./results/{get_month()}/{get_date()}.jl'
    return file_path

def create_files_folders():
    """Create a folder if one doesn't exist"""
    folder_path = './results/' + get_month()
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        print(f'new folder created: {folder_path}')

    file_path = get_file_path()
    if not os.path.exists(file_path):
        open(file_path, 'a').close()
        print(f'new file created: {file_path}')
    return

def check_file_updated():
    file_path = get_file_path()
    last_updated = datetime.fromtimestamp(os.path.getmtime(file_path))
    if (datetime.now() - last_updated) < timedelta(minutes=2):
        print(f'{file_path} was updated at {last_updated}')
    else:
        sleep(60)
        if datetime.now() - last_updated < timedelta(minutes=2):
            print(f'{file_path} was updated at {last_updated}')

        else:
            print("""Error: File Not Updated. In this situation, The DAG 
            will assume that there is no internet connection at all,
            and the Speedtest CLI failed to run. 

            To check for errors, look at the Bash Xcom value to see what 
            was printed after running the speedtest cli.
             
            Airflow will not insert anything into the file, as zeros 
            would break speed calculations in the daily_aggregator_dag.""")

#####
# FUNCTIONS FROM daily_aggregator_dag
####
import json
from pandas import json_normalize
from datetime import datetime, timedelta

def calculate_download_speed(series):
    # File Size In Megabytes / (Download Speed In Megabits / 8) = Time In Seconds
    series['Down-MB'] = series['download.bytes']/10**6
    series['Down-Time'] = (series['download.elapsed']/1000)
    series['Down-MByte/sec'] = (series['Down-MB']/series['Down-Time'])
    series['download_speed_mbps'] = (series['Down-MB']/series['Down-Time']) * 8
    return series

def calculate_upload_speed(series):
    # File Size In Megabytes / (Upload Speed In Megabits / 8) = Time In Seconds
    series['Up-MB'] = series['upload.bytes']/10**6
    series['Up-Time'] = (series['upload.elapsed']/1000)
    series['Up-MByte/sec'] = (series['Up-MB']/series['Up-Time'])
    series['upload_speed_mbps'] = (series['Up-MB']/series['Up-Time']) * 8
    return series
    
def get_yesterdays_date():
    return (datetime.today()-timedelta(days=1)).strftime('%Y_%m_%d')

def get_yesterdays_month():
    return (datetime.today()-timedelta(days=1)).strftime('%Y-%m')

def get_yesterdays_file_path():
    today_date = get_yesterdays_date()
    todays_month = get_yesterdays_month()
    file_path = f'./results/{get_yesterdays_month()}/{get_yesterdays_date()}.jl'
    return file_path

def load_json_as_df(ti):
    file_path = get_yesterdays_file_path()
    with open(file_path,'r') as f:
        data = [json.loads(rec) for rec in f]
    
    false=False
    df = json_normalize(data)
    ti.xcom_push(key='raw_df',value=df)

def clean_transform_df(ti):
    # get data from load_json_as_df task
    d_frame = ti.xcom_pull(
        key='raw_df',
        task_ids=['load_json_as_df'])

    # filter for results only
    results = d_frame[d_frame['type']=='result']
    
    # make speed calculations
    modified_results = results.apply(
        calculate_download_speed,axis=1)
    modified_results = modified_results.apply(
        calculate_upload_speed,axis=1)
    
    #remove unnecessary columns
    cols_to_keep = [
        'timestamp',
        'ping.jitter',
        'ping.latency',
        'download_speed_mbps',
        'upload_speed_mbps',
        'download.bytes',
        'upload.bytes',
        'server.location',
        'server.name',
        'server.ip',
        'isp',
        'result.url'
    ]
    
    final_df = modified_results[cols_to_keep]
    ti.xcom_push(key='final_df',value=final_df)

def save_daily_aggregate():
    # get from clean_transform_df task
    final_df = ti.xcom_pull(
        key='final_df',
        task_ids=['clean_transform_df'])

    # save in same folder as json data
    file_path = get_yesterdays_file_path().replace('.jl','.csv')
    final_df.to_csv(file_path,index=False)
    return