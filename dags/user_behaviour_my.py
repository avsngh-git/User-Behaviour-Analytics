import csv
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models.variable import Variable

from utils import _local_to_s3, run_redshift_external_query

#config
BUCKET_NAME =Variable.get('BUCKET')
EMR_ID = Variable.get("EMR_ID")
EMR_STEPS = {}
with open("./dags/scripts/emr/clean_movie_review.json") as json_file:
    EMR_STEPS = json.load(json_file)


#dag defaults
default_args = {
    "owner": "airflow",
    "depends_on_past": True,
    "wait_for_downstream": True,
    "start_date": datetime(2021, 5, 23), #Edit this to the start date
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id='user_behaviour',
    default_args=default_args,
    schedule_interval='0 0 12 1/1 * ? *',
    max_active_runs=1
) as dag:
    extract_user_purchase_data = PostgresOperator(
        task_id = 'extract_user_purchase_data',
        sql="./scripts/sql/unload_user_pruchase.sql",
        postgres_conn_id='postgres_default',
        params={'user_purchase':'/temp/user_purchase.csv'},
        depends_on_past=True,
        wait_for_downstream=True
    )

    user_purchase_to_stage_data_lake = PythonOperator(
        task_id='user_purchase_to_stage_data_lake',
        python_callable=_local_to_s3,
        op_kwargs={
            "file_name":'opt/airflow/temp/user_purchase.csv',
            'key':'stage/user_purchase/{{ ds }}/user_purchase.csv',
            'bucket_name':BUCKET_NAME,
            'remove_local':'true'
            }
    )
    user_purchase_stage_data_lake_to_stage_tbl = PythonOperator(
        task_id = 'user_purchase_stage_data_lake_to_stage_tbl',
        python_callable= run_redshift_external_query,
        op_kwargs={
            
        }
    )



